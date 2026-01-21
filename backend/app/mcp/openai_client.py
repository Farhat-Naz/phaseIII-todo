"""
OpenAI API Client for direct LLM integration with function calling.

This module provides a direct integration with the OpenAI API,
handling conversation management and function execution.
"""
import os
import sys
import json
from typing import Dict, Any, List, Optional
from uuid import UUID
from openai import OpenAI

from app.mcp.tools import (
    add_task_handler,
    list_tasks_handler,
    complete_task_handler,
    delete_task_handler,
)


class OpenAIClient:
    """
    Client for direct OpenAI API integration with function calling.

    Handles:
    - Message formatting for OpenAI API
    - Function definitions and execution
    - Multi-turn conversation with function usage
    - Error handling and retries
    """

    # Function definitions for OpenAI API
    FUNCTIONS = [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the authenticated user. Use this when the user wants to add, create, or save a new task.",
                "parameters": {
                    "type": "object",
                    "required": ["title"],
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (short description of what needs to be done)",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional detailed description of the task",
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List all tasks for the authenticated user with optional filtering. Use this when the user wants to see, view, or check their tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "completed": {
                            "type": "boolean",
                            "description": "Filter tasks by completion status (omit to get all tasks)",
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as completed. Use this when the user wants to complete, finish, or mark a task as done.",
                "parameters": {
                    "type": "object",
                    "required": ["task_id"],
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "UUID of the task to mark as completed",
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task permanently. Use this when the user wants to delete, remove, or get rid of a task.",
                "parameters": {
                    "type": "object",
                    "required": ["task_id"],
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "UUID of the task to delete",
                        },
                    },
                },
            },
        },
    ]

    # System prompt for OpenAI
    SYSTEM_PROMPT = """You are a helpful task management assistant. You can help users manage their tasks by:
- Adding new tasks
- Listing existing tasks
- Marking tasks as completed
- Deleting tasks

Be conversational and friendly. When users ask to add, create, list, show, complete, finish, or delete tasks, use the appropriate functions.

If the user's message is in Urdu, respond in Urdu. If it's in English, respond in English.

When listing tasks, format them in a clear, numbered list. When adding or completing tasks, confirm the action clearly."""

    def __init__(self):
        """Initialize OpenAI client with API key from environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            raise ValueError(
                "OPENAI_API_KEY not set in environment. "
                "Please add your OpenAI API key to the .env file."
            )

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("AI_MODEL", "gpt-4o")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        user_id: UUID,
        max_turns: int = 5
    ) -> str:
        """
        Send messages to OpenAI and handle function calls.

        Args:
            messages: List of message dicts with 'role' and 'content'
            user_id: UUID of the authenticated user (for function calls)
            max_turns: Maximum number of function call iterations (default: 5)

        Returns:
            Final assistant response text

        Raises:
            RuntimeError: If OpenAI API fails or function execution fails
        """
        try:
            # Convert messages to OpenAI format
            openai_messages = self._convert_messages(messages)

            # Add system message
            openai_messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ] + openai_messages

            print(f"[OpenAI Debug] Sending {len(openai_messages)} messages to {self.model}", file=sys.stderr)

            # Initial API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                tools=self.FUNCTIONS,
                tool_choice="auto",
            )

            print(f"[OpenAI Debug] Received response, stop_reason: {response.choices[0].finish_reason}", file=sys.stderr)

            # Handle function calls in a loop
            turns = 0
            while response.choices[0].message.tool_calls and turns < max_turns:
                turns += 1

                # Add assistant's response to messages
                assistant_message = response.choices[0].message
                openai_messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        }
                        for tool_call in assistant_message.tool_calls
                    ]
                })

                # Execute all function calls
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Execute the function
                    function_result = await self._execute_function(
                        function_name,
                        function_args,
                        user_id
                    )

                    # Add function result to messages
                    openai_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_result
                    })

                # Continue conversation with function results
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=openai_messages,
                    tools=self.FUNCTIONS,
                    tool_choice="auto",
                )

            # Extract final text response
            return self._extract_text_response(response)

        except Exception as e:
            import sys
            print(f"OpenAI API error: {e}", file=sys.stderr)
            raise RuntimeError(f"Failed to communicate with OpenAI API: {str(e)}")

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Convert simple message format to OpenAI API format.

        Args:
            messages: List of dicts with 'role' and 'content'

        Returns:
            List of message dicts for OpenAI API
        """
        openai_messages = []
        for msg in messages:
            if msg["role"] in ["user", "assistant"]:
                openai_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        return openai_messages

    async def _execute_function(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        user_id: UUID
    ) -> str:
        """
        Execute a single function call.

        Args:
            function_name: Name of the function to execute
            arguments: Function input parameters from OpenAI
            user_id: UUID of the authenticated user

        Returns:
            JSON string with function execution result
        """
        # Add user_id to arguments for all function calls
        arguments["user_id"] = str(user_id)

        # Route to appropriate handler
        if function_name == "add_task":
            return await add_task_handler(arguments)
        elif function_name == "list_tasks":
            return await list_tasks_handler(arguments)
        elif function_name == "complete_task":
            return await complete_task_handler(arguments)
        elif function_name == "delete_task":
            return await delete_task_handler(arguments)
        else:
            return json.dumps({
                "error": "UNKNOWN_FUNCTION",
                "message": f"Function '{function_name}' not found"
            })

    def _extract_text_response(self, response) -> str:
        """
        Extract text content from OpenAI's response.

        Args:
            response: OpenAI API response

        Returns:
            Text content from the assistant's message
        """
        content = response.choices[0].message.content
        return content if content else "I'm having trouble responding right now. Please try again."


# Global client instance (singleton pattern)
_openai_client: Optional[OpenAIClient] = None


def get_openai_client() -> OpenAIClient:
    """
    Get or create the global OpenAI client instance.

    Returns:
        OpenAIClient instance

    Raises:
        ValueError: If OPENAI_API_KEY is not configured
    """
    global _openai_client

    if _openai_client is None:
        _openai_client = OpenAIClient()

    return _openai_client
