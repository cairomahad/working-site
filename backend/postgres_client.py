import os
import asyncpg
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class PostgreSQLClient:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL must be set in environment variables")
        
        self.pool = None
        logger.info("PostgreSQL client initialized")

    async def init_pool(self):
        """Initialize connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("PostgreSQL connection pool created")

    async def close_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("PostgreSQL connection pool closed")

    async def create_record(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in the specified table"""
        await self.init_pool()
        
        try:
            # Process data for insertion
            processed_data = self._process_data_for_insert(data)
            
            # Generate column names and placeholders
            columns = list(processed_data.keys())
            placeholders = [f"${i+1}" for i in range(len(columns))]
            values = [processed_data[col] for col in columns]
            
            query = f"""
                INSERT INTO {table} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                RETURNING *
            """
            
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, *values)
                return dict(row) if row else {}
                
        except Exception as e:
            logger.error(f"Error creating record in {table}: {str(e)}")
            raise

    async def get_record(self, table: str, id_field: str, id_value: str) -> Optional[Dict[str, Any]]:
        """Get a single record by ID"""
        await self.init_pool()
        
        try:
            query = f"SELECT * FROM {table} WHERE {id_field} = $1"
            
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, id_value)
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Error getting record from {table}: {str(e)}")
            raise

    async def get_records(self, table: str, filters: Optional[Dict[str, Any]] = None, 
                         order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get multiple records with optional filters"""
        await self.init_pool()
        
        try:
            query = f"SELECT * FROM {table}"
            params = []
            
            # Add WHERE clause
            if filters:
                where_conditions = []
                param_count = 1
                
                for field, value in filters.items():
                    if isinstance(value, dict):
                        # Handle complex filters
                        for operator, op_value in value.items():
                            if operator == "$in":
                                placeholders = [f"${param_count + i}" for i in range(len(op_value))]
                                where_conditions.append(f"{field} = ANY(ARRAY[{', '.join(placeholders)}])")
                                params.extend(op_value)
                                param_count += len(op_value)
                            elif operator == "$gte":
                                where_conditions.append(f"{field} >= ${param_count}")
                                params.append(op_value)
                                param_count += 1
                            elif operator == "$lte":
                                where_conditions.append(f"{field} <= ${param_count}")
                                params.append(op_value)
                                param_count += 1
                            elif operator == "$regex":
                                where_conditions.append(f"{field} ILIKE ${param_count}")
                                params.append(f"%{op_value}%")
                                param_count += 1
                    else:
                        where_conditions.append(f"{field} = ${param_count}")
                        params.append(value)
                        param_count += 1
                
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
            
            # Add ORDER BY clause
            if order_by:
                if order_by.startswith("-"):
                    query += f" ORDER BY {order_by[1:]} DESC"
                else:
                    query += f" ORDER BY {order_by} ASC"
            
            # Add LIMIT clause
            if limit:
                query += f" LIMIT {limit}"
            
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting records from {table}: {str(e)}")
            raise

    async def update_record(self, table: str, id_field: str, id_value: str, 
                          data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record by ID"""
        await self.init_pool()
        
        try:
            processed_data = self._process_data_for_update(data)
            
            if not processed_data:
                return None
            
            # Generate SET clause
            set_clauses = []
            values = []
            param_count = 1
            
            for field, value in processed_data.items():
                set_clauses.append(f"{field} = ${param_count}")
                values.append(value)
                param_count += 1
            
            values.append(id_value)  # For WHERE clause
            
            query = f"""
                UPDATE {table}
                SET {', '.join(set_clauses)}
                WHERE {id_field} = ${param_count}
                RETURNING *
            """
            
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, *values)
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Error updating record in {table}: {str(e)}")
            raise

    async def delete_record(self, table: str, id_field: str, id_value: str) -> bool:
        """Delete a record by ID"""
        await self.init_pool()
        
        try:
            query = f"DELETE FROM {table} WHERE {id_field} = $1"
            
            async with self.pool.acquire() as conn:
                result = await conn.execute(query, id_value)
                return result == "DELETE 1"
                
        except Exception as e:
            logger.error(f"Error deleting record from {table}: {str(e)}")
            raise

    async def count_records(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records in a table with optional filters"""
        await self.init_pool()
        
        try:
            query = f"SELECT COUNT(*) FROM {table}"
            params = []
            
            if filters:
                where_conditions = []
                param_count = 1
                
                for field, value in filters.items():
                    if isinstance(value, dict):
                        for operator, op_value in value.items():
                            if operator == "$in":
                                placeholders = [f"${param_count + i}" for i in range(len(op_value))]
                                where_conditions.append(f"{field} = ANY(ARRAY[{', '.join(placeholders)}])")
                                params.extend(op_value)
                                param_count += len(op_value)
                            elif operator == "$gte":
                                where_conditions.append(f"{field} >= ${param_count}")
                                params.append(op_value)
                                param_count += 1
                            elif operator == "$lte":
                                where_conditions.append(f"{field} <= ${param_count}")
                                params.append(op_value)
                                param_count += 1
                    else:
                        where_conditions.append(f"{field} = ${param_count}")
                        params.append(value)
                        param_count += 1
                
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
            
            async with self.pool.acquire() as conn:
                count = await conn.fetchval(query, *params)
                return count or 0
                
        except Exception as e:
            logger.error(f"Error counting records in {table}: {str(e)}")
            raise

    async def find_one(self, table: str, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single record with filters"""
        records = await self.get_records(table, filters, limit=1)
        return records[0] if records else None

    async def execute_raw_sql(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Execute raw SQL query"""
        await self.init_pool()
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *(params or []))
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error executing raw SQL: {str(e)}")
            raise

    def _process_data_for_insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data before inserting to PostgreSQL"""
        processed = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                processed[key] = value.isoformat()
            elif isinstance(value, (list, dict)):
                processed[key] = json.dumps(value)
            elif hasattr(value, 'dict'):  # Pydantic model
                processed[key] = json.dumps(value.dict())
            else:
                processed[key] = value
        return processed

    def _process_data_for_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data before updating in PostgreSQL"""
        processed = {}
        for key, value in data.items():
            if value is not None:  # Skip None values
                if isinstance(value, datetime):
                    processed[key] = value.isoformat()
                elif isinstance(value, (list, dict)):
                    processed[key] = json.dumps(value)
                elif hasattr(value, 'dict'):  # Pydantic model
                    processed[key] = json.dumps(value.dict())
                else:
                    processed[key] = value
        return processed

# Global instance
postgres_client = PostgreSQLClient()