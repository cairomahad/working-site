#!/bin/bash
# Скрипт для подготовки файлов к развертыванию

echo "🚀 Подготовка файлов для развертывания..."

# Создаем папку для развертывания
mkdir -p deployment_package
cd deployment_package

# Копируем основные файлы приложения
echo "📁 Копирование файлов..."
cp -r ../backend ./
cp -r ../frontend ./
cp ../README_DEPLOYMENT.md ./
cp ../SUPABASE_SETUP_GUIDE.md ./

# Создаем файл с переменными окружения для хостинга
echo "🔧 Создание файла переменных окружения..."
cat > deployment_env.txt << 'EOF'
# ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ДЛЯ ХОСТИНГА

## Backend переменные (.env в папке backend/):
SUPABASE_URL=https://kykzqxoxgcwqurnceslu.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt5a3pxeG94Z2N3cXVybmNlc2x1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTQ4NzI0OCwiZXhwIjoyMDY3MDYzMjQ4fQ.wZcC233qDjrIuXn4it1j-YnxHak14v8GqxCCuW6VIb4
SECRET_KEY=uroki-islama-secret-key-2024
USE_POSTGRES=false

## Frontend переменные (.env в папке frontend/):
REACT_APP_BACKEND_URL=https://ВАШ_ДОМЕН.ru

## Системные переменные (для панели хостинга):
PYTHON_VERSION=3.11
NODE_VERSION=18
EOF

# Создаем инструкцию по развертыванию
cat > DEPLOYMENT_INSTRUCTIONS.md << 'EOF'
# 📋 Инструкция по развертыванию

## 1. Загрузите все файлы из этой папки на хостинг

## 2. Установите переменные окружения из файла deployment_env.txt

## 3. Установите зависимости:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend  
cd frontend
npm install
# или
yarn install
```

## 4. Соберите frontend:
```bash
cd frontend
npm run build
# или
yarn build
```

## 5. Запустите backend:
```bash
cd backend
python server.py
# или
uvicorn server:app --host 0.0.0.0 --port 8000
```

## 6. Настройте веб-сервер для обслуживания frontend и проксирования API

Админ доступ:
- Email: admin@uroki-islama.ru  
- Пароль: admin123
EOF

# Создаем архив для загрузки
echo "📦 Создание архива для загрузки..."
tar -czf ../uroki_islama_deployment.tar.gz .

cd ..
echo "✅ Файлы готовы к развертыванию!"
echo "📦 Архив создан: uroki_islama_deployment.tar.gz"
echo "📋 Следуйте инструкциям в DEPLOYMENT_INSTRUCTIONS.md"