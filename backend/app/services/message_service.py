"""
MessageService for chat message management.

Provides methods for:
- Creating new messages
- Retrieving message history
- Pagination of messages
"""
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select

from app.database import engine
from app.models import ChatMessage, ChatSession


class MessageService:
    """Service for managing chat messages with session scoping."""

    @staticmethod
    def create_message(
        session_id: UUID,
        role: str,
        content: str,
        language: str = "en"
    ) -> ChatMessage:
        """
        Create a new chat message.

        Args:
            session_id: UUID of the parent session
            role: Message role ('user' or 'assistant')
            content: Message text content
            language: Language of the content ('en' or 'ur', default: 'en')

        Returns:
            Created ChatMessage instance

        Note:
            Does not verify session ownership (should be done by caller)
        """
        with Session(engine) as db:
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                language=language
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            return message

    @staticmethod
    def get_history(
        session_id: UUID,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatMessage]:
        """
        Get message history for a session with pagination.

        Args:
            session_id: UUID of the session
            user_id: UUID of the authenticated user (for ownership verification)
            limit: Maximum number of messages to return (default: 50)
            offset: Number of messages to skip (default: 0)

        Returns:
            List of ChatMessage instances ordered by created_at ASC (chronological)
            Returns empty list if session not found or user doesn't own it

        Security:
            Verifies session ownership before returning messages

        Performance:
            - Uses subquery to verify ownership without JOIN
            - Indexed query on session_id and created_at
            - Pagination for large conversations
        """
        with Session(engine) as db:
            # Verify session ownership
            session = db.exec(
                select(ChatSession)
                .where(ChatSession.session_id == session_id)
                .where(ChatSession.user_id == user_id)
            ).first()

            if not session:
                return []

            # Fetch messages ordered chronologically
            messages = db.exec(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc())
                .offset(offset)
                .limit(limit)
            ).all()

            return list(messages)

    @staticmethod
    def get_recent_messages(
        session_id: UUID,
        user_id: UUID,
        count: int = 50
    ) -> List[ChatMessage]:
        """
        Get the most recent N messages from a session.

        Args:
            session_id: UUID of the session
            user_id: UUID of the authenticated user
            count: Number of recent messages to retrieve (default: 50)

        Returns:
            List of ChatMessage instances ordered by created_at ASC (chronological)
            Returns empty list if session not found or user doesn't own it

        Note:
            This is optimized for context building in MCP requests.
            Fetches last N messages in DESC order, then reverses to chronological.
        """
        with Session(engine) as db:
            # Verify session ownership
            session = db.exec(
                select(ChatSession)
                .where(ChatSession.session_id == session_id)
                .where(ChatSession.user_id == user_id)
            ).first()

            if not session:
                return []

            # Fetch recent messages in reverse order
            messages = db.exec(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(count)
            ).all()

            # Reverse to get chronological order
            return list(reversed(messages))

    @staticmethod
    def count_messages(session_id: UUID, user_id: UUID) -> int:
        """
        Count total messages in a session.

        Args:
            session_id: UUID of the session
            user_id: UUID of the authenticated user

        Returns:
            Number of messages in the session
            Returns 0 if session not found or user doesn't own it
        """
        with Session(engine) as db:
            # Verify session ownership
            session = db.exec(
                select(ChatSession)
                .where(ChatSession.session_id == session_id)
                .where(ChatSession.user_id == user_id)
            ).first()

            if not session:
                return 0

            messages = db.exec(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
            ).all()

            return len(messages)

    @staticmethod
    def delete_message(message_id: UUID, user_id: UUID) -> bool:
        """
        Delete a specific message.

        Args:
            message_id: UUID of the message to delete
            user_id: UUID of the authenticated user

        Returns:
            True if deleted successfully, False if message not found or unauthorized

        Security:
            Verifies session ownership before allowing deletion
        """
        with Session(engine) as db:
            # Fetch message with session info
            message = db.exec(
                select(ChatMessage)
                .where(ChatMessage.message_id == message_id)
            ).first()

            if not message:
                return False

            # Verify session ownership
            session = db.exec(
                select(ChatSession)
                .where(ChatSession.session_id == message.session_id)
                .where(ChatSession.user_id == user_id)
            ).first()

            if not session:
                return False

            db.delete(message)
            db.commit()
            return True
