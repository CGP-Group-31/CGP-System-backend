import httpx
from app.core.config import settings


async def trigger_daily_report_generation(elder_id: int, report_date: str) -> dict:
    url = f"{settings.AI_BACKEND_URL}/reports/daily/generate"

    payload = {
        "elder_id": elder_id,
        "report_date": report_date
    }

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(url, json=payload)

    response.raise_for_status()
    return response.json()


async def trigger_weekly_report_generation(elder_id: int, week_start: str, week_end: str):

    url = f"{settings.AI_BACKEND_URL}/reports/weekly/generate"

    payload = {
        "elder_id": elder_id,
        "week_start": week_start,
        "week_end": week_end
    }

    async with httpx.AsyncClient(timeout=60) as client:
        await client.post(url, json=payload)