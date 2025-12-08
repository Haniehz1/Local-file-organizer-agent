# File Organizer - MCP Agent

An intelligent file organization system built with the **mcp-agent framework**. Automatically scans, classifies, and organizes files in your Downloads, Desktop, and other directories.

## ✨ Features

- 🔍 **Smart Scanning**: Recursively scans directories with SHA256 hash-based duplicate detection
- 🏷️ **Intelligent Classification**: 11+ file categories with pattern and extension matching
- 📋 **Safe Organization**: Always shows plan before executing changes
- 🔧 **MCP Server**: Exposes all functionality as MCP tools for Claude Desktop
- 🛡️ **Safety First**: Dry-run mode, collision handling, error recovery
- ⚡ **mcp-agent Native**: Built using proper `@app.async_tool()` patterns

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
# or
uv pip install -r requirements.txt
```

### 2. Configure

Edit `file_organizer/config.json`:
```json
{
  "scan_paths": ["~/Downloads", "~/Desktop"],
  "organization_rules": {
    "Screenshots": "~/Pictures/Screenshots",
    "PDFs": "~/Documents/PDFs"
  }
}
```

### 3. Run

**Interactive Mode:**
```bash
python main.py
```

**MCP Server Mode (for Claude Desktop):**
```bash
python main.py --server
```

**Quick Test:**
```bash
python test_quick.py
```

## 🔧 MCP Tools Exposed

All functionality exposed as async MCP tools:

1. **`scan_files(paths)`** - Scan directories and collect metadata
2. **`classify_files()`** - Classify scanned files into categories
3. **`propose_organization()`** - Generate an organization plan
4. **`execute_plan(dry_run)`** - Execute the plan (dry-run safe!)
5. **`get_summary()`** - Get markdown summary with stats
6. **`reset_state()`** - Clear stored state

## 🤖 Claude Desktop Integration

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
- *"Execute the plan (dry run first)"*

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
│   ├── scanner.py      # Hash-based scanning
│   ├── classifier.py   # Rule-based classification
│   ├── organizer.py    # Safe file operations
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

See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

## 📖 Documentation

- **[USAGE.md](USAGE.md)** - Detailed usage guide with examples
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture decisions
- **[SUMMARY.md](SUMMARY.md)** - Project summary & highlights
- **[CHECKLIST.md](CHECKLIST.md)** - Implementation checklist
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - File structure

## ✅ Safety Features

- ✅ **Dry-run mode** - Test before executing
- ✅ **Collision handling** - Auto-rename on conflict
- ✅ **Error recovery** - Continue after errors
- ✅ **Never overwrite** - Existing files safe
- ✅ **State management** - Track workflow progress

## 🎯 Example Workflow

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

## 🔑 Key Features

- Built with **mcp-agent SDK** (proper patterns)
- Uses `@app.async_tool()` decorators
- Stateful workflow design
- Type-safe with Pydantic
- Clean, modular architecture
- Production-ready error handling

## 📦 Dependencies

```
mcp-agent>=0.1.0    # Framework
pydantic>=2.0.0     # Data models
mcp>=1.0.0          # Protocol
```

## 🌟 Built With mcp-agent

This project demonstrates proper mcp-agent usage:
- ✅ MCPApp initialization
- ✅ @app.async_tool() decoration
- ✅ create_mcp_server_for_app() exposure
- ✅ async with app.run() context
- ✅ mcp_agent.config.yaml structure

## 📝 License

MIT

---

**Ready for Claude Desktop!** See [USAGE.md](USAGE.md) to get started.
