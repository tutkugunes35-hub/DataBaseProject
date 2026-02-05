# Backend (FastAPI)

## Run (Windows)
```powershell
# In the project folder (the folder that contains app\)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Endpoints
- GET / -> service info
- GET /docs -> Swagger UI
- GET /openapi.json -> OpenAPI spec
- GET /health -> health check (db can be null if not configured)
