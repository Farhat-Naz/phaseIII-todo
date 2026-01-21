"""
MCP Server entry point with STDIO transport.

This module implements the Model Context Protocol server for task management,
providing tools for adding, listing, completing, and deleting tasks.

Transport: STDIO (standard input/output for same-server deployment)
"""
import asyncio
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from typing import Any
import yaml
from pathlib import Path

from app.mcp.tools import (
    add_task_handler,
    list_tasks_handler,
    complete_task_handler,
    delete_task_handler,
)


# Load system prompt from contracts/mcp-tools.yaml
def load_system_prompt() -> str:
    """Load system prompt from MCP tools contract file."""
    contract_path = Path(__file__).parent.parent.parent.parent / "specs" / "008-mcp-chatbot" / "contracts" / "mcp-tools.yaml"

    if not contract_path.exists():
        # Fallback to a basic system prompt
        return "You are a helpful task management assistant."

    try:
        with open(contract_path, 'r', encoding='utf-8') as f:
            contract = yaml.safe_load(f)
            return contract.get('system_prompt', "You are a helpful task management assistant.")
    except Exception as e:
        print(f"Warning: Failed to load system prompt: {e}", file=sys.stderr)
        return "You are a helpful task management assistant."


# Initialize MCP server
app = Server("task-management-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available MCP tools for task management.

    Returns:
        List of Tool definitions with JSON Schema input/output specifications
    """
    return [
        Tool(
            name="add_task",
            description="Create a new task for the authenticated user",
            inputSchema={
                "type": "object",
                "required": ["title"],
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title (short description of what needs to be done)",
                        "minLength": 1,
                        "maxLength": 255,
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task",
                        "maxLength": 1000,
                    },
                    "user_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "User ID from JWT token (automatically provided by server)",
                    },
                },
            },
        ),
        Tool(
            name="list_tasks",
            description="List all tasks for the authenticated user with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "completed": {
                        "type": "boolean",
                        "description": "Filter tasks by completion status (omit to get all tasks)",
                    },
                    "user_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "User ID from JWT token (automatically provided by server)",
                    },
                },
            },
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed (or toggle completion status)",
            inputSchema={
                "type": "object",
                "required": ["task_id"],
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "UUID of the task to mark as completed",
                    },
                    "user_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "User ID from JWT token (automatically provided by server)",
                    },
                },
            },
        ),
        Tool(
            name="delete_task",
            description="Delete a task permanently (cannot be undone)",
            inputSchema={
                "type": "object",
                "required": ["task_id"],
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "UUID of the task to delete",
                    },
                    "user_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "User ID from JWT token (automatically provided by server)",
                    },
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Handle MCP tool calls by routing to appropriate handler.

    Args:
        name: Tool name (add_task, list_tasks, complete_task, delete_task)
        arguments: Tool input parameters from LLM

    Returns:
        List of TextContent responses

    Security:
        - user_id is required and must match authenticated user
        - All database queries filter by user_id
        - Ownership verified before UPDATE/DELETE operations
    """
    try:
        # Route to appropriate handler
        if name == "add_task":
            result = await add_task_handler(arguments)
        elif name == "list_tasks":
            result = await list_tasks_handler(arguments)
        elif name == "complete_task":
            result = await complete_task_handler(arguments)
        elif name == "delete_task":
            result = await delete_task_handler(arguments)
        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]

        return [TextContent(type="text", text=result)]

    except Exception as e:
        # Log error but return user-friendly message
        print(f"MCP tool error ({name}): {e}", file=sys.stderr)
        return [TextContent(
            type="text",
            text=f"I'm having trouble processing that request. Please try again."
        )]


async def main():
    """
    Main entry point for MCP server with STDIO transport.

    This function starts the MCP server using standard input/output for communication.
    Suitable for same-server deployment where the chatbot service spawns this process.
    """
    # Load and display system prompt (for debugging)
    system_prompt = load_system_prompt()
    print(f"MCP Server initialized with system prompt ({len(system_prompt)} chars)", file=sys.stderr)

    # Start STDIO server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
