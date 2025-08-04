from fastapi import APIRouter, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, and_, func
from typing import List, Optional
import json
import asyncio
from datetime import datetime, timedelta
from loguru import logger

from ..database import get_db, PhoneCall, Call, CallEvent, RetellAgent, PhoneNumber
from ..services.retell_service import retell_service
from ..schemas import CallCreate, CallResponse, RetellWebhookEvent

router = APIRouter()

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.call_connections: dict = {}  # call_id -> [websockets]
    
    async def connect(self, websocket: WebSocket, call_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if call_id:
            if call_id not in self.call_connections:
                self.call_connections[call_id] = []
            self.call_connections[call_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, call_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if call_id and call_id in self.call_connections:
            if websocket in self.call_connections[call_id]:
                self.call_connections[call_id].remove(websocket)
            if not self.call_connections[call_id]:
                del self.call_connections[call_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            pass
    
    async def broadcast_to_call(self, message: str, call_id: str):
        if call_id in self.call_connections:
            disconnected = []
            for websocket in self.call_connections[call_id]:
                try:
                    await websocket.send_text(message)
                except:
                    disconnected.append(websocket)
            
            # Remove disconnected websockets
            for ws in disconnected:
                self.disconnect(ws, call_id)

manager = ConnectionManager()

@router.websocket("/ws/transcript/{call_id}")
async def websocket_transcript(websocket: WebSocket, call_id: str):
    """WebSocket endpoint for real-time transcript updates"""
    await manager.connect(websocket, call_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": datetime.utcnow().isoformat()}), 
                    websocket
                )
            elif message_data.get("type") == "subscribe":
                # Subscribe to call updates
                await manager.send_personal_message(
                    json.dumps({
                        "type": "subscribed", 
                        "call_id": call_id,
                        "message": f"Subscribed to call {call_id} updates"
                    }), 
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, call_id)
        logger.info(f"WebSocket disconnected for call {call_id}")
    except Exception as e:
        logger.error(f"WebSocket error for call {call_id}: {str(e)}")
        manager.disconnect(websocket, call_id)

@router.get("/", response_model=List[CallResponse])
async def list_calls(
    skip: int = 0,
    limit: int = 100,
    direction: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List calls with filtering options"""
    try:
        # Use the Call model which has proper RetellAI integration
        query = select(Call)
        
        if direction:
            query = query.where(Call.direction == direction)
        
        query = query.order_by(desc(Call.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        calls = result.scalars().all()
        
        # Enrich calls with agent names for display
        enriched_calls = []
        for call in calls:
            call_dict = {
                "id": call.id,
                "retell_call_id": call.retell_call_id,
                "agent_id": call.agent_id,
                "caller_agent_id": call.caller_agent_id,
                "inbound_agent_id": call.inbound_agent_id,
                "phone_number_id": call.phone_number_id,
                "from_number": call.from_number,
                "to_number": call.to_number,
                "direction": call.direction,
                "status": call.status,
                "start_timestamp": call.start_timestamp,
                "end_timestamp": call.end_timestamp,
                "duration_ms": call.duration_ms,
                "recording_url": call.recording_url,
                "transcript": call.transcript,
                "call_analysis": call.call_analysis,
                "call_metadata": call.call_metadata,
                "created_at": call.created_at,
                "caller_agent_name": None,
                "inbound_agent_name": None
            }
            
            # Get agent names if available
            if call.caller_agent_id:
                caller_query = select(RetellAgent).where(RetellAgent.id == call.caller_agent_id)
                caller_result = await db.execute(caller_query)
                caller_agent = caller_result.scalar_one_or_none()
                if caller_agent:
                    call_dict["caller_agent_name"] = caller_agent.name
            
            if call.inbound_agent_id:
                inbound_query = select(RetellAgent).where(RetellAgent.id == call.inbound_agent_id)
                inbound_result = await db.execute(inbound_query)
                inbound_agent = inbound_result.scalar_one_or_none()
                if inbound_agent:
                    call_dict["inbound_agent_name"] = inbound_agent.name
            
            enriched_calls.append(call_dict)
        
        return enriched_calls
        
    except Exception as e:
        logger.error(f"Error listing calls: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{call_id}", response_model=CallResponse)
async def get_call(call_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific call"""
    try:
        # Use the Call model which has proper RetellAI integration
        query = select(Call).where(Call.id == call_id)
        result = await db.execute(query)
        call = result.scalar_one_or_none()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        return call
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting call {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=CallResponse, status_code=201)
async def create_call(
    call_data: CallCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new call record"""
    try:
        # Handle agent-to-agent calls separately
        if call_data.direction == "agent_to_agent" or getattr(call_data, 'call_type', None) == 'agent_to_agent':
            return await create_agent_to_agent_call(call_data, db)
        
        # Create call record in calls table (RetellAI integrated)
        db_call = Call(
            direction=call_data.direction,
            from_number=call_data.from_number,
            to_number=call_data.to_number,
            status="registered",  # Initial status
            created_at=datetime.utcnow()
        )
        
        db.add(db_call)
        await db.commit()
        await db.refresh(db_call)
        
        logger.info(f"Created call record {db_call.id}")
        return db_call
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating call: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

async def create_agent_to_agent_call(call_data: CallCreate, db: AsyncSession) -> CallResponse:
    """Create an agent-to-agent call"""
    # Get caller agent
    caller_query = select(RetellAgent).where(RetellAgent.id == call_data.caller_agent_id)
    caller_result = await db.execute(caller_query)
    caller_agent = caller_result.scalar_one_or_none()
    
    if not caller_agent:
        raise HTTPException(status_code=404, detail="Caller agent not found")
    
    # Get inbound agent
    inbound_query = select(RetellAgent).where(RetellAgent.id == call_data.inbound_agent_id)
    inbound_result = await db.execute(inbound_query)
    inbound_agent = inbound_result.scalar_one_or_none()
    
    if not inbound_agent:
        raise HTTPException(status_code=404, detail="Inbound agent not found")
    
    # Get phone numbers for both agents
    caller_phone_query = select(PhoneNumber).where(
        PhoneNumber.agent_id == call_data.caller_agent_id,
        PhoneNumber.is_active == True
    )
    caller_phone_result = await db.execute(caller_phone_query)
    caller_phone = caller_phone_result.scalar_one_or_none()
    
    inbound_phone_query = select(PhoneNumber).where(
        PhoneNumber.agent_id == call_data.inbound_agent_id,
        PhoneNumber.is_active == True
    )
    inbound_phone_result = await db.execute(inbound_phone_query)
    inbound_phone = inbound_phone_result.scalar_one_or_none()
    
    if not caller_phone:
        raise HTTPException(status_code=400, detail="No phone number assigned to caller agent")
    if not inbound_phone:
        raise HTTPException(status_code=400, detail="No phone number assigned to inbound agent")
    
    # Make agent-to-agent call via RetellAI
    retell_response = await retell_service.make_agent_to_agent_call(
        caller_agent_id=caller_agent.retell_agent_id,
        inbound_agent_id=inbound_agent.retell_agent_id,
        from_number=caller_phone.phone_number,
        to_number=inbound_phone.phone_number
    )
    
    # Store call in database
    db_call = Call(
        retell_call_id=retell_response["call_id"],
        caller_agent_id=call_data.caller_agent_id,
        inbound_agent_id=call_data.inbound_agent_id,
        phone_number_id=caller_phone.id,
        from_number=caller_phone.phone_number,
        to_number=inbound_phone.phone_number,
        direction="agent_to_agent",
        status="registered",
        call_metadata={
            "initiated_via": "api",
            "call_type": "agent_to_agent",
            "caller_agent_name": caller_agent.name,
            "inbound_agent_name": inbound_agent.name
        }
    )
    
    db.add(db_call)
    await db.commit()
    await db.refresh(db_call)
    
    logger.info(f"Created agent-to-agent call {db_call.id} between {caller_agent.name} and {inbound_agent.name}")
    return db_call

@router.get("/{call_id}/sync-retell")
async def sync_call_with_retell(call_id: int, db: AsyncSession = Depends(get_db)):
    """Sync call data with RetellAI"""
    try:
        # Get local call
        query = select(Call).where(Call.id == call_id)
        result = await db.execute(query)
        call = result.scalar_one_or_none()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        # Get call data from RetellAI
        retell_call_data = await retell_service.get_call(call.retell_call_id)
        
        # Update local database with RetellAI data
        update_data = {}
        if retell_call_data.get("start_timestamp"):
            update_data["start_timestamp"] = datetime.fromisoformat(
                retell_call_data["start_timestamp"].replace('Z', '+00:00')
            )
        if retell_call_data.get("end_timestamp"):
            update_data["end_timestamp"] = datetime.fromisoformat(
                retell_call_data["end_timestamp"].replace('Z', '+00:00')
            )
        if retell_call_data.get("call_length_ms"):
            update_data["duration_ms"] = str(retell_call_data["call_length_ms"])
        if retell_call_data.get("recording_url"):
            update_data["recording_url"] = retell_call_data["recording_url"]
        if retell_call_data.get("transcript"):
            update_data["transcript"] = retell_call_data["transcript"]
        if retell_call_data.get("call_analysis"):
            update_data["call_analysis"] = retell_call_data["call_analysis"]
        if retell_call_data.get("call_status"):
            update_data["status"] = retell_call_data["call_status"]
        
        if update_data:
            await db.execute(
                update(Call)
                .where(Call.id == call_id)
                .values(**update_data)
            )
            await db.commit()
            await db.refresh(call)
        
        return {
            "local_call": {
                "id": call.id,
                "retell_call_id": call.retell_call_id,
                "status": call.status,
                "duration_ms": call.duration_ms,
                "updated_at": call.created_at
            },
            "retell_call": retell_call_data,
            "sync_status": "updated" if update_data else "no_changes_needed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing call {call_id} with RetellAI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sync-all/retell")
async def sync_all_calls_with_retell(db: AsyncSession = Depends(get_db)):
    """Sync all recent calls with RetellAI"""
    try:
        # Get recent calls from RetellAI
        retell_calls = await retell_service.list_calls(limit=100, sort_order="desc")
        
        synced_count = 0
        updated_count = 0
        
        for retell_call in retell_calls:
            retell_call_id = retell_call.get("call_id")
            if not retell_call_id:
                continue
            
            # Check if call exists locally
            query = select(Call).where(Call.retell_call_id == retell_call_id)
            result = await db.execute(query)
            existing_call = result.scalar_one_or_none()
            
            if existing_call:
                # Update existing call with RetellAI data
                update_data = {}
                if retell_call.get("call_length_ms"):
                    update_data["duration_ms"] = str(retell_call["call_length_ms"])
                if retell_call.get("recording_url"):
                    update_data["recording_url"] = retell_call["recording_url"]
                if retell_call.get("transcript"):
                    update_data["transcript"] = retell_call["transcript"]
                if retell_call.get("call_analysis"):
                    update_data["call_analysis"] = retell_call["call_analysis"]
                if retell_call.get("call_status"):
                    update_data["status"] = retell_call["call_status"]
                
                if update_data:
                    await db.execute(
                        update(Call)
                        .where(Call.retell_call_id == retell_call_id)
                        .values(**update_data)
                    )
                    updated_count += 1
            else:
                # Create new call record (for calls initiated outside our system)
                new_call = Call(
                    retell_call_id=retell_call_id,
                    from_number=retell_call.get("from_number", ""),
                    to_number=retell_call.get("to_number", ""),
                    direction=retell_call.get("direction", "unknown"),
                    status=retell_call.get("call_status", "unknown"),
                    duration_ms=retell_call.get("call_length_ms"),
                    recording_url=retell_call.get("recording_url"),
                    transcript=retell_call.get("transcript"),
                    call_analysis=retell_call.get("call_analysis"),
                    metadata={"synced_from_retell": True}
                )
                
                # Try to match to an agent
                agent_id = retell_call.get("agent_id")
                if agent_id:
                    agent_query = select(RetellAgent).where(RetellAgent.retell_agent_id == agent_id)
                    agent_result = await db.execute(agent_query)
                    agent = agent_result.scalar_one_or_none()
                    if agent:
                        new_call.agent_id = agent.id
                
                db.add(new_call)
                synced_count += 1
        
        await db.commit()
        
        logger.info(f"Synced {synced_count} new calls, updated {updated_count} existing")
        return {
            "message": "Calls synced successfully",
            "new_count": synced_count,
            "updated_count": updated_count,
            "total_retell_calls": len(retell_calls)
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error syncing calls: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/webhook/retell/test")
async def test_retell_webhook():
    """Test endpoint to verify webhook connectivity"""
    return {
        "status": "webhook_endpoint_active",
        "message": "RetellAI webhook endpoint is accessible",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": "/api/v1/calls/webhook/retell",
        "websocket": "/api/v1/calls/ws/transcript/{call_id}",
        "supported_events": [
            "call_started",
            "call_ended", 
            "agent_response",
            "user_speech",
            "tool_call",
            "speech_detected"
        ]
    }

@router.post("/webhook/retell")
async def retell_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Enhanced webhook endpoint for RetellAI events with real-time transcript streaming"""
    try:
        # Get the raw body for signature verification if needed
        body = await request.body()
        
        # Parse webhook data
        webhook_data = await request.json()
        event_type = webhook_data.get("event")
        call_id = webhook_data.get("data", {}).get("call_id")
        
        if not event_type or not call_id:
            logger.warning(f"Invalid webhook data: {webhook_data}")
            return {"status": "ignored", "reason": "missing_required_fields"}
        
        logger.info(f"Received RetellAI webhook: {event_type} for call {call_id}")
        
        # Find the call in our database
        query = select(Call).where(Call.retell_call_id == call_id)
        result = await db.execute(query)
        call = result.scalar_one_or_none()
        
        if call:
            # Create call event
            call_event = CallEvent(
                call_id=call.id,
                event_type=event_type,
                data=webhook_data
            )
            db.add(call_event)
            
            # Handle different event types
            if event_type == "call_started":
                await db.execute(
                    update(Call)
                    .where(Call.id == call.id)
                    .values(
                        status="ongoing",
                        start_timestamp=datetime.utcnow()
                    )
                )
                
                # Broadcast call started event to WebSocket clients
                await manager.broadcast_to_call(
                    json.dumps({
                        "type": "call_started",
                        "call_id": call_id,
                        "data": webhook_data.get("data", {}),
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    call.retell_call_id
                )
                
            elif event_type == "call_ended":
                call_data = webhook_data.get("data", {})
                await db.execute(
                    update(Call)
                    .where(Call.id == call.id)
                    .values(
                        status="ended",
                        end_timestamp=datetime.utcnow(),
                        duration_ms=call_data.get("call_length_ms"),
                        recording_url=call_data.get("recording_url"),
                        transcript=call_data.get("transcript")
                    )
                )
                
                # Broadcast call ended event to WebSocket clients
                await manager.broadcast_to_call(
                    json.dumps({
                        "type": "call_ended",
                        "call_id": call_id,
                        "data": call_data,
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    call.retell_call_id
                )
                
            elif event_type == "agent_response":
                # Real-time agent response streaming
                response_data = webhook_data.get("data", {})
                await manager.broadcast_to_call(
                    json.dumps({
                        "type": "transcript_update",
                        "call_id": call_id,
                        "data": {
                            "speaker": "agent",
                            "content": response_data.get("response", ""),
                            "timestamp": response_data.get("timestamp", datetime.utcnow().isoformat()),
                            "is_final": response_data.get("is_final", True)
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    call.retell_call_id
                )
                
            elif event_type == "user_speech":
                # Real-time user speech streaming
                speech_data = webhook_data.get("data", {})
                await manager.broadcast_to_call(
                    json.dumps({
                        "type": "transcript_update",
                        "call_id": call_id,
                        "data": {
                            "speaker": "human",
                            "content": speech_data.get("transcript", ""),
                            "timestamp": speech_data.get("timestamp", datetime.utcnow().isoformat()),
                            "is_final": speech_data.get("is_final", True)
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    call.retell_call_id
                )
                
            elif event_type == "tool_call":
                # Tool call events (for ticket creation, customer lookup, etc.)
                tool_data = webhook_data.get("data", {})
                await manager.broadcast_to_call(
                    json.dumps({
                        "type": "tool_call",
                        "call_id": call_id,
                        "data": {
                            "function_name": tool_data.get("tool_call", {}).get("function", {}).get("name"),
                            "arguments": tool_data.get("tool_call", {}).get("function", {}).get("arguments"),
                            "result": tool_data.get("result"),
                            "timestamp": tool_data.get("timestamp", datetime.utcnow().isoformat())
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    call.retell_call_id
                )
                
            elif event_type == "speech_detected":
                # Speech detection events
                speech_data = webhook_data.get("data", {})
                await manager.broadcast_to_call(
                    json.dumps({
                        "type": "speech_detected",
                        "call_id": call_id,
                        "data": {
                            "speaker": speech_data.get("speaker", "unknown"),
                            "detected": speech_data.get("detected", True)
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    call.retell_call_id
                )
                
            else:
                # Broadcast other events (generic handling)
                await manager.broadcast_to_call(
                    json.dumps({
                        "type": event_type,
                        "call_id": call_id,
                        "data": webhook_data.get("data", {}),
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    call.retell_call_id
                )
            
            await db.commit()
            
            return {
                "status": "processed",
                "call_id": call.id,
                "event_type": event_type,
                "broadcast": "sent"
            }
        else:
            logger.warning(f"Call not found in database: {call_id}")
            return {
                "status": "call_not_found",
                "retell_call_id": call_id,
                "event_type": event_type
            }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error processing RetellAI webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/today")
async def get_today_call_stats(db: AsyncSession = Depends(get_db)):
    """Get call statistics for today"""
    try:
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        
        # Total calls today
        total_query = select(func.count(Call.id)).where(
            and_(
                Call.created_at >= today,
                Call.created_at < tomorrow
            )
        )
        total_result = await db.execute(total_query)
        total_calls = total_result.scalar()
        
        # Active calls
        active_query = select(func.count(Call.id)).where(Call.status == "ongoing")
        active_result = await db.execute(active_query)
        active_calls = active_result.scalar()
        
        # Completed calls today
        completed_query = select(func.count(Call.id)).where(
            and_(
                Call.created_at >= today,
                Call.created_at < tomorrow,
                Call.status == "ended"
            )
        )
        completed_result = await db.execute(completed_query)
        completed_calls = completed_result.scalar()
        
        # Average duration (in seconds)
        avg_duration_query = select(func.avg(Call.duration_ms)).where(
            and_(
                Call.created_at >= today,
                Call.created_at < tomorrow,
                Call.duration_ms.isnot(None)
            )
        )
        avg_duration_result = await db.execute(avg_duration_query)
        avg_duration_ms = avg_duration_result.scalar() or 0
        avg_duration_seconds = int(avg_duration_ms / 1000) if avg_duration_ms else 0
        
        return {
            "date": today.isoformat(),
            "total_calls": total_calls,
            "active_calls": active_calls,
            "completed_calls": completed_calls,
            "average_duration_seconds": avg_duration_seconds,
            "success_rate": round((completed_calls / total_calls * 100), 2) if total_calls > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting call stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@router.get("/{call_id}/live-status")
async def get_live_call_status(call_id: int, db: AsyncSession = Depends(get_db)):
    """Get live call status and recent transcript updates for E2E tuning"""
    try:
        # Get local call
        query = select(Call).where(Call.id == call_id)
        result = await db.execute(query)
        call = result.scalar_one_or_none()
        
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        # Get recent call events for live updates
        events_query = select(CallEvent).where(
            CallEvent.call_id == call_id
        ).order_by(desc(CallEvent.timestamp)).limit(50)
        events_result = await db.execute(events_query)
        events = events_result.scalars().all()
        
        # Get latest data from RetellAI if call is ongoing
        retell_data = None
        if call.status == "ongoing" and call.retell_call_id:
            try:
                retell_data = await retell_service.get_call(call.retell_call_id)
            except Exception as e:
                logger.warning(f"Failed to get RetellAI data for call {call_id}: {str(e)}")
        
        return {
            "call": {
                "id": call.id,
                "retell_call_id": call.retell_call_id,
                "status": call.status,
                "duration_ms": call.duration_ms,
                "start_timestamp": call.start_timestamp,
                "end_timestamp": call.end_timestamp,
                "transcript": call.transcript,
                "call_analysis": call.call_analysis
            },
            "recent_events": [
                {
                    "id": event.id,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp,
                    "data": event.data
                } for event in events
            ],
            "retell_live_data": retell_data,
            "websocket_available": True,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting live call status for {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 