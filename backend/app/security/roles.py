from enum import StrEnum

from fastapi import Header, HTTPException


class Role(StrEnum):
    analyst = "analyst"
    reviewer = "reviewer"
    vendor = "vendor"
    leadership = "leadership"


def current_role(x_demo_role: str = Header(default="leadership")) -> Role:
    try:
        return Role(x_demo_role)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Unknown demo role") from exc


def require_role(*allowed: Role):
    def dependency(role: Role = Header(default="leadership")) -> Role:
        if role not in allowed:
            raise HTTPException(status_code=403, detail="Role is not authorized for this action")
        try:
            return Role(role)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="Unknown demo role") from exc

    return dependency