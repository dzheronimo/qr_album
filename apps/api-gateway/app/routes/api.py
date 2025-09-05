from fastapi import APIRouter
router = APIRouter(prefix="/api")

@router.get("/me")
async def me():
    # Для MVP возвращаем заглушку
    return {"user": {"id": "u_1", "email": "demo@example.com"}, "plan": {"tier": "FREE"}}
