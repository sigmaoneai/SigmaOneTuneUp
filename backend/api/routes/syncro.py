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

# Mock data for READ-ONLY operations
MOCK_CUSTOMERS = [
    {
        "id": 1,
        "business_name": "Acme Corporation",
        "contact_name": "John Smith",
        "email": "john@acme.com",
        "phone": "(555) 123-4567",
        "address": "123 Main St, Anytown, ST 12345",
        "created_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": 2,
        "business_name": "Tech Solutions Inc",
        "contact_name": "Sarah Johnson",
        "email": "sarah@techsolutions.com",
        "phone": "(555) 987-6543",
        "address": "456 Oak Ave, Business City, ST 67890",
        "created_at": "2024-02-03T14:22:00Z"
    },
    {
        "id": 3,
        "business_name": "Digital Marketing LLC",
        "contact_name": "Mike Wilson",
        "email": "mike@digitalmarketing.com",
        "phone": "(555) 456-7890",
        "address": "789 Pine Rd, Metro Town, ST 54321",
        "created_at": "2024-01-28T09:15:00Z"
    },
    {
        "id": 4,
        "business_name": "Creative Design Studio",
        "contact_name": "Emily Davis",
        "email": "emily@creativedesign.com",
        "phone": "(555) 321-9876",
        "address": "321 Elm Dr, Art District, ST 98765",
        "created_at": "2024-02-10T16:45:00Z"
    },
    {
        "id": 5,
        "business_name": "Global Consulting Group",
        "contact_name": "Robert Chen",
        "email": "robert@globalconsulting.com",
        "phone": "(555) 654-3210",
        "address": "654 Maple Blvd, Corporate Plaza, ST 13579",
        "created_at": "2024-01-20T11:30:00Z"
    }
]

# Mock tickets data for READ-ONLY operations
MOCK_TICKETS = [
    {
        "id": 1,
        "subject": "Email server not responding",
        "status": "open",
        "priority": "high",
        "customer_id": 1,
        "customer_business_then_name": "Acme Corporation - John Smith",
        "problem_type": "Email Issues",
        "created_at": "2024-03-15T09:30:00Z",
        "updated_at": "2024-03-15T14:20:00Z",
        "description": "Email server has been unresponsive since this morning. Users cannot send or receive emails.",
        "assignee": "Jane Doe",
        "comments": [
            {"id": 1, "comment": "Investigating email server logs", "created_at": "2024-03-15T10:00:00Z", "author": "Jane Doe"},
            {"id": 2, "comment": "Found disk space issue on mail server", "created_at": "2024-03-15T14:20:00Z", "author": "Jane Doe"}
        ]
    },
    {
        "id": 2,
        "subject": "Network connectivity issues in main office",
        "status": "urgent",
        "priority": "critical",
        "customer_id": 2,
        "customer_business_then_name": "Tech Solutions Inc - Sarah Johnson",
        "problem_type": "Network",
        "created_at": "2024-03-14T16:45:00Z",
        "updated_at": "2024-03-15T08:30:00Z",
        "description": "Entire main office experiencing intermittent network connectivity issues affecting all operations.",
        "assignee": "Mike Wilson",
        "comments": []
    },
    {
        "id": 3,
        "subject": "Software installation request",
        "status": "in_progress",
        "priority": "medium",
        "customer_id": 3,
        "customer_business_then_name": "Digital Marketing LLC - Mike Wilson",
        "problem_type": "Software",
        "created_at": "2024-03-13T11:20:00Z",
        "updated_at": "2024-03-14T09:15:00Z",
        "description": "Need to install new design software on 5 workstations for the creative team.",
        "assignee": "Sarah Johnson",
        "comments": [
            {"id": 1, "comment": "Software licenses ordered", "created_at": "2024-03-13T15:00:00Z", "author": "Sarah Johnson"}
        ]
    },
    {
        "id": 4,
        "subject": "Printer maintenance and toner replacement",
        "status": "completed",
        "priority": "low",
        "customer_id": 4,
        "customer_business_then_name": "Creative Design Studio - Emily Davis",
        "problem_type": "Hardware",
        "created_at": "2024-03-12T14:30:00Z",
        "updated_at": "2024-03-13T10:45:00Z",
        "description": "Monthly printer maintenance and toner replacement for main office printer.",
        "assignee": "Tech Support",
        "comments": [
            {"id": 1, "comment": "Maintenance completed, new toner installed", "created_at": "2024-03-13T10:45:00Z", "author": "Tech Support"}
        ]
    },
    {
        "id": 5,
        "subject": "VPN access setup for remote employee",
        "status": "open",
        "priority": "medium",
        "customer_id": 5,
        "customer_business_then_name": "Global Consulting Group - Robert Chen",
        "problem_type": "Remote Access",
        "created_at": "2024-03-15T13:20:00Z",
        "updated_at": "2024-03-15T13:20:00Z",
        "description": "New remote employee needs VPN access configured for secure connection to company resources.",
        "assignee": "Network Team",
        "comments": []
    }
]

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
    """List tickets with optional filtering - READ-ONLY MOCK DATA"""
    try:
        logger.info(f"READ-ONLY: Fetching tickets with filters: status={status}, priority={priority}, limit={limit}")
        
        # Filter mock tickets
        filtered_tickets = MOCK_TICKETS.copy()
        
        if status:
            filtered_tickets = [t for t in filtered_tickets if t["status"] == status]
        
        if priority:
            filtered_tickets = [t for t in filtered_tickets if t["priority"] == priority]
        
        # Apply limit
        filtered_tickets = filtered_tickets[:limit]
        
        return {
            "tickets": filtered_tickets,
            "count": len(filtered_tickets),
            "total_available": len(MOCK_TICKETS),
            "filters_applied": {
                "status": status,
                "priority": priority,
                "limit": limit
            },
            "read_only_mode": True,
            "notice": "This is READ-ONLY mode with mock data. No real SyncroMSP modifications will be made."
        }
    
    except Exception as e:
        logger.error(f"Error fetching tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickets/{ticket_id}", response_model=dict)
async def get_syncro_ticket_details(ticket_id: int):
    """Get detailed ticket information - READ-ONLY MOCK DATA"""
    try:
        logger.info(f"READ-ONLY: Fetching mock ticket details for ID: {ticket_id}")
        
        # Find ticket in mock data
        ticket = next((t for t in MOCK_TICKETS if t["id"] == ticket_id), None)
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found in mock data")
        
        # Add some additional mock details
        detailed_ticket = ticket.copy()
        detailed_ticket.update({
            "time_entries": [
                {"id": 1, "description": "Initial diagnosis", "hours": 0.5, "date": "2024-03-15", "technician": "John Doe"},
                {"id": 2, "description": "System repair", "hours": 2.0, "date": "2024-03-15", "technician": "Jane Smith"}
            ],
            "assets": [
                {"id": 1, "name": "Server-01", "type": "Server", "location": "Data Center"},
                {"id": 2, "name": "Switch-Main", "type": "Network Switch", "location": "Server Room"}
            ],
            "resolution_notes": "Issue resolved by restarting email service and updating network configuration.",
            "customer_satisfaction": 4.5,
            "read_only_mode": True,
            "notice": "This is READ-ONLY mode with mock data."
        })
        
        return detailed_ticket
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticket details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers", response_model=dict)
async def list_customers(limit: int = 100):
    """List customers - READ-ONLY MOCK DATA"""
    try:
        logger.info(f"READ-ONLY: Fetching mock customers with limit: {limit}")
        
        # Apply limit to mock customers
        customers = MOCK_CUSTOMERS[:limit]
        
        return {
            "customers": customers,
            "count": len(customers),
            "total_available": len(MOCK_CUSTOMERS),
            "limit": limit,
            "read_only_mode": True,
            "notice": "This is READ-ONLY mode with mock data. No real SyncroMSP modifications will be made."
        }
    
    except Exception as e:
        logger.error(f"Error fetching customers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers/{customer_id}", response_model=dict)
async def get_customer(customer_id: int):
    """Get customer details - READ-ONLY MOCK DATA"""
    try:
        logger.info(f"READ-ONLY: Fetching mock customer details for ID: {customer_id}")
        
        # Find customer in mock data
        customer = next((c for c in MOCK_CUSTOMERS if c["id"] == customer_id), None)
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found in mock data")
        
        # Add additional mock details
        detailed_customer = customer.copy()
        detailed_customer.update({
            "tickets_count": len([t for t in MOCK_TICKETS if t["customer_id"] == customer_id]),
            "open_tickets": len([t for t in MOCK_TICKETS if t["customer_id"] == customer_id and t["status"] == "open"]),
            "last_activity": "2024-03-15T10:30:00Z",
            "account_status": "active",
            "billing_contact": customer["contact_name"],
            "notes": f"Customer since {customer['created_at'][:4]}",
            "read_only_mode": True,
            "notice": "This is READ-ONLY mode with mock data."
        })
        
        return detailed_customer
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers/search/{search_term}")
async def search_customers(search_term: str):
    """Search customers by name, email, or phone - READ-ONLY MOCK DATA"""
    try:
        logger.info(f"READ-ONLY: Searching customers for term: {search_term}")
        
        search_lower = search_term.lower()
        matching_customers = []
        
        for customer in MOCK_CUSTOMERS:
            if (search_lower in customer["business_name"].lower() or
                search_lower in customer["contact_name"].lower() or
                search_lower in customer["email"].lower() or
                search_lower in customer["phone"]):
                matching_customers.append(customer)
        
        return {
            "customers": matching_customers,
            "search_term": search_term,
            "count": len(matching_customers),
            "read_only_mode": True,
            "notice": "This is READ-ONLY mode with mock data. No real SyncroMSP modifications will be made."
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
async def sync_tickets_from_syncro_disabled(
    status: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """SYNC OPERATION DISABLED - READ-ONLY MODE"""
    logger.warning(f"BLOCKED SYNC OPERATION: Attempt to sync tickets from SyncroMSP")
    
    return {
        "error": "SYNC operations are disabled in read-only mode",
        "message": "This application is configured for READ-ONLY access to SyncroMSP data",
        "operation": "sync_tickets",
        "read_only_mode": True,
        "recommendation": "Enable write operations to sync real data from SyncroMSP",
        "mock_alternative": "Use GET /tickets for read-only access to mock ticket data"
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