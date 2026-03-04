"""
FastAPI main application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import search, docs, health

app = FastAPI(
    title="Confydex API",
    description="Clinical Trial Document Search API",
    version="0.1.0",
)

# CORS - allow all for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(docs.router, prefix="/api", tags=["documents"])


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    # Import to register services
    import config  # noqa
