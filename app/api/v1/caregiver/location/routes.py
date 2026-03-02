from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from .schemas import LocationResponse, LocationHistoryResponse, LocationLatestResponse
from .repository import last_3_location, latest_location

router=APIRouter(prefix="/location-sharing", tags=["Get Location"])


@router.get("/elder/{elder_id}/latest", response_model=LocationLatestResponse)
def elder_latest_location(elder_id: int, db:Session=Depends(get_db)):
    loc= latest_location(db,elder_id)
    if not loc:
        raise HTTPException(status_code=404, detail="No location found")
    location = LocationResponse(
        location_id=loc["LocationID"],
        elder_id=loc["ElderID"],
        latitude=float(loc["Latitude"]),
        longitude=float(loc["Longitude"]),
        recorded_at=loc["RecordedAt"],
    )
    return{"elder_id": elder_id, "location": location}


@router.get("/elder/{elder_id}/history", response_model=LocationHistoryResponse)
def elder_location_history(elder_id: int, db:Session=Depends(get_db)):
    row= last_3_location(db,elder_id)
    if not row:
        raise HTTPException(status_code=404, detail="No location history found")
    
    history = [LocationResponse(
        location_id=loc["LocationID"],
        elder_id=loc["ElderID"],
        latitude=float(loc["Latitude"]),
        longitude=float(loc["Longitude"]),
        recorded_at=loc["RecordedAt"],
        )
        for loc in row
    ]
    return{"elder_id": elder_id, "history": history}