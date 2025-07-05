#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid

# MongoDB connection
mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.getenv('DB_NAME', 'test_database')]

async def init_test_data():
    """Initialize test data for admin panel"""
    print("Initializing test data...")
    
    # Create test teachers
    teachers = [
        {
            "id": str(uuid.uuid4()),
            "name": "Али Евтеев",
            "email": "ali.evteev@uroki-islama.ru",
            "subject": "Этика",
            "bio": "Преподаватель исламской этики с 10-летним опытом",
            "image_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face",
            "is_active": True,
            "courses_count": 1,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Абдуль-Басит Микушкин",
            "email": "abdul.mikushkin@uroki-islama.ru",
            "subject": "Основы веры",
            "bio": "Специалист по основам исламской веры",
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face",
            "is_active": True,
            "courses_count": 1,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Алексей Котенев",
            "email": "alexey.kotenev@uroki-islama.ru",
            "subject": "Практика веры",
            "bio": "Эксперт по практическим аспектам ислама",
            "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face",
            "is_active": True,
            "courses_count": 1,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Микаиль Ганиев",
            "email": "mikail.ganiev@uroki-islama.ru",
            "subject": "История",
            "bio": "Историк ислама, автор научных работ",
            "image_url": "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=400&h=400&fit=crop&crop=face",
            "is_active": True,
            "courses_count": 1,
            "created_at": datetime.utcnow()
        }
    ]
    
    # Insert teachers
    await db.teachers.drop()
    await db.teachers.insert_many(teachers)
    print(f"Inserted {len(teachers)} teachers")
    
    # Create test courses
    courses = [
        {
            "id": "1",
            "title": "Основы веры",
            "description": "Изучите пять столпов ислама и основные принципы веры",
            "teacher_id": teachers[1]["id"],
            "teacher_name": teachers[1]["name"],
            "status": "published",
            "difficulty": "Легко",
            "duration_minutes": 15,
            "questions_count": 10,
            "image_url": "https://images.pexels.com/photos/7249250/pexels-photo-7249250.jpeg",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": "2",
            "title": "Практика веры",
            "description": "Узнайте о ежедневных практиках и обрядах",
            "teacher_id": teachers[2]["id"],
            "teacher_name": teachers[2]["name"],
            "status": "published",
            "difficulty": "Средне",
            "duration_minutes": 20,
            "questions_count": 15,
            "image_url": "https://images.unsplash.com/photo-1582033131298-5bb54c589518",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": "3",
            "title": "Этика ислама",
            "description": "Изучите моральные принципы и этические нормы",
            "teacher_id": teachers[0]["id"],
            "teacher_name": teachers[0]["name"],
            "status": "published",
            "difficulty": "Легко",
            "duration_minutes": 25,
            "questions_count": 12,
            "image_url": "https://images.pexels.com/photos/32470206/pexels-photo-32470206.jpeg",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": "4",
            "title": "История ислама",
            "description": "Познакомьтесь с историей возникновения и развития ислама",
            "teacher_id": teachers[3]["id"],
            "teacher_name": teachers[3]["name"],
            "status": "published",
            "difficulty": "Сложно",
            "duration_minutes": 30,
            "questions_count": 20,
            "image_url": "https://images.unsplash.com/photo-1655552090825-e12b509c83ca",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert courses
    await db.courses.drop()
    await db.courses.insert_many(courses)
    print(f"Inserted {len(courses)} courses")
    
    # Create test students
    students = [
        {
            "id": str(uuid.uuid4()),
            "name": "Ахмед Иванов",
            "email": "ahmed.ivanov@example.com",
            "total_score": 45,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "completed_courses": ["1", "2"]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Фатима Петрова",
            "email": "fatima.petrova@example.com",
            "total_score": 42,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "completed_courses": ["1", "3"]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Умар Сидоров",
            "email": "umar.sidorov@example.com",
            "total_score": 38,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "completed_courses": ["2"]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Айша Козлова",
            "email": "aisha.kozlova@example.com",
            "total_score": 35,
            "is_active": False,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "completed_courses": ["1"]
        }
    ]
    
    # Insert students
    await db.students.drop()
    await db.students.insert_many(students)
    print(f"Inserted {len(students)} students")
    
    # Create test applications
    applications = [
        {
            "id": str(uuid.uuid4()),
            "student_name": "Новый Студент",
            "student_email": "new.student@example.com",
            "course_id": "1",
            "course_title": "Основы веры",
            "message": "Хочу изучать основы ислама",
            "status": "pending",
            "admin_comment": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "student_name": "Еще Один Студент",
            "student_email": "another.student@example.com",
            "course_id": "2",
            "course_title": "Практика веры",
            "message": "Интересуюсь практическими аспектами ислама",
            "status": "approved",
            "admin_comment": "Заявка одобрена",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert applications
    await db.applications.drop()
    await db.applications.insert_many(applications)
    print(f"Inserted {len(applications)} applications")
    
    # Create some test enrollments and scores for statistics
    enrollments = []
    scores = []
    
    for i, student in enumerate(students):
        for j, course in enumerate(courses):
            if j <= i:  # Each student enrolled in fewer courses
                enrollment = {
                    "id": str(uuid.uuid4()),
                    "student_id": student["id"],
                    "course_id": course["id"],
                    "enrolled_at": datetime.utcnow()
                }
                enrollments.append(enrollment)
                
                # Add some scores
                score = {
                    "id": str(uuid.uuid4()),
                    "uid": student["id"],
                    "lessonId": course["id"],
                    "score": 3 + (i * j) % 8,  # Random-ish scores between 3-10
                    "totalQuestions": course["questions_count"],
                    "timeSpent": 120 + (i * 30),
                    "timestamp": datetime.utcnow()
                }
                scores.append(score)
    
    await db.enrollments.drop()
    await db.enrollments.insert_many(enrollments)
    print(f"Inserted {len(enrollments)} enrollments")
    
    await db.scores.insert_many(scores)
    print(f"Inserted {len(scores)} test scores")
    
    print("Test data initialization completed!")

if __name__ == "__main__":
    asyncio.run(init_test_data())