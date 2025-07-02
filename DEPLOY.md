# 🚀 Полная инструкция по деплою "Уроки Ислама"

## 📋 Варианты хостинга (рекомендации)

### 🥇 Лучшие варианты для новичков:
1. **DigitalOcean** - $5/месяц
   - Простой интерфейс
   - Отличная документация
   - Быстрая поддержка

2. **Linode** - $5/месяц
   - Стабильная работа
   - Хорошая производительность

3. **Hetzner** - €3.29/месяц
   - Очень дешево
   - Хорошее качество

### 🇷🇺 Российские хостинги:
1. **Timeweb** - 200₽/месяц
2. **Beget** - 150₽/месяц
3. **Reg.ru** - 200₽/месяц

---

## 🛠 Способ 1: Автоматический деплой (рекомендуется)

### Шаг 1: Арендуйте VPS
- **OS**: Ubuntu 20.04+ или 22.04
- **RAM**: минимум 1GB (лучше 2GB)
- **CPU**: 1 core (лучше 2 cores)
- **Диск**: 20GB SSD

### Шаг 2: Подключитесь к серверу
```bash
ssh root@YOUR_SERVER_IP
# или
ssh ubuntu@YOUR_SERVER_IP
```

### Шаг 3: Скачайте и запустите скрипт деплоя
```bash
# Создайте пользователя (если нужно)
adduser deploy
usermod -aG sudo deploy
su - deploy

# Скачайте файлы проекта (нужно будет создать репозиторий)
git clone https://github.com/YOUR_USERNAME/uroki-islama.git
cd uroki-islama

# Запустите автодеплой
bash deploy.sh
```

### Шаг 4: Готово! 🎉
- Сайт: `http://YOUR_SERVER_IP:3000`
- API: `http://YOUR_SERVER_IP:8001/api`
- Админка: `admin@uroki-islama.ru / admin123`

---

## 🔧 Способ 2: Ручная установка

### 1. Подготовка сервера
```bash
# Обновление
sudo apt update && sudo apt upgrade -y

# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перелогиньтесь для применения групп
exit
ssh user@YOUR_SERVER_IP
```

### 2. Загрузка проекта
```bash
# Создайте папку проекта
mkdir ~/uroki-islama
cd ~/uroki-islama

# Скопируйте файлы из Emergent (или из репозитория)
```

### 3. Настройка переменных
```bash
# Backend
nano backend/.env
```
```env
MONGO_URL=mongodb+srv://plovcentr20:197724qqq@cluster0.5uejhpq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DB_NAME=uroki_islama_production
SECRET_KEY=your-super-secret-key-change-this
ENVIRONMENT=production
```

```bash
# Frontend
nano frontend/.env
```
```env
REACT_APP_BACKEND_URL=http://YOUR_SERVER_IP:8001
REACT_APP_ENVIRONMENT=production
```

### 4. Запуск
```bash
docker-compose up -d --build
```

### 5. Проверка
```bash
docker-compose ps
docker-compose logs -f
```

---

## 🌐 Способ 3: Heroku (Platform-as-a-Service)

### Подготовка для Heroku
```bash
# Создайте Procfile для backend
echo "web: uvicorn server:app --host 0.0.0.0 --port \$PORT" > backend/Procfile

# Создайте Procfile для frontend
echo "web: serve -s build -l \$PORT" > frontend/Procfile
```

### Деплой на Heroku
```bash
# Установите Heroku CLI
# Создайте два приложения: backend и frontend
heroku create uroki-islama-backend
heroku create uroki-islama-frontend

# Настройте переменные окружения
heroku config:set MONGO_URL="mongodb+srv://..." --app uroki-islama-backend
heroku config:set REACT_APP_BACKEND_URL="https://uroki-islama-backend.herokuapp.com" --app uroki-islama-frontend

# Деплой
git subtree push --prefix=backend heroku-backend main
git subtree push --prefix=frontend heroku-frontend main
```

---

## 🔐 Настройка домена и HTTPS

### С доменом (рекомендуется)
```bash
# Установите Certbot
sudo apt install certbot python3-certbot-nginx

# Получите SSL сертификат
sudo certbot --nginx -d your-domain.com

# Обновите .env файлы с доменом
REACT_APP_BACKEND_URL=https://your-domain.com/api
```

### Nginx конфигурация с доменом
```nginx
server {
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
}
```

---

## 📊 Мониторинг и обслуживание

### Полезные команды
```bash
# Просмотр логов
docker-compose logs -f

# Перезапуск
docker-compose restart

# Обновление
git pull origin main
docker-compose build
docker-compose up -d

# Резервная копия
mongodump --uri="mongodb+srv://..."

# Освобождение места
docker system prune -a
```

### Автоматические обновления
```bash
# Добавьте в crontab
crontab -e

# Добавьте строку (обновление каждый день в 3:00)
0 3 * * * cd /home/deploy/uroki-islama && git pull && docker-compose up -d --build
```

---

## ❗ Важные моменты безопасности

1. **Смените пароли:**
   - Админские пароли в базе данных
   - SECRET_KEY в backend/.env

2. **Файрвол:**
   ```bash
   sudo ufw allow 22,80,443/tcp
   sudo ufw enable
   ```

3. **Регулярные обновления:**
   ```bash
   sudo apt update && sudo apt upgrade
   ```

4. **Резервные копии:**
   - MongoDB Atlas (автоматические)
   - Файлы приложения (еженедельно)

---

## 🆘 Решение проблем

### Если не работает:
```bash
# Проверьте логи
docker-compose logs

# Проверьте статус
docker-compose ps

# Перезапустите
docker-compose down && docker-compose up -d
```

### Если не хватает памяти:
```bash
# Добавьте swap
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Если медленно работает:
- Увеличьте ресурсы VPS
- Оптимизируйте базу данных
- Используйте CDN для статики

---

## 📞 Поддержка

- **GitHub Issues**: https://github.com/YOUR_USERNAME/uroki-islama/issues
- **Email**: support@uroki-islama.ru
- **Telegram**: @your_support_bot