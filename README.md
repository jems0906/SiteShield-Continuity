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
$env:AUTH_SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(48))")
alembic upgrade head
python -m scripts.seed_demo
python -m scripts.create_account --username reviewer-one --role reviewer
uvicorn app.main:app --reload
```

In another terminal:

```powershell
cd frontend
npm ci
$env:VITE_API_URL = "http://localhost:8000"
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

Sign in with an operator-provisioned account. Roles are stored on the server and cannot be selected or overridden by request headers. Passwords are Argon2-hashed; sessions use signed HttpOnly cookies and writes require a matching CSRF token. Account creation is available only through the backend operator CLI, not an HTTP endpoint.

Vendor records are hidden unless explicitly marked vendor-visible; case data in the seed profile is not shared. `/health` returns only `{"status":"ok"}`. CORS should be restricted to the exact frontend origin, but CORS is not authentication.

## Railway deployment

Deploy three separate Railway services: PostgreSQL, backend with root directory `/backend`, and frontend with root directory `/frontend`. Set backend `DATABASE_URL` from the PostgreSQL service reference; this project converts `postgres://` and `postgresql://` schemes to `postgresql+psycopg://`. Set backend `CORS_ORIGINS` to the exact HTTPS frontend origin, `AUTH_SECRET_KEY` to a generated secret of at least 32 characters, `AUTH_COOKIE_SECURE=true`, and `AUTH_COOKIE_SAMESITE=none` for credentialed requests between the separate Railway subdomains. Set frontend `VITE_API_URL` to the backend's full HTTPS origin before building and assign the frontend public-domain target port `8080`. The backend binds to Railway's assigned `PORT`.

Run migrations as a controlled release step with `python -m scripts.release` from `/backend`; it applies `alembic upgrade head` and then runs the one-time account provisioner, which is disabled unless `ALLOW_ACCOUNT_PROVISIONING=true`. Seed only an explicit synthetic profile with `python -m scripts.seed_demo`; do not automatically seed production or store credentials in source control. For this deployment, migration, health, role visibility, the vendor-to-reviewer maintenance workflow, restart persistence, and `/asset-register` deep-link refresh were verified. Rebuild the frontend if its API URL changes.

The seed contains no login accounts. To create the initial reviewer, set `ALLOW_ACCOUNT_PROVISIONING=true`, `INITIAL_ACCOUNT_USERNAME=reviewer-demo`, `INITIAL_ACCOUNT_ROLE=reviewer`, and `INITIAL_ACCOUNT_PASSWORD` as temporary Railway backend variables, then trigger a backend deployment. The release step provisions the account inside the private network using an Argon2 hash. Immediately afterward, remove the password/username/role variables and set `ALLOW_ACCOUNT_PROVISIONING=false`; do not leave a provisioning password in service variables. The operator CLI `python -m scripts.create_account` remains available when run where the private database is reachable.

This public instance contains only fictional records and has its own isolated PostgreSQL service. To restore the demo after testing, set `ALLOW_DEMO_RESET=true` on the backend and run `railway run --service siteshield-backend -- python -m scripts.reset_demo` from `/backend`. The command also requires `DEMO_MODE=true`; it is not exposed as an HTTP endpoint. Keep reset disabled on any non-demo environment.

Live frontend: https://siteshield-frontend-production.up.railway.app

Live backend health: https://siteshield-backend-production.up.railway.app/health

The services run in Railway's `us-west2` region. PostgreSQL was migrated through the backend pre-deploy release command, then populated only through the explicit synthetic seed profile. The local overview screenshot is included at `docs/siteshield-dashboard.png`; the seeded case and fixture files are the reproducible worked reports for this source delivery.

## Project map

- `backend/`: FastAPI, SQLAlchemy, Alembic, role demonstration, metrics, and tests.
- `frontend/`: React/Vite workspace and Recharts synthetic event history.
- `fixtures/`: CSV inventory/events and the discussion-based storm tabletop scenario.
- `docs/`: audit, vendor, continuity, exercise, and awareness reference materials.

Data retention is not configured. Audit entries demonstrate approval and state-change recording; export auditing is not implemented because no export feature is provided. This authentication is a minimal workspace sign-in, not an identity provider: production use with sensitive or operational data still requires organizational identity management, MFA, account recovery and access review, and a tested retention policy.