from fastapi import APIRouter, Depends
from typing import Annotated

from app.controllers.notification_crud import send_email_notification

router = APIRouter()


@router.post("/send-notification")
def send_notification(message : Annotated[str, Depends(send_email_notification)]):
    return message