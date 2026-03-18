from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.health import router as health_router
from app.api.humans import router as human_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="huzani-minitask API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(human_router)


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse("app/static/index.html")
