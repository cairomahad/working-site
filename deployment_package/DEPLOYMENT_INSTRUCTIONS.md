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
