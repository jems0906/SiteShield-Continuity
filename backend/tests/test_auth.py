import pytest
from fastapi import HTTPException

from app.api.routes import auth as auth_routes
from app.models import Account
from app.security.auth import hash_password
from app.security.entra import account_from_entra_claims


def test_forged_role_header_does_not_authenticate(client):
    client_api, _ = client
    response = client_api.get("/api/assets", headers={"X-Demo-Role": "leadership"})
    assert response.status_code == 401


def test_login_sets_authenticated_session_and_logout_requires_csrf(client):
    client_api, factory = client
    with factory() as db:
        db.add(Account(username="reviewer", password_hash=hash_password("correct-horse-battery-staple"), role="reviewer"))
        db.commit()

    login = client_api.post("/api/auth/login", json={"username": "reviewer", "password": "correct-horse-battery-staple"})
    assert login.status_code == 200
    assert login.json()["role"] == "reviewer"
    assert "site_session" in login.cookies
    assert "httponly" in login.headers["set-cookie"].lower()

    identity = client_api.get("/api/auth/me")
    assert identity.status_code == 200
    assert identity.json()["username"] == "reviewer"

    csrf_token = login.json()["csrf_token"]
    rejected_logout = client_api.post("/api/auth/logout")
    assert rejected_logout.status_code == 403
    logout = client_api.post("/api/auth/logout", headers={"X-CSRF-Token": csrf_token})
    assert logout.status_code == 204


def test_login_rejects_invalid_password_without_disclosing_account_state(client):
    client_api, factory = client
    with factory() as db:
        db.add(Account(username="analyst", password_hash=hash_password("correct-horse-battery-staple"), role="analyst"))
        db.commit()

    known = client_api.post("/api/auth/login", json={"username": "analyst", "password": "incorrect-password"})
    unknown = client_api.post("/api/auth/login", json={"username": "missing", "password": "incorrect-password"})
    assert known.status_code == unknown.status_code == 401
    assert known.json() == unknown.json()


TENANT_ID = "123e4567-e89b-12d3-a456-426614174000"
CLIENT_ID = "site-shield-client-id"
OBJECT_ID = "123e4567-e89b-12d3-a456-426614174001"


def entra_claims(**overrides):
    claims = {
        "tid": TENANT_ID,
        "oid": OBJECT_ID,
        "aud": CLIENT_ID,
        "amr": ["pwd", "mfa"],
        "roles": ["SiteShield.Reviewer"],
        "name": "Reviewer One",
        "preferred_username": "reviewer@example.test",
    }
    claims.update(overrides)
    return claims


def test_entra_claims_require_expected_tenant_audience_mfa_and_one_role():
    username, role, display_name = account_from_entra_claims(entra_claims(), TENANT_ID, CLIENT_ID)
    assert username == f"entra:{TENANT_ID}:{OBJECT_ID}"
    assert role == "reviewer"
    assert display_name == "Reviewer One"

    with pytest.raises(HTTPException) as wrong_tenant:
        account_from_entra_claims(entra_claims(tid="123e4567-e89b-12d3-a456-426614174099"), TENANT_ID, CLIENT_ID)
    assert wrong_tenant.value.status_code == 403

    with pytest.raises(HTTPException) as wrong_audience:
        account_from_entra_claims(entra_claims(aud="another-app"), TENANT_ID, CLIENT_ID)
    assert wrong_audience.value.status_code == 401

    with pytest.raises(HTTPException) as missing_mfa:
        account_from_entra_claims(entra_claims(amr=["pwd"]), TENANT_ID, CLIENT_ID)
    assert missing_mfa.value.status_code == 403

    with pytest.raises(HTTPException) as multiple_roles:
        account_from_entra_claims(entra_claims(roles=["analyst", "reviewer"]), TENANT_ID, CLIENT_ID)
    assert multiple_roles.value.status_code == 403


def test_entra_callback_creates_passwordless_account_and_session(client, monkeypatch):
    client_api, factory = client
    from app.config import settings

    monkeypatch.setattr(settings, "entra_tenant_id", TENANT_ID)
    monkeypatch.setattr(settings, "entra_client_id", CLIENT_ID)
    monkeypatch.setattr(settings, "entra_client_secret", "test-client-secret")
    monkeypatch.setattr(settings, "entra_redirect_uri", "https://example.test/api/auth/entra/callback")

    class EntraClient:
        async def authorize_access_token(self, request):
            return {"userinfo": entra_claims()}

    monkeypatch.setattr(auth_routes, "_entra_client", lambda: EntraClient())
    response = client_api.get("/api/auth/entra/callback", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == settings.auth_frontend_url
    assert "site_session" in response.cookies
    with factory() as db:
        account = db.get(Account, f"entra:{TENANT_ID}:{OBJECT_ID}")
        assert account is not None
        assert account.role == "reviewer"
        assert account.password_hash is None
        assert account.display_name == "Reviewer One"


def test_auth_methods_enable_entra_only_when_fully_configured(client, monkeypatch):
    client_api, _ = client
    from app.config import settings

    monkeypatch.setattr(settings, "entra_tenant_id", TENANT_ID)
    monkeypatch.setattr(settings, "entra_client_id", CLIENT_ID)
    monkeypatch.setattr(settings, "entra_client_secret", "test-client-secret")
    monkeypatch.setattr(settings, "entra_redirect_uri", "https://example.test/api/auth/entra/callback")

    methods = client_api.get("/api/auth/methods")

    assert methods.json() == {"entra_enabled": True, "local_password_enabled": False}


def test_password_login_is_disabled_when_entra_is_configured(client, monkeypatch):
    client_api, factory = client
    from app.config import settings

    monkeypatch.setattr(settings, "entra_tenant_id", TENANT_ID)
    monkeypatch.setattr(settings, "entra_client_id", CLIENT_ID)
    monkeypatch.setattr(settings, "entra_client_secret", "test-client-secret")
    monkeypatch.setattr(settings, "entra_redirect_uri", "https://example.test/api/auth/entra/callback")
    with factory() as db:
        db.add(Account(username="local-reviewer", password_hash=hash_password("correct-horse-battery-staple"), role="reviewer"))
        db.commit()

    response = client_api.post("/api/auth/login", json={"username": "local-reviewer", "password": "correct-horse-battery-staple"})

    assert response.status_code == 404