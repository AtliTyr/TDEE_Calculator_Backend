from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
import bcrypt

from app.core.config import settings

# =========================
# CONSTANTS
# =========================

ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


# =========================
# PASSWORDS
# =========================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


# =========================
# JWT HELPERS
# =========================

def _create_token(
    *,
    data: dict,
    expires_delta: timedelta,
    token_type: str,
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode = data.copy()
    to_encode.update(
        {
            "exp": int(expire.timestamp()),
            "type": token_type,
        }
    )

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    return _create_token(
        data=data,
        expires_delta=expires_delta
        or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    return _create_token(
        data=data,
        expires_delta=expires_delta
        or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )


# =========================
# TOKEN VERIFICATION
# =========================

def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if payload.get("type") != "access":
            raise JWTError("Invalid token type")

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
