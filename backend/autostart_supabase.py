#!/usr/bin/env python3
"""
Скрипт автозапуска для Supabase
Автоматически выполняется при старте сервера для обеспечения корректных данных
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Добавляем backend в PATH
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

from supabase_client import supabase_client

async def ensure_quality_courses():
    """Обеспечение наличия качественных курсов"""
    print("📚 Проверка качества курсов...")
    
    try:
        # Получаем все курсы
        all_courses = await supabase_client.get_records('courses')
        
        # Удаляем тестовые курсы с некачественными названиями
        test_course_names = ['олипо', 'оиом', 'тест', 'test']
        
        for course in all_courses:
            if course.get('title', '').lower() in test_course_names:
                await supabase_client.delete_record('courses', 'id', course['id'])
                print(f"🗑️ Удален тестовый курс: {course['title']}")
        
        # Проверяем количество качественных курсов
        quality_courses = await supabase_client.get_records('courses', filters={'status': 'published'})
        
        if len(quality_courses) < 3:
            print("➕ Создание качественных демо-курсов...")
            await create_quality_courses()
        
        print(f"✅ Проверка курсов завершена. Опубликовано курсов: {len(await supabase_client.get_records('courses', filters={'status': 'published'}))}")
        
    except Exception as e:
        print(f"❌ Ошибка при проверке курсов: {e}")

async def create_quality_courses():
    """Создание качественных курсов"""
    
    import uuid
    
    quality_courses = [
        {
            "id": str(uuid.uuid4()),
            "title": "Основы Ислама",
            "description": "Базовый курс для изучения основ исламской веры, включающий изучение столпов ислама, веры и основных обрядов.",
            "slug": "osnovy-islama",
            "image_url": "https://images.unsplash.com/photo-1591604466107-ec97de577aff?w=500&h=300&fit=crop",
            "level": "beginner",
            "difficulty": "easy",
            "estimated_duration_hours": 32,
            "lessons_count": 8,
            "tests_count": 3,
            "order": 1,
            "status": "published",
            "teacher_name": "Имам Али Евтеев",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Очищение и молитва",
            "description": "Подробное изучение правил очищения (тахара) и совершения молитвы (салят) согласно исламским традициям.",
            "slug": "ochischenie-i-molitva",
            "image_url": "https://images.unsplash.com/photo-1586592670929-4c1b7cbe65f3?w=500&h=300&fit=crop",
            "level": "beginner",
            "difficulty": "easy",
            "estimated_duration_hours": 24,
            "lessons_count": 6,
            "tests_count": 2,
            "order": 2,
            "status": "published",
            "teacher_name": "Устаз Абдуль-Басит",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Изучение Корана",
            "description": "Курс посвящен изучению Священного Корана: его истории, структуре, основным сурам и принципам чтения.",
            "slug": "izuchenie-korana",
            "image_url": "https://images.unsplash.com/photo-1606813074854-ad1df3b8e00a?w=500&h=300&fit=crop",
            "level": "intermediate",
            "difficulty": "medium",
            "estimated_duration_hours": 48,
            "lessons_count": 12,
            "tests_count": 4,
            "order": 3,
            "status": "published",
            "teacher_name": "Хафиз Микаиль",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    for course_data in quality_courses:
        try:            
            await supabase_client.create_record('courses', course_data)
            print(f"✅ Создан курс: {course_data['title']}")
            
        except Exception as e:
            print(f"❌ Ошибка при создании курса '{course_data['title']}': {e}")

async def ensure_admin_user():
    """Обеспечение наличия админа"""
    import uuid
    try:
        admin = await supabase_client.get_record('admin_users', 'email', 'admin@uroki-islama.ru')
        if not admin:
            admin_data = {
                "id": str(uuid.uuid4()),
                "username": "admin",
                "email": "admin@uroki-islama.ru",
                "full_name": "Администратор системы",
                "role": "admin",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "last_login": None
            }
            
            await supabase_client.create_record('admin_users', admin_data)
            print("✅ Создан админ: admin@uroki-islama.ru / admin123")
        else:
            print("✅ Админ уже существует")
    except Exception as e:
        print(f"❌ Ошибка при проверке админа: {e}")

async def ensure_team_members():
    """Обеспечение наличия команды"""
    import uuid
    try:
        team_count = await supabase_client.count_records('team_members')
        if team_count < 3:
            team_members = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Имам Али Евтеев",
                    "subject": "Основы веры и этика",
                    "description": "Имам с 15-летним стажем, специалист по исламской этике и основам веры.",
                    "image_base64": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face",
                    "order": 1,
                    "is_active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Устаз Абдуль-Басит",
                    "subject": "Коран и хадисы",
                    "description": "Знаток Корана и хадисов, имеет иджазу на преподавание Корана.",
                    "image_base64": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face",
                    "order": 2,
                    "is_active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Хафиз Микаиль",
                    "subject": "История Ислама",
                    "description": "Историк исламской цивилизации, специалист по раннему периоду Ислама.",
                    "image_base64": "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=400&h=400&fit=crop&crop=face",
                    "order": 3,
                    "is_active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            ]
            
            for member in team_members:
                try:
                    await supabase_client.create_record('team_members', member)
                    print(f"✅ Создан участник команды: {member['name']}")
                except Exception as e:
                    print(f"⚠️ Участник уже существует: {member['name']}")
        else:
            print(f"✅ Команда уже настроена ({team_count} участников)")
    except Exception as e:
        print(f"❌ Ошибка при проверке команды: {e}")

async def main():
    """Основная функция автозапуска"""
    print("🚀 Автозапуск Supabase - обеспечение качественных данных")
    print("=" * 60)
    
    try:
        # Проверяем подключение
        await supabase_client.get_records('courses', limit=1)
        print("✅ Подключение к Supabase активно")
        
        # Обеспечиваем качественные данные
        await ensure_admin_user()
        await ensure_quality_courses()
        await ensure_team_members()
        
        print("=" * 60)
        print("✅ Автозапуск завершен. Система готова к работе!")
        
    except Exception as e:
        print(f"❌ Ошибка автозапуска: {e}")
        print("⚠️ Проверьте настройки Supabase")

if __name__ == "__main__":
    asyncio.run(main())