from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import asyncio
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Уроки Ислама API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Enums
class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class CourseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Admin Models
class AdminUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

class AdminUserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: UserRole = UserRole.MODERATOR

class AdminLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Course Models
class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    teacher_id: str
    teacher_name: str
    status: CourseStatus = CourseStatus.DRAFT
    difficulty: str
    duration_minutes: int
    questions_count: int
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CourseCreate(BaseModel):
    title: str
    description: str
    teacher_id: str
    teacher_name: str
    difficulty: str
    duration_minutes: int
    questions_count: int
    image_url: Optional[str] = None

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    teacher_id: Optional[str] = None
    teacher_name: Optional[str] = None
    status: Optional[CourseStatus] = None
    difficulty: Optional[str] = None
    duration_minutes: Optional[int] = None
    questions_count: Optional[int] = None
    image_url: Optional[str] = None

# Student Models
class Student(BaseModel):
    id: str
    name: str
    email: str
    total_score: int = 0
    is_active: bool = True
    created_at: datetime
    last_activity: Optional[datetime] = None
    completed_courses: List[str] = []

class StudentUpdate(BaseModel):
    is_active: Optional[bool] = None
    notes: Optional[str] = None

# Teacher Models
class Teacher(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    subject: str
    bio: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    courses_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TeacherCreate(BaseModel):
    name: str
    email: str
    subject: str
    bio: Optional[str] = None
    image_url: Optional[str] = None

# Application Models
class Application(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_name: str
    student_email: str
    course_id: str
    course_title: str
    message: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.PENDING
    admin_comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ApplicationCreate(BaseModel):
    student_name: str
    student_email: str
    course_id: str
    course_title: str
    message: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: ApplicationStatus
    admin_comment: Optional[str] = None

# Statistics Models
class DashboardStats(BaseModel):
    total_students: int
    total_courses: int
    total_teachers: int
    active_students: int
    pending_applications: int
    completed_tests_today: int

class CourseStats(BaseModel):
    course_id: str
    course_title: str
    enrolled_students: int
    completed_tests: int
    average_score: float
    completion_rate: float

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
    
    admin = await db.admins.find_one({"username": username})
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

# Original routes
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Admin Authentication Routes
@api_router.post("/admin/login", response_model=Token)
async def admin_login(admin_data: AdminLogin):
    admin = await db.admins.find_one({"username": admin_data.username})
    if not admin or not verify_password(admin_data.password, admin["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await db.admins.update_one(
        {"username": admin_data.username},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    access_token = create_access_token(data={"sub": admin["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/admin/register", response_model=AdminUser)
async def create_admin(admin_data: AdminUserCreate, current_admin: dict = Depends(require_admin_role)):
    # Check if username or email already exists
    existing_admin = await db.admins.find_one({
        "$or": [{"username": admin_data.username}, {"email": admin_data.email}]
    })
    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )
    
    admin_dict = admin_data.dict()
    admin_dict["hashed_password"] = get_password_hash(admin_dict.pop("password"))
    admin_obj = AdminUser(**admin_dict)
    
    await db.admins.insert_one(admin_obj.dict())
    return admin_obj

@api_router.get("/admin/me", response_model=AdminUser)
async def get_current_admin_info(current_admin: dict = Depends(get_current_admin)):
    return AdminUser(**current_admin)

# Dashboard Routes
@api_router.get("/admin/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(current_admin: dict = Depends(get_current_admin)):
    # Get statistics from different collections
    total_students = await db.students.count_documents({})
    total_courses = await db.courses.count_documents({})
    total_teachers = await db.teachers.count_documents({})
    active_students = await db.students.count_documents({"is_active": True})
    pending_applications = await db.applications.count_documents({"status": ApplicationStatus.PENDING})
    
    # Get today's completed tests
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    completed_tests_today = await db.scores.count_documents({
        "timestamp": {"$gte": today}
    })
    
    return DashboardStats(
        total_students=total_students,
        total_courses=total_courses,
        total_teachers=total_teachers,
        active_students=active_students,
        pending_applications=pending_applications,
        completed_tests_today=completed_tests_today
    )

# Course Management Routes
@api_router.get("/admin/courses", response_model=List[Course])
async def get_courses(current_admin: dict = Depends(get_current_admin)):
    courses = await db.courses.find().to_list(1000)
    return [Course(**course) for course in courses]

@api_router.post("/admin/courses", response_model=Course)
async def create_course(course_data: CourseCreate, current_admin: dict = Depends(get_current_admin)):
    course_dict = course_data.dict()
    course_obj = Course(**course_dict)
    await db.courses.insert_one(course_obj.dict())
    return course_obj

@api_router.put("/admin/courses/{course_id}", response_model=Course)
async def update_course(course_id: str, course_data: CourseUpdate, current_admin: dict = Depends(get_current_admin)):
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    update_data = {k: v for k, v in course_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.courses.update_one({"id": course_id}, {"$set": update_data})
    
    updated_course = await db.courses.find_one({"id": course_id})
    return Course(**updated_course)

@api_router.delete("/admin/courses/{course_id}")
async def delete_course(course_id: str, current_admin: dict = Depends(require_admin_role)):
    result = await db.courses.delete_one({"id": course_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted successfully"}

# Student Management Routes
@api_router.get("/admin/students", response_model=List[Student])
async def get_students(current_admin: dict = Depends(get_current_admin)):
    students = await db.students.find().to_list(1000)
    return [Student(**student) for student in students]

@api_router.put("/admin/students/{student_id}")
async def update_student(student_id: str, student_data: StudentUpdate, current_admin: dict = Depends(get_current_admin)):
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = {k: v for k, v in student_data.dict().items() if v is not None}
    await db.students.update_one({"id": student_id}, {"$set": update_data})
    
    return {"message": "Student updated successfully"}

# Teacher Management Routes
@api_router.get("/admin/teachers", response_model=List[Teacher])
async def get_teachers(current_admin: dict = Depends(get_current_admin)):
    teachers = await db.teachers.find().to_list(1000)
    return [Teacher(**teacher) for teacher in teachers]

@api_router.post("/admin/teachers", response_model=Teacher)
async def create_teacher(teacher_data: TeacherCreate, current_admin: dict = Depends(get_current_admin)):
    teacher_dict = teacher_data.dict()
    teacher_obj = Teacher(**teacher_dict)
    await db.teachers.insert_one(teacher_obj.dict())
    return teacher_obj

@api_router.put("/admin/teachers/{teacher_id}", response_model=Teacher)
async def update_teacher(teacher_id: str, teacher_data: TeacherCreate, current_admin: dict = Depends(get_current_admin)):
    teacher = await db.teachers.find_one({"id": teacher_id})
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    update_data = teacher_data.dict()
    await db.teachers.update_one({"id": teacher_id}, {"$set": update_data})
    
    updated_teacher = await db.teachers.find_one({"id": teacher_id})
    return Teacher(**updated_teacher)

@api_router.delete("/admin/teachers/{teacher_id}")
async def delete_teacher(teacher_id: str, current_admin: dict = Depends(require_admin_role)):
    result = await db.teachers.delete_one({"id": teacher_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return {"message": "Teacher deleted successfully"}

# Application Management Routes
@api_router.get("/admin/applications", response_model=List[Application])
async def get_applications(current_admin: dict = Depends(get_current_admin)):
    applications = await db.applications.find().sort("created_at", -1).to_list(1000)
    return [Application(**app) for app in applications]

@api_router.put("/admin/applications/{application_id}", response_model=Application)
async def update_application(application_id: str, app_data: ApplicationUpdate, current_admin: dict = Depends(get_current_admin)):
    application = await db.applications.find_one({"id": application_id})
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    update_data = app_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    await db.applications.update_one({"id": application_id}, {"$set": update_data})
    
    updated_app = await db.applications.find_one({"id": application_id})
    return Application(**updated_app)

# Reports and Statistics Routes
@api_router.get("/admin/reports/courses", response_model=List[CourseStats])
async def get_course_statistics(current_admin: dict = Depends(get_current_admin)):
    # This would normally involve complex aggregation queries
    # For now, returning mock data structure
    courses = await db.courses.find().to_list(100)
    stats = []
    
    for course in courses:
        # Get course statistics
        enrolled_count = await db.enrollments.count_documents({"course_id": course["id"]})
        completed_tests = await db.scores.count_documents({"lessonId": course["id"]})
        
        # Calculate average score
        pipeline = [
            {"$match": {"lessonId": course["id"]}},
            {"$group": {"_id": None, "avg_score": {"$avg": "$score"}}}
        ]
        avg_result = await db.scores.aggregate(pipeline).to_list(1)
        avg_score = avg_result[0]["avg_score"] if avg_result else 0.0
        
        completion_rate = (completed_tests / enrolled_count * 100) if enrolled_count > 0 else 0.0
        
        stats.append(CourseStats(
            course_id=course["id"],
            course_title=course["title"],
            enrolled_students=enrolled_count,
            completed_tests=completed_tests,
            average_score=round(avg_score, 2),
            completion_rate=round(completion_rate, 2)
        ))
    
    return stats

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
    """Initialize default admin user if none exists"""
    admin_count = await db.admins.count_documents({})
    if admin_count == 0:
        default_admin = AdminUser(
            username="admin",
            email="admin@uroki-islama.ru",
            full_name="Администратор",
            role=UserRole.SUPER_ADMIN
        )
        admin_dict = default_admin.dict()
        admin_dict["hashed_password"] = get_password_hash("admin123")
        await db.admins.insert_one(admin_dict)
        logger.info("Default admin user created: admin/admin123")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()