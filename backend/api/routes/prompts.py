from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path
from datetime import datetime
from loguru import logger

from ..database import get_db, PromptTemplate, PromptScenario, AgentPromptAssignment, Agent
from ..schemas import (
    PromptTemplateCreate, PromptTemplateUpdate, PromptTemplateResponse,
    PromptScenarioCreate, PromptScenarioUpdate, PromptScenarioResponse,
    AgentPromptAssignmentCreate, AgentPromptAssignmentResponse,
    BulkPromptAssignmentCreate, PromptTemplateImportRequest
)

router = APIRouter()

# Template Management
@router.get("/templates", response_model=List[PromptTemplateResponse])
async def list_templates(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all prompt templates with optional filtering"""
    try:
        query = select(PromptTemplate)
        
        # Apply filters
        conditions = []
        if category:
            conditions.append(PromptTemplate.category == category)
        if is_active is not None:
            conditions.append(PromptTemplate.is_active == is_active)
        if search:
            conditions.append(or_(
                PromptTemplate.name.ilike(f"%{search}%"),
                PromptTemplate.title.ilike(f"%{search}%"),
                PromptTemplate.description.ilike(f"%{search}%")
            ))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit).order_by(PromptTemplate.created_at.desc())
        
        result = await db.execute(query)
        templates = result.scalars().all()
        
        # Add scenario count for each template
        response_templates = []
        for template in templates:
            scenario_count_query = select(func.count(PromptScenario.id)).where(
                and_(
                    PromptScenario.template_id == template.id,
                    PromptScenario.is_active == True
                )
            )
            scenario_count_result = await db.execute(scenario_count_query)
            scenario_count = scenario_count_result.scalar() or 0
            
            template_dict = {
                "id": str(template.id),
                "name": template.name,
                "title": template.title,
                "description": template.description,
                "category": template.category,
                "template_content": template.template_content,
                "variables": template.variables,
                "tools": template.tools,
                "is_active": template.is_active,
                "is_system_template": template.is_system_template,
                "created_at": template.created_at,
                "updated_at": template.updated_at,
                "created_by": template.created_by,
                "scenario_count": scenario_count
            }
            response_templates.append(template_dict)
        
        return response_templates
        
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates", response_model=PromptTemplateResponse, status_code=201)
async def create_template(
    template_data: PromptTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new prompt template"""
    try:
        # Check if template name already exists
        existing_query = select(PromptTemplate).where(PromptTemplate.name == template_data.name)
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Template name already exists")
        
        db_template = PromptTemplate(
            name=template_data.name,
            title=template_data.title,
            description=template_data.description,
            category=template_data.category,
            template_content=template_data.template_content,
            variables=[var.dict() for var in template_data.variables] if template_data.variables else [],
            tools=template_data.tools,
            is_system_template=False,
            created_by="api_user"  # TODO: Get from auth context
        )
        
        db.add(db_template)
        await db.commit()
        await db.refresh(db_template)
        
        logger.info(f"Created template {db_template.id}: {db_template.name}")
        
        return {
            "id": str(db_template.id),
            "name": db_template.name,
            "title": db_template.title,
            "description": db_template.description,
            "category": db_template.category,
            "template_content": db_template.template_content,
            "variables": db_template.variables,
            "tools": db_template.tools,
            "is_active": db_template.is_active,
            "is_system_template": db_template.is_system_template,
            "created_at": db_template.created_at,
            "updated_at": db_template.updated_at,
            "created_by": db_template.created_by,
            "scenario_count": 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}", response_model=PromptTemplateResponse)
async def get_template(template_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific template"""
    try:
        query = select(PromptTemplate).where(PromptTemplate.id == template_id)
        result = await db.execute(query)
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Get scenario count
        scenario_count_query = select(func.count(PromptScenario.id)).where(
            and_(
                PromptScenario.template_id == template.id,
                PromptScenario.is_active == True
            )
        )
        scenario_count_result = await db.execute(scenario_count_query)
        scenario_count = scenario_count_result.scalar() or 0
        
        return {
            "id": str(template.id),
            "name": template.name,
            "title": template.title,
            "description": template.description,
            "category": template.category,
            "template_content": template.template_content,
            "variables": template.variables,
            "tools": template.tools,
            "is_active": template.is_active,
            "is_system_template": template.is_system_template,
            "created_at": template.created_at,
            "updated_at": template.updated_at,
            "created_by": template.created_by,
            "scenario_count": scenario_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/templates/{template_id}", response_model=PromptTemplateResponse)
async def update_template(
    template_id: str,
    template_data: PromptTemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a template"""
    try:
        query = select(PromptTemplate).where(PromptTemplate.id == template_id)
        result = await db.execute(query)
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        if template.is_system_template:
            raise HTTPException(status_code=400, detail="Cannot modify system templates")
        
        # Update fields
        update_data = template_data.dict(exclude_unset=True)
        if 'variables' in update_data and update_data['variables'] is not None:
            update_data['variables'] = [var.dict() if hasattr(var, 'dict') else var for var in update_data['variables']]
        
        for field, value in update_data.items():
            setattr(template, field, value)
        
        template.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(template)
        
        logger.info(f"Updated template {template.id}: {template.name}")
        
        return {
            "id": str(template.id),
            "name": template.name,
            "title": template.title,
            "description": template.description,
            "category": template.category,
            "template_content": template.template_content,
            "variables": template.variables,
            "tools": template.tools,
            "is_active": template.is_active,
            "is_system_template": template.is_system_template,
            "created_at": template.created_at,
            "updated_at": template.updated_at,
            "created_by": template.created_by,
            "scenario_count": 0  # Could calculate if needed
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/templates/{template_id}")
async def delete_template(template_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a template (soft delete by setting is_active=False)"""
    try:
        query = select(PromptTemplate).where(PromptTemplate.id == template_id)
        result = await db.execute(query)
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        if template.is_system_template:
            raise HTTPException(status_code=400, detail="Cannot delete system templates")
        
        # Soft delete
        template.is_active = False
        template.updated_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"Deleted template {template.id}: {template.name}")
        return {"message": "Template deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Scenario Management
@router.get("/scenarios", response_model=List[PromptScenarioResponse])
async def list_scenarios(
    template_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all prompt scenarios with optional filtering"""
    try:
        query = select(PromptScenario).options(selectinload(PromptScenario.template))
        
        # Apply filters
        conditions = []
        if template_id:
            conditions.append(PromptScenario.template_id == template_id)
        if is_active is not None:
            conditions.append(PromptScenario.is_active == is_active)
        if search:
            conditions.append(or_(
                PromptScenario.name.ilike(f"%{search}%"),
                PromptScenario.description.ilike(f"%{search}%")
            ))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit).order_by(PromptScenario.created_at.desc())
        
        result = await db.execute(query)
        scenarios = result.scalars().all()
        
        response_scenarios = []
        for scenario in scenarios:
            # Compile prompt with variables
            compiled_prompt = compile_prompt_template(
                scenario.template.template_content if scenario.template else "",
                scenario.variable_values or {}
            )
            
            scenario_dict = {
                "id": str(scenario.id),
                "name": scenario.name,
                "description": scenario.description,
                "template_id": str(scenario.template_id),
                "variable_values": scenario.variable_values,
                "is_active": scenario.is_active,
                "created_at": scenario.created_at,
                "updated_at": scenario.updated_at,
                "template": {
                    "id": str(scenario.template.id),
                    "name": scenario.template.name,
                    "title": scenario.template.title,
                    "description": scenario.template.description,
                    "category": scenario.template.category,
                    "template_content": scenario.template.template_content,
                    "variables": scenario.template.variables,
                    "tools": scenario.template.tools,
                    "is_active": scenario.template.is_active,
                    "is_system_template": scenario.template.is_system_template,
                    "created_at": scenario.template.created_at,
                    "updated_at": scenario.template.updated_at,
                    "created_by": scenario.template.created_by,
                    "scenario_count": 0
                } if scenario.template else None,
                "compiled_prompt": compiled_prompt
            }
            response_scenarios.append(scenario_dict)
        
        return response_scenarios
        
    except Exception as e:
        logger.error(f"Error listing scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scenarios", response_model=PromptScenarioResponse, status_code=201)
async def create_scenario(
    scenario_data: PromptScenarioCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new prompt scenario"""
    try:
        # Verify template exists
        template_query = select(PromptTemplate).where(PromptTemplate.id == scenario_data.template_id)
        template_result = await db.execute(template_query)
        template = template_result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check if scenario name already exists for this template
        existing_query = select(PromptScenario).where(
            and_(
                PromptScenario.name == scenario_data.name,
                PromptScenario.template_id == scenario_data.template_id
            )
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Scenario name already exists for this template")
        
        db_scenario = PromptScenario(
            name=scenario_data.name,
            description=scenario_data.description,
            template_id=scenario_data.template_id,
            variable_values=scenario_data.variable_values
        )
        
        db.add(db_scenario)
        await db.commit()
        await db.refresh(db_scenario)
        
        # Load template for response
        await db.refresh(db_scenario, ["template"])
        
        # Compile prompt
        compiled_prompt = compile_prompt_template(
            template.template_content,
            scenario_data.variable_values or {}
        )
        
        logger.info(f"Created scenario {db_scenario.id}: {db_scenario.name}")
        
        return {
            "id": str(db_scenario.id),
            "name": db_scenario.name,
            "description": db_scenario.description,
            "template_id": str(db_scenario.template_id),
            "variable_values": db_scenario.variable_values,
            "is_active": db_scenario.is_active,
            "created_at": db_scenario.created_at,
            "updated_at": db_scenario.updated_at,
            "template": None,  # Can be loaded separately if needed
            "compiled_prompt": compiled_prompt
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scenarios/{scenario_id}", response_model=PromptScenarioResponse)
async def get_scenario(scenario_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific scenario with compiled prompt"""
    try:
        query = select(PromptScenario).options(selectinload(PromptScenario.template)).where(PromptScenario.id == scenario_id)
        result = await db.execute(query)
        scenario = result.scalar_one_or_none()
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Compile prompt
        compiled_prompt = compile_prompt_template(
            scenario.template.template_content if scenario.template else "",
            scenario.variable_values or {}
        )
        
        return {
            "id": str(scenario.id),
            "name": scenario.name,
            "description": scenario.description,
            "template_id": str(scenario.template_id),
            "variable_values": scenario.variable_values,
            "is_active": scenario.is_active,
            "created_at": scenario.created_at,
            "updated_at": scenario.updated_at,
            "template": {
                "id": str(scenario.template.id),
                "name": scenario.template.name,
                "title": scenario.template.title,
                "description": scenario.template.description,
                "category": scenario.template.category,
                "template_content": scenario.template.template_content,
                "variables": scenario.template.variables,
                "tools": scenario.template.tools,
                "is_active": scenario.template.is_active,
                "is_system_template": scenario.template.is_system_template,
                "created_at": scenario.template.created_at,
                "updated_at": scenario.template.updated_at,
                "created_by": scenario.template.created_by,
                "scenario_count": 0
            } if scenario.template else None,
            "compiled_prompt": compiled_prompt
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scenario {scenario_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/scenarios/{scenario_id}", response_model=PromptScenarioResponse)
async def update_scenario(
    scenario_id: str,
    scenario_data: PromptScenarioUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a scenario"""
    try:
        query = select(PromptScenario).options(selectinload(PromptScenario.template)).where(PromptScenario.id == scenario_id)
        result = await db.execute(query)
        scenario = result.scalar_one_or_none()
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Update fields
        update_data = scenario_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(scenario, field, value)
        
        scenario.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(scenario)
        
        # Compile prompt
        compiled_prompt = compile_prompt_template(
            scenario.template.template_content if scenario.template else "",
            scenario.variable_values or {}
        )
        
        logger.info(f"Updated scenario {scenario.id}: {scenario.name}")
        
        return {
            "id": str(scenario.id),
            "name": scenario.name,
            "description": scenario.description,
            "template_id": str(scenario.template_id),
            "variable_values": scenario.variable_values,
            "is_active": scenario.is_active,
            "created_at": scenario.created_at,
            "updated_at": scenario.updated_at,
            "template": None,  # Can be loaded separately if needed
            "compiled_prompt": compiled_prompt
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating scenario {scenario_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/scenarios/{scenario_id}")
async def delete_scenario(scenario_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a scenario (soft delete)"""
    try:
        query = select(PromptScenario).where(PromptScenario.id == scenario_id)
        result = await db.execute(query)
        scenario = result.scalar_one_or_none()
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Soft delete
        scenario.is_active = False
        scenario.updated_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"Deleted scenario {scenario.id}: {scenario.name}")
        return {"message": "Scenario deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting scenario {scenario_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Import templates from files
@router.post("/templates/import-from-files")
async def import_templates_from_files(db: AsyncSession = Depends(get_db)):
    """Import templates from the templates directory"""
    try:
        templates_dir = Path(__file__).parent.parent / "prompts" / "templates"
        
        if not templates_dir.exists():
            raise HTTPException(status_code=404, detail="Templates directory not found")
        
        imported_count = 0
        errors = []
        
        # Import JSON templates
        for json_file in templates_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                # Check if template already exists
                existing_query = select(PromptTemplate).where(PromptTemplate.name == json_file.stem)
                existing_result = await db.execute(existing_query)
                if existing_result.scalar_one_or_none():
                    continue  # Skip existing templates
                
                db_template = PromptTemplate(
                    name=json_file.stem,
                    title=template_data.get("title", json_file.stem),
                    description=template_data.get("description", ""),
                    category=template_data.get("category", "imported"),
                    template_content=template_data.get("template", ""),
                    variables=template_data.get("variables", []),
                    tools=template_data.get("tools", []),
                    is_system_template=True,
                    created_by="system_import"
                )
                
                db.add(db_template)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Error importing {json_file.name}: {str(e)}")
        
        # Import TXT templates
        for txt_file in templates_dir.glob("*.txt"):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if template already exists
                existing_query = select(PromptTemplate).where(PromptTemplate.name == txt_file.stem)
                existing_result = await db.execute(existing_query)
                if existing_result.scalar_one_or_none():
                    continue  # Skip existing templates
                
                db_template = PromptTemplate(
                    name=txt_file.stem,
                    title=txt_file.stem.replace("_", " ").title(),
                    description=f"Imported from {txt_file.name}",
                    category="text_templates",
                    template_content=content,
                    variables=[],
                    tools=[],
                    is_system_template=True,
                    created_by="system_import"
                )
                
                db.add(db_template)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Error importing {txt_file.name}: {str(e)}")
        
        await db.commit()
        
        logger.info(f"Imported {imported_count} templates from files")
        
        return {
            "message": f"Successfully imported {imported_count} templates",
            "imported_count": imported_count,
            "errors": errors
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error importing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent Assignment Management
@router.get("/assignments", response_model=List[AgentPromptAssignmentResponse])
async def list_assignments(
    agent_id: Optional[str] = None,
    scenario_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """List prompt assignments"""
    try:
        query = select(AgentPromptAssignment).options(
            selectinload(AgentPromptAssignment.scenario).selectinload(PromptScenario.template)
        )
        
        conditions = []
        if agent_id:
            conditions.append(AgentPromptAssignment.agent_id == agent_id)
        if scenario_id:
            conditions.append(AgentPromptAssignment.scenario_id == scenario_id)
        if is_active is not None:
            conditions.append(AgentPromptAssignment.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await db.execute(query)
        assignments = result.scalars().all()
        
        response_assignments = []
        for assignment in assignments:
            scenario_data = None
            if assignment.scenario:
                compiled_prompt = compile_prompt_template(
                    assignment.scenario.template.template_content if assignment.scenario.template else "",
                    assignment.scenario.variable_values or {}
                )
                
                scenario_data = {
                    "id": str(assignment.scenario.id),
                    "name": assignment.scenario.name,
                    "description": assignment.scenario.description,
                    "template_id": str(assignment.scenario.template_id),
                    "variable_values": assignment.scenario.variable_values,
                    "is_active": assignment.scenario.is_active,
                    "created_at": assignment.scenario.created_at,
                    "updated_at": assignment.scenario.updated_at,
                    "template": None,  # Avoid deep nesting
                    "compiled_prompt": compiled_prompt
                }
            
            assignment_dict = {
                "id": str(assignment.id),
                "agent_id": assignment.agent_id,
                "scenario_id": str(assignment.scenario_id),
                "is_active": assignment.is_active,
                "assigned_at": assignment.assigned_at,
                "scenario": scenario_data
            }
            response_assignments.append(assignment_dict)
        
        return response_assignments
        
    except Exception as e:
        logger.error(f"Error listing assignments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assignments", response_model=AgentPromptAssignmentResponse, status_code=201)
async def create_assignment(
    assignment_data: AgentPromptAssignmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Assign a prompt scenario to an agent"""
    try:
        # Verify agent exists
        agent_query = select(Agent).where(Agent.id == assignment_data.agent_id)
        agent_result = await db.execute(agent_query)
        if not agent_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Verify scenario exists
        scenario_query = select(PromptScenario).where(PromptScenario.id == assignment_data.scenario_id)
        scenario_result = await db.execute(scenario_query)
        if not scenario_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Check if assignment already exists
        existing_query = select(AgentPromptAssignment).where(
            and_(
                AgentPromptAssignment.agent_id == assignment_data.agent_id,
                AgentPromptAssignment.scenario_id == assignment_data.scenario_id,
                AgentPromptAssignment.is_active == True
            )
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Assignment already exists")
        
        db_assignment = AgentPromptAssignment(
            agent_id=assignment_data.agent_id,
            scenario_id=assignment_data.scenario_id
        )
        
        db.add(db_assignment)
        await db.commit()
        await db.refresh(db_assignment)
        
        logger.info(f"Created assignment {db_assignment.id}: agent {assignment_data.agent_id} -> scenario {assignment_data.scenario_id}")
        
        return {
            "id": str(db_assignment.id),
            "agent_id": db_assignment.agent_id,
            "scenario_id": str(db_assignment.scenario_id),
            "is_active": db_assignment.is_active,
            "assigned_at": db_assignment.assigned_at,
            "scenario": None  # Can be loaded separately if needed
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating assignment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assignments/bulk", status_code=201)
async def create_bulk_assignments(
    assignment_data: BulkPromptAssignmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Assign a prompt scenario to multiple agents"""
    try:
        # Verify scenario exists
        scenario_query = select(PromptScenario).where(PromptScenario.id == assignment_data.scenario_id)
        scenario_result = await db.execute(scenario_query)
        if not scenario_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        created_assignments = []
        errors = []
        
        for agent_id in assignment_data.agent_ids:
            try:
                # Verify agent exists
                agent_query = select(Agent).where(Agent.id == agent_id)
                agent_result = await db.execute(agent_query)
                if not agent_result.scalar_one_or_none():
                    errors.append(f"Agent {agent_id} not found")
                    continue
                
                # Check if assignment already exists
                existing_query = select(AgentPromptAssignment).where(
                    and_(
                        AgentPromptAssignment.agent_id == agent_id,
                        AgentPromptAssignment.scenario_id == assignment_data.scenario_id,
                        AgentPromptAssignment.is_active == True
                    )
                )
                existing_result = await db.execute(existing_query)
                if existing_result.scalar_one_or_none():
                    errors.append(f"Assignment already exists for agent {agent_id}")
                    continue
                
                db_assignment = AgentPromptAssignment(
                    agent_id=agent_id,
                    scenario_id=assignment_data.scenario_id
                )
                
                db.add(db_assignment)
                created_assignments.append(agent_id)
                
            except Exception as e:
                errors.append(f"Error assigning to agent {agent_id}: {str(e)}")
        
        await db.commit()
        
        logger.info(f"Created {len(created_assignments)} bulk assignments for scenario {assignment_data.scenario_id}")
        
        return {
            "message": f"Successfully created {len(created_assignments)} assignments",
            "created_count": len(created_assignments),
            "assigned_agents": created_assignments,
            "errors": errors
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating bulk assignments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/assignments/{assignment_id}")
async def delete_assignment(assignment_id: str, db: AsyncSession = Depends(get_db)):
    """Remove a prompt assignment"""
    try:
        query = select(AgentPromptAssignment).where(AgentPromptAssignment.id == assignment_id)
        result = await db.execute(query)
        assignment = result.scalar_one_or_none()
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        assignment.is_active = False
        await db.commit()
        
        logger.info(f"Deleted assignment {assignment.id}")
        return {"message": "Assignment deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting assignment {assignment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility function to compile templates
def compile_prompt_template(template_content: str, variable_values: Dict[str, Any]) -> str:
    """Compile a prompt template with variable values"""
    try:
        compiled = template_content
        for key, value in variable_values.items():
            placeholder = f"{{{key}}}"
            compiled = compiled.replace(placeholder, str(value))
        return compiled
    except Exception as e:
        logger.error(f"Error compiling template: {str(e)}")
        return template_content

# Get categories
@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get all unique template categories"""
    try:
        query = select(PromptTemplate.category).distinct().where(PromptTemplate.is_active == True)
        result = await db.execute(query)
        categories = [row[0] for row in result.fetchall()]
        return {"categories": sorted(categories)}
        
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 