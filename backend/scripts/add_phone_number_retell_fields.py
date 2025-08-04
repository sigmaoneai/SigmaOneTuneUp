#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.database import engine
from sqlalchemy import text

async def add_retell_fields_to_phone_numbers():
    """Add RetellAI integration fields to phone_numbers table"""
    
    async with engine.begin() as conn:
        print("Adding RetellAI integration fields to phone_numbers table...")
        
        # Add RetellAI fields
        await conn.execute(text("""
            ALTER TABLE phone_numbers 
            ADD COLUMN IF NOT EXISTS retell_phone_number_id VARCHAR UNIQUE,
            ADD COLUMN IF NOT EXISTS area_code VARCHAR,
            ADD COLUMN IF NOT EXISTS inbound_agent_id VARCHAR,
            ADD COLUMN IF NOT EXISTS outbound_agent_id VARCHAR,
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
        """))
        print("✓ Added RetellAI integration fields to phone_numbers table")
        
        # Update existing phone numbers to be active by default
        await conn.execute(text("""
            UPDATE phone_numbers 
            SET is_active = TRUE 
            WHERE is_active IS NULL;
        """))
        print("✓ Updated existing phone numbers to be active")
        
    print("✅ Phone numbers table updated successfully for RetellAI integration!")

if __name__ == "__main__":
    asyncio.run(add_retell_fields_to_phone_numbers()) 