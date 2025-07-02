#!/bin/bash

echo "🔄 Тестирование подключения к MongoDB Atlas..."
echo "============================================"

# Проверяем DNS
echo "1. Проверка DNS..."
nslookup cluster0.5uejhpq.mongodb.net

echo -e "\n2. Проверка подключения..."
cd /app/backend && python test_atlas_connection.py

echo -e "\n3. Если подключение успешно, перезапускаем backend..."
if [ $? -eq 0 ]; then
    sudo supervisorctl restart backend
    echo "✅ Backend перезапущен с MongoDB Atlas"
else
    echo "❌ Подключение не удалось. Проверьте настройки Atlas."
fi