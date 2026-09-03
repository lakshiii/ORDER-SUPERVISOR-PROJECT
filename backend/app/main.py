import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import engine, SessionLocal, Base
from backend.app.api.supervisors import router as supervisors_router
from backend.app.api.orders import router as orders_router
from backend.app.api.runs import router as runs_router
from backend.app.services.supervisor_service import seed_default_supervisor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    # Seed default supervisor template
    logger.info("Seeding default supervisor template if needed...")
    db = SessionLocal()
    try:
        seed_default_supervisor(db)
    finally:
        db.close()

    yield
    logger.info("Order Supervisor backend shutting down.")

app = FastAPI(
    title="Order Supervisor API",
    description="Backend API for Order Supervisor Proof of Concept",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(supervisors_router)
app.include_router(orders_router)
app.include_router(runs_router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": "Order Supervisor POC",
        "version": "0.1.0",
        "docs_url": "/docs",
    }
