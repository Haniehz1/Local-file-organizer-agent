# File Organizer - Project Structure

## Complete File Tree

```
download_folder_manager/
│
├── file_organizer/                    # Main package
│   ├── __init__.py
│   ├── server.py                      # MCP server with @app.async_tool() decorators
│   ├── config.json                    # User configuration
│   │
│   ├── agents/                        # Core agent classes
│   │   ├── __init__.py
│   │   ├── scanner.py                 # File scanning & hash computation
│   │   ├── classifier.py              # Rule-based file classification
│   │   ├── organizer.py               # Plan creation & execution
│   │   └── reporter.py                # Summary generation
│   │
│   ├── models/                        # Pydantic data models
│   │   ├── __init__.py
│   │   └── file_metadata.py           # FileMetadata, Classification, Plan, etc.
│   │
│   ├── servers/                       # (Reserved for future extensions)
│   │   └── __init__.py
│   │
│   └── workflows/                     # (Reserved for Temporal workflows)
│       └── __init__.py
│
├── main.py                            # Main entrypoint (interactive + server modes)
├── test_quick.py                      # Quick functionality test
│
├── mcp_agent.config.yaml              # MCP Agent configuration
├── mcp_agent.secrets.yaml.example     # Secrets template
│
├── requirements.txt                   # Python dependencies
│
├── README.md                          # Project overview
├── USAGE.md                           # Detailed usage guide
├── SUMMARY.md                         # Project summary & highlights
└── PROJECT_STRUCTURE.md               # This file
```

## Key Files Explained

### Entry Points

- **main.py** - Main entrypoint with two modes:
  - Interactive mode: User-friendly CLI
  - Server mode: MCP server on STDIO for Claude Desktop

- **test_quick.py** - Quick test script to verify functionality

### Core Implementation

- **file_organizer/server.py** - MCP server implementation
  - Uses `@app.async_tool()` decorators
  - Implements all 6 MCP tools
  - Manages stateful workflow
  - Uses `create_mcp_server_for_app()` for server exposure

### Agent Classes

- **agents/scanner.py** - FileScanner class
  - Recursive directory scanning
  - SHA256 hash computation
  - Duplicate detection
  - Metadata extraction

- **agents/classifier.py** - FileClassifier class
  - Rule-based classification
  - Pattern matching
  - Extension mapping
  - Category grouping

- **agents/organizer.py** - FileOrganizer class
  - Plan creation
  - Safe file moving
  - Collision handling
  - Dry-run support

- **agents/reporter.py** - Reporter class
  - Summary generation
  - Markdown formatting
  - Plan preview formatting
  - Statistics calculation

### Data Models

- **models/file_metadata.py** - Pydantic models
  - FileMetadata
  - FileClassification
  - OrganizationAction
  - OrganizationPlan
  - ExecutionResult
  - ScanSummary

### Configuration

- **file_organizer/config.json** - User configuration
  - Scan paths
  - Organization rules
  - Duplicate handling
  - Auto-execute settings

- **mcp_agent.config.yaml** - MCP Agent config
  - App name and description
  - MCP servers (none needed)
  - Optional Temporal settings

- **mcp_agent.secrets.yaml.example** - Secrets template
  - API keys placeholder
  - Other sensitive config

### Documentation

- **README.md** - Quick overview and setup
- **USAGE.md** - Comprehensive usage guide with examples
- **SUMMARY.md** - Project summary and architecture highlights
- **PROJECT_STRUCTURE.md** - This file

## Code Organization Principles

### 1. Separation of Concerns

Each agent class has a single responsibility:
- Scanner: I/O operations
- Classifier: Categorization logic
- Organizer: Plan creation and execution
- Reporter: Output formatting

### 2. mcp-agent Integration

Follows mcp-agent best practices:
- `@app.async_tool()` for tool decoration
- `async with app.run()` for context management
- `create_mcp_server_for_app()` for server creation
- `Context` parameter for state access

### 3. Type Safety

Uses Pydantic models throughout:
- Type hints on all functions
- Validation at boundaries
- Serialization support

### 4. Extensibility

Easy to extend:
- Add categories in classifier.py
- Add organization rules in config.json
- Add new tools in server.py
- Add workflow tasks in workflows/

## Data Flow

```
User/Client
    ↓
main.py (entry point)
    ↓
file_organizer/server.py (MCP tools)
    ↓
agents/ (Scanner, Classifier, Organizer, Reporter)
    ↓
models/ (Pydantic data models)
    ↓
Filesystem (read/write operations)
```

## MCP Tool Flow

```
1. scan_files(paths)
   ↓ FileScanner
   ↓ Returns: JSON with file metadata
   ↓ Stores: files, duplicates in state

2. classify_files()
   ↓ FileClassifier
   ↓ Returns: JSON with categories
   ↓ Stores: classifications in state

3. propose_organization()
   ↓ FileOrganizer.create_plan()
   ↓ Returns: Markdown plan preview
   ↓ Stores: plan in state

4. execute_plan(dry_run)
   ↓ FileOrganizer.execute_plan()
   ↓ Returns: JSON with results
   ↓ Stores: result, summary in state

5. get_summary()
   ↓ Reporter.format_markdown()
   ↓ Returns: Markdown summary
   ↓ Reads: summary from state

6. reset_state()
   ↓ Clear all state
   ↓ Returns: Confirmation
```

## Configuration Files

### file_organizer/config.json

User-facing configuration:
```json
{
  "scan_paths": [...],           # Directories to scan
  "organization_rules": {...},   # Category → destination mapping
  "delete_duplicates": false,    # Duplicate handling
  "auto_execute": false          # Auto-execute without confirmation
}
```

### mcp_agent.config.yaml

Framework configuration:
```yaml
name: file-organizer
description: "..."
servers: {}                      # External MCP servers (none needed)
temporal: {...}                  # Optional: Temporal config
workflow_tasks_module: "..."     # Optional: Custom tasks
```

## State Management

Global state stored in `_scan_state` dict:
```python
{
    "files": [],              # List[FileMetadata]
    "classifications": [],    # List[FileClassification]
    "duplicates": {},         # Dict[hash, List[FileMetadata]]
    "plan": None,            # OrganizationPlan
    "result": None,          # ExecutionResult
    "summary": None          # ScanSummary
}
```

State persists across tool calls within a session.

## File Categories

Defined in `agents/classifier.py`:

| Category | Logic |
|----------|-------|
| Screenshots | Pattern + extension match |
| Images | Extension match (.png, .jpg, etc.) |
| Documents | Extension match (.doc, .txt, etc.) |
| PDFs | Extension match (.pdf) |
| Spreadsheets | Extension match (.xls, .csv, etc.) |
| Presentations | Extension match (.ppt, .key, etc.) |
| Archives | Extension match (.zip, .tar, etc.) |
| Installers | Pattern + extension match |
| Code | Extension match (.py, .js, etc.) |
| Videos | Extension match (.mp4, .mov, etc.) |
| Audio | Extension match (.mp3, .wav, etc.) |
| Unknown | No match found |

## Error Handling

- FileScanner: Catches PermissionError, logs and continues
- Organizer: Catches exceptions per-action, logs errors
- Reporter: Safe defaults if data missing
- Server tools: Return error JSON if state invalid

## Testing

- **test_quick.py** - Smoke test of main functionality
- Manual testing: `python main.py` with test directory
- Integration testing: Claude Desktop connection

## Future Extensions

Easy to add:
- New file categories (edit classifier.py)
- New organization rules (edit config.json)
- LLM classification (add to classifier.py)
- Temporal workflows (add to workflows/)
- Custom tasks (add workflow_task decorators)

## Dependencies

```
mcp-agent>=0.1.0    # Framework
pydantic>=2.0.0     # Data models
mcp>=1.0.0          # Protocol
```

## Development Setup

```bash
cd download_folder_manager
pip install -r requirements.txt
python test_quick.py    # Verify installation
python main.py          # Run interactive mode
```

## Production Deployment

```bash
# Option 1: Local MCP server for Claude Desktop
python main.py --server

# Option 2: Temporal cloud deployment (future)
# mcp-agent deploy

# Option 3: Programmatic usage
from file_organizer.server import app, run_full_workflow
```

---

This structure follows mcp-agent best practices and PRD requirements.
