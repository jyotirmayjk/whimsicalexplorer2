from fastapi import FastAPI
from app.core.config import settings
from app.api import auth, settings as api_settings, discoveries, activity, devices, media, websockets

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Core API Groupings
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(api_settings.router, prefix=f"{settings.API_V1_STR}/app/settings", tags=["settings"])
app.include_router(discoveries.router, prefix=f"{settings.API_V1_STR}/app/discoveries", tags=["discoveries"])
app.include_router(activity.router, prefix=f"{settings.API_V1_STR}/app/activity", tags=["activity"])

# Hardware Endpoints
app.include_router(devices.router, prefix=f"{settings.API_V1_STR}/device", tags=["device"])
app.include_router(media.router, prefix=f"{settings.API_V1_STR}/device/media", tags=["media"])
app.include_router(websockets.router, prefix=f"{settings.API_V1_STR}/device", tags=["websocket"])

@app.on_event("startup")
def on_startup():
    from app.models.db_models import Base
    from app.db.session import engine
    # Create all DB tables (for local testing without alembic)
    Base.metadata.create_all(bind=engine)

@app.get("/healthz")
def health_check():
    return {"status": "ok"}
