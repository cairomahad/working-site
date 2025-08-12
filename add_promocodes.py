#!/usr/bin/env python3
"""
Добавление новых промокодов SAVE10NOW и WELCOME25
"""

import os
import sys
sys.path.append('/app/backend')

from supabase_client import supabase_client
import asyncio

async def add_new_promocodes():
    """Добавить новые промокоды"""
    try:
        print("🔍 Получаем ID админа...")
        
        # Получаем ID первого админа
        admin_users = await supabase_client.get_records("admin_users", limit=1)
        if not admin_users:
            print("❌ Админы не найдены")
            return
            
        admin_id = admin_users[0]["id"]
        print(f"✅ ID админа: {admin_id}")
        
        # Промокоды для добавления
        new_promocodes = [
            {
                "code": "SAVE10NOW",
                "promocode_type": "all_courses",
                "description": "Скидка 10% на все курсы - ограниченное предложение",
                "price_rub": 4410,  # 4900 - 10% = 4410
                "discount_percent": 10,
                "is_active": True,
                "max_uses": 200,
                "used_count": 0,
                "created_by": admin_id,
                "created_at": "2025-08-12T20:45:00Z",
                "updated_at": "2025-08-12T20:45:00Z"
            },
            {
                "code": "WELCOME25", 
                "promocode_type": "all_courses",
                "description": "Приветственная скидка 25% для новых пользователей",
                "price_rub": 3675,  # 4900 - 25% = 3675
                "discount_percent": 25,
                "is_active": True,
                "max_uses": 100,
                "used_count": 0,
                "created_by": admin_id,
                "created_at": "2025-08-12T20:45:00Z",
                "updated_at": "2025-08-12T20:45:00Z"
            }
        ]
        
        for promo_data in new_promocodes:
            # Проверяем, существует ли уже такой промокод
            existing = await supabase_client.find_one("promocodes", {"code": promo_data["code"]})
            
            if existing:
                print(f"⚠️ Промокод {promo_data['code']} уже существует")
                continue
                
            # Создаем промокод
            result = await supabase_client.create_record("promocodes", promo_data)
            print(f"✅ Создан промокод: {result['code']}")
            print(f"   💰 Цена: {result['price_rub']} руб (скидка {result['discount_percent']}%)")
            print(f"   📝 Описание: {result['description']}")
            print(f"   🎯 Лимит использований: {result['max_uses']}")
            print()
        
        print("📊 Все промокоды в базе:")
        all_promocodes = await supabase_client.get_records("promocodes", order_by="created_at")
        for promo in all_promocodes:
            status = "🟢" if promo["is_active"] else "🔴"
            print(f"  {status} {promo['code']} - {promo['description']} ({promo['price_rub']} руб)")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(add_new_promocodes())