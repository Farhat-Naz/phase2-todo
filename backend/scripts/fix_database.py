"""
Fix database schema by adding missing columns
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

# Create engine
engine = create_engine(DATABASE_URL)

def fix_schema():
    """Add missing columns to user table"""
    with engine.connect() as conn:
        # Add email_verified column if not exists
        try:
            conn.execute(text(
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS email_verified BOOLEAN NOT NULL DEFAULT false'
            ))
            print("Added email_verified column")
        except Exception as e:
            print(f"email_verified error: {e}")

        # Add last_login column if not exists
        try:
            conn.execute(text(
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_login TIMESTAMP'
            ))
            print("Added last_login column")
        except Exception as e:
            print(f"last_login error: {e}")

        # Add index on last_login if not exists
        try:
            conn.execute(text(
                'CREATE INDEX IF NOT EXISTS ix_user_last_login ON "user" (last_login)'
            ))
            print("Added index on last_login")
        except Exception as e:
            print(f"index error: {e}")

        conn.commit()
        print("\nDatabase schema fixed successfully!")

if __name__ == "__main__":
    fix_schema()
