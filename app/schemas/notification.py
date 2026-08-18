from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    user_id: int
    pantry_item_id: Optional[int]
    message: str
    created_at: datetime
    is_read: bool

    model_config = {"from_attributes": True}
