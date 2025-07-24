from datetime import time

from pydantic import BaseModel, ConfigDict, Field

from api.models.phone_number import PhoneNumberResponse
from domain.model.models_domain import CommunicationChannel


class VoiceResponse(BaseModel):
    id: str
    voice_type: str
    audio_url: str
    gender: str | None = None
    accent: str | None = None


class CustomerResponse(BaseModel):
    id: int | None = None
    name: str | None = None
    type: str | None = None


class AgentBase(BaseModel):
    name: str
    first_message: str
    sops: str
    communication_channel: CommunicationChannel = CommunicationChannel.INBOUND_CALL
    closing_statement: str | None = None


class HumanAgentAvailabilityBase(BaseModel):
    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time


class AgentSettingsBase(BaseModel):
    timezone: str
    human_agent_availability: list[HumanAgentAvailabilityBase] = Field(min_length=0)
    business_hours_call_transfer: bool
    business_hours_call_transfer_phone_number: str | None = None
    business_hours_call_transfer_contact_name: str | None = None
    business_hours_call_transfer_contact_id: int | None = None
    emergency_call_transfer: bool
    emergency_call_transfer_phone_number: str | None = None
    emergency_call_transfer_contact_name: str | None = None
    emergency_call_transfer_contact_id: int | None = None
    emergency_text_message: bool
    emergency_text_message_phone_number: str | None = None
    emergency_text_message_contact_name: str | None = None
    emergency_text_message_contact_id: int | None = None
    after_hours_call_transfer: bool
    after_hours_call_transfer_phone_number: str | None = None
    after_hours_call_transfer_contact_name: str | None = None
    after_hours_call_transfer_contact_id: int | None = None
    after_hours_text_message: bool
    after_hours_text_message_phone_number: str | None = None
    after_hours_text_message_contact_name: str | None = None
    after_hours_text_message_contact_id: int | None = None


class AgentCreateRequest(AgentBase):
    phone_number_ids: list[str]
    customer_ids: list[int]
    voice_id: str
    settings: AgentSettingsBase

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Lionel Messi",
                    "first_message": "This is the first message",
                    "sops": "This is the sops",
                    "voice_id": "1234abcd-1234-abcd-1234-abcd12345678",
                    "communication_channel": "sms",
                    "phone_number_ids": [
                        "1234abcd-1234-abcd-1234-abcd12345671",
                        "1234abcd-1234-abcd-1234-abcd12345672",
                        "1234abcd-1234-abcd-1234-abcd12345673",
                    ],
                    "settings": {
                        "timezone": "America/Los_Angeles",
                        "human_agent_availability": [
                            {"weekday": 1, "start_time": "09:00", "end_time": "17:00"},
                            {"weekday": 3, "start_time": "10:00", "end_time": "17:00"},
                            {"weekday": 4, "start_time": "12:00", "end_time": "15:00"},
                            {"weekday": 5, "start_time": "09:00", "end_time": "17:00"},
                        ],
                        "business_hours_call_transfer": True,
                        "business_hours_call_transfer_phone_number": "+1234567890",
                        "business_hours_call_transfer_contact_name": "John Wick",
                        "emergency_call_transfer": True,
                        "emergency_call_transfer_contact_id": 123,
                        "emergency_text_message": True,
                        "emergency_text_message_contact_id": 345,
                        "after_hours_call_transfer": True,
                        "after_hours_call_transfer_phone_number": "+1234567890",
                        "after_hours_call_transfer_contact_name": "Leo Messi",
                        "after_hours_text_message": True,
                        "after_hours_text_message_phone_number": "+1234567890",
                        "after_hours_text_message_contact_name": "Cristiano Ronaldo",
                    },
                    "customer_ids": [123424, 2345345, 354466],
                }
            ]
        }
    )


class AgentSettingsUpdateRequest(BaseModel):
    timezone: str | None = None
    human_agent_availability: list[HumanAgentAvailabilityBase] | None = Field(
        None, min_length=0
    )
    business_hours_call_transfer: bool | None = None
    business_hours_call_transfer_phone_number: str | None = None
    business_hours_call_transfer_contact_name: str | None = None
    business_hours_call_transfer_contact_id: int | None = None
    emergency_call_transfer: bool | None = None
    emergency_call_transfer_phone_number: str | None = None
    emergency_call_transfer_contact_name: str | None = None
    emergency_call_transfer_contact_id: int | None = None
    emergency_text_message: bool | None = None
    emergency_text_message_phone_number: str | None = None
    emergency_text_message_contact_name: str | None = None
    emergency_text_message_contact_id: int | None = None
    after_hours_call_transfer: bool | None = None
    after_hours_call_transfer_phone_number: str | None = None
    after_hours_call_transfer_contact_name: str | None = None
    after_hours_call_transfer_contact_id: int | None = None
    after_hours_text_message: bool | None = None
    after_hours_text_message_phone_number: str | None = None
    after_hours_text_message_contact_name: str | None = None
    after_hours_text_message_contact_id: int | None = None


class AgentUpdateRequest(BaseModel):
    name: str | None = None
    first_message: str | None = None
    sops: str | None = None
    closing_statement: str | None = None
    phone_number_ids: list[str] | None = None
    customer_ids: list[int] | None = None
    voice_id: str | None = None
    settings: AgentSettingsUpdateRequest | None = None


class AgentResponse(AgentBase):
    id: str
    phone_numbers: list[PhoneNumberResponse]
    customers: list[CustomerResponse]
    voice: VoiceResponse
    settings: AgentSettingsBase

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "7ac06486-4286-4e66-be4a-2e4de0dd9586",
                    "name": "Lionel Messi",
                    "first_message": "This is the first message",
                    "sops": "This is the sops",
                    "communication_channel": "sms",
                    "voice": {
                        "id": "1234abcd-1234-abcd-1234-abcd12345678",
                        "voice_type": "voice",
                        "audio_url": "https://example.com/audio.mp3",
                    },
                    "phone_numbers": [
                        {
                            "id": "1234abcd-1234-abcd-1234-abcd12345671",
                            "phone_number": "234567890",
                            "country_code": "+1",
                        }
                    ],
                    "settings": {
                        "timezone": "America/Los_Angeles",
                        "human_agent_availability": [
                            {"weekday": 1, "start_time": "09:00", "end_time": "17:00"},
                            {"weekday": 3, "start_time": "10:00", "end_time": "17:00"},
                            {"weekday": 4, "start_time": "12:00", "end_time": "15:00"},
                            {"weekday": 5, "start_time": "09:00", "end_time": "17:00"},
                        ],
                        "business_hours_call_transfer": True,
                        "business_hours_call_transfer_phone_number": "+1234567890",
                        "emergency_call_transfer": True,
                        "emergency_call_transfer_phone_number": "+1234567890",
                        "emergency_text_message": True,
                        "emergency_text_message_phone_number": "+1234567890",
                        "after_hours_call_transfer": True,
                        "after_hours_call_transfer_phone_number": "+1234567890",
                        "after_hours_text_message": True,
                        "after_hours_text_message_phone_number": "+1234567890",
                    },
                    "customers": [
                        {
                            "id": 123424,
                            "name": "Dental Clinic Name",
                            "type": "individual",
                        }
                    ],
                }
            ]
        }
    )


class PaginatedAgentsResponse(BaseModel):
    agents: list[AgentResponse]
    total: int
