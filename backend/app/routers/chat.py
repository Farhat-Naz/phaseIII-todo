"""
Chat endpoints for AI-powered chatbot using OpenAI GPT-4o.

Endpoints:
- POST /api/chat/ - Send message and get AI response
"""
import os
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from typing import Annotated
from datetime import datetime

from app.dependencies import CurrentUser
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])

# OpenAI client (lazy init)
_openai_client = None


def get_openai_client():
    global _openai_client
    if _openai_client is None:
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            _openai_client = OpenAI(api_key=api_key)
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OpenAI package not installed"
            )
    return _openai_client


# In-memory session store (per-process, resets on cold start)
_sessions: dict[str, List[dict]] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: str = "en"


class ChatResponse(BaseModel):
    assistant_message: str
    session_id: str
    timestamp: str


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send chat message",
    description="Send a message to the AI chatbot and receive a response.",
)
async def send_message(
    request: ChatRequest,
    current_user: Annotated[User, CurrentUser],
) -> ChatResponse:
    """
    Send a message to OpenAI GPT-4o and get a response.

    Maintains conversation history per session for context.
    Session is identified by user_id + session_id.
    """
    client = get_openai_client()

    # Use session_id or create new one based on user
    session_id = request.session_id or str(current_user.id)
    session_key = f"{current_user.id}:{session_id}"

    # Get or create conversation history
    if session_key not in _sessions:
        _sessions[session_key] = []

    history = _sessions[session_key]

    # Add user message to history
    history.append({
        "role": "user",
        "content": request.message,
    })

    # Build system prompt
    lang_instruction = "Respond in Urdu." if request.language == "ur" else "Respond in English."
    system_prompt = (
        f"You are a helpful AI assistant for a Todo app called TodoApp. "
        f"Help users manage their tasks, answer questions, and provide productivity tips. "
        f"{lang_instruction} "
        f"Keep responses concise and friendly."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                *history,
            ],
            max_tokens=1024,
            temperature=0.7,
        )

        assistant_message = response.choices[0].message.content or "Sorry, I couldn't generate a response."

        # Add assistant response to history
        history.append({
            "role": "assistant",
            "content": assistant_message,
        })

        # Keep history manageable (last 20 messages)
        if len(history) > 20:
            _sessions[session_key] = history[-20:]

        return ChatResponse(
            assistant_message=assistant_message,
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        # Remove the failed user message from history
        if history:
            history.pop()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI response: {str(e)}",
        )
