from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
import asyncio
from loguru import logger
from datetime import datetime

from ..database import get_db, Agent, RetellAgent, PhoneNumber
from ..services.retell_service import retell_service
from ..schemas import AgentCreate, AgentUpdate, AgentResponse, LegacyAgentResponse, TestCallRequest
from ..prompts.prompt_manager import prompt_manager
import uuid

router = APIRouter()

@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(
    agent_data: AgentCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create a new RetellAI agent"""
    try:
        # Create agent in RetellAI
        retell_response = await retell_service.create_agent({
            "name": agent_data.name,
            "prompt": agent_data.prompt,
            "voice_id": agent_data.voice_id,
            "llm_websocket_url": agent_data.llm_websocket_url,
            "boosted_keywords": agent_data.boosted_keywords,
            "tools": agent_data.tools,
        })
        
        # Store in database
        db_agent = RetellAgent(
            retell_agent_id=retell_response["agent_id"],
            name=agent_data.name,
            prompt=agent_data.prompt,
            voice_id=agent_data.voice_id,
            llm_websocket_url=agent_data.llm_websocket_url,
            boosted_keywords=agent_data.boosted_keywords,
            tools=agent_data.tools,
        )
        
        db.add(db_agent)
        await db.commit()
        await db.refresh(db_agent)
        
        logger.info(f"Created agent {db_agent.id} with RetellAI ID {db_agent.retell_agent_id}")
        return db_agent
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/onboarding", status_code=201)
async def create_onboarding_agent(
    agent_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Create a new onboarding agent"""
    try:
        # Generate UUID for agent ID
        agent_id = str(uuid.uuid4())
        
        # If setting as default, unset other default agents of the same type
        if agent_data.get('is_default', False):
            await db.execute(
                update(Agent)
                .where(Agent.type == 'onboarding')
                .values(is_default=False)
            )
        
        # Create agent in database
        db_agent = Agent(
            id=agent_id,
            user_id=agent_data.get('user_id', 'system'),
            name=agent_data['name'],
            voice_id=uuid.uuid4(),  # Generate a UUID for voice_id
            type='onboarding',
            is_default=agent_data.get('is_default', False),
            prompt=agent_data.get('prompt'),
            focus_areas=agent_data.get('focus_areas', []),
            created_at=datetime.utcnow(),
            hidden=False
        )
        
        db.add(db_agent)
        await db.commit()
        await db.refresh(db_agent)
        
        logger.info(f"Created onboarding agent {db_agent.id}")
        
        # Return the agent data
        return {
            'id': db_agent.id,
            'name': db_agent.name,
            'type': db_agent.type,
            'is_default': db_agent.is_default,
            'prompt': db_agent.prompt,
            'focus_areas': db_agent.focus_areas,
            'voice_id': agent_data.get('voice_id', '11labs-Adrian'),
            'active': True,
            'created_at': db_agent.created_at
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating onboarding agent: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/onboarding/{agent_id}")
async def update_onboarding_agent(
    agent_id: str,
    agent_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Update an onboarding agent"""
    try:
        # Find the agent
        query = select(Agent).where(Agent.id == agent_id, Agent.type == 'onboarding')
        result = await db.execute(query)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Onboarding agent not found")
        
        # If setting as default, unset other default agents of the same type
        if agent_data.get('is_default', False) and not agent.is_default:
            await db.execute(
                update(Agent)
                .where(Agent.type == 'onboarding', Agent.id != agent_id)
                .values(is_default=False)
            )
        
        # Update agent fields
        agent.name = agent_data.get('name', agent.name)
        agent.prompt = agent_data.get('prompt', agent.prompt)
        agent.focus_areas = agent_data.get('focus_areas', agent.focus_areas)
        agent.is_default = agent_data.get('is_default', agent.is_default)
        
        await db.commit()
        await db.refresh(agent)
        
        logger.info(f"Updated onboarding agent {agent.id}")
        
        return {
            'id': agent.id,
            'name': agent.name,
            'type': agent.type,
            'is_default': agent.is_default,
            'prompt': agent.prompt,
            'focus_areas': agent.focus_areas,
            'voice_id': agent_data.get('voice_id', '11labs-Adrian'),
            'active': True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating onboarding agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/onboarding/{agent_id}")
async def delete_onboarding_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an onboarding agent"""
    try:
        # Find the agent
        query = select(Agent).where(Agent.id == agent_id, Agent.type == 'onboarding')
        result = await db.execute(query)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Onboarding agent not found")
        
        await db.delete(agent)
        await db.commit()
        
        logger.info(f"Deleted onboarding agent {agent_id}")
        
        return {"message": "Agent deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting onboarding agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[LegacyAgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all agents"""
    try:
        query = select(Agent)
        if active_only:
            query = query.where(Agent.hidden.is_(None) | (Agent.hidden == False))
        
        # Filter by type if provided
        if type:
            query = query.where(Agent.type == type)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        agents = result.scalars().all()
        
        # Convert UUID fields to strings and add computed properties
        response_agents = []
        for agent in agents:
            agent_dict = {
                'id': agent.id,
                'user_id': agent.user_id,
                'remote_agent_id': agent.remote_agent_id,
                'remote_llm_id': agent.remote_llm_id,
                'name': agent.name,
                'voice_id': str(agent.voice_id),  # Convert UUID to string
                'first_message': agent.first_message,
                'sops': agent.sops,
                'closing_statement': agent.closing_statement,
                'created_at': agent.created_at,
                'hidden': agent.hidden,
                'email': agent.email,
                'ms_teams_app_id': agent.ms_teams_app_id,
                'communication_channel': agent.communication_channel,
                'is_active': agent.is_active,  # This uses the computed property
                # Add new fields for onboarding agents
                'type': agent.type,
                'is_default': agent.is_default,
                'prompt': agent.prompt,
                'focus_areas': agent.focus_areas
            }
            response_agents.append(agent_dict)
        
        return response_agents
        
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific agent"""
    try:
        query = select(RetellAgent).where(RetellAgent.id == agent_id)
        result = await db.execute(query)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an agent"""
    try:
        # Get existing agent
        query = select(RetellAgent).where(RetellAgent.id == agent_id)
        result = await db.execute(query)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Prepare update data for RetellAI
        retell_update_data = {}
        if agent_data.name is not None:
            retell_update_data["agent_name"] = agent_data.name
        if agent_data.prompt is not None:
            retell_update_data["general_prompt"] = agent_data.prompt
        if agent_data.voice_id is not None:
            retell_update_data["voice_id"] = agent_data.voice_id
        if agent_data.llm_websocket_url is not None:
            retell_update_data["llm_websocket_url"] = agent_data.llm_websocket_url
        if agent_data.boosted_keywords is not None:
            retell_update_data["boosted_keywords"] = agent_data.boosted_keywords
        if agent_data.tools is not None:
            retell_update_data["general_tools"] = agent_data.tools
        
        # Update in RetellAI
        if retell_update_data:
            await retell_service.update_agent(agent.retell_agent_id, retell_update_data)
        
        # Update in database
        update_data = agent_data.model_dump(exclude_unset=True)
        if update_data:
            await db.execute(
                update(RetellAgent)
                .where(RetellAgent.id == agent_id)
                .values(**update_data)
            )
            await db.commit()
            await db.refresh(agent)
        
        logger.info(f"Updated agent {agent_id}")
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{agent_id}")
async def delete_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an agent"""
    try:
        # Get existing agent
        query = select(RetellAgent).where(RetellAgent.id == agent_id)
        result = await db.execute(query)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Delete from RetellAI
        await retell_service.delete_agent(agent.retell_agent_id)
        
        # Mark as inactive in database (soft delete)
        await db.execute(
            update(RetellAgent)
            .where(RetellAgent.id == agent_id)
            .values(is_active=False)
        )
        await db.commit()
        
        logger.info(f"Deleted agent {agent_id}")
        return {"message": "Agent deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{agent_id}/test-call")
async def test_agent_call(
    agent_id: int,
    test_request: TestCallRequest,
    db: AsyncSession = Depends(get_db)
):
    """Make a test call with an agent"""
    try:
        # Get agent
        query = select(RetellAgent).where(RetellAgent.id == agent_id)
        result = await db.execute(query)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get a phone number for this agent
        phone_query = select(PhoneNumber).where(
            PhoneNumber.agent_id == agent_id,
            PhoneNumber.is_active == True
        )
        phone_result = await db.execute(phone_query)
        phone_number = phone_result.scalar_one_or_none()
        
        if not phone_number:
            raise HTTPException(
                status_code=400, 
                detail="No phone number assigned to this agent"
            )
        
        # Make the test call
        call_response = await retell_service.make_call(
            from_number=phone_number.phone_number,
            to_number=test_request.test_phone_number,
            agent_id=agent.retell_agent_id
        )
        
        logger.info(f"Initiated test call for agent {agent_id}: {call_response.get('call_id')}")
        return {
            "message": "Test call initiated",
            "call_id": call_response.get("call_id"),
            "from_number": phone_number.phone_number,
            "to_number": test_request.test_phone_number,
            "agent_name": agent.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making test call for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{agent_id}/sync-retell")
async def sync_agent_with_retell(agent_id: int, db: AsyncSession = Depends(get_db)):
    """Sync agent data with RetellAI (useful for observability)"""
    try:
        # Get local agent
        query = select(RetellAgent).where(RetellAgent.id == agent_id)
        result = await db.execute(query)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get agent data from RetellAI
        retell_agent_data = await retell_service.get_agent(agent.retell_agent_id)
        
        return {
            "local_agent": {
                "id": agent.id,
                "name": agent.name,
                "retell_agent_id": agent.retell_agent_id,
                "is_active": agent.is_active,
                "updated_at": agent.updated_at
            },
            "retell_agent": retell_agent_data,
            "sync_status": "data_retrieved"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing agent {agent_id} with RetellAI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{agent_id}/save-prompt")
async def save_agent_prompt_as_template(
    agent_id: int,
    prompt_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Save an agent's prompt as a reusable template"""
    try:
        # Get agent
        query = select(RetellAgent).where(RetellAgent.id == agent_id)
        result = await db.execute(query)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Use agent name as prompt name if not provided
        if not prompt_name:
            prompt_name = agent.name.lower().replace(" ", "_").replace("-", "_")
        
        # Create prompt template
        template_name = prompt_manager.create_from_retell_agent(
            agent_name=agent.name,
            retell_prompt=agent.prompt,
            description=f"Saved from agent '{agent.name}'",
            category="saved_agents"
        )
        
        logger.info(f"Saved agent {agent_id} prompt as template '{template_name}'")
        return {
            "message": f"Agent prompt saved as template '{template_name}'",
            "template_name": template_name,
            "agent_name": agent.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving agent prompt: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{agent_id}/prompt-suggestions")
async def get_prompt_suggestions(agent_id: int, db: AsyncSession = Depends(get_db)):
    """Get prompt template suggestions for an agent"""
    try:
        # Get agent
        query = select(RetellAgent).where(RetellAgent.id == agent_id)
        result = await db.execute(query)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get all available prompts
        all_prompts = prompt_manager.list_prompts()
        
        # Categorize suggestions
        suggestions = {
            "recommended": [],
            "by_category": {}
        }
        
        # Simple recommendation based on agent name keywords
        agent_name_lower = agent.name.lower()
        keywords = ["support", "sales", "appointment", "schedule", "customer", "service"]
        
        for prompt in all_prompts:
            category = prompt.get("category", "general")
            
            if category not in suggestions["by_category"]:
                suggestions["by_category"][category] = []
            
            suggestions["by_category"][category].append(prompt)
            
            # Simple keyword matching for recommendations
            prompt_name_lower = prompt.get("name", "").lower()
            prompt_title_lower = prompt.get("title", "").lower()
            
            for keyword in keywords:
                if (keyword in agent_name_lower and 
                    (keyword in prompt_name_lower or keyword in prompt_title_lower)):
                    if prompt not in suggestions["recommended"]:
                        suggestions["recommended"].append(prompt)
        
        return {
            "agent_name": agent.name,
            "current_prompt_length": len(agent.prompt),
            "suggestions": suggestions,
            "total_templates": len(all_prompts)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 

@router.get("/sync-all-from-retell")
async def sync_all_agents_from_retell(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Sync all agents from RetellAI into local database"""
    try:
        # Get all agents from RetellAI
        retell_agents = await retell_service.list_agents()
        
        synced_count = 0
        
        for retell_agent in retell_agents:
            # Check if agent already exists
            existing_agent = await db.execute(
                select(RetellAgent).where(RetellAgent.retell_agent_id == retell_agent['agent_id'])
            )
            existing_agent = existing_agent.scalar_one_or_none()
            
            if not existing_agent:
                # Create new agent in database
                new_agent = RetellAgent(
                    retell_agent_id=retell_agent['agent_id'],
                    name=retell_agent.get('agent_name', f"Agent {retell_agent['agent_id'][:8]}"),
                    prompt=retell_agent.get('general_prompt', ''),
                    voice_id=retell_agent.get('voice_id', ''),
                    llm_websocket_url=retell_agent.get('llm_websocket_url', ''),
                    boosted_keywords=retell_agent.get('boosted_keywords', []),
                    tools=retell_agent.get('functions', []),
                    response_engine=retell_agent.get('response_engine', {}),
                    language=retell_agent.get('language', 'en-US'),
                    webhook_url=retell_agent.get('webhook_url', ''),
                    is_active=True,
                    last_modified=datetime.utcnow()
                )
                db.add(new_agent)
                synced_count += 1
        
        await db.commit()
        
        logger.info(f"Synced {synced_count} agents from RetellAI")
        
        return {
            "message": f"Successfully synced {synced_count} agents from RetellAI",
            "synced_count": synced_count,
            "total_retell_agents": len(retell_agents)
        }
        
    except Exception as e:
        logger.error(f"Error syncing agents from RetellAI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to sync agents: {str(e)}") 