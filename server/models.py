from pydantic import BaseModel, Field
from typing import Dict, List

class RoundCreate(BaseModel):
    date: str          
    min_participants: int = 3

class Contribution(BaseModel):
    client_id: str
    date: str
    total_screen_time_minutes: float = Field(ge=0)
    app_usage_minutes: Dict[str, float] = {}

class RoundStatus(BaseModel):
    round_id: str
    date: str
    expected_clients: int
    received: int
    valid_clients: List[str]
    status: str


class AppUsageItem(BaseModel):
    app_id: str
    total_minutes: float

class RoundResult(BaseModel):
    round_id: str
    date: str
    status: str
    participants_used: int
    average_screen_time_minutes: float | None
    app_ranking: list[AppUsageItem] | None
    released: bool
    reason: str | None = None