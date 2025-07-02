#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к MongoDB Atlas
"""

import os
import asyncio
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import socket

load_dotenv()

async def test_atlas_connection():
    """Тестирование подключения к MongoDB Atlas"""
    
    print("🔍 Тестирование подключения к MongoDB Atlas...")
    print("=" * 60)
    
    # 1. Проверяем DNS разрешение
    print("\n1. Проверка DNS разрешения...")
    try:
        host = "cluster0.5uejhpq.mongodb.net"
        ip = socket.gethostbyname(host)
        print(f"✅ DNS разрешение работает: {host} -> {ip}")
    except Exception as e:
        print(f"❌ DNS разрешение не работает: {e}")
        return False
    
    # 2. Тестируем подключение к MongoDB
    print("\n2. Тестирование подключения к MongoDB...")
    try:
        mongo_url = os.environ['MONGO_URL']
        print(f"🔗 Строка подключения: {mongo_url}")
        
        client = AsyncIOMotorClient(
            mongo_url,
            serverSelectionTimeoutMS=10000,  # 10 секунд timeout
            connectTimeoutMS=10000
        )
        
        # Проверяем подключение
        print("⏳ Подключение...")
        server_info = await client.server_info()
        print(f"✅ Подключение успешно!")
        print(f"📍 Версия сервера: {server_info.get('version', 'Unknown')}")
        
        # Проверяем доступ к базе данных
        db = client[os.environ['DB_NAME']]
        collections = await db.list_collection_names()
        print(f"📦 База данных: {os.environ['DB_NAME']}")
        print(f"📚 Коллекции: {len(collections)} найдено")
        
        if collections:
            print("   Коллекции:", ", ".join(collections))
        else:
            print("   База данных пустая")
        
        # Проверяем операции записи/чтения
        print("\n3. Тестирование операций...")
        test_collection = db.connection_test
        
        # Вставляем тестовую запись
        test_doc = {"test": "connection", "timestamp": "2025-07-02"}
        result = await test_collection.insert_one(test_doc)
        print(f"✅ Запись создана: {result.inserted_id}")
        
        # Читаем запись
        found_doc = await test_collection.find_one({"test": "connection"})
        if found_doc:
            print(f"✅ Запись найдена: {found_doc['timestamp']}")
        
        # Удаляем тестовую запись
        await test_collection.delete_one({"test": "connection"})
        print("✅ Тестовая запись удалена")
        
        client.close()
        
        print("\n" + "=" * 60)
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ MongoDB Atlas готов к работе")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка подключения: {e}")
        print("\n🔧 Возможные решения:")
        print("1. Убедитесь, что кластер активен (не в состоянии 'Inactive')")
        print("2. Проверьте Network Access (IP Whitelist) в MongoDB Atlas")
        print("3. Убедитесь, что пользователь БД существует и имеет права")
        print("4. Проверьте правильность пароля")
        
        return False

if __name__ == "__main__":
    result = asyncio.run(test_atlas_connection())
    exit(0 if result else 1)