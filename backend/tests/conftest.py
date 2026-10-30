import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import get_db
from app.main import app
from app.models import Account, Base
from app.security.auth import create_session_token


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(settings, "auth_secret_key", "test-session-secret-key-with-at-least-32-characters")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_db():
        with testing_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client, testing_session
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def auth_context(factory, role: str, write: bool = False):
    username = f"test-{role}"
    with factory() as db:
        if not db.get(Account, username):
            db.add(Account(username=username, password_hash="unused-test-hash", role=role))
            db.commit()
    csrf_token = "test-csrf-token"
    headers = {"X-CSRF-Token": csrf_token} if write else {}
    cookies = {"site_session": create_session_token(username), "site_csrf": csrf_token}
    return headers, cookies