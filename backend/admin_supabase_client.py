"""
Admin Supabase Client with Service Role privileges
Provides universal table management capabilities
"""

import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment variables
load_dotenv()

class AdminSupabaseClient:
    """
    Admin Supabase client with service role privileges for universal table management
    """
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.supabase_url or not self.service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        # Create client with service role key for admin privileges
        self.client: Client = create_client(self.supabase_url, self.service_role_key)
        print("✅ Admin Supabase Client initialized with service role privileges")
    
    async def get_all_tables(self) -> List[Dict[str, Any]]:
        """Get list of all tables in the database"""
        try:
            # Query information_schema to get table information
            result = self.client.rpc('get_all_tables').execute()
            
            if result.data:
                return result.data
            
            # Fallback: try to get tables from pg_tables
            result = self.client.rpc('get_tables_info').execute()
            
            if result.data:
                return result.data
            
            # If RPC functions don't exist, return known tables
            return [
                {"table_name": "courses", "table_schema": "public"},
                {"table_name": "lessons", "table_schema": "public"},
                {"table_name": "tests", "table_schema": "public"},
                {"table_name": "questions", "table_schema": "public"},
                {"table_name": "admin_users", "table_schema": "public"},
                {"table_name": "team_members", "table_schema": "public"},
                {"table_name": "qa_questions", "table_schema": "public"},
                {"table_name": "qa_categories", "table_schema": "public"},
                {"table_name": "users", "table_schema": "public"},
                {"table_name": "test_sessions", "table_schema": "public"},
                {"table_name": "test_results", "table_schema": "public"},
                {"table_name": "promocodes", "table_schema": "public"},
                {"table_name": "user_course_access", "table_schema": "public"}
            ]
            
        except Exception as e:
            print(f"❌ Error getting tables: {e}")
            # Return known tables as fallback
            return [
                {"table_name": "courses", "table_schema": "public"},
                {"table_name": "lessons", "table_schema": "public"},
                {"table_name": "tests", "table_schema": "public"},
                {"table_name": "questions", "table_schema": "public"},
                {"table_name": "admin_users", "table_schema": "public"},
                {"table_name": "team_members", "table_schema": "public"},
                {"table_name": "qa_questions", "table_schema": "public"},
                {"table_name": "qa_categories", "table_schema": "public"},
                {"table_name": "users", "table_schema": "public"},
                {"table_name": "test_sessions", "table_schema": "public"},
                {"table_name": "test_results", "table_schema": "public"},
                {"table_name": "promocodes", "table_schema": "public"},
                {"table_name": "user_course_access", "table_schema": "public"}
            ]
    
    async def get_table_structure(self, table_name: str) -> Dict[str, Any]:
        """Get table structure (columns, types, constraints)"""
        try:
            # Try to get some sample data to infer structure
            sample_result = self.client.table(table_name).select("*").limit(1).execute()
            
            if sample_result.data:
                sample_row = sample_result.data[0]
                columns = []
                for key, value in sample_row.items():
                    column_type = "text"
                    if isinstance(value, int):
                        column_type = "integer"
                    elif isinstance(value, float):
                        column_type = "numeric"
                    elif isinstance(value, bool):
                        column_type = "boolean"
                    elif isinstance(value, dict) or isinstance(value, list):
                        column_type = "json"
                    
                    columns.append({
                        "column_name": key,
                        "data_type": column_type,
                        "is_nullable": "YES"
                    })
                
                return columns
            
            # If no data, return basic structure based on known table schemas
            if table_name == "courses":
                return [
                    {"column_name": "id", "data_type": "uuid", "is_nullable": "NO"},
                    {"column_name": "title", "data_type": "text", "is_nullable": "NO"},
                    {"column_name": "description", "data_type": "text", "is_nullable": "YES"},
                    {"column_name": "level", "data_type": "text", "is_nullable": "YES"},
                    {"column_name": "status", "data_type": "text", "is_nullable": "YES"},
                    {"column_name": "created_at", "data_type": "timestamp", "is_nullable": "YES"},
                    {"column_name": "updated_at", "data_type": "timestamp", "is_nullable": "YES"}
                ]
            elif table_name == "lessons":
                return [
                    {"column_name": "id", "data_type": "uuid", "is_nullable": "NO"},
                    {"column_name": "course_id", "data_type": "uuid", "is_nullable": "NO"},
                    {"column_name": "title", "data_type": "text", "is_nullable": "NO"},
                    {"column_name": "description", "data_type": "text", "is_nullable": "YES"},
                    {"column_name": "content", "data_type": "text", "is_nullable": "YES"},
                    {"column_name": "lesson_type", "data_type": "text", "is_nullable": "YES"},
                    {"column_name": "video_url", "data_type": "text", "is_nullable": "YES"},
                    {"column_name": "created_at", "data_type": "timestamp", "is_nullable": "YES"},
                    {"column_name": "updated_at", "data_type": "timestamp", "is_nullable": "YES"}
                ]
            else:
                return [
                    {"column_name": "id", "data_type": "uuid", "is_nullable": "NO"},
                    {"column_name": "created_at", "data_type": "timestamp", "is_nullable": "YES"},
                    {"column_name": "updated_at", "data_type": "timestamp", "is_nullable": "YES"}
                ]
            
        except Exception as e:
            print(f"❌ Error getting table structure for {table_name}: {e}")
            # Return basic structure as fallback
            return [
                {"column_name": "id", "data_type": "uuid", "is_nullable": "NO"},
                {"column_name": "created_at", "data_type": "timestamp", "is_nullable": "YES"},
                {"column_name": "updated_at", "data_type": "timestamp", "is_nullable": "YES"}
            ]
    
    async def get_table_data(self, table_name: str, page: int = 1, limit: int = 50, 
                           filters: Optional[Dict[str, Any]] = None, 
                           search: Optional[str] = None) -> Dict[str, Any]:
        """Get table data with pagination and filtering"""
        try:
            query = self.client.table(table_name).select("*")
            
            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if value is not None and value != "":
                        query = query.eq(key, value)
            
            # Apply search if provided (search in all text fields)
            if search:
                # This is a simplified search - in production you'd want to search specific columns
                query = query.ilike("*", f"%{search}%")
            
            # Count total records
            count_result = self.client.table(table_name).select("*", count="exact").execute()
            total_count = count_result.count if count_result.count else 0
            
            # Apply pagination
            offset = (page - 1) * limit
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            
            return {
                "data": result.data or [],
                "total_count": total_count,
                "page": page,
                "limit": limit,
                "total_pages": (total_count + limit - 1) // limit
            }
            
        except Exception as e:
            print(f"❌ Error getting table data for {table_name}: {e}")
            return {
                "data": [],
                "total_count": 0,
                "page": page,
                "limit": limit,
                "total_pages": 0,
                "error": str(e)
            }
    
    async def create_record(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in the specified table"""
        try:
            result = self.client.table(table_name).insert(data).execute()
            
            if result.data:
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "Record created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create record",
                    "data": None
                }
                
        except Exception as e:
            print(f"❌ Error creating record in {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def update_record(self, table_name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record in the specified table"""
        try:
            result = self.client.table(table_name).update(data).eq("id", record_id).execute()
            
            if result.data:
                return {
                    "success": True,
                    "data": result.data[0],
                    "message": "Record updated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update record",
                    "data": None
                }
                
        except Exception as e:
            print(f"❌ Error updating record in {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def delete_record(self, table_name: str, record_id: str) -> Dict[str, Any]:
        """Delete a record from the specified table"""
        try:
            result = self.client.table(table_name).delete().eq("id", record_id).execute()
            
            return {
                "success": True,
                "message": "Record deleted successfully",
                "deleted_id": record_id
            }
                
        except Exception as e:
            print(f"❌ Error deleting record from {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "deleted_id": None
            }
    
    async def execute_custom_query(self, query: str) -> Dict[str, Any]:
        """Execute a custom SQL query (use with caution)"""
        try:
            result = self.client.rpc('execute_sql', {"sql_query": query}).execute()
            
            return {
                "success": True,
                "data": result.data,
                "message": "Query executed successfully"
            }
                
        except Exception as e:
            print(f"❌ Error executing custom query: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

# Global instance
admin_supabase_client = AdminSupabaseClient()