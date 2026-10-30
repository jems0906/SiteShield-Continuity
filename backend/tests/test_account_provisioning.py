import pytest

from app.models import Account
from app.security.auth import verify_password
from scripts import create_account


def test_provision_account_stores_a_hash_and_server_assigned_role(client, monkeypatch):
    _, factory = client
    monkeypatch.setattr(create_account, "SessionLocal", factory)

    create_account.provision_account("  new-reviewer  ", "reviewer", "a-long-fictional-password")

    with factory() as db:
        account = db.get(Account, "new-reviewer")
        assert account is not None
        assert account.role == "reviewer"
        assert account.password_hash != "a-long-fictional-password"
        assert verify_password(account.password_hash, "a-long-fictional-password")


def test_provision_account_rejects_duplicate_usernames(client, monkeypatch):
    _, factory = client
    monkeypatch.setattr(create_account, "SessionLocal", factory)
    create_account.provision_account("existing", "analyst", "a-long-fictional-password")

    with pytest.raises(ValueError, match="already exists"):
        create_account.provision_account("existing", "vendor", "another-long-password")