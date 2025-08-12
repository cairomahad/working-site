-- СОЗДАНИЕ ПРОМОКОДОВ В БАЗЕ ДАННЫХ SUPABASE
-- Выполните эти SQL команды в Supabase SQL Editor

-- 1. ПРОМОКОД ДЛЯ ПОЛНОГО ДОСТУПА КО ВСЕМ РАЗДЕЛАМ
INSERT INTO promocodes (
    code,                    -- Код промокода (например: "ИСЛАМ2025")
    promocode_type,          -- Тип: "all_courses" для полного доступа
    description,             -- Описание промокода
    price_rub,              -- Цена в рублях (может быть null)
    is_active,              -- Активен ли промокод
    max_uses,               -- Максимальное количество использований (null = без ограничений)
    expires_at,             -- Дата истечения (null = без истечения)
    created_by              -- ID администратора (используйте существующий admin ID)
) VALUES (
    'ИСЛАМ2025',            -- Промокод
    'all_courses',          -- Тип - полный доступ
    'Полный доступ ко всем разделам платформы "Уроки Ислама"',
    4900,                   -- Цена 4900 рублей
    true,                   -- Активен
    100,                    -- Максимум 100 использований
    '2026-12-31 23:59:59+00:00',  -- Истекает 31 декабря 2026
    (SELECT id FROM admin_users LIMIT 1)  -- ID первого админа
);

-- 2. ПРОМОКОД ДЛЯ ДОСТУПА К КОНКРЕТНОМУ КУРСУ
INSERT INTO promocodes (
    code,
    promocode_type,
    description,
    course_ids,             -- JSON массив с ID курсов
    price_rub,
    discount_percent,
    is_active,
    max_uses,
    expires_at,
    created_by
) VALUES (
    'НАМАЗ2025',           -- Промокод для урока о намазе
    'single_course',        -- Тип - доступ к конкретному курсу
    'Доступ к курсу "Очищение и молитва" со скидкой 30%',
    '["9f6e6e9a-16a2-48a9-9068-6ed420126208"]',  -- ID курса "Очищение и молитва"
    2900,                   -- Цена 2900 рублей
    30,                     -- Скидка 30%
    true,                   -- Активен
    50,                     -- Максимум 50 использований
    '2025-12-31 23:59:59+00:00',  -- Истекает в конце 2025 года
    (SELECT id FROM admin_users LIMIT 1)
);

-- 3. БЕСПЛАТНЫЙ ПРОМОКОД ДЛЯ ТЕСТИРОВАНИЯ
INSERT INTO promocodes (
    code,
    promocode_type,
    description,
    price_rub,
    is_active,
    max_uses,
    created_by
) VALUES (
    'ТЕСТ123',             -- Простой тестовый промокод
    'all_courses',
    'Бесплатный доступ для тестирования функциональности',
    0,                      -- Бесплатный
    true,
    10,                     -- Только 10 использований
    (SELECT id FROM admin_users LIMIT 1)
);

-- 4. ПРОМОКОД ТОЛЬКО ДЛЯ Q&A РАЗДЕЛА (через специальную логику)
INSERT INTO promocodes (
    code,
    promocode_type,
    description,
    price_rub,
    is_active,
    created_by
) VALUES (
    'ВОПРОСЫ2025',
    'all_courses',          -- Используем all_courses, но можно добавить логику для отдельных разделов
    'Доступ к разделу Вопросы и Ответы',
    1500,
    true,
    (SELECT id FROM admin_users LIMIT 1)
);

-- ПРОВЕРИТЬ СОЗДАННЫЕ ПРОМОКОДЫ:
SELECT 
    code,
    promocode_type,
    description,
    price_rub,
    discount_percent,
    is_active,
    used_count,
    max_uses,
    expires_at,
    created_at
FROM promocodes 
ORDER BY created_at DESC;

-- ПОСМОТРЕТЬ ИСПОЛЬЗОВАНИЕ ПРОМОКОДОВ:
SELECT 
    pc.code,
    pu.student_email,
    pu.used_at,
    pu.course_ids
FROM promocodes pc
LEFT JOIN promocode_usage pu ON pc.id = pu.promocode_id
ORDER BY pu.used_at DESC;