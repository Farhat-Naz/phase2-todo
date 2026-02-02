# Backend - Todo Application API

FastAPI backend with SQLModel ORM and Neon Serverless PostgreSQL.

## Tech Stack

- **Framework**: FastAPI (async-capable)
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Database**: Neon Serverless PostgreSQL
- **Migrations**: Alembic
- **Package Manager**: uv (NOT pip or poetry)
- **Python**: 3.13+

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Package marker
│   ├── models.py            # SQLModel database models
│   ├── database.py          # Database configuration and session management
│   ├── main.py              # FastAPI application entry point (future)
│   ├── routers/             # API route handlers (future)
│   └── schemas.py           # Pydantic request/response schemas (future)
├── alembic/
│   ├── versions/            # Database migration scripts
│   │   └── 001_create_users_table.py
│   ├── env.py               # Alembic environment configuration
│   └── script.py.mako       # Migration template
├── alembic.ini              # Alembic configuration
├── tests/                   # Test suite (future)
└── README.md                # This file
```

## Environment Setup

### 1. Install Dependencies

```bash
# Install dependencies using uv
uv pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# Application
ENV=development
DEBUG=True

# JWT (for future authentication)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important**: Replace `DATABASE_URL` with your Neon PostgreSQL connection string.

### 3. Database Migrations

```bash
# Run migrations to create tables
uv run alembic upgrade head

# Verify migration status
uv run alembic current

# Rollback last migration (if needed)
uv run alembic downgrade -1
```

## Database Models

### User Model

Located in `app/models.py`, represents user accounts with authentication.

**Schema**:
- `id`: UUID (primary key, auto-generated)
- `email`: VARCHAR(255) (unique, indexed)
- `hashed_password`: VARCHAR(255) (bcrypt hash)
- `name`: VARCHAR(255) (nullable)
- `created_at`: TIMESTAMP WITH TIME ZONE (indexed)
- `updated_at`: TIMESTAMP WITH TIME ZONE

**Methods**:
- `verify_password(plain_password)`: Verify password against hash
- `hash_password(plain_password)`: Static method to hash passwords

**Security Features**:
- Passwords hashed with bcrypt (12 salt rounds)
- Email unique constraint at database level
- UUID primary keys for security
- Indexed email for fast login queries

## Database Connection

The `app/database.py` module provides:

### Connection Pooling Configuration

Optimized for Neon Serverless PostgreSQL:
- `pool_size=5`: Persistent connections
- `max_overflow=10`: Additional connections when pool exhausted
- `pool_pre_ping=True`: Verify connections before use (critical for serverless)
- `pool_recycle=3600`: Recycle connections after 1 hour

### FastAPI Dependency

```python
from app.database import get_db
from sqlmodel import Session

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.exec(select(User)).all()
    return users
```

### Manual Session Handling

```python
from app.database import get_session

with get_session() as db:
    user = User(email="test@example.com", ...)
    db.add(user)
    db.commit()
```

### Connection Testing

```python
from app.database import test_connection

# Test database connectivity
if test_connection():
    print("Database connected successfully!")
```

## Alembic Migration Workflow

### Create New Migration

```bash
# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "Add todo table"

# Create empty migration template
uv run alembic revision -m "Custom migration"
```

### Apply Migrations

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Apply specific migration
uv run alembic upgrade <revision_id>

# Apply next migration
uv run alembic upgrade +1
```

### Rollback Migrations

```bash
# Rollback last migration
uv run alembic downgrade -1

# Rollback to specific revision
uv run alembic downgrade <revision_id>

# Rollback all migrations
uv run alembic downgrade base
```

### Migration History

```bash
# Show current revision
uv run alembic current

# Show migration history
uv run alembic history

# Show pending migrations
uv run alembic heads
```

## Development Guidelines

### Adding New Models

1. Define model in `app/models.py`:
```python
class Todo(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=500)
    # ... other fields
```

2. Generate migration:
```bash
uv run alembic revision --autogenerate -m "Add todo table"
```

3. Review generated migration in `alembic/versions/`

4. Apply migration:
```bash
uv run alembic upgrade head
```

### Database Indexes

Critical indexes for performance:
- `user.email`: Unique index for login queries
- `user.created_at`: For sorting/filtering users
- `todo.user_id`: Foreign key index (when added)
- `todo.completed`: For filtering todos by status (when added)

### Security Best Practices

1. **User Data Isolation**:
   - ALWAYS filter queries by `user_id` from JWT token
   - NEVER trust `user_id` from request body
   - Verify ownership before UPDATE/DELETE operations

2. **Password Security**:
   - Passwords NEVER stored in plain text
   - Use `User.hash_password()` before saving
   - Use `user.verify_password()` for authentication

3. **SQL Injection Prevention**:
   - SQLModel uses parameterized queries automatically
   - Never concatenate SQL strings manually

4. **Connection Security**:
   - Always use SSL with Neon (`sslmode=require`)
   - Keep DATABASE_URL in environment variables
   - Never commit credentials to version control

## Testing Database Connection

```python
# Test connection
from app.database import test_connection

try:
    test_connection()
    print("✅ Database connection successful")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

## Troubleshooting

### Connection Issues

1. **SSL Required Error**:
   - Ensure `sslmode=require` is in DATABASE_URL
   - Neon requires SSL connections

2. **Pool Timeout**:
   - Check `pool_size` and `max_overflow` settings
   - Monitor connection usage with `get_pool_status()`

3. **Migration Conflicts**:
   - Run `uv run alembic current` to check status
   - Use `uv run alembic history` to see all migrations
   - Resolve conflicts by creating new migration

### Common Commands

```bash
# Check Python version
python --version  # Should be 3.13+

# Install dependencies
uv pip install -r requirements.txt

# Run migrations
uv run alembic upgrade head

# Check migration status
uv run alembic current

# Test database connection (future)
uv run python -c "from app.database import test_connection; test_connection()"
```

## Next Steps

1. **Authentication** (US1): Implement JWT-based auth endpoints
2. **Todo CRUD** (US2): Add Todo model and CRUD operations
3. **API Documentation**: Auto-generated with FastAPI Swagger UI
4. **Testing**: Add pytest tests for models and endpoints
5. **Deployment**: Configure for production with Neon

## References

- **Data Model**: `specs/001-todo-full-stack-app/data-model.md`
- **Database Skill**: `.claude/skills/database.skill.md`
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **Alembic Docs**: https://alembic.sqlalchemy.org/
- **Neon Docs**: https://neon.tech/docs/
