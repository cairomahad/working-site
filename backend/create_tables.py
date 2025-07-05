import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

def create_tables():
    """Create all necessary tables for the application"""
    
    # Connect using psycopg2
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    
    try:
        # Create tables with proper schema
        
        # Admin users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                last_login TIMESTAMPTZ
            )
        """)
        
        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                total_score INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                last_activity TIMESTAMPTZ,
                completed_courses JSONB DEFAULT '[]'::jsonb,
                current_level TEXT DEFAULT 'level_1'
            )
        """)
        
        # Teachers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                subject TEXT NOT NULL,
                bio TEXT,
                image_url TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                courses_count INTEGER DEFAULT 0,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        
        # Courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                slug TEXT UNIQUE,
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
                prerequisites JSONB DEFAULT '[]'::jsonb,
                additional_materials TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        
        # Lessons table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id TEXT PRIMARY KEY,
                course_id TEXT NOT NULL,
                title TEXT NOT NULL,
                slug TEXT,
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
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        """)
        
        # Tests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tests (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                course_id TEXT NOT NULL,
                lesson_id TEXT,
                time_limit_minutes INTEGER,
                passing_score INTEGER DEFAULT 70,
                max_attempts INTEGER DEFAULT 3,
                is_published BOOLEAN DEFAULT TRUE,
                "order" INTEGER DEFAULT 1,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
            )
        """)
        
        # Questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                test_id TEXT NOT NULL,
                text TEXT NOT NULL,
                question_type TEXT NOT NULL,
                options JSONB DEFAULT '[]'::jsonb,
                correct_answer TEXT,
                explanation TEXT,
                points INTEGER DEFAULT 1,
                "order" INTEGER NOT NULL,
                FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
            )
        """)
        
        # Test sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_sessions (
                id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                test_id TEXT NOT NULL,
                course_id TEXT NOT NULL,
                lesson_id TEXT,
                selected_questions JSONB DEFAULT '[]'::jsonb,
                shuffled_options JSONB DEFAULT '{}'::jsonb,
                answers JSONB DEFAULT '{}'::jsonb,
                score INTEGER DEFAULT 0,
                total_points INTEGER DEFAULT 0,
                percentage NUMERIC(5,2) DEFAULT 0.0,
                is_completed BOOLEAN DEFAULT FALSE,
                is_passed BOOLEAN DEFAULT FALSE,
                time_taken_minutes INTEGER DEFAULT 0,
                started_at TIMESTAMPTZ DEFAULT NOW(),
                completed_at TIMESTAMPTZ,
                FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        """)
        
        # Team members table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                id TEXT PRIMARY KEY,
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
            )
        """)
        
        # Q&A Questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qa_questions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                question_text TEXT NOT NULL,
                answer_text TEXT NOT NULL,
                category TEXT NOT NULL,
                tags JSONB DEFAULT '[]'::jsonb,
                slug TEXT UNIQUE,
                is_featured BOOLEAN DEFAULT FALSE,
                views_count INTEGER DEFAULT 0,
                likes_count INTEGER DEFAULT 0,
                imam_name TEXT DEFAULT 'Имам',
                references JSONB DEFAULT '[]'::jsonb,
                related_questions JSONB DEFAULT '[]'::jsonb,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        
        # Applications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id TEXT PRIMARY KEY,
                student_name TEXT NOT NULL,
                student_email TEXT NOT NULL,
                course_id TEXT NOT NULL,
                course_title TEXT NOT NULL,
                message TEXT,
                status TEXT DEFAULT 'pending',
                admin_comment TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        
        # Test attempts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_attempts (
                id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                test_id TEXT NOT NULL,
                course_id TEXT NOT NULL,
                lesson_id TEXT,
                answers JSONB DEFAULT '{}'::jsonb,
                score INTEGER DEFAULT 0,
                total_points INTEGER DEFAULT 0,
                percentage NUMERIC(5,2) DEFAULT 0.0,
                is_passed BOOLEAN DEFAULT FALSE,
                time_taken_minutes INTEGER DEFAULT 0,
                attempt_number INTEGER DEFAULT 1,
                started_at TIMESTAMPTZ DEFAULT NOW(),
                completed_at TIMESTAMPTZ
            )
        """)
        
        # Status checks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS status_checks (
                id TEXT PRIMARY KEY,
                client_name TEXT NOT NULL,
                timestamp TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        
        # Commit the changes
        conn.commit()
        print("✅ All tables created successfully!")
        
        # Insert default admin user
        cursor.execute("""
            INSERT INTO admin_users (id, username, email, full_name, role)
            VALUES ('admin-1', 'admin', 'admin@uroki-islama.ru', 'Администратор', 'admin')
            ON CONFLICT (username) DO NOTHING
        """)
        
        # Commit the changes
        conn.commit()
        print("✅ Default admin user created!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()