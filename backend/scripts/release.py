from alembic import command
from alembic.config import Config

from scripts.provision_account_from_env import main as provision_account_from_env


def main() -> None:
    command.upgrade(Config("alembic.ini"), "head")
    provision_account_from_env()


if __name__ == "__main__":
    main()