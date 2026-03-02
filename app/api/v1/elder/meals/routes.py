# app/api/v1/elder/meals/routes.py
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix="/meals", tags=["Meals"])


class UpdateMealStatusRequest(BaseModel):
    elderId: int = Field(..., gt=0)
    mealTime: str  # BREAKFAST/LUNCH/DINNER
    scheduledFor: str  # ISO string
    status: str  # TAKEN or MISSED
    diet: str | None = None


@router.get("/today/{elder_id}")
def get_today_meals(elder_id: int, db: Session = Depends(get_db)):
    q = text("""SELECT MealAdherenceID, ElderID, MealTime, ScheduledFor, Status, Diet, UpdatedAt
        FROM MealAdherence
        WHERE ElderID = :eid
          AND CAST(ScheduledFor AS date) = CAST(GETDATE() AS date)
        ORDER BY ScheduledFor ASC;""")
    rows = db.execute(q, {"eid": elder_id}).mappings().all()
    return {"items": rows}


@router.post("/update")
def update_meal_status(data: UpdateMealStatusRequest, db: Session = Depends(get_db)):
    status = data.status.strip().upper()
    meal_time = data.mealTime.strip().upper()

    if status not in ("TAKEN", "MISSED"):
        raise HTTPException(status_code=400, detail="status must be TAKEN or MISSED")
    if meal_time not in ("BREAKFAST", "LUNCH", "DINNER"):
        raise HTTPException(status_code=400, detail="mealTime invalid")

    q = text("""UPDATE MealAdherence SET Status = :st,
            Diet = :diet,
            UpdatedAt = GETDATE()
        WHERE ElderID = :eid
          AND MealTime = :mt
          AND ScheduledFor = :sf;

        SELECT @@ROWCOUNT AS affected;""")

    row = db.execute(q, {
        "st": status,
        "diet": (data.diet or None),
        "eid": data.elderId,
        "mt": meal_time,
        "sf": data.scheduledFor,
    }).fetchone()

    db.commit()

    if not row or row.affected == 0:
        raise HTTPException(status_code=404, detail="Meal record not found")

    return {"message": "Meal updated"}