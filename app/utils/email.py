from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from app.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


async def send_reset_email(email: str, link: str) -> None:
    message = MessageSchema(
        subject="Password Reset — Medical History API",
        recipients=[email],
        body=f"Click the link below to reset your password:\n\n{link}\n\nThis link expires in 1 hour.",
        subtype=MessageType.plain,
    )
    fm = FastMail(conf)
    await fm.send_message(message)