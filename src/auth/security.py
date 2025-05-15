from datetime import UTC, datetime, timedelta

import bcrypt
from authlib.jose import jwt
from fastapi import HTTPException, status

from src.config import settings


def create_access_token(email: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"exp": expire, "sub": str(email)}
    header = {"alg": "HS256"}

    encoded_jwt = jwt.encode(header, payload, settings.JWT_TOKEN).decode("utf-8")
    return encoded_jwt


def decode_token(token: str):
    try:
        claims = jwt.decode(token, settings.JWT_TOKEN)
        claims.validate()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from None
    else:
        return claims["sub"]


async def verify_password(password: str, password_in_db: bytes) -> bool:
    password_bytes = bytes(password, "utf-8")
    return bcrypt.checkpw(password_bytes, password_in_db)


def hash_password(password: str) -> bytes:
    pw = bytes(password, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)
