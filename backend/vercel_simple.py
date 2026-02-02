"""
Simple Vercel serverless function - No authentication for testing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Todo API - Simple",
    version="1.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory todo storage (for testing without database)
todos_storage = []

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "todo-api-simple",
        "version": "1.0.0"
    }

@app.get("/api/test")
async def test():
    """Simple test endpoint."""
    return {
        "status": "success",
        "message": "API is working!",
        "timestamp": "2026-01-15"
    }

@app.get("/api/todos")
async def get_todos():
    """Get all todos (no authentication)."""
    return {
        "todos": todos_storage,
        "count": len(todos_storage)
    }

@app.post("/api/todos")
async def create_todo(title: str, description: str = ""):
    """Create a new todo (no authentication)."""
    todo = {
        "id": len(todos_storage) + 1,
        "title": title,
        "description": description,
        "completed": False
    }
    todos_storage.append(todo)
    return todo

@app.patch("/api/todos/{todo_id}")
async def update_todo(todo_id: int, completed: bool = None, title: str = None):
    """Update a todo (no authentication)."""
    for todo in todos_storage:
        if todo["id"] == todo_id:
            if completed is not None:
                todo["completed"] = completed
            if title is not None:
                todo["title"] = title
            return todo

    return JSONResponse(
        status_code=404,
        content={"error": "Todo not found"}
    )

@app.delete("/api/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """Delete a todo (no authentication)."""
    global todos_storage
    todos_storage = [t for t in todos_storage if t["id"] != todo_id]
    return {"message": "Todo deleted"}

# Vercel handler
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
