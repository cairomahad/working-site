#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid
from models import *

# MongoDB connection
mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.getenv('DB_NAME', 'test_database')]

async def init_course_structure():
    """Initialize 3-level course structure"""
    print("Initializing 3-level course structure...")
    
    # Create teachers first
    teachers = [
        {
            "id": str(uuid.uuid4()),
            "name": "Устад Али Хасанов",
            "email": "ali.hasanov@uroki-islama.ru",
            "subject": "Основы ислама",
            "bio": "Преподаватель основ исламской веры с 15-летним опытом",
            "image_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face",
            "is_active": True,
            "courses_count": 0,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Устада Фатима Ахмедова",
            "email": "fatima.ahmedova@uroki-islama.ru",
            "subject": "Практическая религия",
            "bio": "Специалист по практическим аспектам ислама",
            "image_url": "https://images.unsplash.com/photo-1494790108755-2616b332c63c?w=400&h=400&fit=crop&crop=face",
            "is_active": True,
            "courses_count": 0,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Шейх Ибрагим Садыков",
            "email": "ibrahim.sadykov@uroki-islama.ru",
            "subject": "Углубленное изучение",
            "bio": "Доктор исламских наук, эксперт по Корану и Сунне",
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face",
            "is_active": True,
            "courses_count": 0,
            "created_at": datetime.utcnow()
        }
    ]
    
    # Clear and insert teachers
    await db.teachers.drop()
    await db.teachers.insert_many(teachers)
    print(f"Создано {len(teachers)} преподавателей")
    
    # Create courses for each level
    courses = [
        # Level 1 Courses
        {
            "id": str(uuid.uuid4()),
            "title": "Основы веры (Акыда)",
            "description": "Изучение основ исламской веры: шахада, единобожие, пророки",
            "level": CourseLevel.LEVEL_1,
            "teacher_id": teachers[0]["id"],
            "teacher_name": teachers[0]["name"],
            "status": CourseStatus.PUBLISHED,
            "difficulty": "Начальный",
            "estimated_duration_hours": 20,
            "lessons_count": 0,
            "tests_count": 0,
            "image_url": "https://images.pexels.com/photos/7249250/pexels-photo-7249250.jpeg",
            "order": 1,
            "prerequisites": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Пять столпов ислама",
            "description": "Детальное изучение пяти основных обязанностей мусульманина",
            "level": CourseLevel.LEVEL_1,
            "teacher_id": teachers[1]["id"],
            "teacher_name": teachers[1]["name"],
            "status": CourseStatus.PUBLISHED,
            "difficulty": "Начальный",
            "estimated_duration_hours": 25,
            "lessons_count": 0,
            "tests_count": 0,
            "image_url": "https://images.unsplash.com/photo-1582033131298-5bb54c589518",
            "order": 2,
            "prerequisites": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Очищение и молитва",
            "description": "Практическое руководство по совершению омовения и намаза",
            "level": CourseLevel.LEVEL_1,
            "teacher_id": teachers[1]["id"],
            "teacher_name": teachers[1]["name"],
            "status": CourseStatus.PUBLISHED,
            "difficulty": "Начальный",
            "estimated_duration_hours": 15,
            "lessons_count": 0,
            "tests_count": 0,
            "image_url": "https://images.pexels.com/photos/32470206/pexels-photo-32470206.jpeg",
            "order": 3,
            "prerequisites": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        
        # Level 2 Courses
        {
            "id": str(uuid.uuid4()),
            "title": "Коран: чтение и понимание",
            "description": "Изучение правил чтения Корана и понимание основных сур",
            "level": CourseLevel.LEVEL_2,
            "teacher_id": teachers[2]["id"],
            "teacher_name": teachers[2]["name"],
            "status": CourseStatus.PUBLISHED,
            "difficulty": "Средний",
            "estimated_duration_hours": 40,
            "lessons_count": 0,
            "tests_count": 0,
            "image_url": "https://images.unsplash.com/photo-1655552090825-e12b509c83ca",
            "order": 1,
            "prerequisites": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Исламская этика и мораль",
            "description": "Изучение моральных принципов ислама и их применение в жизни",
            "level": CourseLevel.LEVEL_2,
            "teacher_id": teachers[0]["id"],
            "teacher_name": teachers[0]["name"],
            "status": CourseStatus.PUBLISHED,
            "difficulty": "Средний",
            "estimated_duration_hours": 30,
            "lessons_count": 0,
            "tests_count": 0,
            "image_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f",
            "order": 2,
            "prerequisites": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "История пророков",
            "description": "Жизнеописания пророков от Адама до Мухаммада (мир им всем)",
            "level": CourseLevel.LEVEL_2,
            "teacher_id": teachers[2]["id"],
            "teacher_name": teachers[2]["name"],
            "status": CourseStatus.PUBLISHED,
            "difficulty": "Средний",
            "estimated_duration_hours": 35,
            "lessons_count": 0,
            "tests_count": 0,
            "image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570",
            "order": 3,
            "prerequisites": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        
        # Level 3 Courses
        {
            "id": str(uuid.uuid4()),
            "title": "Фикх: исламское право",
            "description": "Углубленное изучение исламского права и его применения",
            "level": CourseLevel.LEVEL_3,
            "teacher_id": teachers[2]["id"],
            "teacher_name": teachers[2]["name"],
            "status": CourseStatus.PUBLISHED,
            "difficulty": "Продвинутый",
            "estimated_duration_hours": 60,
            "lessons_count": 0,
            "tests_count": 0,
            "image_url": "https://images.unsplash.com/photo-1568667256549-094345857637",
            "order": 1,
            "prerequisites": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Тафсир: толкование Корана",
            "description": "Научное толкование Корана на основе классических источников",
            "level": CourseLevel.LEVEL_3,
            "teacher_id": teachers[2]["id"],
            "teacher_name": teachers[2]["name"],
            "status": CourseStatus.PUBLISHED,
            "difficulty": "Продвинутый",
            "estimated_duration_hours": 80,
            "lessons_count": 0,
            "tests_count": 0,
            "image_url": "https://images.unsplash.com/photo-1609347964230-8aa56fa2773d",
            "order": 2,
            "prerequisites": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Исламская философия и теология",
            "description": "Изучение философских и теологических аспектов ислама",
            "level": CourseLevel.LEVEL_3,
            "teacher_id": teachers[0]["id"],
            "teacher_name": teachers[0]["name"],
            "status": CourseStatus.PUBLISHED,
            "difficulty": "Продвинутый",
            "estimated_duration_hours": 50,
            "lessons_count": 0,
            "tests_count": 0,
            "image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570",
            "order": 3,
            "prerequisites": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Clear and insert courses
    await db.courses.drop()
    await db.courses.insert_many(courses)
    print(f"Создано {len(courses)} курсов:")
    for level in [CourseLevel.LEVEL_1, CourseLevel.LEVEL_2, CourseLevel.LEVEL_3]:
        level_courses = [c for c in courses if c["level"] == level]
        print(f"  - {level.value}: {len(level_courses)} курсов")
    
    # Create sample lessons for first course
    sample_course = courses[0]
    lessons = [
        {
            "id": str(uuid.uuid4()),
            "course_id": sample_course["id"],
            "title": "Введение в ислам",
            "description": "Основные понятия и принципы ислама",
            "content": """
            <h2>Что такое ислам?</h2>
            <p>Ислам - это религия единобожия, основанная на поклонении Одному Всевышнему Аллаху.</p>
            
            <h3>Основные принципы:</h3>
            <ul>
                <li>Единобожие (Таухид)</li>
                <li>Следование Корану и Сунне</li>
                <li>Соблюдение пяти столпов ислама</li>
                <li>Праведная жизнь согласно исламским принципам</li>
            </ul>
            
            <h3>Пять столпов ислама:</h3>
            <ol>
                <li><strong>Шахада</strong> - свидетельство веры</li>
                <li><strong>Салят</strong> - ежедневная молитва</li>
                <li><strong>Закят</strong> - обязательная милостыня</li>
                <li><strong>Саум</strong> - пост в месяц Рамадан</li>
                <li><strong>Хадж</strong> - паломничество в Мекку</li>
            </ol>
            """,
            "lesson_type": LessonType.TEXT,
            "video_url": None,
            "video_duration": None,
            "attachments": [],
            "order": 1,
            "is_published": True,
            "estimated_duration_minutes": 20,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "course_id": sample_course["id"],
            "title": "Шахада - свидетельство веры",
            "description": "Изучение первого столпа ислама",
            "content": """
            <h2>Шахада - основа исламской веры</h2>
            <p>Шахада - это свидетельство того, что нет божества, кроме Аллаха, и Мухаммад - Его посланник.</p>
            
            <h3>Текст шахады:</h3>
            <p><strong>Арабский:</strong> لا إله إلا الله محمد رسول الله</p>
            <p><strong>Транскрипция:</strong> Ля иляха илля Ллах, Мухаммадун расулю Ллах</p>
            <p><strong>Перевод:</strong> Нет божества, кроме Аллаха, Мухаммад - посланник Аллаха</p>
            
            <h3>Значение шахады:</h3>
            <ul>
                <li>Признание единственности Аллаха</li>
                <li>Отрицание поклонения кому-либо, кроме Аллаха</li>
                <li>Признание пророческой миссии Мухаммада ﷺ</li>
            </ul>
            """,
            "lesson_type": LessonType.MIXED,
            "video_url": "https://www.youtube.com/embed/example-video-1",
            "video_duration": 900,  # 15 minutes
            "attachments": [],
            "order": 2,
            "is_published": True,
            "estimated_duration_minutes": 25,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "course_id": sample_course["id"],
            "title": "Единобожие (Таухид)",
            "description": "Глубокое понимание концепции единобожия в исламе",
            "content": """
            <h2>Таухид - основа исламской веры</h2>
            <p>Таухид означает единобожие - веру в единственность и уникальность Аллаха.</p>
            
            <h3>Три категории Таухида:</h3>
            <ol>
                <li><strong>Таухид ар-Рубубийя</strong> - единственность в господстве</li>
                <li><strong>Таухид аль-Улюхийя</strong> - единственность в поклонении</li>
                <li><strong>Таухид аль-Асма ва-с-Сифат</strong> - единственность в именах и качествах</li>
            </ol>
            
            <h3>Важность Таухида:</h3>
            <p>Таухид является основой всех деяний мусульманина и условием принятия его поклонения Аллахом.</p>
            """,
            "lesson_type": LessonType.TEXT,
            "video_url": None,
            "video_duration": None,
            "attachments": [],
            "order": 3,
            "is_published": True,
            "estimated_duration_minutes": 30,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insert sample lessons
    await db.lessons.drop()
    await db.lessons.insert_many(lessons)
    print(f"Создано {len(lessons)} примеров уроков для курса '{sample_course['title']}'")
    
    # Update course lessons count
    await db.courses.update_one(
        {"id": sample_course["id"]},
        {"$set": {"lessons_count": len(lessons)}}
    )
    
    # Create sample test
    sample_test = {
        "id": str(uuid.uuid4()),
        "title": "Проверка знаний: Основы ислама",
        "description": "Тест на понимание базовых концепций ислама",
        "course_id": sample_course["id"],
        "lesson_id": None,  # Course-level test
        "questions": [
            {
                "id": str(uuid.uuid4()),
                "text": "Что означает слово 'ислам'?",
                "question_type": QuestionType.SINGLE_CHOICE,
                "options": [
                    {"id": str(uuid.uuid4()), "text": "Покорность Аллаху", "is_correct": True},
                    {"id": str(uuid.uuid4()), "text": "Мир", "is_correct": False},
                    {"id": str(uuid.uuid4()), "text": "Вера", "is_correct": False},
                    {"id": str(uuid.uuid4()), "text": "Молитва", "is_correct": False}
                ],
                "correct_answer": None,
                "explanation": "Слово 'ислам' происходит от арабского корня 'с-л-м' и означает покорность и предание себя Аллаху.",
                "points": 1,
                "order": 1
            },
            {
                "id": str(uuid.uuid4()),
                "text": "Сколько столпов ислама существует?",
                "question_type": QuestionType.SINGLE_CHOICE,
                "options": [
                    {"id": str(uuid.uuid4()), "text": "3", "is_correct": False},
                    {"id": str(uuid.uuid4()), "text": "4", "is_correct": False},
                    {"id": str(uuid.uuid4()), "text": "5", "is_correct": True},
                    {"id": str(uuid.uuid4()), "text": "6", "is_correct": False}
                ],
                "correct_answer": None,
                "explanation": "В исламе существует пять столпов: шахада, салят, закят, саум и хадж.",
                "points": 1,
                "order": 2
            },
            {
                "id": str(uuid.uuid4()),
                "text": "Шахада является первым столпом ислама",
                "question_type": QuestionType.TRUE_FALSE,
                "options": [
                    {"id": str(uuid.uuid4()), "text": "Верно", "is_correct": True},
                    {"id": str(uuid.uuid4()), "text": "Неверно", "is_correct": False}
                ],
                "correct_answer": None,
                "explanation": "Да, шахада (свидетельство веры) является первым и основным столпом ислама.",
                "points": 1,
                "order": 3
            }
        ],
        "time_limit_minutes": 15,
        "passing_score": 70,
        "max_attempts": 3,
        "is_published": True,
        "order": 1,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert sample test
    await db.tests.drop()
    await db.tests.insert_one(sample_test)
    print(f"Создан пример теста '{sample_test['title']}'")
    
    # Update course tests count
    await db.courses.update_one(
        {"id": sample_course["id"]},
        {"$inc": {"tests_count": 1}}
    )
    
    # Create some sample students and enrollments
    students = [
        {
            "id": str(uuid.uuid4()),
            "name": "Амир Исламов",
            "email": "amir@example.com",
            "total_score": 0,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "completed_courses": [],
            "current_level": CourseLevel.LEVEL_1
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Лейла Хасанова",
            "email": "leila@example.com",
            "total_score": 0,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "completed_courses": [],
            "current_level": CourseLevel.LEVEL_1
        }
    ]
    
    await db.students.drop()
    await db.students.insert_many(students)
    print(f"Создано {len(students)} примеров студентов")
    
    # Create sample enrollments
    enrollments = []
    for student in students:
        # Enroll each student in first level courses
        for course in courses[:3]:  # First 3 courses (Level 1)
            enrollment = {
                "id": str(uuid.uuid4()),
                "student_id": student["id"],
                "course_id": course["id"],
                "enrolled_at": datetime.utcnow(),
                "completed_at": None,
                "is_completed": False,
                "progress_percentage": 0,
                "current_lesson_id": lessons[0]["id"] if course["id"] == sample_course["id"] else None
            }
            enrollments.append(enrollment)
    
    await db.enrollments.drop()
    await db.enrollments.insert_many(enrollments)
    print(f"Создано {len(enrollments)} записей на курсы")
    
    print("\n✅ Инициализация структуры курсов завершена!")
    print("\n📊 Структура:")
    print("├── 1-й уровень: 3 курса (Основы)")
    print("├── 2-й уровень: 3 курса (Углубленное изучение)")  
    print("└── 3-й уровень: 3 курса (Продвинутое изучение)")
    print(f"\n📚 Всего создано:")
    print(f"   - Курсов: {len(courses)}")
    print(f"   - Уроков: {len(lessons)} (примеры)")
    print(f"   - Тестов: 1 (пример)")
    print(f"   - Преподавателей: {len(teachers)}")
    print(f"   - Студентов: {len(students)}")

if __name__ == "__main__":
    asyncio.run(init_course_structure())