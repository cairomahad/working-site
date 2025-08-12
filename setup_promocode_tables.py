#!/usr/bin/env python3
"""
Создание таблицы promocode_usage если её нет
"""

import os
import sys
sys.path.append('/app/backend')

from supabase_client import supabase_client
import asyncio

async def setup_promocode_tables():
    """Создаем таблицы для использования промокодов"""
    try:
        print("🔍 Проверяем таблицы для промокодов...")
        
        # Проверяем существует ли таблица promocode_usage
        try:
            usage_data = await supabase_client.get_records("promocode_usage", limit=1)
            print("✅ Таблица promocode_usage уже существует")
        except:
            print("❌ Таблица promocode_usage не найдена - возможно, её нужно создать в Supabase")
        
        # Проверяем существует ли таблица user_course_access
        try:
            access_data = await supabase_client.get_records("user_course_access", limit=1)
            print("✅ Таблица user_course_access уже существует")
        except:
            print("❌ Таблица user_course_access не найдена - возможно, её нужно создать в Supabase")
        
        print("\n📋 SQL для создания таблиц (если нужно выполнить в Supabase SQL Editor):")
        print("""
-- Создание таблицы promocode_usage
CREATE TABLE IF NOT EXISTS promocode_usage (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    promocode_id UUID NOT NULL,
    promocode_code TEXT NOT NULL,
    student_id UUID NOT NULL,
    student_email TEXT NOT NULL,
    course_ids JSONB DEFAULT '[]'::jsonb,
    used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание таблицы user_course_access
CREATE TABLE IF NOT EXISTS user_course_access (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    student_email TEXT NOT NULL,
    course_id UUID NOT NULL,
    promocode_id UUID,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_promocode_usage_email ON promocode_usage(student_email);
CREATE INDEX IF NOT EXISTS idx_promocode_usage_code ON promocode_usage(promocode_code);
CREATE INDEX IF NOT EXISTS idx_user_course_access_email ON user_course_access(student_email);
CREATE INDEX IF NOT EXISTS idx_user_course_access_course ON user_course_access(course_id);
        """)
        
        print("\n🔧 Тестируем доступ к промокодам...")
        promocodes = await supabase_client.get_records("promocodes")
        for promo in promocodes:
            print(f"  📎 {promo.get('code')} - {promo.get('description')}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(setup_promocode_tables())