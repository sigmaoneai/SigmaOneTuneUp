#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.database import engine
from sqlalchemy import text

async def add_agent_fields_to_phone_calls():
    """Add agent-related fields to phone_calls table to support agent-to-agent calling"""
    
    async with engine.begin() as conn:
        print("Adding agent-related fields to phone_calls table...")
        
        # Add agent-related fields
        await conn.execute(text("""
            ALTER TABLE phone_calls 
            ADD COLUMN IF NOT EXISTS agent_id UUID,
            ADD COLUMN IF NOT EXISTS caller_agent_id UUID,
            ADD COLUMN IF NOT EXISTS inbound_agent_id UUID,
            ADD COLUMN IF NOT EXISTS phone_number_id UUID,
            ADD COLUMN IF NOT EXISTS retell_call_id VARCHAR UNIQUE,
            ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'completed',
            ADD COLUMN IF NOT EXISTS start_timestamp TIMESTAMP,
            ADD COLUMN IF NOT EXISTS end_timestamp TIMESTAMP,
            ADD COLUMN IF NOT EXISTS duration_ms VARCHAR,
            ADD COLUMN IF NOT EXISTS call_analysis JSON,
            ADD COLUMN IF NOT EXISTS call_metadata JSON;
        """))
        print("✓ Added agent-related fields to phone_calls table")
        
        # Add foreign key constraints (without IF NOT EXISTS as PostgreSQL doesn't support it)
        constraints = [
            ("fk_phone_calls_agent_id", "agent_id", "agents(id)"),
            ("fk_phone_calls_caller_agent_id", "caller_agent_id", "agents(id)"),
            ("fk_phone_calls_inbound_agent_id", "inbound_agent_id", "agents(id)"),
            ("fk_phone_calls_phone_number_id", "phone_number_id", "phone_numbers(id)")
        ]
        
        for constraint_name, column, reference in constraints:
            try:
                await conn.execute(text(f"""
                    ALTER TABLE phone_calls 
                    ADD CONSTRAINT {constraint_name} 
                    FOREIGN KEY ({column}) REFERENCES {reference};
                """))
                print(f"✓ Added constraint {constraint_name}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"✓ Constraint {constraint_name} already exists")
                else:
                    print(f"⚠ Warning: Could not add constraint {constraint_name}: {e}")
        
        # Create phone_call_events table to replace call_events
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS phone_call_events (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                phone_call_id VARCHAR NOT NULL,
                event_type VARCHAR NOT NULL,
                event_data JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (phone_call_id) REFERENCES phone_calls(id)
            );
        """))
        print("✓ Created phone_call_events table")
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_phone_calls_agent_id ON phone_calls(agent_id);",
            "CREATE INDEX IF NOT EXISTS idx_phone_calls_caller_agent_id ON phone_calls(caller_agent_id);",
            "CREATE INDEX IF NOT EXISTS idx_phone_calls_inbound_agent_id ON phone_calls(inbound_agent_id);",
            "CREATE INDEX IF NOT EXISTS idx_phone_calls_retell_call_id ON phone_calls(retell_call_id);",
            "CREATE INDEX IF NOT EXISTS idx_phone_calls_status ON phone_calls(status);",
            "CREATE INDEX IF NOT EXISTS idx_phone_calls_created_at ON phone_calls(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_phone_call_events_phone_call_id ON phone_call_events(phone_call_id);",
            "CREATE INDEX IF NOT EXISTS idx_phone_call_events_event_type ON phone_call_events(event_type);"
        ]
        
        for index_sql in indexes:
            try:
                await conn.execute(text(index_sql))
            except Exception as e:
                print(f"⚠ Warning: Could not create index: {e}")
        
        print("✓ Created indexes")
        
        print("\n✅ Successfully added agent fields to phone_calls table!")
        print("The phone_calls table now supports:")
        print("- Agent relationships (agent_id, caller_agent_id, inbound_agent_id)")
        print("- RetellAI integration (retell_call_id)")
        print("- Call status tracking")
        print("- Extended metadata (call_analysis, call_metadata)")
        print("- Call events via phone_call_events table")

if __name__ == "__main__":
    asyncio.run(add_agent_fields_to_phone_calls()) 