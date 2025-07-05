# 🔧 Настройка проекта для Replit

## Шаг 1: Создайте .replit файл

Создайте файл `.replit` в корне проекта:

```toml
modules = ["python-3.11", "nodejs-18"]

[nix]
channel = "stable-23.11"

[[ports]]
localPort = 3000
externalPort = 80

[[ports]]
localPort = 5000
externalPort = 3001

[deployment]
build = ["sh", "-c", "cd backend && pip install -r requirements.txt && cd ../frontend && npm install && npm run build"]
run = ["sh", "-c", "cd backend && python -m uvicorn server:app --host 0.0.0.0 --port 5000 & cd frontend && npm start"]

[env]
PYTHONPATH = "/home/runner/$REPL_SLUG/backend"
```

## Шаг 2: Обновите backend/.env

```env
SUPABASE_URL=https://kykzqxoxgcwqurnceslu.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt5a3pxeG94Z2N3cXVybmNlc2x1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTQ4NzI0OCwiZXhwIjoyMDY3MDYzMjQ4fQ.wZcC233qDjrIuXn4it1j-YnxHak14v8GqxCCuW6VIb4
SECRET_KEY=uroki-islama-secret-key-2024
USE_POSTGRES=false
PORT=5000
```

## Шаг 3: Обновите frontend/.env

```env
REACT_APP_BACKEND_URL=https://ваш-repl-slug.вашusername.repl.co:3001
```

## Шаг 4: Создайте start.sh

Создайте файл `start.sh` в корне:

```bash
#!/bin/bash
echo "🚀 Запуск приложения в Replit..."

# Установка зависимостей backend
echo "📦 Установка Python зависимостей..."
cd backend
pip install -r requirements.txt

# Проверка подключения к Supabase
echo "🔌 Проверка подключения к Supabase..."
python -c "
import asyncio
import sys
sys.path.append('.')
from supabase_client import supabase_client

async def test():
    try:
        courses = await supabase_client.get_records('courses', limit=1)
        print('✅ Supabase подключен!')
    except Exception as e:
        print(f'❌ Ошибка Supabase: {e}')

asyncio.run(test())
"

# Запуск backend в фоне
echo "🔧 Запуск backend сервера..."
python -m uvicorn server:app --host 0.0.0.0 --port 5000 &
BACKEND_PID=$!

# Переход к frontend
cd ../frontend

# Установка зависимостей frontend
echo "📦 Установка Node.js зависимостей..."
npm install

# Запуск frontend
echo "🌐 Запуск frontend..."
npm start &
FRONTEND_PID=$!

# Ожидание завершения
wait $BACKEND_PID $FRONTEND_PID
```

## Шаг 5: Настройте Secrets в Replit

В Replit перейдите в раздел "Secrets" и добавьте:

```
SUPABASE_URL=https://kykzqxoxgcwqurnceslu.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt5a3pxeG94Z2N3cXVybmNlc2x1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTQ4NzI0OCwiZXhwIjoyMDY3MDYzMjQ4fQ.wZcC233qDjrIuXn4it1j-YnxHak14v8GqxCCuW6VIb4
SECRET_KEY=uroki-islama-secret-key-2024
USE_POSTGRES=false
```

## Шаг 6: Обновите server.py для Replit

Добавьте в начало backend/server.py:

```python
import os

# Для Replit - читаем порт из переменной среды
PORT = int(os.environ.get('PORT', 5000))

# В конце файла добавьте:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
```

## Шаг 7: Обновите package.json для frontend

В frontend/package.json добавьте прокси:

```json
{
  "name": "frontend",
  "proxy": "http://localhost:5000",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}
```