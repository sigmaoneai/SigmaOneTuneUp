from pydantic import BaseModel, ConfigDict


INBOUND_TEMPLATE_REQUEST_EXAMPLE = {
    "first_message": "This is the first message",
    "sops": "This is the sops",
    "closing_statement": "This is the closing statement",
    "name": "This is the name of the template",
    "description": "This is the description of the template",
}


INBOUND_TEMPLATE_RESPONSE_EXAMPLE = {
    **INBOUND_TEMPLATE_REQUEST_EXAMPLE,
    "id": "039ad4cc-3b5e-48a8-84f5-b82b6f2a9827",
    "created_at": "2023-01-01T00:00:00Z",
}


OUTBOUND_TEMPLATE_REQUEST_EXAMPLE = {
    "name": "This is the name of the template",
    "description": "This is the description of the template",
    "sops": "This is the sops",
}


OUTBOUND_TEMPLATE_RESPONSE_EXAMPLE = {
    **OUTBOUND_TEMPLATE_REQUEST_EXAMPLE,
    "id": "039ad4cc-3b5e-48a8-84f5-b82b6f2a9827",
    "created_at": "2023-01-01T00:00:00Z",
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
}


class InboundTemplateCreateRequest(BaseModel):
    name: str
    first_message: str
    sops: str
    closing_statement: str
    description: str | None = None

    model_config = ConfigDict(
        json_schema_extra={"examples": [INBOUND_TEMPLATE_REQUEST_EXAMPLE]}
    )


class InboundTemplateResponse(BaseModel):
    first_message: str
    sops: str
    closing_statement: str
    id: str
    created_at: str
    name: str | None = None
    description: str | None = None
    model_config = ConfigDict(
        json_schema_extra={"examples": [INBOUND_TEMPLATE_RESPONSE_EXAMPLE]}
    )


class OutboundTemplateCreateRequest(BaseModel):
    name: str
    sops: str
    description: str | None = None

    model_config = ConfigDict(
        json_schema_extra={"examples": [OUTBOUND_TEMPLATE_REQUEST_EXAMPLE]}
    )


class OutboundTemplateUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    sops: str | None = None
    model_config = ConfigDict(
        json_schema_extra={"examples": [OUTBOUND_TEMPLATE_REQUEST_EXAMPLE]}
    )


class OutboundTemplateResponse(BaseModel):
    id: str
    created_at: str
    sops: str
    user_id: str
    name: str | None = None
    description: str | None = None
    model_config = ConfigDict(
        json_schema_extra={"examples": [OUTBOUND_TEMPLATE_RESPONSE_EXAMPLE]}
    )
