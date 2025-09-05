from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/print", tags=["print"])

@router.post("/labels", response_class=PlainTextResponse)
async def gen_labels():
    # Заглушка: возвращаем текст вместо PDF; подключите WeasyPrint для реального PDF
    return "PDF labels job accepted"
