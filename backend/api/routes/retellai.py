from fastapi import APIRouter, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime
from loguru import logger

from ..database import get_db, Call, CallEvent, RetellAgent
from ..services.retell_service import retell_service
from ..schemas import CallBase

router = APIRouter()

# WebSocket connection manager (duplicate from calls.py for this endpoint)
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

# Use the same manager instance as calls.py by importing it
try:
    from .calls import manager
except ImportError:
    # Fallback: create our own manager if import fails
    manager = ConnectionManager()

@router.post("/agent-level-webhook")
async def retellai_agent_level_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    RetellAI agent-level webhook endpoint for real-time transcript streaming
    This is the endpoint your RETELLAI_AGENT_WEBHOOK_URL points to
    """
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
        
        logger.info(f"Received RetellAI agent-level webhook: {event_type} for call {call_id}")
        
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
            
            # Handle different event types with real-time streaming
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
                "broadcast": "sent",
                "webhook_type": "agent-level"
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
        logger.error(f"Error processing RetellAI agent-level webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent-level-webhook/test")
async def test_agent_level_webhook():
    """Test endpoint to verify agent-level webhook connectivity"""
    return {
        "status": "agent_level_webhook_active",
        "message": "RetellAI agent-level webhook endpoint is accessible",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": "/api/v1/retellai/agent-level-webhook",
        "websocket": "/api/v1/calls/ws/transcript/{call_id}",
        "webhook_type": "agent-level",
        "supported_events": [
            "call_started",
            "call_ended", 
            "agent_response",
            "user_speech",
            "tool_call",
            "speech_detected"
        ]
    } 

@router.post("/conversation-flows")
async def create_conversation_flow(request: Request, db: AsyncSession = Depends(get_db)):
    """Create a new RetellAI conversation flow"""
    try:
        flow_data = await request.json()
        result = await retell_service.create_conversation_flow(flow_data)
        return result
    except Exception as e:
        logger.error(f"Error creating conversation flow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation-flows")
async def list_conversation_flows(db: AsyncSession = Depends(get_db)):
    """List all RetellAI conversation flows"""
    try:
        result = await retell_service.list_conversation_flows()
        return result
    except Exception as e:
        logger.error(f"Error listing conversation flows: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation-flows/{flow_id}")
async def get_conversation_flow(flow_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific RetellAI conversation flow"""
    try:
        result = await retell_service.get_conversation_flow(flow_id)
        return result
    except Exception as e:
        logger.error(f"Error getting conversation flow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/conversation-flows/{flow_id}")
async def update_conversation_flow(flow_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Update a RetellAI conversation flow"""
    try:
        flow_data = await request.json()
        result = await retell_service.update_conversation_flow(flow_id, flow_data)
        return result
    except Exception as e:
        logger.error(f"Error updating conversation flow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversation-flows/{flow_id}")
async def delete_conversation_flow(flow_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a RetellAI conversation flow"""
    try:
        result = await retell_service.delete_conversation_flow(flow_id)
        return {"success": result, "message": "Conversation flow deleted successfully" if result else "Failed to delete conversation flow"}
    except Exception as e:
        logger.error(f"Error deleting conversation flow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 