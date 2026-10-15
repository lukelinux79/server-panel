from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api import samba, storage

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compute a robust path to the frontend/public directory relative to the project root.
# This works both when running from the repo (bare-metal) and inside the Docker image.
BASE_DIR = Path(__file__).resolve().parents[1]  # file is at <project>/app/app/main.py -> parents[1] == <project>/app/.. => <project>
STATIC_DIR = BASE_DIR / "frontend" / "public"

if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
else:
    # If the static dir is missing, expose a small JSON root so the service still starts and the API is usable.
    @app.get("/")
    def root():
        return {"status": "ok", "message": "Static frontend not found. Use the API under /api."}

app.include_router(samba.router, prefix=settings.api_prefix)
app.include_router(storage.router, prefix=settings.api_prefix)


@app.get('/health')
def health():
    return {"status": "ok"}
