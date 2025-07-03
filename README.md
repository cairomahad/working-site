# 🕌 Уроки Ислама - Образовательная платформа

**Уроки Ислама** — это современная веб-платформа для изучения основ ислама на русском языке с интерактивными тестами, системой прогресса и административной панелью.

## 🌟 Основные функции

### 📚 Для студентов:
- **Структурированные курсы** по различным темам ислама
- **Видеоуроки** с YouTube интеграцией  
- **Интерактивные тесты** с рандомизацией вопросов
- **Система баллов** и отслеживание прогресса
- **Лидерборд** для мотивации обучения
- **Q&A система** - вопросы и ответы имама
- **Премиум курсы** с системой промокодов

### 🛠️ Для администраторов:
- **Управление курсами** и уроками
- **Создание тестов** с множественными вопросами
- **Загрузка медиа** (видео, PDF, DOCX)
- **Управление командой** преподавателей
- **Система аналитики** и статистики
- **Q&A модерация** и управление

## 🏗️ Технический стек

- **Frontend**: React 19 + Tailwind CSS
- **Backend**: FastAPI (Python)
- **База данных**: Supabase (PostgreSQL)
- **Аутентификация**: JWT токены
- **Файловое хранилище**: Локальная файловая система
- **API**: RESTful с автоматической документацией

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.11+
- Node.js 18+
- Yarn package manager

### 1. Клонирование репозитория

```bash
git clone <your-repo-url>
cd uroki-islama
```

### 2. Настройка базы данных Supabase

1. Создайте аккаунт на [Supabase](https://supabase.com)
2. Создайте новый проект
3. Скопируйте URL и API Key

### 3. Настройка Backend

```bash
cd backend

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл:
SUPABASE_URL="your-supabase-url"
SUPABASE_ANON_KEY="your-supabase-key"
SECRET_KEY="your-secret-key"
```

### 4. Настройка Frontend

```bash
cd frontend

# Установка зависимостей
yarn install

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл:
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 5. Создание таблиц в Supabase

Выполните SQL скрипты в Supabase SQL Editor:

```sql
-- Создание таблиц
CREATE TABLE admin_users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'admin',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_login TIMESTAMPTZ
);

CREATE TABLE courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  description TEXT NOT NULL,
  level TEXT NOT NULL,
  teacher_id TEXT NOT NULL,
  teacher_name TEXT NOT NULL,
  status TEXT DEFAULT 'draft',
  difficulty TEXT NOT NULL,
  estimated_duration_hours INTEGER NOT NULL,
  lessons_count INTEGER DEFAULT 0,
  tests_count INTEGER DEFAULT 0,
  image_url TEXT,
  "order" INTEGER DEFAULT 1,
  prerequisites TEXT[] DEFAULT '{}',
  additional_materials TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE lessons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  slug TEXT NOT NULL,
  description TEXT,
  content TEXT NOT NULL,
  lesson_type TEXT NOT NULL,
  video_url TEXT,
  video_duration INTEGER,
  attachment_url TEXT,
  "order" INTEGER NOT NULL,
  is_published BOOLEAN DEFAULT TRUE,
  estimated_duration_minutes INTEGER DEFAULT 15,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT,
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
  time_limit_minutes INTEGER,
  passing_score INTEGER DEFAULT 70,
  max_attempts INTEGER DEFAULT 3,
  is_published BOOLEAN DEFAULT TRUE,
  "order" INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  test_id UUID REFERENCES tests(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  question_type TEXT NOT NULL,
  options JSONB DEFAULT '[]',
  correct_answer TEXT,
  explanation TEXT,
  points INTEGER DEFAULT 1,
  "order" INTEGER NOT NULL
);

CREATE TABLE students (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  total_score INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_activity TIMESTAMPTZ DEFAULT NOW(),
  completed_courses TEXT[] DEFAULT '{}',
  current_level TEXT DEFAULT 'level_1'
);

CREATE TABLE team_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  subject TEXT NOT NULL,
  image_url TEXT,
  image_base64 TEXT,
  bio TEXT,
  email TEXT,
  "order" INTEGER DEFAULT 1,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE qa_questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  question_text TEXT NOT NULL,
  answer_text TEXT NOT NULL,
  category TEXT NOT NULL,
  tags TEXT[] DEFAULT '{}',
  slug TEXT UNIQUE NOT NULL,
  is_featured BOOLEAN DEFAULT FALSE,
  views_count INTEGER DEFAULT 0,
  likes_count INTEGER DEFAULT 0,
  imam_name TEXT DEFAULT 'Имам',
  references TEXT[] DEFAULT '{}',
  related_questions TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE test_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id TEXT NOT NULL,
  test_id UUID REFERENCES tests(id) ON DELETE CASCADE,
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
  selected_questions TEXT[] DEFAULT '{}',
  shuffled_options JSONB DEFAULT '{}',
  answers JSONB DEFAULT '{}',
  score INTEGER DEFAULT 0,
  total_points INTEGER DEFAULT 0,
  percentage DECIMAL DEFAULT 0,
  is_completed BOOLEAN DEFAULT FALSE,
  is_passed BOOLEAN DEFAULT FALSE,
  time_taken_minutes INTEGER DEFAULT 0,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Вставка тестовых данных
INSERT INTO admin_users (username, email, full_name, role) VALUES 
('admin', 'admin@uroki-islama.ru', 'Администратор', 'super_admin');

INSERT INTO team_members (name, subject, image_url, "order") VALUES 
('Али Евтеев', 'Этика', 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face', 1),
('Абдуль-Басит Микушкин', 'Основы веры', 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face', 2),
('Алексей Котенев', 'Практика веры', 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face', 3),
('Микаиль Ганиев', 'История', 'https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=400&h=400&fit=crop&crop=face', 4);
```

### 6. Запуск приложения

```bash
# Terminal 1 - Backend
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend  
cd frontend
yarn start
```

Приложение будет доступно по адресу: `http://localhost:3000`

## 🔐 Доступ к админке

**Данные для входа:**
- Email: `admin@uroki-islama.ru`
- Пароль: `admin123`

## 📋 API Документация

API документация доступна по адресу: `http://localhost:8001/docs`

### Основные endpoints:

- `GET /api/courses` - Получить опубликованные курсы
- `GET /api/courses/{course_id}/lessons` - Получить уроки курса
- `GET /api/lessons/{lesson_id}` - Получить урок
- `GET /api/team` - Получить команду преподавателей
- `GET /api/qa/questions` - Получить Q&A вопросы
- `POST /api/admin/login` - Авторизация администратора

## 🎯 Структура проекта

```
uroki-islama/
├── backend/                 # FastAPI backend
│   ├── server.py           # Основное приложение
│   ├── models.py           # Pydantic модели
│   ├── supabase_client.py  # Клиент Supabase
│   ├── requirements.txt    # Python зависимости
│   └── .env               # Переменные окружения
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.js         # Главный компонент
│   │   ├── components/    # Компоненты UI
│   │   └── ...
│   ├── package.json       # Node.js зависимости
│   └── .env              # Переменные окружения
└── README.md             # Эта документация
```

## 🛡️ Безопасность

- JWT токены для аутентификации
- Проверка ролей и разрешений
- Валидация всех входных данных
- CORS защита
- Хеширование паролей с bcrypt

## 🌍 Деплой

### Развертывание на Vercel (Frontend)

```bash
# Установка Vercel CLI
npm i -g vercel

# Деплой из папки frontend
cd frontend
vercel

# Настройте переменные окружения в Vercel dashboard:
# REACT_APP_BACKEND_URL=https://your-backend-url.com
```

### Развертывание на Railway/Heroku (Backend)

```bash
# Создайте Procfile в корне backend:
web: uvicorn server:app --host 0.0.0.0 --port $PORT

# Настройте переменные окружения:
# SUPABASE_URL=your-supabase-url
# SUPABASE_ANON_KEY=your-supabase-key
# SECRET_KEY=your-secret-key
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензируется под MIT License - смотрите файл [LICENSE](LICENSE) для деталей.

## 📞 Поддержка

Если у вас есть вопросы или проблемы:

- 📧 Email: info@uroki-islama.ru
- 🐛 Создайте Issue в GitHub
- 💬 Обратитесь к документации API

## 🙏 Благодарности

- Команде Supabase за отличную платформу баз данных
- Сообществу React и FastAPI за инструменты разработки
- Всем, кто участвует в развитии исламского образования

---

**Сделано с ❤️ для мусульманской уммы**
