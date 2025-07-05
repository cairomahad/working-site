from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
    created_status = await supabase_client.create_record("status_checks", status_obj.dict())
    return StatusCheck(**created_status)

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await supabase_client.get_records("status_checks", limit=1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# ====================================================================
# AUTHENTICATION ENDPOINTS
# ====================================================================

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

# ====================================================================
# DASHBOARD ENDPOINTS
# ====================================================================

@api_router.get("/admin/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(current_admin: dict = Depends(get_current_admin)):
    total_students = await supabase_client.count_records("students")
    total_courses = await supabase_client.count_records("courses")
    total_lessons = await supabase_client.count_records("lessons")
    total_tests = await supabase_client.count_records("tests")
    total_teachers = await supabase_client.count_records("teachers")
    active_students = await supabase_client.count_records("students", {"is_active": True})
    pending_applications = await supabase_client.count_records("applications", {"status": "pending"})
    
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

# ====================================================================
# COURSE MANAGEMENT ENDPOINTS
# ====================================================================

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

@api_router.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str):
    course = await supabase_client.get_record("courses", "id", course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return Course(**course)

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

@api_router.delete("/admin/courses/{course_id}")
async def delete_course(course_id: str, current_admin: dict = Depends(require_admin_role)):
    course = await supabase_client.get_record("courses", "id", course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    success = await supabase_client.delete_record("courses", "id", course_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete course")
    return {"message": "Course deleted successfully"}

# ====================================================================
# LESSON MANAGEMENT ENDPOINTS
# ====================================================================

@api_router.get("/courses/{course_id}/lessons", response_model=List[Lesson])
async def get_course_lessons(course_id: str):
    lessons = await supabase_client.get_records(
        "lessons", 
        filters={"course_id": course_id, "is_published": True},
        order_by="order"
    )
    return [Lesson(**lesson) for lesson in lessons]

@api_router.get("/admin/courses/{course_id}/lessons", response_model=List[Lesson])
async def get_admin_course_lessons(course_id: str, current_admin: dict = Depends(get_current_admin)):
    lessons = await supabase_client.get_records(
        "lessons", 
        filters={"course_id": course_id},
        order_by="order"
    )
    return [Lesson(**lesson) for lesson in lessons]

@api_router.get("/lessons/{lesson_id}", response_model=Lesson)
async def get_lesson(lesson_id: str):
    lesson = await supabase_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return Lesson(**lesson)

@api_router.get("/admin/lessons/{lesson_id}", response_model=Lesson)
async def get_admin_lesson(lesson_id: str, current_admin: dict = Depends(get_current_admin)):
    lesson = await supabase_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return Lesson(**lesson)

@api_router.post("/admin/lessons", response_model=Lesson)
async def create_lesson(lesson_data: LessonCreate, current_admin: dict = Depends(get_current_admin)):
    lesson_dict = lesson_data.dict()
    
    # Convert YouTube URL to embed format
    if lesson_dict.get("video_url"):
        lesson_dict["video_url"] = convert_to_embed_url(lesson_dict["video_url"])
    
    lesson_obj = Lesson(**lesson_dict)
    created_lesson = await supabase_client.create_record("lessons", lesson_obj.dict())
    return Lesson(**created_lesson)

@api_router.put("/admin/lessons/{lesson_id}", response_model=Lesson)
async def update_lesson(lesson_id: str, lesson_data: LessonUpdate, current_admin: dict = Depends(get_current_admin)):
    lesson = await supabase_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    update_data = {k: v for k, v in lesson_data.dict().items() if v is not None}
    
    # Convert YouTube URL to embed format
    if update_data.get("video_url"):
        update_data["video_url"] = convert_to_embed_url(update_data["video_url"])
    
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_lesson = await supabase_client.update_record("lessons", "id", lesson_id, update_data)
    return Lesson(**updated_lesson)

@api_router.delete("/admin/lessons/{lesson_id}")
async def delete_lesson(lesson_id: str, current_admin: dict = Depends(require_admin_role)):
    lesson = await supabase_client.get_record("lessons", "id", lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    success = await supabase_client.delete_record("lessons", "id", lesson_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete lesson")
    return {"message": "Lesson deleted successfully"}

# ====================================================================
# TEST MANAGEMENT ENDPOINTS
# ====================================================================

@api_router.get("/lessons/{lesson_id}/tests", response_model=List[Test])
async def get_lesson_tests(lesson_id: str):
    tests = await supabase_client.get_records(
        "tests", 
        filters={"lesson_id": lesson_id, "is_published": True},
        order_by="order"
    )
    return [Test(**test) for test in tests]

@api_router.get("/admin/tests", response_model=List[Test])
async def get_admin_tests(current_admin: dict = Depends(get_current_admin)):
    tests = await supabase_client.get_records("tests", order_by="created_at")
    return [Test(**test) for test in tests]

@api_router.get("/tests/{test_id}", response_model=Test)
async def get_test(test_id: str):
    test = await supabase_client.get_record("tests", "id", test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return Test(**test)

@api_router.post("/admin/tests", response_model=Test)
async def create_test(test_data: TestCreate, current_admin: dict = Depends(get_current_admin)):
    test_dict = test_data.dict()
    test_obj = Test(**test_dict)
    created_test = await supabase_client.create_record("tests", test_obj.dict())
    return Test(**created_test)

@api_router.put("/admin/tests/{test_id}", response_model=Test)
async def update_test(test_id: str, test_data: TestUpdate, current_admin: dict = Depends(get_current_admin)):
    test = await supabase_client.get_record("tests", "id", test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    update_data = {k: v for k, v in test_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_test = await supabase_client.update_record("tests", "id", test_id, update_data)
    return Test(**updated_test)

@api_router.delete("/admin/tests/{test_id}")
async def delete_test(test_id: str, current_admin: dict = Depends(require_admin_role)):
    test = await supabase_client.get_record("tests", "id", test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    success = await supabase_client.delete_record("tests", "id", test_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete test")
    return {"message": "Test deleted successfully"}

# ====================================================================
# QUESTION MANAGEMENT ENDPOINTS
# ====================================================================

@api_router.get("/admin/tests/{test_id}/questions", response_model=List[Question])
async def get_test_questions(test_id: str, current_admin: dict = Depends(get_current_admin)):
    questions = await supabase_client.get_records(
        "questions", 
        filters={"test_id": test_id},
        order_by="order"
    )
    return [Question(**question) for question in questions]

@api_router.post("/admin/questions", response_model=Question)
async def create_question(question_data: QuestionCreate, current_admin: dict = Depends(get_current_admin)):
    question_dict = question_data.dict()
    question_obj = Question(**question_dict)
    created_question = await supabase_client.create_record("questions", question_obj.dict())
    return Question(**created_question)

@api_router.put("/admin/questions/{question_id}", response_model=Question)
async def update_question(question_id: str, question_data: QuestionUpdate, current_admin: dict = Depends(get_current_admin)):
    question = await supabase_client.get_record("questions", "id", question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    update_data = {k: v for k, v in question_data.dict().items() if v is not None}
    
    updated_question = await supabase_client.update_record("questions", "id", question_id, update_data)
    return Question(**updated_question)

@api_router.delete("/admin/questions/{question_id}")
async def delete_question(question_id: str, current_admin: dict = Depends(require_admin_role)):
    question = await supabase_client.get_record("questions", "id", question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    success = await supabase_client.delete_record("questions", "id", question_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete question")
    return {"message": "Question deleted successfully"}

# ====================================================================
# TEST SESSION ENDPOINTS (Random Questions & Answer Shuffling)
# ====================================================================

@api_router.post("/tests/{test_id}/start-session")
async def start_test_session(test_id: str, student_data: dict):
    """Start a new test session with random question selection and shuffled answers"""
    test = await supabase_client.get_record("tests", "id", test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Get all questions for this test
    all_questions = await supabase_client.get_records(
        "questions", 
        filters={"test_id": test_id}
    )
    
    if not all_questions:
        raise HTTPException(status_code=400, detail="Test has no questions")
    
    # Select random questions (limit to 10 or all available if less)
    max_questions = min(10, len(all_questions))
    selected_questions = random.sample(all_questions, max_questions)
    
    # Shuffle answer options for each question
    shuffled_options = {}
    for question in selected_questions:
        if question.get("options"):
            option_indices = list(range(len(question["options"])))
            random.shuffle(option_indices)
            shuffled_options[question["id"]] = option_indices
    
    # Create test session
    session_data = {
        "id": str(uuid.uuid4()),
        "student_id": student_data.get("student_id", "anonymous"),
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
    
    created_session = await supabase_client.create_record("test_sessions", session_data)
    
    # Return session with shuffled questions
    shuffled_questions = []
    for question in selected_questions:
        q_dict = dict(question)
        if question["id"] in shuffled_options and q_dict.get("options"):
            # Reorder options based on shuffled indices
            indices = shuffled_options[question["id"]]
            original_options = q_dict["options"]
            q_dict["options"] = [original_options[i] for i in indices]
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
    session = await supabase_client.get_record("test_sessions", "id", session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    
    if session["is_completed"]:
        raise HTTPException(status_code=400, detail="Test session already completed")
    
    # Get questions for scoring
    questions = await supabase_client.get_records(
        "questions", 
        filters={"id": {"$in": session["selected_questions"]}}
    )
    
    # Calculate score
    score = 0
    total_points = 0
    correct_answers = {}
    
    for question in questions:
        total_points += question.get("points", 1)
        question_id = question["id"]
        user_answer = answers.get("answers", {}).get(question_id)
        
        if question["question_type"] == "single_choice":
            # Find correct option considering shuffling
            shuffled_indices = session["shuffled_options"].get(question_id, [])
            if shuffled_indices and user_answer is not None:
                # Convert shuffled answer back to original index
                try:
                    shuffled_index = int(user_answer)
                    original_index = shuffled_indices[shuffled_index]
                    if question["options"][original_index]["is_correct"]:
                        score += question.get("points", 1)
                        correct_answers[question_id] = True
                    else:
                        correct_answers[question_id] = False
                except (ValueError, IndexError):
                    correct_answers[question_id] = False
        # Add other question types handling here
    
    percentage = (score / total_points * 100) if total_points > 0 else 0
    is_passed = percentage >= session.get("passing_score", 70)
    
    # Update session
    update_data = {
        "answers": answers.get("answers", {}),
        "score": score,
        "percentage": round(percentage, 2),
        "is_completed": True,
        "is_passed": is_passed,
        "completed_at": datetime.utcnow().isoformat()
    }
    
    updated_session = await supabase_client.update_record("test_sessions", "id", session_id, update_data)
    
    return {
        "session_id": session_id,
        "score": score,
        "total_points": total_points,
        "percentage": round(percentage, 2),
        "is_passed": is_passed,
        "correct_answers": correct_answers
    }

# ====================================================================
# TEAM MANAGEMENT ENDPOINTS
# ====================================================================

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

# ====================================================================
# Q&A MANAGEMENT ENDPOINTS
# ====================================================================

@api_router.get("/qa/questions", response_model=List[QAQuestion])
async def get_qa_questions(category: Optional[str] = None, featured: Optional[bool] = None, limit: int = 50):
    """Get Q&A questions with optional filtering"""
    filters = {}
    if category:
        filters["category"] = category
    if featured is not None:
        filters["is_featured"] = featured
    
    questions = await supabase_client.get_records(
        "qa_questions", 
        filters=filters,
        order_by="-created_at",
        limit=limit
    )
    return [QAQuestion(**question) for question in questions]

@api_router.get("/qa/questions/{question_id}")
async def get_qa_question(question_id: str):
    """Get single Q&A question and increment view count"""
    question = await supabase_client.get_record("qa_questions", "id", question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Increment view count
    await supabase_client.update_record(
        "qa_questions", "id", question_id,
        {"views_count": question.get("views_count", 0) + 1}
    )
    
    return QAQuestion(**question)

@api_router.get("/qa/questions/slug/{slug}")
async def get_qa_question_by_slug(slug: str):
    """Get Q&A question by slug and increment view count"""
    question = await supabase_client.find_one("qa_questions", {"slug": slug})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Increment view count
    await supabase_client.update_record(
        "qa_questions", "id", question["id"],
        {"views_count": question.get("views_count", 0) + 1}
    )
    
    return QAQuestion(**question)

@api_router.get("/qa/categories")
async def get_qa_categories():
    """Get list of Q&A categories with counts"""
    # This would need aggregation in a real implementation
    categories = [
        {"id": "aqidah", "name": "Вероучение", "count": 0},
        {"id": "ibadah", "name": "Поклонение", "count": 0},
        {"id": "muamalat", "name": "Взаимоотношения", "count": 0},
        {"id": "akhlaq", "name": "Нравственность", "count": 0},
        {"id": "fiqh", "name": "Фикх", "count": 0},
        {"id": "hadith", "name": "Хадисы", "count": 0},
        {"id": "quran", "name": "Коран", "count": 0},
        {"id": "seerah", "name": "Жизнеописание Пророка", "count": 0},
        {"id": "general", "name": "Общие вопросы", "count": 0}
    ]
    return categories

@api_router.get("/qa/featured")
async def get_featured_qa_questions():
    """Get featured Q&A questions"""
    questions = await supabase_client.get_records(
        "qa_questions", 
        filters={"is_featured": True},
        order_by="-views_count",
        limit=10
    )
    return [QAQuestion(**question) for question in questions]

@api_router.get("/qa/popular")
async def get_popular_qa_questions():
    """Get popular Q&A questions"""
    questions = await supabase_client.get_records(
        "qa_questions", 
        order_by="-views_count",
        limit=10
    )
    return [QAQuestion(**question) for question in questions]

@api_router.get("/qa/recent")
async def get_recent_qa_questions():
    """Get recent Q&A questions"""
    questions = await supabase_client.get_records(
        "qa_questions", 
        order_by="-created_at",
        limit=10
    )
    return [QAQuestion(**question) for question in questions]

@api_router.get("/qa/stats")
async def get_qa_stats():
    """Get Q&A statistics"""
    total_questions = await supabase_client.count_records("qa_questions")
    featured_count = await supabase_client.count_records("qa_questions", {"is_featured": True})
    
    return {
        "total_questions": total_questions,
        "featured_count": featured_count,
        "questions_by_category": {},
        "total_views": 0
    }

@api_router.post("/admin/qa/questions", response_model=QAQuestion)
async def create_qa_question(question_data: QAQuestionCreate, current_admin: dict = Depends(get_current_admin)):
    """Create new Q&A question"""
    question_dict = question_data.dict()
    question_obj = QAQuestion(**question_dict)
    created_question = await supabase_client.create_record("qa_questions", question_obj.dict())
    return QAQuestion(**created_question)

@api_router.put("/admin/qa/questions/{question_id}", response_model=QAQuestion)
async def update_qa_question(question_id: str, question_data: QAQuestionUpdate, current_admin: dict = Depends(get_current_admin)):
    """Update Q&A question"""
    question = await supabase_client.get_record("qa_questions", "id", question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    update_data = {k: v for k, v in question_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    updated_question = await supabase_client.update_record("qa_questions", "id", question_id, update_data)
    return QAQuestion(**updated_question)

@api_router.delete("/admin/qa/questions/{question_id}")
async def delete_qa_question(question_id: str, current_admin: dict = Depends(require_admin_role)):
    """Delete Q&A question"""
    success = await supabase_client.delete_record("qa_questions", "id", question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}

# ====================================================================
# STUDENT MANAGEMENT ENDPOINTS
# ====================================================================

@api_router.get("/admin/students", response_model=List[Student])
async def get_admin_students(current_admin: dict = Depends(get_current_admin)):
    students = await supabase_client.get_records("students", order_by="-created_at")
    return [Student(**student) for student in students]

@api_router.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get top students by score"""
    students = await supabase_client.get_records(
        "students", 
        filters={"is_active": True},
        order_by="-total_score",
        limit=limit
    )
    return [
        {
            "name": student["name"],
            "total_score": student.get("total_score", 0),
            "completed_courses": len(student.get("completed_courses", [])),
            "current_level": student.get("current_level", "level_1")
        }
        for student in students
    ]

@api_router.put("/admin/students/{student_id}")
async def update_student(student_id: str, student_data: StudentUpdate, current_admin: dict = Depends(get_current_admin)):
    student = await supabase_client.get_record("students", "id", student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = {k: v for k, v in student_data.dict().items() if v is not None}
    
    updated_student = await supabase_client.update_record("students", "id", student_id, update_data)
    return Student(**updated_student)

# ====================================================================
# TEACHER MANAGEMENT ENDPOINTS
# ====================================================================

@api_router.get("/admin/teachers", response_model=List[Teacher])
async def get_admin_teachers(current_admin: dict = Depends(get_current_admin)):
    teachers = await supabase_client.get_records("teachers", order_by="name")
    return [Teacher(**teacher) for teacher in teachers]

@api_router.post("/admin/teachers", response_model=Teacher)
async def create_teacher(teacher_data: TeacherCreate, current_admin: dict = Depends(get_current_admin)):
    teacher_dict = teacher_data.dict()
    teacher_obj = Teacher(**teacher_dict)
    created_teacher = await supabase_client.create_record("teachers", teacher_obj.dict())
    return Teacher(**created_teacher)

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
# TEST IMPORT ENDPOINTS
# ====================================================================

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
        
        test_obj = Test(**test_data)
        created_test = await supabase_client.create_record("tests", test_obj.dict())
        
        # Import questions
        questions_imported = 0
        for i, q_data in enumerate(data.get("questions", [])):
            question_data = {
                "test_id": created_test["id"],
                "text": q_data.get("question", q_data.get("text", "")),
                "question_type": q_data.get("type", "single_choice"),
                "options": [
                    {"id": str(uuid.uuid4()), "text": opt, "is_correct": False}
                    for opt in q_data.get("options", [])
                ],
                "correct_answer": q_data.get("correct_answer"),
                "explanation": q_data.get("explanation"),
                "points": q_data.get("points", 1),
                "order": i + 1
            }
            
            # Mark correct option
            correct_idx = q_data.get("correct_option_index", 0)
            if question_data["options"] and 0 <= correct_idx < len(question_data["options"]):
                question_data["options"][correct_idx]["is_correct"] = True
            
            question_obj = Question(**question_data)
            await supabase_client.create_record("questions", question_obj.dict())
            questions_imported += 1
        
        return {
            "message": f"Successfully imported test with {questions_imported} questions",
            "test_id": created_test["id"],
            "questions_count": questions_imported
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

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