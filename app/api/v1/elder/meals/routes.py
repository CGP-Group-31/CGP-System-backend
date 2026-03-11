from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Literal
from datetime import datetime

from app.core.database import get_db

router = APIRouter(prefix="/meals", tags=["Meals"])


class UpdateMealStatusRequest(BaseModel):
    elderId: int = Field(..., gt=0)
    mealTime: Literal["BREAKFAST", "LUNCH", "DINNER"]
    scheduledFor: datetime
    status: Literal["TAKEN", "MISSED"]
    diet: str | None = None


@router.get("/today/{elder_id}")
def get_today_meals(elder_id: int, db: Session = Depends(get_db)):
    q = text("""
        SELECT 
            m.MealAdherenceID,
            m.ElderID,
            m.MealTime,
            m.ScheduledFor,
            s.StatusName AS Status,
            m.Diet,
            m.UpdatedAt
        FROM MealAdherence m
        JOIN Status s ON m.StatusID = s.StatusID
        WHERE m.ElderID = :eid
          AND CAST(m.ScheduledFor AS date) = CAST(GETDATE() AS date)
        ORDER BY m.ScheduledFor ASC;
    """)

    rows = db.execute(q, {"eid": elder_id}).mappings().all()
    return {"items": rows}


@router.post("/update")
def update_meal_status(data: UpdateMealStatusRequest, db: Session = Depends(get_db)):
    try:
        meal_time = data.mealTime.strip().upper()
        status_text = data.status.strip().upper()

        status_map = {
            "TAKEN": 2,
            "MISSED": 4,
        }

        if status_text not in status_map:
            raise HTTPException(status_code=400, detail="status must be TAKEN or MISSED")

        status_id = status_map[status_text]

        q = text("""
            UPDATE MealAdherence
            SET StatusID = :status_id,
                Diet = :diet,
                UpdatedAt = GETDATE()
            WHERE ElderID = :eid
              AND MealTime = :mt
              AND ScheduledFor = :sf
        """)

        result = db.execute(q, {
            "status_id": status_id,
            "diet": data.diet,
            "eid": data.elderId,
            "mt": meal_time,
            "sf": data.scheduledFor,
        })

        db.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Meal record not found")

        return {"message": "Meal updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("MEAL UPDATE ERROR:", e)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")