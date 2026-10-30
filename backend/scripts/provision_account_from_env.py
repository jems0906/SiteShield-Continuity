import os

from scripts.create_account import provision_account


def main() -> None:
    if os.getenv("ALLOW_ACCOUNT_PROVISIONING", "").lower() != "true":
        return

    username = os.getenv("INITIAL_ACCOUNT_USERNAME", "")
    role = os.getenv("INITIAL_ACCOUNT_ROLE", "")
    password = os.getenv("INITIAL_ACCOUNT_PASSWORD", "")
    if not username or not role or not password:
        raise RuntimeError("One-time account provisioning is enabled but required values are missing.")
    provision_account(username, role, password)


if __name__ == "__main__":
    main()