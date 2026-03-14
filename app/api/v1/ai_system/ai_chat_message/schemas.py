from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel


class ChatMessageItem(BaseModel):
    message_id: int
    thread_id: int
    elder_id: int
    role: Literal["elder", "assistant", "system"]
    content: str
    created_at: datetime
    detected_mood_id: Optional[int] = None


class ChatMessageListResponse(BaseModel):
    messages: List[ChatMessageItem]