"""FastAPI application factory."""
import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.database import create_tables


import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup (with graceful fallback for read-only serverless environments)."""
    try:
        await create_tables()
    except Exception as e:
        print(f"[Lifespan Warning] Could not create tables: {e}")
    try:
        os.makedirs(str(BASE_DIR / "static" / "uploads"), exist_ok=True)
    except Exception:
        pass
    yield


app = FastAPI(
    title="My Pantry Book API",
    description="A warm cookbook-style recipe & pantry manager.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Register all routers FIRST ─────────────────────────────────────────────────
# (Static file mount must come LAST — it acts as a catch-all)

from app.api import ingredients, pantry, recipes, notifications  # noqa: E402
from app.api.views import router as views_router, templates as _views_templates  # noqa: E402

# Custom Jinja2 filter: convert JSON step array back to plain text for textarea
def _from_json_steps(value: str) -> str:
    try:
        steps = json.loads(value)
        return "\n".join(str(s) for s in steps)
    except Exception:
        return value or ""

_views_templates.env.filters["from_json_steps"] = _from_json_steps

# API routes (/api/...)
app.include_router(ingredients.router, prefix="/api")
app.include_router(pantry.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")

# HTML page routes (/, /pantry, /recipes, ...)
app.include_router(views_router)

# ── Static files mount LAST (catch-all sub-app) ────────────────────────────────
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
