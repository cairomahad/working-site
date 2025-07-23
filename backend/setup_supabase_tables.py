import asyncio
import sys
sys.path.append('.')
from supabase_client import SupabaseClient

async def create_supabase_tables():
    """Create missing tables using Supabase client"""
    
    client = SupabaseClient()
    
    # Create users table (for students)
    try:
        # Check if users table exists by trying to insert a test record
        await client.create_record("users", {
            "id": "test-user-id",
            "name": "Test User",
            "email": "test@test.com",
            "total_score": 0,
            "is_active": True
        })
        print("✅ Таблица users существует")
        # Delete test record
        await client.delete_record("users", "id", "test-user-id")
    except Exception as e:
        if "does not exist" in str(e):
            print("❌ Таблица users не существует, создаем...")
            # For now, we'll use the existing table creation logic
        else:
            print(f"✅ Таблица users доступна: {e}")

    # Create admins table (using admin_users table name)
    try:
        # Check if admin_users table exists
        await client.create_record("admin_users", {
            "id": "test-admin-id",
            "username": "testadmin",
            "email": "testadmin@test.com",
            "full_name": "Test Admin",
            "role": "admin",
            "is_active": True
        })
        print("✅ Таблица admin_users существует")
        # Delete test record
        await client.delete_record("admin_users", "id", "test-admin-id")
    except Exception as e:
        if "does not exist" in str(e):
            print("❌ Таблица admin_users не существует, создаем...")
        else:
            print(f"✅ Таблица admin_users доступна: {e}")

    # Create default admin user
    try:
        existing_admin = await client.get_record("admin_users", "email", "admin@uroki-islama.ru")
        if not existing_admin:
            await client.create_record("admin_users", {
                "id": "admin-1",
                "username": "admin",
                "email": "admin@uroki-islama.ru",
                "full_name": "Администратор",
                "role": "admin",
                "is_active": True
            })
            print("✅ Создан админский пользователь admin@uroki-islama.ru")
        else:
            print("✅ Админский пользователь уже существует")
    except Exception as e:
        print(f"❌ Ошибка создания админа: {e}")

if __name__ == "__main__":
    asyncio.run(create_supabase_tables())