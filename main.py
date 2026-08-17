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

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, engine, get_db
from app.routers import auth, profile, kyc, campaigns, proposals, gigs, chats, creators, banners

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

    # Seed default promo banners if none exist
    from app.database import SessionLocal
    from app.models.banner import PromoBanner
    
    db = SessionLocal()
    try:
        if db.query(PromoBanner).count() == 0:
            print("🌱 Seeding default promo banners...")
            default_banners = [
                PromoBanner(
                    title="Create Sponsorship Gigs",
                    subtitle="Offer packages specifying your platforms, follower reach, price...",
                    button_text="Create Gig Post",
                    redirect_to="/create-gig",
                    icon_name="store",
                    background_gradient="linear-gradient(135deg, #6366f1, #a855f7)",
                    sort_order=1
                ),
                PromoBanner(
                    title="Verify Your Identity (KYC)",
                    subtitle="Complete your KYC verification to start pitching for premium sponsorships.",
                    button_text="Verify Now",
                    redirect_to="/verify-kyc",
                    icon_name="id-card",
                    background_gradient="linear-gradient(135deg, #10b981, #059669)",
                    sort_order=2
                ),
                PromoBanner(
                    title="Explore Marketplace Gigs",
                    subtitle="Find content creators offering top-tier content packages for your brands.",
                    button_text="Browse Gigs",
                    redirect_to="/marketplace",
                    icon_name="search",
                    background_gradient="linear-gradient(135deg, #f59e0b, #d97706)",
                    sort_order=3
                ),
                PromoBanner(
                    title="Secure Payments with Escrow",
                    subtitle="All contract funds are locked securely and released only upon delivery.",
                    button_text="Learn More",
                    redirect_to="/escrow-faq",
                    icon_name="lock",
                    background_gradient="linear-gradient(135deg, #3b82f6, #1d4ed8)",
                    sort_order=4
                ),
                PromoBanner(
                    title="AI-Powered Script Generator",
                    subtitle="Need ideas? Generate high-converting video script briefs instantly.",
                    button_text="Generate Script",
                    redirect_to="/ai-script",
                    icon_name="wand-magic-sparkles",
                    background_gradient="linear-gradient(135deg, #ec4899, #be185d)",
                    sort_order=5
                )
            ]
            db.add_all(default_banners)
            db.commit()
            print("✅ Promo banners seeded successfully!")
    except Exception as e:
        print(f"❌ Failed to seed promo banners: {e}")
        db.rollback()
    finally:
        db.close()

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
app.include_router(profile.router, prefix="/api")
app.include_router(kyc.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(proposals.router, prefix="/api")
app.include_router(gigs.router, prefix="/api")
app.include_router(chats.router, prefix="/api")
app.include_router(creators.router, prefix="/api")
app.include_router(banners.router, prefix="/api")

# ── SQLAdmin Setup ───────────────────────────────────────────
from app.admin import setup_admin
setup_admin(app, engine)


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
@app.get(
    "/api/db-test",
    tags=["🏠 Health"],
    summary="Test Database Connection",
)
def test_db_connection(db: Session = Depends(get_db)):
    """Executes a simple query to verify database connection."""
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {
            "status": "✅ connected",
            "database": "PostgreSQL",
            "result": result,
            "message": "Database connection verified successfully! 🚀"
        }
    except Exception as e:
        return {
            "status": "❌ error",
            "message": f"Failed to connect to database: {str(e)}"
        }
