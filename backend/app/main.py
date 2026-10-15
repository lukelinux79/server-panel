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

# Mount static frontend (if built into frontend/public)
app.mount("/", StaticFiles(directory="../frontend/public", html=True), name="static")

app.include_router(samba.router, prefix=settings.api_prefix)
app.include_router(storage.router, prefix=settings.api_prefix)


@app.get('/health')
def health():
    return {"status": "ok"}
