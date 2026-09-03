import sys
import logging
from sqlalchemy import inspect
from backend.app.database import engine, Base, DATABASE_URL
from backend.app.models import Supervisor, Order, Run, Activity, Memory, FinalSummary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")

def init_db():
    logger.info("Connecting to database using DATABASE_URL: %s", DATABASE_URL)
    try:
        # Create all registered tables
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully executed Base.metadata.create_all()")

        # Inspect engine to verify table existence
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info("Database tables verified in database: %s", tables)

        expected_tables = {"supervisors", "orders", "runs", "activities", "memories", "final_summaries"}
        found_tables = set(tables)
        missing = expected_tables - found_tables

        if missing:
            logger.error("Missing expected tables: %s", missing)
            return False

        logger.info("All 6 core tables present: %s", sorted(list(found_tables)))
        return True

    except Exception as e:
        logger.error("Failed to initialize database tables: %s", str(e))
        print("\n================ DATABASE INITIALIZATION ISSUE ================")
        print("Could not connect to PostgreSQL or initialize tables.")
        print(f"Error details: {e}")
        print("\nTroubleshooting guidance:")
        print("1. Copy backend/.env.example to backend/.env")
        print("2. Set DATABASE_URL to your PostgreSQL instance, e.g.:")
        print("   DATABASE_URL=postgresql+psycopg://postgres:<PASSWORD>@localhost:5432/order_supervisor")
        print("3. Ensure the database 'order_supervisor' exists:")
        print("   CREATE DATABASE order_supervisor;")
        print("=================================================================\n")
        return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
