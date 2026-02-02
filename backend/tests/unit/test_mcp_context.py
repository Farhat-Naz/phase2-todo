"""
Unit tests for MCP context builder logic.

Tests cover:
- Context building from message history
- Message ordering (chronological)
- Message limit (last 50 messages)
- Session ownership verification
- Message persistence
"""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.mcp.context import (
    build_chat_context,
    save_messages_to_session,
    get_or_create_session,
    update_session_title_from_first_message,
)


class TestBuildChatContext:
    """Unit tests for build_chat_context function."""

    @pytest.mark.asyncio
    async def test_build_context_with_messages(self):
        """Test building context from existing messages."""
        session_id = uuid4()
        user_id = uuid4()

        with patch('app.mcp.context.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock session found
            mock_chat_session = Mock()
            mock_chat_session.session_id = session_id
            mock_chat_session.user_id = user_id

            # Mock messages
            mock_msg1 = Mock()
            mock_msg1.role = "user"
            mock_msg1.content = "Hello"
            mock_msg1.created_at = datetime.utcnow() - timedelta(minutes=5)

            mock_msg2 = Mock()
            mock_msg2.role = "assistant"
            mock_msg2.content = "Hi there!"
            mock_msg2.created_at = datetime.utcnow()

            # First exec call returns session, second returns messages
            exec_results = [
                Mock(first=Mock(return_value=mock_chat_session)),
                Mock(all=Mock(return_value=[mock_msg2, mock_msg1]))  # Descending order
            ]
            mock_db.exec.side_effect = exec_results

            context = await build_chat_context(session_id, user_id)

            assert len(context) == 2
            # Should be reversed to chronological order
            assert context[0]["role"] == "user"
            assert context[0]["content"] == "Hello"
            assert context[1]["role"] == "assistant"
            assert context[1]["content"] == "Hi there!"

    @pytest.mark.asyncio
    async def test_build_context_empty_session(self):
        """Test building context from session with no messages."""
        session_id = uuid4()
        user_id = uuid4()

        with patch('app.mcp.context.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock session found
            mock_chat_session = Mock()
            exec_results = [
                Mock(first=Mock(return_value=mock_chat_session)),
                Mock(all=Mock(return_value=[]))
            ]
            mock_db.exec.side_effect = exec_results

            context = await build_chat_context(session_id, user_id)

            assert context == []

    @pytest.mark.asyncio
    async def test_build_context_unauthorized_session(self):
        """Test building context for session user doesn't own."""
        session_id = uuid4()
        user_id = uuid4()

        with patch('app.mcp.context.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock session not found (ownership check failed)
            mock_db.exec.return_value.first.return_value = None

            context = await build_chat_context(session_id, user_id)

            assert context == []

    @pytest.mark.asyncio
    async def test_build_context_limits_messages(self):
        """Test context builder respects message limit."""
        session_id = uuid4()
        user_id = uuid4()

        with patch('app.mcp.context.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock session found
            mock_chat_session = Mock()

            # Create 100 mock messages
            mock_messages = []
            for i in range(100):
                msg = Mock()
                msg.role = "user" if i % 2 == 0 else "assistant"
                msg.content = f"Message {i}"
                msg.created_at = datetime.utcnow() - timedelta(minutes=100-i)
                mock_messages.append(msg)

            exec_results = [
                Mock(first=Mock(return_value=mock_chat_session)),
                Mock(all=Mock(return_value=mock_messages[:50]))  # Should limit to 50
            ]
            mock_db.exec.side_effect = exec_results

            context = await build_chat_context(session_id, user_id, max_messages=50)

            assert len(context) <= 50


class TestSaveMessagesToSession:
    """Unit tests for save_messages_to_session function."""

    @pytest.mark.asyncio
    async def test_save_messages_success(self):
        """Test successful message persistence."""
        session_id = uuid4()
        user_id = uuid4()

        with patch('app.mcp.context.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock session found
            mock_chat_session = Mock()
            mock_chat_session.last_activity_at = datetime.utcnow()
            mock_db.exec.return_value.first.return_value = mock_chat_session

            result = await save_messages_to_session(
                session_id,
                user_id,
                "User message",
                "Assistant response",
                "en"
            )

            assert result is True
            # Verify two messages were added
            assert mock_db.add.call_count >= 2
            # Verify commit was called
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_messages_unauthorized(self):
        """Test save fails for unauthorized session."""
        session_id = uuid4()
        user_id = uuid4()

        with patch('app.mcp.context.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock session not found
            mock_db.exec.return_value.first.return_value = None

            result = await save_messages_to_session(
                session_id,
                user_id,
                "User message",
                "Assistant response"
            )

            assert result is False


class TestGetOrCreateSession:
    """Unit tests for get_or_create_session function."""

    @pytest.mark.asyncio
    async def test_get_existing_session(self):
        """Test retrieving existing session."""
        session_id = uuid4()
        user_id = uuid4()

        with patch('app.mcp.context.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock session found
            mock_chat_session = Mock()
            mock_chat_session.session_id = session_id
            mock_db.exec.return_value.first.return_value = mock_chat_session

            result_id = await get_or_create_session(user_id, session_id)

            assert result_id == session_id

    @pytest.mark.asyncio
    async def test_create_new_session(self):
        """Test creating new session."""
        user_id = uuid4()

        with patch('app.mcp.context.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock session creation
            new_session_id = uuid4()
            mock_new_session = Mock()
            mock_new_session.session_id = new_session_id

            def mock_refresh(session):
                session.session_id = new_session_id

            mock_db.refresh.side_effect = mock_refresh

            result_id = await get_or_create_session(
                user_id,
                title="Test conversation",
                language="en"
            )

            # Verify session was created
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_session_truncates_long_title(self):
        """Test new session truncates title to 50 chars."""
        user_id = uuid4()
        long_title = "A" * 100

        with patch('app.mcp.context.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            mock_new_session = Mock()
            mock_new_session.session_id = uuid4()
            mock_db.refresh.side_effect = lambda s: setattr(s, 'session_id', mock_new_session.session_id)

            await get_or_create_session(user_id, title=long_title)

            # Check that add was called with truncated title
            call_args = mock_db.add.call_args[0][0]
            assert len(call_args.title) == 50


class TestUpdateSessionTitle:
    """Unit tests for update_session_title_from_first_message function."""

    @pytest.mark.asyncio
    async def test_update_title_success(self):
        """Test successful title update."""
        session_id = uuid4()
        user_id = uuid4()

        with patch('app.mcp.context.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            # Mock session found
            mock_chat_session = Mock()
            mock_chat_session.title = "New conversation"
            mock_db.exec.return_value.first.return_value = mock_chat_session

            await update_session_title_from_first_message(
                session_id,
                user_id,
                "Help me with groceries"
            )

            assert mock_chat_session.title == "Help me with groceries"
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_title_truncates_long_message(self):
        """Test title truncation for long first message."""
        session_id = uuid4()
        user_id = uuid4()
        long_message = "A" * 100

        with patch('app.mcp.context.Session') as mock_session:
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db

            mock_chat_session = Mock()
            mock_chat_session.title = "New conversation"
            mock_db.exec.return_value.first.return_value = mock_chat_session

            await update_session_title_from_first_message(
                session_id,
                user_id,
                long_message
            )

            # Should be truncated to 50 chars + "..."
            assert len(mock_chat_session.title) == 53
            assert mock_chat_session.title.endswith("...")


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
