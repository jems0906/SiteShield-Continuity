# SiteShield Continuity

SiteShield Continuity is a synthetic maintenance-coordination and preparedness workspace. It demonstrates how fictional physical-security assets, inspection findings, alarm-event classifications, vendor work, shift handoffs, and continuity exercises can be recorded together. It is not an operational alarm controller.

## Demonstration status

All sites, people, IDs, event histories, repair notes, and exercise outputs are fictional. The recurring door-contact case is a worked synthetic example: repeated event records lead to an approved vendor scope, a documented repair, a successful functional retest, a monitoring-coverage review, and reviewer acceptance. The matched seven-day before/after event counts are constructed fixtures, not an achieved alarm reduction. Event-volume changes alone do not establish improved security.

No feature suppresses alarms, changes thresholds, bypasses controls, disables devices, exposes device endpoints or credentials, or accepts arbitrary evidence uploads. The storm/outage and incident-mitigation scenarios are discussion-based tabletops, not emergency response. Use employer procedures and authorized professional direction for real events.

## Workspace screenshot

![SiteShield Continuity overview with synthetic metrics and case status](docs/siteshield-dashboard.png)

## Run locally

Prerequisites: Python 3.12+, Node.js 22+, npm, and PostgreSQL for persistent multi-service use. SQLite is the local default.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "sqlite:///./siteshield.db"
alembic upgrade head
python -m scripts.seed_demo
uvicorn app.main:app --reload
```

In another terminal:

```powershell
cd frontend
npm ci
$env:VITE_API_URL = "http://127.0.0.1:8000"
npm run dev
```

Open the Vite URL printed in the terminal (normally `http://localhost:5173`). API health is `http://127.0.0.1:8000/health`; interactive API documentation is at `/docs`.

Workspace sections have refreshable paths: `/`, `/asset-register`, `/audits`, `/alarms`, `/work-orders`, `/handoffs`, `/continuity`, and `/awareness`.

## Reproducible checks

```powershell
cd backend
python -m pytest tests -q
```

```powershell
cd frontend
npm ci
npm run check
npm run build
```

CI runs the backend tests and frontend check/build on pull requests and pushes. GitHub Actions retains each run with its triggering commit SHA and result.

## Demo roles and limitations

Choose a demonstration view in the workspace header. The API accepts `X-Demo-Role` for analyst, reviewer, vendor, and read-only leadership examples. This is intentionally a demo-only permission simulation, not authentication: clients can choose their own role. Do not expose this service publicly with sensitive data or treat it as an authorization boundary. Production use requires an identity provider, server-verified roles, tenant/site scoping, CSRF/session protections as appropriate, access reviews, and a retention policy.

Vendor records are hidden unless explicitly marked vendor-visible; case data in the seed profile is not shared. `/health` returns only `{"status":"ok"}`. CORS should be restricted to the exact frontend origin, but CORS is not authentication.

## Railway deployment

Deploy three separate Railway services: PostgreSQL, backend with root directory `/backend`, and frontend with root directory `/frontend`. Set backend `DATABASE_URL` from the PostgreSQL service reference; this project converts `postgres://` and `postgresql://` schemes to `postgresql+psycopg://`. Set backend `CORS_ORIGINS` to the exact HTTPS frontend origin. Set frontend `VITE_API_URL` to the backend's full HTTPS origin before building and assign the frontend public-domain target port `8080`. The backend binds to Railway's assigned `PORT`.

Run migrations as a controlled release step with `alembic upgrade head` from `/backend`, then seed only an explicit synthetic profile with `python -m scripts.seed_demo`. Do not automatically seed production or store credentials in source control. For this deployment, migration, health, role visibility, the vendor-to-reviewer maintenance workflow, restart persistence, and `/asset-register` deep-link refresh were verified. Rebuild the frontend if its API URL changes.

This public instance contains only fictional records and has its own isolated PostgreSQL service. To restore the demo after testing, set `ALLOW_DEMO_RESET=true` on the backend and run `railway ssh --service siteshield-backend --environment production -- python -m scripts.reset_demo`. The command also requires `DEMO_MODE=true`; it is not exposed as an HTTP endpoint. Keep reset disabled on any non-demo environment.

Live frontend: https://siteshield-frontend-production.up.railway.app

Live backend health: https://siteshield-backend-production.up.railway.app/health

The services run in Railway's `us-west2` region. PostgreSQL was migrated through the backend pre-deploy release command, then populated only through the explicit synthetic seed profile. The local overview screenshot is included at `docs/siteshield-dashboard.png`; the seeded case and fixture files are the reproducible worked reports for this source delivery.

## Project map

- `backend/`: FastAPI, SQLAlchemy, Alembic, role demonstration, metrics, and tests.
- `frontend/`: React/Vite workspace and Recharts synthetic event history.
- `fixtures/`: CSV inventory/events and the discussion-based storm tabletop scenario.
- `docs/`: audit, vendor, continuity, exercise, and awareness reference materials.

Data retention is not configured. Audit entries demonstrate approval and state-change recording; export auditing is not implemented because no export feature is provided. Demo-role headers are not production access control.