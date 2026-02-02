"""
Initialize database tables for Vercel deployment.
Run this script once to create all necessary tables.
"""
import os
from sqlmodel import SQLModel, create_engine
from app.models import User, Todo, Session, PasswordResetToken, EmailVerificationToken

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("ERROR: DATABASE_URL environment variable not set!")
    exit(1)

print("Connecting to database...")
print(f"URL: {database_url[:50]}...")

try:
    # Create engine
    engine = create_engine(database_url, echo=True)

    print("\nCreating database tables...")

    # Create all tables
    SQLModel.metadata.create_all(engine)

    print("\nDatabase tables created successfully!")
    print("\nTables created:")
    print("  - user")
    print("  - todo")
    print("  - session")
    print("  - password_reset_token")
    print("  - email_verification_token")

except Exception as e:
    print(f"\nERROR: Failed to create tables")
    print(f"   {type(e).__name__}: {e}")
    exit(1)
