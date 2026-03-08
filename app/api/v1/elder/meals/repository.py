from sqlalchemy import text
from sqlalchemy.orm import Session


def get_today_meals_repo(elder_id: int, db: Session):
    q = text("""SELECT MealAdherenceID, ElderID, MealTime, ScheduledFor, StatusID, Diet, UpdatedAt
        FROM MealAdherence WHERE ElderID = :eid
          AND CAST(ScheduledFor AS date) = CAST(GETDATE() AS date)
        ORDER BY ScheduledFor ASC""")

    rows = db.execute(q, {"eid": elder_id}).mappings().all()
    return rows


def update_meal_status_repo(data, db: Session):
    q = text("""UPDATE MealAdherence
        SET
            StatusID = :status_id,
            Diet = :diet,
            UpdatedAt = GETDATE() WHERE ElderID = :eid
          AND MealTime = :mt
          AND ScheduledFor = :sf""")

    result = db.execute(q, {
        "status_id": data.statusId,
        "diet": data.diet or None,
        "eid": data.elderId,
        "mt": data.mealTime,
        "sf": data.scheduledFor,
    })

    return result.rowcount