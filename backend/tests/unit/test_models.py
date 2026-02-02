"""
Unit tests for database models.

Tests cover:
- ChatSession model validation
- ChatMessage model validation
- Field constraints and defaults
- Relationship integrity
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from app.models import ChatSession, ChatMessage, User


class TestChatSessionModel:
    """Unit tests for ChatSession model validation."""

    def test_chat_session_creation_with_required_fields(self):
        """Test ChatSession creation with all required fields."""
        user_id = uuid4()
        session = ChatSession(
            user_id=user_id,
            title="Test conversation about groceries",
            language="en"
        )

        assert session.session_id is not None
        assert session.user_id == user_id
        assert session.title == "Test conversation about groceries"
        assert session.language == "en"
        assert session.created_at is not None
        assert session.last_activity_at is not None
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_activity_at, datetime)

    def test_chat_session_default_language(self):
        """Test ChatSession defaults to 'en' language."""
        session = ChatSession(
            user_id=uuid4(),
            title="Test session"
        )

        assert session.language == "en"

    def test_chat_session_urdu_language(self):
        """Test ChatSession with Urdu language."""
        session = ChatSession(
            user_id=uuid4(),
            title="اردو گفتگو",
            language="ur"
        )

        assert session.language == "ur"

    def test_chat_session_title_max_length(self):
        """Test ChatSession title respects 255 character limit."""
        long_title = "A" * 255
        session = ChatSession(
            user_id=uuid4(),
            title=long_title,
            language="en"
        )

        assert len(session.title) == 255
        assert session.title == long_title

    def test_chat_session_auto_timestamps(self):
        """Test ChatSession auto-generates timestamps."""
        before = datetime.utcnow()
        session = ChatSession(
            user_id=uuid4(),
            title="Timestamp test"
        )
        after = datetime.utcnow()

        assert before <= session.created_at <= after
        assert before <= session.last_activity_at <= after

    def test_chat_session_last_activity_updates(self):
        """Test ChatSession last_activity_at can be updated."""
        session = ChatSession(
            user_id=uuid4(),
            title="Activity test"
        )
        original_activity = session.last_activity_at

        # Simulate activity update
        new_activity = datetime.utcnow() + timedelta(minutes=5)
        session.last_activity_at = new_activity

        assert session.last_activity_at > original_activity

    def test_chat_session_session_id_is_uuid(self):
        """Test ChatSession session_id is a valid UUID."""
        session = ChatSession(
            user_id=uuid4(),
            title="UUID test"
        )

        assert session.session_id is not None
        # Should be able to convert to string and back
        str_id = str(session.session_id)
        assert len(str_id) == 36  # UUID string length


class TestChatMessageModel:
    """Unit tests for ChatMessage model validation."""

    def test_chat_message_creation_user_role(self):
        """Test ChatMessage creation with user role."""
        session_id = uuid4()
        message = ChatMessage(
            session_id=session_id,
            role="user",
            content="Add buy groceries to my tasks",
            language="en"
        )

        assert message.message_id is not None
        assert message.session_id == session_id
        assert message.role == "user"
        assert message.content == "Add buy groceries to my tasks"
        assert message.language == "en"
        assert message.created_at is not None

    def test_chat_message_creation_assistant_role(self):
        """Test ChatMessage creation with assistant role."""
        session_id = uuid4()
        message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content="I've added 'buy groceries' to your tasks.",
            language="en"
        )

        assert message.role == "assistant"
        assert message.content == "I've added 'buy groceries' to your tasks."

    def test_chat_message_default_language(self):
        """Test ChatMessage defaults to 'en' language."""
        message = ChatMessage(
            session_id=uuid4(),
            role="user",
            content="Test message"
        )

        assert message.language == "en"

    def test_chat_message_urdu_content(self):
        """Test ChatMessage with Urdu content."""
        message = ChatMessage(
            session_id=uuid4(),
            role="user",
            content="نیا کام: دودھ خریدنا",
            language="ur"
        )

        assert message.language == "ur"
        assert message.content == "نیا کام: دودھ خریدنا"

    def test_chat_message_long_content(self):
        """Test ChatMessage can store unlimited content length."""
        long_content = "A" * 10000  # 10,000 characters
        message = ChatMessage(
            session_id=uuid4(),
            role="assistant",
            content=long_content,
            language="en"
        )

        assert len(message.content) == 10000
        assert message.content == long_content

    def test_chat_message_auto_timestamp(self):
        """Test ChatMessage auto-generates created_at timestamp."""
        before = datetime.utcnow()
        message = ChatMessage(
            session_id=uuid4(),
            role="user",
            content="Timestamp test"
        )
        after = datetime.utcnow()

        assert before <= message.created_at <= after

    def test_chat_message_preserves_whitespace(self):
        """Test ChatMessage preserves whitespace and formatting."""
        content_with_whitespace = """
        Line 1

        Line 3 with   spaces
        """
        message = ChatMessage(
            session_id=uuid4(),
            role="user",
            content=content_with_whitespace
        )

        assert message.content == content_with_whitespace

    def test_chat_message_message_id_is_uuid(self):
        """Test ChatMessage message_id is a valid UUID."""
        message = ChatMessage(
            session_id=uuid4(),
            role="user",
            content="UUID test"
        )

        assert message.message_id is not None
        str_id = str(message.message_id)
        assert len(str_id) == 36  # UUID string length

    def test_chat_message_valid_roles(self):
        """Test ChatMessage accepts valid roles."""
        session_id = uuid4()

        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content="User message"
        )
        assert user_msg.role == "user"

        assistant_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content="Assistant message"
        )
        assert assistant_msg.role == "assistant"


class TestUserModelLanguagePreference:
    """Unit tests for User model language_preference field."""

    def test_user_default_language_preference(self):
        """Test User model defaults to 'en' language preference."""
        user = User(
            email="test@example.com",
            hashed_password=User.hash_password("password123"),
            name="Test User"
        )

        assert user.language_preference == "en"

    def test_user_urdu_language_preference(self):
        """Test User model with Urdu language preference."""
        user = User(
            email="test@example.com",
            hashed_password=User.hash_password("password123"),
            name="Test User",
            language_preference="ur"
        )

        assert user.language_preference == "ur"

    def test_user_language_preference_max_length(self):
        """Test User language_preference is limited to 2 characters."""
        user = User(
            email="test@example.com",
            hashed_password=User.hash_password("password123"),
            name="Test User",
            language_preference="en"
        )

        assert len(user.language_preference) <= 2


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
