#!/usr/bin/env python3
"""
Добавить новый промокод в таблицу promocodes
"""

import os
import sys
sys.path.append('/app/backend')

from supabase_client import supabase_client
import asyncio

async def add_single_promocode():
    """Добавить один промокод"""
    try:
        print("🔍 Получаем ID админа...")
        
        admin_users = await supabase_client.get_records("admin_users", limit=1)
        if not admin_users:
            print("❌ Админы не найдены")
            return
            
        admin_id = admin_users[0]["id"]
        
        # ЗАМЕНИТЕ НА НУЖНЫЙ ПРОМОКОД:
        new_promocode = {
            "code": "СПЕЦИАЛЬНЫЙ2025",  # ←← ИЗМЕНИТЕ КОД ЗДЕСЬ
            "promocode_type": "all_courses",
            "description": "Специальный промокод с доступом ко всем курсам",  # ←← ИЗМЕНИТЕ ОПИСАНИЕ
            "price_rub": 2900,  # ←← ИЗМЕНИТЕ ЦЕНУ
            "discount_percent": 40,  # ←← ИЗМЕНИТЕ СКИДКУ (или уберите строку)
            "is_active": True,
            "max_uses": 50,  # ←← ИЗМЕНИТЕ ЛИМИТ (или уберите для безлимитного)
            "used_count": 0,
            "created_by": admin_id
        }
        
        # Проверяем, существует ли уже такой промокод
        existing = await supabase_client.find_one("promocodes", {"code": new_promocode["code"]})
        
        if existing:
            print(f"⚠️ Промокод {new_promocode['code']} уже существует!")
            return
            
        # Создаем промокод
        result = await supabase_client.create_record("promocodes", new_promocode)
        print(f"✅ УСПЕШНО СОЗДАН ПРОМОКОД:")
        print(f"   🎟️ Код: {result['code']}")
        print(f"   💰 Цена: {result['price_rub']} руб")
        if result.get('discount_percent'):
            print(f"   🎯 Скидка: {result['discount_percent']}%")
        print(f"   📝 Описание: {result['description']}")
        print(f"   🔢 Лимит: {result['max_uses']} использований")
        print(f"   🆔 ID: {result['id']}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(add_single_promocode())