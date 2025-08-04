from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from ..database import get_db, Agent, PhoneNumber, PhoneCall, Conversation
from ..services.retell_service import retell_service
from ..services.syncro_service import syncro_service

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get comprehensive dashboard statistics"""
    try:
        # Total agents (using actual agents table)
        agents_query = select(func.count(Agent.id)).where(
            (Agent.hidden.is_(None)) | (Agent.hidden == False)
        )
        agents_result = await db.execute(agents_query)
        total_agents = agents_result.scalar()
        
        # Total phone numbers (existing schema doesn't have is_active column)
        phones_query = select(func.count(PhoneNumber.id))
        phones_result = await db.execute(phones_query)
        total_phone_numbers = phones_result.scalar()
        
        # Total interactions today (phone_calls + conversations)
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        
        # Phone calls today
        phone_calls_today_query = select(func.count(PhoneCall.id)).where(
            and_(
                PhoneCall.created_at >= today,
                PhoneCall.created_at < tomorrow
            )
        )
        phone_calls_today_result = await db.execute(phone_calls_today_query)
        phone_calls_today = phone_calls_today_result.scalar() or 0
        
        # Conversations today
        conversations_today_query = select(func.count(Conversation.id)).where(
            and_(
                Conversation.created_at >= today,
                Conversation.created_at < tomorrow
            )
        )
        conversations_today_result = await db.execute(conversations_today_query)
        conversations_today = conversations_today_result.scalar() or 0
        
        total_calls_today = phone_calls_today + conversations_today
        
        # Active interactions - recent activity in last hour
        phone_calls_recent_query = select(func.count(PhoneCall.id)).where(
            PhoneCall.created_at >= datetime.utcnow() - timedelta(hours=1)
        )
        phone_calls_recent_result = await db.execute(phone_calls_recent_query)
        phone_calls_recent = phone_calls_recent_result.scalar() or 0
        
        conversations_recent_query = select(func.count(Conversation.id)).where(
            Conversation.created_at >= datetime.utcnow() - timedelta(hours=1)
        )
        conversations_recent_result = await db.execute(conversations_recent_query)
        conversations_recent = conversations_recent_result.scalar() or 0
        
        active_calls = phone_calls_recent + conversations_recent
        
        # Recent interactions (mix of phone_calls and conversations)
        recent_phone_calls_query = select(PhoneCall).order_by(desc(PhoneCall.created_at)).limit(5)
        recent_phone_calls_result = await db.execute(recent_phone_calls_query)
        recent_phone_calls = recent_phone_calls_result.scalars().all()
        
        recent_conversations_query = select(Conversation).order_by(desc(Conversation.created_at)).limit(5)
        recent_conversations_result = await db.execute(recent_conversations_query)
        recent_conversations = recent_conversations_result.scalars().all()
        
        # Convert to simplified response format
        recent_calls_data = []
        
        # Add phone calls
        for call in recent_phone_calls:
            recent_calls_data.append({
                "id": call.id,
                "type": "phone_call",
                "from_number": call.from_number,
                "to_number": call.to_number,
                "direction": call.direction,
                "status": "completed",
                "duration": call.duration,  # seconds
                "created_at": call.created_at.isoformat() if call.created_at else None,
                "recording_url": call.recording_url,
                "transcript": call.transcript[:100] + "..." if call.transcript and len(call.transcript) > 100 else call.transcript
            })
        
        # Add conversations
        for convo in recent_conversations:
            recent_calls_data.append({
                "id": convo.id,
                "type": "conversation",
                "from_number": None,
                "to_number": None,
                "direction": convo.conversation_type,  # email, sms, etc.
                "status": "completed",
                "duration": None,
                "created_at": convo.created_at.isoformat() if convo.created_at else None,
                "agent_name": convo.agent_name,
                "customer_name": convo.customer_name or convo.customer_contact_name,
                "summary": convo.summary[:100] + "..." if convo.summary and len(convo.summary) > 100 else convo.summary
            })
        
        # Sort by created_at and take top 10
        recent_calls_data.sort(key=lambda x: x["created_at"] or "", reverse=True)
        recent_calls_data = recent_calls_data[:10]
        
        return {
            "total_agents": total_agents or 0,
            "total_phone_numbers": total_phone_numbers or 0,
            "total_calls_today": total_calls_today or 0,
            "active_calls": active_calls or 0,
            "recent_calls": recent_calls_data,
            "agents_with_numbers": []  # We'll populate this later if needed
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health-check")
async def health_check():
    """Comprehensive health check of all systems"""
    try:
        health_status = {
            "database": "unknown",
            "retell_ai": "unknown", 
            "syncro_msp": "unknown",
            "overall": "unknown",
            "timestamp": datetime.utcnow().isoformat(),
            "details": {}
        }
        
        # Database health
        try:
            from ..database import engine
            from sqlalchemy import text
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            health_status["database"] = "healthy"
        except Exception as e:
            health_status["database"] = "unhealthy"
            health_status["details"]["database_error"] = str(e)
        
        # RetellAI health - requires real API key
        try:
            agents = await retell_service.list_agents()
            health_status["retell_ai"] = "healthy"
            health_status["details"]["retell_agents_count"] = len(agents)
        except Exception as e:
            health_status["retell_ai"] = "unhealthy"
            health_status["details"]["retell_error"] = str(e)
        
        # SyncroMSP health
        try:
            tickets = await syncro_service.get_tickets(limit=1)
            health_status["syncro_msp"] = "healthy"
            health_status["details"]["syncro_tickets_accessible"] = len(tickets) > 0
        except Exception as e:
            health_status["syncro_msp"] = "unhealthy"
            health_status["details"]["syncro_error"] = str(e)
        
        # Overall health
        unhealthy_services = [
            service for service, status in {
                "database": health_status["database"],
                "retell_ai": health_status["retell_ai"], 
                "syncro_msp": health_status["syncro_msp"]
            }.items() 
            if status == "unhealthy"
        ]
        
        if not unhealthy_services:
            health_status["overall"] = "healthy"
        elif len(unhealthy_services) == 1:
            health_status["overall"] = "degraded"
        else:
            health_status["overall"] = "unhealthy"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/call-activity")
async def get_call_activity(db: AsyncSession = Depends(get_db)):
    """Get call activity metrics"""
    try:
        # For now, return mock data structure that frontend expects
        # You can enhance this later with real database queries
        
        # Get some basic stats from database
        total_calls_query = select(func.count(PhoneCall.id))
        total_calls_result = await db.execute(total_calls_query)
        total_calls = total_calls_result.scalar() or 0
        
        return {
            "total_calls": total_calls,
            "calls_today": 0,  # Would need to implement proper date filtering
            "average_duration": "4m 32s",
            "success_rate": 94.2,
            "hourly_activity": [],  # Would populate with real data
            "call_outcomes": {
                "successful": 85,
                "failed": 10,
                "no_answer": 5
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting call activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent-performance") 
async def get_agent_performance(db: AsyncSession = Depends(get_db)):
    """Get agent performance metrics"""
    try:
        # Get basic agent count
        agents_query = select(func.count(Agent.id))
        agents_result = await db.execute(agents_query)
        total_agents = agents_result.scalar() or 0
        
        return {
            "total_agents": total_agents,
            "active_agents": total_agents,  # Assume all are active for now
            "average_rating": 4.5,
            "total_conversations": 0,
            "agent_metrics": []  # Would populate with individual agent stats
        }
        
    except Exception as e:
        logger.error(f"Error getting agent performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-overview")
async def get_system_overview(db: AsyncSession = Depends(get_db)):
    """Get complete system overview"""
    try:
        # Combine multiple metrics
        stats = await get_dashboard_stats(db)
        health = await health_check()
        
        return {
            "stats": stats,
            "health": health,
            "uptime": "2h 15m",  # Would implement real uptime tracking
            "version": "1.0.0",
            "environment": "development"
        }
        
    except Exception as e:
        logger.error(f"Error getting system overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@router.get("/ngrok-status")
async def get_ngrok_status():
    """Get ngrok tunnel status via backend proxy to avoid CORS issues"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:4040/api/tunnels", timeout=5.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {"tunnels": []}
    except Exception as e:
        logger.warning(f"Could not fetch ngrok status: {str(e)}")
        return {"tunnels": []}

@router.post("/update-retellai-webhook")
async def update_retellai_webhook():
    """Automatically update RetellAI webhook URLs with current ngrok tunnel"""
    try:
        # Get current ngrok tunnel URL
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:4040/api/tunnels", timeout=5.0)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Could not fetch ngrok tunnels")
            
            tunnels_data = response.json()
            tunnels = tunnels_data.get('tunnels', [])
            
            # Find backend tunnel (port 8000)
            backend_tunnel = None
            for tunnel in tunnels:
                if (tunnel.get('proto') == 'https' and 
                    tunnel.get('config', {}).get('addr', '').endswith(':8000')):
                    backend_tunnel = tunnel
                    break
            
            if not backend_tunnel:
                raise HTTPException(status_code=400, detail="No ngrok tunnel found for port 8000")
            
            ngrok_url = backend_tunnel['public_url']
            webhook_url = f"{ngrok_url}/api/v1/retellai/agent-level-webhook"
            
            # Update all RetellAI agents with new webhook URL
            from ..services.retell_service import retell_service
            result = await retell_service.update_all_agent_webhooks(webhook_url)
            
            return {
                "success": True,
                "ngrok_url": ngrok_url,
                "webhook_url": webhook_url,
                "update_result": result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating RetellAI webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update webhook: {str(e)}") 