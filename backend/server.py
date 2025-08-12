from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
import json
import csv
import io

# Setup logging
logger = logging.getLogger(__name__)
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

# Import Supabase client
try:
    from supabase_client import supabase_client
    SUPABASE_AVAILABLE = True
    print("✅ Supabase client доступен")
except ImportError:
    SUPABASE_AVAILABLE = False
    print("❌ Supabase client недоступен")

import shutil
import aiofiles
import json
import csv
import random
import io
import re
import base64

# Import admin supabase client
try:
    from admin_supabase_client import admin_supabase_client
    ADMIN_SUPABASE_AVAILABLE = True
    print("✅ Admin Supabase client доступен")
except ImportError:
    ADMIN_SUPABASE_AVAILABLE = False
    print("❌ Admin Supabase client недоступен")

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
SECRET_KEY = os.getenv("SECRET_KEY", "uroki-islama-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database client selection
if SUPABASE_AVAILABLE:
    db_client = supabase_client
    print("🔗 Используется Supabase API")
else:
    raise Exception("Supabase клиент не доступен!")

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
    
    admin = await db_client.find_one("admin_users", {"username": username})
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

# File upload utilities
async def save_uploaded_file(upload_file: UploadFile, folder: str = "general") -> str:
    """Save uploaded file and return the URL"""
    file_extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    folder_path = UPLOAD_DIR / folder
    folder_path.mkdir(exist_ok=True)
    file_path = folder_path / unique_filename
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await upload_file.read()
        await f.write(content)
    
    return f"/uploads/{folder}/{unique_filename}"

def convert_to_embed_url(url: str) -> str:
    """Convert YouTube URL to embed format"""
    if not url:
        return url
    
    # Handle different YouTube URL formats
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}"
    
    return url

# ====================================================================
# ROOT ENDPOINTS
# ====================================================================

@api_router.get("/")
async def root():
    return {"message": "Hello World with Supabase"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    created_status = await db_client.create_record("status_checks", status_obj.dict())
    return StatusCheck(**created_status)

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db_client.get_records("status_checks", limit=1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# ====================================================================
# AUTHENTICATION ENDPOINTS
# ====================================================================

@api_router.post("/admin/login", response_model=Token)
async def admin_login(admin_data: AdminLogin):
    admin = await db_client.find_one("admin_users", {"username": admin_data.username})
    if not admin or not verify_simple_password(admin_data.username, admin_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    await db_client.update_record(
        "admin_users", "username", admin_data.username,
        {"last_login": datetime.utcnow().isoformat()}
    )
    
    access_token = create_access_token(data={"sub": admin["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/auth/login")
async def unified_login(login_data: dict):
    email = login_data.get("email")
    password = login_data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # First check if it's an admin by email
    admin = await db_client.find_one("admin_users", {"email": email})
    if admin:
        # Use username from admin record for password verification
        if verify_simple_password(admin["username"], password):
            # Update last login
            await db_client.update_record(
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
    student = await db_client.find_one("students", {"email": email})
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
        student = await db_client.create_record("students", student_data)
    else:
        # Update last activity
        await db_client.update_record(
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

# ====================================================================
# DASHBOARD ENDPOINTS
# ====================================================================

@api_router.get("/admin/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(current_admin: dict = Depends(get_current_admin)):
    total_students = await db_client.count_records("students")
    total_courses = await db_client.count_records("courses")
    total_lessons = await db_client.count_records("lessons")
    total_tests = await db_client.count_records("tests")
    total_teachers = await db_client.count_records("teachers")
    active_students = await db_client.count_records("students", {"is_active": True})
    pending_applications = await db_client.count_records("applications", {"status": "pending"})
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    completed_tests_today = await db_client.count_records("test_attempts", {
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

# ====================================================================
# COURSE MANAGEMENT ENDPOINTS
# ====================================================================

@api_router.get("/courses", response_model=List[Course])
async def get_public_courses():
    """Public endpoint for published courses"""
    courses = await db_client.get_records(
        "courses", 
        filters={"status": "published"},
        order_by="order"
    )
    return [Course(**course) for course in courses]

@api_router.get("/admin/courses", response_model=List[Course])
async def get_admin_courses(current_admin: dict = Depends(get_current_admin)):
    courses = await db_client.get_records("courses", order_by="order")
    return [Course(**course) for course in courses]

@api_router.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str):
    course = await db_client.get_record("courses", "id", course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return Course(**course)

@api_router.post("/admin/courses", response_model=Course)
async def create_course(course_data: CourseCreate, current_admin: dict = Depends(get_current_admin)):
    course_dict = course_data.dict()
    course_obj = Course(**course_dict)
    created_course = await db_client.create_record("courses", course_obj.dict())
    return Course(**created_course)

@api_router.put("/admin/courses/{course_id}", response_model=Course)
async def update_course(course_id: str, course_data: CourseUpdate, current_admin: dict = Depends(get_current_admin)):
    course = await db_client.get_record("courses", "id", course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    update_data = {k: v for k, v in course_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_course = await db_client.update_record("courses", "id", course_id, update_data)
    return Course(**updated_course)

@api_router.delete("/admin/courses/{course_id}")
async def delete_course(course_id: str, current_admin: dict = Depends(require_admin_role)):
    course = await db_client.get_record("courses", "id", course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    success = await db_client.delete_record("courses", "id", course_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete course")
    return {"message": "Course deleted successfully"}

# ====================================================================
# ====================================================================
# NEW LESSON MANAGEMENT ENDPOINTS - CLEAN AND SIMPLE
# ====================================================================

@api_router.get("/courses/{course_id}/lessons", response_model=List[Lesson])
async def get_course_lessons(course_id: str):
    """Get all published lessons for a course"""
    lessons = await db_client.get_records(
        "lessons", 
        filters={"course_id": course_id, "is_published": True},
        order_by="order"
    )
    return [Lesson(**lesson) for lesson in lessons]

@api_router.get("/lessons/{lesson_id}", response_model=Lesson)
async def get_lesson(lesson_id: str):
    """Get a specific lesson by ID"""
    lesson = await db_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return Lesson(**lesson)

# ADMIN ENDPOINTS
@api_router.get("/admin/lessons", response_model=List[Lesson])
async def get_all_lessons_admin(current_admin: dict = Depends(get_current_admin)):
    """Get all lessons for admin panel"""
    lessons = await db_client.get_records("lessons", order_by="-created_at")
    return [Lesson(**lesson) for lesson in lessons]

@api_router.get("/admin/courses/{course_id}/lessons", response_model=List[Lesson])
async def get_admin_course_lessons(course_id: str, current_admin: dict = Depends(get_current_admin)):
    """Get all lessons for a specific course (admin view)"""
    lessons = await db_client.get_records(
        "lessons", 
        filters={"course_id": course_id},
        order_by="order"
    )
    return [Lesson(**lesson) for lesson in lessons]

@api_router.post("/admin/lessons", response_model=Lesson)
async def create_lesson_admin(lesson_data: LessonCreate, current_admin: dict = Depends(get_current_admin)):
    """Create a new lesson"""
    try:
        # Validate course exists
        course = await db_client.get_record("courses", "id", lesson_data.course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Create lesson data
        lesson_dict = lesson_data.dict()
        lesson_dict["id"] = str(uuid.uuid4())
        lesson_dict["created_at"] = datetime.utcnow().isoformat()
        lesson_dict["updated_at"] = datetime.utcnow().isoformat()
        
        # Generate slug from title
        if not lesson_dict.get("slug"):
            lesson_dict["slug"] = create_slug(lesson_dict["title"])
        
        # Convert YouTube URL if provided
        if lesson_dict.get("video_url"):
            lesson_dict["video_url"] = convert_to_embed_url(lesson_dict["video_url"])
        
        created_lesson = await db_client.create_record("lessons", lesson_dict)
        return Lesson(**created_lesson)
        
    except Exception as e:
        logger.error(f"Error creating lesson: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create lesson: {str(e)}")

@api_router.put("/admin/lessons/{lesson_id}", response_model=Lesson)
async def update_lesson_admin(lesson_id: str, lesson_data: LessonUpdate, current_admin: dict = Depends(get_current_admin)):
    """Update an existing lesson"""
    try:
        # Check lesson exists
        lesson = await db_client.get_record("lessons", "id", lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Prepare update data (only non-None values)
        update_data = {k: v for k, v in lesson_data.dict().items() if v is not None}
        
        if update_data:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Convert YouTube URL if provided
            if "video_url" in update_data and update_data["video_url"]:
                update_data["video_url"] = convert_to_embed_url(update_data["video_url"])
            
            updated_lesson = await db_client.update_record("lessons", "id", lesson_id, update_data)
            return Lesson(**updated_lesson)
        
        return Lesson(**lesson)
        
    except Exception as e:
        logger.error(f"Error updating lesson: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update lesson: {str(e)}")

@api_router.delete("/admin/lessons/{lesson_id}")
async def delete_lesson_admin(lesson_id: str, current_admin: dict = Depends(get_current_admin)):
    """Delete a lesson"""
    lesson = await db_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    await db_client.delete_record("lessons", "id", lesson_id)
    return {"message": "Lesson deleted successfully"}

# ====================================================================
# TEAM MANAGEMENT ENDPOINTS
# ====================================================================

@api_router.get("/team", response_model=List[TeamMember])
async def get_team_members():
    """Get all active team members for public page"""
    members = await db_client.get_records(
        "team_members", 
        filters={"is_active": True},
        order_by="order"
    )
    return [TeamMember(**member) for member in members]

@api_router.get("/admin/team", response_model=List[TeamMember])
async def get_admin_team_members(current_admin: dict = Depends(get_current_admin)):
    """Get all team members for admin"""
    members = await db_client.get_records("team_members", order_by="order")
    return [TeamMember(**member) for member in members]

@api_router.post("/admin/team", response_model=TeamMember)
async def create_team_member(member_data: TeamMemberCreate, current_admin: dict = Depends(get_current_admin)):
    """Create new team member"""
    member_dict = member_data.dict()
    member_obj = TeamMember(**member_dict)
    created_member = await db_client.create_record("team_members", member_obj.dict())
    return TeamMember(**created_member)

@api_router.put("/admin/team/{member_id}", response_model=TeamMember)
async def update_team_member(
    member_id: str, 
    member_data: TeamMemberUpdate, 
    current_admin: dict = Depends(get_current_admin)
):
    """Update team member"""
    member = await db_client.get_record("team_members", "id", member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    update_data = {k: v for k, v in member_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_member = await db_client.update_record("team_members", "id", member_id, update_data)
    return TeamMember(**updated_member)

@api_router.delete("/admin/team/{member_id}")
async def delete_team_member(member_id: str, current_admin: dict = Depends(require_admin_role)):
    """Delete team member"""
    success = await db_client.delete_record("team_members", "id", member_id)
    if not success:
        raise HTTPException(status_code=404, detail="Team member not found")
    return {"message": "Team member deleted successfully"}

# ====================================================================
# TEACHER MANAGEMENT ENDPOINTS
# ====================================================================

@api_router.get("/admin/teachers", response_model=List[Teacher])
async def get_admin_teachers(current_admin: dict = Depends(get_current_admin)):
    """Get all teachers for admin"""
    teachers = await db_client.get_records("teachers", order_by="name")
    return [Teacher(**teacher) for teacher in teachers]

@api_router.post("/admin/teachers", response_model=Teacher)
async def create_teacher(teacher_data: TeacherCreate, current_admin: dict = Depends(get_current_admin)):
    """Create new teacher"""
    teacher_dict = teacher_data.dict()
    teacher_obj = Teacher(**teacher_dict)
    created_teacher = await db_client.create_record("teachers", teacher_obj.dict())
    return Teacher(**created_teacher)

@api_router.put("/admin/teachers/{teacher_id}", response_model=Teacher)
async def update_teacher(
    teacher_id: str, 
    teacher_data: TeacherCreate, 
    current_admin: dict = Depends(get_current_admin)
):
    """Update teacher"""
    teacher = await db_client.get_record("teachers", "id", teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    update_data = {k: v for k, v in teacher_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_teacher = await db_client.update_record("teachers", "id", teacher_id, update_data)
    return Teacher(**updated_teacher)

@api_router.delete("/admin/teachers/{teacher_id}")
async def delete_teacher(teacher_id: str, current_admin: dict = Depends(require_admin_role)):
    """Delete teacher"""
    success = await db_client.delete_record("teachers", "id", teacher_id)
    if not success:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return {"message": "Teacher deleted successfully"}

# ====================================================================
# NEW SIMPLE TEST SYSTEM ENDPOINTS
# ====================================================================

@api_router.get("/admin/tests", response_model=List[SimpleTest])
async def get_admin_tests(current_admin: dict = Depends(get_current_admin)):
    """Get all tests for admin"""
    try:
        logger.info("Getting tests from 'tests' table")
        # Use the old tests table since that's what exists
        tests = await db_client.get_records("tests")
        logger.info(f"Found {len(tests)} tests in database")
        
        # Convert old format to new format (simplified)
        converted_tests = []
        for i, test in enumerate(tests):
            logger.info(f"Converting test {i+1}: {test.get('title', 'Unknown')}")
            converted_test = {
                "id": test.get("id"),
                "lesson_id": test.get("lesson_id") or "",  # Handle None values
                "title": test.get("title") or "",
                "description": test.get("description") or "",
                "questions": [],  # For now, questions are not loaded from separate table
                "time_limit_minutes": test.get("time_limit_minutes", 10),
                "is_published": test.get("is_published", True),
                "created_at": test.get("created_at"),
                "updated_at": test.get("updated_at")
            }
            converted_tests.append(SimpleTest(**converted_test))
        
        logger.info(f"Returning {len(converted_tests)} converted tests")
        return converted_tests
        
    except Exception as e:
        logger.error(f"Error getting tests: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []

@api_router.get("/lessons/{lesson_id}/test", response_model=SimpleTest)
async def get_lesson_test(lesson_id: str):
    """Get test for a specific lesson"""
    try:
        # Use the old tests table since that's what exists
        tests = await db_client.get_records("tests", filters={"lesson_id": lesson_id})
        if tests:
            test = tests[0]
            converted_test = {
                "id": test.get("id"),
                "lesson_id": test.get("lesson_id") or "",
                "title": test.get("title") or "",
                "description": test.get("description") or "",
                "questions": [],
                "time_limit_minutes": test.get("time_limit_minutes", 10),
                "is_published": test.get("is_published", True),
                "created_at": test.get("created_at"),
                "updated_at": test.get("updated_at")
            }
            return SimpleTest(**converted_test)
    except:
        pass
    
    raise HTTPException(status_code=404, detail="No test found for this lesson")

@api_router.get("/lessons/{lesson_id}/tests", response_model=List[SimpleTest])
async def get_lesson_tests(lesson_id: str):
    """Get all tests for a specific lesson (returns list for compatibility)"""
    try:
        # Use the old tests table since that's what exists
        tests = await db_client.get_records("tests", filters={"lesson_id": lesson_id})
        converted_tests = []
        
        for test in tests:
            converted_test = {
                "id": test.get("id"),
                "lesson_id": test.get("lesson_id") or "",
                "title": test.get("title") or "",
                "description": test.get("description") or "",
                "questions": [],
                "time_limit_minutes": test.get("time_limit_minutes", 10),
                "is_published": test.get("is_published", True),
                "created_at": test.get("created_at"),
                "updated_at": test.get("updated_at")
            }
            converted_tests.append(SimpleTest(**converted_test))
        
        return converted_tests
        
    except Exception as e:
        logger.error(f"Error getting tests for lesson {lesson_id}: {str(e)}")
        return []

@api_router.get("/tests/{test_id}", response_model=SimpleTest)
async def get_test_details(test_id: str):
    """Get test details with questions for taking test"""
    try:
        # Get test from tests table
        test = await db_client.get_record("tests", "id", test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        
        # Get questions from simple_test_questions table or fallback to questions table
        questions = []
        
        # Try to load from new simple_test_questions table first
        try:
            test_questions = await db_client.get_records("simple_test_questions", filters={"test_id": test_id})
            for q in test_questions:
                question = {
                    "question": q.get("question_text", ""),
                    "options": [
                        q.get("option_a", ""),
                        q.get("option_b", ""),
                        q.get("option_c", ""),
                        q.get("option_d", "")
                    ],
                    "correct": q.get("correct_option", 0)
                }
                questions.append(question)
            logger.info(f"Loaded {len(questions)} questions from simple_test_questions table")
        except Exception as e:
            logger.info(f"simple_test_questions table not available: {e}")
            # Fallback to old questions table
            try:
                test_questions = await db_client.get_records("questions", filters={"test_id": test_id})
                for q in test_questions:
                    question = {
                        "question": q.get("text", ""),
                        "options": [],
                        "correct": int(q.get("correct_answer", "0"))
                    }
                    
                    # Try to parse options from explanation field
                    explanation = q.get("explanation", "")
                    if explanation.startswith("OPTIONS_JSON:"):
                        try:
                            options_json = explanation[13:]  # Remove "OPTIONS_JSON:" prefix
                            options = json.loads(options_json)
                            question["options"] = options
                        except Exception as e:
                            logger.warning(f"Could not parse options JSON: {e}")
                    
                    questions.append(question)
                logger.info(f"Loaded {len(questions)} questions from questions table with JSON options")
            except Exception as e2:
                logger.warning(f"Could not load questions from any table: {e2}")
        
        # Fallback: Load questions from JSON field (if exists)
        if not questions and test.get("questions"):
            questions = test.get("questions", [])
            logger.info(f"Loaded {len(questions)} questions from JSON field")
        
        converted_test = {
            "id": test.get("id"),
            "lesson_id": test.get("lesson_id") or "",
            "title": test.get("title") or "",
            "description": test.get("description") or "",
            "questions": questions,
            "time_limit_minutes": test.get("time_limit_minutes", 10),
            "is_published": test.get("is_published", True),
            "created_at": test.get("created_at"),
            "updated_at": test.get("updated_at")
        }
        
        logger.info(f"Returning test with {len(questions)} questions")
        return SimpleTest(**converted_test)
        
    except Exception as e:
        logger.error(f"Error getting test details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get test: {str(e)}")

@api_router.post("/admin/tests", response_model=SimpleTest)
async def create_test_admin(test_data: SimpleTestCreate, current_admin: dict = Depends(get_current_admin)):
    """Create new test for a lesson"""
    try:
        logger.info(f"Creating test with data: {test_data}")
        
        # Validate lesson exists
        lesson = await db_client.get_record("lessons", "id", test_data.lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        logger.info(f"Found lesson: {lesson.get('title', 'Unknown')}")
        
        # Create test data
        test_dict = test_data.dict()
        test_dict["id"] = str(uuid.uuid4())
        test_dict["created_at"] = datetime.utcnow().isoformat()
        test_dict["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Prepared test dict: {test_dict}")
        
        # Create in old tests table format - БЕЗ ПОЛЯ QUESTIONS пока что
        old_format_data = {
            "id": test_dict["id"],
            "lesson_id": test_dict["lesson_id"],
            "title": test_dict["title"],
            "description": test_dict["description"],
            "course_id": lesson.get("course_id", ""),
            "time_limit_minutes": test_dict["time_limit_minutes"],
            "passing_score": 70,
            "max_attempts": 3,
            "is_published": True,
            "order": 1,
            "created_at": test_dict["created_at"],
            "updated_at": test_dict["updated_at"]
        }
        
        logger.info(f"Creating test in old format: {old_format_data}")
        
        created_test = await db_client.create_record("tests", old_format_data)
        logger.info(f"Created test: {created_test}")
        
        # Store questions in the new simple_test_questions table
        questions = test_dict.get("questions", [])
        if questions:
            logger.info(f"Will store {len(questions)} questions in simple_test_questions table")
            for i, question_data in enumerate(questions):
                try:
                    # New simplified structure
                    question_record = {
                        "id": str(uuid.uuid4()),
                        "test_id": test_dict["id"],
                        "question_text": question_data.get("question", ""),
                        "option_a": question_data.get("options", ["", "", "", ""])[0] if len(question_data.get("options", [])) > 0 else "",
                        "option_b": question_data.get("options", ["", "", "", ""])[1] if len(question_data.get("options", [])) > 1 else "",
                        "option_c": question_data.get("options", ["", "", "", ""])[2] if len(question_data.get("options", [])) > 2 else "",
                        "option_d": question_data.get("options", ["", "", "", ""])[3] if len(question_data.get("options", [])) > 3 else "",
                        "correct_option": question_data.get("correct", 0),
                        "order": i + 1
                    }
                    await db_client.create_record("simple_test_questions", question_record)
                    logger.info(f"Created question {i+1} in simple_test_questions")
                except Exception as e:
                    logger.warning(f"Could not create question in simple_test_questions: {e}")
                    # Fallback to old questions table
                    # Fallback to old questions table with JSON storage
                    try:
                        question_record = {
                            "id": str(uuid.uuid4()),
                            "test_id": test_dict["id"],
                            "text": question_data.get("question", ""),
                            "question_type": "single_choice",
                            "correct_answer": str(question_data.get("correct", 0)),
                            "explanation": f"OPTIONS_JSON:{json.dumps(question_data.get('options', []))}",  # Store options in explanation field as JSON
                            "points": 1,
                            "order": i + 1
                        }
                        await db_client.create_record("questions", question_record)
                        logger.info(f"Created question {i+1} in fallback questions table with options in JSON")
                    except Exception as e2:
                        logger.error(f"Could not create question in any table: {e2}")
                        break
        
        # Return in SimpleTest format
        result = SimpleTest(**{
            "id": created_test["id"],
            "lesson_id": created_test["lesson_id"],
            "title": created_test["title"],
            "description": created_test["description"],
            "questions": questions,
            "time_limit_minutes": created_test["time_limit_minutes"],
            "is_published": created_test["is_published"],
            "created_at": created_test["created_at"],
            "updated_at": created_test["updated_at"]
        })
        
        logger.info(f"Returning result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating test: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create test: {str(e)}")

@api_router.put("/admin/tests/{test_id}", response_model=SimpleTest)
async def update_test_admin(test_id: str, test_data: SimpleTestUpdate, current_admin: dict = Depends(get_current_admin)):
    """Update an existing test"""
    try:
        # Check test exists
        test = await db_client.get_record("simple_tests", "id", test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        
        # Prepare update data
        update_data = {k: v for k, v in test_data.dict().items() if v is not None}
        
        if update_data:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            updated_test = await db_client.update_record("simple_tests", "id", test_id, update_data)
            return SimpleTest(**updated_test)
        
        return SimpleTest(**test)
        
    except Exception as e:
        logger.error(f"Error updating test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update test: {str(e)}")

@api_router.delete("/admin/tests/{test_id}")
async def delete_test_admin(test_id: str, current_admin: dict = Depends(get_current_admin)):
    """Delete a test"""
    test = await db_client.get_record("simple_tests", "id", test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    await db_client.delete_record("simple_tests", "id", test_id)
    return {"message": "Test deleted successfully"}

@api_router.post("/tests/{test_id}/submit")
async def submit_test(
    test_id: str, 
    submission_data: Dict[str, Any]
):
    """Submit test answers and calculate score with points system"""
    try:
        # Get test from tests table (not simple_tests!)
        test = await db_client.get_record("tests", "id", test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Test not found")
        
        user_id = submission_data.get("user_id")
        user_name = submission_data.get("user_name")
        answers = submission_data.get("answers", {})
        
        if not user_id or not user_name:
            raise HTTPException(status_code=400, detail="User ID and name are required")
        
        # Get questions from simple_test_questions table or fallback
        test_questions = []
        
        # Try new simple_test_questions table first
        try:
            questions_records = await db_client.get_records("simple_test_questions", filters={"test_id": test_id})
            for q in questions_records:
                question = {
                    "question": q.get("question_text", ""),
                    "correct": q.get("correct_option", 0)
                }
                test_questions.append(question)
            logger.info(f"Using questions from simple_test_questions: {len(test_questions)}")
        except Exception as e:
            logger.info(f"simple_test_questions not available: {e}")
            # Fallback to old questions table
            try:
                questions_records = await db_client.get_records("questions", filters={"test_id": test_id})
                for q in questions_records:
                    question = {
                        "question": q.get("text", ""),
                        "correct": int(q.get("correct_answer", "0"))
                    }
                    test_questions.append(question)
                logger.info(f"Using questions from questions table: {len(test_questions)}")
            except Exception as e2:
                logger.warning(f"Could not load questions from questions table: {e2}")
        
        # Final fallback: try JSON field
        if not test_questions and test.get("questions"):
            test_questions = test.get("questions", [])
            logger.info(f"Using questions from JSON: {len(test_questions)}")
        
        # Calculate score
        total_questions = len(test_questions)
        correct_count = 0
        
        if total_questions == 0:
            raise HTTPException(status_code=400, detail="Test has no questions")
        
        for i, question in enumerate(test_questions):
            question_id = f"q{i}"
            user_answer = answers.get(question_id)
            correct_answer = question.get("correct")
            
            logger.info(f"Q{i}: user={user_answer}, correct={correct_answer}")
            
            if user_answer is not None and user_answer == correct_answer:
                correct_count += 1
        
        percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # Check if user has already taken this test before (more strict checking)
        try:
            existing_results = await db_client.get_records("test_results", filters={
                "user_id": user_id, 
                "test_id": test_id
            })
            has_taken_before = len(existing_results) > 0
            
            # Also check by user_name as additional verification
            if not has_taken_before:
                name_results = await db_client.get_records("test_results", filters={
                    "user_name": user_name, 
                    "test_id": test_id
                })
                has_taken_before = len(name_results) > 0
                
            if has_taken_before:
                logger.info(f"User {user_name} (ID: {user_id}) has already taken test {test_id}")
            else:
                logger.info(f"First attempt for user {user_name} (ID: {user_id}) on test {test_id}")
                
        except Exception as e:
            logger.info(f"Could not check existing results: {e}")
            has_taken_before = False
        
        # Calculate points: 5 for completion + 1 per correct answer, but only if first attempt
        if has_taken_before:
            points_earned = 0  # No points for retaking
            message = f"Тест завершен! Результат: {correct_count}/{total_questions} ({percentage:.1f}%). За повторное прохождение очки не начисляются."
        else:
            points_earned = 5 + correct_count  # 5 for completion + 1 per correct answer
            message = f"Тест завершен! Получено {points_earned} очков (5 за завершение + {correct_count} за правильные ответы)."
        
        logger.info(f"Test result: {correct_count}/{total_questions} = {percentage}%, +{points_earned} points")
        
        # Save test result (try to create table if not exists)
        try:
            result_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "user_name": user_name,
                "test_id": test_id,
                "lesson_id": test.get("lesson_id", ""),
                "score": correct_count,
                "total_questions": total_questions,
                "percentage": percentage,
                "points_earned": points_earned,
                "completed_at": datetime.utcnow().isoformat()
            }
            
            await db_client.create_record("test_results", result_data)
        except Exception as e:
            logger.warning(f"Could not save test result: {e}")
        
        # Update user score only if points were earned (first time taking test)
        if points_earned > 0:
            try:
                await update_user_score(user_id, user_name, points_earned)
            except Exception as e:
                logger.warning(f"Could not update user score: {e}")
        
        return {
            "score": correct_count,
            "total_questions": total_questions,
            "percentage": percentage,
            "points_earned": points_earned,
            "message": message,
            "is_retake": has_taken_before,
            "correct_answers": [
                {
                    "question": q.get("question", ""),
                    "user_answer": answers.get(f"q{i}"),
                    "correct_answer": q.get("correct"),
                    "is_correct": answers.get(f"q{i}") == q.get("correct")
                }
                for i, q in enumerate(test_questions)
            ]
        }
        
    except Exception as e:
        logger.error(f"Error submitting test: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to submit test: {str(e)}")

async def update_user_score(user_id: str, user_name: str, points_earned: int):
    """Update user's total score"""
    try:
        # Try to get existing user score (fallback if table doesn't exist)
        existing_scores = []
        try:
            existing_scores = await db_client.get_records("user_scores", filters={"user_id": user_id})
        except Exception as e:
            logger.info(f"user_scores table not available, will try to create record: {e}")
        
        if existing_scores:
            # Update existing score
            user_score = existing_scores[0]
            update_data = {
                "total_points": user_score["total_points"] + points_earned,
                "tests_completed": user_score["tests_completed"] + 1,
                "last_test_date": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            await db_client.update_record("user_scores", "id", user_score["id"], update_data)
            logger.info(f"Updated score for user {user_name}: +{points_earned} points")
        else:
            # Create new user score
            score_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "user_name": user_name,
                "total_points": points_earned,
                "tests_completed": 1,
                "last_test_date": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            await db_client.create_record("user_scores", score_data)
            logger.info(f"Created new score record for user {user_name}: {points_earned} points")
            
    except Exception as e:
        logger.error(f"Error updating user score: {str(e)}")
        # Don't fail the whole test submission if scoring fails

# ====================================================================
# POINTS-BASED LEADERBOARD ENDPOINTS  
# ====================================================================

@api_router.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get top users leaderboard based on points earned from tests"""
    try:
        # Try to get all user scores ordered by points
        user_scores = []
        try:
            user_scores = await db_client.get_records(
                "user_scores",
                order_by="-total_points",
                limit=limit
            )
        except Exception as e:
            logger.info(f"user_scores table not available: {e}")
            return []
        
        leaderboard = []
        for i, score in enumerate(user_scores, 1):
            leaderboard.append({
                "rank": i,
                "user_name": score["user_name"],
                "total_points": score["total_points"],
                "tests_completed": score["tests_completed"],
                "last_test_date": score.get("last_test_date")
            })
        
        return leaderboard
        
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        return []

# ====================================================================
# FILE UPLOAD ENDPOINTS
# ====================================================================

@api_router.post("/admin/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = "general",
    current_admin: dict = Depends(get_current_admin)
):
    """Upload file and return URL"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_url = await save_uploaded_file(file, folder)
    return {"file_url": file_url, "filename": file.filename}

@api_router.post("/admin/upload-enhanced")
async def upload_enhanced_file(
    file: UploadFile = File(...),
    current_admin: dict = Depends(get_current_admin)
):
    """Enhanced file upload with chunked reading for large files"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file with chunked reading
    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            await f.write(chunk)
    
    file_url = f"/uploads/{unique_filename}"
    file_size = file_path.stat().st_size
    
    return {
        "file_url": file_url,
        "filename": file.filename,
        "size": file_size,
        "type": file.content_type
    }

# ====================================================================
# Q&A MANAGEMENT ENDPOINTS (Imam Questions and Answers)
# ====================================================================

@api_router.get("/qa/questions", response_model=List[QAQuestion])
async def get_qa_questions(
    limit: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Get Q&A questions for public view"""
    filters = {}
    if category:
        filters["category"] = category
    if search:
        filters["title"] = {"$regex": search}
    
    questions = await db_client.get_records(
        "qa_questions",
        filters=filters,
        order_by="-created_at",
        limit=limit
    )
    
    # Increment view counts
    for question in questions:
        try:
            await db_client.update_record(
                "qa_questions", "id", question["id"],
                {"views_count": question.get("views_count", 0) + 1}
            )
        except:
            pass  # Don't fail if view count update fails
    
    return [QAQuestion(**question) for question in questions]

@api_router.get("/qa/questions/{question_id}", response_model=QAQuestion)
async def get_qa_question(question_id: str):
    """Get single Q&A question by ID"""
    question = await db_client.get_record("qa_questions", "id", question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Increment view count
    try:
        await db_client.update_record(
            "qa_questions", "id", question_id,
            {"views_count": question.get("views_count", 0) + 1}
        )
    except:
        pass
    
    return QAQuestion(**question)

@api_router.get("/qa/questions/slug/{slug}", response_model=QAQuestion)
async def get_qa_question_by_slug(slug: str):
    """Get Q&A question by slug"""
    question = await db_client.find_one("qa_questions", {"slug": slug})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Increment view count
    try:
        await db_client.update_record(
            "qa_questions", "id", question["id"],
            {"views_count": question.get("views_count", 0) + 1}
        )
    except:
        pass
    
    return QAQuestion(**question)

@api_router.get("/qa/categories")
async def get_qa_categories():
    """Get list of Q&A categories"""
    try:
        # Get categories with question counts
        questions = await db_client.get_records("qa_questions")
        categories = {}
        
        for question in questions:
            category = question.get("category", "general")
            if category not in categories:
                categories[category] = {"name": category, "count": 0}
            categories[category]["count"] += 1
        
        return list(categories.values())
    except Exception as e:
        logger.error(f"Error fetching Q&A categories: {e}")
        return []

@api_router.get("/qa/featured", response_model=List[QAQuestion])
async def get_featured_qa_questions(limit: int = 5):
    """Get featured Q&A questions"""
    questions = await db_client.get_records(
        "qa_questions",
        filters={"is_featured": True},
        order_by="-created_at",
        limit=limit
    )
    return [QAQuestion(**question) for question in questions]

@api_router.get("/qa/popular", response_model=List[QAQuestion])
async def get_popular_qa_questions(limit: int = 10):
    """Get most popular Q&A questions"""
    questions = await db_client.get_records(
        "qa_questions",
        filters={},
        order_by="-views_count",
        limit=limit
    )
    return [QAQuestion(**question) for question in questions]

@api_router.get("/qa/recent", response_model=List[QAQuestion])
async def get_recent_qa_questions(limit: int = 10):
    """Get most recent Q&A questions"""
    questions = await db_client.get_records(
        "qa_questions",
        filters={},
        order_by="-created_at",
        limit=limit
    )
    return [QAQuestion(**question) for question in questions]

@api_router.get("/qa/stats", response_model=QAStats)
async def get_qa_stats():
    """Get Q&A statistics"""
    try:
        total_questions = await db_client.count_records("qa_questions")
        featured_count = await db_client.count_records("qa_questions", {"is_featured": True})
        
        # Get questions by category
        questions = await db_client.get_records("qa_questions")
        questions_by_category = {}
        total_views = 0
        
        for question in questions:
            category = question.get("category", "general")
            if category not in questions_by_category:
                questions_by_category[category] = 0
            questions_by_category[category] += 1
            total_views += question.get("views_count", 0)
        
        return QAStats(
            total_questions=total_questions,
            questions_by_category=questions_by_category,
            featured_count=featured_count,
            total_views=total_views,
            most_viewed_questions=[]
        )
    except Exception as e:
        logger.error(f"Error fetching Q&A stats: {e}")
        return QAStats(
            total_questions=0,
            questions_by_category={},
            featured_count=0,
            total_views=0,
            most_viewed_questions=[]
        )

# ====================================================================
# ADMIN Q&A MANAGEMENT ENDPOINTS
# ====================================================================

@api_router.get("/admin/qa/questions", response_model=List[QAQuestion])
async def get_admin_qa_questions(current_admin: dict = Depends(get_current_admin)):
    """Get all Q&A questions for admin"""
    questions = await db_client.get_records("qa_questions", order_by="-created_at")
    return [QAQuestion(**question) for question in questions]

@api_router.post("/admin/qa/questions", response_model=QAQuestion)
async def create_qa_question(question_data: QAQuestionCreate, current_admin: dict = Depends(get_current_admin)):
    """Create new Q&A question"""
    question_dict = question_data.dict()
    question_obj = QAQuestion(**question_dict)
    created_question = await db_client.create_record("qa_questions", question_obj.dict())
    return QAQuestion(**created_question)

@api_router.get("/admin/qa/questions/{question_id}", response_model=QAQuestion)
async def get_admin_qa_question(question_id: str, current_admin: dict = Depends(get_current_admin)):
    """Get Q&A question for admin"""
    question = await db_client.get_record("qa_questions", "id", question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return QAQuestion(**question)

@api_router.put("/admin/qa/questions/{question_id}", response_model=QAQuestion)
async def update_qa_question(
    question_id: str, 
    question_data: QAQuestionUpdate, 
    current_admin: dict = Depends(get_current_admin)
):
    """Update Q&A question"""
    question = await db_client.get_record("qa_questions", "id", question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    update_data = {k: v for k, v in question_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_question = await db_client.update_record("qa_questions", "id", question_id, update_data)
    return QAQuestion(**updated_question)

@api_router.delete("/admin/qa/questions/{question_id}")
async def delete_qa_question(question_id: str, current_admin: dict = Depends(require_admin_role)):
    """Delete Q&A question"""
    success = await db_client.delete_record("qa_questions", "id", question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}

# UNIVERSAL TABLE MANAGEMENT ENDPOINTS
@api_router.get("/admin/tables/list")
async def get_all_tables(current_admin: dict = Depends(get_current_admin)):
    """Get list of all tables in the database"""
    if not ADMIN_SUPABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Admin Supabase client not available")
    
    try:
        tables = await admin_supabase_client.get_all_tables()
        return {
            "success": True,
            "tables": tables,
            "message": "Tables retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/tables/{table_name}/structure")
async def get_table_structure(
    table_name: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Get table structure (columns, types, constraints)"""
    if not ADMIN_SUPABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Admin Supabase client not available")
    
    try:
        structure = await admin_supabase_client.get_table_structure(table_name)
        return {
            "success": True,
            "structure": structure,
            "message": "Table structure retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting table structure: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/tables/{table_name}/data")
async def get_table_data(
    table_name: str,
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """Get table data with pagination and search"""
    if not ADMIN_SUPABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Admin Supabase client not available")
    
    try:
        data = await admin_supabase_client.get_table_data(
            table_name=table_name,
            page=page,
            limit=limit,
            search=search
        )
        return {
            "success": True,
            "table_data": data,
            "message": "Table data retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting table data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/tables/{table_name}/records")
async def create_table_record(
    table_name: str,
    record_data: Dict[str, Any],
    current_admin: dict = Depends(get_current_admin)
):
    """Create a new record in the specified table"""
    if not ADMIN_SUPABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Admin Supabase client not available")
    
    try:
        result = await admin_supabase_client.create_record(table_name, record_data)
        
        if result["success"]:
            return {
                "success": True,
                "record": result["data"],
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Error creating record: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/admin/tables/{table_name}/records/{record_id}")
async def update_table_record(
    table_name: str,
    record_id: str,
    record_data: Dict[str, Any],
    current_admin: dict = Depends(get_current_admin)
):
    """Update a record in the specified table"""
    if not ADMIN_SUPABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Admin Supabase client not available")
    
    try:
        result = await admin_supabase_client.update_record(table_name, record_id, record_data)
        
        if result["success"]:
            return {
                "success": True,
                "record": result["data"],
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Error updating record: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/admin/tables/{table_name}/records/{record_id}")
async def delete_table_record(
    table_name: str,
    record_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Delete a record from the specified table"""
    if not ADMIN_SUPABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Admin Supabase client not available")
    
    try:
        result = await admin_supabase_client.delete_record(table_name, record_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Error deleting record: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================================
# PROMOCODE API ENDPOINTS
# ======================================

@api_router.post("/validate-promocode")
async def validate_promocode(validation: PromocodeValidation):
    """Проверить валидность промокода"""
    try:
        # Найти промокод в базе
        promocode = await db_client.find_one("promocodes", {"code": validation.code})
        
        if not promocode:
            raise HTTPException(status_code=404, detail="Промокод не найден")
        
        if not promocode.get("is_active", True):
            raise HTTPException(status_code=400, detail="Промокод неактивен")
        
        # Проверить срок действия
        if promocode.get("expires_at"):
            expires_at = datetime.fromisoformat(promocode["expires_at"].replace('Z', '+00:00'))
            if datetime.utcnow() > expires_at:
                raise HTTPException(status_code=400, detail="Срок действия промокода истек")
        
        # Проверить лимит использований
        if promocode.get("max_uses") and promocode.get("used_count", 0) >= promocode["max_uses"]:
            raise HTTPException(status_code=400, detail="Лимит использований промокода исчерпан")
        
        # Проверить, использовал ли уже этот пользователь промокод
        existing_usage = await db_client.find_one("promocode_usage", {
            "promocode_code": validation.code,
            "student_email": validation.student_email
        })
        
        if existing_usage:
            # Если уже использовал, просто возвращаем информацию о доступе
            return {
                "valid": True,
                "already_used": True,
                "promocode_type": promocode["promocode_type"],
                "description": promocode["description"],
                "course_ids": promocode.get("course_ids", []),
                "message": "Промокод уже был использован ранее"
            }
        
        return {
            "valid": True,
            "already_used": False,
            "promocode_type": promocode["promocode_type"],
            "description": promocode["description"],
            "course_ids": promocode.get("course_ids", []),
            "price_rub": promocode.get("price_rub"),
            "discount_percent": promocode.get("discount_percent")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating promocode: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при проверке промокода")

@api_router.post("/activate-promocode")
async def activate_promocode(validation: PromocodeValidation):
    """Активировать промокод для пользователя"""
    try:
        # Сначала валидируем промокод
        promocode = await db_client.find_one("promocodes", {"code": validation.code})
        
        if not promocode:
            raise HTTPException(status_code=404, detail="Промокод не найден")
        
        if not promocode.get("is_active", True):
            raise HTTPException(status_code=400, detail="Промокод неактивен")
        
        # Проверить, не использовал ли уже этот пользователь промокод
        existing_usage = await db_client.find_one("promocode_usage", {
            "promocode_code": validation.code,
            "student_email": validation.student_email
        })
        
        if existing_usage:
            raise HTTPException(status_code=400, detail="Промокод уже был использован")
        
        # Создать запись об использовании
        usage_data = {
            "promocode_id": promocode["id"],
            "promocode_code": validation.code,
            "student_id": str(uuid.uuid4()),  # Генерируем ID студента
            "student_email": validation.student_email,
            "course_ids": promocode.get("course_ids", []),
            "used_at": datetime.utcnow().isoformat()
        }
        
        await db_client.create_record("promocode_usage", usage_data)
        
        # Обновить счетчик использований промокода
        new_used_count = promocode.get("used_count", 0) + 1
        await db_client.update_record("promocodes", "id", promocode["id"], {
            "used_count": new_used_count,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        # Создать записи доступа к курсам если нужно
        if promocode.get("course_ids"):
            for course_id in promocode["course_ids"]:
                access_data = {
                    "student_email": validation.student_email,
                    "course_id": course_id,
                    "promocode_id": promocode["id"],
                    "granted_at": datetime.utcnow().isoformat(),
                    "is_active": True
                }
                await db_client.create_record("user_course_access", access_data)
        
        return {
            "success": True,
            "message": "Промокод успешно активирован",
            "promocode_type": promocode["promocode_type"],
            "description": promocode["description"],
            "course_ids": promocode.get("course_ids", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating promocode: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при активации промокода")

@api_router.post("/check-access")
async def check_user_access(request: Dict[str, str]):
    """Проверить доступ пользователя к разделам"""
    try:
        student_email = request.get("student_email")
        section = request.get("section")  # "lessons" или "qa"
        
        if not student_email:
            raise HTTPException(status_code=400, detail="Email пользователя обязателен")
        
        # Проверить активированные промокоды пользователя
        usages = await db_client.get_records("promocode_usage", {"student_email": student_email})
        
        access_granted = False
        access_details = []
        
        for usage in usages:
            # Получить информацию о промокоде
            promocode = await db_client.get_record("promocodes", "id", usage["promocode_id"])
            if promocode and promocode.get("is_active", True):
                if promocode["promocode_type"] == "all_courses":
                    access_granted = True
                    access_details.append({
                        "code": promocode["code"],
                        "type": "all_courses",
                        "description": promocode["description"]
                    })
                elif section == "lessons" and promocode.get("course_ids"):
                    access_granted = True
                    access_details.append({
                        "code": promocode["code"],
                        "type": "single_course",
                        "description": promocode["description"],
                        "course_ids": promocode["course_ids"]
                    })
        
        return {
            "has_access": access_granted,
            "access_details": access_details,
            "student_email": student_email,
            "section": section
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking user access: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при проверке доступа")

@api_router.get("/promocodes/{code}")
async def get_promocode_info(code: str):
    """Получить публичную информацию о промокоде"""
    try:
        promocode = await db_client.find_one("promocodes", {"code": code})
        
        if not promocode:
            raise HTTPException(status_code=404, detail="Промокод не найден")
        
        if not promocode.get("is_active", True):
            raise HTTPException(status_code=400, detail="Промокод неактивен")
        
        # Возвращаем только публичную информацию
        return {
            "code": promocode["code"],
            "description": promocode["description"],
            "promocode_type": promocode["promocode_type"],
            "price_rub": promocode.get("price_rub"),
            "discount_percent": promocode.get("discount_percent"),
            "is_active": promocode.get("is_active", True),
            "expires_at": promocode.get("expires_at"),
            "usage_stats": {
                "used_count": promocode.get("used_count", 0),
                "max_uses": promocode.get("max_uses")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting promocode info: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении информации о промокоде")

@api_router.post("/admin/tables/{table_name}/query")
async def execute_custom_query(
    table_name: str,
    query_data: Dict[str, str],
    current_admin: dict = Depends(get_current_admin)
):
    """Execute a custom query on the table (use with caution)"""
    if not ADMIN_SUPABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Admin Supabase client not available")
    
    try:
        custom_query = query_data.get("query", "")
        if not custom_query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        result = await admin_supabase_client.execute_custom_query(custom_query)
        
        if result["success"]:
            return {
                "success": True,
                "data": result["data"],
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Error executing custom query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        "http://localhost:3000",
        "https://*.replit.dev", 
        "https://*.replit.co",
        "https://*.replit.app",
        "https://*.repl.co",
        "*"
    ],
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
    """Initialize default data and ensure quality content"""
    logger.info("Starting application with Supabase integration...")
    
    # Check if admins exist
    try:
        admin_count = await db_client.count_records("admin_users")
        logger.info(f"Found {admin_count} admin users in database")
        
        # Check existing team members
        team_count = await db_client.count_records("team_members")
        logger.info(f"Found {team_count} team members in database")
        
        # Check courses
        course_count = await db_client.count_records("courses", {"status": "published"})
        logger.info(f"Found {course_count} published courses in database")
        
        # Run autostart to ensure quality data
        logger.info("Running Supabase autostart to ensure quality data...")
        try:
            import subprocess
            import sys
            result = subprocess.run([
                sys.executable, 
                str(ROOT_DIR / "autostart_supabase.py")
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("✅ Supabase autostart completed successfully")
            else:
                logger.warning(f"⚠️ Supabase autostart issues: {result.stderr}")
        except Exception as e:
            logger.warning(f"⚠️ Could not run autostart: {e}")
        
        logger.info("Application startup completed with Supabase integration")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")