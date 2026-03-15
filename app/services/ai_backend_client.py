import httpx
from app.core.config import settings


async def start_ai_checkin(run_id: int, elder_id: int, schedule_name: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{settings.AI_BACKEND_URL}/ai/checkin/start",
            json={
                "run_id": run_id,
                "elder_id": elder_id,
                "schedule_name": schedule_name
            }
        )
        response.raise_for_status()
        return response.json()


async def respond_ai_checkin(run_id: int, elder_id: int, message: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{settings.AI_BACKEND_URL}/ai/checkin/respond",
            json={
                "run_id": run_id,
                "elder_id": elder_id,
                "message": message
            }
        )
        response.raise_for_status()
        return response.json()