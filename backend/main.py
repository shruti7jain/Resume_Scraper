"""
Resume Shapeshifter — FastAPI Backend Entry Point
"""

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import upload, analyze, optimize, download, parse_jd

app = FastAPI(
    title="Resume Shapeshifter API",
    description="AI-powered resume tailoring engine using Groq LLM",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
import os

origins = [
    "http://localhost:5173",   # Vite dev server
    "http://127.0.0.1:5173",
]

env_origins = os.getenv("CORS_ORIGINS")
if env_origins:
    origins.extend([origin.strip() for origin in env_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(upload.router,    prefix="/api", tags=["Resume Upload"])
app.include_router(parse_jd.router,  prefix="/api", tags=["JD Parser"])
app.include_router(analyze.router,   prefix="/api", tags=["Analysis"])
app.include_router(optimize.router,  prefix="/api", tags=["Optimization"])
app.include_router(download.router,  prefix="/api", tags=["PDF Download"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "Resume Shapeshifter API"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
