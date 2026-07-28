"""
Brand Bridge (CreatorHub AI) — FastAPI Backend
===============================================

🚀 Main Application Entry Point

Run with:
    uvicorn main:app --reload --port 8000

API Docs:
    Swagger UI: http://localhost:8000/docs
    ReDoc:      http://localhost:8000/redoc
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import auth

settings = get_settings()


# ── Lifespan: Create tables on startup ────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Create all database tables on startup.
    In production, use Alembic migrations instead.
    """
    print("\n🚀 Brand Bridge API Starting...")
    print(f"📦 Environment: {settings.APP_ENV}")
    print(f"🗄️  Database: {settings.DATABASE_URL}")

    # Auto-create tables (dev only)
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified!")
    print(f"📚 API Docs: http://localhost:8000/docs\n")

    yield

    print("\n👋 Brand Bridge API Shutting down...")


# ── FastAPI App ───────────────────────────────────────────────
app = FastAPI(
    title="Brand Bridge API",
    description=(
        "🎯 **Brand Bridge (CreatorHub AI)** — Influencer Marketing Marketplace API\n\n"
        "Brands এবং Content Creators-দের connect করার platform।\n\n"
        "## Features\n"
        "- 🔐 JWT Authentication (Register, Login, OTP Verify)\n"
        "- 👤 Profile Management\n"
        "- 🎯 Campaign & Proposal System\n"
        "- 🎨 Gig Marketplace\n"
        "- 💬 Real-time Chat & Contract System\n"
        "- 💰 Wallet & Escrow Payments\n"
        "- 🤖 AI Creator Matching\n\n"
        "---\n"
        "*Currently implemented: Authentication Module (10%)*"
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS Middleware ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Register Routers ─────────────────────────────────────────
app.include_router(auth.router, prefix="/api")


# ── Root Health Check ─────────────────────────────────────────
@app.get(
    "/",
    tags=["🏠 Health"],
    summary="API Health Check",
)
def health_check():
    """Root endpoint — returns API status."""
    return {
        "status": "✅ running",
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "environment": settings.APP_ENV,
        "docs": "/docs",
        "message": "Brand Bridge API চালু আছে! 🚀",
    }


@app.get(
    "/api",
    tags=["🏠 Health"],
    summary="API Base",
)
def api_base():
    """API base path — lists available modules."""
    return {
        "message": "Brand Bridge API v0.1.0",
        "modules": {
            "auth": "/api/auth — 🔐 Authentication (✅ Implemented)",
            "profile": "/api/profile — 👤 Profile (🔜 Coming Soon)",
            "kyc": "/api/kyc — 📝 KYC (🔜 Coming Soon)",
            "campaigns": "/api/campaigns — 🎯 Campaigns (🔜 Coming Soon)",
            "proposals": "/api/proposals — 📨 Proposals (🔜 Coming Soon)",
            "gigs": "/api/gigs — 🎨 Gigs (🔜 Coming Soon)",
            "chats": "/api/chats — 💬 Chat (🔜 Coming Soon)",
            "orders": "/api/orders — 📦 Orders (🔜 Coming Soon)",
            "wallet": "/api/wallet — 💰 Wallet (🔜 Coming Soon)",
            "ai": "/api/ai — 🤖 AI Features (🔜 Coming Soon)",
            "analytics": "/api/analytics — 📊 Analytics (🔜 Coming Soon)",
            "creators": "/api/creators — 🔍 Creator Search (🔜 Coming Soon)",
            "settings": "/api/settings — ⚙️ Settings (🔜 Coming Soon)",
        },
    }
