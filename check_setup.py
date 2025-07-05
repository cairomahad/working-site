#!/usr/bin/env python3
"""
Скрипт проверки настройки проекта на Replit
"""

import asyncio
import sys
import os
import requests
import subprocess

# Добавляем путь к backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def check_environment():
    """Проверяем переменные окружения"""
    print("🔍 Проверка переменных окружения...")
    
    replit_vars = ['REPL_SLUG', 'REPL_OWNER', 'REPLIT_DEV_DOMAIN']
    found_vars = []
    
    for var in replit_vars:
        if os.getenv(var):
            found_vars.append(f"{var}={os.getenv(var)}")
    
    if found_vars:
        print("✅ Переменные Replit найдены:")
        for var in found_vars:
            print(f"   {var}")
    else:
        print("⚠️  Переменные Replit не найдены (возможно, локальная разработка)")

def check_files():
    """Проверяем необходимые файлы"""
    print("\n📁 Проверка файлов...")
    
    required_files = [
        'backend/server.py',
        'backend/supabase_client.py',
        'backend/models.py',
        'backend/.env',
        'frontend/package.json',
        'frontend/.env',
        '.replit',
        'replit.nix',
        'setup-replit.sh'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - НЕ НАЙДЕН")

def check_dependencies():
    """Проверяем установленные зависимости"""
    print("\n📦 Проверка зависимостей...")
    
    # Проверяем Python пакеты
    try:
        import fastapi
        import supabase
        import pydantic
        print("✅ Python зависимости установлены")
    except ImportError as e:
        print(f"❌ Отсутствуют Python зависимости: {e}")
    
    # Проверяем Node.js зависимости
    if os.path.exists('frontend/node_modules'):
        print("✅ Node.js зависимости установлены")
    else:
        print("❌ Node.js зависимости не установлены")

async def check_database():
    """Проверяем подключение к базе данных"""
    print("\n🗄️  Проверка базы данных...")
    
    try:
        from supabase_client import supabase_client
        
        # Проверяем подключение
        admin_count = await supabase_client.count_records("admin_users")
        courses_count = await supabase_client.count_records("courses")
        
        print(f"✅ База данных подключена")
        print(f"   Админов: {admin_count}")
        print(f"   Курсов: {courses_count}")
        
        if admin_count == 0 or courses_count == 0:
            print("⚠️  База данных пуста. Запустите: python init_database.py")
        
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")

def check_processes():
    """Проверяем запущенные процессы"""
    print("\n🔄 Проверка процессов...")
    
    try:
        # Проверяем supervisor
        result = subprocess.run(['supervisorctl', 'status'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Supervisor работает:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print("❌ Supervisor не работает")
    except Exception as e:
        print(f"❌ Ошибка проверки supervisor: {e}")

def check_urls():
    """Проверяем доступность URL"""
    print("\n🌐 Проверка URL...")
    
    # Читаем URL из frontend .env
    try:
        with open('frontend/.env', 'r') as f:
            env_content = f.read()
            for line in env_content.split('\n'):
                if line.startswith('REACT_APP_BACKEND_URL='):
                    backend_url = line.split('=', 1)[1].strip()
                    print(f"🔗 Backend URL: {backend_url}")
                    
                    # Проверяем API
                    try:
                        response = requests.get(f"{backend_url}/api/", timeout=10)
                        if response.status_code == 200:
                            print("✅ API доступен")
                        else:
                            print(f"⚠️  API вернул статус: {response.status_code}")
                    except Exception as e:
                        print(f"❌ API недоступен: {e}")
                    break
        else:
            print("❌ REACT_APP_BACKEND_URL не найден в frontend/.env")
    except Exception as e:
        print(f"❌ Ошибка чтения frontend/.env: {e}")

async def main():
    """Основная функция проверки"""
    print("🚀 Проверка настройки проекта 'Уроки Ислама'")
    print("=" * 50)
    
    check_environment()
    check_files()
    check_dependencies()
    await check_database()
    check_processes()
    check_urls()
    
    print("\n" + "=" * 50)
    print("✅ Проверка завершена!")
    print("\n📋 Что делать дальше:")
    print("1. Если есть ошибки - исправьте их")
    print("2. Если база пуста - запустите: python init_database.py")
    print("3. Перезапустите Replit (кнопка Run)")
    print("4. Проверьте сайт в браузере")

if __name__ == "__main__":
    asyncio.run(main())