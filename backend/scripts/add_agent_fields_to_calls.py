#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.database import engine
from sqlalchemy import text

async def add_agent_fields_to_calls():
    """Add missing agent fields to calls table for agent-to-agent calling"""
    
    async with engine.begin() as conn:
        print("Adding missing agent fields to calls table...")
        
        # Add agent-related fields
        await conn.execute(text("""
            ALTER TABLE calls 
            ADD COLUMN IF NOT EXISTS caller_agent_id UUID,
            ADD COLUMN IF NOT EXISTS inbound_agent_id UUID;
        """))
        print("✓ Added caller_agent_id and inbound_agent_id to calls table")
        
        # Add foreign key constraints
        try:
            await conn.execute(text("""
                ALTER TABLE calls 
                ADD CONSTRAINT IF NOT EXISTS fk_calls_caller_agent_id 
                FOREIGN KEY (caller_agent_id) REFERENCES retell_agents(id);
            """))
            print("✓ Added foreign key constraint for caller_agent_id")
        except Exception as e:
            print(f"  - Foreign key constraint for caller_agent_id already exists or retell_agents table not found: {e}")
        
        try:
            await conn.execute(text("""
                ALTER TABLE calls 
                ADD CONSTRAINT IF NOT EXISTS fk_calls_inbound_agent_id 
                FOREIGN KEY (inbound_agent_id) REFERENCES retell_agents(id);
            """))
            print("✓ Added foreign key constraint for inbound_agent_id")
        except Exception as e:
            print(f"  - Foreign key constraint for inbound_agent_id already exists or retell_agents table not found: {e}")
        
    print("✅ Calls table updated successfully for agent-to-agent calling!")

if __name__ == "__main__":
    asyncio.run(add_agent_fields_to_calls()) 