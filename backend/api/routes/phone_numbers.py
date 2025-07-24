from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from loguru import logger

from ..database import get_db, PhoneNumber, RetellAgent
from ..services.retell_service import retell_service
from ..schemas import PhoneNumberAssign, PhoneNumberResponse

router = APIRouter()

@router.get("/", response_model=List[PhoneNumberResponse])
async def list_phone_numbers(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List all phone numbers"""
    try:
        query = select(PhoneNumber)
        if active_only:
            query = query.where(PhoneNumber.is_active == True)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        phone_numbers = result.scalars().all()
        
        return phone_numbers
        
    except Exception as e:
        logger.error(f"Error listing phone numbers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sync-from-retell")
async def sync_phone_numbers_from_retell(db: AsyncSession = Depends(get_db)):
    """Sync phone numbers from RetellAI to local database"""
    try:
        # Get phone numbers from RetellAI
        retell_phone_numbers = await retell_service.get_phone_numbers()
        
        synced_count = 0
        updated_count = 0
        
        for retell_phone in retell_phone_numbers:
            retell_id = retell_phone.get("phone_number_id")
            phone_number = retell_phone.get("phone_number")
            area_code = retell_phone.get("area_code")
            
            if not retell_id or not phone_number:
                continue
            
            # Check if phone number exists locally
            query = select(PhoneNumber).where(PhoneNumber.retell_phone_number_id == retell_id)
            result = await db.execute(query)
            existing_phone = result.scalar_one_or_none()
            
            if existing_phone:
                # Update existing
                await db.execute(
                    update(PhoneNumber)
                    .where(PhoneNumber.retell_phone_number_id == retell_id)
                    .values(
                        phone_number=phone_number,
                        area_code=area_code,
                        inbound_agent_id=retell_phone.get("inbound_agent_id"),
                        outbound_agent_id=retell_phone.get("outbound_agent_id"),
                        is_active=True
                    )
                )
                updated_count += 1
            else:
                # Create new
                new_phone = PhoneNumber(
                    retell_phone_number_id=retell_id,
                    phone_number=phone_number,
                    area_code=area_code,
                    inbound_agent_id=retell_phone.get("inbound_agent_id"),
                    outbound_agent_id=retell_phone.get("outbound_agent_id"),
                    is_active=True
                )
                db.add(new_phone)
                synced_count += 1
        
        await db.commit()
        
        logger.info(f"Synced {synced_count} new phone numbers, updated {updated_count} existing")
        return {
            "message": "Phone numbers synced successfully",
            "new_count": synced_count,
            "updated_count": updated_count,
            "total_retell_numbers": len(retell_phone_numbers)
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error syncing phone numbers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assign", response_model=PhoneNumberResponse)
async def assign_phone_number_to_agent(
    assignment: PhoneNumberAssign,
    db: AsyncSession = Depends(get_db)
):
    """Assign a phone number to an agent"""
    try:
        # Get phone number
        phone_query = select(PhoneNumber).where(
            PhoneNumber.retell_phone_number_id == assignment.retell_phone_number_id
        )
        phone_result = await db.execute(phone_query)
        phone_number = phone_result.scalar_one_or_none()
        
        if not phone_number:
            raise HTTPException(status_code=404, detail="Phone number not found")
        
        # Get agent
        agent_query = select(RetellAgent).where(RetellAgent.id == assignment.agent_id)
        agent_result = await db.execute(agent_query)
        agent = agent_result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update phone number assignment in RetellAI
        await retell_service.update_phone_number(
            phone_number.retell_phone_number_id,
            agent.retell_agent_id
        )
        
        # Update local database
        await db.execute(
            update(PhoneNumber)
            .where(PhoneNumber.retell_phone_number_id == assignment.retell_phone_number_id)
            .values(
                agent_id=assignment.agent_id,
                inbound_agent_id=agent.retell_agent_id,
                outbound_agent_id=agent.retell_agent_id
            )
        )
        await db.commit()
        await db.refresh(phone_number)
        
        logger.info(f"Assigned phone number {phone_number.phone_number} to agent {agent.name}")
        return phone_number
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error assigning phone number: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{phone_number_id}/unassign")
async def unassign_phone_number(
    phone_number_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Unassign a phone number from its current agent"""
    try:
        # Get phone number
        query = select(PhoneNumber).where(PhoneNumber.id == phone_number_id)
        result = await db.execute(query)
        phone_number = result.scalar_one_or_none()
        
        if not phone_number:
            raise HTTPException(status_code=404, detail="Phone number not found")
        
        # Update local database
        await db.execute(
            update(PhoneNumber)
            .where(PhoneNumber.id == phone_number_id)
            .values(
                agent_id=None,
                inbound_agent_id=None,
                outbound_agent_id=None
            )
        )
        await db.commit()
        
        logger.info(f"Unassigned phone number {phone_number.phone_number}")
        return {"message": "Phone number unassigned successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error unassigning phone number: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{phone_number_id}", response_model=PhoneNumberResponse)
async def get_phone_number(phone_number_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific phone number"""
    try:
        query = select(PhoneNumber).where(PhoneNumber.id == phone_number_id)
        result = await db.execute(query)
        phone_number = result.scalar_one_or_none()
        
        if not phone_number:
            raise HTTPException(status_code=404, detail="Phone number not found")
        
        return phone_number
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting phone number {phone_number_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/retell/{retell_phone_id}/details")
async def get_retell_phone_number_details(retell_phone_id: str):
    """Get phone number details from RetellAI"""
    try:
        retell_phone_data = await retell_service.get_phone_number(retell_phone_id)
        
        return {
            "retell_data": retell_phone_data,
            "status": "retrieved"
        }
        
    except Exception as e:
        logger.error(f"Error getting RetellAI phone number details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 