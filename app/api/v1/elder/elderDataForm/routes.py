from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from .schemas import (
    ElderFormCreate,
    ElderFormCreateResponse,
    ElderFormResponse,
)
from .repository import (
    insert_elder_form,
    get_latest_elder_form,
)

router = APIRouter(prefix="/elder-form", tags=["Elder Form"])


@router.post("/", response_model=ElderFormCreateResponse)
def create_elder_form(data: ElderFormCreate, db: Session = Depends(get_db)):
    try:
        row = insert_elder_form(db, data)
        db.commit()
        return row

    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{elder_id}/latest", response_model=ElderFormResponse)
def fetch_latest_elder_form(elder_id: int, db: Session = Depends(get_db)):
    try:
        row = get_latest_elder_form(db, elder_id)

        if not row:
            raise HTTPException(status_code=404, detail="No elder form found")

        return row

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))