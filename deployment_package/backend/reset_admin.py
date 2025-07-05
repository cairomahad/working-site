#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def reset_admin_password():
    """Reset admin password"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.getenv('DB_NAME', 'test_database')]
    
    # New password
    new_password = "admin123"
    hashed_password = pwd_context.hash(new_password)
    
    print(f"Сброс пароля для админа...")
    print(f"Новый пароль: {new_password}")
    print(f"Хэш пароля: {hashed_password}")
    
    # Update admin password
    result = await db.admins.update_one(
        {"username": "admin"},
        {"$set": {
            "hashed_password": hashed_password,
            "updated_at": datetime.utcnow()
        }}
    )
    
    if result.modified_count > 0:
        print("✅ Пароль админа успешно обновлен!")
    else:
        print("❌ Не удалось обновить пароль")
    
    # Verify password
    admin = await db.admins.find_one({"username": "admin"})
    if admin:
        is_valid = pwd_context.verify(new_password, admin["hashed_password"])
        print(f"Проверка пароля: {'✅ Корректно' if is_valid else '❌ Ошибка'}")
        
        print("\nДанные для входа:")
        print("Логин: admin")
        print("Пароль: admin123")
        print("Роль:", admin.get('role'))
    
    client.close()

if __name__ == "__main__":
    asyncio.run(reset_admin_password())