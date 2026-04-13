from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.config import settings

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def generate_reset_token(email: str) -> str:
    return serializer.dumps(email, salt="reset-password")


def verify_reset_token(token: str, max_age: int = 3600) -> str | None:
    try:
        email: str = serializer.loads(token, salt="reset-password", max_age=max_age)
        return email
    except (BadSignature, SignatureExpired):
        return None