import httpx
import os
from typing import Dict, Any, Optional, List
from loguru import logger

class SyncroMSPService:
    def __init__(self):
        self.api_key = os.getenv("SYNCROMSP_API_KEY")
        self.base_url = os.getenv("SYNCROMSP_API_URL")
        self.tickets_path = os.getenv("SYNCROMSP_TICKETS_PATH", "/api/v1/tickets")
        self.customers_path = os.getenv("SYNCROMSP_CUSTOMERS_PATH", "/api/v1/customers")
        self.ticket_comments_path = os.getenv("SYNCROMSP_TICKET_COMMENTS_PATH", "/comment")
        
        # READ-ONLY MODE: Log configuration status
        if not self.api_key or not self.base_url:
            raise ValueError("SyncroMSP API credentials not found - real credentials required for read-only operations")
        else:
            logger.info("SyncroMSP credentials found - service configured for READ-ONLY mode")
            
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
    
    # ============================================================================
    # READ OPERATIONS (ACTIVE)
    # ============================================================================
    
    async def get_tickets(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get tickets from SyncroMSP - READ-ONLY OPERATION"""
        try:
            async with httpx.AsyncClient() as client:
                params = {"limit": limit}
                if status:
                    params["status"] = status
                
                response = await client.get(
                    f"{self.base_url}{self.tickets_path}",
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    tickets = data.get("tickets", [])
                    logger.info(f"Retrieved {len(tickets)} tickets from SyncroMSP")
                    return tickets
                else:
                    logger.error(f"Failed to get tickets: {response.status_code} - {response.text}")
                    raise Exception(f"SyncroMSP API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error getting SyncroMSP tickets: {str(e)}")
            raise
    
    async def get_ticket(self, ticket_id: int) -> Dict[str, Any]:
        """Get a specific ticket from SyncroMSP - READ-ONLY OPERATION"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}{self.tickets_path}/{ticket_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ticket = data.get("ticket", {})
                    logger.info(f"Retrieved ticket {ticket_id} from SyncroMSP")
                    return ticket
                else:
                    logger.error(f"Failed to get ticket: {response.status_code} - {response.text}")
                    raise Exception(f"SyncroMSP API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error getting SyncroMSP ticket: {str(e)}")
            raise
    
    async def get_customers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get customers from SyncroMSP - READ-ONLY OPERATION"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}{self.customers_path}",
                    headers=self.headers,
                    params={"limit": limit}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    customers = data.get("customers", [])
                    logger.info(f"Retrieved {len(customers)} customers from SyncroMSP")
                    return customers
                else:
                    logger.error(f"Failed to get customers: {response.status_code} - {response.text}")
                    raise Exception(f"SyncroMSP API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error getting SyncroMSP customers: {str(e)}")
            raise
    
    async def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """Get a specific customer from SyncroMSP - READ-ONLY OPERATION"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}{self.customers_path}/{customer_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    customer = data.get("customer", {})
                    logger.info(f"Retrieved customer {customer_id} from SyncroMSP")
                    return customer
                else:
                    logger.error(f"Failed to get customer: {response.status_code} - {response.text}")
                    raise Exception(f"SyncroMSP API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error getting SyncroMSP customer: {str(e)}")
            raise
    
    # ============================================================================
    # CUD OPERATIONS (DISABLED FOR READ-ONLY MODE)
    # ============================================================================
    
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """CREATE OPERATION DISABLED - READ-ONLY MODE"""
        logger.warning(f"BLOCKED CREATE OPERATION: Attempt to create ticket in SyncroMSP with data: {ticket_data}")
        
        raise Exception(
            "CREATE operations are disabled - Application is in READ-ONLY mode. "
            "SyncroMSP ticket creation is not permitted to prevent unintended modifications."
        )
    
    async def update_ticket(self, ticket_id: int, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """UPDATE OPERATION DISABLED - READ-ONLY MODE"""
        logger.warning(f"BLOCKED UPDATE OPERATION: Attempt to update ticket {ticket_id} in SyncroMSP with data: {ticket_data}")
        
        raise Exception(
            "UPDATE operations are disabled - Application is in READ-ONLY mode. "
            "SyncroMSP ticket updates are not permitted to prevent unintended modifications."
        )
    
    async def add_comment(self, ticket_id: int, comment: str, hidden: bool = False) -> Dict[str, Any]:
        """UPDATE OPERATION DISABLED - READ-ONLY MODE"""
        logger.warning(f"BLOCKED COMMENT OPERATION: Attempt to add comment to ticket {ticket_id} in SyncroMSP: {comment[:50]}...")
        
        raise Exception(
            "COMMENT operations are disabled - Application is in READ-ONLY mode. "
            "SyncroMSP comment additions are not permitted to prevent unintended modifications."
        )
    


# ============================================================================
# COMMENTED OUT: Original CUD operations (completely disabled)
# ============================================================================

"""
# ORIGINAL SYNCROMSP CUD OPERATIONS - COMMENTED OUT FOR READ-ONLY MODE
# These were the original write operations that are now disabled

async def create_ticket_original(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    # Original create ticket implementation
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{self.tickets_path}",
                headers=self.headers,
                json={"ticket": ticket_data}
            )
            
            if response.status_code == 201:
                data = response.json()
                ticket = data.get("ticket", {})
                logger.info(f"Created ticket {ticket.get('id')} in SyncroMSP")
                return ticket
            else:
                logger.error(f"Failed to create ticket: {response.status_code} - {response.text}")
                raise Exception(f"SyncroMSP API error: {response.status_code}")
                
    except Exception as e:
        logger.error(f"Error creating SyncroMSP ticket: {str(e)}")
        raise

async def update_ticket_original(self, ticket_id: int, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    # Original update ticket implementation
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}{self.tickets_path}/{ticket_id}",
                headers=self.headers,
                json={"ticket": ticket_data}
            )
            
            if response.status_code == 200:
                data = response.json()
                ticket = data.get("ticket", {})
                logger.info(f"Updated ticket {ticket_id} in SyncroMSP")
                return ticket
            else:
                logger.error(f"Failed to update ticket: {response.status_code} - {response.text}")
                raise Exception(f"SyncroMSP API error: {response.status_code}")
                
    except Exception as e:
        logger.error(f"Error updating SyncroMSP ticket: {str(e)}")
        raise

async def add_comment_original(self, ticket_id: int, comment: str, hidden: bool = False) -> Dict[str, Any]:
    # Original add comment implementation
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}{self.tickets_path}/{ticket_id}{self.ticket_comments_path}",
                headers=self.headers,
                json={
                    "comment": {
                        "body": comment,
                        "hidden": hidden
                    }
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                comment_obj = data.get("comment", {})
                logger.info(f"Added comment to ticket {ticket_id} in SyncroMSP")
                return comment_obj
            else:
                logger.error(f"Failed to add comment: {response.status_code} - {response.text}")
                raise Exception(f"SyncroMSP API error: {response.status_code}")
                
    except Exception as e:
        logger.error(f"Error adding SyncroMSP comment: {str(e)}")
        raise
"""

# Create singleton instance
syncro_service = SyncroMSPService() 