#!/usr/bin/env python3
"""
Test script to verify SigmaOne TuneUp backend setup
"""

import asyncio
import httpx
import sys
from dotenv import load_dotenv
import os

load_dotenv()

async def test_backend():
    """Test the backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing SigmaOne TuneUp Backend...")
    print(f"🔗 Base URL: {base_url}")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test health endpoint
            print("\n1️⃣ Testing health endpoint...")
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
            
            # Test dashboard health check
            print("\n2️⃣ Testing system health check...")
            response = await client.get(f"{base_url}/api/v1/dashboard/health-check")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ System health check working")
                print(f"   📊 Overall status: {health_data.get('overall')}")
                print(f"   🗄️ Database: {health_data.get('database')}")
                print(f"   📞 RetellAI: {health_data.get('retell_ai')}")
                print(f"   🎫 SyncroMSP: {health_data.get('syncro_msp')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
            
            # Test agents list
            print("\n3️⃣ Testing agents endpoint...")
            response = await client.get(f"{base_url}/api/v1/agents")
            if response.status_code == 200:
                agents = response.json()
                print(f"✅ Agents endpoint working (found {len(agents)} agents)")
            else:
                print(f"❌ Agents endpoint failed: {response.status_code}")
            
            # Test phone numbers sync
            print("\n4️⃣ Testing phone numbers sync...")
            response = await client.get(f"{base_url}/api/v1/phone-numbers/sync-from-retell")
            if response.status_code == 200:
                sync_result = response.json()
                print(f"✅ Phone sync working")
                print(f"   📱 New: {sync_result.get('new_count', 0)}")
                print(f"   🔄 Updated: {sync_result.get('updated_count', 0)}")
                print(f"   📊 Total RetellAI numbers: {sync_result.get('total_retell_numbers', 0)}")
            else:
                print(f"❌ Phone sync failed: {response.status_code}")
            
            # Test dashboard stats
            print("\n5️⃣ Testing dashboard stats...")
            response = await client.get(f"{base_url}/api/v1/dashboard/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Dashboard stats working")
                print(f"   👥 Total agents: {stats.get('total_agents', 0)}")
                print(f"   📱 Phone numbers: {stats.get('total_phone_numbers', 0)}")
                print(f"   📞 Calls today: {stats.get('total_calls_today', 0)}")
            else:
                print(f"❌ Dashboard stats failed: {response.status_code}")
            
            # Test SyncroMSP
            print("\n6️⃣ Testing SyncroMSP integration...")
            response = await client.get(f"{base_url}/api/v1/syncro/customers?limit=1")
            if response.status_code == 200:
                customers = response.json()
                print(f"✅ SyncroMSP integration working")
                print(f"   👤 Customer count: {customers.get('count', 0)}")
            else:
                print(f"❌ SyncroMSP integration failed: {response.status_code}")
            
            print("\n🎉 Backend test completed!")
            print(f"\n📖 Access API documentation at: {base_url}/docs")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            print("\nMake sure the server is running: python run.py")
            sys.exit(1)

if __name__ == "__main__":
    print("Starting backend tests...")
    print("Make sure your .env file is configured and the server is running!")
    asyncio.run(test_backend()) 