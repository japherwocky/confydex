"""
FastAPI main application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import search, docs, health, upload, review, reports

app = FastAPI(
    title="Confydex API",
    description="Clinical Trial Protocol Regulatory Review API",
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
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(review.router, prefix="/api", tags=["review"])
app.include_router(reports.router, prefix="/api", tags=["reports"])


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    # Import to register services
    import config  # noqa
