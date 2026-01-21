"""
Context builder for MCP chat requests.

Builds conversation context by fetching message history from database
and formatting for MCP tool calls.

Strategy: Fetch last 50 messages for performance (<3s response target)
"""
from typing import List, Dict, Any
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime

from app.database import get_engine

engine = get_engine()
from app.models import ChatMessage, ChatSession


async def build_chat_context(
    session_id: UUID,
    user_id: UUID,
    max_messages: int = 50
) -> List[Dict[str, str]]:
    """
    Build conversation context from database message history.

    Fetches the last N messages from the specified session and formats them
    for MCP tool calls. Messages are ordered chronologically (oldest first).

    Args:
        session_id: UUID of the chat session
        user_id: UUID of the authenticated user (for ownership verification)
        max_messages: Maximum number of messages to fetch (default: 50)

    Returns:
        List of message dictionaries in format:
        [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            ...
        ]

    Security:
        - Verifies session ownership before fetching messages
        - Returns empty list if session not found or unauthorized

    Performance:
        - Limits to last 50 messages by default
        - Uses indexed query on session_id and created_at
        - Expected query time: <50ms
    """
    with Session(engine) as db:
        # Verify session ownership
        session = db.exec(
            select(ChatSession)
            .where(ChatSession.session_id == session_id)
            .where(ChatSession.user_id == user_id)
        ).first()

        if not session:
            # Session not found or user doesn't own it
            return []

        # Fetch last N messages ordered by created_at DESC
        messages = db.exec(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(max_messages)
        ).all()

        # Reverse to get chronological order (oldest first)
        messages = list(reversed(messages))

        # Format for MCP context
        context = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]

        return context


async def save_messages_to_session(
    session_id: UUID,
    user_id: UUID,
    user_message: str,
    assistant_message: str,
    language: str = "en"
) -> bool:
    """
    Save user and assistant messages to the database.

    This is called after receiving a response from the MCP server to persist
    both the user's message and the assistant's response.

    Args:
        session_id: UUID of the chat session
        user_id: UUID of the authenticated user
        user_message: The user's message content
        assistant_message: The assistant's response content
        language: Language of the messages ('en' or 'ur', default: 'en')

    Returns:
        True if messages saved successfully, False otherwise

    Side Effects:
        - Creates two ChatMessage records
        - Updates ChatSession.last_activity_at
    """
    try:
        with Session(engine) as db:
            # Verify session ownership
            session = db.exec(
                select(ChatSession)
                .where(ChatSession.session_id == session_id)
                .where(ChatSession.user_id == user_id)
            ).first()

            if not session:
                return False

            # Create user message
            user_msg = ChatMessage(
                session_id=session_id,
                role="user",
                content=user_message,
                language=language
            )
            db.add(user_msg)

            # Create assistant message
            assistant_msg = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=assistant_message,
                language=language
            )
            db.add(assistant_msg)

            # Update session last_activity_at
            session.last_activity_at = datetime.utcnow()
            db.add(session)

            db.commit()
            return True

    except Exception as e:
        import sys
        print(f"Failed to save messages: {e}", file=sys.stderr)
        return False


async def get_or_create_session(
    user_id: UUID,
    session_id: UUID = None,
    title: str = None,
    language: str = "en"
) -> UUID:
    """
    Get existing session or create new one (lazy creation strategy).

    Args:
        user_id: UUID of the authenticated user
        session_id: UUID of existing session (optional)
        title: Title for new session (optional, auto-generated from first message)
        language: Language for new session ('en' or 'ur', default: 'en')

    Returns:
        UUID of the session (existing or newly created)

    Strategy:
        - If session_id provided and exists: return it
        - If session_id not provided: create new session
        - Title defaults to truncated first message (max 50 chars)
    """
    with Session(engine) as db:
        # If session_id provided, verify it exists and user owns it
        if session_id:
            session = db.exec(
                select(ChatSession)
                .where(ChatSession.session_id == session_id)
                .where(ChatSession.user_id == user_id)
            ).first()

            if session:
                return session.session_id

        # Create new session
        if not title:
            title = "New conversation"

        # Truncate title to 50 chars (will be updated from first message)
        if len(title) > 50:
            title = title[:50]

        session = ChatSession(
            user_id=user_id,
            title=title,
            language=language
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        return session.session_id


async def update_session_title_from_first_message(
    session_id: UUID,
    user_id: UUID,
    first_message: str
):
    """
    Update session title based on first user message.

    Called after the first message in a session to set a descriptive title.

    Args:
        session_id: UUID of the chat session
        user_id: UUID of the authenticated user
        first_message: The user's first message content

    Strategy:
        - Truncate to 50 characters for display
        - Preserves full message in database, title is just for UI
    """
    with Session(engine) as db:
        session = db.exec(
            select(ChatSession)
            .where(ChatSession.session_id == session_id)
            .where(ChatSession.user_id == user_id)
        ).first()

        if not session:
            return

        # Update title (truncate to 50 chars for display)
        title = first_message.strip()
        if len(title) > 50:
            title = title[:50] + "..."

        session.title = title
        db.add(session)
        db.commit()
