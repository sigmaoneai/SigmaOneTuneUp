#!/usr/bin/env python3
"""
Add onboarding fields to agents table
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

# Database configuration
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

async def add_onboarding_fields_to_agents():
    """Add onboarding-specific fields to the agents table"""
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            print("Adding onboarding fields to agents table...")
            
            # PostgreSQL syntax (both dev and prod use PostgreSQL now)
            await session.execute(text("""
                ALTER TABLE agents 
                ADD COLUMN IF NOT EXISTS type VARCHAR,
                ADD COLUMN IF NOT EXISTS is_default BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS prompt TEXT,
                ADD COLUMN IF NOT EXISTS focus_areas JSON
            """))
            
            await session.commit()
            print("Successfully added onboarding fields to agents table!")
            
        except Exception as e:
            print(f"Error adding onboarding fields: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_onboarding_fields_to_agents()) 