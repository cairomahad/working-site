#!/usr/bin/env python3

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
from models import AdminUser, UserRole
import uuid

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin_user():
    """Create admin user with specified credentials"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.getenv('DB_NAME', 'test_database')]
    
    # Admin credentials
    admin_email = "miftahylum@gmail.com"
    admin_password = "197724"
    admin_username = "miftahylum"
    admin_name = "Администратор Мифтахюлум"
    
    print(f"Создание администратора...")
    print(f"Email: {admin_email}")
    print(f"Пароль: {admin_password}")
    print(f"Имя пользователя: {admin_username}")
    
    # Check if admin already exists
    existing_admin = await db.admins.find_one({
        "$or": [
            {"email": admin_email},
            {"username": admin_username}
        ]
    })
    
    if existing_admin:
        print("Обновление существующего администратора...")
        # Update existing admin
        hashed_password = pwd_context.hash(admin_password)
        
        await db.admins.update_one(
            {"$or": [{"email": admin_email}, {"username": admin_username}]},
            {"$set": {
                "username": admin_username,
                "email": admin_email,
                "full_name": admin_name,
                "hashed_password": hashed_password,
                "role": UserRole.SUPER_ADMIN,
                "is_active": True,
                "updated_at": datetime.utcnow()
            }}
        )
        print("✅ Администратор обновлен!")
    else:
        print("Создание нового администратора...")
        # Create new admin
        hashed_password = pwd_context.hash(admin_password)
        
        admin_obj = AdminUser(
            username=admin_username,
            email=admin_email,
            full_name=admin_name,
            role=UserRole.SUPER_ADMIN
        )
        
        admin_dict = admin_obj.dict()
        admin_dict["hashed_password"] = hashed_password
        
        await db.admins.insert_one(admin_dict)
        print("✅ Новый администратор создан!")
    
    # Verify admin can login
    admin = await db.admins.find_one({"email": admin_email})
    if admin:
        is_valid = pwd_context.verify(admin_password, admin["hashed_password"])
        print(f"Проверка пароля: {'✅ Корректно' if is_valid else '❌ Ошибка'}")
        
        print("\n🔐 Данные для входа в админ панель:")
        print("─" * 40)
        print(f"Email: {admin_email}")
        print(f"Пароль: {admin_password}")
        print(f"Роль: {admin.get('role')}")
        print("─" * 40)
        print("\n📋 Инструкция:")
        print("1. Откройте сайт")
        print("2. Нажмите 'Войти' в шапке")
        print("3. Введите указанные email и пароль")
        print("4. Система автоматически определит, что вы админ")
        print("5. Будет выполнен переход в админ панель")
    
    # Also update the default admin credentials if it exists
    default_admin = await db.admins.find_one({"username": "admin"})
    if default_admin:
        print("\n🔄 Обновление резервного админа...")
        backup_password = "admin123"
        backup_hashed = pwd_context.hash(backup_password)
        
        await db.admins.update_one(
            {"username": "admin"},
            {"$set": {
                "email": "admin@uroki-islama.ru",
                "hashed_password": backup_hashed,
                "updated_at": datetime.utcnow()
            }}
        )
        print(f"✅ Резервный админ (admin/admin123) также обновлен")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin_user())