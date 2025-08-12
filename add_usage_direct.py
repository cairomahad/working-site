#!/usr/bin/env python3
"""
Добавить использование промокода напрямую через SQL
"""

import os
import sys
sys.path.append('/app/backend')

from supabase_client import supabase_client
import asyncio

async def add_promocode_usage_direct():
    """Добавить использование промокода прямым SQL запросом"""
    try:
        # ПАРАМЕТРЫ:
        promocode_code = "ШАМИЛЬ"
        user_email = "student@example.com"
        
        print(f"🔍 Добавляем использование промокода: {promocode_code}")
        
        # Находим промокод
        promocode = await supabase_client.find_one("promocodes", {"code": promocode_code})
        if not promocode:
            print(f"❌ Промокод {promocode_code} не найден!")
            return
            
        print(f"✅ Промокод найден: {promocode['description']}")
        
        # Добавляем запись использования с минимальными полями
        usage_data = {
            "promocode_id": promocode["id"],
            "promocode_code": promocode_code,
            "student_email": user_email,
            "course_ids": promocode.get("course_ids", []) if promocode.get("course_ids") else []
        }
        
        # Проверяем существующие записи
        existing = await supabase_client.find_one("promocode_usage", {
            "promocode_code": promocode_code,
            "student_email": user_email
        })
        
        if existing:
            print(f"⚠️ Пользователь {user_email} уже использовал промокод {promocode_code}")
            return
        
        result = await supabase_client.create_record("promocode_usage", usage_data)
        print(f"✅ УСПЕШНО ДОБАВЛЕНО ИСПОЛЬЗОВАНИЕ:")
        print(f"   👤 Пользователь: {result['student_email']}")
        print(f"   🎟️ Промокод: {result['promocode_code']}")
        print(f"   🆔 ID записи: {result['id']}")
        
        # Обновляем счетчик использований промокода
        new_used_count = promocode.get("used_count", 0) + 1
        await supabase_client.update_record("promocodes", "id", promocode["id"], {
            "used_count": new_used_count
        })
        print(f"   📊 Обновлен счетчик: {new_used_count} использований")
        
        # Показываем все использования
        all_usages = await supabase_client.get_records("promocode_usage")
        print(f"\n📋 Всего записей об использовании: {len(all_usages)}")
        for usage in all_usages:
            print(f"   - {usage['student_email']} использовал {usage['promocode_code']}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(add_promocode_usage_direct())