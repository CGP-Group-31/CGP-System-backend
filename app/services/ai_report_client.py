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