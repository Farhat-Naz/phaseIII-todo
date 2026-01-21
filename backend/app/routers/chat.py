"""
Chat API router for MCP-based chatbot.

Endpoints:
- POST /api/chat - Send a message to the chatbot
- GET /api/chat/sessions - List user's chat sessions
- POST /api/chat/sessions - Create a new chat session
- GET /api/chat/sessions/{session_id}/messages - Get messages for a session
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.dependencies import get_current_user
from app.models import User
from app.services.chatbot_service import ChatbotService

router = APIRouter()


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for sending a chat message."""
    message: str = Field(..., min_length=1, max_length=5000, description="User message content")
    session_id: Optional[str] = Field(None, description="Existing session ID (creates new if not provided)")
    language: str = Field("en", pattern="^(en|ur)$", description="Language preference: 'en' or 'ur'")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Add buy groceries to my tasks",
                "session_id": None,
                "language": "en"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat message."""
    session_id: str = Field(..., description="Session ID for this conversation")
    assistant_message: str = Field(..., description="Assistant's response")
    language: str = Field(..., description="Language of the response")
    timestamp: str = Field(..., description="ISO timestamp of response")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "assistant_message": "I've added 'buy groceries' to your tasks.",
                "language": "en",
                "timestamp": "2026-01-20T12:00:00.000Z"
            }
        }


class SessionListResponse(BaseModel):
    """Response model for listing chat sessions."""
    sessions: List[dict] = Field(..., description="List of chat sessions")

    class Config:
        json_schema_extra = {
            "example": {
                "sessions": [
                    {
                        "session_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Buy groceries conversation",
                        "language": "en",
                        "created_at": "2026-01-20T12:00:00.000Z",
                        "last_activity_at": "2026-01-20T12:30:00.000Z"
                    }
                ]
            }
        }


# Endpoints
@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the chatbot",
    description="Process a user message through the MCP chatbot and return assistant's response"
)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
) -> ChatResponse:
    """
    Send a message to the chatbot.

    Flow:
    1. Validate user authentication
    2. Get or create session
    3. Fetch conversation history from database
    4. Send to MCP client (with tools for task management)
    5. Store user message + assistant response
    6. Return assistant response

    Args:
        request: ChatRequest with message, optional session_id, and language
        current_user: Authenticated user from JWT token

    Returns:
        ChatResponse with assistant's message and session info

    Raises:
        400: Invalid input (empty message, invalid language)
        401: Unauthorized (invalid/missing JWT token)
        500: Server error (MCP failure, database error)
    """
    try:
        # Parse session_id if provided
        session_id_uuid = UUID(request.session_id) if request.session_id else None

        # Process message through chatbot service
        result = await ChatbotService.process_message(
            user_id=current_user.id,
            user_message=request.message,
            session_id=session_id_uuid,
            language=request.language
        )

        return ChatResponse(**result)

    except ValueError as e:
        # Invalid UUID or empty message
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        # MCP or database failure
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chatbot service is temporarily unavailable. Please try again."
        )
    except Exception as e:
        # Unexpected error
        import sys
        print(f"Unexpected error in chat endpoint: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )


@router.get(
    "/sessions",
    response_model=SessionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user's chat sessions",
    description="Get all chat sessions for the authenticated user"
)
async def list_sessions(
    current_user: User = Depends(get_current_user)
) -> SessionListResponse:
    """
    List all chat sessions for the authenticated user.

    Returns sessions ordered by last_activity_at DESC (most recent first).

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        SessionListResponse with list of sessions

    Raises:
        401: Unauthorized (invalid/missing JWT token)
        500: Server error (database error)
    """
    try:
        from sqlmodel import Session, select
        from app.database import get_engine
        from app.models import ChatSession

        engine = get_engine()

        with Session(engine) as db:
            sessions = db.exec(
                select(ChatSession)
                .where(ChatSession.user_id == current_user.id)
                .order_by(ChatSession.last_activity_at.desc())
            ).all()

            return SessionListResponse(
                sessions=[
                    {
                        "session_id": str(session.session_id),
                        "title": session.title,
                        "language": session.language,
                        "created_at": session.created_at.isoformat(),
                        "last_activity_at": session.last_activity_at.isoformat()
                    }
                    for session in sessions
                ]
            )

    except Exception as e:
        import sys
        print(f"Error listing sessions: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat sessions"
        )


@router.get(
    "/sessions/{session_id}/messages",
    status_code=status.HTTP_200_OK,
    summary="Get messages for a session",
    description="Retrieve conversation history for a specific chat session"
)
async def get_session_messages(
    session_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get all messages for a specific chat session.

    Args:
        session_id: UUID of the chat session
        current_user: Authenticated user from JWT token

    Returns:
        List of messages ordered chronologically

    Raises:
        401: Unauthorized (invalid/missing JWT token)
        404: Session not found or user doesn't own session
        500: Server error (database error)
    """
    try:
        from sqlmodel import Session, select
        from app.database import get_engine
        from app.models import ChatSession, ChatMessage

        engine = get_engine()

        with Session(engine) as db:
            # Verify session ownership
            session = db.exec(
                select(ChatSession)
                .where(ChatSession.session_id == session_id)
                .where(ChatSession.user_id == current_user.id)
            ).first()

            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found or you don't have access"
                )

            # Fetch messages
            messages = db.exec(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc())
            ).all()

            return {
                "session_id": str(session_id),
                "messages": [
                    {
                        "message_id": str(msg.message_id),
                        "role": msg.role,
                        "content": msg.content,
                        "language": msg.language,
                        "created_at": msg.created_at.isoformat()
                    }
                    for msg in messages
                ]
            }

    except HTTPException:
        raise
    except Exception as e:
        import sys
        print(f"Error getting session messages: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )
