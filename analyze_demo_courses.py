#!/usr/bin/env python3
"""
Поиск автоматически создаваемых курсов - анализ базы данных
"""

import os
import sys
sys.path.append('/app/backend')

from supabase_client import supabase_client
import asyncio

async def analyze_demo_courses():
    """Анализируем как создаются демо курсы"""
    try:
        print("🔍 АНАЛИЗ ДЕМО КУРСОВ В БАЗЕ ДАННЫХ")
        print("=" * 50)
        
        # Получаем все курсы
        courses = await supabase_client.get_records("courses", order_by="created_at")
        
        print(f"📚 Всего курсов: {len(courses)}")
        print()
        
        demo_patterns = ["Основы Ислама", "Очищение и молитва", "Изучение Корана"]
        demo_courses = []
        
        for course in courses:
            print(f"🎓 КУРС: {course['title']}")
            print(f"   🆔 ID: {course['id']}")
            print(f"   📅 Создан: {course['created_at']}")
            print(f"   👨‍🏫 Преподаватель: {course.get('teacher_name', 'N/A')}")
            print(f"   📖 Уроков: {course['lessons_count']}")
            print(f"   📝 Тестов: {course['tests_count']}")
            print(f"   📊 Статус: {course.get('status', 'N/A')}")
            
            # Проверяем, является ли курс демо
            if any(pattern in course['title'] for pattern in demo_patterns):
                demo_courses.append(course)
                print("   ⭐ ДЕМО КУРС ОБНАРУЖЕН!")
            
            print()
        
        print("=" * 50)
        print(f"🎯 НАЙДЕНО ДЕМО КУРСОВ: {len(demo_courses)}")
        
        if demo_courses:
            print("\n📋 АНАЛИЗ ДЕМО КУРСОВ:")
            for course in demo_courses:
                print(f"   • {course['title']}")
                
                # Получаем уроки курса
                lessons = await supabase_client.get_records("lessons", {"course_id": course["id"]})
                if lessons:
                    print(f"     📚 Уроки ({len(lessons)}):")
                    for lesson in lessons[:3]:  # Показываем первые 3 урока
                        print(f"       - {lesson.get('title', 'Без названия')}")
                    if len(lessons) > 3:
                        print(f"       ... и ещё {len(lessons) - 3} уроков")
                
                # Получаем тесты курса  
                tests = await supabase_client.get_records("tests", {"course_id": course["id"]})
                if tests:
                    print(f"     📝 Тесты ({len(tests)}):")
                    for test in tests[:2]:
                        print(f"       - {test.get('title', 'Без названия')}")
                    if len(tests) > 2:
                        print(f"       ... и ещё {len(tests) - 2} тестов")
                
                print()
        
        print("🔎 ВОЗМОЖНЫЕ ИСТОЧНИКИ ДЕМО ДАННЫХ:")
        print("   1. Supabase SQL функции/триггеры при первом запуске")
        print("   2. Скрипт инициализации, который уже выполнился")  
        print("   3. Данные загружены напрямую в Supabase Dashboard")
        print("   4. Скрипт autostart_supabase.py (файл не найден)")
        
        # Проверяем админов - возможно они создают курсы при создании
        admins = await supabase_client.get_records("admin_users")
        print(f"\n👨‍💼 Найдено админов: {len(admins)}")
        for admin in admins:
            print(f"   • {admin.get('email', 'N/A')} (создан: {admin.get('created_at', 'N/A')})")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_demo_courses())