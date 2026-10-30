import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Account
from app.security.auth import create_session_token, current_account, dummy_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=1024)


def _set_cookies(response: Response, username: str, csrf_token: str) -> None:
    common = {
        "secure": settings.auth_cookie_secure,
        "samesite": settings.auth_cookie_samesite,
        "max_age": settings.auth_session_seconds,
        "path": "/api",
    }
    response.set_cookie("site_session", create_session_token(username), httponly=True, **common)
    response.set_cookie("site_csrf", csrf_token, httponly=False, **common)


def _user_payload(account: Account, csrf_token: str) -> dict[str, str]:
    return {"username": account.username, "role": account.role, "csrf_token": csrf_token}


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    if len(settings.auth_secret_key) < 32:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication is not configured")
    account = db.get(Account, payload.username)
    password_hash = account.password_hash if account else dummy_password_hash
    valid_password = verify_password(password_hash, payload.password)
    if not account or not account.is_active or not valid_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    csrf_token = secrets.token_urlsafe(32)
    _set_cookies(response, account.username, csrf_token)
    return _user_payload(account, csrf_token)


@router.get("/me")
def me(request: Request, response: Response, account: Account = Depends(current_account)):
    csrf_token = request.cookies.get("site_csrf") or secrets.token_urlsafe(32)
    if not request.cookies.get("site_csrf"):
        _set_cookies(response, account.username, csrf_token)
    return _user_payload(account, csrf_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie("site_session", path="/api", secure=settings.auth_cookie_secure, samesite=settings.auth_cookie_samesite)
    response.delete_cookie("site_csrf", path="/api", secure=settings.auth_cookie_secure, samesite=settings.auth_cookie_samesite)
    response.status_code = status.HTTP_204_NO_CONTENT