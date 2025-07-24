from pydantic import BaseModel


class PastTicket(BaseModel):
    id: str | None = None
    subject: str | None = None
    status: str | None = None
    comments: str | None = None


class TicketResponse(BaseModel):
    id: str | None = None
    subject: str | None = None
    url: str | None = None
