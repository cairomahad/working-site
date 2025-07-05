#!/bin/bash

echo "🚀 Простой запуск проекта для Replit..."

# Устанавливаем зависимости если нужно
if [ ! -d "backend/__pycache__" ]; then
    echo "📦 Установка Python зависимостей..."
    cd backend && pip install -r requirements.txt && cd ..
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Установка Node зависимостей..."
    cd frontend && npm install && cd ..
fi

# Настраиваем URL для frontend
echo "🔧 Настройка URL..."
cat > frontend/.env << EOF
WDS_SOCKET_PORT=443
REACT_APP_BACKEND_URL=https://\${REPL_SLUG}-\${REPL_ID}.\${REPL_OWNER}.repl.co
EOF

# Инициализируем БД если нужно
echo "🗄️ Проверка базы данных..."
python init_database.py

# Запускаем backend
echo "🐍 Запуск backend..."
cd backend
python server.py &
cd ..

# Запускаем frontend  
echo "⚛️ Запуск frontend..."
cd frontend
npm start &
cd ..

echo "✅ Проект запущен!"
echo "🌐 Откройте Preview для просмотра сайта"
echo "👤 Админ: admin@uroki-islama.ru / admin123"

wait