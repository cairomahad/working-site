#!/usr/bin/env python3
"""
Удаление демо курсов и связанных данных
"""

import os
import sys
sys.path.append('/app/backend')

from supabase_client import supabase_client
import asyncio

async def remove_demo_courses():
    """Удалить демо курсы полностью"""
    try:
        print("🗑️ УДАЛЕНИЕ ДЕМО КУРСОВ")
        print("=" * 50)
        
        # Демо курсы для удаления
        demo_course_names = ["Основы Ислама", "Очищение и молитва", "Изучение Корана"]
        
        for course_name in demo_course_names:
            print(f"\n🎯 Удаляем курс: {course_name}")
            
            # Найти курс
            course = await supabase_client.find_one("courses", {"title": course_name})
            if not course:
                print(f"   ⚠️ Курс '{course_name}' не найден")
                continue
                
            course_id = course["id"]
            print(f"   🆔 ID курса: {course_id}")
            
            # 1. Удаляем результаты тестов
            try:
                test_results = await supabase_client.get_records("test_results", {"course_id": course_id})
                for result in test_results:
                    await supabase_client.delete_record("test_results", "id", result["id"])
                print(f"   ✅ Удалено результатов тестов: {len(test_results)}")
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении результатов тестов: {e}")
            
            # 2. Удаляем прогресс уроков
            try:
                lesson_progress = await supabase_client.get_records("lesson_progress", {"course_id": course_id})
                for progress in lesson_progress:
                    await supabase_client.delete_record("lesson_progress", "id", progress["id"])
                print(f"   ✅ Удалено записей прогресса уроков: {len(lesson_progress)}")
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении прогресса: {e}")
            
            # 3. Удаляем вопросы тестов
            try:
                tests = await supabase_client.get_records("tests", {"course_id": course_id})
                total_questions = 0
                for test in tests:
                    questions = await supabase_client.get_records("test_questions", {"test_id": test["id"]})
                    for question in questions:
                        await supabase_client.delete_record("test_questions", "id", question["id"])
                        total_questions += 1
                print(f"   ✅ Удалено вопросов тестов: {total_questions}")
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении вопросов: {e}")
            
            # 4. Удаляем тесты
            try:
                tests = await supabase_client.get_records("tests", {"course_id": course_id})
                for test in tests:
                    await supabase_client.delete_record("tests", "id", test["id"])
                print(f"   ✅ Удалено тестов: {len(tests)}")
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении тестов: {e}")
            
            # 5. Удаляем уроки
            try:
                lessons = await supabase_client.get_records("lessons", {"course_id": course_id})
                for lesson in lessons:
                    await supabase_client.delete_record("lessons", "id", lesson["id"])
                print(f"   ✅ Удалено уроков: {len(lessons)}")
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении уроков: {e}")
            
            # 6. Удаляем доступы к курсу (если есть таблица)
            try:
                user_accesses = await supabase_client.get_records("user_course_access", {"course_id": course_id})
                for access in user_accesses:
                    await supabase_client.delete_record("user_course_access", "id", access["id"])
                print(f"   ✅ Удалено записей доступа: {len(user_accesses)}")
            except Exception as e:
                print(f"   ⚠️ Таблица user_course_access не найдена или ошибка: {e}")
            
            # 7. Наконец, удаляем сам курс
            try:
                await supabase_client.delete_record("courses", "id", course_id)
                print(f"   🎯 КУРС '{course_name}' ПОЛНОСТЬЮ УДАЛЕН!")
            except Exception as e:
                print(f"   ❌ Ошибка при удалении курса: {e}")
        
        print("\n" + "=" * 50)
        print("✅ УДАЛЕНИЕ ЗАВЕРШЕНО!")
        
        # Проверяем оставшиеся курсы
        remaining_courses = await supabase_client.get_records("courses")
        print(f"\n📚 Оставшиеся курсы: {len(remaining_courses)}")
        for course in remaining_courses:
            print(f"   • {course['title']} (создан: {course['created_at']})")
            
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(remove_demo_courses())