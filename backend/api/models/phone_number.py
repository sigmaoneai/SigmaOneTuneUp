from pydantic import BaseModel, ConfigDict

from domain.model.phone_number.phone_number import PhoneNumberType


class PhoneNumberResponse(BaseModel):
    id: str
    phone_number: str
    country_code: str
    full_phone_number: str | None = None
    user_id: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "039ad4cc-3b5e-48a8-84f5-b82b6f2a9827",
                    "phone_number": "23456789",
                    "country_code": "1",
                    "full_phone_number": "+123456789",
                    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                }
            ]
        }
    )


class BuyPhoneNumbersRequest(BaseModel):
    phone_number_ids: list[str]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "phone_number_ids": [
                        "039ad4cc-3b5e-48a8-84f5-b82b6f2a9827",
                        "67de94cc-3b5e-48a8-84f5-b82b6f2a9827",
                    ],
                }
            ]
        }
    )


class BuyPhoneNumbersResponse(BaseModel):
    stripe_url: str

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"stripe_url": "http://example.com"}]}
    )


class PhoneNumberCreate(BaseModel):
    phone_number: int
    country_code: int
    phone_number_type: PhoneNumberType
    user_email: str | None = None
    description: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "phone_number": "23456789",
                    "country_code": "1",
                    "phone_number_type": 1,
                    "user_email": "example@gmail.com",
                    "description": "",
                }
            ]
        }
    )


class PhoneCallContactResponse(BaseModel):
    id: int
    contact_name: str | None = None
    description: str | None = None
    phone_number: PhoneNumberResponse

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 123,
                    "contact_name": "John Smith",
                    "description": "If person wants to talk to sales person",
                    "phone_number": {
                        "id": "039ad4cc-3b5e-48a8-84f5-b82b6f2a9827",
                        "phone_number": "23456789",
                        "country_code": "1",
                        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    },
                }
            ]
        }
    )
