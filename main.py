#!/usr/bin/env python3
"""
Точка входа для Replit - объединенный FastAPI + React сервер
"""

import os
import subprocess
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Импортируем основное приложение
sys.path.append(str(Path(__file__).parent / "backend"))
from backend.server import app as backend_app

# Создаем основное приложение
app = FastAPI(title="Уроки Ислама - Full Stack")

# Монтируем backend API
app.mount("/api", backend_app)

# Функция для сборки React приложения
def build_frontend():
    """Собирает React приложение если нужно"""
    frontend_dir = Path("frontend")
    build_dir = frontend_dir / "build"
    
    if not build_dir.exists():
        print("🔨 Сборка React приложения...")
        os.chdir(frontend_dir)
        
        # Установка зависимостей
        subprocess.run(["npm", "install"], check=True)
        
        # Сборка приложения
        subprocess.run(["npm", "run", "build"], check=True)
        
        os.chdir("..")
        print("✅ React приложение собрано")

# Проверяем и собираем frontend при запуске
build_frontend()

# Монтируем статические файлы React
frontend_build = Path("frontend/build")
if frontend_build.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_build / "static")), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Отдает главную страницу React"""
        return FileResponse(str(frontend_build / "index.html"))
    
    @app.get("/{path:path}")
    async def serve_frontend_routes(path: str):
        """Отдает React роуты (SPA routing)"""
        file_path = frontend_build / path
        if file_path.is_file():
            return FileResponse(str(file_path))
        else:
            # Для SPA роутинга возвращаем index.html
            return FileResponse(str(frontend_build / "index.html"))

@app.get("/health")
async def health_check():
    """Проверка работоспособности"""
    return {"status": "healthy", "service": "Уроки Ислама"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"🚀 Запуск сервера на порту {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)