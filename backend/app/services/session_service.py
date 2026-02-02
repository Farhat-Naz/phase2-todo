"""
SessionService for chat session management.

Provides methods for:
- Creating new chat sessions
- Retrieving sessions by ID
- Listing user's sessions
- Updating last activity timestamp
- Deleting inactive sessions (cleanup job)
"""
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timedelta
from sqlmodel import Session, select

from app.database import engine
from app.models import ChatSession


class SessionService:
    """Service for managing chat sessions with user scoping."""

    @staticmethod
    def create_session(
        user_id: UUID,
        title: str = "New conversation",
        language: str = "en"
    ) -> ChatSession:
        """
        Create a new chat session for the user.

        Args:
            user_id: UUID of the authenticated user
            title: Session title (default: "New conversation")
            language: Preferred language ('en' or 'ur', default: 'en')

        Returns:
            Created ChatSession instance

        Note:
            Title can be updated later from first user message
        """
        with Session(engine) as db:
            session = ChatSession(
                user_id=user_id,
                title=title,
                language=language
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return session

    @staticmethod
    def get_session(session_id: UUID, user_id: UUID) -> Optional[ChatSession]:
        """
        Get a chat session by ID with ownership verification.

        Args:
            session_id: UUID of the session
            user_id: UUID of the authenticated user

        Returns:
            ChatSession if found and owned by user, None otherwise

        Security:
            Returns None if session doesn't exist or user doesn't own it
        """
        with Session(engine) as db:
            return db.exec(
                select(ChatSession)
                .where(ChatSession.session_id == session_id)
                .where(ChatSession.user_id == user_id)
            ).first()

    @staticmethod
    def list_sessions(
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatSession]:
        """
        List chat sessions for the user with pagination.

        Args:
            user_id: UUID of the authenticated user
            limit: Maximum number of sessions to return (default: 50)
            offset: Number of sessions to skip (default: 0)

        Returns:
            List of ChatSession instances ordered by last_activity_at DESC

        Performance:
            - Indexed query on user_id and last_activity_at
            - Pagination for large session lists
        """
        with Session(engine) as db:
            sessions = db.exec(
                select(ChatSession)
                .where(ChatSession.user_id == user_id)
                .order_by(ChatSession.last_activity_at.desc())
                .offset(offset)
                .limit(limit)
            ).all()
            return list(sessions)

    @staticmethod
    def update_last_activity(session_id: UUID, user_id: UUID) -> bool:
        """
        Update session's last activity timestamp.

        Args:
            session_id: UUID of the session
            user_id: UUID of the authenticated user

        Returns:
            True if updated successfully, False if session not found or unauthorized

        Note:
            Called automatically when messages are saved to session
        """
        with Session(engine) as db:
            session = db.exec(
                select(ChatSession)
                .where(ChatSession.session_id == session_id)
                .where(ChatSession.user_id == user_id)
            ).first()

            if not session:
                return False

            session.last_activity_at = datetime.utcnow()
            db.add(session)
            db.commit()
            return True

    @staticmethod
    def update_title(session_id: UUID, user_id: UUID, title: str) -> bool:
        """
        Update session title.

        Args:
            session_id: UUID of the session
            user_id: UUID of the authenticated user
            title: New title for the session

        Returns:
            True if updated successfully, False if session not found or unauthorized

        Note:
            Truncates title to 255 characters if longer
        """
        with Session(engine) as db:
            session = db.exec(
                select(ChatSession)
                .where(ChatSession.session_id == session_id)
                .where(ChatSession.user_id == user_id)
            ).first()

            if not session:
                return False

            # Truncate title to 255 chars
            session.title = title[:255] if len(title) > 255 else title
            db.add(session)
            db.commit()
            return True

    @staticmethod
    def delete_inactive_sessions(days_inactive: int = 30) -> int:
        """
        Delete sessions inactive for more than specified days.

        Args:
            days_inactive: Number of days of inactivity (default: 30)

        Returns:
            Number of sessions deleted

        Note:
            This is a cleanup job, typically run as a background task
            CASCADE delete ensures all messages are also deleted
        """
        with Session(engine) as db:
            cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)

            # Find inactive sessions
            inactive_sessions = db.exec(
                select(ChatSession)
                .where(ChatSession.last_activity_at < cutoff_date)
            ).all()

            count = len(inactive_sessions)

            # Delete sessions (CASCADE will delete messages)
            for session in inactive_sessions:
                db.delete(session)

            db.commit()
            return count

    @staticmethod
    def delete_session(session_id: UUID, user_id: UUID) -> bool:
        """
        Delete a specific session.

        Args:
            session_id: UUID of the session to delete
            user_id: UUID of the authenticated user

        Returns:
            True if deleted successfully, False if session not found or unauthorized

        Note:
            CASCADE delete ensures all messages are also deleted
        """
        with Session(engine) as db:
            session = db.exec(
                select(ChatSession)
                .where(ChatSession.session_id == session_id)
                .where(ChatSession.user_id == user_id)
            ).first()

            if not session:
                return False

            db.delete(session)
            db.commit()
            return True
