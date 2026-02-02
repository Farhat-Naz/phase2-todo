"""
Script to create database tables in Neon PostgreSQL.
Run this once to initialize the database schema.
"""
import os
from sqlmodel import SQLModel, create_engine

# Import models to ensure they're registered with SQLModel
from app.models import User, Todo

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://neondb_owner:npg_ZAGN4xaUk2mh@ep-red-unit-a13i3o3z-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
)

def create_tables():
    """Create all database tables."""
    print(f"Connecting to database...")
    print(f"Database URL: {DATABASE_URL[:50]}...")

    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)

    print("\nCreating tables...")
    # Create all tables
    SQLModel.metadata.create_all(engine)

    print("\n✅ Database tables created successfully!")
    print("Tables created:")
    print("  - user")
    print("  - todo")

if __name__ == "__main__":
    create_tables()
