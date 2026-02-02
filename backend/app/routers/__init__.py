"""
API routers for the Todo application.

This module exports all API routers for easy importing in main.py.

Available routers:
- auth: Authentication endpoints (register, login, me)
- todos: Todo CRUD endpoints (create, list, get, update, delete)
"""
from app.routers import auth, todos

__all__ = ["auth", "todos"]
