#!/usr/bin/env python3
"""
File Organizer - Main Entrypoint

A local MCP agent that scans, classifies, and organizes files.
Uses the mcp-agent framework to expose tools via MCP protocol.
"""
import asyncio
import sys
from pathlib import Path

# Add file_organizer to path
sys.path.insert(0, str(Path(__file__).parent))

from file_organizer.server import app, run_full_workflow, _scan_state
from file_organizer.agents.organizer import FileOrganizer
from mcp_agent.server.app_server import create_mcp_server_for_app
import json


async def interactive_mode():
    """Run in interactive mode with user prompts"""
    print("=" * 60)
    print("File Organizer - Interactive Mode")
    print("=" * 60)

    # Get paths to scan
    print("\nEnter paths to scan (comma-separated):")
    print("Press Enter for default (~/Downloads, ~/Desktop)")
    user_input = input("> ").strip()

    if user_input:
        scan_paths = [p.strip() for p in user_input.split(",")]
    else:
        scan_paths = None

    # Ask about dry run
    print("\nDo you want to do a DRY RUN (recommended)?")
    print("Dry run will show what would happen without moving files.")
    dry_run_input = input("Dry run? (Y/n): ").strip().lower()
    dry_run = dry_run_input != 'n'

    print("\n" + "=" * 60)
    print("Starting workflow...")
    print("=" * 60 + "\n")

    # Run the workflow
    async with app.run():
        result = await run_full_workflow(scan_paths=scan_paths, dry_run=dry_run)

        # Show backup information if actual execution occurred
        if not dry_run:
            from file_organizer.agents.backup import BackupManager
            backup_manager = BackupManager()
            latest_backup = backup_manager.get_latest_backup()

            if latest_backup:
                print("\n" + "=" * 60)
                print("✅ BACKUP CREATED")
                print("=" * 60)
                print(f"Backup manifest: {latest_backup}")
                print("\nTo undo these changes, run:")
                print(f"  python -c 'from file_organizer.agents.backup import BackupManager; ")
                print(f"             BackupManager().restore_from_manifest(\"{latest_backup}\", dry_run=False)'")
                print("\nOr use the MCP tool: restore_from_backup()")
                print("=" * 60)


async def server_mode():
    """Run as MCP server (for Claude Desktop or other clients)"""
    print("Starting File Organizer MCP Server...")
    print("Available tools:")
    print("  - scan_files")
    print("  - classify_files")
    print("  - propose_organization")
    print("  - execute_plan")
    print("  - get_summary")
    print("  - reset_state")
    print("  - list_backups")
    print("  - restore_from_backup")
    print("\nServer running on STDIO. Connect via Claude Desktop or other MCP clients...")

    # Create and run the MCP server
    mcp_server = create_mcp_server_for_app(app)

    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )


def print_usage():
    """Print usage instructions"""
    print("""
File Organizer - Usage

Modes:
  python main.py                    Run in interactive mode
  python main.py --server           Run as MCP server
  python main.py --help             Show this help

MCP Server Configuration:
  Add to your Claude Desktop config (~/.claude/claude_desktop_config.json):

  {
    "mcpServers": {
      "file-organizer": {
        "command": "python",
        "args": ["/path/to/main.py", "--server"]
      }
    }
  }

Quick Start:
  1. Edit file_organizer/config.json with your preferred settings
  2. Run: python main.py
  3. Follow the prompts
  4. Review the plan and execute (or do a dry run first)

Configuration:
  Edit file_organizer/config.json to customize:
  - scan_paths: Directories to scan
  - organization_rules: Where to move each category
  - delete_duplicates: Whether to delete duplicate files
    """)


async def main():
    """Main entrypoint"""
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print_usage()
        return

    if "--server" in args:
        await server_mode()
    else:
        await interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
