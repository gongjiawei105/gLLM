import json
import os
import time

from chainlit.utils import mount_chainlit
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.core import oauth2_scheme
from src.core.config import Settings
from src.routers.adminrouter import AdminRouter
from src.routers.authrouter import AuthRouter
from src.routers.docsrouter import DocsRouter
from src.routers.finetuningrouter import FineTuningRouter
from src.services.authservice import require_roles
from src.schema.models import UserRole


limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app = FastAPI(title="gLLM", version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS ---
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Health check ---
@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}

app.include_router(AuthRouter)
app.include_router(
    AdminRouter,
    dependencies=[Depends(oauth2_scheme), Depends(require_roles(UserRole.admin))],
)
app.include_router(
    DocsRouter,
    dependencies=[Depends(oauth2_scheme)],
)
app.include_router(
    FineTuningRouter,
    dependencies=[
        Depends(oauth2_scheme),
        Depends(require_roles(UserRole.admin, UserRole.fine_tuner)),
    ],
)
mount_chainlit(app=app, target="./chainlit-app.py", path="/gllm")

if os.path.isdir("../frontend/dist"):
    app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")
else:
    print("No frontend dist folder detected. Skipping admin UI deployment")
