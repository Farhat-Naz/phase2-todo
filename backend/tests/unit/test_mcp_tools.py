"""
Unit tests for MCP tool handlers with mock database.

Tests cover:
- add_task tool with user scoping
- list_tasks tool with filtering
- complete_task tool with ownership verification
- delete_task tool with ownership verification
- Error handling for all tools
"""
import pytest
import json
from uuid import uuid4, UUID
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.mcp.tools import (
    add_task_handler,
    list_tasks_handler,
    complete_task_handler,
    delete_task_handler,
)


class TestAddTaskHandler:
    """Unit tests for add_task MCP tool."""

    @pytest.mark.asyncio
    async def test_add_task_success(self):
        """Test successful task creation."""
        user_id = uuid4()
        arguments = {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "user_id": str(user_id)
        }

        with patch('app.mcp.tools.Session') as mock_session:
            # Mock database session
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock task creation
            mock_task = Mock()
            mock_task.id = uuid4()
            mock_task.title = "Buy groceries"
            mock_task.description = "Milk, eggs, bread"
            mock_task.completed = False
            mock_task.created_at = datetime.utcnow()

            mock_db.refresh = Mock(side_effect=lambda t: setattr(t, 'id', mock_task.id))

            result = await add_task_handler(arguments)
            result_data = json.loads(result)

            assert "task_id" in result_data
            assert result_data["title"] == "Buy groceries"
            assert result_data["description"] == "Milk, eggs, bread"
            assert result_data["completed"] is False

    @pytest.mark.asyncio
    async def test_add_task_missing_title(self):
        """Test add_task with missing title returns error."""
        user_id = uuid4()
        arguments = {
            "description": "Some description",
            "user_id": str(user_id)
        }

        result = await add_task_handler(arguments)
        result_data = json.loads(result)

        assert result_data["error"] == "INVALID_INPUT"
        assert "required" in result_data["message"].lower()

    @pytest.mark.asyncio
    async def test_add_task_title_too_long(self):
        """Test add_task with title exceeding 255 chars."""
        user_id = uuid4()
        arguments = {
            "title": "A" * 256,
            "user_id": str(user_id)
        }

        result = await add_task_handler(arguments)
        result_data = json.loads(result)

        assert result_data["error"] == "INVALID_INPUT"
        assert "255" in result_data["message"]

    @pytest.mark.asyncio
    async def test_add_task_missing_user_id(self):
        """Test add_task without user_id returns UNAUTHORIZED."""
        arguments = {
            "title": "Test task"
        }

        result = await add_task_handler(arguments)
        result_data = json.loads(result)

        assert result_data["error"] == "UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_add_task_truncates_long_description(self):
        """Test add_task truncates description to 1000 chars."""
        user_id = uuid4()
        long_desc = "A" * 1500
        arguments = {
            "title": "Test",
            "description": long_desc,
            "user_id": str(user_id)
        }

        with patch('app.mcp.tools.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            mock_task = Mock()
            mock_task.id = uuid4()
            mock_task.title = "Test"
            mock_task.description = "A" * 1000  # Truncated
            mock_task.completed = False
            mock_task.created_at = datetime.utcnow()

            await add_task_handler(arguments)

            # Verify description was truncated when creating Todo
            call_args = mock_db.add.call_args
            assert len(call_args[0][0].description or "") <= 1000


class TestListTasksHandler:
    """Unit tests for list_tasks MCP tool."""

    @pytest.mark.asyncio
    async def test_list_tasks_success(self):
        """Test successful task listing."""
        user_id = uuid4()
        arguments = {
            "user_id": str(user_id)
        }

        with patch('app.mcp.tools.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock tasks
            mock_task1 = Mock()
            mock_task1.id = uuid4()
            mock_task1.title = "Task 1"
            mock_task1.description = "Description 1"
            mock_task1.completed = False
            mock_task1.created_at = datetime.utcnow()
            mock_task1.updated_at = datetime.utcnow()

            mock_exec_result = Mock()
            mock_exec_result.all.return_value = [mock_task1]
            mock_db.exec.return_value = mock_exec_result

            result = await list_tasks_handler(arguments)
            result_data = json.loads(result)

            assert "tasks" in result_data
            assert len(result_data["tasks"]) == 1
            assert result_data["tasks"][0]["title"] == "Task 1"

    @pytest.mark.asyncio
    async def test_list_tasks_filter_completed(self):
        """Test list_tasks with completed filter."""
        user_id = uuid4()
        arguments = {
            "completed": True,
            "user_id": str(user_id)
        }

        with patch('app.mcp.tools.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            mock_exec_result = Mock()
            mock_exec_result.all.return_value = []
            mock_db.exec.return_value = mock_exec_result

            result = await list_tasks_handler(arguments)
            result_data = json.loads(result)

            assert "tasks" in result_data
            assert len(result_data["tasks"]) == 0

    @pytest.mark.asyncio
    async def test_list_tasks_missing_user_id(self):
        """Test list_tasks without user_id returns UNAUTHORIZED."""
        arguments = {}

        result = await list_tasks_handler(arguments)
        result_data = json.loads(result)

        assert result_data["error"] == "UNAUTHORIZED"


class TestCompleteTaskHandler:
    """Unit tests for complete_task MCP tool."""

    @pytest.mark.asyncio
    async def test_complete_task_success(self):
        """Test successful task completion."""
        user_id = uuid4()
        task_id = uuid4()
        arguments = {
            "task_id": str(task_id),
            "user_id": str(user_id)
        }

        with patch('app.mcp.tools.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock task found
            mock_task = Mock()
            mock_task.id = task_id
            mock_task.title = "Test task"
            mock_task.completed = False
            mock_task.updated_at = datetime.utcnow()

            mock_exec_result = Mock()
            mock_exec_result.first.return_value = mock_task
            mock_db.exec.return_value = mock_exec_result

            result = await complete_task_handler(arguments)
            result_data = json.loads(result)

            assert result_data["task_id"] == str(task_id)
            assert result_data["completed"] is True

    @pytest.mark.asyncio
    async def test_complete_task_not_found(self):
        """Test complete_task with non-existent task."""
        user_id = uuid4()
        task_id = uuid4()
        arguments = {
            "task_id": str(task_id),
            "user_id": str(user_id)
        }

        with patch('app.mcp.tools.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock task not found
            mock_exec_result = Mock()
            mock_exec_result.first.return_value = None
            mock_db.exec.return_value = mock_exec_result

            result = await complete_task_handler(arguments)
            result_data = json.loads(result)

            assert result_data["error"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_complete_task_missing_task_id(self):
        """Test complete_task without task_id."""
        user_id = uuid4()
        arguments = {
            "user_id": str(user_id)
        }

        result = await complete_task_handler(arguments)
        result_data = json.loads(result)

        assert result_data["error"] == "INVALID_INPUT"


class TestDeleteTaskHandler:
    """Unit tests for delete_task MCP tool."""

    @pytest.mark.asyncio
    async def test_delete_task_success(self):
        """Test successful task deletion."""
        user_id = uuid4()
        task_id = uuid4()
        arguments = {
            "task_id": str(task_id),
            "user_id": str(user_id)
        }

        with patch('app.mcp.tools.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock task found
            mock_task = Mock()
            mock_task.id = task_id

            mock_exec_result = Mock()
            mock_exec_result.first.return_value = mock_task
            mock_db.exec.return_value = mock_exec_result

            result = await delete_task_handler(arguments)
            result_data = json.loads(result)

            assert result_data["success"] is True
            assert result_data["deleted_task_id"] == str(task_id)

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self):
        """Test delete_task with non-existent task."""
        user_id = uuid4()
        task_id = uuid4()
        arguments = {
            "task_id": str(task_id),
            "user_id": str(user_id)
        }

        with patch('app.mcp.tools.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock task not found
            mock_exec_result = Mock()
            mock_exec_result.first.return_value = None
            mock_db.exec.return_value = mock_exec_result

            result = await delete_task_handler(arguments)
            result_data = json.loads(result)

            assert result_data["error"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_delete_task_missing_user_id(self):
        """Test delete_task without user_id."""
        task_id = uuid4()
        arguments = {
            "task_id": str(task_id)
        }

        result = await delete_task_handler(arguments)
        result_data = json.loads(result)

        assert result_data["error"] == "UNAUTHORIZED"


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
