import secrets

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Account, AuditLog
from app.security.auth import create_session_token, current_account, dummy_password_hash, verify_password
from app.security.entra import account_from_entra_claims
from app.security.roles import Role

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=1024)


class RoleSelection(BaseModel):
    role: Role


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
    return {
        "username": account.display_name or account.username,
        "role": account.role,
        "roles": account.roles or [account.role],
        "csrf_token": csrf_token,
    }


def _entra_client():
    if not settings.entra_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Entra sign-in is not configured")
    oauth = OAuth()
    return oauth.register(
        name="entra",
        client_id=settings.entra_client_id,
        client_secret=settings.entra_client_secret,
        server_metadata_url=f"https://login.microsoftonline.com/{settings.entra_tenant_id}/v2.0/.well-known/openid-configuration",
        client_kwargs={"scope": "openid profile email"},
    )


@router.get("/methods")
def methods():
    return {"entra_enabled": settings.entra_enabled, "local_password_enabled": not settings.entra_enabled}


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    if settings.entra_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Use Microsoft Entra sign-in")
    if len(settings.auth_secret_key) < 32:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication is not configured")
    account = db.get(Account, payload.username)
    password_hash = account.password_hash if account else dummy_password_hash
    valid_password = bool(password_hash and verify_password(password_hash, payload.password))
    if not account or not account.is_active or not valid_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    csrf_token = secrets.token_urlsafe(32)
    _set_cookies(response, account.username, csrf_token)
    return _user_payload(account, csrf_token)


@router.get("/entra/login")
async def entra_login(request: Request):
    client = _entra_client()
    return await client.authorize_redirect(request, settings.entra_redirect_uri)


@router.get("/entra/callback")
async def entra_callback(request: Request, db: Session = Depends(get_db)):
    client = _entra_client()
    try:
        token = await client.authorize_access_token(request)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Microsoft Entra sign-in failed") from exc
    claims = token.get("userinfo")
    if not isinstance(claims, dict):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Entra ID token claims are missing")
    username, roles, display_name = account_from_entra_claims(
        dict(claims), settings.entra_tenant_id, settings.entra_client_id
    )
    active_role = "reviewer" if "reviewer" in roles else roles[0]
    account = db.get(Account, username)
    if account is not None and not account.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    if account is None:
        account = Account(username=username, display_name=display_name, password_hash=None, role=active_role, roles=roles)
        db.add(account)
    else:
        account.display_name = display_name
        account.roles = roles
        if account.role not in roles:
            account.role = active_role
    db.add(AuditLog(actor_role=account.role, action="entra_login", record_type="account", record_id=username))
    db.commit()
    csrf_token = secrets.token_urlsafe(32)
    response = RedirectResponse(settings.auth_frontend_url, status_code=status.HTTP_303_SEE_OTHER)
    _set_cookies(response, username, csrf_token)
    return response


@router.post("/role")
def select_role(
    payload: RoleSelection,
    request: Request,
    response: Response,
    account: Account = Depends(current_account),
    db: Session = Depends(get_db),
):
    allowed_roles = account.roles or [account.role]
    if payload.role.value not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role is not assigned to this account")
    account.role = payload.role.value
    db.add(AuditLog(actor_role=account.role, action="active_role_changed", record_type="account", record_id=account.username))
    db.commit()
    db.refresh(account)
    csrf_token = request.cookies.get("site_csrf", "")
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