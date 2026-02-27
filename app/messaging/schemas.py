from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class SendMessageIn(BaseModel):
    relationship_id: int
    sender_id: int
    message_text: str = Field(min_length=1, max_length=5000)

class MessageOut(BaseModel):
    message_id: int
    relationship_id: int
    sender_id: int
    message_text: Optional[str]
    is_read: bool
    sent_at: datetime

class MessagesListOut(BaseModel):
    relationship_id: int
    messages: List[MessageOut]

class MarkReadIn(BaseModel):
    relationship_id: int
    reader_id: int
    message_ids: List[int]