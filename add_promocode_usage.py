#!/usr/bin/env python3
"""
Добавить запись об использовании промокода в таблицу promocode_usage
"""

import os
import sys
import uuid
sys.path.append('/app/backend')

from supabase_client import supabase_client
import asyncio

async def add_promocode_usage():
    """Добавить запись об использовании промокода"""
    try:
        # ПАРАМЕТРЫ ДЛЯ ИЗМЕНЕНИЯ:
        promocode_to_use = "ШАМИЛЬ"  # ←← ИЗМЕНИТЕ НА НУЖНЫЙ ПРОМОКОД
        user_email = "test@example.com"  # ←← ИЗМЕНИТЕ EMAIL ПОЛЬЗОВАТЕЛЯ
        
        print(f"🔍 Ищем промокод: {promocode_to_use}")
        
        # Находим промокод
        promocode = await supabase_client.find_one("promocodes", {"code": promocode_to_use})
        if not promocode:
            print(f"❌ Промокод {promocode_to_use} не найден!")
            return
            
        print(f"✅ Промокод найден: {promocode['description']}")
        
        # Проверяем, не использовал ли уже этот пользователь промокод
        existing_usage = await supabase_client.find_one("promocode_usage", {
            "promocode_code": promocode_to_use,
            "student_email": user_email
        })
        
        if existing_usage:
            print(f"⚠️ Пользователь {user_email} уже использовал промокод {promocode_to_use}")
            return
            
        # Создаем запись об использовании
        usage_data = {
            "promocode_id": promocode["id"],
            "promocode_code": promocode_to_use,
            "student_id": str(uuid.uuid4()),  # Генерируем случайный ID студента
            "student_email": user_email,
            "course_ids": promocode.get("course_ids", []),
            "used_at": "2025-08-12T21:00:00Z"
        }
        
        result = await supabase_client.create_record("promocode_usage", usage_data)
        print(f"✅ УСПЕШНО ДОБАВЛЕНО ИСПОЛЬЗОВАНИЕ:")
        print(f"   👤 Пользователь: {result['student_email']}")
        print(f"   🎟️ Промокод: {result['promocode_code']}")
        print(f"   📅 Дата использования: {result['used_at']}")
        print(f"   🆔 ID записи: {result['id']}")
        
        # Обновляем счетчик использований промокода
        new_used_count = promocode.get("used_count", 0) + 1
        await supabase_client.update_record("promocodes", "id", promocode["id"], {
            "used_count": new_used_count
        })
        print(f"   📊 Обновлен счетчик: {new_used_count} использований")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(add_promocode_usage())