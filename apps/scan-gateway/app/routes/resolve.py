from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import RedirectResponse

router = APIRouter()

# MVP: сразу редиректим на публичную страницу (заглушка)
@router.get("/r/{slug}")
async def resolve(slug: str):
    # Здесь должен быть запрос в qr-svc, получение target и логирование события
    # Пока редиректим на демонстрационную страницу
    return RedirectResponse(url=f"https://example.com/page/{slug}", status_code=302)
