from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
import asyncio
from loguru import logger
from datetime import datetime, timedelta
import random

from ..database import get_db, SyncroTicket
from ..services.syncro_service import syncro_service
from ..schemas import TicketCreate, TicketResponse, ErrorResponse

router = APIRouter()

# Real SyncroMSP data only - no mock data

# ============================================================================
# READ-ONLY OPERATIONS (ACTIVE)
# ============================================================================

@router.get("/tickets", response_model=dict)
async def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List tickets with optional filtering from SyncroMSP API"""
    try:
        logger.info(f"Fetching tickets from SyncroMSP with filters: status={status}, priority={priority}, limit={limit}")
        
        # Get tickets from SyncroMSP service
        tickets = await syncro_service.get_tickets(status=status, limit=limit)
        
        # Apply priority filter if specified (SyncroMSP might not support this directly)
        if priority:
            tickets = [t for t in tickets if t.get("priority") == priority]
        
        return {
            "tickets": tickets,
            "count": len(tickets),
            "filters_applied": {
                "status": status,
                "priority": priority,
                "limit": limit
            },
            "source": "syncromsp_api"
        }
    
    except Exception as e:
        logger.error(f"Error fetching tickets from SyncroMSP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickets/{ticket_id}", response_model=dict)
async def get_syncro_ticket_details(ticket_id: int):
    """Get detailed ticket information from SyncroMSP API"""
    try:
        logger.info(f"Fetching ticket details from SyncroMSP for ID: {ticket_id}")
        
        # Get ticket from SyncroMSP service
        ticket = await syncro_service.get_ticket(ticket_id)
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return {
            "ticket": ticket,
            "source": "syncromsp_api"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticket details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers", response_model=dict)
async def list_customers(limit: int = 100):
    """List customers from SyncroMSP API"""
    try:
        logger.info(f"Fetching customers from SyncroMSP with limit: {limit}")
        
        # Get customers from SyncroMSP service
        customers = await syncro_service.get_customers(limit=limit)
        
        return {
            "customers": customers,
            "count": len(customers),
            "limit": limit,
            "source": "syncromsp_api"
        }
    
    except Exception as e:
        logger.error(f"Error fetching customers from SyncroMSP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers/{customer_id}", response_model=dict)
async def get_customer(customer_id: int):
    """Get customer details from SyncroMSP API"""
    try:
        logger.info(f"Fetching customer details from SyncroMSP for ID: {customer_id}")
        
        # Get customer from SyncroMSP service
        customer = await syncro_service.get_customer(customer_id)
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return {
            "customer": customer,
            "source": "syncromsp_api"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers/search/{search_term}")
async def search_customers(search_term: str):
    """Search customers by name, email, or phone using SyncroMSP API"""
    try:
        logger.info(f"Searching SyncroMSP customers for term: {search_term}")
        
        # Get all customers and filter locally
        # Note: SyncroMSP may have specific search endpoints, but for now we'll filter client-side
        all_customers = await syncro_service.get_customers(limit=1000)
        
        search_lower = search_term.lower()
        matching_customers = []
        
        for customer in all_customers:
            # Search in various fields - adjust based on SyncroMSP API response structure
            business_name = customer.get("business_name", "").lower()
            contact_name = customer.get("contact_name", "").lower()
            email = customer.get("email", "").lower()
            phone = customer.get("phone", "")
            
            if (search_lower in business_name or
                search_lower in contact_name or
                search_lower in email or
                search_lower in phone):
                matching_customers.append(customer)
        
        return {
            "customers": matching_customers,
            "search_term": search_term,
            "count": len(matching_customers),
            "source": "syncromsp_api"
        }
    
    except Exception as e:
        logger.error(f"Error searching customers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CUD OPERATIONS (DISABLED FOR READ-ONLY MODE)
# ============================================================================

# DISABLED: All CREATE, UPDATE, DELETE operations are commented out below
# These endpoints return read-only warnings instead of performing real operations

@router.post("/tickets", response_model=dict)
async def create_syncro_ticket_disabled(
    ticket: TicketCreate,
    db: AsyncSession = Depends(get_db)
):
    """CREATE OPERATION DISABLED - READ-ONLY MODE"""
    logger.warning(f"BLOCKED CREATE OPERATION: Attempt to create ticket with subject: {ticket.subject}")
    
    return {
        "error": "CREATE operations are disabled in READ-only mode",
        "message": "This application is configured for READ-ONLY access to SyncroMSP data",
        "operation": "create_ticket",
        "blocked_data": {
            "subject": ticket.subject,
            "customer_id": ticket.customer_id if hasattr(ticket, 'customer_id') else None
        },
        "read_only_mode": True,
        "recommendation": "Use mock data or enable write operations if needed"
    }

@router.post("/tickets/{ticket_id}/comments")
async def add_ticket_comment_disabled(
    ticket_id: int,
    comment_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """UPDATE OPERATION DISABLED - READ-ONLY MODE"""
    comment = comment_data.get("comment", "")
    logger.warning(f"BLOCKED UPDATE OPERATION: Attempt to add comment to ticket {ticket_id}: {comment[:50]}...")
    
    return {
        "error": "UPDATE operations are disabled in read-only mode",
        "message": "This application is configured for READ-ONLY access to SyncroMSP data",
        "operation": "add_comment",
        "blocked_data": {
            "ticket_id": ticket_id,
            "comment": comment[:100] + "..." if len(comment) > 100 else comment
        },
        "read_only_mode": True,
        "recommendation": "Comments cannot be added in read-only mode"
    }

@router.get("/tickets/sync-from-syncro")
async def sync_tickets_from_syncro(
    status: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Sync tickets from SyncroMSP API (READ-ONLY) - fetches latest data without modifications"""
    try:
        logger.info(f"Syncing tickets from SyncroMSP API (read-only): status={status}, limit={limit}")
        
        # Get fresh tickets from SyncroMSP API
        tickets = await syncro_service.get_tickets(status=status, limit=limit)
        
        # Count new vs existing (for stats - we're not actually writing to local DB in read-only mode)
        new_count = len(tickets)  # All tickets are "new" since we're just fetching
        updated_count = 0  # No updates in read-only mode
        
        return {
            "message": "Tickets synced from SyncroMSP API (read-only mode)",
            "new_count": new_count,
            "updated_count": updated_count,
            "total_tickets": len(tickets),
            "tickets": tickets,
            "filters_applied": {
                "status": status,
                "limit": limit
            },
            "read_only_mode": True,
            "source": "syncromsp_api",
            "note": "Data fetched from SyncroMSP API but not stored locally (read-only mode)"
        }
        
    except Exception as e:
        logger.error(f"Error syncing tickets from SyncroMSP: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_syncro_connection_status():
    """Get SyncroMSP connection status"""
    try:
        # Check if credentials are configured
        has_credentials = syncro_service.api_key and syncro_service.base_url
        
        connection_status = {
            "connected": has_credentials,
            "read_only_mode": True,
            "api_configured": has_credentials,
            "base_url": syncro_service.base_url if has_credentials else None
        }
        
        if has_credentials:
            try:
                # Test connection by fetching a small number of tickets
                test_tickets = await syncro_service.get_tickets(limit=1)
                connection_status["api_test"] = "success"
                connection_status["last_test"] = datetime.utcnow().isoformat()
            except Exception as e:
                connection_status["connected"] = False
                connection_status["api_test"] = "failed"
                connection_status["error"] = str(e)
        else:
            connection_status["message"] = "SyncroMSP API credentials not configured"
            
        return connection_status
        
    except Exception as e:
        logger.error(f"Error checking SyncroMSP status: {str(e)}")
        return {
            "connected": False,
            "read_only_mode": True,
            "api_configured": False,
            "error": str(e)
        }

@router.post("/retell-tools/create-ticket")
async def retell_tool_create_ticket_disabled(request: dict):
    """RETELL TOOL CREATE OPERATION DISABLED - READ-ONLY MODE"""
    customer_id = request.get("customer_id")
    subject = request.get("subject", "")
    
    logger.warning(f"BLOCKED RETELL TOOL: Attempt to create ticket for customer {customer_id} with subject: {subject}")
    
    return {
        "success": False,
        "error": "CREATE operations are disabled in read-only mode",
        "message": "RetellAI ticket creation is disabled - application is in READ-ONLY mode",
        "operation": "retell_create_ticket",
        "blocked_data": {
            "customer_id": customer_id,
            "subject": subject,
            "description": request.get("description", "")[:100]
        },
        "read_only_mode": True,
        "recommendation": "Enable write operations for RetellAI agents to create real tickets"
    }

# ============================================================================
# COMMENTED OUT: Real SyncroMSP operations (completely disabled)
# ============================================================================

"""
# ALL REAL SYNCROMSP CUD OPERATIONS ARE COMMENTED OUT FOR READ-ONLY MODE
# Uncomment these sections only when ready to enable real SyncroMSP writes

@router.post("/tickets-real")
async def create_syncro_ticket_real(ticket: TicketCreate, db: AsyncSession = Depends(get_db)):
    # Real ticket creation via SyncroMSP API
    try:
        syncro_ticket = await syncro_service.create_ticket({
            "subject": ticket.subject,
            "customer_id": ticket.customer_id,
            "priority": ticket.priority,
            "description": ticket.description,
            "problem_type": ticket.problem_type
        })
        # Store in local database
        db_ticket = SyncroTicket(
            syncro_ticket_id=str(syncro_ticket["id"]),
            customer_id=str(ticket.customer_id),
            subject=ticket.subject,
            description=ticket.description,
            status=syncro_ticket.get("status", "open"),
            priority=ticket.priority,
            problem_type=ticket.problem_type
        )
        db.add(db_ticket)
        await db.commit()
        await db.refresh(db_ticket)
        
        return {"message": "Real ticket created in SyncroMSP", "ticket": syncro_ticket}
    except Exception as e:
        logger.error(f"Error creating real ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tickets-real/{ticket_id}")
async def update_syncro_ticket_real(ticket_id: int, updates: dict, db: AsyncSession = Depends(get_db)):
    # Real ticket update via SyncroMSP API
    try:
        updated_ticket = await syncro_service.update_ticket(ticket_id, updates)
        return {"message": "Real ticket updated in SyncroMSP", "ticket": updated_ticket}
    except Exception as e:
        logger.error(f"Error updating real ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tickets-real/{ticket_id}")
async def delete_syncro_ticket_real(ticket_id: int, db: AsyncSession = Depends(get_db)):
    # Real ticket deletion via SyncroMSP API - DANGEROUS OPERATION
    # This should only be enabled with extreme caution
    pass
""" 