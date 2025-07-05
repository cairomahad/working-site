#!/usr/bin/env python3
"""
Скрипт для проверки и автоматической настройки подключения к Supabase
Этот скрипт проверяет все компоненты подключения и исправляет проблемы
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Добавляем backend в PATH
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

def check_env_files():
    """Проверка наличия и содержимого .env файлов"""
    print("🔍 Проверка .env файлов...")
    
    backend_env = Path("backend/.env")
    frontend_env = Path("frontend/.env")
    
    # Проверка backend .env
    if not backend_env.exists():
        print("❌ backend/.env не найден!")
        return False
    
    # Читаем backend .env
    with open(backend_env, 'r') as f:
        backend_content = f.read()
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'USE_POSTGRES']
    missing_vars = []
    
    for var in required_vars:
        if var not in backend_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ В backend/.env отсутствуют переменные: {', '.join(missing_vars)}")
        return False
    
    # Проверяем настройку USE_POSTGRES
    if 'USE_POSTGRES=true' in backend_content:
        print("⚠️ USE_POSTGRES=true - переключаю на Supabase API...")
        # Заменяем на false
        new_content = backend_content.replace('USE_POSTGRES=true', 'USE_POSTGRES=false')
        with open(backend_env, 'w') as f:
            f.write(new_content)
        print("✅ Переключено на USE_POSTGRES=false")
    
    # Проверка frontend .env
    if not frontend_env.exists():
        print("❌ frontend/.env не найден!")
        return False
    
    # Читаем frontend .env
    with open(frontend_env, 'r') as f:
        frontend_content = f.read()
    
    if 'REACT_APP_BACKEND_URL' not in frontend_content:
        print("❌ В frontend/.env отсутствует REACT_APP_BACKEND_URL")
        return False
    
    print("✅ .env файлы настроены корректно")
    return True

def check_dependencies():
    """Проверка Python зависимостей"""
    print("📦 Проверка зависимостей...")
    
    try:
        import supabase
        print("✅ supabase library установлена")
    except ImportError:
        print("❌ supabase library не установлена")
        print("Выполните: pip install supabase")
        return False
    
    try:
        import httpx
        print("✅ httpx library установлена")
    except ImportError:
        print("❌ httpx library не установлена")
        return False
    
    return True

async def test_supabase_connection():
    """Тестирование подключения к Supabase"""
    print("🔌 Тестирование подключения к Supabase...")
    
    try:
        from supabase_client import supabase_client
        
        # Проверяем базовое подключение
        courses = await supabase_client.get_records('courses', limit=1)
        print(f"✅ Подключение к Supabase работает")
        
        # Проверяем основные таблицы
        tables_to_check = ['courses', 'admin_users', 'team_members']
        for table in tables_to_check:
            try:
                count = await supabase_client.count_records(table)
                print(f"✅ Таблица {table}: {count} записей")
            except Exception as e:
                print(f"⚠️ Проблема с таблицей {table}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к Supabase: {e}")
        return False

async def ensure_demo_data():
    """Убеждаемся, что есть демо-данные"""
    print("📊 Проверка демо-данных...")
    
    try:
        from supabase_client import supabase_client
        
        # Проверяем курсы
        courses = await supabase_client.get_records('courses', filters={'status': 'published'})
        if len(courses) < 3:
            print("⚠️ Мало опубликованных курсов, инициализирую демо-данные...")
            # Здесь можно вызвать init_demo_data.py
            import subprocess
            result = subprocess.run([sys.executable, 'backend/init_demo_data.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Демо-данные инициализированы")
            else:
                print(f"⚠️ Проблема при инициализации: {result.stderr}")
        else:
            print(f"✅ Найдено {len(courses)} опубликованных курсов")
        
        # Проверяем админа
        admin = await supabase_client.get_record('admin_users', 'email', 'admin@uroki-islama.ru')
        if admin:
            print("✅ Админ admin@uroki-islama.ru найден")
        else:
            print("⚠️ Админ не найден")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке данных: {e}")
        return False

def restart_services():
    """Перезапуск сервисов"""
    print("🔄 Перезапуск сервисов...")
    
    try:
        import subprocess
        
        # Перезапуск backend
        result = subprocess.run(['sudo', 'supervisorctl', 'restart', 'backend'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Backend перезапущен")
        else:
            print(f"⚠️ Проблема с перезапуском backend: {result.stderr}")
        
        # Перезапуск frontend (если нужно)
        result = subprocess.run(['sudo', 'supervisorctl', 'restart', 'frontend'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Frontend перезапущен")
        else:
            print(f"⚠️ Проблема с перезапуском frontend: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при перезапуске: {e}")
        return False

async def test_api_endpoints():
    """Тестирование API эндпоинтов"""
    print("🌐 Тестирование API...")
    
    try:
        import requests
        import time
        
        # Даем время сервису запуститься
        time.sleep(3)
        
        # Читаем backend URL из frontend .env
        frontend_env = Path("frontend/.env")
        if frontend_env.exists():
            with open(frontend_env, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        backend_url = line.split('=')[1].strip()
                        break
        else:
            backend_url = "http://localhost:8001"
        
        # Тестируем основные эндпоинты
        endpoints = [
            '/api/',
            '/api/courses',
            '/api/team'
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{backend_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ {endpoint} работает")
                else:
                    print(f"⚠️ {endpoint} вернул {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} недоступен: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании API: {e}")
        return False

def create_backup():
    """Создание резервной копии настроек"""
    print("💾 Создание резервной копии...")
    
    try:
        backup_dir = Path("supabase_backup")
        backup_dir.mkdir(exist_ok=True)
        
        # Копируем важные файлы
        import shutil
        
        files_to_backup = [
            "backend/.env",
            "frontend/.env",
            "backend/supabase_client.py",
            "backend/models.py"
        ]
        
        for file_path in files_to_backup:
            src = Path(file_path)
            if src.exists():
                dst = backup_dir / src.name
                shutil.copy2(src, dst)
                print(f"✅ Скопирован {file_path}")
        
        # Создаем архив
        import tarfile
        with tarfile.open(f"supabase_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz", "w:gz") as tar:
            tar.add(backup_dir, arcname="supabase_backup")
        
        print("✅ Резервная копия создана")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании резервной копии: {e}")
        return False

async def main():
    """Основная функция проверки и настройки"""
    print("🚀 Автоматическая настройка подключения к Supabase")
    print("=" * 60)
    
    all_ok = True
    
    # 1. Проверка .env файлов
    if not check_env_files():
        all_ok = False
    
    # 2. Проверка зависимостей
    if not check_dependencies():
        all_ok = False
    
    # 3. Перезапуск сервисов (если нужно)
    if not all_ok:
        restart_services()
        # Даем время запуститься
        await asyncio.sleep(5)
    
    # 4. Тестирование подключения
    if not await test_supabase_connection():
        all_ok = False
    
    # 5. Проверка демо-данных
    if not await ensure_demo_data():
        all_ok = False
    
    # 6. Тестирование API
    if not await test_api_endpoints():
        all_ok = False
    
    # 7. Создание резервной копии
    create_backup()
    
    print("=" * 60)
    if all_ok:
        print("✅ Все проверки пройдены! Supabase настроен корректно.")
        print("🌐 Ваш сайт готов к развертыванию на хостинге")
        print("📖 Подробная инструкция в файле SUPABASE_SETUP_GUIDE.md")
    else:
        print("⚠️ Обнаружены проблемы. Проверьте логи выше.")
    
    print("\n📋 Информация для хостинга:")
    print("SUPABASE_URL=https://kykzqxoxgcwqurnceslu.supabase.co")
    print("SUPABASE_ANON_KEY=<ключ из backend/.env>")
    print("USE_POSTGRES=false")

if __name__ == "__main__":
    asyncio.run(main())