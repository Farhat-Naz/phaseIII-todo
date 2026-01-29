"""
Chat endpoints for AI-powered chatbot using MCP architecture.

This module provides stateless chat endpoints with:
- OpenAI GPT-4o with function calling
- MCP tools for task management
- Database-persisted conversation history
- Multi-language support (English/Urdu)

Endpoints:
- POST /api/chat/ - Send message and get AI response
"""
import os
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from sqlmodel import Session, select

from app.dependencies import CurrentUser
from app.models import User, ChatSession, ChatMessage
from app.database import get_db
from app.mcp.openai_client import get_openai_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


@router.get("/test", summary="Test OpenAI client initialization")
async def test_openai_client():
    """Test endpoint to verify OpenAI client can be initialized."""
    try:
        client = get_openai_client()
        return {
            "status": "success",
            "message": "OpenAI client initialized successfully",
            "model": client.model,
        }
    except Exception as e:
        logger.error(f"OpenAI client test failed: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "detail": "Check OPENAI_API_KEY environment variable",
        }


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: Optional[str] = None
    language: str = "en"


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    assistant_message: str
    session_id: str
    timestamp: str


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send chat message",
    description="Send a message to the AI chatbot and receive a response with MCP-powered task management.",
)
async def send_message(
    request: ChatRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    Send a message to OpenAI GPT-4o with MCP tools for task management.

    **Stateless Design:**
    - Loads conversation history from database
    - Processes message with OpenAI + MCP tools
    - Saves conversation back to database
    - No in-memory state

    **MCP Tools:**
    - add_task: Create new task
    - list_tasks: List user's tasks
    - complete_task: Mark task as completed
    - delete_task: Delete task

    **Multi-turn Function Calling:**
    - AI can call multiple tools in sequence
    - Results are persisted to database
    - Conversation continues until natural response
    """
    try:
        logger.info(f"Chat request from user {current_user.id}: {request.message[:50]}...")

        # Get or create chat session
        logger.debug("Getting or creating chat session...")
        session = await _get_or_create_session(
            db=db,
            user_id=current_user.id,
            session_id=request.session_id,
            language=request.language,
            first_message=request.message,
        )
        logger.debug(f"Chat session: {session.session_id}")

        # Load conversation history from database
        logger.debug("Loading conversation history...")
        history = await _load_conversation_history(db, session.session_id)
        logger.debug(f"Loaded {len(history)} messages from history")

        # Add user message to history
        history.append({
            "role": "user",
            "content": request.message,
        })

        # Save user message to database
        logger.debug("Saving user message to database...")
        user_msg = ChatMessage(
            session_id=session.session_id,
            role="user",
            content=request.message,
            language=request.language,
        )
        db.add(user_msg)
        db.commit()
        logger.debug("User message saved")

        # Get OpenAI client and send request with MCP tools
        logger.info("Initializing OpenAI client...")
        try:
            client = get_openai_client()
            logger.info("OpenAI client initialized successfully")
        except Exception as client_error:
            logger.error(f"Failed to initialize OpenAI client: {client_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OpenAI client initialization failed: {str(client_error)}"
            )

        logger.info("Sending request to OpenAI...")
        try:
            assistant_response = await client.chat(
                messages=history,
                user_id=current_user.id,
            )
            logger.info(f"Received response from OpenAI: {assistant_response[:100]}...")
        except Exception as openai_error:
            logger.error(f"OpenAI API call failed: {openai_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OpenAI API error: {str(openai_error)}"
            )

        # Save assistant response to database
        assistant_msg = ChatMessage(
            session_id=session.session_id,
            role="assistant",
            content=assistant_response,
            language=request.language,
        )
        db.add(assistant_msg)

        # Update session last activity
        session.last_activity_at = datetime.utcnow()
        db.add(session)
        db.commit()

        return ChatResponse(
            assistant_message=assistant_response,
            session_id=str(session.session_id),
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}",
        )


async def _get_or_create_session(
    db: Session,
    user_id: UUID,
    session_id: Optional[str],
    language: str,
    first_message: str,
) -> ChatSession:
    """
    Get existing session or create new one.

    Args:
        db: Database session
        user_id: Current user's UUID
        session_id: Optional session ID from client
        language: Message language
        first_message: First user message (for title generation)

    Returns:
        ChatSession instance
    """
    # Try to find existing session
    if session_id:
        try:
            session_uuid = UUID(session_id)
            session = db.exec(
                select(ChatSession)
                .where(ChatSession.session_id == session_uuid)
                .where(ChatSession.user_id == user_id)
            ).first()

            if session:
                return session
        except ValueError:
            logger.warning(f"Invalid session_id format: {session_id}")

    # Create new session
    # Generate title from first message (first 50 chars)
    title = first_message[:50] + "..." if len(first_message) > 50 else first_message

    session = ChatSession(
        user_id=user_id,
        title=title,
        language=language,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info(f"Created new chat session: {session.session_id} for user {user_id}")
    return session


async def _load_conversation_history(
    db: Session,
    session_id: UUID,
    limit: int = 20,
) -> List[dict]:
    """
    Load conversation history from database.

    Args:
        db: Database session
        session_id: Chat session UUID
        limit: Maximum number of messages to load (default: 20)

    Returns:
        List of message dicts with 'role' and 'content'
    """
    messages = db.exec(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    ).all()

    return [
        {
            "role": msg.role,
            "content": msg.content,
        }
        for msg in messages
    ]
