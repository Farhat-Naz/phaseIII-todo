"""
Claude API Client for direct LLM integration with tool calling.

This module provides a direct integration with the Anthropic Claude API,
handling conversation management and tool execution without requiring
a separate MCP server process.
"""
import os
import json
from typing import Dict, Any, List, Optional
from uuid import UUID
from anthropic import Anthropic
from anthropic.types import (
    Message,
    MessageParam,
    TextBlock,
    ToolUseBlock,
    ToolResultBlockParam,
)

from app.mcp.tools import (
    add_task_handler,
    list_tasks_handler,
    complete_task_handler,
    delete_task_handler,
)


class ClaudeClient:
    """
    Client for direct Claude API integration with tool calling.

    Handles:
    - Message formatting for Claude API
    - Tool definitions and execution
    - Multi-turn conversation with tool usage
    - Error handling and retries
    """

    # Tool definitions for Claude API
    TOOLS = [
        {
            "name": "add_task",
            "description": "Create a new task for the authenticated user. Use this when the user wants to add, create, or save a new task.",
            "input_schema": {
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
        {
            "name": "list_tasks",
            "description": "List all tasks for the authenticated user with optional filtering. Use this when the user wants to see, view, or check their tasks.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "completed": {
                        "type": "boolean",
                        "description": "Filter tasks by completion status (omit to get all tasks)",
                    },
                },
            },
        },
        {
            "name": "complete_task",
            "description": "Mark a task as completed. Use this when the user wants to complete, finish, or mark a task as done.",
            "input_schema": {
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
        {
            "name": "delete_task",
            "description": "Delete a task permanently. Use this when the user wants to delete, remove, or get rid of a task.",
            "input_schema": {
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
    ]

    # System prompt for Claude
    SYSTEM_PROMPT = """You are a helpful task management assistant. You can help users manage their tasks by:
- Adding new tasks
- Listing existing tasks
- Marking tasks as completed
- Deleting tasks

Be conversational and friendly. When users ask to add, create, list, show, complete, finish, or delete tasks, use the appropriate tools.

If the user's message is in Urdu, respond in Urdu. If it's in English, respond in English.

When listing tasks, format them in a clear, numbered list. When adding or completing tasks, confirm the action clearly."""

    def __init__(self):
        """Initialize Claude client with API key from environment."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key == "your_anthropic_api_key_here":
            raise ValueError(
                "ANTHROPIC_API_KEY not set in environment. "
                "Please add your Anthropic API key to the .env file."
            )

        self.client = Anthropic(api_key=api_key)
        self.model = os.getenv("AI_MODEL", "claude-3-5-sonnet-20241022")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        user_id: UUID,
        max_turns: int = 5
    ) -> str:
        """
        Send messages to Claude and handle tool calls.

        Args:
            messages: List of message dicts with 'role' and 'content'
            user_id: UUID of the authenticated user (for tool calls)
            max_turns: Maximum number of tool call iterations (default: 5)

        Returns:
            Final assistant response text

        Raises:
            RuntimeError: If Claude API fails or tool execution fails
        """
        try:
            # Convert messages to Claude format
            claude_messages = self._convert_messages(messages)

            # Initial API call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.SYSTEM_PROMPT,
                messages=claude_messages,
                tools=self.TOOLS,
            )

            # Handle tool calls in a loop
            turns = 0
            while response.stop_reason == "tool_use" and turns < max_turns:
                turns += 1

                # Extract tool calls and execute them
                tool_results = await self._execute_tools(response, user_id)

                # Add assistant's response and tool results to messages
                claude_messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                claude_messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # Continue conversation with tool results
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=self.SYSTEM_PROMPT,
                    messages=claude_messages,
                    tools=self.TOOLS,
                )

            # Extract final text response
            return self._extract_text_response(response)

        except Exception as e:
            import sys
            print(f"Claude API error: {e}", file=sys.stderr)
            raise RuntimeError(f"Failed to communicate with Claude API: {str(e)}")

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[MessageParam]:
        """
        Convert simple message format to Claude API format.

        Args:
            messages: List of dicts with 'role' and 'content'

        Returns:
            List of MessageParam objects for Claude API
        """
        claude_messages = []
        for msg in messages:
            if msg["role"] in ["user", "assistant"]:
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        return claude_messages

    async def _execute_tools(
        self,
        response: Message,
        user_id: UUID
    ) -> List[ToolResultBlockParam]:
        """
        Execute all tool calls from Claude's response.

        Args:
            response: Claude API response containing tool calls
            user_id: UUID of the authenticated user

        Returns:
            List of tool result blocks to send back to Claude
        """
        tool_results = []

        for block in response.content:
            if isinstance(block, ToolUseBlock):
                # Execute the tool
                result = await self._execute_single_tool(
                    block.name,
                    block.input,
                    user_id
                )

                # Add result
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        return tool_results

    async def _execute_single_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: UUID
    ) -> str:
        """
        Execute a single tool call.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool input parameters from Claude
            user_id: UUID of the authenticated user

        Returns:
            JSON string with tool execution result
        """
        # Add user_id to arguments for all tool calls
        arguments["user_id"] = str(user_id)

        # Route to appropriate handler
        if tool_name == "add_task":
            return await add_task_handler(arguments)
        elif tool_name == "list_tasks":
            return await list_tasks_handler(arguments)
        elif tool_name == "complete_task":
            return await complete_task_handler(arguments)
        elif tool_name == "delete_task":
            return await delete_task_handler(arguments)
        else:
            return json.dumps({
                "error": "UNKNOWN_TOOL",
                "message": f"Tool '{tool_name}' not found"
            })

    def _extract_text_response(self, response: Message) -> str:
        """
        Extract text content from Claude's response.

        Args:
            response: Claude API response

        Returns:
            Combined text from all text blocks
        """
        text_parts = []
        for block in response.content:
            if isinstance(block, TextBlock):
                text_parts.append(block.text)

        return "\n".join(text_parts) if text_parts else "I'm having trouble responding right now. Please try again."


# Global client instance (singleton pattern)
_claude_client: Optional[ClaudeClient] = None


def get_claude_client() -> ClaudeClient:
    """
    Get or create the global Claude client instance.

    Returns:
        ClaudeClient instance

    Raises:
        ValueError: If ANTHROPIC_API_KEY is not configured
    """
    global _claude_client

    if _claude_client is None:
        _claude_client = ClaudeClient()

    return _claude_client
