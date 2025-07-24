from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
from loguru import logger
from datetime import datetime

from ..database import get_db, EvalTest
from ..schemas import EvalTestCreate, EvalTestUpdate, EvalTestResponse

router = APIRouter()

@router.post("/", response_model=EvalTestResponse, status_code=201)
async def create_eval_test(
    eval_test_data: EvalTestCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new eval test"""
    try:
        eval_test = EvalTest(
            test_scenario_id=eval_test_data.test_scenario_id,
            name=eval_test_data.name,
            description=eval_test_data.description,
            eval_criteria=eval_test_data.eval_criteria,
            expected_outcome=eval_test_data.expected_outcome,
            eval_type=eval_test_data.eval_type,
            weight=eval_test_data.weight,
        )
        
        db.add(eval_test)
        await db.commit()
        await db.refresh(eval_test)
        
        # Convert UUID to string for response
        response_data = {
            'id': str(eval_test.id),
            'test_scenario_id': eval_test.test_scenario_id,
            'name': eval_test.name,
            'description': eval_test.description,
            'eval_criteria': eval_test.eval_criteria,
            'expected_outcome': eval_test.expected_outcome,
            'eval_type': eval_test.eval_type,
            'weight': eval_test.weight,
            'status': eval_test.status,
            'score': eval_test.score,
            'notes': eval_test.notes,
            'last_evaluated': eval_test.last_evaluated,
            'created_at': eval_test.created_at,
            'updated_at': eval_test.updated_at
        }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error creating eval test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[EvalTestResponse])
async def list_eval_tests(
    test_scenario_id: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List all eval tests, optionally filtered by test scenario"""
    try:
        query = select(EvalTest)
        if test_scenario_id:
            query = query.where(EvalTest.test_scenario_id == test_scenario_id)
        
        query = query.order_by(EvalTest.created_at)
        result = await db.execute(query)
        eval_tests = result.scalars().all()
        
        # Convert to response format
        response_tests = []
        for test in eval_tests:
            response_data = {
                'id': str(test.id),
                'test_scenario_id': test.test_scenario_id,
                'name': test.name,
                'description': test.description,
                'eval_criteria': test.eval_criteria,
                'expected_outcome': test.expected_outcome,
                'eval_type': test.eval_type,
                'weight': test.weight,
                'status': test.status,
                'score': test.score,
                'notes': test.notes,
                'last_evaluated': test.last_evaluated,
                'created_at': test.created_at,
                'updated_at': test.updated_at
            }
            response_tests.append(response_data)
        
        return response_tests
        
    except Exception as e:
        logger.error(f"Error listing eval tests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{eval_test_id}", response_model=EvalTestResponse)
async def get_eval_test(
    eval_test_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific eval test"""
    try:
        result = await db.execute(select(EvalTest).where(EvalTest.id == eval_test_id))
        eval_test = result.scalar_one_or_none()
        
        if not eval_test:
            raise HTTPException(status_code=404, detail="Eval test not found")
        
        response_data = {
            'id': str(eval_test.id),
            'test_scenario_id': eval_test.test_scenario_id,
            'name': eval_test.name,
            'description': eval_test.description,
            'eval_criteria': eval_test.eval_criteria,
            'expected_outcome': eval_test.expected_outcome,
            'eval_type': eval_test.eval_type,
            'weight': eval_test.weight,
            'status': eval_test.status,
            'score': eval_test.score,
            'notes': eval_test.notes,
            'last_evaluated': eval_test.last_evaluated,
            'created_at': eval_test.created_at,
            'updated_at': eval_test.updated_at
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting eval test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{eval_test_id}", response_model=EvalTestResponse)
async def update_eval_test(
    eval_test_id: str,
    eval_test_data: EvalTestUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an eval test"""
    try:
        result = await db.execute(select(EvalTest).where(EvalTest.id == eval_test_id))
        eval_test = result.scalar_one_or_none()
        
        if not eval_test:
            raise HTTPException(status_code=404, detail="Eval test not found")
        
        # Update fields
        update_data = {}
        for field, value in eval_test_data.dict(exclude_unset=True).items():
            if hasattr(eval_test, field):
                setattr(eval_test, field, value)
                update_data[field] = value
        
        if update_data:
            eval_test.updated_at = datetime.utcnow()
            if eval_test_data.status and eval_test_data.status != eval_test.status:
                eval_test.last_evaluated = datetime.utcnow()
        
        await db.commit()
        await db.refresh(eval_test)
        
        response_data = {
            'id': str(eval_test.id),
            'test_scenario_id': eval_test.test_scenario_id,
            'name': eval_test.name,
            'description': eval_test.description,
            'eval_criteria': eval_test.eval_criteria,
            'expected_outcome': eval_test.expected_outcome,
            'eval_type': eval_test.eval_type,
            'weight': eval_test.weight,
            'status': eval_test.status,
            'score': eval_test.score,
            'notes': eval_test.notes,
            'last_evaluated': eval_test.last_evaluated,
            'created_at': eval_test.created_at,
            'updated_at': eval_test.updated_at
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating eval test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{eval_test_id}")
async def delete_eval_test(
    eval_test_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an eval test"""
    try:
        result = await db.execute(select(EvalTest).where(EvalTest.id == eval_test_id))
        eval_test = result.scalar_one_or_none()
        
        if not eval_test:
            raise HTTPException(status_code=404, detail="Eval test not found")
        
        await db.execute(delete(EvalTest).where(EvalTest.id == eval_test_id))
        await db.commit()
        
        return {"message": "Eval test deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting eval test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{eval_test_id}/evaluate")
async def evaluate_test(
    eval_test_id: str,
    score: int,
    notes: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Evaluate a test and update its score/status"""
    try:
        result = await db.execute(select(EvalTest).where(EvalTest.id == eval_test_id))
        eval_test = result.scalar_one_or_none()
        
        if not eval_test:
            raise HTTPException(status_code=404, detail="Eval test not found")
        
        # Update evaluation
        eval_test.score = score
        eval_test.notes = notes or eval_test.notes
        eval_test.last_evaluated = datetime.utcnow()
        eval_test.updated_at = datetime.utcnow()
        
        # Set status based on score
        if score >= 80:
            eval_test.status = 'passed'
        elif score >= 60:
            eval_test.status = 'warning'
        else:
            eval_test.status = 'failed'
        
        await db.commit()
        
        return {"message": "Eval test evaluated successfully", "score": score, "status": eval_test.status}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 