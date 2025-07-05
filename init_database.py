#!/usr/bin/env python3
"""
Скрипт инициализации базы данных для проекта 'Уроки Ислама'
Создает все необходимые данные для работы приложения
"""

import asyncio
import os
import sys
from datetime import datetime
import uuid

# Добавляем путь к backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from supabase_client import supabase_client
    from models import *
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь что вы запускаете скрипт из корневой директории проекта")
    sys.exit(1)

async def init_database():
    """Инициализация базы данных с начальными данными"""
    print("🚀 Начинаем инициализацию базы данных Supabase...")
    
    try:
        # 1. Проверяем подключение
        print("📡 Проверяем подключение к Supabase...")
        admin_count = await supabase_client.count_records("admin_users")
        print(f"✅ Подключение работает. Найдено {admin_count} админов.")
        
        # 2. Создаем админа если его нет
        admin = await supabase_client.find_one("admin_users", {"username": "admin"})
        if not admin:
            print("👤 Создаем администратора...")
            admin_data = {
                "id": str(uuid.uuid4()),
                "username": "admin",
                "email": "admin@uroki-islama.ru",
                "full_name": "Главный Администратор",
                "role": "admin",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }
            await supabase_client.create_record("admin_users", admin_data)
            print("✅ Администратор создан: admin@uroki-islama.ru / admin123")
        else:
            print(f"✅ Администратор найден: {admin['email']}")
            
        # 3. Создаем команду если ее нет
        team_count = await supabase_client.count_records("team_members")
        if team_count == 0:
            print("👥 Создаем команду...")
            team_members = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Али Евтеев",
                    "subject": "Этика",
                    "image_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face",
                    "bio": "Специалист по исламской этике и нравственности",
                    "order": 1,
                    "is_active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Абдуль-Басит Микушкин", 
                    "subject": "Основы веры",
                    "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face",
                    "bio": "Эксперт по основам исламской веры и догматике",
                    "order": 2,
                    "is_active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Алексей Котенев",
                    "subject": "Практика веры",
                    "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face",
                    "bio": "Специалист по практическим аспектам ислама",
                    "order": 3,
                    "is_active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Микаиль Ганиев",
                    "subject": "История",
                    "image_url": "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=400&h=400&fit=crop&crop=face",
                    "bio": "Историк ислама и исламской цивилизации",
                    "order": 4,
                    "is_active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            ]
            
            for member in team_members:
                await supabase_client.create_record("team_members", member)
            print(f"✅ Создано {len(team_members)} членов команды")
        else:
            print(f"✅ Найдено {team_count} членов команды")
            
        # 4. Создаем курсы если их нет
        courses_count = await supabase_client.count_records("courses")
        if courses_count == 0:
            print("📚 Создаем демо-курсы...")
            
            # Создаем основной курс
            course_data = {
                "id": str(uuid.uuid4()),
                "title": "Основы ислама для начинающих",
                "slug": "osnovy-islama-dlya-nachinayushchih",
                "description": "Базовый курс для изучения основ исламской веры. Включает изучение пяти столпов ислама, основных принципов веры и практических аспектов религии.",
                "level": "level_1",
                "teacher_id": str(uuid.uuid4()),
                "teacher_name": "Али Евтеев",
                "status": "published",
                "difficulty": "Легко",
                "estimated_duration_hours": 3,
                "lessons_count": 0,
                "tests_count": 0,
                "order": 1,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            created_course = await supabase_client.create_record("courses", course_data)
            print(f"✅ Создан курс: {created_course['title']}")
            
            # Создаем уроки
            lessons_data = [
                {
                    "id": str(uuid.uuid4()),
                    "course_id": created_course["id"],
                    "title": "Что такое ислам?",
                    "slug": "chto-takoe-islam",
                    "description": "Введение в основы исламской веры и её принципы",
                    "content": """<div class="lesson-content">
                    <h2>Что такое ислам?</h2>
                    <p>Ислам - это монотеистическая религия, основанная пророком Мухаммадом (мир ему) в VII веке нашей эры в Аравии.</p>
                    
                    <h3>Основные принципы ислама:</h3>
                    <ul>
                    <li><strong>Единобожие (Таухид)</strong> - вера в единого Бога (Аллаха)</li>
                    <li><strong>Пророчество</strong> - вера в посланников Аллаха</li>
                    <li><strong>Священные писания</strong> - вера в божественные откровения</li>
                    <li><strong>Судный день</strong> - вера в загробную жизнь</li>
                    </ul>
                    
                    <h3>Пять столпов ислама:</h3>
                    <ol>
                    <li><strong>Шахада</strong> - свидетельство веры</li>
                    <li><strong>Салят</strong> - ежедневные молитвы (5 раз в день)</li>
                    <li><strong>Закят</strong> - обязательная благотворительность</li>
                    <li><strong>Саум</strong> - пост в месяц Рамадан</li>
                    <li><strong>Хадж</strong> - паломничество в Мекку</li>
                    </ol>
                    
                    <p>Ислам призывает к справедливости, милосердию и служению Богу через поклонение и добрые дела.</p>
                    </div>""",
                    "lesson_type": "text",
                    "order": 1,
                    "is_published": True,
                    "estimated_duration_minutes": 20,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "course_id": created_course["id"],
                    "title": "Пять столпов ислама",
                    "slug": "pyat-stolpov-islama",
                    "description": "Подробное изучение пяти основных обязанностей мусульманина",
                    "content": """<div class="lesson-content">
                    <h2>Пять столпов ислама</h2>
                    <p>Пять столпов ислама - это основные обязанности каждого мусульманина.</p>
                    
                    <h3>1. Шахада (Свидетельство веры)</h3>
                    <p>"Нет божества, кроме Аллаха, и Мухаммад - Его посланник"</p>
                    <p>Это основное исповедание веры в исламе.</p>
                    
                    <h3>2. Салят (Молитва)</h3>
                    <p>Мусульмане молятся пять раз в день:</p>
                    <ul>
                    <li>Фаджр - утренняя молитва</li>
                    <li>Зухр - полуденная молитва</li>
                    <li>Аср - послеполуденная молитва</li>
                    <li>Магриб - вечерняя молитва</li>
                    <li>Иша - ночная молитва</li>
                    </ul>
                    
                    <h3>3. Закят (Благотворительность)</h3>
                    <p>Обязательное пожертвование 2.5% от накоплений нуждающимся.</p>
                    
                    <h3>4. Саум (Пост)</h3>
                    <p>Пост в течение месяца Рамадан от рассвета до заката.</p>
                    
                    <h3>5. Хадж (Паломничество)</h3>
                    <p>Паломничество в Мекку, обязательное для тех, кто физически и финансово способен.</p>
                    </div>""",
                    "lesson_type": "text",
                    "order": 2,
                    "is_published": True,
                    "estimated_duration_minutes": 25,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            ]
            
            lesson_ids = []
            for lesson_data in lessons_data:
                created_lesson = await supabase_client.create_record("lessons", lesson_data)
                lesson_ids.append(created_lesson["id"])
                print(f"✅ Создан урок: {created_lesson['title']}")
            
            # Создаем тесты для уроков
            for i, lesson_id in enumerate(lesson_ids):
                test_data = {
                    "id": str(uuid.uuid4()),
                    "title": f"Тест к уроку {i+1}",
                    "description": f"Проверьте свои знания по уроку {i+1}",
                    "course_id": created_course["id"],
                    "lesson_id": lesson_id,
                    "time_limit_minutes": 15,
                    "passing_score": 70,
                    "max_attempts": 3,
                    "is_published": True,
                    "order": i+1,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                created_test = await supabase_client.create_record("tests", test_data)
                print(f"✅ Создан тест: {created_test['title']}")
                
                # Создаем вопросы для каждого теста
                if i == 0:  # Вопросы для первого урока
                    questions = [
                        {
                            "id": str(uuid.uuid4()),
                            "test_id": created_test["id"],
                            "text": "Сколько столпов ислама существует?",
                            "question_type": "single_choice",
                            "options": [
                                {"id": str(uuid.uuid4()), "text": "3", "is_correct": False},
                                {"id": str(uuid.uuid4()), "text": "4", "is_correct": False},
                                {"id": str(uuid.uuid4()), "text": "5", "is_correct": True},
                                {"id": str(uuid.uuid4()), "text": "6", "is_correct": False}
                            ],
                            "points": 1,
                            "order": 1
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "test_id": created_test["id"],
                            "text": "Как называется священная книга мусульман?",
                            "question_type": "single_choice",
                            "options": [
                                {"id": str(uuid.uuid4()), "text": "Тора", "is_correct": False},
                                {"id": str(uuid.uuid4()), "text": "Библия", "is_correct": False},
                                {"id": str(uuid.uuid4()), "text": "Коран", "is_correct": True},
                                {"id": str(uuid.uuid4()), "text": "Веды", "is_correct": False}
                            ],
                            "points": 1,
                            "order": 2
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "test_id": created_test["id"],
                            "text": "Кто основал ислам?",
                            "question_type": "single_choice",
                            "options": [
                                {"id": str(uuid.uuid4()), "text": "Иисус", "is_correct": False},
                                {"id": str(uuid.uuid4()), "text": "Мухаммад", "is_correct": True},
                                {"id": str(uuid.uuid4()), "text": "Моисей", "is_correct": False},
                                {"id": str(uuid.uuid4()), "text": "Будда", "is_correct": False}
                            ],
                            "points": 1,
                            "order": 3
                        }
                    ]
                else:  # Вопросы для второго урока
                    questions = [
                        {
                            "id": str(uuid.uuid4()),
                            "test_id": created_test["id"],
                            "text": "Как называется свидетельство веры в исламе?",
                            "question_type": "single_choice",
                            "options": [
                                {"id": str(uuid.uuid4()), "text": "Шахада", "is_correct": True},
                                {"id": str(uuid.uuid4()), "text": "Салят", "is_correct": False},
                                {"id": str(uuid.uuid4()), "text": "Закят", "is_correct": False},
                                {"id": str(uuid.uuid4()), "text": "Хадж", "is_correct": False}
                            ],
                            "points": 1,
                            "order": 1
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "test_id": created_test["id"],
                            "text": "Сколько раз в день мусульмане должны молиться?",
                            "question_type": "single_choice",
                            "options": [
                                {"id": str(uuid.uuid4()), "text": "3", "is_correct": False},
                                {"id": str(uuid.uuid4()), "text": "4", "is_correct": False},
                                {"id": str(uuid.uuid4()), "text": "5", "is_correct": True},
                                {"id": str(uuid.uuid4()), "text": "6", "is_correct": False}
                            ],
                            "points": 1,
                            "order": 2
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "test_id": created_test["id"],
                            "text": "Какой процент от накоплений составляет закят?",
                            "question_type": "single_choice",
                            "options": [
                                {"id": str(uuid.uuid4()), "text": "1%", "is_correct": False},
                                {"id": str(uuid.uuid4()), "text": "2.5%", "is_correct": True},
                                {"id": str(uuid.uuid4()), "text": "5%", "is_correct": False},
                                {"id": str(uuid.uuid4()), "text": "10%", "is_correct": False}
                            ],
                            "points": 1,
                            "order": 3
                        }
                    ]
                
                for question in questions:
                    await supabase_client.create_record("questions", question)
                print(f"✅ Создано {len(questions)} вопросов для теста")
            
        else:
            print(f"✅ Найдено {courses_count} курсов")
            
        # 5. Создаем Q&A вопросы если их нет
        qa_count = await supabase_client.count_records("qa_questions")
        if qa_count == 0:
            print("❓ Создаем Q&A вопросы...")
            qa_questions = [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Можно ли мусульманину есть халяль мясо?",
                    "question_text": "Я новичок в исламе. Обязательно ли есть только халяль мясо? Что если в моем городе нет халяль продуктов?",
                    "answer_text": "Да, мусульманам предписано употреблять только халяль пищу. Это один из важных принципов ислама. Если в вашем городе нет халяль мяса, вы можете обратиться к рыбе, овощам и другим разрешенным продуктам. Также можно заказывать халяль продукты через интернет.",
                    "category": "fiqh",
                    "tags": ["халяль", "питание", "фикх"],
                    "slug": "mozhno-li-musulmaninu-est-halyal-myaso",
                    "is_featured": True,
                    "views_count": 0,
                    "imam_name": "Имам Али",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Как правильно совершать омовение?",
                    "question_text": "Можете объяснить, как правильно совершать омовение (вуду) перед молитвой?",
                    "answer_text": "Омовение (вуду) совершается в следующем порядке: 1) Намерение, 2) Произнесение 'Бисмиллях', 3) Мытье рук до запястий, 4) Полоскание рта, 5) Промывание носа, 6) Мытье лица, 7) Мытье рук до локтей, 8) Протирание головы, 9) Мытье ног до щиколоток. Каждое действие повторяется три раза.",
                    "category": "ibadah",
                    "tags": ["омовение", "вуду", "молитва"],
                    "slug": "kak-pravilno-sovershat-omovenie",
                    "is_featured": True,
                    "views_count": 0,
                    "imam_name": "Имам Мухаммад",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Что читать в молитве новичку?",
                    "question_text": "Я только начинаю изучать ислам. Что минимально нужно знать наизусть для совершения молитвы?",
                    "answer_text": "Для начала вам необходимо выучить: 1) Суру 'Аль-Фатиха' (первая сура Корана), 2) Любую короткую суру (например, 'Аль-Ихляс'), 3) Основные фразы молитвы ('Аллаху акбар', 'Субхана раббийаль-азым', 'Субхана раббийаль-аля'). Постепенно добавляйте другие дуа и суры.",
                    "category": "ibadah",
                    "tags": ["молитва", "салят", "новичок"],
                    "slug": "chto-chitat-v-molitve-novichku",
                    "is_featured": False,
                    "views_count": 0,
                    "imam_name": "Имам Али",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            ]
            
            for qa in qa_questions:
                await supabase_client.create_record("qa_questions", qa)
            print(f"✅ Создано {len(qa_questions)} Q&A вопросов")
        else:
            print(f"✅ Найдено {qa_count} Q&A вопросов")
            
        print("\n🎉 Инициализация базы данных завершена успешно!")
        print("\n📋 ДАННЫЕ ДЛЯ ВХОДА:")
        print("👤 Администратор: admin@uroki-islama.ru / admin123")
        print("👥 Студент: любой email (создается автоматически)")
        print("\n🌐 Доступные разделы:")
        print("📚 Курсы и уроки")
        print("❓ Вопросы и ответы имама")
        print("👥 Информация о команде")
        print("🏆 Система лидерборда")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(init_database())