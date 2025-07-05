#!/usr/bin/env python3
"""
Скрипт для инициализации демо-данных в Supabase
Этот скрипт создает основные курсы, уроки и другие данные для демонстрации
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Добавляем текущую директорию в PATH для импорта
sys.path.append(str(Path(__file__).parent))

from supabase_client import supabase_client
from models import *

async def init_demo_courses():
    """Создание демо-курсов"""
    print("🚀 Инициализация демо-курсов...")
    
    # Проверим, есть ли уже публичные курсы
    existing_courses = await supabase_client.get_records('courses', filters={'status': 'published'})
    if len(existing_courses) >= 3:
        print(f"✅ Найдено {len(existing_courses)} опубликованных курсов, пропускаем создание")
        return
    
    demo_courses = [
        {
            "id": "course-001-basics",
            "title": "Основы Ислама",
            "description": "Базовый курс для изучения основ исламской веры, включающий изучение столпов ислама, веры и основных обрядов.",
            "slug": "osnovy-islama",
            "image_url": "https://images.unsplash.com/photo-1591604466107-ec97de577aff?w=500&h=300&fit=crop",
            "level": "beginner",
            "duration": "4 недели",
            "lessons_count": 8,
            "order": 1,
            "status": "published",
            "is_featured": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "course-002-prayer",
            "title": "Очищение и молитва",
            "description": "Подробное изучение правил очищения (тахара) и совершения молитвы (салят) согласно исламским традициям.",
            "slug": "ochischenie-i-molitva",
            "image_url": "https://images.unsplash.com/photo-1586592670929-4c1b7cbe65f3?w=500&h=300&fit=crop",
            "level": "beginner",
            "duration": "3 недели",
            "lessons_count": 6,
            "order": 2,
            "status": "published",
            "is_featured": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "course-003-quran",
            "title": "Изучение Корана",
            "description": "Курс посвящен изучению Священного Корана: его истории, структуре, основным сурам и принципам чтения.",
            "slug": "izuchenie-korana",
            "image_url": "https://images.unsplash.com/photo-1606813074854-ad1df3b8e00a?w=500&h=300&fit=crop",
            "level": "intermediate",
            "duration": "6 недель",
            "lessons_count": 12,
            "order": 3,
            "status": "published",
            "is_featured": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "course-004-culture",
            "title": "Культура Ислама",
            "description": "Премиум курс о богатой культуре исламской цивилизации: история, искусство, архитектура, философия и наука.",
            "slug": "kultura-islama",
            "image_url": "https://images.unsplash.com/photo-1605298862320-b2d2e7b5e0c7?w=500&h=300&fit=crop",
            "level": "advanced",
            "duration": "8 недель",
            "lessons_count": 15,
            "order": 4,
            "status": "published",
            "is_featured": True,
            "is_premium": True,
            "price": 2999,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    for course_data in demo_courses:
        try:
            existing = await supabase_client.get_record('courses', 'id', course_data['id'])
            if existing:
                print(f"⚠️ Курс '{course_data['title']}' уже существует")
                continue
                
            await supabase_client.create_record('courses', course_data)
            print(f"✅ Создан курс: {course_data['title']}")
            
        except Exception as e:
            print(f"❌ Ошибка при создании курса '{course_data['title']}': {e}")

async def init_demo_lessons():
    """Создание демо-уроков"""
    print("📚 Инициализация демо-уроков...")
    
    # Проверим, есть ли уже уроки
    existing_lessons = await supabase_client.count_records('lessons')
    if existing_lessons >= 5:
        print(f"✅ Найдено {existing_lessons} уроков, пропускаем создание")
        return
    
    demo_lessons = [
        {
            "id": "lesson-001-001",
            "course_id": "course-001-basics",
            "title": "Что такое Ислам?",
            "description": "Введение в исламскую веру, её основные принципы и место в мировых религиях.",
            "slug": "chto-takoe-islam",
            "content": """
# Что такое Ислам?

Ислам — это монотеистическая религия, основанная на вере в единого Бога (Аллаха) и следовании учению пророка Мухаммада (мир ему).

## Основные принципы:

1. **Единобожие (Таухид)** - вера в единого Бога
2. **Пророчество** - вера в пророков и посланников
3. **Священные книги** - вера в божественные писания
4. **Судный день** - вера в загробную жизнь
5. **Предопределение** - вера в божественную судьбу

## Пять столпов Ислама:

- **Шахада** - свидетельство веры
- **Салят** - пятикратная молитва
- **Закят** - обязательная милостыня
- **Саум** - пост в месяц Рамадан  
- **Хадж** - паломничество в Мекку

Ислам призывает к миру, справедливости и милосердию ко всем творениям Аллаха.
            """,
            "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "order": 1,
            "duration": 15,
            "is_published": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "lesson-001-002",
            "course_id": "course-001-basics",
            "title": "Пророк Мухаммад (мир ему)",
            "description": "Жизнь и учение последнего пророка Ислама, его роль в истории человечества.",
            "slug": "prorok-muhammad",
            "content": """
# Пророк Мухаммад (мир ему)

Мухаммад (да благословит его Аллах и приветствует) — последний пророк и посланник Аллаха.

## Основные этапы жизни:

### Ранние годы (570-610 гг.)
- Рождение в Мекке
- Потеря родителей в раннем детстве
- Воспитание дедом и дядей
- Честность и надежность в торговле

### Призыв к Исламу (610-632 гг.)
- Первое откровение в пещере Хира
- Начало проповедования
- Переселение в Медину (Хиджра)
- Создание мусульманской общины

## Качества пророка:
- **Правдивость** - всегда говорил правду
- **Честность** - был известен как Аль-Амин (Надежный)
- **Милосердие** - проявлял сострадание ко всем
- **Справедливость** - судил по справедливости
- **Скромность** - жил просто и скромно

Пророк Мухаммад (мир ему) является примером для всех мусульман.
            """,
            "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "order": 2,
            "duration": 20,
            "is_published": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": "lesson-002-001",
            "course_id": "course-002-prayer",
            "title": "Виды очищения",
            "description": "Изучение различных видов очищения в Исламе: малое омовение, большое омовение, таяммум.",
            "slug": "vidy-ochischeniya",
            "content": """
# Виды очищения (Тахара)

В Исламе существует несколько видов очищения, необходимых для совершения молитвы.

## Малое омовение (Вуду)

### Обязательные действия:
1. Омовение лица
2. Омовение рук до локтей
3. Протирание головы
4. Омовение ног до щиколоток

### Нарушители вуду:
- Выход газов
- Малая и большая нужда
- Сон
- Потеря сознания

## Большое омовение (Гусль)

Необходимо после:
- Полового сношения
- Менструации
- Послеродового кровотечения
- Семяизвержения

## Таяммум (Очищение песком)

Разрешается при:
- Отсутствии воды
- Болезни
- Крайней нужде

Очищение — это не только физическая, но и духовная подготовка к молитве.
            """,
            "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "order": 1,
            "duration": 18,
            "is_published": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    for lesson_data in demo_lessons:
        try:
            existing = await supabase_client.get_record('lessons', 'id', lesson_data['id'])
            if existing:
                print(f"⚠️ Урок '{lesson_data['title']}' уже существует")
                continue
                
            await supabase_client.create_record('lessons', lesson_data)
            print(f"✅ Создан урок: {lesson_data['title']}")
            
        except Exception as e:
            print(f"❌ Ошибка при создании урока '{lesson_data['title']}': {e}")

async def init_demo_team():
    """Создание демо-команды"""
    print("👥 Инициализация команды...")
    
    # Проверим, есть ли уже команда
    existing_team = await supabase_client.count_records('team_members')
    if existing_team >= 3:
        print(f"✅ Найдено {existing_team} участников команды, пропускаем создание")
        return
    
    demo_team = [
        {
            "id": "team-001",
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
            "id": "team-002",
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
            "id": "team-003",
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
    
    for member_data in demo_team:
        try:
            existing = await supabase_client.get_record('team_members', 'id', member_data['id'])
            if existing:
                print(f"⚠️ Участник '{member_data['name']}' уже существует")
                continue
                
            await supabase_client.create_record('team_members', member_data)
            print(f"✅ Создан участник команды: {member_data['name']}")
            
        except Exception as e:
            print(f"❌ Ошибка при создании участника '{member_data['name']}': {e}")

async def init_demo_admin():
    """Создание демо-админа"""
    print("🔐 Инициализация админа...")
    
    # Проверим, есть ли уже админ
    existing_admin = await supabase_client.get_record('admin_users', 'email', 'admin@uroki-islama.ru')
    if existing_admin:
        print("✅ Админ уже существует")
        return
    
    admin_data = {
        "id": "admin-001",
        "username": "admin",
        "email": "admin@uroki-islama.ru",
        "full_name": "Администратор системы",
        "role": "admin",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "last_login": None
    }
    
    try:
        await supabase_client.create_record('admin_users', admin_data)
        print("✅ Создан админ: admin@uroki-islama.ru / admin123")
    except Exception as e:
        print(f"❌ Ошибка при создании админа: {e}")

async def main():
    """Основная функция инициализации"""
    print("🚀 Начало инициализации демо-данных для Supabase...")
    
    try:
        # Проверим подключение
        await supabase_client.get_records('courses', limit=1)
        print("✅ Подключение к Supabase успешно")
        
        # Инициализируем данные
        await init_demo_admin()
        await init_demo_courses()
        await init_demo_lessons()
        await init_demo_team()
        
        print("\n✅ Инициализация завершена успешно!")
        print("🔗 Данные сохранены в Supabase и будут доступны при следующем запуске")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())