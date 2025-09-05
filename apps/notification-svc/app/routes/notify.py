from fastapi import APIRouter
from pydantic import BaseModel
import smtplib, os

router = APIRouter(prefix="/notify", tags=["notify"])

class EmailMessage(BaseModel):
    to: str
    subject: str
    text: str

@router.post("/email")
async def send_email(msg: EmailMessage):
    # Demo via local SMTP (e.g., MailHog)
    host = os.getenv("SMTP_HOST", "mailhog")
    port = int(os.getenv("SMTP_PORT", "1025"))
    sender = os.getenv("SMTP_FROM", "noreply@qr.local")
    with smtplib.SMTP(host, port) as s:
        s.sendmail(sender, [msg.to], f"Subject: {msg.subject}\n\n{msg.text}")
    return {"ok": True}
