import asyncio
from supabase_client import supabase_client

async def create_default_data():
    """Создаем тестовые данные в существующих таблицах Supabase"""
    
    try:
        # Проверим, есть ли данные
        courses = await supabase_client.get_records("courses", limit=5)
        print(f"Найдено курсов: {len(courses)}")
        
        students = await supabase_client.get_records("students", limit=5)
        print(f"Найдено студентов: {len(students)}")
        
        team = await supabase_client.get_records("team_members", limit=5)
        print(f"Найдено членов команды: {len(team)}")
        
        # Если данных мало, добавим тестовые данные
        if len(courses) < 2:
            # Создадим тестовый курс
            course_data = {
                "id": "test-course-1",
                "title": "Тестовый курс PostgreSQL",
                "slug": "test-course-postgresql",
                "description": "Курс для тестирования прямого подключения к PostgreSQL через Supabase",
                "level": "level_1",
                "teacher_id": "teacher-1",
                "teacher_name": "Имам Тестович",
                "status": "published",
                "difficulty": "Начальный",
                "estimated_duration_hours": 2,
                "lessons_count": 0,
                "tests_count": 0,
                "order": 1
            }
            
            created_course = await supabase_client.create_record("courses", course_data)
            print(f"✅ Создан тестовый курс: {created_course.get('title')}")
        
        print("✅ База данных готова к работе!")
        
    except Exception as e:
        print(f"❌ Ошибка при создании данных: {e}")

if __name__ == "__main__":
    asyncio.run(create_default_data())