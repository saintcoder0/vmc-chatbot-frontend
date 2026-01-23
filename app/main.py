from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.db import Base, engine
from app.routers import admin, db, whatsapp


settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    # For hackathon/demo, auto-create tables. For production, use Alembic.
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        # If DB is not up yet, don't crash the whole API.
        # You can start MySQL and then hit /db/ping to confirm connectivity.
        return


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.environment}


app.include_router(whatsapp.router)
app.include_router(db.router)
app.include_router(admin.router)
if hasattr(whatsapp, "root_router"):
    app.include_router(whatsapp.root_router)


