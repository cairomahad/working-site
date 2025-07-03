from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import *
from supabase_client import supabase_client
import shutil
import aiofiles
import json
import csv
import random
import io
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create the main app
app = FastAPI(title="Уроки Ислама API", version="2.0.0")

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Utility functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Simple password verification for development
def verify_simple_password(username: str, password: str) -> bool:
    """Temporary simple password check until proper auth is implemented"""
    simple_passwords = {
        "admin": "admin123",
        "miftahulum": "197724"
    }
    return simple_passwords.get(username) == password

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    admin = await supabase_client.find_one("admin_users", {"username": username})
    if admin is None:
        raise credentials_exception
    return admin

async def require_admin_role(current_admin: dict = Depends(get_current_admin)):
    if current_admin["role"] not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_admin

# Original routes (legacy)
@api_router.get("/")
async def root():
    return {"message": "Hello World with Supabase"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    created_status = await supabase_client.create_record("status_checks", status_obj.dict())
    return StatusCheck(**created_status)

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await supabase_client.get_records("status_checks", limit=1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Admin Authentication Routes
@api_router.post("/admin/login", response_model=Token)
async def admin_login(admin_data: AdminLogin):
    admin = await supabase_client.find_one("admin_users", {"username": admin_data.username})
    if not admin or not verify_simple_password(admin_data.username, admin_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    await supabase_client.update_record(
        "admin_users", "username", admin_data.username,
        {"last_login": datetime.utcnow().isoformat()}
    )
    
    access_token = create_access_token(data={"sub": admin["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Unified Auth Route for both users and admins
@api_router.post("/auth/login")
async def unified_login(login_data: dict):
    email = login_data.get("email")
    password = login_data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # First check if it's an admin by email
    admin = await supabase_client.find_one("admin_users", {"email": email})
    if admin:
        # Use username from admin record for password verification
        if verify_simple_password(admin["username"], password):
            # Update last login
            await supabase_client.update_record(
                "admin_users", "email", email,
                {"last_login": datetime.utcnow().isoformat()}
            )
            
            access_token = create_access_token(data={"sub": admin["username"], "type": "admin"})
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_type": "admin",
                "user": {
                    "id": admin["id"],
                    "email": admin["email"],
                    "name": admin["full_name"],
                    "role": admin["role"]
                }
            }
    
    # If not admin, check regular users
    student = await supabase_client.find_one("students", {"email": email})
    if not student:
        # Create new student record
        student_data = {
            "id": str(uuid.uuid4()),
            "name": email.split("@")[0].title(),
            "email": email,
            "total_score": 0,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "completed_courses": [],
            "current_level": CourseLevel.LEVEL_1
        }
        student = await supabase_client.create_record("students", student_data)
    else:
        # Update last activity
        await supabase_client.update_record(
            "students", "email", email,
            {"last_activity": datetime.utcnow().isoformat()}
        )
    
    access_token = create_access_token(data={"sub": email, "type": "user"})
    return {
        "access_token": access_token,
        "token_type": "bearer", 
        "user_type": "user",
        "user": {
            "id": student["id"],
            "email": student["email"],
            "name": student["name"],
            "total_score": student.get("total_score", 0)
        }
    }

@api_router.get("/admin/me", response_model=AdminUser)
async def get_current_admin_info(current_admin: dict = Depends(get_current_admin)):
    return AdminUser(**current_admin)

# Dashboard Routes
@api_router.get("/admin/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(current_admin: dict = Depends(get_current_admin)):
    total_students = await supabase_client.count_records("students")
    total_courses = await supabase_client.count_records("courses")
    total_lessons = await supabase_client.count_records("lessons")
    total_tests = await supabase_client.count_records("tests")
    total_teachers = await supabase_client.count_records("teachers")
    active_students = await supabase_client.count_records("students", {"is_active": True})
    pending_applications = await supabase_client.count_records("applications", {"status": ApplicationStatus.PENDING})
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    completed_tests_today = await supabase_client.count_records("test_attempts", {
        "completed_at": {"$gte": today.isoformat()}
    })
    
    return DashboardStats(
        total_students=total_students,
        total_courses=total_courses,
        total_lessons=total_lessons,
        total_tests=total_tests,
        total_teachers=total_teachers,
        active_students=active_students,
        pending_applications=pending_applications,
        completed_tests_today=completed_tests_today
    )

# Course Management Routes
@api_router.get("/courses", response_model=List[Course])
async def get_public_courses():
    """Public endpoint for published courses"""
    courses = await supabase_client.get_records(
        "courses", 
        filters={"status": "published"},
        order_by="level"
    )
    return [Course(**course) for course in courses]

@api_router.get("/admin/courses", response_model=List[Course])
async def get_admin_courses(current_admin: dict = Depends(get_current_admin)):
    courses = await supabase_client.get_records("courses", order_by="level")
    return [Course(**course) for course in courses]

@api_router.post("/admin/courses", response_model=Course)
async def create_course(course_data: CourseCreate, current_admin: dict = Depends(get_current_admin)):
    course_dict = course_data.dict()
    course_obj = Course(**course_dict)
    created_course = await supabase_client.create_record("courses", course_obj.dict())
    return Course(**created_course)

@api_router.put("/admin/courses/{course_id}", response_model=Course)
async def update_course(course_id: str, course_data: CourseUpdate, current_admin: dict = Depends(get_current_admin)):
    course = await supabase_client.get_record("courses", "id", course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    update_data = {k: v for k, v in course_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_course = await supabase_client.update_record("courses", "id", course_id, update_data)
    return Course(**updated_course)

# Team Management Routes
@api_router.get("/team", response_model=List[TeamMember])
async def get_team_members():
    """Get all active team members for public page"""
    members = await supabase_client.get_records(
        "team_members", 
        filters={"is_active": True},
        order_by="order"
    )
    return [TeamMember(**member) for member in members]

@api_router.get("/admin/team", response_model=List[TeamMember])
async def get_admin_team_members(current_admin: dict = Depends(get_current_admin)):
    """Get all team members for admin"""
    members = await supabase_client.get_records("team_members", order_by="order")
    return [TeamMember(**member) for member in members]

@api_router.post("/admin/team", response_model=TeamMember)
async def create_team_member(member_data: TeamMemberCreate, current_admin: dict = Depends(get_current_admin)):
    """Create new team member"""
    member_dict = member_data.dict()
    member_obj = TeamMember(**member_dict)
    created_member = await supabase_client.create_record("team_members", member_obj.dict())
    return TeamMember(**created_member)

@api_router.put("/admin/team/{member_id}", response_model=TeamMember)
async def update_team_member(
    member_id: str, 
    member_data: TeamMemberUpdate, 
    current_admin: dict = Depends(get_current_admin)
):
    """Update team member"""
    member = await supabase_client.get_record("team_members", "id", member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    update_data = {k: v for k, v in member_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_member = await supabase_client.update_record("team_members", "id", member_id, update_data)
    return TeamMember(**updated_member)

@api_router.delete("/admin/team/{member_id}")
async def delete_team_member(member_id: str, current_admin: dict = Depends(require_admin_role)):
    """Delete team member"""
    success = await supabase_client.delete_record("team_members", "id", member_id)
    if not success:
        raise HTTPException(status_code=404, detail="Team member not found")
    return {"message": "Team member deleted successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize default data"""
    logger.info("Starting application with Supabase integration...")
    
    # Check if admins exist
    admin_count = await supabase_client.count_records("admin_users")
    logger.info(f"Found {admin_count} admin users in database")
    
    # Check existing team members
    team_count = await supabase_client.count_records("team_members")
    logger.info(f"Found {team_count} team members in database")
    
    logger.info("Application startup completed with Supabase integration")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")