# File Organizer - Architecture

## Key Architecture Decision

**This app PROVIDES MCP tools, it doesn't consume them.**

### Why No Filesystem MCP Server?

We use **direct Python file operations** (pathlib, shutil) because:

1. **Hash computation** - Need SHA256 hashing for duplicate detection
2. **Atomic operations** - Need safe file moving with collision handling
3. **Performance** - Direct I/O is faster than MCP protocol overhead
4. **Simplicity** - No need for intermediate protocol layer

### When Would We Use Filesystem MCP Server?

If we were building an **agent that calls other tools**, we'd use MCP servers. For example:
- A research agent using `filesystem` + `fetch` + `brave-search` servers
- A code assistant using `filesystem` + `github` servers

But since we **ARE the tool provider**, we implement file operations directly.

## Clean Folder Structure

```
file_organizer/
├── __init__.py
├── agents/              # Core logic
│   ├── scanner.py      # File I/O (pathlib)
│   ├── classifier.py   # Business logic
│   ├── organizer.py    # File operations (shutil)
│   └── reporter.py     # Formatting
├── models/             # Data models (Pydantic)
│   └── file_metadata.py
├── server.py           # MCP server (@app.async_tool)
└── config.json         # User configuration
```

### What We Removed

- ❌ `.mcp-agent/` - Not needed (use root `mcp_agent.config.yaml`)
- ❌ `servers/` - Empty folder, not needed
- ❌ `workflows/` - Empty folder, not needed

### What We Kept

- ✅ `.claude/` - Your Claude Code settings (don't touch)
- ✅ `agents/` - Core business logic
- ✅ `models/` - Pydantic data models

## mcp-agent SDK Usage

### 1. App Creation

```python
from mcp_agent.app import MCPApp

app = MCPApp(
    name="file-organizer",
    description="..."
)
```

### 2. Tool Decoration

```python
@app.async_tool()
async def scan_files(paths: Optional[List[str]] = None, app_ctx: Context | None = None) -> str:
    """Scan directories and collect file metadata"""
    # Direct Python file operations
    scanner = FileScanner()
    files = scanner.scan_paths(paths)
    return json.dumps(result)
```

### 3. Server Exposure

```python
from mcp_agent.server.app_server import create_mcp_server_for_app
from mcp.server.stdio import stdio_server

mcp_server = create_mcp_server_for_app(app)

async with stdio_server() as (read_stream, write_stream):
    await mcp_server.run(read_stream, write_stream, ...)
```

### 4. Configuration

```yaml
# mcp_agent.config.yaml
name: file-organizer
description: "..."
servers: {}  # We don't consume MCP servers
```

## Tool Flow

```
Claude Desktop (or other MCP client)
    ↓ (MCP protocol)
main.py --server
    ↓ (STDIO)
create_mcp_server_for_app(app)
    ↓
@app.async_tool() decorated functions
    ↓
agents/ (Scanner, Classifier, Organizer)
    ↓ (direct Python I/O)
Filesystem (pathlib, shutil, hashlib)
```

## Why This Is Correct

### ✅ Proper mcp-agent Usage

1. Uses `MCPApp` for app creation
2. Uses `@app.async_tool()` for tool decoration
3. Uses `create_mcp_server_for_app()` for server exposure
4. Uses `async with app.run()` for context management
5. Includes `app_ctx: Context | None` parameter

### ✅ Clean Architecture

1. Separation of concerns (agents vs server)
2. Pydantic models for type safety
3. Configuration file for user settings
4. No unnecessary folders or files

### ✅ Correct Tool Provider Pattern

We implement tools that:
- Scan files → return metadata
- Classify files → return categories
- Propose plan → return markdown
- Execute plan → move files
- Get summary → return report

External clients (Claude Desktop) call these tools via MCP protocol.

## Comparison: Tool Provider vs Tool Consumer

### Tool Provider (This App)

```python
@app.async_tool()
async def scan_files(paths):
    # Direct implementation
    scanner = FileScanner()
    return scanner.scan_paths(paths)

# Exposed via MCP for others to use
```

### Tool Consumer (Different Pattern)

```python
async def research_agent():
    async with app.run():
        agent = Agent(
            server_names=["filesystem", "fetch"]  # Use external MCP servers
        )
        llm = await agent.attach_llm(OpenAIAugmentedLLM)
        result = await llm.generate_str("Research topic")
        # LLM calls filesystem.read_file, fetch.get, etc.
```

## Summary

**File Organizer Architecture:**
- ✅ Provides MCP tools (not consumes)
- ✅ Uses direct Python file operations
- ✅ Clean folder structure (no unused folders)
- ✅ Proper mcp-agent SDK patterns
- ✅ Ready for Claude Desktop integration

**Key Insight:** We're building a reusable tool that OTHER agents can call, not an agent that calls other tools. This is why we don't need MCP server dependencies.
