from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from routers.assessment import router as assessment_router
from routers.evidence import router as evidence_router
from routers.payments import router as payments_router
import os
import time
from collections import defaultdict

load_dotenv()

app = FastAPI(
    title       = "CyberGuard Compliance API",
    description = (
        "AI-powered Cyber Essentials gap analysis and compliance monitoring for UK SMEs. "
        "Built by Corvaxis Ltd — powered by Claude AI."
    ),
    version     = "1.1.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = [
    "https://ceready.co.uk",
    "https://www.ceready.co.uk",
    "https://cyberguard-frontend-production-e3cd.up.railway.app",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ALLOWED_ORIGINS,
    allow_credentials = True,
    allow_methods     = ["GET", "POST", "OPTIONS"],
    allow_headers     = ["Content-Type", "Authorization", "Accept"],
)

# ── Simple in-memory rate limiter ─────────────────────────────────────────────
# Limits: 10 assessments per IP per hour
_rate_store: dict = defaultdict(list)
RATE_LIMIT   = 10          # max requests
RATE_WINDOW  = 3600        # per second window (1 hour)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in ["/api/v1/assess", "/api/v1/evidence-pack", "/api/v1/checkout"]:
        ip  = request.client.host
        now = time.time()

        # Remove timestamps outside the window
        _rate_store[ip] = [t for t in _rate_store[ip] if now - t < RATE_WINDOW]

        if len(_rate_store[ip]) >= RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."}
            )
        _rate_store[ip].append(now)

    return await call_next(request)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(assessment_router)
app.include_router(evidence_router)
app.include_router(payments_router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "CyberGuard Compliance API",
        "version": "1.1.0",
        "docs":    "/docs",
        "health":  "/api/v1/health",
        "by":      "Corvaxis Ltd — ceready.co.uk"
    }

@app.get("/api/v1/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "CyberGuard Compliance API"}
