#!/usr/bin/env python3
"""
Скрипт для исправления категории в таблице qa_questions
Изменяет 'iqidah' на 'aqidah'
"""

import os
import sys
sys.path.append('/app/backend')

from supabase_client import supabase_client
import asyncio

async def fix_qa_categories():
    """Исправляем неправильные категории"""
    try:
        print("🔍 Проверяем данные в таблице qa_questions...")
        
        # Получаем все записи
        questions = await supabase_client.get_records("qa_questions")
        print(f"Найдено вопросов: {len(questions)}")
        
        # Проверяем категории
        categories_found = set()
        for question in questions:
            category = question.get('category', 'unknown')
            categories_found.add(category)
            print(f"Вопрос: {question.get('title', 'Без названия')[:50]}... | Категория: {category}")
        
        print(f"\nНайденные категории: {categories_found}")
        
        # Исправляем 'iqidah' на 'aqidah'
        fixed_count = 0
        for question in questions:
            if question.get('category') == 'iqidah':
                print(f"🔧 Исправляем категорию для: {question.get('title', 'Без названия')[:50]}...")
                await supabase_client.update_record(
                    "qa_questions", 
                    "id", 
                    question['id'], 
                    {"category": "aqidah"}
                )
                fixed_count += 1
        
        print(f"\n✅ Исправлено записей: {fixed_count}")
        
        # Проверяем результат
        questions_after = await supabase_client.get_records("qa_questions")
        categories_after = set()
        for question in questions_after:
            categories_after.add(question.get('category', 'unknown'))
        
        print(f"Категории после исправления: {categories_after}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(fix_qa_categories())