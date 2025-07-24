from pydantic import BaseModel, ConfigDict


class IndustryResponse(BaseModel):
    id: int
    name: str


class IntegrationResponse(BaseModel):
    id: str
    name: str
    logo: str


class UserIntegrationResponse(BaseModel):
    integration_id: str
    api_url: str
    api_key: str


class UserIntegrationCreateUpdateRequest(BaseModel):
    integration_id: str
    api_url: str
    api_key: str | None = None
    client_id: str | None = None
    private_key: str | None = None
    public_key: str | None = None
    company_id: str | None = None
    confirm: bool | None = False


class UserResponse(BaseModel):
    id: str | None = None
    name: str | None = None
    email: str | None = None
    company_name: str | None = None
    industries: list[IndustryResponse] | None = None
    has_integration: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "29e20576-f322-4a54-9488-accc1e7c3e7e",
                    "name": "Lionel Messi",
                    "email": "mail@example.com",
                    "company_name": "FC Barcelona",
                    "industries": [
                        {"id": 1, "name": "Dental"},
                        {"id": 3, "name": "Healthcare"},
                    ],
                    "has_integration": True,
                }
            ]
        }
    )


class UserUpdateRequest(BaseModel):
    name: str
    company_name: str
    email: str
    industries_ids: list[int]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Lionel Messi",
                    "company_name": "FC Barcelona",
                    "email": "mail@example.com",
                    "industries_ids": [1, 2],
                }
            ]
        }
    )


class UserOnboardingRequest(BaseModel):
    """
    Flexible model for onboarding data - all fields optional
    to handle partial form submissions during signup process
    """
    name: str | None = None
    company_name: str | None = None
    email: str | None = None
    industries_ids: list[int] | None = None
    industries: list[str] | None = None  # Support both formats

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "John Doe",
                    "company_name": "Chatty AI",
                    "email": "john@chatty.ai",
                    "industries_ids": [1],
                },
                {
                    "company_name": "Dental Clinic",
                    "industries": ["dental"]
                }
            ]
        }
    )
