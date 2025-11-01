"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.services.scheduled_tasks import cleanup_unconfirmed_exams, send_pending_review_reminders

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()
logger.info("Background scheduler started")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Startup event - Schedule background jobs"""
    # Schedule cleanup job to run every 6 hours
    scheduler.add_job(
        cleanup_unconfirmed_exams,
        'interval',
        hours=6,
        id='cleanup_unconfirmed_exams',
        replace_existing=True
    )
    logger.info("Scheduled cleanup job: runs every 6 hours")

    # Schedule reminder job to run every hour
    scheduler.add_job(
        send_pending_review_reminders,
        'interval',
        hours=1,
        id='send_pending_review_reminders',
        replace_existing=True
    )
    logger.info("Scheduled reminder job: runs every hour")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - Stop scheduler"""
    scheduler.shutdown()
    logger.info("Background scheduler stopped")


# Import and include routers
from app.api.routes import exams, analytics, recommendations, learning_outcomes, study_plans, curriculum

app.include_router(exams.router, prefix=f"{settings.API_V1_PREFIX}/exams", tags=["exams"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_PREFIX}/analytics", tags=["analytics"])
app.include_router(recommendations.router, prefix=f"{settings.API_V1_PREFIX}/recommendations", tags=["recommendations"])
app.include_router(learning_outcomes.router, prefix=settings.API_V1_PREFIX, tags=["learning-outcomes"])
app.include_router(study_plans.router, prefix=f"{settings.API_V1_PREFIX}/study-plans", tags=["study-plans"])
app.include_router(curriculum.router, prefix=settings.API_V1_PREFIX, tags=["curriculum"])
# app.include_router(student.router, prefix=f"{settings.API_V1_PREFIX}/student", tags=["student"])
