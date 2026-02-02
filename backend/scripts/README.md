# Backend Scripts

This directory contains utility scripts for database management and maintenance.

## Scripts

### fix_database.py
One-time migration script to add missing columns to the user table:
- `email_verified` (BOOLEAN, default: false)
- `last_login` (TIMESTAMP, nullable)
- Index on `last_login`

**Usage:**
```bash
cd backend
python scripts/fix_database.py
```

**Note:** For production migrations, use Alembic instead. This script is provided for emergency fixes or manual database repairs.
