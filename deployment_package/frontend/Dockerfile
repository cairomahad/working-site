# Сборка приложения
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Продакшн сервер
FROM node:18-alpine

WORKDIR /app

# Устанавливаем serve для статических файлов
RUN npm install -g serve

# Копируем собранное приложение
COPY --from=builder /app/build ./build

# Открываем порт
EXPOSE 3000

# Команда запуска
CMD ["serve", "-s", "build", "-l", "3000"]