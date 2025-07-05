#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт тестирования развертывания
Проверяет все основные функции после развертывания на Replit
"""

import asyncio
import sys
import os
import subprocess
import json

# Добавляем путь к backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_database_connection():
    """Тест подключения к базе данных"""
    print("🗄️  Тестирование базы данных...")
    
    try:
        from supabase_client import supabase_client
        
        # Проверяем основные таблицы
        tables = ['admin_users', 'courses', 'lessons', 'tests', 'students', 'team_members', 'qa_questions']
        
        for table in tables:
            count = await supabase_client.count_records(table)
            print(f"   {table}: {count} записей")
        
        # Проверяем админа
        admin = await supabase_client.find_one("admin_users", {"username": "admin"})
        if admin:
            print(f"✅ Админ найден: {admin['email']}")
        else:
            print("❌ Админ не найден")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка БД: {e}")
        return False

async def test_admin_authentication():
    """Тест аутентификации администратора"""
    print("\n👤 Тестирование аутентификации...")
    
    try:
        # Читаем URL из frontend .env
        with open('frontend/.env', 'r') as f:
            env_content = f.read()
            backend_url = None
            for line in env_content.split('\n'):
                if line.startswith('REACT_APP_BACKEND_URL='):
                    backend_url = line.split('=', 1)[1].strip()
                    break
        
        if not backend_url:
            print("❌ Backend URL не найден")
            return False
        
        # Тестируем админ логин через curl
        cmd = [
            'curl', '-s', '-X', 'POST',
            f"{backend_url}/api/admin/login",
            '-H', 'Content-Type: application/json',
            '-d', '{"username":"admin","password":"admin123"}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                if 'access_token' in response:
                    print("✅ Админ аутентификация работает")
                    return True
                else:
                    print(f"❌ Неверный ответ: {response}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ Неверный JSON ответ: {result.stdout}")
                return False
        else:
            print(f"❌ Ошибка запроса: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка теста аутентификации: {e}")
        return False

async def test_api_endpoints():
    """Тест основных API эндпоинтов"""
    print("\n🔗 Тестирование API эндпоинтов...")
    
    try:
        # Получаем backend URL
        with open('frontend/.env', 'r') as f:
            env_content = f.read()
            backend_url = None
            for line in env_content.split('\n'):
                if line.startswith('REACT_APP_BACKEND_URL='):
                    backend_url = line.split('=', 1)[1].strip()
                    break
        
        if not backend_url:
            print("❌ Backend URL не найден")
            return False
        
        # Тестируем основные эндпоинты
        endpoints = [
            '/api/',
            '/api/courses',
            '/api/team',
            '/api/qa/questions',
            '/api/leaderboard'
        ]
        
        success_count = 0
        for endpoint in endpoints:
            cmd = ['curl', '-s', '-w', '%{http_code}', f"{backend_url}{endpoint}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Получаем HTTP код из конца ответа
                response = result.stdout
                if len(response) >= 3:
                    http_code = response[-3:]
                    if http_code.startswith('2'):  # 2xx статус
                        print(f"✅ {endpoint} → {http_code}")
                        success_count += 1
                    else:
                        print(f"⚠️  {endpoint} → {http_code}")
                else:
                    print(f"❌ {endpoint} → неизвестная ошибка")
            else:
                print(f"❌ {endpoint} → недоступен")
        
        return success_count >= len(endpoints) // 2  # Хотя бы половина должна работать
        
    except Exception as e:
        print(f"❌ Ошибка тестирования API: {e}")
        return False

def test_file_structure():
    """Тест структуры файлов"""
    print("\n📁 Тестирование структуры файлов...")
    
    required_files = [
        'backend/server.py',
        'backend/supabase_client.py',
        'backend/models.py',
        'backend/.env',
        'frontend/package.json',
        'frontend/.env',
        'frontend/src/App.js',
        '.replit',
        'replit.nix',
        'setup-replit.sh',
        'init_database.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_dependencies():
    """Тест установленных зависимостей"""
    print("\n📦 Тестирование зависимостей...")
    
    # Проверяем Python зависимости
    python_deps = ['fastapi', 'supabase', 'pydantic', 'uvicorn']
    python_ok = True
    
    for dep in python_deps:
        try:
            __import__(dep)
            print(f"✅ Python: {dep}")
        except ImportError:
            print(f"❌ Python: {dep}")
            python_ok = False
    
    # Проверяем Node.js зависимости
    node_ok = os.path.exists('frontend/node_modules')
    if node_ok:
        print("✅ Node.js: зависимости установлены")
    else:
        print("❌ Node.js: зависимости не установлены")
    
    return python_ok and node_ok

async def run_full_test():
    """Запуск полного тестирования"""
    print("🚀 Полное тестирование развертывания проекта 'Уроки Ислама'")
    print("=" * 60)
    
    tests = [
        ("Структура файлов", test_file_structure()),
        ("Зависимости", test_dependencies()),
        ("База данных", await test_database_connection()),
        ("API эндпоинты", await test_api_endpoints()),
        ("Аутентификация", await test_admin_authentication())
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        if result:
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ! Проект готов к использованию!")
        print("\n📋 Следующие шаги:")
        print("1. Откройте сайт в браузере")
        print("2. Войдите как админ: admin@uroki-islama.ru / admin123")
        print("3. Протестируйте функции сайта")
        print("4. Наслаждайтесь обучением!")
        return True
    else:
        print("⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("\n🔧 Рекомендации:")
        if not tests[0][1]:  # Структура файлов
            print("- Проверьте что все файлы загружены из GitHub")
        if not tests[1][1]:  # Зависимости
            print("- Перезапустите Replit для установки зависимостей")
        if not tests[2][1]:  # База данных
            print("- Запустите: python init_database.py")
        if not tests[3][1]:  # API
            print("- Проверьте URL в frontend/.env")
        if not tests[4][1]:  # Аутентификация
            print("- Убедитесь что база данных инициализирована")
        
        return False

if __name__ == "__main__":
    success = asyncio.run(run_full_test())
    sys.exit(0 if success else 1)