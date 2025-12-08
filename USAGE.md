# File Organizer - Usage Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or using uv (recommended for mcp-agent)
uv pip install -r requirements.txt
```

## Configuration

### 1. Edit file_organizer/config.json

Customize your file organization rules:

```json
{
  "scan_paths": [
    "~/Downloads",
    "~/Desktop"
  ],
  "organization_rules": {
    "Screenshots": "~/Pictures/Screenshots",
    "Documents": "~/Documents/Organized",
    "Images": "~/Pictures/Organized",
    "Archives": "~/Documents/Archives",
    "Installers": "~/Documents/Installers",
    "Code": "~/Documents/Code",
    "PDFs": "~/Documents/PDFs"
  },
  "delete_duplicates": false,
  "auto_execute": false
}
```

### 2. (Optional) Configure secrets

If you plan to use LLM-enhanced classification:

```bash
cp mcp_agent.secrets.yaml.example mcp_agent.secrets.yaml
# Edit mcp_agent.secrets.yaml to add API keys
```

## Running the Application

### Interactive Mode

Best for one-time organization tasks:

```bash
python main.py
```

Follow the prompts:
1. Enter paths to scan (or press Enter for defaults)
2. Choose dry-run (recommended first time) or actual execution
3. Review the organization plan
4. Confirm execution

### MCP Server Mode

Run as an MCP server for Claude Desktop or other clients:

```bash
python main.py --server
```

The server will run on STDIO and wait for MCP client connections.

## Claude Desktop Integration

### Configuration

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "file-organizer": {
      "command": "python3",
      "args": [
        "/absolute/path/to/download_folder_manager/main.py",
        "--server"
      ]
    }
  }
}
```

**Important:** Use the absolute path to main.py!

### Usage from Claude Desktop

Once configured, you can ask Claude:

```
"Can you scan my Downloads folder and organize it?"

"Show me what files are in my Downloads"

"Classify the files you scanned and propose an organization plan"

"Execute the organization plan (dry run first!)"

"Give me a summary of what was done"
```

Claude will use these MCP tools:
- `scan_files(paths)` - Scan directories
- `classify_files()` - Classify scanned files
- `propose_organization()` - Generate plan
- `execute_plan(dry_run)` - Execute plan
- `get_summary()` - Get summary report
- `reset_state()` - Clear stored state

## Workflow

The complete workflow has 5 steps:

### 1. Scan
```python
await scan_files(paths=["~/Downloads"])
```

Scans directories recursively, computes file hashes for duplicate detection.

### 2. Classify
```python
await classify_files()
```

Classifies files into categories based on extensions and filename patterns.

### 3. Propose Organization
```python
await propose_organization()
```

Generates a plan showing where each file will be moved.

### 4. Execute Plan
```python
await execute_plan(dry_run=True)  # dry_run=False for actual execution
```

Moves files according to the plan. Use `dry_run=True` to test first!

### 5. Get Summary
```python
await get_summary()
```

Returns a markdown summary with statistics and chaos index.

## Safety Features

### Dry Run Mode

Always test with `dry_run=True` first:
- Shows what would happen
- No files are moved
- No files are deleted

### Duplicate Detection

Files are compared using SHA256 hashes. Duplicates are:
- Identified in the plan
- Only deleted if `delete_duplicates: true` in config
- Keep first occurrence, mark others for deletion

### Collision Handling

If destination file exists:
- Automatically renames with suffix `_1`, `_2`, etc.
- Never overwrites existing files

### Error Recovery

- Logs all errors
- Continues processing after errors
- Reports failed actions in summary

## Customization

### Adding New Categories

Edit `file_organizer/agents/classifier.py`:

```python
CATEGORIES = {
    "YourCategory": {
        "extensions": [".ext1", ".ext2"],
        "patterns": [r"pattern1", r"pattern2"]
    },
    # ... other categories
}
```

Then add the rule in `config.json`:

```json
{
  "organization_rules": {
    "YourCategory": "~/path/to/destination"
  }
}
```

### Custom Scan Paths

Add to `config.json`:

```json
{
  "scan_paths": [
    "~/Downloads",
    "~/Desktop",
    "~/Documents/Temp",
    "/path/to/custom/folder"
  ]
}
```

## Troubleshooting

### Python not found

Use `python3` instead of `python` in commands.

### Permission denied

Ensure you have read/write permissions for:
- Source directories (scan_paths)
- Destination directories (organization_rules)

### Module not found

Make sure you're in the project directory:

```bash
cd /path/to/download_folder_manager
pip install -r requirements.txt
```

### MCP server not connecting

1. Check the absolute path in Claude Desktop config
2. Verify python/python3 command works
3. Test server manually: `python main.py --server`
4. Check Claude Desktop logs

## Examples

### Example 1: Quick Cleanup

```bash
$ python main.py
Enter paths to scan: ~/Downloads
Dry run? (Y/n): y

[Scans and shows plan]
[Safe to review without changes]
```

### Example 2: Actual Organization

```bash
$ python main.py
Enter paths to scan: ~/Downloads, ~/Desktop
Dry run? (Y/n): n

[Moves files according to plan]
[Shows summary with statistics]
```

### Example 3: Using from Claude Desktop

```
You: "Scan my Downloads folder and tell me what's there"
Claude: [Uses scan_files] "Found 150 files..."

You: "Classify them and propose an organization"
Claude: [Uses classify_files and propose_organization] "Here's the plan..."

You: "Do a dry run first"
Claude: [Uses execute_plan(dry_run=True)] "Dry run complete..."

You: "Looks good, execute it for real"
Claude: [Uses execute_plan(dry_run=False)] "Done! Here's the summary..."
```

## File Categories

| Category | Extensions | Patterns |
|----------|------------|----------|
| Screenshots | .png, .jpg, .jpeg | screenshot, screen shot |
| Images | .png, .jpg, .gif, .webp, etc. | - |
| Documents | .doc, .docx, .txt, .rtf | - |
| PDFs | .pdf | - |
| Spreadsheets | .xls, .xlsx, .csv | - |
| Presentations | .ppt, .pptx, .key | - |
| Archives | .zip, .tar, .rar, .7z | - |
| Installers | .dmg, .pkg, .exe, .msi | setup, install |
| Code | .py, .js, .ts, .java, etc. | - |
| Videos | .mp4, .mov, .avi, etc. | - |
| Audio | .mp3, .wav, .aac, etc. | - |
| Unknown | (anything else) | - |

## Best Practices

1. **Always dry run first** - See what will happen before executing
2. **Backup important files** - Before running on important directories
3. **Test with small folders** - Start with a small set of files
4. **Review the plan** - Read the organization plan carefully
5. **Check permissions** - Ensure you have write access to destinations
6. **Use specific paths** - More specific rules give better organization

## Advanced Usage

### Using mcp-agent Workflows

The tool is built on mcp-agent and can be extended with:
- Temporal workflows for scheduled runs
- Custom workflow tasks
- Agent composition patterns
- Cloud deployment

See `mcp_agent.config.yaml` for configuration options.

### Programmatic Usage

Import and use directly in Python:

```python
from file_organizer.server import app, run_full_workflow

async def main():
    async with app.run():
        summary = await run_full_workflow(
            scan_paths=["~/Downloads"],
            dry_run=True
        )
        print(summary)
```

## License

MIT
