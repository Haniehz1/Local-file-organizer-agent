# Deployment Guide

## Local MCP Server Deployment

Your file organizer is already configured as an MCP server and can be deployed in multiple ways:

### Option 1: Claude Desktop Integration (Recommended)

Add to your `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "file-organizer": {
      "command": "python3",
      "args": ["/absolute/path/to/download_folder_manager/main.py", "--server"]
    }
  }
}
```

**Important:** Replace `/absolute/path/to/download_folder_manager/` with your actual path:
```bash
pwd  # Run this in the project directory to get the full path
```

Then restart Claude Desktop, and you can use commands like:
- "Scan my Downloads folder"
- "Classify and organize my files"
- "List available backups"
- "Restore from the most recent backup"

### Option 2: Standalone Python Process

Run as a persistent MCP server:

```bash
cd /path/to/download_folder_manager
python main.py --server
```

This starts an MCP server on STDIO that any MCP client can connect to.

### Option 3: Remote/Cloud Deployment

For cloud deployment, you would need to:

1. **Deploy to a server** (AWS, GCP, Azure, etc.)
2. **Use SSH or remote execution** to run the MCP server
3. **Configure Claude Desktop** to connect via SSH:

```json
{
  "mcpServers": {
    "file-organizer": {
      "command": "ssh",
      "args": [
        "user@your-server.com",
        "cd /path/to/app && python3 main.py --server"
      ]
    }
  }
}
```

### Option 4: Docker Deployment

Create a Docker container for portability:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "main.py", "--server"]
```

Build and run:
```bash
docker build -t file-organizer-mcp .
docker run -v ~/Downloads:/downloads file-organizer-mcp
```

## Available MCP Tools

When deployed, your app exposes these tools to MCP clients:

1. **scan_files** - Scan directories for files
2. **classify_files** - Classify files into categories
3. **propose_organization** - Generate organization plan
4. **execute_plan** - Execute the plan (with dry-run option)
5. **get_summary** - Get execution summary
6. **list_backups** - List all backup manifests
7. **restore_from_backup** - Undo file moves
8. **reset_state** - Clear workflow state

## Configuration

Edit `file_organizer/config.json` to customize:

```json
{
  "scan_paths": ["~/Downloads"],
  "scan_mode": "top_level_only",
  "organization_rules": {
    "Screenshots": "~/Pictures/Screenshots",
    "PDFs": "~/Documents/PDFs"
  }
}
```

## Security Notes

- The `mcp_agent.secrets.yaml` file is gitignored and should never be committed
- Backup manifests are stored in `~/.file_organizer_backups/`
- All file operations require explicit execution (dry-run by default)

## Testing

Test your MCP server locally:

```bash
# Interactive mode
python main.py

# Server mode (for MCP clients)
python main.py --server
```

## Troubleshooting

**Issue:** Claude Desktop doesn't see the tools
- Restart Claude Desktop completely
- Check that the path in config is absolute, not relative
- Verify `python main.py --server` runs without errors

**Issue:** Permission errors
- Check file permissions on scan_paths
- Ensure Python has access to the directories

**Issue:** No backups created
- Backups are only created when `dry_run=False`
- Check `~/.file_organizer_backups/` exists
