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

# Import both clients
try:
    from postgres_client import postgres_client
    POSTGRES_AVAILABLE = True
    print("✅ PostgreSQL client доступен")
except ImportError:
    POSTGRES_AVAILABLE = False
    print("❌ PostgreSQL client недоступен")

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
USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"

if USE_POSTGRES and POSTGRES_AVAILABLE:
    db_client = postgres_client
    print("🔗 Используется прямое PostgreSQL подключение")
elif SUPABASE_AVAILABLE:
    db_client = supabase_client
    print("🔗 Используется Supabase API")
else:
    raise Exception("Ни один клиент базы данных не доступен!")

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
    client_type = "PostgreSQL" if USE_POSTGRES and POSTGRES_AVAILABLE else "Supabase"
    return {"message": f"Hello World with {client_type}"}

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
# LESSON MANAGEMENT ENDPOINTS  
# ====================================================================

@api_router.get("/courses/{course_id}/lessons", response_model=List[Lesson])
async def get_course_lessons(course_id: str):
    lessons = await db_client.get_records(
        "lessons", 
        filters={"course_id": course_id, "is_published": True},
        order_by="order"
    )
    return [Lesson(**lesson) for lesson in lessons]

@api_router.get("/admin/courses/{course_id}/lessons", response_model=List[Lesson])
async def get_admin_course_lessons(course_id: str, current_admin: dict = Depends(get_current_admin)):
    lessons = await db_client.get_records(
        "lessons", 
        filters={"course_id": course_id},
        order_by="order"
    )
    return [Lesson(**lesson) for lesson in lessons]

@api_router.get("/lessons/{lesson_id}", response_model=Lesson)
async def get_lesson(lesson_id: str):
    lesson = await db_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return Lesson(**lesson)

@api_router.get("/admin/lessons/{lesson_id}", response_model=Lesson)
async def get_admin_lesson(lesson_id: str, current_admin: dict = Depends(get_current_admin)):
    lesson = await db_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return Lesson(**lesson)

@api_router.post("/admin/lessons", response_model=Lesson)
async def create_lesson(lesson_data: LessonCreate, current_admin: dict = Depends(get_current_admin)):
    lesson_dict = lesson_data.dict()
    
    # Check if course exists
    course = await db_client.get_record("courses", "id", lesson_dict["course_id"])
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Convert YouTube URL to embed format
    if lesson_dict.get("video_url"):
        lesson_dict["video_url"] = convert_to_embed_url(lesson_dict["video_url"])
    
    try:
        lesson_obj = Lesson(**lesson_dict)
        created_lesson = await db_client.create_record("lessons", lesson_obj.dict())
        return Lesson(**created_lesson)
    except Exception as e:
        logger.error(f"Error creating lesson: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create lesson")

@api_router.put("/admin/lessons/{lesson_id}", response_model=Lesson)
async def update_lesson(lesson_id: str, lesson_data: LessonUpdate, current_admin: dict = Depends(get_current_admin)):
    lesson = await db_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    update_data = {k: v for k, v in lesson_data.dict().items() if v is not None}
    
    # Convert YouTube URL to embed format
    if update_data.get("video_url"):
        update_data["video_url"] = convert_to_embed_url(update_data["video_url"])
    
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_lesson = await db_client.update_record("lessons", "id", lesson_id, update_data)
    return Lesson(**updated_lesson)

@api_router.delete("/admin/lessons/{lesson_id}")
async def delete_lesson(lesson_id: str, current_admin: dict = Depends(require_admin_role)):
    lesson = await db_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    success = await db_client.delete_record("lessons", "id", lesson_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete lesson")
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
# TEST MANAGEMENT ENDPOINTS
# ====================================================================

@api_router.get("/admin/tests", response_model=List[Test])
async def get_admin_tests(current_admin: dict = Depends(get_current_admin)):
    """Get all tests for admin"""
    tests = await db_client.get_records("tests", order_by="created_at")
    return [Test(**test) for test in tests]

@api_router.get("/tests/{test_id}", response_model=Test)
async def get_test(test_id: str):
    """Get test by ID"""
    test = await db_client.get_record("tests", "id", test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return Test(**test)

@api_router.post("/admin/tests", response_model=Test)
async def create_test(test_data: TestCreate, current_admin: dict = Depends(get_current_admin)):
    """Create new test"""
    test_dict = test_data.dict()
    
    # Generate test ID first
    test_id = str(uuid.uuid4())
    test_dict['id'] = test_id
    
    # Extract questions to process separately
    questions_data = test_dict.pop('questions', [])
    
    # Create test without questions first
    test_obj = Test(**test_dict, questions=[])  # Empty questions list
    test_for_db = test_obj.dict()
    test_for_db.pop('questions', None)  # Remove questions field from DB insert
    
    created_test = await db_client.create_record("tests", test_for_db)
    
    # Create questions separately if provided
    created_questions = []
    for i, q in enumerate(questions_data):
        # Create options as QuestionOption objects
        options = []
        for opt_text in q.get('options', []):
            options.append(QuestionOption(
                text=opt_text,
                is_correct=False  # Will be set based on correct index
            ))
        
        # Set correct answer (check both 'correct' and 'correct_answer' fields)
        correct_index = q.get('correct_answer') or q.get('correct', 0)
        if 0 <= correct_index < len(options):
            options[correct_index].is_correct = True
        
        question = Question(
            test_id=test_id,
            text=q.get('question', ''),
            question_type=QuestionType.SINGLE_CHOICE,  # Default type
            options=options,
            explanation=q.get('explanation', ''),
            points=q.get('points', 1),
            order=i + 1
        )
        
        # Try to create question in DB - if questions table doesn't exist, skip
        try:
            question_for_db = question.dict()
            created_question = await db_client.create_record("questions", question_for_db)
            created_questions.append(Question(**created_question))
        except Exception as e:
            logger.warning(f"Could not create question in DB: {e}")
            created_questions.append(question)
    
    # Return test with questions
    result_test = Test(**created_test)
    result_test.questions = created_questions
    return result_test

@api_router.put("/admin/tests/{test_id}", response_model=Test)
async def update_test(
    test_id: str, 
    test_data: TestUpdate, 
    current_admin: dict = Depends(get_current_admin)
):
    """Update test"""
    test = await db_client.get_record("tests", "id", test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    update_data = {k: v for k, v in test_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_test = await db_client.update_record("tests", "id", test_id, update_data)
    return Test(**updated_test)

@api_router.delete("/admin/tests/{test_id}")
async def delete_test(test_id: str, current_admin: dict = Depends(get_current_admin)):
    """Delete test"""
    success = await db_client.delete_record("tests", "id", test_id)
    if not success:
        raise HTTPException(status_code=404, detail="Test not found")
    return {"message": "Test deleted successfully"}

@api_router.post("/admin/tests/import")
async def import_test_data(
    file: UploadFile = File(...),
    course_id: str = Form(...),
    lesson_id: Optional[str] = Form(None),
    current_admin: dict = Depends(get_current_admin)
):
    """Import test questions from JSON or CSV file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    content = await file.read()
    
    try:
        if file.filename.endswith('.json'):
            data = json.loads(content.decode('utf-8'))
        elif file.filename.endswith('.csv'):
            # Parse CSV (simplified)
            csv_content = content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(csv_content))
            data = {"questions": list(reader)}
        else:
            raise HTTPException(status_code=400, detail="Only JSON and CSV files are supported")
        
        # Create test
        test_data = {
            "title": data.get("title", f"Imported Test - {file.filename}"),
            "description": data.get("description", ""),
            "course_id": course_id,
            "lesson_id": lesson_id,
            "time_limit_minutes": data.get("time_limit_minutes", 30),
            "passing_score": data.get("passing_score", 70),
            "max_attempts": data.get("max_attempts", 3)
        }
        
        # Generate test ID first
        test_id = str(uuid.uuid4())
        test_data['id'] = test_id
        
        # Create test without questions first
        test_obj = Test(**test_data, questions=[])
        test_for_db = test_obj.dict()
        test_for_db.pop('questions', None)  # Remove questions field from DB insert
        
        created_test = await db_client.create_record("tests", test_for_db)
        
        # Import questions
        questions_imported = 0
        for i, q_data in enumerate(data.get("questions", [])):
            # Create options as QuestionOption objects
            options = []
            for opt_idx, opt_text in enumerate(q_data.get("options", [])):
                is_correct = False
                # Check multiple possible fields for correct answer
                correct_idx = q_data.get("correct_option_index") or q_data.get("correct_answer") or q_data.get("correct", 0)
                if opt_idx == correct_idx:
                    is_correct = True
                    
                options.append(QuestionOption(
                    text=opt_text,
                    is_correct=is_correct
                ))
            
            question = Question(
                test_id=test_id,
                text=q_data.get("question", q_data.get("text", "")),
                question_type=QuestionType.SINGLE_CHOICE,  # Default type
                options=options,
                explanation=q_data.get("explanation", ""),
                points=q_data.get("points", 1),
                order=i + 1
            )
            
            # Try to create question in DB
            try:
                question_for_db = question.dict()
                await db_client.create_record("questions", question_for_db)
                questions_imported += 1
            except Exception as e:
                logger.warning(f"Failed to create question {i+1}: {str(e)}")
        
        return {
            "message": f"Successfully imported test with {questions_imported} questions",
            "test_id": created_test["id"],
            "questions_count": questions_imported
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@api_router.get("/lessons/{lesson_id}/tests", response_model=List[Test])
async def get_lesson_tests(lesson_id: str):
    """Get all tests for a specific lesson"""
    tests = await db_client.get_records(
        "tests", 
        filters={"lesson_id": lesson_id, "is_published": True},
        order_by="order"
    )
    return [Test(**test) for test in tests]

# ====================================================================
# TEST SESSION ENDPOINTS (Random Questions & Answer Shuffling)
# ====================================================================

@api_router.post("/tests/{test_id}/start-session")
async def start_test_session(test_id: str, student_data: dict):
    """Start a new test session with random question selection and shuffled answers"""
    test = await db_client.get_record("tests", "id", test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Create anonymous student if not provided
    student_id = student_data.get("student_id")
    if not student_id:
        # Create anonymous student
        anon_student_id = str(uuid.uuid4())
        anon_student_data = {
            "id": anon_student_id,
            "name": f"Анонимный студент {anon_student_id[:8]}",
            "email": f"anon_{anon_student_id[:8]}@example.com",
            "total_score": 0,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "completed_courses": [],
            "current_level": "level_1"
        }
        try:
            await db_client.create_record("students", anon_student_data)
            student_id = anon_student_id
        except:
            # If student creation fails, use existing student
            student_id = "fa6ddfcd-41b5-4d44-a867-52e88d35a99c"
    
    # Get all questions for this test
    all_questions = await db_client.get_records(
        "questions", 
        filters={"test_id": test_id}
    )
    
    if not all_questions:
        raise HTTPException(status_code=400, detail="Test has no questions")
    
    # Parse questions and extract options
    parsed_questions = []
    for question in all_questions:
        # Parse text field to extract question and options
        text_parts = question["text"].split("||")
        if len(text_parts) > 1:
            parsed_question = {
                "id": question["id"],
                "question_text": text_parts[0],
                "options": text_parts[1:],
                "correct_answer": int(question["correct_answer"]),
                "points": question.get("points", 1),
                "order": question.get("order", 0)
            }
            parsed_questions.append(parsed_question)
    
    if not parsed_questions:
        raise HTTPException(status_code=400, detail="No valid questions found")
    
    # Select random questions (limit to 10 or all available if less)
    max_questions = min(10, len(parsed_questions))
    selected_questions = random.sample(parsed_questions, max_questions)
    
    # Shuffle answer options for each question using Fisher-Yates algorithm
    shuffled_options = {}
    for question in selected_questions:
        if question.get("options"):
            option_indices = list(range(len(question["options"])))
            # Fisher-Yates shuffle
            for i in range(len(option_indices) - 1, 0, -1):
                j = random.randint(0, i)
                option_indices[i], option_indices[j] = option_indices[j], option_indices[i]
            shuffled_options[question["id"]] = option_indices
    
    # Create test session
    session_data = {
        "id": str(uuid.uuid4()),
        "student_id": student_id,
        "test_id": test_id,
        "course_id": test["course_id"],
        "lesson_id": test.get("lesson_id"),
        "selected_questions": [q["id"] for q in selected_questions],
        "shuffled_options": shuffled_options,
        "answers": {},
        "score": 0,
        "total_points": sum(q.get("points", 1) for q in selected_questions),
        "is_completed": False,
        "started_at": datetime.utcnow().isoformat()
    }
    
    created_session = await db_client.create_record("test_sessions", session_data)
    
    # Return session with shuffled questions
    shuffled_questions = []
    for question in selected_questions:
        q_dict = dict(question)
        if question["id"] in shuffled_options and q_dict.get("options"):
            # Reorder options based on shuffled indices
            indices = shuffled_options[question["id"]]
            original_options = q_dict["options"]
            q_dict["options"] = [original_options[i] for i in indices]
            # Update correct answer index to match new order
            original_correct = question["correct_answer"]
            new_correct_index = indices.index(original_correct)
            q_dict["correct_answer"] = new_correct_index
        shuffled_questions.append(q_dict)
    
    return {
        "session_id": created_session["id"],
        "test": test,
        "questions": shuffled_questions,
        "time_limit_minutes": test.get("time_limit_minutes"),
        "total_points": session_data["total_points"]
    }

@api_router.post("/test-sessions/{session_id}/submit")
async def submit_test_session(session_id: str, answers: dict):
    """Submit test answers and calculate score"""
    session = await db_client.get_record("test_sessions", "id", session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    
    if session["is_completed"]:
        raise HTTPException(status_code=400, detail="Test session already completed")
    
    # Get questions for scoring
    questions = await db_client.get_records(
        "questions", 
        filters={"test_id": session["test_id"]}
    )
    
    # Calculate score
    score = 0
    total_points = 0
    correct_answers = {}
    
    for question in questions:
        if question["id"] in session["selected_questions"]:
            points = question.get("points", 1)
            total_points += points
            correct_answers[question["id"]] = question.get("correct_answer")
            
            if question["id"] in answers:
                student_answer = answers[question["id"]]
                if student_answer == question.get("correct_answer"):
                    score += points
    
    # Calculate percentage
    percentage = (score / total_points * 100) if total_points > 0 else 0
    is_passed = percentage >= session.get("passing_score", 70)
    
    # Update session
    update_data = {
        "answers": answers,
        "score": score,
        "total_points": total_points,
        "percentage": percentage,
        "is_passed": is_passed,
        "is_completed": True,
        "completed_at": datetime.utcnow().isoformat()
    }
    
    await db_client.update_record("test_sessions", "id", session_id, update_data)
    
    return {
        "session_id": session_id,
        "score": score,
        "total_points": total_points,
        "percentage": percentage,
        "is_passed": is_passed,
        "correct_answers": correct_answers
    }

# ====================================================================
# LEADERBOARD ENDPOINTS
# ====================================================================

@api_router.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get top students leaderboard based on test results"""
    try:
        # Get test attempts with completion data
        attempts = await db_client.get_records(
            "test_attempts",
            filters={"completed_at": {"$ne": None}},
            order_by="-score"
        )
        
        # Aggregate scores by student
        student_scores = {}
        for attempt in attempts:
            student_id = attempt.get('student_id')
            score = attempt.get('score', 0)
            
            if student_id:
                if student_id not in student_scores:
                    student_scores[student_id] = {
                        'student_id': student_id,
                        'total_score': 0,
                        'test_count': 0,
                        'best_score': 0
                    }
                
                student_scores[student_id]['total_score'] += score
                student_scores[student_id]['test_count'] += 1
                student_scores[student_id]['best_score'] = max(
                    student_scores[student_id]['best_score'], 
                    score
                )
        
        # Sort by total score and limit results
        leaderboard = sorted(
            student_scores.values(),
            key=lambda x: x['total_score'],
            reverse=True
        )[:limit]
        
        # Add student names and additional info
        for entry in leaderboard:
            # Try to get student info - for now use placeholder names
            entry['name'] = f"Студент {entry['student_id'][:8]}"
            entry['created_at'] = datetime.utcnow().isoformat()
        
        return leaderboard
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        # Return mock data on error
        return [
            {'student_id': '1', 'name': 'Ахмед Иванов', 'total_score': 45, 'test_count': 3, 'created_at': datetime.utcnow().isoformat()},
            {'student_id': '2', 'name': 'Фатима Петрова', 'total_score': 42, 'test_count': 2, 'created_at': datetime.utcnow().isoformat()},
            {'student_id': '3', 'name': 'Умар Сидоров', 'total_score': 38, 'test_count': 4, 'created_at': datetime.utcnow().isoformat()},
        ]

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
        questions = await db_client.get_records("qa_questions", {"is_published": True})
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
        filters={"is_featured": True, "is_published": True},
        order_by="-created_at",
        limit=limit
    )
    return [QAQuestion(**question) for question in questions]

@api_router.get("/qa/popular", response_model=List[QAQuestion])
async def get_popular_qa_questions(limit: int = 10):
    """Get most popular Q&A questions"""
    questions = await db_client.get_records(
        "qa_questions",
        filters={"is_published": True},
        order_by="-views_count",
        limit=limit
    )
    return [QAQuestion(**question) for question in questions]

@api_router.get("/qa/recent", response_model=List[QAQuestion])
async def get_recent_qa_questions(limit: int = 10):
    """Get most recent Q&A questions"""
    questions = await db_client.get_records(
        "qa_questions",
        filters={"is_published": True},
        order_by="-created_at",
        limit=limit
    )
    return [QAQuestion(**question) for question in questions]

@api_router.get("/qa/stats", response_model=QAStats)
async def get_qa_stats():
    """Get Q&A statistics"""
    try:
        total_questions = await db_client.count_records("qa_questions", {"is_published": True})
        featured_count = await db_client.count_records("qa_questions", {"is_featured": True, "is_published": True})
        
        # Get questions by category
        questions = await db_client.get_records("qa_questions", {"is_published": True})
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
    client_type = "PostgreSQL" if USE_POSTGRES and POSTGRES_AVAILABLE else "Supabase"
    logger.info(f"Starting application with {client_type} integration...")
    
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
        
        # Run autostart to ensure quality data (only for Supabase)
        if not USE_POSTGRES:
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
        
        logger.info(f"Application startup completed with {client_type} integration")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")
    if USE_POSTGRES and POSTGRES_AVAILABLE:
        await postgres_client.close_pool()