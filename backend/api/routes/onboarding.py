from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from loguru import logger
import json
import asyncio

from ..database import (
    get_db, OnboardingSession, OrganizationProfile, MSPIntegration,
    InternalPolicy, EscalationProcedure, BusinessHours, OnboardingTranscript
)
from ..services.retell_service import retell_service
from ..schemas import (
    OnboardingSessionCreate, OnboardingSessionResponse, OnboardingSessionUpdate,
    StartOnboardingCallRequest, StartOnboardingCallResponse,
    AddTranscriptMessageRequest, UpdateSOPDataRequest, OnboardingExportResponse,
    OrganizationProfileData, MSPIntegrationData, InternalPolicyData,
    EscalationProcedureData, BusinessHoursData, OnboardingTranscriptMessage
)

router = APIRouter()

# Enhanced WebSocket connection manager for real-time collaborative editing
class OnboardingConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}  # session_id -> {user_id: {"websocket": ws, "user_info": {...}}}
        self.session_users: dict = {}  # session_id -> set of user_ids
        self.user_activities: dict = {}  # user_id -> {"session_id": str, "last_seen": datetime, "editing": str}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str = "anonymous", user_info: dict = None):
        await websocket.accept()
        
        # Initialize session connections if not exists
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
            self.session_users[session_id] = set()
        
        # Store connection with user info
        self.active_connections[session_id][user_id] = {
            "websocket": websocket,
            "user_info": user_info or {"name": f"User {user_id}", "avatar": None},
            "connected_at": datetime.utcnow(),
            "editing": None  # Currently editing field
        }
        
        # Track user activity
        self.session_users[session_id].add(user_id)
        self.user_activities[user_id] = {
            "session_id": session_id,
            "last_seen": datetime.utcnow(),
            "editing": None
        }
        
        # Notify other users about new connection
        await self.broadcast_to_session(session_id, {
            "type": "user_connected",
            "user_id": user_id,
            "user_info": self.active_connections[session_id][user_id]["user_info"],
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)
        
        # Send current session presence to new user
        await self.send_to_user(session_id, user_id, {
            "type": "session_presence",
            "users": [
                {
                    "user_id": uid,
                    "user_info": conn["user_info"],
                    "connected_at": conn["connected_at"].isoformat(),
                    "editing": conn["editing"]
                }
                for uid, conn in self.active_connections[session_id].items()
                if uid != user_id
            ]
        })
        
        logger.info(f"User {user_id} connected to session {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str, user_id: str = None):
        if session_id in self.active_connections:
            user_to_remove = None
            
            # Find user by websocket if user_id not provided
            if user_id is None:
                for uid, conn in self.active_connections[session_id].items():
                    if conn["websocket"] == websocket:
                        user_to_remove = uid
                        break
            else:
                user_to_remove = user_id
            
            if user_to_remove and user_to_remove in self.active_connections[session_id]:
                del self.active_connections[session_id][user_to_remove]
                self.session_users[session_id].discard(user_to_remove)
                
                # Clean up user activity
                if user_to_remove in self.user_activities:
                    del self.user_activities[user_to_remove]
                
                # Notify other users about disconnection
                asyncio.create_task(self.broadcast_to_session(session_id, {
                    "type": "user_disconnected",
                    "user_id": user_to_remove,
                    "timestamp": datetime.utcnow().isoformat()
                }))
                
                # Clean up empty session
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
                    del self.session_users[session_id]
                
                logger.info(f"User {user_to_remove} disconnected from session {session_id}")
    
    async def broadcast_to_session(self, session_id: str, message: dict, exclude_user: str = None):
        """Broadcast message to all users in a session, optionally excluding one user"""
        if session_id in self.active_connections:
            disconnected_users = []
            
            for user_id, connection in self.active_connections[session_id].items():
                if exclude_user and user_id == exclude_user:
                    continue
                    
                try:
                    await connection["websocket"].send_text(json.dumps(message))
                    # Update last seen
                    if user_id in self.user_activities:
                        self.user_activities[user_id]["last_seen"] = datetime.utcnow()
                except Exception as e:
                    logger.warning(f"Failed to send message to user {user_id}: {e}")
                    disconnected_users.append(user_id)
            
            # Clean up disconnected users
            for user_id in disconnected_users:
                self.disconnect(None, session_id, user_id)
    
    async def send_to_user(self, session_id: str, user_id: str, message: dict):
        """Send message to specific user"""
        if (session_id in self.active_connections and 
            user_id in self.active_connections[session_id]):
            try:
                await self.active_connections[session_id][user_id]["websocket"].send_text(json.dumps(message))
                # Update last seen
                if user_id in self.user_activities:
                    self.user_activities[user_id]["last_seen"] = datetime.utcnow()
            except Exception as e:
                logger.warning(f"Failed to send message to user {user_id}: {e}")
                self.disconnect(None, session_id, user_id)
    
    async def set_user_editing(self, session_id: str, user_id: str, field: str = None):
        """Set what field a user is currently editing"""
        if (session_id in self.active_connections and 
            user_id in self.active_connections[session_id]):
            
            self.active_connections[session_id][user_id]["editing"] = field
            if user_id in self.user_activities:
                self.user_activities[user_id]["editing"] = field
            
            # Broadcast editing status to other users
            await self.broadcast_to_session(session_id, {
                "type": "user_editing",
                "user_id": user_id,
                "field": field,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_user=user_id)
    
    def get_session_users(self, session_id: str) -> list:
        """Get list of users in a session"""
        if session_id not in self.active_connections:
            return []
        
        return [
            {
                "user_id": user_id,
                "user_info": conn["user_info"],
                "connected_at": conn["connected_at"].isoformat(),
                "editing": conn["editing"],
                "last_seen": self.user_activities.get(user_id, {}).get("last_seen", datetime.utcnow()).isoformat()
            }
            for user_id, conn in self.active_connections[session_id].items()
        ]

manager = OnboardingConnectionManager()

@router.post("/sessions", response_model=OnboardingSessionResponse, status_code=201)
async def create_onboarding_session(
    session_data: OnboardingSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new onboarding session"""
    try:
        # Create the session
        session = OnboardingSession(
            user_id=session_data.user_id,
            status='active'
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        # Create empty related records
        organization = OrganizationProfile(session_id=session.id)
        msp_integration = MSPIntegration(session_id=session.id)
        business_hours = BusinessHours(session_id=session.id)
        
        db.add_all([organization, msp_integration, business_hours])
        await db.commit()
        
        logger.info(f"Created onboarding session {session.id} for user {session_data.user_id}")
        
        # Return the session with nested data
        return await get_session_with_data(session.id, db)
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating onboarding session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}", response_model=OnboardingSessionResponse)
async def get_onboarding_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get an onboarding session with all related data"""
    try:
        return await get_session_with_data(session_id, db)
    except Exception as e:
        logger.error(f"Error getting onboarding session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=List[OnboardingSessionResponse])
async def list_onboarding_sessions(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List onboarding sessions with optional filtering"""
    try:
        query = select(OnboardingSession)
        
        if user_id:
            query = query.where(OnboardingSession.user_id == user_id)
        if status:
            query = query.where(OnboardingSession.status == status)
        
        query = query.order_by(OnboardingSession.created_at.desc()).limit(limit)
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        # Get full data for each session
        response_sessions = []
        for session in sessions:
            session_data = await get_session_with_data(str(session.id), db)
            response_sessions.append(session_data)
        
        return response_sessions
        
    except Exception as e:
        logger.error(f"Error listing onboarding sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/sessions/{session_id}", response_model=OnboardingSessionResponse)
async def update_onboarding_session(
    session_id: str,
    update_data: OnboardingSessionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an onboarding session and its related data"""
    try:
        # Get the session
        session_query = select(OnboardingSession).where(OnboardingSession.id == session_id)
        session_result = await db.execute(session_query)
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update session fields
        if update_data.status:
            session.status = update_data.status
        if update_data.session_data:
            session.session_data = update_data.session_data
        session.updated_at = datetime.utcnow()
        
        # Update organization profile
        if update_data.organization:
            await update_organization_profile(session_id, update_data.organization, db)
        
        # Update MSP integration
        if update_data.msp_integration:
            await update_msp_integration(session_id, update_data.msp_integration, db)
        
        # Update policies
        if update_data.policies is not None:
            await update_policies(session_id, update_data.policies, db)
        
        # Update escalations
        if update_data.escalations is not None:
            await update_escalations(session_id, update_data.escalations, db)
        
        # Update business hours
        if update_data.business_hours:
            await update_business_hours(session_id, update_data.business_hours, db)
        
        await db.commit()
        
        # Broadcast update to connected clients
        await manager.broadcast_to_session(session_id, {
            "type": "session_updated",
            "session_id": session_id,
            "data": update_data.dict(exclude_none=True),
            "timestamp": datetime.utcnow().isoformat(),
            "updated_by": "system"  # In production, get from auth context
        })
        
        logger.info(f"Updated onboarding session {session_id}")
        
        return await get_session_with_data(session_id, db)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating onboarding session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/start-call", response_model=StartOnboardingCallResponse)
async def start_onboarding_call(
    session_id: str,
    call_request: StartOnboardingCallRequest,
    db: AsyncSession = Depends(get_db)
):
    """Start an onboarding call with Retell AI"""
    try:
        # Get the session
        session_query = select(OnboardingSession).where(OnboardingSession.id == session_id)
        session_result = await db.execute(session_query)
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # For now, we'll simulate the call creation since we need to integrate with RetellAI
        # In production, this would create a real RetellAI call
        mock_call_id = f"call_{session_id}_{int(datetime.utcnow().timestamp())}"
        
        # Update session with call information
        session.retell_call_id = mock_call_id
        session.status = 'call_active'
        session.updated_at = datetime.utcnow()
        
        # Add system message to transcript
        await add_transcript_message(
            session_id,
            "system",
            "Onboarding call started - SOP Builder Assistant is ready to help you document your business processes.",
            "system",
            {"event": "call_started"},
            db
        )
        
        await db.commit()
        
        # Broadcast call started event to all connected users
        await manager.broadcast_to_session(session_id, {
            "type": "call_started",
            "session_id": session_id,
            "call_id": mock_call_id,
            "retell_call_id": mock_call_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "call_active"
        })
        
        logger.info(f"Started onboarding call for session {session_id}")
        
        return StartOnboardingCallResponse(
            session_id=session_id,
            call_id=mock_call_id,
            retell_call_id=mock_call_id,
            status="call_active"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error starting onboarding call for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/end-call")
async def end_onboarding_call(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """End an onboarding call"""
    try:
        # Get the session
        session_query = select(OnboardingSession).where(OnboardingSession.id == session_id)
        session_result = await db.execute(session_query)
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update session status
        session.status = 'call_ended'
        session.updated_at = datetime.utcnow()
        
        # Add system message to transcript
        await add_transcript_message(
            session_id,
            "system",
            "Onboarding call ended. Your SOPs have been saved and can be exported.",
            "system",
            {"event": "call_ended"},
            db
        )
        
        await db.commit()
        
        # Broadcast call ended event to all connected users
        await manager.broadcast_to_session(session_id, {
            "type": "call_ended",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "call_ended"
        })
        
        logger.info(f"Ended onboarding call for session {session_id}")
        
        return {"status": "call_ended", "session_id": session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error ending onboarding call for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/transcript")
async def add_transcript_message_endpoint(
    session_id: str,
    message: AddTranscriptMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """Add a message to the onboarding transcript"""
    try:
        await add_transcript_message(
            session_id,
            message.speaker,
            message.content,
            message.message_type,
            message.extra_data,
            db
        )
        
        # Broadcast transcript update to all connected users
        await manager.broadcast_to_session(session_id, {
            "type": "transcript_update",
            "session_id": session_id,
            "message": {
                "id": f"msg_{datetime.utcnow().timestamp()}",
                "speaker": message.speaker,
                "content": message.content,
                "timestamp": datetime.utcnow().isoformat(),
                "message_type": message.message_type,
                "extra_data": message.extra_data,
                "system": message.message_type == 'system',
                "sop_update": message.extra_data.get('sop_update') if message.extra_data else None
            }
        })
        
        return {"status": "message_added", "session_id": session_id}
        
    except Exception as e:
        logger.error(f"Error adding transcript message to session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/sop-update")
async def update_sop_data(
    session_id: str,
    sop_update: UpdateSOPDataRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update SOP data for a specific area"""
    try:
        if sop_update.area == "organization":
            org_data = OrganizationProfileData(**sop_update.data)
            await update_organization_profile(session_id, org_data, db)
        elif sop_update.area == "msp_integration":
            msp_data = MSPIntegrationData(**sop_update.data)
            await update_msp_integration(session_id, msp_data, db)
        elif sop_update.area == "business_hours":
            hours_data = BusinessHoursData(**sop_update.data)
            await update_business_hours(session_id, hours_data, db)
        elif sop_update.area == "policies":
            if "policies" in sop_update.data:
                policies_data = [InternalPolicyData(**p) for p in sop_update.data["policies"]]
                await update_policies(session_id, policies_data, db)
        elif sop_update.area == "escalations":
            if "escalations" in sop_update.data:
                escalations_data = [EscalationProcedureData(**e) for e in sop_update.data["escalations"]]
                await update_escalations(session_id, escalations_data, db)
        
        await db.commit()
        
        # Add system message about the update
        if sop_update.description:
            await add_transcript_message(
                session_id,
                "system",
                f"SOP Updated: {sop_update.description}",
                "sop_update",
                {"area": sop_update.area, "description": sop_update.description},
                db
            )
        
        # Broadcast SOP update to all connected users
        await manager.broadcast_to_session(session_id, {
            "type": "sop_updated",
            "session_id": session_id,
            "area": sop_update.area,
            "data": sop_update.data,
            "description": sop_update.description,
            "timestamp": datetime.utcnow().isoformat(),
            "updated_by": "system"  # In production, get from auth context
        })
        
        return {"status": "sop_updated", "area": sop_update.area, "session_id": session_id}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating SOP data for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/export", response_model=OnboardingExportResponse)
async def export_sop_data(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Export all SOP data for a session"""
    try:
        session_data = await get_session_with_data(session_id, db)
        
        return OnboardingExportResponse(
            session_id=session_id,
            organization=session_data.organization,
            msp_integration=session_data.msp_integration,
            policies=session_data.policies,
            escalations=session_data.escalations,
            business_hours=session_data.business_hours,
            exported_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error exporting SOP data for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_onboarding_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an onboarding session and all related data"""
    try:
        # Delete all related records (cascade should handle this, but let's be explicit)
        await db.execute(delete(OnboardingTranscript).where(OnboardingTranscript.session_id == session_id))
        await db.execute(delete(InternalPolicy).where(InternalPolicy.session_id == session_id))
        await db.execute(delete(EscalationProcedure).where(EscalationProcedure.session_id == session_id))
        await db.execute(delete(BusinessHours).where(BusinessHours.session_id == session_id))
        await db.execute(delete(MSPIntegration).where(MSPIntegration.session_id == session_id))
        await db.execute(delete(OrganizationProfile).where(OrganizationProfile.session_id == session_id))
        await db.execute(delete(OnboardingSession).where(OnboardingSession.id == session_id))
        
        await db.commit()
        
        logger.info(f"Deleted onboarding session {session_id}")
        
        return {"status": "deleted", "session_id": session_id}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting onboarding session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str, user_id: str = "anonymous"):
    """Enhanced WebSocket endpoint for real-time collaborative editing"""
    user_info = {"name": f"User {user_id}", "avatar": None}  # In production, get from auth context
    
    await manager.connect(websocket, session_id, user_id, user_info)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_websocket_message(session_id, user_id, message)
            except json.JSONDecodeError:
                await manager.send_to_user(session_id, user_id, {
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await manager.send_to_user(session_id, user_id, {
                    "type": "error",
                    "message": "Failed to process message"
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id, user_id)
        logger.info(f"WebSocket disconnected for user {user_id} in session {session_id}")

async def handle_websocket_message(session_id: str, user_id: str, message: dict):
    """Handle incoming WebSocket messages from clients"""
    message_type = message.get("type")
    
    if message_type == "ping":
        # Heartbeat/keep-alive
        await manager.send_to_user(session_id, user_id, {"type": "pong"})
    
    elif message_type == "start_editing":
        # User started editing a field
        field = message.get("field")
        await manager.set_user_editing(session_id, user_id, field)
    
    elif message_type == "stop_editing":
        # User stopped editing
        await manager.set_user_editing(session_id, user_id, None)
    
    elif message_type == "typing":
        # User is typing (for live cursor/typing indicators)
        field = message.get("field")
        content = message.get("content", "")
        await manager.broadcast_to_session(session_id, {
            "type": "user_typing",
            "user_id": user_id,
            "field": field,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)
    
    elif message_type == "cursor_position":
        # Real-time cursor position sharing
        field = message.get("field")
        position = message.get("position", 0)
        await manager.broadcast_to_session(session_id, {
            "type": "cursor_update",
            "user_id": user_id,
            "field": field,
            "position": position,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)
    
    elif message_type == "request_presence":
        # Client requesting current presence info
        users = manager.get_session_users(session_id)
        await manager.send_to_user(session_id, user_id, {
            "type": "session_presence",
            "users": [u for u in users if u["user_id"] != user_id]
        })
    
    else:
        logger.warning(f"Unknown WebSocket message type: {message_type}")

@router.get("/sessions/{session_id}/users")
async def get_session_users(session_id: str):
    """Get list of users currently in a session"""
    users = manager.get_session_users(session_id)
    return {"users": users, "count": len(users)}

# Helper functions
async def get_session_with_data(session_id: str, db: AsyncSession) -> OnboardingSessionResponse:
    """Get a session with all related data"""
    # Get session
    session_query = select(OnboardingSession).where(OnboardingSession.id == session_id)
    session_result = await db.execute(session_query)
    session = session_result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get organization profile
    org_query = select(OrganizationProfile).where(OrganizationProfile.session_id == session_id)
    org_result = await db.execute(org_query)
    organization = org_result.scalar_one_or_none()
    
    # Get MSP integration
    msp_query = select(MSPIntegration).where(MSPIntegration.session_id == session_id)
    msp_result = await db.execute(msp_query)
    msp_integration = msp_result.scalar_one_or_none()
    
    # Get policies
    policies_query = select(InternalPolicy).where(InternalPolicy.session_id == session_id)
    policies_result = await db.execute(policies_query)
    policies = policies_result.scalars().all()
    
    # Get escalations
    escalations_query = select(EscalationProcedure).where(EscalationProcedure.session_id == session_id)
    escalations_result = await db.execute(escalations_query)
    escalations = escalations_result.scalars().all()
    
    # Get business hours
    hours_query = select(BusinessHours).where(BusinessHours.session_id == session_id)
    hours_result = await db.execute(hours_query)
    business_hours = hours_result.scalar_one_or_none()
    
    # Get transcript
    transcript_query = select(OnboardingTranscript).where(
        OnboardingTranscript.session_id == session_id
    ).order_by(OnboardingTranscript.timestamp)
    transcript_result = await db.execute(transcript_query)
    transcript_messages = transcript_result.scalars().all()
    
    # Build response
    return OnboardingSessionResponse(
        id=str(session.id),
        user_id=session.user_id,
        retell_call_id=session.retell_call_id,
        status=session.status,
        session_data=session.session_data,
        created_at=session.created_at,
        updated_at=session.updated_at,
        completed_at=session.completed_at,
        organization=OrganizationProfileData(
            name=organization.name if organization else None,
            industry=organization.industry if organization else None,
            size=organization.size if organization else None,
            description=organization.description if organization else None
        ) if organization else None,
        msp_integration=MSPIntegrationData(
            platform=msp_integration.platform if msp_integration else None,
            workflows=msp_integration.workflows if msp_integration else []
        ) if msp_integration else None,
        policies=[
            InternalPolicyData(
                category=p.category,
                description=p.description,
                priority=p.priority
            ) for p in policies
        ],
        escalations=[
            EscalationProcedureData(
                trigger=e.trigger,
                action=e.action,
                priority=e.priority,
                contact_info=e.contact_info
            ) for e in escalations
        ],
        business_hours=BusinessHoursData(
            standard=business_hours.standard if business_hours else None,
            emergency=business_hours.emergency if business_hours else None,
            timezone=business_hours.timezone if business_hours else None
        ) if business_hours else None,
        transcript=[
            OnboardingTranscriptMessage(
                speaker=msg.speaker,
                content=msg.content,
                timestamp=msg.timestamp,
                message_type=msg.message_type,
                extra_data=msg.extra_data
            ) for msg in transcript_messages
        ]
    )

async def add_transcript_message(
    session_id: str,
    speaker: str,
    content: str,
    message_type: str = 'transcript',
    extra_data: dict = None,
    db: AsyncSession = None
):
    """Add a message to the transcript"""
    message = OnboardingTranscript(
        session_id=session_id,
        speaker=speaker,
        content=content,
        message_type=message_type,
        extra_data=extra_data,
        timestamp=datetime.utcnow()
    )
    
    db.add(message)
    await db.commit()

async def update_organization_profile(session_id: str, data: OrganizationProfileData, db: AsyncSession):
    """Update organization profile"""
    query = select(OrganizationProfile).where(OrganizationProfile.session_id == session_id)
    result = await db.execute(query)
    org = result.scalar_one_or_none()
    
    if org:
        if data.name is not None:
            org.name = data.name
        if data.industry is not None:
            org.industry = data.industry
        if data.size is not None:
            org.size = data.size
        if data.description is not None:
            org.description = data.description
        org.updated_at = datetime.utcnow()

async def update_msp_integration(session_id: str, data: MSPIntegrationData, db: AsyncSession):
    """Update MSP integration"""
    query = select(MSPIntegration).where(MSPIntegration.session_id == session_id)
    result = await db.execute(query)
    msp = result.scalar_one_or_none()
    
    if msp:
        if data.platform is not None:
            msp.platform = data.platform
        if data.workflows is not None:
            msp.workflows = [w.dict() for w in data.workflows]
        msp.updated_at = datetime.utcnow()

async def update_business_hours(session_id: str, data: BusinessHoursData, db: AsyncSession):
    """Update business hours"""
    query = select(BusinessHours).where(BusinessHours.session_id == session_id)
    result = await db.execute(query)
    hours = result.scalar_one_or_none()
    
    if hours:
        if data.standard is not None:
            hours.standard = data.standard
        if data.emergency is not None:
            hours.emergency = data.emergency
        if data.timezone is not None:
            hours.timezone = data.timezone
        hours.updated_at = datetime.utcnow()

async def update_policies(session_id: str, policies: List[InternalPolicyData], db: AsyncSession):
    """Update internal policies"""
    # Delete existing policies
    await db.execute(delete(InternalPolicy).where(InternalPolicy.session_id == session_id))
    
    # Add new policies
    for policy_data in policies:
        policy = InternalPolicy(
            session_id=session_id,
            category=policy_data.category,
            description=policy_data.description,
            priority=policy_data.priority
        )
        db.add(policy)

async def update_escalations(session_id: str, escalations: List[EscalationProcedureData], db: AsyncSession):
    """Update escalation procedures"""
    # Delete existing escalations
    await db.execute(delete(EscalationProcedure).where(EscalationProcedure.session_id == session_id))
    
    # Add new escalations
    for escalation_data in escalations:
        escalation = EscalationProcedure(
            session_id=session_id,
            trigger=escalation_data.trigger,
            action=escalation_data.action,
            priority=escalation_data.priority,
            contact_info=escalation_data.contact_info
        )
        db.add(escalation) 