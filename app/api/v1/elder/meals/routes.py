from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.elder.meals.repository import (
    get_today_meals_repo,
    update_meal_status_repo
)
from app.api.v1.elder.meals.schemas import (
    UpdateMealStatusRequest,
    TodayMealsResponse,
    MessageResponse
)

router = APIRouter(prefix="/meals", tags=["Meals"])


@router.get("/today/{elder_id}", response_model=TodayMealsResponse)
def get_today_meals(
    elder_id: int,
    db: Session = Depends(get_db)
):
    try:
        items = get_today_meals_repo(elder_id, db)
        return {"items": items}

    except Exception as e:
        print("GET TODAY MEALS ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch meals"
        )


@router.post("/update", response_model=MessageResponse)
def update_meal_status(
    data: UpdateMealStatusRequest,
    db: Session = Depends(get_db)
):

    try:

        affected = update_meal_status_repo(data, db)

        if affected == 0:
            raise HTTPException(
                status_code=404,
                detail="Meal record not found"
            )

        db.commit()

        return {"message": "Meal updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("MEAL UPDATE ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail="Database error while updating meal"
        )