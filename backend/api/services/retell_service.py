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
        self.base_url_v2 = "https://api.retellai.com/v2"
        self.webhook_url = os.getenv("RETELLAI_AGENT_WEBHOOK_URL")
        self.agent_name_prefix = os.getenv("RETELLAI_AGENT_NAME_PREFIX", "SigmaOne - User <user_id> - Agent '<agent_name>'")
        
        if not self.api_key:
            raise ValueError("RETELLAI_API_KEY not found in environment variables. Real API key is required.")
            
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
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/list-agents",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to list agents: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error listing RetellAI agents: {str(e)}")
            raise
    
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

    async def update_all_agent_webhooks(self, new_webhook_url: str) -> Dict[str, Any]:
        """Update webhook URL for all RetellAI agents"""
        try:
            # First, get all agents
            agents_response = await self.list_agents()
            agents = agents_response.get('data', [])
            
            if not agents:
                return {"success": True, "message": "No agents found", "updated_count": 0}
            
            updated_count = 0
            failed_updates = []
            
            # Update each agent's webhook URL
            for agent in agents:
                agent_id = agent.get('agent_id')
                if not agent_id:
                    continue
                    
                try:
                    await self.update_agent(agent_id, {
                        "agent_level_webhook_url": new_webhook_url
                    })
                    updated_count += 1
                    logger.info(f"Updated webhook for agent {agent_id}")
                except Exception as e:
                    failed_updates.append({"agent_id": agent_id, "error": str(e)})
                    logger.error(f"Failed to update webhook for agent {agent_id}: {str(e)}")
            
            result = {
                "success": True,
                "message": f"Updated {updated_count} agents successfully",
                "updated_count": updated_count,
                "total_agents": len(agents),
                "new_webhook_url": new_webhook_url
            }
            
            if failed_updates:
                result["failed_updates"] = failed_updates
                result["message"] += f", {len(failed_updates)} failed"
            
            return result
            
        except Exception as e:
            logger.error(f"Error bulk updating agent webhooks: {str(e)}")
            raise

    async def create_conversation_flow(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new RetellAI conversation flow"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/create-conversation-flow",
                    headers=self.headers,
                    json=flow_data
                )
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"Successfully created conversation flow: {result.get('conversation_flow_id')}")
                    return result
                else:
                    logger.error(f"Failed to create conversation flow: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error creating conversation flow: {str(e)}")
            raise

    async def list_conversation_flows(self) -> Dict[str, Any]:
        """List all conversation flows"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/list-conversation-flows",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully retrieved {len(result.get('data', []))} conversation flows")
                    return result
                else:
                    logger.error(f"Failed to list conversation flows: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error listing conversation flows: {str(e)}")
            raise

    async def get_conversation_flow(self, flow_id: str) -> Dict[str, Any]:
        """Get a specific conversation flow"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/get-conversation-flow/{flow_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully retrieved conversation flow: {flow_id}")
                    return result
                else:
                    logger.error(f"Failed to get conversation flow: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error getting conversation flow: {str(e)}")
            raise

    async def update_conversation_flow(self, flow_id: str, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a conversation flow"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/update-conversation-flow/{flow_id}",
                    headers=self.headers,
                    json=flow_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully updated conversation flow: {flow_id}")
                    return result
                else:
                    logger.error(f"Failed to update conversation flow: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error updating conversation flow: {str(e)}")
            raise

    async def delete_conversation_flow(self, flow_id: str) -> bool:
        """Delete a conversation flow"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/delete-conversation-flow/{flow_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully deleted conversation flow: {flow_id}")
                    return True
                else:
                    logger.error(f"Failed to delete conversation flow: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error deleting conversation flow: {str(e)}")
            raise
    
    # async def delete_agent(self, agent_id: str) -> bool:
    #     """Delete a RetellAI agent"""
    #     try:
    #         async with httpx.AsyncClient() as client:
    #             response = await client.delete(
    #                 f"{self.base_url}/delete-agent/{agent_id}",
    #                 headers=self.headers
    #             )
    #             
    #             if response.status_code == 200:
    #                 logger.info(f"Successfully deleted RetellAI agent: {agent_id}")
    #                 return True
    #             else:
    #                 logger.error(f"Failed to delete agent: {response.status_code} - {response.text}")
    #                 raise Exception(f"RetellAI API error: {response.status_code}")
    #                 
    #     except Exception as e:
    #         logger.error(f"Error deleting RetellAI agent: {str(e)}")
    #         raise
    
    async def get_phone_numbers(self) -> List[Dict[str, Any]]:
        """List all phone numbers"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/list-phone-numbers",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to list phone numbers: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error listing phone numbers: {str(e)}")
            raise
    
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
                    f"{self.base_url_v2}/create-phone-call",
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
                    f"{self.base_url_v2}/create-phone-call",
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
                    f"{self.base_url_v2}/get-call/{call_id}",
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
    
    async def list_calls(self, limit: int = 100, sort_order: str = "descending") -> List[Dict[str, Any]]:
        """List calls"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url_v2}/list-calls",
                    headers=self.headers,
                    json={
                        "limit": limit,
                        "sort_order": sort_order
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to list calls: {response.status_code} - {response.text}")
                    raise Exception(f"RetellAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error listing calls: {str(e)}")
            raise



# Create singleton instance
retell_service = RetellAIService() 