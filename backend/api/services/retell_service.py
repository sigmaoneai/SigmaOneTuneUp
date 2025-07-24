import httpx
import os
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from loguru import logger
from datetime import datetime

class RetellAIService:
    def __init__(self):
        self.api_key = os.getenv("RETELLAI_API_KEY")
        self.base_url = "https://api.retellai.com"
        self.webhook_url = os.getenv("RETELLAI_AGENT_WEBHOOK_URL")
        self.agent_name_prefix = os.getenv("RETELLAI_AGENT_NAME_PREFIX", "SigmaOne - User <user_id> - Agent '<agent_name>'")
        
        if not self.api_key:
            raise ValueError("RETELLAI_API_KEY not found in environment variables")
            
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new RetellAI agent"""
        try:
            async with httpx.AsyncClient() as client:
                # Prepare agent configuration
                agent_config = {
                    "llm_websocket_url": agent_data.get("llm_websocket_url"),
                    "voice_id": agent_data.get("voice_id", "11labs-Adrian"),
                    "agent_name": agent_data.get("name"),
                    "ambient_sound": os.getenv("RETELLAI_AGENT_AMBIENT_SOUND", "call-center"),
                    "webhook_url": self.webhook_url,
                    "boosted_keywords": agent_data.get("boosted_keywords", []),
                    "enable_backchannel": True,
                    "backchannel_frequency": 0.9,
                    "backchannel_words": ["yeah", "uh-huh", "mm-hmm"],
                    "reminder_trigger_ms": 10000,
                    "reminder_max_count": 2,
                    "interruption_sensitivity": 1,
                    "responsiveness": 1,
                    "llm_type": os.getenv("RETELLAI_AGENT_LLM_TYPE", "retell-llm"),
                    "general_prompt": agent_data.get("prompt", ""),
                    "general_tools": agent_data.get("tools", []),
                    "inbound_dynamic_variables_webhook_url": os.getenv("RETELLAI_AGENT_INBOUND_DYNAMIC_VARIABLES_WEBHOOK_URL"),
                    "end_call_after_silence_ms": int(os.getenv("RETELLAI_AGENT_END_CALL_AFTER_SILENCE_MS", "30000")),
                }
                
                response = await client.post(
                    f"{self.base_url}/create-agent",
                    headers=self.headers,
                    json=agent_config
                )
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"Successfully created RetellAI agent: {result.get('agent_id')}")
                    return result
                else:
                    logger.error(f"Failed to create agent: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error creating RetellAI agent: {str(e)}")
            raise
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all RetellAI agents"""
        try:
            if not self.api_key:
                logger.warning("RetellAI API key not configured, returning mock data")
                return self._get_mock_agents()
                
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/list-agents",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to list agents: {response.status_code} - {response.text}")
                    logger.info("Falling back to mock data")
                    return self._get_mock_agents()
                    
        except Exception as e:
            logger.error(f"Error listing RetellAI agents: {str(e)}")
            logger.info("Falling back to mock data")
            return self._get_mock_agents()
    
    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get a specific RetellAI agent"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/get-agent/{agent_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get agent: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error getting RetellAI agent: {str(e)}")
            raise
    
    async def update_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a RetellAI agent"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/update-agent/{agent_id}",
                    headers=self.headers,
                    json=agent_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully updated RetellAI agent: {agent_id}")
                    return result
                else:
                    logger.error(f"Failed to update agent: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error updating RetellAI agent: {str(e)}")
            raise
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete a RetellAI agent"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/delete-agent/{agent_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully deleted RetellAI agent: {agent_id}")
                    return True
                else:
                    logger.error(f"Failed to delete agent: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error deleting RetellAI agent: {str(e)}")
            raise
    
    async def get_phone_numbers(self) -> List[Dict[str, Any]]:
        """List all phone numbers"""
        try:
            if not self.api_key:
                logger.warning("RetellAI API key not configured, returning mock data")
                return self._get_mock_phone_numbers()
                
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/list-phone-numbers",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to list phone numbers: {response.status_code} - {response.text}")
                    logger.info("Falling back to mock data")
                    return self._get_mock_phone_numbers()
                    
        except Exception as e:
            logger.error(f"Error listing phone numbers: {str(e)}")
            logger.info("Falling back to mock data")
            return self._get_mock_phone_numbers()
    
    async def get_phone_number(self, phone_number_id: str) -> Dict[str, Any]:
        """Get a specific phone number"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/get-phone-number/{phone_number_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get phone number: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error getting phone number: {str(e)}")
            raise
    
    async def update_phone_number(self, phone_number_id: str, agent_id: str) -> Dict[str, Any]:
        """Update phone number agent assignment"""
        try:
            async with httpx.AsyncClient() as client:
                phone_config = {
                    "inbound_agent_id": agent_id,
                    "outbound_agent_id": agent_id
                }
                
                response = await client.patch(
                    f"{self.base_url}/update-phone-number/{phone_number_id}",
                    headers=self.headers,
                    json=phone_config
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully updated phone number: {phone_number_id}")
                    return result
                else:
                    logger.error(f"Failed to update phone number: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error updating phone number: {str(e)}")
            raise
    
    async def make_call(self, from_number: str, to_number: str, agent_id: str) -> Dict[str, Any]:
        """Make an outbound call"""
        try:
            async with httpx.AsyncClient() as client:
                call_config = {
                    "from_number": from_number,
                    "to_number": to_number,
                    "override_agent_id": agent_id
                }
                
                response = await client.post(
                    f"{self.base_url}/create-phone-call",
                    headers=self.headers,
                    json=call_config
                )
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"Successfully initiated call: {result.get('call_id')}")
                    return result
                else:
                    logger.error(f"Failed to make call: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error making call: {str(e)}")
            raise
    
    async def make_agent_to_agent_call(self, caller_agent_id: str, inbound_agent_id: str, from_number: str, to_number: str) -> Dict[str, Any]:
        """Make an agent-to-agent call"""
        try:
            async with httpx.AsyncClient() as client:
                # For agent-to-agent calls, we create a call where the caller agent calls the inbound agent's number
                # The inbound agent will automatically answer based on RetellAI's configuration
                call_config = {
                    "from_number": from_number,
                    "to_number": to_number,
                    "override_agent_id": caller_agent_id,
                    "metadata": {
                        "call_type": "agent_to_agent",
                        "caller_agent_id": caller_agent_id,
                        "inbound_agent_id": inbound_agent_id
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/create-phone-call",
                    headers=self.headers,
                    json=call_config
                )
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"Successfully initiated agent-to-agent call: {result.get('call_id')}")
                    return result
                else:
                    logger.error(f"Failed to make agent-to-agent call: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error making agent-to-agent call: {str(e)}")
            raise
    
    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """Get call details"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/get-call/{call_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to get call: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error getting call: {str(e)}")
            raise
    
    async def list_calls(self, limit: int = 100, sort_order: str = "desc") -> List[Dict[str, Any]]:
        """List calls"""
        try:
            if not self.api_key:
                logger.warning("RetellAI API key not configured, returning mock data")
                return self._get_mock_calls(limit)
                
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "limit": limit,
                    "sort_order": sort_order
                }
                
                response = await client.get(
                    f"{self.base_url}/list-calls",
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to list calls: {response.status_code} - {response.text}")
                    logger.info("Falling back to mock data")
                    return self._get_mock_calls(limit)
                    
        except Exception as e:
            logger.error(f"Error listing calls: {str(e)}")
            logger.info("Falling back to mock data")
            return self._get_mock_calls(limit)

    def _get_mock_agents(self) -> List[Dict[str, Any]]:
        """Return mock agent data for development/fallback"""
        from datetime import datetime
        return [
            {
                "agent_id": "mock_agent_1",
                "agent_name": "Customer Service Agent",
                "voice_id": "11labs-Adrian",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "last_modification_timestamp": datetime.utcnow().isoformat() + "Z",
                "llm_websocket_url": "wss://example.com/llm",
                "general_prompt": "You are a helpful customer service agent.",
                "general_tools": [],
                "mock_data": True
            },
            {
                "agent_id": "mock_agent_2", 
                "agent_name": "Sales Support Agent",
                "voice_id": "11labs-Rachel",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "last_modification_timestamp": datetime.utcnow().isoformat() + "Z",
                "llm_websocket_url": "wss://example.com/llm",
                "general_prompt": "You are a helpful sales support agent.",
                "general_tools": [],
                "mock_data": True
            },
            {
                "agent_id": "mock_agent_3",
                "agent_name": "Technical Support Agent", 
                "voice_id": "11labs-Domi",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "last_modification_timestamp": datetime.utcnow().isoformat() + "Z",
                "llm_websocket_url": "wss://example.com/llm",
                "general_prompt": "You are a helpful technical support agent.",
                "general_tools": [],
                "mock_data": True
            }
        ]
    
    def _get_mock_phone_numbers(self) -> List[Dict[str, Any]]:
        """Return mock phone number data for development/fallback"""
        from datetime import datetime
        return [
            {
                "phone_number_id": "mock_phone_1",
                "phone_number": "+1 (555) 123-4567",
                "area_code": "555",
                "country": "US",
                "region": "California",
                "inbound_agent_id": "mock_agent_1",
                "outbound_agent_id": "mock_agent_1",
                "capabilities": ["inbound", "outbound"],
                "monthly_cost": 2.99,
                "calls_today": 15,
                "status": "active",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "mock_data": True
            },
            {
                "phone_number_id": "mock_phone_2",
                "phone_number": "+1 (555) 987-6543",
                "area_code": "555", 
                "country": "US",
                "region": "New York",
                "inbound_agent_id": "mock_agent_2",
                "outbound_agent_id": "mock_agent_2",
                "capabilities": ["inbound", "outbound"],
                "monthly_cost": 2.99,
                "calls_today": 8,
                "status": "active",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "mock_data": True
            },
            {
                "phone_number_id": "mock_phone_3",
                "phone_number": "+1 (555) 456-7890",
                "area_code": "555",
                "country": "US", 
                "region": "Texas",
                "inbound_agent_id": "mock_agent_3",
                "outbound_agent_id": "mock_agent_3",
                "capabilities": ["inbound"],
                "monthly_cost": 1.99,
                "calls_today": 22,
                "status": "active",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "mock_data": True
            }
        ]
    
    def _get_mock_calls(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return mock call data for development/fallback"""
        from datetime import datetime, timedelta
        import random
        
        calls = []
        statuses = ["completed", "in_progress", "failed"]
        directions = ["inbound", "outbound"]
        agents = ["mock_agent_1", "mock_agent_2", "mock_agent_3"]
        phone_numbers = ["+1 (555) 123-4567", "+1 (555) 987-6543", "+1 (555) 456-7890"]
        
        for i in range(min(limit, 25)):  # Generate up to 25 mock calls
            start_time = datetime.utcnow() - timedelta(hours=random.randint(1, 168))  # Last week
            duration = random.randint(30, 600)  # 30 seconds to 10 minutes
            
            calls.append({
                "call_id": f"mock_call_{i+1}",
                "agent_id": random.choice(agents),
                "phone_number": random.choice(phone_numbers),
                "from_number": random.choice(phone_numbers),
                "to_number": f"+1 (555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "direction": random.choice(directions),
                "status": random.choice(statuses),
                "start_timestamp": start_time.isoformat() + "Z",
                "end_timestamp": (start_time + timedelta(seconds=duration)).isoformat() + "Z",
                "call_length_ms": duration * 1000,
                "recording_url": f"https://example.com/recording_{i+1}.mp3" if random.choice([True, False]) else None,
                "transcript": f"Mock call transcript for call {i+1}...",
                "agent_name": f"Agent {random.randint(1, 3)}",
                "created_at": start_time.isoformat() + "Z",
                "mock_data": True
            })
        
        return calls

# Create singleton instance
retell_service = RetellAIService() 