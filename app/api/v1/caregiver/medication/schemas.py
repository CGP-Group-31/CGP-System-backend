# app/modules/medication/schemas.py
from pydantic import BaseModel, field_validator, model_validator
from datetime import date
from typing import List, Optional
import re

VALID_DAYS = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


class MedicationCreateRequest(BaseModel):
    elderId: int
    caregiverId: int
    name: str
    dosage: str
    instructions: str

    times: List[str]
    repeatDays: str
    startDate: date
    endDate: Optional[date] = None

    @field_validator("times")
    @classmethod
    def validate_times(cls, v: List[str]):
        if not v:
            raise ValueError("times cannot be empty")

        if len(v) > 6:
            raise ValueError("max 6 times per day allowed")

        clean = []
        seen = set()

        for t in v:
            t = t.strip()

            if not TIME_RE.match(t):
                raise ValueError(f"invalid time format: {t}")

            if t not in seen:
                seen.add(t)
                clean.append(t)

        clean.sort()
        return clean

    @field_validator("repeatDays")
    @classmethod
    def validate_repeat_days(cls, v: str):

        v = v.strip()

        if v in ("Daily", "EveryOtherDay"):
            return v

        parts = [p.strip() for p in v.split(",") if p.strip()]

        invalid = [p for p in parts if p not in VALID_DAYS]

        if invalid:
            raise ValueError(f"invalid repeat day(s): {','.join(invalid)}")

        order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        parts = sorted(set(parts), key=lambda d: order.index(d))

        return ",".join(parts)

    @model_validator(mode="after")
    def validate_dates(self):

        if self.endDate and self.endDate < self.startDate:
            raise ValueError("endDate must be >= startDate")

        return self


class MedicationCreateResponse(BaseModel):
    medicationId: int
    elderId: int
    name: str
    dosage: str
    instructions: str
    times: List[str]
    repeatDays: str
    startDate: date
    endDate: Optional[date] = None


class MedicationUpdateRequest(BaseModel):

    name: str
    dosage: str
    instructions: str

    times: List[str]
    repeatDays: str

    startDate: date
    endDate: Optional[date] = None

    _validate_times = MedicationCreateRequest.validate_times
    _validate_repeat = MedicationCreateRequest.validate_repeat_days