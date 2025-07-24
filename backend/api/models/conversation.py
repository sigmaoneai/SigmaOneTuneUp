from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConversationResponse(BaseModel):
    id: str

    customer_name: str | None = None
    customer_contact_name: str | None = None
    customer_phone_number: str | None = None
    agent_name: str | None = None
    agent_phone_number: str | None = None

    ticket_number: str | None = None
    ticket_url: str | None = None

    conversation_type: str | None = None
    summary: str | None = None
    recording_url: str | None = None
    sentiment: str | None = None
    potential_issues: str | None = None
    issue_category: str | None = None
    recommended_next_steps: str | None = None
    transcript: str | None = None

    duration: float | None = None
    total_cost: float | None = None
    created_at: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "88bbfbbb-e5ec-4ab8-a209-8403f91612bd",
                    "customer_name": "Dental Clinic #1",
                    "customer_contact_name": "Emma Smith",
                    "customer_phone_number": "+123-456-7899",
                    "agent_name": "Andy Lane",
                    "agent_phone_number": "+123-456-7888",
                    "ticket_number": "435843990",
                    "ticket_url": "http://example.com/435843990",
                    "conversation_type": "voice",
                    "summary": "Lorem ipsum dolor sit amet",
                    "recording_url": "http://example.com/recording.wav",
                    "sentiment": "positive",
                    "potential_issues": "Lorem ipsum dolor sit amet",
                    "recommended_next_steps": "Lorem ipsum dolor sit amet",
                    "transcript": "Lorem ipsum dolor sit amet",
                    "duration": 102,
                    "total_costs": "1.35",
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ]
        }
    )


class PaginatedConversationsResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int


class OptionValueText(BaseModel):
    value: str
    text: str


class ConversationFilterValuesResponse(BaseModel):
    customer_names: list[OptionValueText]
    customer_contact_names: list[OptionValueText]
    agent_names: list[OptionValueText]
    types: list[OptionValueText]
    sentiments: list[OptionValueText]


class DemoCallCustomerDetailsRequest(BaseModel):
    name: str
    email: str
    company_name: str
    phone_number: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "phone_number": "123-456-7899",
                    "name": "John Smith",
                    "company_name": "Name of company",
                    "email": "mail@example.com",
                }
            ]
        }
    }


class CallTransferPhoneNumberDetail(BaseModel):
    phone_number: str | None = None
    description: str | None = None
    contact_name: str | None = None
    contact_id: int | None = None


class SendCallRequest(BaseModel):
    ticket_id: str
    from_number_id: str
    to_number: str | None = None
    contact_name: str | None = None
    contact_id: int | None = None
    instructions: str
    call_transfer: bool
    call_transfer_phone_numbers: list[CallTransferPhoneNumberDetail] | None = None
    scheduled: bool
    scheduled_at: datetime | None = None
    timezone: str | None = None
