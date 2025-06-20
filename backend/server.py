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