from pydantic import BaseModel, Field, EmailStr, computed_field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID

# Agent Schemas
class AgentCreate(BaseModel):
    name: str
    prompt: str
    voice_id: str
    llm_websocket_url: Optional[str] = None
    webhook_url: Optional[str] = None
    boosted_keywords: Optional[List[str]] = None
    inbound_dynamic_variables_webhook_url: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None
    voice_id: Optional[str] = None
    ambient_sound: Optional[str] = None
    webhook_url: Optional[str] = None
    boosted_keywords: Optional[List[str]] = None
    tools: Optional[List[Dict[str, Any]]] = None

class LegacyAgentResponse(BaseModel):
    id: str
    user_id: str
    remote_agent_id: Optional[str]
    remote_llm_id: Optional[str]
    name: str
    voice_id: str  # This will be UUID but we'll handle it as string
    first_message: Optional[str]
    sops: Optional[str]
    closing_statement: Optional[str]
    created_at: datetime
    hidden: Optional[bool]
    email: Optional[str]
    ms_teams_app_id: Optional[str]
    communication_channel: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class AgentResponse(BaseModel):
    id: int
    retell_agent_id: str
    name: str
    prompt: str
    voice_id: str
    ambient_sound: str
    webhook_url: Optional[str]
    boosted_keywords: Optional[List[str]]
    tools: Optional[List[Dict[str, Any]]]
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

# Eval Test Schemas
class EvalTestCreate(BaseModel):
    test_scenario_id: str
    name: str
    description: Optional[str] = None
    eval_criteria: str
    expected_outcome: str
    eval_type: str = 'accuracy'
    weight: int = 1

class EvalTestUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    eval_criteria: Optional[str] = None
    expected_outcome: Optional[str] = None
    eval_type: Optional[str] = None
    weight: Optional[int] = None
    status: Optional[str] = None
    score: Optional[int] = None
    notes: Optional[str] = None

class EvalTestResponse(BaseModel):
    id: str
    test_scenario_id: str
    name: str
    description: Optional[str]
    eval_criteria: str
    expected_outcome: str
    eval_type: str
    weight: int
    status: str
    score: Optional[int]
    notes: Optional[str]
    last_evaluated: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Phone Number Schemas
class PhoneNumberAssign(BaseModel):
    retell_phone_number_id: str
    agent_id: UUID

class PhoneNumberResponse(BaseModel):
    id: UUID
    phone_number: str
    country_code: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    phone_number_type: Optional[int] = None
    retell_phone_number_id: Optional[str] = None
    area_code: Optional[str] = None
    inbound_agent_id: Optional[str] = None
    outbound_agent_id: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True

# Call Schemas (using phone_calls table)
class CallCreate(BaseModel):
    from_number: str
    to_number: str
    direction: str = "outbound"  # inbound, outbound

class CallResponse(BaseModel):
    id: UUID
    retell_call_id: Optional[str] = None
    agent_id: Optional[UUID] = None
    caller_agent_id: Optional[UUID] = None
    inbound_agent_id: Optional[UUID] = None
    phone_number_id: Optional[UUID] = None
    from_number: Optional[str] = None
    to_number: Optional[str] = None
    direction: Optional[str] = None
    status: Optional[str] = None
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None
    duration_ms: Optional[str] = None
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    call_analysis: Optional[dict] = None
    call_metadata: Optional[dict] = None
    created_at: datetime
    
    # Computed fields for backward compatibility
    @computed_field
    @property
    def duration(self) -> int:
        """Convert duration_ms to seconds for backward compatibility"""
        if self.duration_ms:
            try:
                return int(self.duration_ms) // 1000
            except (ValueError, TypeError):
                return 0
        return 0
    
    # Agent names for display (populated by the API if agents are loaded)
    caller_agent_name: Optional[str] = None
    inbound_agent_name: Optional[str] = None

    class Config:
        from_attributes = True

# SyncroMSP Schemas
class TicketCreate(BaseModel):
    subject: str
    problem_type: str
    status: Optional[str] = "New"
    priority: Optional[str] = "Medium"
    customer_id: int
    description: Optional[str] = None

class TicketResponse(BaseModel):
    id: int
    syncro_ticket_id: int
    subject: str
    status: str
    priority: str
    customer_id: int
    customer_business_then_name: str
    problem_type: str
    created_at: datetime
    updated_at: datetime
    raw_data: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_agents: int
    total_phone_numbers: int
    total_calls_today: int
    active_calls: int
    recent_calls: List[CallResponse]
    agents_with_numbers: List[Dict[str, Any]]

# Test Call Schema
class TestCallRequest(BaseModel):
    agent_id: int
    test_phone_number: str = Field(..., description="Phone number to call for testing")
    test_prompt_override: Optional[str] = Field(None, description="Override prompt for testing")

# Webhook Schemas
class RetellWebhookEvent(BaseModel):
    event: str
    call: Optional[Dict[str, Any]]
    agent_id: Optional[str]
    call_id: Optional[str]
    timestamp: Optional[datetime]

# Error Response Schema
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None 

# Prompt Management Schemas
class PromptTemplateVariable(BaseModel):
    name: str
    description: str
    type: str = "string"  # string, number, boolean, array
    required: bool = True
    default: Optional[str] = None

class PromptTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=100)
    template_content: str = Field(..., min_length=1)
    variables: Optional[List[PromptTemplateVariable]] = []
    tools: Optional[List[Dict[str, Any]]] = []

class PromptTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    template_content: Optional[str] = Field(None, min_length=1)
    variables: Optional[List[PromptTemplateVariable]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None

class PromptTemplateResponse(BaseModel):
    id: str
    name: str
    title: str
    description: Optional[str]
    category: str
    template_content: str
    variables: Optional[List[Dict[str, Any]]]
    tools: Optional[List[Dict[str, Any]]]
    is_active: bool
    is_system_template: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    scenario_count: Optional[int] = 0

    class Config:
        from_attributes = True

class PromptScenarioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_id: str
    variable_values: Optional[Dict[str, Any]] = {}

class PromptScenarioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    variable_values: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class PromptScenarioResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    template_id: str
    variable_values: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    template: Optional[PromptTemplateResponse] = None
    compiled_prompt: Optional[str] = None  # Template with variables filled in

    class Config:
        from_attributes = True

class AgentPromptAssignmentCreate(BaseModel):
    agent_id: str
    scenario_id: str

class AgentPromptAssignmentResponse(BaseModel):
    id: str
    agent_id: str
    scenario_id: str
    is_active: bool
    assigned_at: datetime
    scenario: Optional[PromptScenarioResponse] = None

    class Config:
        from_attributes = True

# Bulk operations
class BulkPromptAssignmentCreate(BaseModel):
    agent_ids: List[str]
    scenario_id: str

class PromptTemplateImportRequest(BaseModel):
    file_path: str
    category: Optional[str] = "imported"
    overwrite_existing: bool = False

# Onboarding Schemas
class OrganizationProfileData(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None

class MSPWorkflow(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class MSPIntegrationData(BaseModel):
    platform: Optional[str] = None
    workflows: Optional[List[MSPWorkflow]] = []

class InternalPolicyData(BaseModel):
    category: str
    description: str
    priority: Optional[str] = 'medium'

class EscalationProcedureData(BaseModel):
    trigger: str
    action: str
    priority: Optional[str] = 'medium'
    contact_info: Optional[Dict[str, Any]] = None

class BusinessHoursData(BaseModel):
    standard: Optional[str] = None
    emergency: Optional[str] = None
    timezone: Optional[str] = None

class OnboardingTranscriptMessage(BaseModel):
    speaker: str  # agent, human, system
    content: str
    timestamp: datetime
    message_type: Optional[str] = 'transcript'
    extra_data: Optional[Dict[str, Any]] = None

class OnboardingSessionCreate(BaseModel):
    user_id: str

class OnboardingSessionResponse(BaseModel):
    id: str
    user_id: str
    retell_call_id: Optional[str] = None
    status: str
    session_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    # Nested data
    organization: Optional[OrganizationProfileData] = None
    msp_integration: Optional[MSPIntegrationData] = None
    policies: Optional[List[InternalPolicyData]] = []
    escalations: Optional[List[EscalationProcedureData]] = []
    business_hours: Optional[BusinessHoursData] = None
    transcript: Optional[List[OnboardingTranscriptMessage]] = []

    class Config:
        from_attributes = True

class OnboardingSessionUpdate(BaseModel):
    organization: Optional[OrganizationProfileData] = None
    msp_integration: Optional[MSPIntegrationData] = None
    policies: Optional[List[InternalPolicyData]] = None
    escalations: Optional[List[EscalationProcedureData]] = None
    business_hours: Optional[BusinessHoursData] = None
    status: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = None

class StartOnboardingCallRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None  # If continuing existing session

class StartOnboardingCallResponse(BaseModel):
    session_id: str
    call_id: str
    retell_call_id: Optional[str] = None
    status: str

class AddTranscriptMessageRequest(BaseModel):
    speaker: str
    content: str
    message_type: Optional[str] = 'transcript'
    metadata: Optional[Dict[str, Any]] = None

class UpdateSOPDataRequest(BaseModel):
    area: str  # organization, msp_integration, policies, escalations, business_hours
    data: Dict[str, Any]
    description: Optional[str] = None  # Description of what was updated

class OnboardingExportResponse(BaseModel):
    session_id: str
    organization: Optional[OrganizationProfileData] = None
    msp_integration: Optional[MSPIntegrationData] = None
    policies: Optional[List[InternalPolicyData]] = []
    escalations: Optional[List[EscalationProcedureData]] = []
    business_hours: Optional[BusinessHoursData] = None
    exported_at: datetime 