from pydantic import BaseModel


class StripeCheckoutSessionDTO(BaseModel):
    checkout_session_url: str


class SubscriptionResponse(BaseModel):
    id: str
    name: str
    max_credits: int
    credit_type: str
    description: str | None = None
    price: float | None = None


class UserSubscriptionResponse(BaseModel):
    subscription: SubscriptionResponse
    credits_left: int
    status: str
    current_period_end: str | None = None
    stripe_subscription_id: str | None = None


class CreateCheckoutSessionRequest(BaseModel):
    subscription_id: str
    success_url: str
    cancel_url: str


class CancelSubscriptionResponse(BaseModel):
    success: bool
    message: str
