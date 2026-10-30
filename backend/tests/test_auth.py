from app.models import Account
from app.security.auth import hash_password


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