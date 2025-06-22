from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

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

class CourseLevel(str, Enum):
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"

class LessonType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    MIXED = "mixed"

class QuestionType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    TEXT_INPUT = "text_input"

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# Base Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

import re

def create_slug(text: str) -> str:
    """Convert text to URL-friendly slug"""
    # Convert to lowercase and replace non-alphanumeric with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    # Remove leading/trailing hyphens
    return slug.strip('-')

# Course Models
class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    slug: Optional[str] = None
    description: str
    level: CourseLevel
    teacher_id: str
    teacher_name: str
    status: CourseStatus = CourseStatus.DRAFT
    difficulty: str
    estimated_duration_hours: int
    lessons_count: int = 0
    tests_count: int = 0
    image_url: Optional[str] = None
    order: int = 1  # Порядок отображения
    prerequisites: List[str] = []  # ID предыдущих курсов
    additional_materials: Optional[str] = None  # URL to additional materials
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.slug:
            self.slug = create_slug(self.title)

class CourseCreate(BaseModel):
    title: str
    slug: Optional[str] = None
    description: str
    level: CourseLevel
    teacher_id: str
    teacher_name: str
    difficulty: str
    estimated_duration_hours: int
    image_url: Optional[str] = None
    order: Optional[int] = 1
    prerequisites: List[str] = []
    additional_materials: Optional[str] = None

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    level: Optional[CourseLevel] = None
    teacher_id: Optional[str] = None
    teacher_name: Optional[str] = None
    status: Optional[CourseStatus] = None
    difficulty: Optional[str] = None
    estimated_duration_hours: Optional[int] = None
    image_url: Optional[str] = None
    order: Optional[int] = None
    prerequisites: Optional[List[str]] = None

# Lesson Models
class LessonAttachment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    file_url: str
    file_type: str  # pdf, doc, image, etc.
    file_size: int  # in bytes

class Lesson(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    title: str
    slug: Optional[str] = None
    description: Optional[str] = None
    content: str  # HTML content
    lesson_type: LessonType
    video_url: Optional[str] = None
    video_duration: Optional[int] = None  # in seconds
    attachment_url: Optional[str] = None  # Single attachment URL
    order: int
    is_published: bool = True
    estimated_duration_minutes: int = 15
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.slug:
            self.slug = create_slug(self.title)

class LessonCreate(BaseModel):
    course_id: str
    title: str
    description: Optional[str] = None
    content: str
    lesson_type: LessonType
    video_url: Optional[str] = None
    video_duration: Optional[int] = None
    order: int
    estimated_duration_minutes: int = 15

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    lesson_type: Optional[LessonType] = None
    video_url: Optional[str] = None
    video_duration: Optional[int] = None
    order: Optional[int] = None
    is_published: Optional[bool] = None
    estimated_duration_minutes: Optional[int] = None

# Test/Quiz Models
class QuestionOption(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    is_correct: bool = False

class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    question_type: QuestionType
    options: List[QuestionOption] = []
    correct_answer: Optional[str] = None  # For text input questions
    explanation: Optional[str] = None
    points: int = 1
    order: int

class Test(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    course_id: str
    lesson_id: Optional[str] = None  # If None, it's a course-level test
    questions: List[Question] = []
    time_limit_minutes: Optional[int] = None
    passing_score: int = 70  # Percentage
    max_attempts: int = 3
    is_published: bool = True
    order: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: str
    lesson_id: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    passing_score: int = 70
    max_attempts: int = 3
    order: int = 1

class TestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    lesson_id: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    passing_score: Optional[int] = None
    max_attempts: Optional[int] = None
    is_published: Optional[bool] = None
    order: Optional[int] = None

class QuestionCreate(BaseModel):
    test_id: str
    text: str
    question_type: QuestionType
    options: List[QuestionOption] = []
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points: int = 1
    order: int

class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    question_type: Optional[QuestionType] = None
    options: Optional[List[QuestionOption]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points: Optional[int] = None
    order: Optional[int] = None

# Student Progress Models
class LessonProgress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    lesson_id: str
    course_id: str
    is_completed: bool = False
    completion_percentage: int = 0
    time_spent_minutes: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_accessed: datetime = Field(default_factory=datetime.utcnow)

class TestAttempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    test_id: str
    course_id: str
    lesson_id: Optional[str] = None
    answers: Dict[str, Any] = {}  # question_id -> answer
    score: int = 0
    total_points: int = 0
    percentage: float = 0.0
    is_passed: bool = False
    time_taken_minutes: int = 0
    attempt_number: int = 1
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class CourseEnrollment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    course_id: str
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    is_completed: bool = False
    progress_percentage: int = 0
    current_lesson_id: Optional[str] = None

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
    current_level: CourseLevel = CourseLevel.LEVEL_1

class StudentUpdate(BaseModel):
    is_active: Optional[bool] = None
    notes: Optional[str] = None

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

# Test Import Models
class TestImportData(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: str
    lesson_id: Optional[str] = None
    questions: List[Dict[str, Any]]  # Raw question data from JSON/CSV
    time_limit_minutes: Optional[int] = None
    passing_score: int = 70
    max_attempts: int = 3

class TestSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    test_id: str
    course_id: str
    lesson_id: Optional[str] = None
    selected_questions: List[str] = []  # List of question IDs selected for this session
    shuffled_options: Dict[str, List[int]] = {}  # question_id -> shuffled option indices
    answers: Dict[str, Any] = {}  # question_id -> answer
    score: int = 0
    total_points: int = 0
    percentage: float = 0.0
    is_completed: bool = False
    is_passed: bool = False
    time_taken_minutes: int = 0
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class QuestionPool(BaseModel):
    """Extended Question model for question pools with 30+ questions"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    question_type: QuestionType
    options: List[QuestionOption] = []
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points: int = 1
    category: Optional[str] = None  # For grouping questions
    difficulty: Optional[str] = None  # easy, medium, hard
    is_active: bool = True

# Statistics Models
class DashboardStats(BaseModel):
    total_students: int
    total_courses: int
    total_lessons: int
    total_tests: int
    total_teachers: int
    active_students: int
    pending_applications: int
    completed_tests_today: int

class CourseStats(BaseModel):
    course_id: str
    course_title: str
    level: CourseLevel
    enrolled_students: int
    completed_students: int
    lessons_count: int
    tests_count: int
    average_score: float
    completion_rate: float

class LevelStats(BaseModel):
    level: CourseLevel
    courses_count: int
    total_lessons: int
    enrolled_students: int
    completion_rate: float
    points: int = 1
    category: Optional[str] = None  # For grouping questions
    difficulty: Optional[str] = None  # easy, medium, hard
    is_active: bool = True

class CourseStats(BaseModel):
    course_id: str
    course_title: str
    level: CourseLevel
    enrolled_students: int
    completed_students: int
    lessons_count: int
    tests_count: int
    average_score: float
    completion_rate: float

class LevelStats(BaseModel):
    level: CourseLevel
    courses_count: int
    total_lessons: int
    enrolled_students: int
    completion_rate: float