from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from .schemas import LocationShareRequest
from .repository import share_location

router=APIRouter(prefix="/location-sharing", tags=["Elder share Location"])


@router.post("/share")
def share_location_api(data: LocationShareRequest, db:Session=Depends(get_db)):
    loc= share_location(db,data)
    if not loc:
        raise HTTPException(status_code=400, detail="Failed to share location")
    db.commit()
    return{"message": "Location shared"}


