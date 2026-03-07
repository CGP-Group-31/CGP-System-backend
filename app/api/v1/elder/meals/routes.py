from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from .schemas import (
    UpdateMealStatusRequest,
    TodayMealsResponse,
    MessageResponse,
)
from .repository import get_today_meals_repo, update_meal_status_repo

router = APIRouter(prefix="/meals", tags=["Meals"])


@router.get("/today/{elder_id}", response_model=TodayMealsResponse)
def get_today_meals(elder_id: int, db: Session = Depends(get_db)):
    if elder_id <= 0:
        raise HTTPException(status_code=400, detail="elder_id must be greater than 0")

    rows = get_today_meals_repo(elder_id, db)
    return {"items": rows}


@router.post("/update", response_model=MessageResponse)
def update_meal_status(data: UpdateMealStatusRequest, db: Session = Depends(get_db)):
    affected = update_meal_status_repo(data, db)
    db.commit()

    if affected == 0:
        raise HTTPException(status_code=404, detail="Meal record not found")

    return {"message": "Meal updated"}