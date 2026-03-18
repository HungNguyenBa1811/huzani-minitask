# Backend Setup Plan - Phase 1 (DB Connectivity Only)

## Goal

Build a minimal FastAPI server that:

- is callable from frontend via HTTP API
- verifies connectivity to SQL Server
- does not depend on schema or business tables yet

## Scope

In scope:

- FastAPI app bootstrap
- Environment-based DB configuration
- SQL Server connectivity test endpoint
- Basic CORS setup for frontend integration

Out of scope:

- ORM models
- CRUD endpoints for domain entities
- Authentication/authorization
- Migration scripts

## Project Structure

```text
app/
  api/
    health.py
  core/
    config.py
  db/
    session.py
  main.py
.env.example
requirements.txt
```

## Dependencies

Declared in requirements.txt (install manually):

- fastapi
- uvicorn[standard]
- sqlalchemy
- pyodbc
- pydantic-settings
- python-dotenv

System requirement:

- Microsoft ODBC Driver for SQL Server installed on host machine (recommended: ODBC Driver 18 for SQL Server)

## Configuration Contract

Use environment variables:

- APP_ENV
- APP_HOST
- APP_PORT
- APP_CORS_ORIGINS
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_DRIVER
- DB_ENCRYPT
- DB_TRUST_SERVER_CERT
- DB_CONNECT_TIMEOUT

## API Contract (Phase 1)

- `GET /health`
    - 200 when API server is alive
- `GET /health/db`
    - 200 when DB connection succeeds (`SELECT 1`)
    - 503 when DB connection fails

## How to Run

1. Fill `.env` based on `.env.example`
2. Install dependencies manually from `requirements.txt`
3. Start server:
    - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
4. Test endpoints:
    - `/health`
    - `/health/db`

## Definition of Done

- Server starts successfully
- `/health` returns 200
- `/health/db` returns 200 when DB is reachable
- `/health/db` returns 503 with safe error details when DB is not reachable
- Frontend can call APIs without CORS errors in local development
