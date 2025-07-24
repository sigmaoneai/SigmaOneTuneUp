from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Text, Boolean, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Database configuration based on environment
environment = os.getenv("ENVIRONMENT", "dev")

if environment == "prod":
    db_host = os.getenv("POSTGRES_DB_HOST")
    db_port = os.getenv("POSTGRES_DB_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB_NAME")
    db_user = os.getenv("POSTGRES_DB_USER")
    db_password = os.getenv("POSTGRES_DB_PASSWORD")
else:
    db_host = os.getenv("POSTGRES_DB_HOST_DEV")
    db_port = os.getenv("POSTGRES_DB_PORT_DEV", "5432")
    db_name = os.getenv("POSTGRES_DB_NAME_DEV")
    db_user = os.getenv("POSTGRES_DB_USER_DEV")
    db_password = os.getenv("POSTGRES_DB_PASSWORD_DEV")

# Create database URL
DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create engine
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_size=10,
    max_overflow=20,
)

# Create session maker
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create declarative base
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

class Agent(Base):
    __tablename__ = "agents"
    
    # Match existing schema exactly
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    remote_agent_id = Column(String, nullable=True)
    remote_llm_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    voice_id = Column(UUID(as_uuid=True), nullable=False)
    first_message = Column(String, nullable=True)
    sops = Column(String, nullable=True)
    closing_statement = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    hidden = Column(Boolean, nullable=True)
    email = Column(String, nullable=True)
    ms_teams_app_id = Column(String, nullable=True)
    communication_channel = Column(String, nullable=True)
    
    # Add computed property for compatibility
    @property
    def is_active(self):
        return not self.hidden if self.hidden is not None else True
    
    # Relationships - conversations table has agent_id, phone_calls doesn't
    conversations = relationship("Conversation", back_populates="agent")

class EvalTest(Base):
    __tablename__ = "eval_tests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    test_scenario_id = Column(String, nullable=False)  # Links to test scenario ID from localStorage
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    eval_criteria = Column(Text, nullable=False)  # What to evaluate
    expected_outcome = Column(Text, nullable=False)  # Expected result
    eval_type = Column(String, nullable=False, default='accuracy')  # accuracy, latency, tone, etc.
    weight = Column(Integer, default=1)  # Importance weight (1-10)
    status = Column(String, default='pending')  # pending, passed, failed
    score = Column(Integer, nullable=True)  # Score out of 100
    notes = Column(Text, nullable=True)
    last_evaluated = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Keep RetellAgent for compatibility with new RetellAI integrations
class RetellAgent(Base):
    __tablename__ = "retell_agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    retell_agent_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    prompt = Column(Text)
    voice_id = Column(String)
    llm_websocket_url = Column(String)
    webhook_url = Column(String)
    boosted_keywords = Column(JSON)
    inbound_dynamic_variables_webhook_url = Column(String)
    tools = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    calls = relationship("Call", foreign_keys="[Call.agent_id]", back_populates="agent")

class PhoneNumber(Base):
    __tablename__ = "phone_numbers"
    
    # Match existing schema exactly
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    phone_number = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    description = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    agent_id = Column(String, nullable=True)  # String to match existing schema
    phone_number_type = Column(Integer, nullable=False)
    
    # Add computed property for compatibility with existing code
    @property
    def is_active(self):
        return True  # For now, assume all phone numbers are active

class PhoneCall(Base):
    __tablename__ = "phone_calls"
    
    # Match existing schema exactly (no agent_id in phone_calls table)
    id = Column(String, primary_key=True, index=True)
    direction = Column(String, nullable=False)
    from_number = Column(String, nullable=False)
    to_number = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # integer, not string
    transcript = Column(String, nullable=False)  # varchar, not text
    recording_url = Column(String, nullable=False)
    total_cost = Column(String, nullable=False)  # We'll treat as string for compatibility
    created_at = Column(DateTime, nullable=False)
    
    # No agent relationship for phone_calls table

class Conversation(Base):
    __tablename__ = "conversations"
    
    # Match existing schema exactly
    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=True)
    customer_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False)
    user_id = Column(String, nullable=False)
    agent_name = Column(String, nullable=True)
    customer_name = Column(String, nullable=True)
    customer_contact_name = Column(String, nullable=True)
    conversation_type = Column(String, nullable=False)
    ticket_id = Column(String, nullable=True)
    ticket_url = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    potential_issues = Column(String, nullable=True)
    issue_category = Column(String, nullable=True)
    recommended_next_steps = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)
    
    # Relationships
    agent = relationship("Agent", foreign_keys=[agent_id])

# Keep Call model for RetellAI integrations
class Call(Base):
    __tablename__ = "calls"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    retell_call_id = Column(String, unique=True, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("retell_agents.id"))  # Keep for backward compatibility
    caller_agent_id = Column(UUID(as_uuid=True), ForeignKey("retell_agents.id"), nullable=True)  # Agent making the call
    inbound_agent_id = Column(UUID(as_uuid=True), ForeignKey("retell_agents.id"), nullable=True)  # Agent receiving the call
    phone_number_id = Column(UUID(as_uuid=True), ForeignKey("phone_numbers.id"))
    from_number = Column(String)
    to_number = Column(String)
    direction = Column(String)  # inbound, outbound, agent_to_agent
    status = Column(String)  # registered, ongoing, ended
    start_timestamp = Column(DateTime)
    end_timestamp = Column(DateTime)
    duration_ms = Column(String)
    recording_url = Column(String)
    transcript = Column(Text)
    call_analysis = Column(JSON)
    call_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("RetellAgent", foreign_keys=[agent_id], back_populates="calls")
    caller_agent = relationship("RetellAgent", foreign_keys=[caller_agent_id])
    inbound_agent = relationship("RetellAgent", foreign_keys=[inbound_agent_id])
    phone_number = relationship("PhoneNumber")
    events = relationship("CallEvent", back_populates="call")

class CallEvent(Base):
    __tablename__ = "call_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"))
    event_type = Column(String)  # call_started, call_ended, call_interrupted, etc.
    event_data = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    call = relationship("Call", back_populates="events")

class SyncroTicket(Base):
    __tablename__ = "syncro_tickets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    syncro_ticket_id = Column(String, unique=True, index=True)
    customer_id = Column(String)
    subject = Column(String)
    description = Column(Text)
    status = Column(String)
    priority = Column(String)
    problem_type = Column(String)
    assigned_technician = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    synced_at = Column(DateTime, default=datetime.utcnow)
    
    # Additional metadata
    ticket_metadata = Column(JSON) 

class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False, index=True)  # support, sales, appointment, etc.
    template_content = Column(Text, nullable=False)  # The actual prompt template
    variables = Column(JSON, nullable=True)  # Template variables with defaults
    tools = Column(JSON, nullable=True)  # Available tools for this template
    is_active = Column(Boolean, default=True)
    is_system_template = Column(Boolean, default=False)  # True for built-in templates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String, nullable=True)  # User who created it
    
    # Relationships
    scenarios = relationship("PromptScenario", back_populates="template")

class PromptScenario(Base):
    __tablename__ = "prompt_scenarios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("prompt_templates.id"), nullable=False)
    variable_values = Column(JSON, nullable=True)  # Specific values for template variables
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    template = relationship("PromptTemplate", back_populates="scenarios")
    agent_assignments = relationship("AgentPromptAssignment", back_populates="scenario")

class AgentPromptAssignment(Base):
    __tablename__ = "agent_prompt_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("prompt_scenarios.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent")
    scenario = relationship("PromptScenario", back_populates="agent_assignments")

# Onboarding Models
class OnboardingSession(Base):
    __tablename__ = "onboarding_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(String, nullable=False, index=True)  # User who owns this session
    retell_call_id = Column(String, nullable=True, unique=True)  # Associated Retell AI call
    status = Column(String, default='active')  # active, completed, cancelled
    session_data = Column(JSON, nullable=True)  # Store conversation state
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("OrganizationProfile", back_populates="session", uselist=False)
    msp_integration = relationship("MSPIntegration", back_populates="session", uselist=False)
    policies = relationship("InternalPolicy", back_populates="session")
    escalations = relationship("EscalationProcedure", back_populates="session")
    business_hours = relationship("BusinessHours", back_populates="session", uselist=False)
    transcript_messages = relationship("OnboardingTranscript", back_populates="session")

class OrganizationProfile(Base):
    __tablename__ = "organization_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_sessions.id"), nullable=False)
    name = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    size = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("OnboardingSession", back_populates="organization")

class MSPIntegration(Base):
    __tablename__ = "msp_integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_sessions.id"), nullable=False)
    platform = Column(String, nullable=True)  # Syncro, ConnectWise, etc.
    workflows = Column(JSON, default=list)  # List of workflow objects
    api_configuration = Column(JSON, nullable=True)  # Store API settings if needed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("OnboardingSession", back_populates="msp_integration")

class InternalPolicy(Base):
    __tablename__ = "internal_policies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_sessions.id"), nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default='medium')  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("OnboardingSession", back_populates="policies")

class EscalationProcedure(Base):
    __tablename__ = "escalation_procedures"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_sessions.id"), nullable=False)
    trigger = Column(String, nullable=False)  # What triggers this escalation
    action = Column(Text, nullable=False)  # What action to take
    priority = Column(String, default='medium')  # low, medium, high, critical
    contact_info = Column(JSON, nullable=True)  # Contact details if needed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("OnboardingSession", back_populates="escalations")

class BusinessHours(Base):
    __tablename__ = "business_hours"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_sessions.id"), nullable=False)
    standard = Column(String, nullable=True)  # e.g., "Monday-Friday, 9 AM - 5 PM"
    emergency = Column(String, nullable=True)  # Emergency support hours
    timezone = Column(String, nullable=True)  # e.g., "Eastern Time"
    schedule_details = Column(JSON, nullable=True)  # Detailed schedule if needed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("OnboardingSession", back_populates="business_hours")

class OnboardingTranscript(Base):
    __tablename__ = "onboarding_transcripts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_sessions.id"), nullable=False)
    speaker = Column(String, nullable=False)  # agent, human, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_type = Column(String, default='transcript')  # transcript, system, sop_update
    extra_data = Column(JSON, nullable=True)  # Additional data like sop_update info
    
    # Relationships
    session = relationship("OnboardingSession", back_populates="transcript_messages") 