from pydantic import BaseModel


class IntStatResponse(BaseModel):
    value: int
    delta_value: int | None = None


class OverviewTotalsResponse(BaseModel):
    total_contacts_handled: IntStatResponse
    total_hours_saved: IntStatResponse
    global_sentiment_score: IntStatResponse


class CustomerSentimentResponse(BaseModel):
    customer_name: str
    score: int


class DateToSentimentResponse(BaseModel):
    sentiment_date: str
    sentiment_value: float


class SentimentScoreResponse(BaseModel):
    top_negative_scores: list[CustomerSentimentResponse]
    trend: list[DateToSentimentResponse]


class DateToTimeSavedResponse(BaseModel):
    time_saved_date: str
    time_saved_in_minutes: int


class StaffTimeSavedResponse(BaseModel):
    total_cost_savings: float
    time_saved: list[DateToTimeSavedResponse]


class CommonIssueResponse(BaseModel):
    category: str
    count: int
