from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import alarms, assets, audits, exercises, handoffs, work_orders
from app.config import settings

app = FastAPI(title="SiteShield Continuity", version="1.0.0", description="Synthetic maintenance-coordination and preparedness workspace")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Demo-Role"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


for route in (assets.router, audits.router, alarms.router, work_orders.router, handoffs.router, exercises.router):
    app.include_router(route, prefix="/api")