import pytest

from app.models import Account
from app.security.auth import verify_password
from scripts import create_account, provision_account_from_env, release


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


def test_release_provisioning_is_disabled_without_opt_in(monkeypatch):
    monkeypatch.delenv("ALLOW_ACCOUNT_PROVISIONING", raising=False)
    monkeypatch.setattr(provision_account_from_env, "provision_account", lambda *_: pytest.fail("must stay disabled"))

    provision_account_from_env.main()


def test_release_provisioning_uses_only_explicit_environment_values(monkeypatch):
    captured = []
    monkeypatch.setenv("ALLOW_ACCOUNT_PROVISIONING", "true")
    monkeypatch.setenv("INITIAL_ACCOUNT_USERNAME", "reviewer-demo")
    monkeypatch.setenv("INITIAL_ACCOUNT_ROLE", "reviewer")
    monkeypatch.setenv("INITIAL_ACCOUNT_PASSWORD", "a-private-test-password")
    monkeypatch.setattr(provision_account_from_env, "provision_account", lambda *args: captured.append(args))

    provision_account_from_env.main()

    assert captured == [("reviewer-demo", "reviewer", "a-private-test-password")]


def test_release_migrates_before_optional_account_provisioning(monkeypatch):
    operations = []
    monkeypatch.setattr(release.command, "upgrade", lambda config, revision: operations.append(("migration", revision)))
    monkeypatch.setattr(release, "provision_account_from_env", lambda: operations.append(("provision", None)))

    release.main()

    assert operations == [("migration", "head"), ("provision", None)]