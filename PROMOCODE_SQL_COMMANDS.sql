-- БЫСТРЫЕ SQL КОМАНДЫ ДЛЯ SUPABASE

-- 1. ДОБАВИТЬ НОВЫЙ ПРОМОКОД:
INSERT INTO promocodes (code, promocode_type, description, price_rub, discount_percent, is_active, max_uses, created_by) 
VALUES (
    'ВАШ_КОД_ЗДЕСЬ',           -- Замените на ваш промокод
    'all_courses',             -- all_courses или single_course
    'Описание промокода',      -- Замените описание
    2900,                      -- Цена в рублях
    40,                        -- Процент скидки (или уберите эту строку)
    true,                      -- Активен
    100,                       -- Лимит использований
    (SELECT id FROM admin_users LIMIT 1)
);

-- 2. ДОБАВИТЬ ИСПОЛЬЗОВАНИЕ ПРОМОКОДА:
INSERT INTO promocode_usage (promocode_id, promocode_code, student_id, student_email, course_ids) 
VALUES (
    (SELECT id FROM promocodes WHERE code = 'ШАМИЛЬ'),  -- ID промокода
    'ШАМИЛЬ',                                           -- Код промокода
    gen_random_uuid(),                                  -- Случайный ID студента
    'user@example.com',                                 -- Email пользователя
    '[]'::jsonb                                         -- Список курсов
);

-- И ОБНОВИТЬ СЧЕТЧИК:
UPDATE promocodes 
SET used_count = used_count + 1 
WHERE code = 'ШАМИЛЬ';

-- 3. ПРОВЕРИТЬ ИСПОЛЬЗОВАНИЯ:
SELECT 
    pu.student_email,
    pu.promocode_code, 
    pu.used_at,
    p.description
FROM promocode_usage pu
JOIN promocodes p ON pu.promocode_id = p.id
ORDER BY pu.used_at DESC;

-- 4. СТАТИСТИКА ПО ПРОМОКОДАМ:
SELECT 
    code,
    description,
    used_count,
    max_uses,
    CASE 
        WHEN max_uses IS NULL THEN 'Без лимита'
        ELSE CONCAT(used_count, '/', max_uses)
    END as usage_stats
FROM promocodes 
ORDER BY used_count DESC;