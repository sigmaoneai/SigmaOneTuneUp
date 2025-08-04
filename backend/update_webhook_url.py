#!/usr/bin/env python3
"""
Update RetellAI webhook URLs when ngrok URL changes
Usage: python update_webhook_url.py <new_ngrok_url>
"""

import os
import sys
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def update_webhook_urls(new_base_url: str):
    """Update all RetellAI agents with new webhook URL"""
    api_key = os.getenv("RETELLAI_API_KEY")
    if not api_key:
        print("❌ RETELLAI_API_KEY not found in environment")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    webhook_url = f"{new_base_url}/api/v1/retellai/agent-level-webhook"
    
    async with httpx.AsyncClient() as client:
        try:
            # Get all agents
            response = await client.get(
                "https://api.retellai.com/list-agents",
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to list agents: {response.text}")
                return
                
            agents = response.json()
            print(f"📍 Found {len(agents)} agents to update")
            
            # Update each agent
            for agent in agents:
                agent_id = agent["agent_id"]
                agent_name = agent.get("agent_name", "Unknown")
                
                update_data = {"webhook_url": webhook_url}
                
                update_response = await client.patch(
                    f"https://api.retellai.com/update-agent/{agent_id}",
                    headers=headers,
                    json=update_data
                )
                
                if update_response.status_code == 200:
                    print(f"✅ Updated agent '{agent_name}' ({agent_id})")
                else:
                    print(f"❌ Failed to update agent '{agent_name}': {update_response.text}")
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n🎯 New webhook URL: {webhook_url}")
    print("💡 Don't forget to update your .env file:")
    print(f"RETELLAI_AGENT_WEBHOOK_URL={webhook_url}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_webhook_url.py <new_ngrok_url>")
        print("Example: python update_webhook_url.py https://abc123.ngrok.io")
        sys.exit(1)
    
    new_url = sys.argv[1].rstrip('/')
    asyncio.run(update_webhook_urls(new_url)) 