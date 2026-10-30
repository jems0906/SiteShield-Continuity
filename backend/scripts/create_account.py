import argparse
from getpass import getpass

from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import Account
from app.security.auth import hash_password
from app.security.roles import Role


def provision_account(username: str, role: str, password: str) -> None:
    normalized_username = username.strip()
    if not normalized_username or len(normalized_username) > 80:
        raise ValueError("Username must contain between 1 and 80 characters.")
    try:
        role_value = Role(role).value
    except ValueError as exc:
        raise ValueError("Role must be analyst, reviewer, vendor, or leadership.") from exc

    password_hash = hash_password(password)
    with SessionLocal() as db:
        if db.get(Account, normalized_username):
            raise ValueError("That username already exists.")
        db.add(Account(username=normalized_username, password_hash=password_hash, role=role_value))
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ValueError("That username already exists.") from exc
    print(f"Provisioned {role_value} account {normalized_username}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision a SiteShield workspace account.")
    parser.add_argument("--username", required=True)
    parser.add_argument("--role", required=True, choices=[role.value for role in Role])
    args = parser.parse_args()
    password = getpass("Password (minimum 12 characters): ")
    confirmation = getpass("Confirm password: ")
    if password != confirmation:
        parser.error("Passwords do not match.")
    try:
        provision_account(args.username, args.role, password)
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()