#!/bin/bash

echo "🚀 Автоматический деплой 'Уроки Ислама'"
echo "========================================"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Проверка root прав
if [[ $EUID -eq 0 ]]; then
   error "Не запускайте этот скрипт от root!"
   exit 1
fi

# 1. Обновление системы
log "Обновление системы..."
sudo apt update && sudo apt upgrade -y

# 2. Установка Docker
if ! command -v docker &> /dev/null; then
    log "Установка Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    log "Docker уже установлен"
fi

# 3. Установка Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log "Установка Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    log "Docker Compose уже установлен"
fi

# 4. Установка Git (если нужно)
if ! command -v git &> /dev/null; then
    log "Установка Git..."
    sudo apt install git -y
else
    log "Git уже установлен"
fi

# 5. Создание директории проекта
PROJECT_DIR="/home/$USER/uroki-islama"
if [ ! -d "$PROJECT_DIR" ]; then
    log "Создание директории проекта..."
    mkdir -p "$PROJECT_DIR"
fi

# 6. Получение IP адреса сервера
SERVER_IP=$(curl -s ifconfig.me)
log "IP адрес сервера: $SERVER_IP"

# 7. Настройка переменных окружения
log "Настройка переменных окружения..."

# Backend .env
cat > "$PROJECT_DIR/backend/.env" << EOF
MONGO_URL=mongodb+srv://plovcentr20:197724qqq@cluster0.5uejhpq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DB_NAME=uroki_islama_production
SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=production
EOF

# Frontend .env
cat > "$PROJECT_DIR/frontend/.env" << EOF
REACT_APP_BACKEND_URL=http://$SERVER_IP:8001
REACT_APP_ENVIRONMENT=production
EOF

# 8. Настройка файрвола
log "Настройка файрвола..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 8001/tcp
sudo ufw --force enable

# 9. Запуск приложения
log "Запуск приложения..."
cd "$PROJECT_DIR"
docker-compose down 2>/dev/null || true
docker-compose up -d --build

# 10. Проверка статуса
log "Проверка статуса сервисов..."
sleep 10
docker-compose ps

# 11. Вывод информации
echo ""
echo "🎉 Деплой завершен!"
echo "==================="
echo "Frontend: http://$SERVER_IP:3000"
echo "Backend API: http://$SERVER_IP:8001/api"
echo "Админка: http://$SERVER_IP:3000 (admin@uroki-islama.ru / admin123)"
echo ""
echo "Логи можно посмотреть командой:"
echo "cd $PROJECT_DIR && docker-compose logs -f"
echo ""
echo "Для остановки приложения:"
echo "cd $PROJECT_DIR && docker-compose down"
echo ""

warning "ВАЖНО: Смените пароли админов и SECRET_KEY перед продакшном!"
warning "Настройте HTTPS и домен для безопасности!"

exit 0