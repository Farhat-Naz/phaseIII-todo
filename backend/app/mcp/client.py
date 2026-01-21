"""
MCP Client initialization with STDIO transport.

This module provides the MCP client for communicating with the MCP server
to execute task management tools.

Transport: STDIO (spawns MCP server as subprocess)
"""
import asyncio
import sys
from typing import Optional, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import asynccontextmanager
import os
from pathlib import Path


class MCPClient:
    """
    MCP Client for task management operations.

    Manages connection to MCP server via STDIO transport and provides
    methods for calling MCP tools with proper error handling.
    """

    def __init__(self):
        """Initialize MCP client (connection established on first use)."""
        self.session: Optional[ClientSession] = None
        self._read_stream = None
        self._write_stream = None

    async def connect(self):
        """
        Establish connection to MCP server via STDIO transport.

        Spawns the MCP server as a subprocess and establishes bidirectional
        communication via standard input/output.
        """
        if self.session is not None:
            return  # Already connected

        # Path to MCP server entry point
        server_script = Path(__file__).parent / "server.py"

        # Server parameters for STDIO transport
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "python", str(server_script)],
            env=os.environ.copy()
        )

        # Establish STDIO connection
        self._read_stream, self._write_stream = await stdio_client(server_params)

        # Create session
        self.session = ClientSession(self._read_stream, self._write_stream)

        # Initialize session
        await self.session.initialize()

        print("MCP Client connected to server", file=sys.stderr)

    async def disconnect(self):
        """Close connection to MCP server."""
        if self.session:
            await self.session.__aexit__(None, None, None)
            self.session = None
            self._read_stream = None
            self._write_stream = None

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """
        Call an MCP tool with given arguments.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool input parameters

        Returns:
            Tool response (parsed from JSON if applicable)

        Raises:
            RuntimeError: If not connected to server
            Exception: If tool call fails
        """
        if not self.session:
            raise RuntimeError("MCP client not connected. Call connect() first.")

        try:
            # Call tool via session
            result = await self.session.call_tool(tool_name, arguments)

            # Return result content
            if result.content and len(result.content) > 0:
                return result.content[0].text

            return None

        except Exception as e:
            print(f"MCP tool call error ({tool_name}): {e}", file=sys.stderr)
            raise


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


@asynccontextmanager
async def get_mcp_client():
    """
    Context manager for MCP client with automatic connection management.

    Usage:
        async with get_mcp_client() as client:
            result = await client.call_tool("add_task", {...})

    Yields:
        Connected MCPClient instance

    Note:
        Automatically connects on first use and maintains single instance
        for performance. Connection is kept alive across requests.
    """
    global _mcp_client

    if _mcp_client is None:
        _mcp_client = MCPClient()

    if _mcp_client.session is None:
        await _mcp_client.connect()

    try:
        yield _mcp_client
    except Exception as e:
        # Log error but don't disconnect (keep connection for next request)
        print(f"MCP client error: {e}", file=sys.stderr)
        raise


async def shutdown_mcp_client():
    """
    Shutdown MCP client connection.

    Call this during application shutdown to cleanly close the connection.
    """
    global _mcp_client

    if _mcp_client:
        await _mcp_client.disconnect()
        _mcp_client = None
