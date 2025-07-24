#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.database import engine
from sqlalchemy import text

async def check_database_schema():
    async with engine.begin() as conn:
        print("=== PHONE_CALLS TABLE ===")
        try:
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'phone_calls'
                ORDER BY ordinal_position;
            """))
            rows = result.fetchall()
            if rows:
                for row in rows:
                    print(f"{row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
            else:
                print("No phone_calls table found")
        except Exception as e:
            print(f"Error checking phone_calls: {e}")
        
        print("\n=== CALLS TABLE ===")
        try:
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'calls'
                ORDER BY ordinal_position;
            """))
            rows = result.fetchall()
            if rows:
                for row in rows:
                    print(f"{row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
            else:
                print("No calls table found")
        except Exception as e:
            print(f"Error checking calls: {e}")
        
        print("\n=== ALL TABLES ===")
        try:
            result = await conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            rows = result.fetchall()
            for row in rows:
                print(f"- {row[0]}")
        except Exception as e:
            print(f"Error listing tables: {e}")

if __name__ == "__main__":
    asyncio.run(check_database_schema()) 