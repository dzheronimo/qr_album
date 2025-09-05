from fastapi import APIRouter
router = APIRouter(prefix="/moderation", tags=["moderation"])

@router.post("/scan/{media_id}")
async def scan_media(media_id: str):
    return {"media_id": media_id, "safe": True, "labels": []}
