# ШАБЛОН CSV ДЛЯ УПРАВЛЕНИЯ ПРОМОКОДАМИ

## Файл: promocodes_template.csv

Используйте этот CSV файл для массового создания промокодов. 

### Поля CSV:

| Поле | Описание | Обязательное | Примеры |
|------|----------|--------------|---------|
| **code** | Код промокода | ✅ Да | SAVE20, НОВЫЙ2025, ТЕСТ123 |
| **promocode_type** | Тип промокода | ✅ Да | `all_courses` или `single_course` |
| **description** | Описание промокода | ✅ Да | "Скидка 20% на все курсы" |
| **price_rub** | Цена в рублях | ✅ Да | 4900, 0 (бесплатный), 3920 |
| **discount_percent** | Процент скидки | ❌ Нет | 10, 25, 50 (может быть пустым) |
| **is_active** | Активен ли промокод | ✅ Да | TRUE или FALSE |
| **max_uses** | Макс. использований | ❌ Нет | 100, 50 (пустое = без лимита) |
| **expires_at** | Дата истечения | ❌ Нет | 2025-12-31 23:59:59 |
| **course_ids** | ID курсов (для single_course) | ❌ Нет | `["course-id-1","course-id-2"]` |

### Типы промокодов:

1. **all_courses** - Полный доступ ко всем курсам и разделам (Уроки + Q&A)
2. **single_course** - Доступ к конкретным курсам (нужно указать course_ids)

### Примеры использования:

**Скидочный промокод:**
```csv
СКИДКА20,all_courses,Скидка 20% на все курсы,3920,20,TRUE,100,2025-12-31 23:59:59,
```

**Бесплатный промокод:**
```csv
БЕСПЛАТНО,all_courses,Бесплатный тестовый доступ,0,,TRUE,10,,
```

**Промокод для одного курса:**
```csv
КОРАН50,single_course,Скидка на курс Корана,2450,50,TRUE,25,,"[""4e89a0ff-527e-4d8d-93db-620feef87217""]"
```

### Как получить ID курсов:

1. Откройте Supabase Dashboard
2. Перейдите в Table Editor → courses
3. Скопируйте нужные ID из колонки 'id'
4. Для single_course используйте формат: `["id1","id2"]`

### Загрузка промокодов из CSV:

```sql
-- В Supabase SQL Editor выполните:
INSERT INTO promocodes (code, promocode_type, description, price_rub, discount_percent, is_active, max_uses, expires_at, course_ids, created_by)
SELECT 
    code,
    promocode_type,
    description, 
    price_rub::INTEGER,
    CASE WHEN discount_percent = '' THEN NULL ELSE discount_percent::INTEGER END,
    is_active::BOOLEAN,
    CASE WHEN max_uses = '' THEN NULL ELSE max_uses::INTEGER END,
    CASE WHEN expires_at = '' THEN NULL ELSE expires_at::TIMESTAMP END,
    CASE WHEN course_ids = '' THEN NULL ELSE course_ids::JSONB END,
    (SELECT id FROM admin_users LIMIT 1)
FROM your_csv_import_table;
```

### Полезные SQL команды:

**Проверить все промокоды:**
```sql
SELECT code, description, price_rub, discount_percent, is_active, used_count, max_uses 
FROM promocodes ORDER BY created_at DESC;
```

**Деактивировать промокод:**
```sql
UPDATE promocodes SET is_active = false WHERE code = 'ПРОМОКОД';
```

**Изменить лимит использований:**
```sql
UPDATE promocodes SET max_uses = 200 WHERE code = 'ПРОМОКОД';
```

**Посмотреть статистику использования:**
```sql
SELECT 
    p.code,
    p.used_count,
    p.max_uses,
    COUNT(pu.id) as actual_usage
FROM promocodes p 
LEFT JOIN promocode_usage pu ON p.id = pu.promocode_id
GROUP BY p.code, p.used_count, p.max_uses
ORDER BY p.used_count DESC;
```