# 🚀 Шпаргалка по развертыванию - БЫСТРЫЙ СТАРТ

## 📋 За 15 минут на любом хостинге

### 1. Выберите хостинг (рекомендую):
- **Timeweb.com** - лучший для новичков
- **Beget.com** - хорошая техподдержка
- **Любой VPS** с Ubuntu

### 2. Переменные окружения (главное!):

**Backend (.env в папке backend/):**
```env
SUPABASE_URL=https://kykzqxoxgcwqurnceslu.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt5a3pxeG94Z2N3cXVybmNlc2x1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTQ4NzI0OCwiZXhwIjoyMDY3MDYzMjQ4fQ.wZcC233qDjrIuXn4it1j-YnxHak14v8GqxCCuW6VIb4
SECRET_KEY=uroki-islama-secret-key-2024
USE_POSTGRES=false
```

**Frontend (.env в папке frontend/):**
```env
REACT_APP_BACKEND_URL=https://ВАШ_ДОМЕН.ru
```

### 3. Команды установки:

```bash
# Backend
cd backend
pip install -r requirements.txt
python server.py

# Frontend
cd frontend
npm install
npm run build
```

### 4. Конфигурация nginx:

```nginx
server {
    listen 80;
    server_name ваш-домен.ru;
    
    location / {
        root /path/to/frontend/build;
        try_files $uri /index.html;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### 5. Запуск:

```bash
# Backend
uvicorn server:app --host 0.0.0.0 --port 8000

# Проверка
curl http://ваш-домен.ru/api/courses
```

## ✅ Админ доступ:
- **Email:** admin@uroki-islama.ru
- **Пароль:** admin123

## 🔧 Если что-то не работает:

```bash
# Проверка подключения к базе
cd backend
python -c "
import asyncio
from supabase_client import supabase_client
asyncio.run(supabase_client.get_records('courses'))
print('База работает!')
"

# Проверка API
curl http://localhost:8000/api/

# Логи ошибок
tail -f /var/log/nginx/error.log
```

## 📱 Результат:
- ✅ Сайт работает на **https://ваш-домен.ru**
- ✅ **3 курса** уже загружены из Supabase
- ✅ **Админка** готова к работе
- ✅ **Все данные** сохраняются в облаке

**🎉 Готово! Сайт будет работать постоянно!**