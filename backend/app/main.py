import hmac

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import alarms, assets, audits, auth, exercises, handoffs, work_orders
from app.config import settings

app = FastAPI(title="SiteShield Continuity", version="1.0.0", description="Synthetic maintenance-coordination and preparedness workspace")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)


@app.middleware("http")
async def protect_state_changes(request: Request, call_next):
    if request.url.path.startswith("/api/") and request.method not in {"GET", "HEAD", "OPTIONS"} and request.url.path != "/api/auth/login":
        csrf_cookie = request.cookies.get("site_csrf", "")
        csrf_header = request.headers.get("X-CSRF-Token", "")
        if not csrf_cookie or not csrf_header or not hmac.compare_digest(csrf_cookie, csrf_header):
            return JSONResponse(status_code=403, content={"detail": "CSRF validation failed"})
    return await call_next(request)


@app.get("/health")
def health():
    return {"status": "ok"}


for route in (auth.router, assets.router, audits.router, alarms.router, work_orders.router, handoffs.router, exercises.router):
    app.include_router(route, prefix="/api")