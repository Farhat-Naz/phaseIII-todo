"""
ChatbotService for orchestrating stateless chat conversations.

Provides methods for:
- Processing user messages through the MCP flow
- Building conversation context from database
- Handling MCP client calls
- Persisting messages to database
- Managing session lifecycle
"""
from uuid import UUID
from typing import Dict, Any, Optional
from datetime import datetime

from app.mcp.openai_client import get_openai_client
from app.mcp.context import (
    build_chat_context,
    save_messages_to_session,
    get_or_create_session,
    update_session_title_from_first_message,
)


class ChatbotService:
    """Service for orchestrating stateless chat conversations with MCP integration."""

    @staticmethod
    async def process_message(
        user_id: UUID,
        user_message: str,
        session_id: Optional[UUID] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Process a user message through the stateless chat flow.

        Flow:
        1. Get or create session (lazy creation)
        2. Fetch conversation history from database
        3. Build context array for MCP
        4. Send to MCP client (calls LLM with tools)
        5. Receive and parse MCP response
        6. Save user message + assistant response to database
        7. Update session last_activity timestamp
        8. Return response to caller

        Args:
            user_id: UUID of the authenticated user
            user_message: User's message text
            session_id: Optional UUID of existing session (creates new if None)
            language: Language code ('en' or 'ur', default: 'en')

        Returns:
            Dict with keys:
                - session_id: UUID of the session
                - assistant_message: Assistant's response text
                - language: Language of the conversation
                - timestamp: ISO timestamp of response

        Raises:
            RuntimeError: If MCP client fails to connect or process message
            ValueError: If user_message is empty

        Note:
            This is STATELESS - no conversation state is held in memory.
            All context is rebuilt from database on each call.
        """
        # Validate input
        if not user_message or not user_message.strip():
            raise ValueError("User message cannot be empty")

        # Step 1: Get or create session (lazy creation strategy)
        # If session_id is None, creates new session with title from first message
        active_session_id = await get_or_create_session(
            user_id=user_id,
            session_id=session_id,
            title=user_message[:50] + "..." if len(user_message) > 50 else user_message,
            language=language
        )

        # Step 2: Fetch conversation history from database
        # Fetches last 50 messages in chronological order
        context = await build_chat_context(
            session_id=active_session_id,
            user_id=user_id,
            max_messages=50
        )

        # Step 3: Build full context with new user message
        full_context = context + [{"role": "user", "content": user_message}]

        # Step 4: Call OpenAI API with context and functions
        try:
            openai_client = get_openai_client()
            assistant_message = await openai_client.chat(
                messages=full_context,
                user_id=user_id,
                max_turns=5
            )
        except ValueError as e:
            # API key not configured
            raise RuntimeError(f"OpenAI API not configured: {str(e)}")
        except Exception as e:
            # Other OpenAI API errors
            import sys
            print(f"OpenAI API error: {e}", file=sys.stderr)
            raise RuntimeError(f"Failed to get response from OpenAI: {str(e)}")

        # Step 5: Save both messages to database
        # This updates ChatSession.last_activity_at automatically
        success = await save_messages_to_session(
            session_id=active_session_id,
            user_id=user_id,
            user_message=user_message,
            assistant_message=assistant_message,
            language=language
        )

        if not success:
            raise RuntimeError("Failed to save messages to database")

        # Step 6: Update session title from first message if default title
        if len(context) == 0:  # First message in new session
            await update_session_title_from_first_message(
                session_id=active_session_id,
                user_id=user_id,
                first_message=user_message
            )

        # Step 7: Return response
        return {
            "session_id": str(active_session_id),
            "assistant_message": assistant_message,
            "language": language,
            "timestamp": datetime.utcnow().isoformat()
        }

