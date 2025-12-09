# File Organizer - MCP Agent

An intelligent file organization system built with the **mcp-agent framework**. Automatically scans, classifies, and organizes files in your Downloads, Desktop, and other directories.

##  Features

- **Smart Scanning**: Top-level only scanning (protects project folders) with SHA256 duplicate detection
- **Intelligent Classification**: 12+ file categories with pattern and extension matching
- **Safe Organization**: Always shows plan before executing changes
- **Fully Reversible**: Backup manifests allow complete undo of all file moves
- **MCP Server**: Exposes all functionality as MCP tools for Claude Desktop
- **Safety First**: Dry-run mode, collision handling, error recovery
- **mcp-agent Native**: Built using proper `@app.async_tool()` patterns

##  Quick Start

### 1. Install Dependencies

```bash
pip install -e .
# or with uv
uv pip install -e .
```

### 2. Configure

Edit `file_organizer/config.json`:
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

### 3. Run

**Interactive Mode:**
```bash
uv run main.py
```

**MCP Server Mode (for Claude Desktop):**
```bash
uv run  main.py --server
```

## 🔧 MCP Tools Exposed

All functionality exposed as async MCP tools:

1. **`scan_files(paths)`** - Scan directories and collect metadata
2. **`classify_files()`** - Classify scanned files into categories
3. **`propose_organization()`** - Generate an organization plan
4. **`execute_plan(dry_run)`** - Execute the plan (dry-run safe!)
5. **`get_summary()`** - Get markdown summary with stats
6. **`list_backups()`** - List all available backup manifests
7. **`restore_from_backup(manifest_path, dry_run)`** - Undo file moves from a backup
8. **`reset_state()`** - Clear stored state

##  Deployment

### Option 1: Cloud Deployment (Recommended)

Deploy to mcp-agent cloud:

```bash
uvx mcp-agent login
uvx mcp-agent deploy file-organizer
```

After deployment, add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "file-organizer": {
      "url": "https://your-deployment-url.deployments.mcp-agent.com/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

### Option 2: Local Claude Desktop Integration

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "file-organizer": {
      "command": "python3",
      "args": ["/absolute/path/to/main.py", "--server"]
    }
  }
}
```

Then ask Claude:
- *"Scan my Downloads folder"*
- *"Classify and organize my files"*
- *"List available backups"*
- *"Restore from the most recent backup"*

## 📁 File Categories

| Category | Count | Examples |
|----------|-------|----------|
| Screenshots | Pattern-based | Screenshot 2024-*.png |
| Images | 11 types | .png, .jpg, .gif, .webp |
| Documents | 5 types | .doc, .txt, .rtf |
| PDFs | 1 type | .pdf |
| Code | 20+ types | .py, .js, .ts, .java |
| Archives | 6 types | .zip, .tar, .rar |
| Installers | 5+ types | .dmg, .pkg, .exe |
| Videos | 7 types | .mp4, .mov, .avi |
| Audio | 6 types | .mp3, .wav, .aac |
| Spreadsheets | 3 types | .xls, .csv |
| Presentations | 3 types | .ppt, .key |
| Unknown | Fallback | Everything else |

## 🏗️ Architecture

**Tool Provider Pattern** - We provide MCP tools, we don't consume them.

```
file_organizer/
├── agents/              # Core logic
│   ├── scanner.py      # Top-level scanning (protects folders)
│   ├── classifier.py   # Rule-based classification
│   ├── organizer.py    # Safe file operations
│   ├── backup.py       # Reversibility & manifest management
│   └── reporter.py     # Markdown generation
├── models/             # Pydantic data models
│   └── file_metadata.py
├── server.py           # MCP server (@app.async_tool)
└── config.json         # User configuration
```

Uses **direct Python I/O** (pathlib, shutil) for:
- SHA256 hashing
- Atomic file moves
- Performance

## Safety Features

- ✅ **Dry-run mode** - Test before executing
- ✅ **Backup manifests** - Every move is recorded and reversible
- ✅ **Top-level only** - Never touches project folders or subdirectories
- ✅ **Collision handling** - Auto-rename on conflict
- ✅ **Error recovery** - Continue after errors
- ✅ **Never overwrite** - Existing files safe
- ✅ **State management** - Track workflow progress

### Reversibility

When you execute file moves (not dry-run), a backup manifest is automatically created:

```json
{
  "timestamp": "20251208_143000",
  "actions": [
    {"action": "move", "source": "/Downloads/file.pdf", "destination": "~/Documents/PDFs/file.pdf"}
  ]
}
```

**To undo all changes:**
```python
# Via MCP tool
restore_from_backup()  # Uses most recent backup

# Or directly
python -c 'from file_organizer.agents.backup import BackupManager;
           BackupManager().restore_from_manifest("path/to/manifest.json", dry_run=False)'
```

Manifests are stored in `~/.file_organizer_backups/`

## Example Workflow

```bash
$ python main.py

Enter paths: ~/Downloads
Dry run? (Y/n): y

Step 1: Scanning... Found 150 files, 5 duplicates
Step 2: Classifying... 12 categories identified
Step 3: Planning... Will move 143 files
Step 4: Executing (DRY RUN)... [Shows plan]
Step 5: Summary...

Chaos Index: 8.6 → 2.1
```

## Key Features

- Built with **mcp-agent SDK** (proper patterns)
- Uses `@app.async_tool()` decorators
- Stateful workflow design
- Type-safe with Pydantic
- Clean, modular architecture
- Production-ready error handling

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

## License

MIT
