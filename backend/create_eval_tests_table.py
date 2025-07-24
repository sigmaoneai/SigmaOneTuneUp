"""
Migration script to create eval_tests table
Run this script to create the eval_tests table in your database
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

# Database configuration based on environment
environment = os.getenv("ENVIRONMENT", "dev")

if environment == "prod":
    db_host = os.getenv("POSTGRES_DB_HOST")
    db_port = os.getenv("POSTGRES_DB_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB_NAME")
    db_user = os.getenv("POSTGRES_DB_USER")
    db_password = os.getenv("POSTGRES_DB_PASSWORD")
else:
    db_host = os.getenv("POSTGRES_DB_HOST_DEV")
    db_port = os.getenv("POSTGRES_DB_PORT_DEV", "5432")
    db_name = os.getenv("POSTGRES_DB_NAME_DEV")
    db_user = os.getenv("POSTGRES_DB_USER_DEV")
    db_password = os.getenv("POSTGRES_DB_PASSWORD_DEV")

# Create database URL
DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

async def create_eval_tests_table():
    """Create the eval_tests table"""
    engine = create_async_engine(DATABASE_URL)
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS eval_tests (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        test_scenario_id VARCHAR NOT NULL,
        name VARCHAR NOT NULL,
        description TEXT,
        eval_criteria TEXT NOT NULL,
        expected_outcome TEXT NOT NULL,
        eval_type VARCHAR NOT NULL DEFAULT 'accuracy',
        weight INTEGER DEFAULT 1,
        status VARCHAR DEFAULT 'pending',
        score INTEGER,
        notes TEXT,
        last_evaluated TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        async with engine.begin() as conn:
            print("Creating eval_tests table...")
            await conn.execute(text(create_table_sql))
            print("✅ eval_tests table created successfully!")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_eval_tests_table()) 