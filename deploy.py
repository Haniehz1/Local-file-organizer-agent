#!/usr/bin/env python3
"""
File Organizer - Cloud Deployment Entry Point

This file exposes the MCPApp directly for mcp-agent cloud deployment.
"""
import sys
from pathlib import Path

# Add file_organizer to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and expose the app
from file_organizer.server import app

# The app object is already configured with all the @app.async_tool() decorators
# in file_organizer/server.py, so we just need to export it here.

if __name__ == "__main__":
    import asyncio
    from mcp_agent.server.app_server import create_mcp_server_for_app
    from mcp.server.stdio import stdio_server

    async def main():
        """Run as MCP server"""
        mcp_server = create_mcp_server_for_app(app)

        async with stdio_server() as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options()
            )

    asyncio.run(main())
