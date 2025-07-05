# 🗄️ Руководство по постоянному подключению к Supabase

## 📋 Как работает подключение к Supabase

### 1. **Основные компоненты подключения:**

- **SUPABASE_URL**: URL вашего проекта Supabase
- **SUPABASE_ANON_KEY**: Публичный анонимный ключ для доступа к базе данных
- **supabase_client.py**: Клиент для работы с Supabase API
- **server.py**: Основной сервер, который использует Supabase клиент

### 2. **Текущие настройки:**
```bash
SUPABASE_URL="https://kykzqxoxgcwqurnceslu.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
USE_POSTGRES=false  # Использует Supabase API вместо прямого PostgreSQL
```

## 🚀 Как сделать подключение постоянным

### 1. **Файлы, которые ОБЯЗАТЕЛЬНО нужно сохранить:**

#### `/app/backend/.env`
```env
SUPABASE_URL="https://kykzqxoxgcwqurnceslu.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt5a3pxeG94Z2N3cXVybmNlc2x1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTQ4NzI0OCwiZXhwIjoyMDY3MDYzMjQ4fQ.wZcC233qDjrIuXn4it1j-YnxHak14v8GqxCCuW6VIb4"
SECRET_KEY="uroki-islama-secret-key-2024"
USE_POSTGRES=false
```

#### `/app/frontend/.env`
```env
REACT_APP_BACKEND_URL=https://ваш-домен.com  # Замените на ваш домен
```

### 2. **Критически важные файлы:**
- `/app/backend/supabase_client.py` - Клиент для работы с Supabase
- `/app/backend/models.py` - Модели данных
- `/app/backend/server.py` - Основной сервер
- `/app/backend/requirements.txt` - Зависимости Python

## 🌐 Настройка для хостинга

### 1. **Переменные окружения на хостинге:**

При развертывании на хостинге установите эти переменные:

```bash
# Supabase настройки
SUPABASE_URL=https://kykzqxoxgcwqurnceslu.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt5a3pxeG94Z2N3cXVybmNlc2x1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTQ4NzI0OCwiZXhwIjoyMDY3MDYzMjQ4fQ.wZcC233qDjrIuXn4it1j-YnxHak14v8GqxCCuW6VIb4

# Настройки приложения
SECRET_KEY=uroki-islama-secret-key-2024
USE_POSTGRES=false

# Frontend URL (обновите на ваш домен)
REACT_APP_BACKEND_URL=https://ваш-домен.com
```

### 2. **Для разных типов хостинга:**

#### **Vercel/Netlify:**
```bash
# В dashboard → Settings → Environment Variables
SUPABASE_URL=https://kykzqxoxgcwqurnceslu.supabase.co
SUPABASE_ANON_KEY=ключ_из_файла_выше
USE_POSTGRES=false
```

#### **Heroku:**
```bash
heroku config:set SUPABASE_URL="https://kykzqxoxgcwqurnceslu.supabase.co"
heroku config:set SUPABASE_ANON_KEY="ключ_из_файла_выше"
heroku config:set USE_POSTGRES=false
```

#### **VPS/Dedicated Server:**
```bash
# Создать .env файл с теми же настройками
cp /app/backend/.env /ваш/путь/к/проекту/backend/.env
```

## 🔧 Проверка подключения

### 1. **Скрипт для проверки подключения:**

Создайте файл `test_connection.py`:
```python
import asyncio
import os
from supabase_client import supabase_client

async def test_connection():
    try:
        # Проверяем подключение
        courses = await supabase_client.get_records('courses')
        print(f"✅ Подключение работает! Найдено курсов: {len(courses)}")
        
        # Проверяем админов
        admins = await supabase_client.get_records('admin_users')
        print(f"✅ Найдено админов: {len(admins)}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
```

### 2. **Команда для проверки через API:**
```bash
curl https://ваш-домен.com/api/courses
```

## 📊 Информация о Supabase проекте

### Ваш текущий проект:
- **Project URL**: https://kykzqxoxgcwqurnceslu.supabase.co
- **Project ID**: kykzqxoxgcwqurnceslu
- **Region**: Автоматически определяется

### Доступ к Supabase Dashboard:
1. Зайдите на https://app.supabase.com
2. Найдите проект с ID: `kykzqxoxgcwqurnceslu`
3. Там вы можете видеть все данные, таблицы, статистику

## 🔒 Безопасность ключей

### **ВАЖНО**: 
- `SUPABASE_ANON_KEY` - это публичный ключ, его можно использовать в коде
- Не путайте с `service_role` ключом - тот приватный!
- Ваш ключ действует до 2067 года (expires: 2067063248)

## 🚀 Автоматическая инициализация данных

### Скрипт для автоматического создания демо-данных:
```bash
cd /app/backend
python init_demo_data.py
```

Этот скрипт создаст:
- Демо-курсы по Исламу
- Базовые уроки
- Команду преподавателей
- Админского пользователя

## 🔄 Резервное копирование настроек

### Создайте бэкап важных файлов:
```bash
# Создать папку с резервными копиями
mkdir supabase_backup

# Скопировать важные файлы
cp /app/backend/.env supabase_backup/
cp /app/frontend/.env supabase_backup/
cp /app/backend/supabase_client.py supabase_backup/
cp /app/backend/init_demo_data.py supabase_backup/

# Создать архив
tar -czf supabase_backup.tar.gz supabase_backup/
```

## ✅ Чек-лист для развертывания

- [ ] Скопированы все файлы проекта
- [ ] Установлены переменные окружения
- [ ] Проверено подключение к Supabase
- [ ] Запущен init_demo_data.py
- [ ] Протестирован API
- [ ] Обновлен REACT_APP_BACKEND_URL

## 🆘 Помощь при проблемах

### Если подключение не работает:
1. Проверьте переменные окружения
2. Убедитесь что USE_POSTGRES=false
3. Проверьте интернет-соединение к supabase.co
4. Перезапустите сервер

### Контакты поддержки:
- Supabase Support: https://supabase.com/support
- Документация: https://supabase.com/docs