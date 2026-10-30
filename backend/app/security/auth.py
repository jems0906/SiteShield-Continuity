from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from fastapi import Depends, HTTPException, Request, status
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Account

password_hasher = PasswordHasher()
dummy_password_hash = password_hasher.hash("not-a-valid-site-shield-password")


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Passwords must contain at least 12 characters.")
    return password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except VerificationError:
        return False


def _serializer() -> URLSafeTimedSerializer:
    if len(settings.auth_secret_key) < 32:
        raise RuntimeError("AUTH_SECRET_KEY must contain at least 32 characters.")
    return URLSafeTimedSerializer(settings.auth_secret_key, salt="siteshield-session")


def create_session_token(username: str) -> str:
    return _serializer().dumps({"sub": username})


def current_account(request: Request, db: Session = Depends(get_db)) -> Account:
    token = request.cookies.get("site_session")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign-in required")
    try:
        payload = _serializer().loads(token, max_age=settings.auth_session_seconds)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication is not configured") from exc
    except BadSignature as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid or expired") from exc
    username = payload.get("sub") if isinstance(payload, dict) else None
    account = db.get(Account, username) if isinstance(username, str) else None
    if not account or not account.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid or expired")
    return account