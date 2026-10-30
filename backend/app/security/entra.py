import hashlib
from uuid import UUID

from fastapi import HTTPException, status

from app.security.roles import Role

ROLE_CLAIMS = {
    "analyst": Role.analyst,
    "reviewer": Role.reviewer,
    "vendor": Role.vendor,
    "leadership": Role.leadership,
    "SiteShield.Analyst": Role.analyst,
    "SiteShield.Reviewer": Role.reviewer,
    "SiteShield.Vendor": Role.vendor,
    "SiteShield.Leadership": Role.leadership,
}


def account_from_entra_claims(claims: dict, tenant_id: str, client_id: str) -> tuple[str, list[str], str]:
    token_tenant = claims.get("tid")
    object_id = claims.get("oid")
    if token_tenant != tenant_id or not isinstance(object_id, str):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Identity tenant is not authorized")
    try:
        normalized_tenant = str(UUID(token_tenant))
        normalized_object_id = str(UUID(object_id))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identity claims are invalid") from exc

    audience = claims.get("aud")
    if client_id not in (audience if isinstance(audience, list) else [audience]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identity audience is invalid")

    methods = claims.get("amr", [])
    if not isinstance(methods, list) or "mfa" not in methods:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Entra MFA is required")

    role_claims = claims.get("roles", [])
    if not isinstance(role_claims, list):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="An assigned SiteShield role is required")
    roles = {ROLE_CLAIMS[item] for item in role_claims if isinstance(item, str) and item in ROLE_CLAIMS}
    if not roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="At least one SiteShield app role must be assigned")

    raw_subject = f"entra:{normalized_tenant}:{normalized_object_id}"
    username = f"entra:{hashlib.sha256(raw_subject.encode()).hexdigest()}"
    display_name = "Workspace member"
    return username, sorted(role.value for role in roles), display_name