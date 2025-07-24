from pydantic import BaseModel


class LookupCustomerResponse(BaseModel):
    customer_id: int
    contact_id: int
    contact_name: str
    unknown_contact_name: str | None = None
    customer_assets: dict
    past_issues: list[dict]
