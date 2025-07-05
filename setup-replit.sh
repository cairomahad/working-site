#!/bin/bash

echo "🚀 Настройка проекта 'Уроки Ислама' для Replit..."

# Получаем URL Replit
if [ -n "$REPL_SLUG" ] && [ -n "$REPL_OWNER" ]; then
    REPLIT_URL="https://$REPL_SLUG.$REPL_OWNER.repl.co"
elif [ -n "$REPLIT_DEV_DOMAIN" ]; then
    REPLIT_URL="https://$REPLIT_DEV_DOMAIN"
else
    # Fallback для локального развертывания
    REPLIT_URL="http://localhost:3000"
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
yarn install
cd ..

# Инициализируем базу данных
echo "🗄️  Инициализация базы данных..."
python init_database.py

# Создаем supervisor конфигурацию
echo "⚙️  Настройка supervisor..."
mkdir -p /tmp/supervisor/conf.d
cat > /tmp/supervisor/supervisord.conf << EOF
[unix_http_server]
file=/tmp/supervisor.sock

[supervisord]
logfile=/tmp/supervisord.log
logfile_maxbytes=50MB
logfile_backups=10
loglevel=info
pidfile=/tmp/supervisord.pid
nodaemon=false
minfds=1024
minprocs=200

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock

[program:backend]
command=python server.py
directory=/app/backend
autostart=true
autorestart=true
stdout_logfile=/tmp/backend.out.log
stderr_logfile=/tmp/backend.err.log
environment=PYTHONPATH="/app/backend"

[program:frontend]
command=yarn start
directory=/app/frontend
autostart=true
autorestart=true
stdout_logfile=/tmp/frontend.out.log
stderr_logfile=/tmp/frontend.err.log
environment=CI=true
EOF

# Запускаем supervisor
echo "🚀 Запуск сервисов..."
supervisord -c /tmp/supervisor/supervisord.conf

# Ждем запуска сервисов
sleep 5

# Проверяем статус
echo "📊 Статус сервисов:"
supervisorctl -c /tmp/supervisor/supervisord.conf status

echo ""
echo "🎉 Проект настроен и запущен!"
echo "📍 URL приложения: $REPLIT_URL"
echo "👤 Админ: admin@uroki-islama.ru / admin123"
echo "🔍 Для проверки API: $REPLIT_URL/api/"

# Держим скрипт активным
tail -f /tmp/backend.out.log /tmp/frontend.out.log