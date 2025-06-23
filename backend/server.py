from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import asyncio
from models import *
import shutil
import aiofiles
import json
import csv
import random
import io

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

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

def shuffle_options(options: List[QuestionOption]) -> tuple[List[QuestionOption], List[int]]:
    """Shuffle question options and return shuffled options with mapping"""
    indices = list(range(len(options)))
    random.shuffle(indices)
    shuffled_options = [options[i] for i in indices]
    return shuffled_options, indices

def select_random_questions(questions: List[Question], count: int = 10) -> List[Question]:
    """Select random questions from a larger pool"""
    if len(questions) <= count:
        return questions
    return random.sample(questions, count)

def parse_csv_test(csv_content: str) -> List[Dict[str, Any]]:
    """Parse CSV test data into question format"""
    questions = []
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    
    for row in csv_reader:
        question = {
            "text": row.get("question", ""),
            "question_type": row.get("type", "single_choice"),
            "options": [],
            "correct_answer": row.get("correct_answer", ""),
            "explanation": row.get("explanation", ""),
            "points": int(row.get("points", 1))
        }
        
        # Parse options (assuming columns like option1, option2, etc.)
        options = []
        for i in range(1, 10):  # Support up to 9 options
            option_key = f"option{i}"
            if option_key in row and row[option_key]:
                options.append({
                    "text": row[option_key],
                    "is_correct": row.get("correct_answer") == str(i)
                })
        
        question["options"] = options
        questions.append(question)
    
    return questions

def parse_json_test(json_content: str) -> List[Dict[str, Any]]:
    """Parse JSON test data into question format"""
    try:
        data = json.loads(json_content)
        if isinstance(data, dict) and "questions" in data:
            return data["questions"]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("Invalid JSON format")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON content")

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

# Original routes (legacy)
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
    
    await db.admins.update_one(
        {"username": admin_data.username},
        {"$set": {"last_login": datetime.utcnow()}}
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
    admin = await db.admins.find_one({"email": email})
    if admin and verify_password(password, admin["hashed_password"]):
        # Update last login
        await db.admins.update_one(
            {"email": email},
            {"$set": {"last_login": datetime.utcnow()}}
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
    
    # If not admin, check regular users (Firebase users)
    # For now, we'll implement a simple check
    # In a real scenario, you'd verify with Firebase
    
    # Check if user exists in our students database
    student = await db.students.find_one({"email": email})
    if not student:
        # Create new student record for Firebase users
        student = {
            "id": str(uuid.uuid4()),
            "name": email.split("@")[0].title(),  # Simple name from email
            "email": email,
            "total_score": 0,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "completed_courses": [],
            "current_level": CourseLevel.LEVEL_1
        }
        await db.students.insert_one(student)
    else:
        # Update last activity
        await db.students.update_one(
            {"email": email},
            {"$set": {"last_activity": datetime.utcnow()}}
        )
    
    # For regular users, we'll return a simple token
    # In production, you'd verify with Firebase here
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
    total_students = await db.students.count_documents({})
    total_courses = await db.courses.count_documents({})
    total_lessons = await db.lessons.count_documents({})
    total_tests = await db.tests.count_documents({})
    total_teachers = await db.teachers.count_documents({})
    active_students = await db.students.count_documents({"is_active": True})
    pending_applications = await db.applications.count_documents({"status": ApplicationStatus.PENDING})
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    completed_tests_today = await db.test_attempts.count_documents({
        "completed_at": {"$gte": today}
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
    courses = await db.courses.find({"status": CourseStatus.PUBLISHED}).sort("level", 1).sort("order", 1).to_list(1000)
    return [Course(**course) for course in courses]

@api_router.get("/admin/courses", response_model=List[Course])
async def get_admin_courses(current_admin: dict = Depends(get_current_admin)):
    courses = await db.courses.find().sort("level", 1).sort("order", 1).to_list(1000)
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
    # Check if course has lessons
    lessons_count = await db.lessons.count_documents({"course_id": course_id})
    if lessons_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete course with existing lessons")
    
    result = await db.courses.delete_one({"id": course_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted successfully"}

# Lesson Management Routes
@api_router.get("/courses/{course_id}/lessons", response_model=List[Lesson])
async def get_course_lessons(course_id: str):
    """Public endpoint for published lessons"""
    lessons = await db.lessons.find({
        "course_id": course_id, 
        "is_published": True
    }).sort("order", 1).to_list(1000)
    return [Lesson(**lesson) for lesson in lessons]

@api_router.get("/admin/courses/{course_id}/lessons", response_model=List[Lesson])
async def get_admin_course_lessons(course_id: str, current_admin: dict = Depends(get_current_admin)):
    lessons = await db.lessons.find({"course_id": course_id}).sort("order", 1).to_list(1000)
    return [Lesson(**lesson) for lesson in lessons]

@api_router.post("/admin/lessons", response_model=Lesson)
async def create_lesson(lesson_data: LessonCreate, current_admin: dict = Depends(get_current_admin)):
    # Verify course exists
    course = await db.courses.find_one({"id": lesson_data.course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    lesson_dict = lesson_data.dict()
    lesson_obj = Lesson(**lesson_dict)
    
    await db.lessons.insert_one(lesson_obj.dict())
    
    # Update course lessons count
    await db.courses.update_one(
        {"id": lesson_data.course_id},
        {"$inc": {"lessons_count": 1}}
    )
    
    return lesson_obj

@api_router.get("/lessons/{lesson_id}", response_model=Lesson)
async def get_lesson(lesson_id: str):
    lesson = await db.lessons.find_one({"id": lesson_id, "is_published": True})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return Lesson(**lesson)

@api_router.put("/admin/lessons/{lesson_id}", response_model=Lesson)
async def update_lesson(lesson_id: str, lesson_data: LessonUpdate, current_admin: dict = Depends(get_current_admin)):
    lesson = await db.lessons.find_one({"id": lesson_id})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    update_data = {k: v for k, v in lesson_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.lessons.update_one({"id": lesson_id}, {"$set": update_data})
    
    updated_lesson = await db.lessons.find_one({"id": lesson_id})
    return Lesson(**updated_lesson)

@api_router.delete("/admin/lessons/{lesson_id}")
async def delete_lesson(lesson_id: str, current_admin: dict = Depends(require_admin_role)):
    lesson = await db.lessons.find_one({"id": lesson_id})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Delete lesson
    await db.lessons.delete_one({"id": lesson_id})
    
    # Update course lessons count
    await db.courses.update_one(
        {"id": lesson["course_id"]},
        {"$inc": {"lessons_count": -1}}
    )
    
    # Delete associated tests
    await db.tests.delete_many({"lesson_id": lesson_id})
    
    return {"message": "Lesson deleted successfully"}

# Test Management Routes
@api_router.get("/courses/{course_id}/tests", response_model=List[Test])
async def get_course_tests(course_id: str):
    """Get course-level tests (not lesson-specific)"""
    tests = await db.tests.find({
        "course_id": course_id,
        "lesson_id": None,
        "is_published": True
    }).sort("order", 1).to_list(1000)
    return [Test(**test) for test in tests]

@api_router.get("/lessons/{lesson_id}/tests", response_model=List[Test])
async def get_lesson_tests(lesson_id: str):
    """Get lesson-specific tests"""
    tests = await db.tests.find({
        "lesson_id": lesson_id,
        "is_published": True
    }).sort("order", 1).to_list(1000)
    return [Test(**test) for test in tests]

@api_router.get("/admin/tests", response_model=List[Test])
async def get_admin_tests(current_admin: dict = Depends(get_current_admin)):
    tests = await db.tests.find().sort("course_id", 1).sort("order", 1).to_list(1000)
    return [Test(**test) for test in tests]

@api_router.post("/admin/tests", response_model=Test)
async def create_test(test_data: TestCreate, current_admin: dict = Depends(get_current_admin)):
    # Verify course exists
    course = await db.courses.find_one({"id": test_data.course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify lesson exists if specified
    if test_data.lesson_id:
        lesson = await db.lessons.find_one({"id": test_data.lesson_id})
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
    
    test_dict = test_data.dict()
    test_obj = Test(**test_dict)
    
    await db.tests.insert_one(test_obj.dict())
    
    # Update course tests count
    await db.courses.update_one(
        {"id": test_data.course_id},
        {"$inc": {"tests_count": 1}}
    )
    
    return test_obj

@api_router.get("/tests/{test_id}", response_model=Test)
async def get_test(test_id: str):
    test = await db.tests.find_one({"id": test_id, "is_published": True})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return Test(**test)

@api_router.put("/admin/tests/{test_id}", response_model=Test)
async def update_test(test_id: str, test_data: TestUpdate, current_admin: dict = Depends(get_current_admin)):
    test = await db.tests.find_one({"id": test_id})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    update_data = {k: v for k, v in test_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.tests.update_one({"id": test_id}, {"$set": update_data})
    
    updated_test = await db.tests.find_one({"id": test_id})
    return Test(**updated_test)

@api_router.delete("/admin/tests/{test_id}")
async def delete_test(test_id: str, current_admin: dict = Depends(require_admin_role)):
    test = await db.tests.find_one({"id": test_id})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    await db.tests.delete_one({"id": test_id})
    
    # Update course tests count
    await db.courses.update_one(
        {"id": test["course_id"]},
        {"$inc": {"tests_count": -1}}
    )
    
    return {"message": "Test deleted successfully"}

# Question Management Routes
@api_router.post("/admin/tests/{test_id}/questions", response_model=Question)
async def add_question_to_test(test_id: str, question_data: QuestionCreate, current_admin: dict = Depends(get_current_admin)):
    test = await db.tests.find_one({"id": test_id})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    question_dict = question_data.dict()
    question_dict.pop("test_id")  # Remove test_id from question data
    question_obj = Question(**question_dict)
    
    # Add question to test
    await db.tests.update_one(
        {"id": test_id},
        {"$push": {"questions": question_obj.dict()}}
    )
    
    return question_obj

@api_router.put("/admin/tests/{test_id}/questions/{question_id}", response_model=Question)
async def update_question(test_id: str, question_id: str, question_data: QuestionUpdate, current_admin: dict = Depends(get_current_admin)):
    test = await db.tests.find_one({"id": test_id})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Find and update the question
    questions = test.get("questions", [])
    for i, question in enumerate(questions):
        if question["id"] == question_id:
            update_data = {k: v for k, v in question_data.dict().items() if v is not None}
            questions[i].update(update_data)
            
            await db.tests.update_one(
                {"id": test_id},
                {"$set": {"questions": questions}}
            )
            
            return Question(**questions[i])
    
    raise HTTPException(status_code=404, detail="Question not found")

@api_router.delete("/admin/tests/{test_id}/questions/{question_id}")
async def delete_question(test_id: str, question_id: str, current_admin: dict = Depends(require_admin_role)):
    test = await db.tests.find_one({"id": test_id})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Remove question from test
    await db.tests.update_one(
        {"id": test_id},
        {"$pull": {"questions": {"id": question_id}}}
    )
    
    return {"message": "Question deleted successfully"}

# Enhanced File Upload Routes
@api_router.post("/admin/upload-enhanced")
async def upload_enhanced_file(
    file: UploadFile = File(...), 
    current_admin: dict = Depends(get_current_admin)
):
    """Enhanced file upload with support for larger files and more formats"""
    # Extended allowed types
    allowed_types = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "video/mp4", "video/avi", "video/mov",
        "application/pdf", 
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/csv",
        "application/json",
        "text/plain"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Increased file size limits based on type
    if file.content_type.startswith("video/"):
        max_size = 100 * 1024 * 1024  # 100MB for videos
    elif file.content_type == "application/pdf":
        max_size = 50 * 1024 * 1024   # 50MB for PDFs
    else:
        max_size = 10 * 1024 * 1024   # 10MB for other files
    
    # Read file in chunks to handle large files
    total_size = 0
    chunks = []
    
    while chunk := await file.read(1024 * 1024):  # Read 1MB chunks
        chunks.append(chunk)
        total_size += len(chunk)
        
        if total_size > max_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File size too large (max {max_size // (1024*1024)}MB)"
            )
    
    file_content = b''.join(chunks)
    
    # Generate unique filename with timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
    unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)
        
        file_url = f"/uploads/{unique_filename}"
        
        return {
            "filename": file.filename,
            "file_url": file_url,
            "file_type": file.content_type,
            "file_size": total_size,
            "success": True,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

@api_router.post("/admin/lessons/{lesson_id}/attachments")
async def add_lesson_attachment(
    lesson_id: str,
    file: UploadFile = File(...),
    current_admin: dict = Depends(get_current_admin)
):
    """Add attachment to a lesson"""
    lesson = await db.lessons.find_one({"id": lesson_id})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Upload file
    upload_result = await upload_enhanced_file(file, current_admin)
    
    # Create attachment object
    attachment = LessonAttachment(
        filename=upload_result["filename"],
        file_url=upload_result["file_url"],
        file_type=upload_result["file_type"],
        file_size=upload_result["file_size"]
    )
    
    # Add to lesson
    await db.lessons.update_one(
        {"id": lesson_id},
        {"$push": {"attachments": attachment.dict()}}
    )
    
    return {
        "message": "Attachment added successfully",
        "attachment": attachment
    }

@api_router.delete("/admin/lessons/{lesson_id}/attachments/{attachment_id}")
async def remove_lesson_attachment(
    lesson_id: str,
    attachment_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Remove attachment from a lesson"""
    lesson = await db.lessons.find_one({"id": lesson_id})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Remove attachment from lesson
    result = await db.lessons.update_one(
        {"id": lesson_id},
        {"$pull": {"attachments": {"id": attachment_id}}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    return {"message": "Attachment removed successfully"}

# File Upload Routes
@api_router.post("/admin/upload")
async def upload_file(file: UploadFile = File(...), current_admin: dict = Depends(get_current_admin)):
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4", "application/pdf", "application/msword"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(status_code=400, detail="File size too large (max 10MB)")
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        file_url = f"/uploads/{unique_filename}"
        
        return {
            "filename": file.filename,
            "file_url": file_url,
            "file_type": file.content_type,
            "file_size": len(file_content),
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

# Student Progress Routes (Public)
@api_router.post("/enroll/{course_id}")
async def enroll_in_course(course_id: str, student_data: dict):
    """Enroll student in course"""
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if already enrolled
    existing = await db.enrollments.find_one({
        "student_id": student_data["student_id"],
        "course_id": course_id
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
    
    enrollment = CourseEnrollment(
        student_id=student_data["student_id"],
        course_id=course_id
    )
    
    await db.enrollments.insert_one(enrollment.dict())
    return {"message": "Successfully enrolled in course"}

# Statistics Routes
@api_router.get("/admin/reports/levels", response_model=List[LevelStats])
async def get_level_statistics(current_admin: dict = Depends(get_current_admin)):
    stats = []
    
    for level in CourseLevel:
        courses = await db.courses.find({"level": level}).to_list(1000)
        courses_count = len(courses)
        
        course_ids = [course["id"] for course in courses]
        lessons_count = await db.lessons.count_documents({"course_id": {"$in": course_ids}})
        enrolled_count = await db.enrollments.count_documents({"course_id": {"$in": course_ids}})
        completed_count = await db.enrollments.count_documents({
            "course_id": {"$in": course_ids},
            "is_completed": True
        })
        
        completion_rate = (completed_count / enrolled_count * 100) if enrolled_count > 0 else 0
        
        stats.append(LevelStats(
            level=level,
            courses_count=courses_count,
            total_lessons=lessons_count,
            enrolled_students=enrolled_count,
            completion_rate=round(completion_rate, 2)
        ))
    
    return stats

# Enhanced Test Management Routes

@api_router.post("/admin/tests/import")
async def import_test_from_file(
    file: UploadFile = File(...), 
    course_id: str = None,
    lesson_id: str = None,
    current_admin: dict = Depends(get_current_admin)
):
    """Import test questions from JSON or CSV file"""
    if not file.filename.endswith(('.json', '.csv')):
        raise HTTPException(status_code=400, detail="Only JSON and CSV files are supported")
    
    # Verify course exists
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Verify lesson exists if specified
    if lesson_id:
        lesson = await db.lessons.find_one({"id": lesson_id})
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
    
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Parse questions based on file type
        if file.filename.endswith('.json'):
            questions_data = parse_json_test(content_str)
        else:  # CSV
            questions_data = parse_csv_test(content_str)
        
        # Create test
        test_data = {
            "title": f"Imported Test - {file.filename}",
            "description": f"Test imported from {file.filename}",
            "course_id": course_id,
            "lesson_id": lesson_id,
            "time_limit_minutes": 30,
            "passing_score": 70,
            "max_attempts": 3,
            "is_published": True,
            "order": 1
        }
        
        test_obj = Test(**test_data)
        
        # Convert questions to proper format
        questions = []
        for i, q_data in enumerate(questions_data):
            options = []
            for opt_data in q_data.get("options", []):
                option = QuestionOption(
                    text=opt_data["text"],
                    is_correct=opt_data.get("is_correct", False)
                )
                options.append(option)
            
            question = Question(
                text=q_data["text"],
                question_type=QuestionType(q_data.get("question_type", "single_choice")),
                options=options,
                correct_answer=q_data.get("correct_answer"),
                explanation=q_data.get("explanation"),
                points=q_data.get("points", 1),
                order=i + 1
            )
            questions.append(question)
        
        test_obj.questions = questions
        
        # Save to database
        await db.tests.insert_one(test_obj.dict())
        
        # Update course tests count
        await db.courses.update_one(
            {"id": course_id},
            {"$inc": {"tests_count": 1}}
        )
        
        return {
            "message": "Test imported successfully",
            "test_id": test_obj.id,
            "questions_count": len(questions),
            "test": test_obj
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to import test: {str(e)}")

@api_router.post("/tests/{test_id}/start-session")
async def start_test_session(test_id: str, student_data: dict):
    """Start a new test session with random question selection"""
    test = await db.tests.find_one({"id": test_id, "is_published": True})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check if student exists
    student_id = student_data.get("student_id")
    if not student_id:
        raise HTTPException(status_code=400, detail="Student ID required")
    
    # Check previous attempts
    attempt_count = await db.test_sessions.count_documents({
        "student_id": student_id,
        "test_id": test_id,
        "is_completed": True
    })
    
    if attempt_count >= test.get("max_attempts", 3):
        raise HTTPException(status_code=400, detail="Maximum attempts reached")
    
    # Select random questions (10 from available pool)
    all_questions = test.get("questions", [])
    if len(all_questions) == 0:
        raise HTTPException(status_code=400, detail="Test has no questions")
    
    selected_questions = select_random_questions(all_questions, 10)
    
    # Create shuffled options for each question
    shuffled_options = {}
    for question in selected_questions:
        if question.get("options"):
            _, shuffle_indices = shuffle_options([QuestionOption(**opt) for opt in question["options"]])
            shuffled_options[question["id"]] = shuffle_indices
    
    # Create test session
    session = TestSession(
        student_id=student_id,
        test_id=test_id,
        course_id=test["course_id"],
        lesson_id=test.get("lesson_id"),
        selected_questions=[q["id"] for q in selected_questions],
        shuffled_options=shuffled_options,
        total_points=sum(q.get("points", 1) for q in selected_questions)
    )
    
    await db.test_sessions.insert_one(session.dict())
    
    # Prepare questions for frontend (with shuffled options)
    questions_for_frontend = []
    for question in selected_questions:
        q_copy = question.copy()
        if question["id"] in shuffled_options:
            shuffle_indices = shuffled_options[question["id"]]
            original_options = question.get("options", [])
            q_copy["options"] = [original_options[i] for i in shuffle_indices]
            # Remove correct answer info for security
            for opt in q_copy["options"]:
                opt.pop("is_correct", None)
        questions_for_frontend.append(q_copy)
    
    return {
        "session_id": session.id,
        "test_title": test["title"],
        "questions": questions_for_frontend,
        "time_limit_minutes": test.get("time_limit_minutes"),
        "total_points": session.total_points
    }

@api_router.post("/test-sessions/{session_id}/submit")
async def submit_test_session(session_id: str, answers: Dict[str, Any]):
    """Submit test session answers and calculate score"""
    session = await db.test_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    
    if session.get("is_completed"):
        raise HTTPException(status_code=400, detail="Test session already completed")
    
    # Get test data
    test = await db.tests.find_one({"id": session["test_id"]})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Calculate score
    score = 0
    total_points = 0
    selected_question_ids = session.get("selected_questions", [])
    
    for question in test.get("questions", []):
        if question["id"] in selected_question_ids:
            total_points += question.get("points", 1)
            
            # Check if answer is correct
            question_id = question["id"]
            if question_id in answers:
                user_answer = answers[question_id]
                
                if question.get("question_type") == "single_choice":
                    # For shuffled options, we need to map back to original indices
                    if question_id in session.get("shuffled_options", {}):
                        shuffle_indices = session["shuffled_options"][question_id]
                        if isinstance(user_answer, int) and 0 <= user_answer < len(shuffle_indices):
                            original_index = shuffle_indices[user_answer]
                            if original_index < len(question.get("options", [])):
                                if question["options"][original_index].get("is_correct"):
                                    score += question.get("points", 1)
                    else:
                        # No shuffling applied
                        if isinstance(user_answer, int) and 0 <= user_answer < len(question.get("options", [])):
                            if question["options"][user_answer].get("is_correct"):
                                score += question.get("points", 1)
                
                elif question.get("question_type") == "text_input":
                    if str(user_answer).strip().lower() == str(question.get("correct_answer", "")).strip().lower():
                        score += question.get("points", 1)
    
    # Calculate percentage
    percentage = (score / total_points * 100) if total_points > 0 else 0
    is_passed = percentage >= test.get("passing_score", 70)
    
    # Update session
    update_data = {
        "answers": answers,
        "score": score,
        "total_points": total_points,
        "percentage": percentage,
        "is_completed": True,
        "is_passed": is_passed,
        "completed_at": datetime.utcnow()
    }
    
    await db.test_sessions.update_one(
        {"id": session_id},
        {"$set": update_data}
    )
    
    # Also create a test attempt record for compatibility
    attempt = TestAttempt(
        student_id=session["student_id"],
        test_id=session["test_id"],
        course_id=session["course_id"],
        lesson_id=session.get("lesson_id"),
        answers=answers,
        score=score,
        total_points=total_points,
        percentage=percentage,
        is_passed=is_passed,
        completed_at=datetime.utcnow()
    )
    
    await db.test_attempts.insert_one(attempt.dict())
    
    return {
        "score": score,
        "total_points": total_points,
        "percentage": percentage,
        "is_passed": is_passed,
        "passing_score": test.get("passing_score", 70)
    }

@api_router.get("/admin/tests/{test_id}/sessions")
async def get_test_sessions(test_id: str, current_admin: dict = Depends(get_current_admin)):
    """Get all sessions for a specific test"""
    sessions = await db.test_sessions.find({"test_id": test_id}).to_list(1000)
    return sessions

# Legacy routes for compatibility
@api_router.get("/admin/students", response_model=List[Student])
async def get_students(current_admin: dict = Depends(get_current_admin)):
    students = await db.students.find().to_list(1000)
    return [Student(**student) for student in students]

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

@api_router.get("/admin/applications", response_model=List[Application])
async def get_applications(current_admin: dict = Depends(get_current_admin)):
    applications = await db.applications.find().sort("created_at", -1).to_list(1000)
    return [Application(**app) for app in applications]

# ==================== Q&A ENDPOINTS ====================

@api_router.get("/qa/questions", response_model=List[QAQuestion])
async def get_qa_questions(
    category: Optional[QACategory] = None,
    featured: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 20,
    skip: int = 0
):
    """Получить список вопросов и ответов"""
    query = {}
    
    if category:
        query["category"] = category
    if featured is not None:
        query["is_featured"] = featured
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"question_text": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [search]}},
        ]
    
    questions = await db.qa_questions.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return [QAQuestion(**q) for q in questions]

@api_router.get("/qa/questions/{question_id}", response_model=QAQuestion)
async def get_qa_question(question_id: str):
    """Получить конкретный вопрос по ID"""
    question = await db.qa_questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    
    # Увеличить счетчик просмотров
    await db.qa_questions.update_one(
        {"id": question_id},
        {"$inc": {"views_count": 1}}
    )
    question["views_count"] += 1
    
    return QAQuestion(**question)

@api_router.get("/qa/questions/slug/{slug}", response_model=QAQuestion)
async def get_qa_question_by_slug(slug: str):
    """Получить вопрос по slug"""
    question = await db.qa_questions.find_one({"slug": slug})
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    
    # Увеличить счетчик просмотров
    await db.qa_questions.update_one(
        {"slug": slug},
        {"$inc": {"views_count": 1}}
    )
    question["views_count"] += 1
    
    return QAQuestion(**question)

@api_router.get("/qa/categories")
async def get_qa_categories():
    """Получить все категории с количеством вопросов"""
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    category_counts = await db.qa_questions.aggregate(pipeline).to_list(100)
    
    # Добавить русские названия категорий
    category_names = {
        "aqidah": "Вероучение",
        "ibadah": "Поклонение", 
        "muamalat": "Взаимоотношения",
        "akhlaq": "Нравственность",
        "fiqh": "Фикх",
        "hadith": "Хадисы",
        "quran": "Коран",
        "seerah": "Жизнеописание Пророка",
        "general": "Общие вопросы"
    }
    
    categories = []
    for cat in category_counts:
        categories.append({
            "id": cat["_id"],
            "name": category_names.get(cat["_id"], cat["_id"].title()),
            "count": cat["count"]
        })
    
    return categories

@api_router.get("/qa/featured", response_model=List[QAQuestion])
async def get_featured_qa_questions(limit: int = 5):
    """Получить рекомендуемые вопросы"""
    questions = await db.qa_questions.find({"is_featured": True}).sort("views_count", -1).limit(limit).to_list(limit)
    return [QAQuestion(**q) for q in questions]

@api_router.get("/qa/popular", response_model=List[QAQuestion])
async def get_popular_qa_questions(limit: int = 10):
    """Получить популярные вопросы"""
    questions = await db.qa_questions.find().sort("views_count", -1).limit(limit).to_list(limit)
    return [QAQuestion(**q) for q in questions]

@api_router.get("/qa/recent", response_model=List[QAQuestion])
async def get_recent_qa_questions(limit: int = 10):
    """Получить последние вопросы"""
    questions = await db.qa_questions.find().sort("created_at", -1).limit(limit).to_list(limit)
    return [QAQuestion(**q) for q in questions]

@api_router.get("/qa/stats", response_model=QAStats)
async def get_qa_stats():
    """Получить статистику Q&A"""
    total_questions = await db.qa_questions.count_documents({})
    featured_count = await db.qa_questions.count_documents({"is_featured": True})
    
    # Группировка по категориям
    pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}]
    category_stats = await db.qa_questions.aggregate(pipeline).to_list(100)
    questions_by_category = {cat["_id"]: cat["count"] for cat in category_stats}
    
    # Общее количество просмотров
    views_pipeline = [{"$group": {"_id": None, "total_views": {"$sum": "$views_count"}}}]
    views_result = await db.qa_questions.aggregate(views_pipeline).to_list(1)
    total_views = views_result[0]["total_views"] if views_result else 0
    
    # Самые просматриваемые вопросы
    most_viewed = await db.qa_questions.find().sort("views_count", -1).limit(5).to_list(5)
    most_viewed_questions = [{"id": q["id"], "title": q["title"], "views": q["views_count"]} for q in most_viewed]
    
    # Последние вопросы
    recent = await db.qa_questions.find().sort("created_at", -1).limit(5).to_list(5)
    recent_questions = [{"id": q["id"], "title": q["title"], "created_at": q["created_at"]} for q in recent]
    
    return QAStats(
        total_questions=total_questions,
        questions_by_category=questions_by_category,
        featured_count=featured_count,
        total_views=total_views,
        most_viewed_questions=most_viewed_questions,
        recent_questions=recent_questions
    )

# ==================== ADMIN Q&A ENDPOINTS ====================

@api_router.post("/admin/qa/questions", response_model=QAQuestion)
async def create_qa_question(
    question_data: QAQuestionCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Создать новый вопрос и ответ (только админы)"""
    question_dict = question_data.dict()
    question_dict["id"] = str(uuid.uuid4())
    question_dict["created_at"] = datetime.utcnow()
    question_dict["updated_at"] = datetime.utcnow()
    
    if not question_dict.get("slug"):
        question_dict["slug"] = create_slug(question_dict["title"])
    
    # Проверить уникальность slug
    existing = await db.qa_questions.find_one({"slug": question_dict["slug"]})
    if existing:
        question_dict["slug"] += f"-{question_dict['id'][:8]}"
    
    question_obj = QAQuestion(**question_dict)
    await db.qa_questions.insert_one(question_obj.dict())
    return question_obj

@api_router.put("/admin/qa/questions/{question_id}", response_model=QAQuestion)
async def update_qa_question(
    question_id: str,
    question_data: QAQuestionUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    """Обновить вопрос и ответ (только админы)"""
    existing = await db.qa_questions.find_one({"id": question_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    
    update_data = {k: v for k, v in question_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    if "title" in update_data and not update_data.get("slug"):
        update_data["slug"] = create_slug(update_data["title"])
    
    await db.qa_questions.update_one({"id": question_id}, {"$set": update_data})
    
    updated_question = await db.qa_questions.find_one({"id": question_id})
    return QAQuestion(**updated_question)

@api_router.delete("/admin/qa/questions/{question_id}")
async def delete_qa_question(
    question_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Удалить вопрос (только админы)"""
    result = await db.qa_questions.delete_one({"id": question_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    
    return {"message": "Вопрос успешно удален"}

@api_router.get("/admin/qa/questions", response_model=List[QAQuestion])
async def get_admin_qa_questions(
    current_admin: dict = Depends(get_current_admin),
    category: Optional[QACategory] = None,
    search: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """Получить все вопросы для админа"""
    query = {}
    
    if category:
        query["category"] = category
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"question_text": {"$regex": search, "$options": "i"}},
            {"answer_text": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [search]}},
        ]
    
    questions = await db.qa_questions.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return [QAQuestion(**q) for q in questions]

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
    admin_count = await db.admins.count_documents({})
    if admin_count == 0:
        # Create default admin
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
        
        # Create second admin with frontend credentials
        second_admin = AdminUser(
            username="miftahulum",
            email="miftahulum@gmail.com",
            full_name="Мифтахулюм",
            role=UserRole.SUPER_ADMIN
        )
        second_admin_dict = second_admin.dict()
        second_admin_dict["hashed_password"] = get_password_hash("197724")
        await db.admins.insert_one(second_admin_dict)
        logger.info("Second admin user created: miftahulum@gmail.com/197724")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()