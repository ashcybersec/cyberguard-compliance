from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers.assessment import router as assessment_router
import os
from routers.evidence import router as evidence_router
load_dotenv()

app = FastAPI(
    title       = "CyberGuard Compliance API",
    description = (
        "AI-powered Cyber Essentials gap analysis and compliance monitoring for UK SMEs. "
        "Built by ashcybersec — powered by Claude AI."
    ),
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# ── CORS — tighten origins in production ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(assessment_router)
app.include_router(evidence_router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "service":     "CyberGuard Compliance API",
        "version":     "1.0.0",
        "docs":        "/docs",
        "health":      "/api/v1/health",
        "by":          "ashcybersec.co.uk"
    }
