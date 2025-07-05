#!/bin/bash

echo "🚀 Настройка проекта 'Уроки Ислама' для Replit..."

# Получаем URL Replit
if [ -n "$REPL_SLUG" ] && [ -n "$REPL_ID" ] && [ -n "$REPL_OWNER" ]; then
    REPLIT_URL="https://${REPL_SLUG}-${REPL_ID}.${REPL_OWNER}.repl.co"
elif [ -n "$REPLIT_DEV_DOMAIN" ]; then
    REPLIT_URL="https://$REPLIT_DEV_DOMAIN"
else
    # Fallback для других случаев
    REPLIT_URL="https://$(hostname)"
fi

echo "📡 Обнаружен URL: $REPLIT_URL"

# Обновляем frontend .env
echo "🔧 Настройка frontend..."
cat > frontend/.env << EOF
WDS_SOCKET_PORT=443
REACT_APP_BACKEND_URL=$REPLIT_URL
EOF

echo "✅ Frontend настроен для: $REPLIT_URL"

# Проверяем backend .env
echo "🔧 Проверка backend конфигурации..."
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Создание backend .env файла..."
    cat > backend/.env << EOF
SUPABASE_URL="https://kykzqxoxgcwqurnceslu.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt5a3pxeG94Z2N3cXVybmNlc2x1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTQ4NzI0OCwiZXhwIjoyMDY3MDYzMjQ4fQ.wZcC233qDjrIuXn4it1j-YnxHak14v8GqxCCuW6VIb4"
SECRET_KEY="uroki-islama-secret-key-2024"
EOF
fi

# Устанавливаем зависимости backend
echo "📦 Установка зависимостей backend..."
cd backend
pip install -r requirements.txt
cd ..

# Устанавливаем зависимости frontend
echo "📦 Установка зависимостей frontend..."
cd frontend
npm install
cd ..

# Инициализируем базу данных
echo "🗄️  Инициализация базы данных..."
python init_database.py

# Запускаем сервисы
echo "🚀 Запуск сервисов..."

# Запускаем backend в фоне
cd backend
python server.py &
BACKEND_PID=$!
cd ..

# Ждем немного для запуска backend
sleep 3

# Запускаем frontend в фоне
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Проект запущен!"
echo "📍 URL приложения: $REPLIT_URL"
echo "👤 Админ: admin@uroki-islama.ru / admin123"
echo "🔍 Для проверки API: $REPLIT_URL/api/"
echo ""
echo "🔄 Сервисы:"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"

# Ждем завершения процессов
wait