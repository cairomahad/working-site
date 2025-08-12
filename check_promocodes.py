#!/usr/bin/env python3
"""
Проверим данные в таблице promocodes
"""

import os
import sys
sys.path.append('/app/backend')

from supabase_client import supabase_client
import asyncio

async def check_promocodes():
    """Проверяем промокоды в базе"""
    try:
        print("🔍 Проверяем данные в таблице promocodes...")
        
        # Получаем все промокоды
        promocodes = await supabase_client.get_records("promocodes")
        print(f"Найдено промокодов: {len(promocodes)}")
        
        for promo in promocodes:
            print(f"\nПромокод: {promo.get('code', 'N/A')}")
            print(f"  Тип: {promo.get('promocode_type', 'N/A')}")
            print(f"  Описание: {promo.get('description', 'N/A')}")
            print(f"  Курсы: {promo.get('course_ids', [])}")
            print(f"  Активен: {promo.get('is_active', False)}")
            print(f"  Использований: {promo.get('used_count', 0)}/{promo.get('max_uses', 'unlimited')}")
        
        if not promocodes:
            print("❌ Промокоды не найдены в базе данных")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_promocodes())