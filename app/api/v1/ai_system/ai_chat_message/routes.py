from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from .repository import get_chat_messages_by_elder
from .schemas import ChatMessageListResponse

router = APIRouter(prefix="/chat-messages", tags=["Chat Messages"])


@router.get("/elder/{elder_id}", response_model=ChatMessageListResponse, status_code=200)
def get_chat_messages_by_elder_api(
    elder_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    messages, error = get_chat_messages_by_elder(db, elder_id, limit)

    if error:
        if error == "Elder not found.":
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=400, detail=error)

    return {"messages": messages}