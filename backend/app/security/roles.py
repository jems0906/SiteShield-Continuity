from enum import StrEnum

from fastapi import Depends, HTTPException

from app.models import Account
from app.security.auth import current_account


class Role(StrEnum):
    analyst = "analyst"
    reviewer = "reviewer"
    vendor = "vendor"
    leadership = "leadership"


def current_role(account: Account = Depends(current_account)) -> Role:
    try:
        return Role(account.role)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="Account role is not recognized") from exc


def require_role(*allowed: Role):
    def dependency(role: Role = Depends(current_role)) -> Role:
        if role not in allowed:
            raise HTTPException(status_code=403, detail="Role is not authorized for this action")
        return role

    return dependency