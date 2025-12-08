"""MCP Server for File Organizer using mcp-agent SDK"""
import json
import time
from pathlib import Path
from typing import Optional, List
from mcp_agent.app import MCPApp
from mcp_agent.core.context import Context
from file_organizer.agents.scanner import FileScanner
from file_organizer.agents.classifier import FileClassifier
from file_organizer.agents.organizer import FileOrganizer
from file_organizer.agents.reporter import Reporter
from file_organizer.agents.backup import BackupManager


# Initialize the MCP app
app = MCPApp(
    name="file-organizer",
    description="Intelligent file organization system that scans, classifies, and organizes files"
)

# Global state to store scan results
_scan_state = {
    "files": [],
    "classifications": [],
    "duplicates": {},
    "plan": None,
    "result": None,
    "summary": None
}


def load_config() -> dict:
    """Load configuration from config.json"""
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    return {
        "scan_paths": ["~/Downloads"],
        "organization_rules": {},
        "delete_duplicates": False
    }


@app.async_tool()
async def scan_files(paths: Optional[List[str]] = None, app_ctx: Context | None = None) -> str:
    """
    Scan directories and collect file metadata.

    Args:
        paths: List of paths to scan. If not provided, uses config defaults.

    Returns:
        JSON string with scan results
    """
    config = load_config()
    scan_paths = paths if paths else config.get("scan_paths", ["~/Downloads"])

    print(f"Scanning paths: {scan_paths}")
    print("Mode: Only scanning top-level files (skipping all subdirectories)")
    scanner = FileScanner(compute_hashes=True, only_top_level=True)
    files = scanner.scan_paths(scan_paths)

    # Find duplicates
    duplicates = scanner.find_duplicates()

    # Store in global state
    _scan_state["files"] = files
    _scan_state["duplicates"] = duplicates

    result = {
        "total_files": len(files),
        "duplicates_found": sum(len(dups) - 1 for dups in duplicates.values()),
        "files": [
            {
                "path": f.path,
                "filename": f.filename,
                "size_mb": f.size_mb,
                "extension": f.extension
            } for f in files[:20]  # Return first 20 for preview
        ],
        "message": f"Scanned {len(files)} files from {len(scan_paths)} paths"
    }

    return json.dumps(result, indent=2)


@app.async_tool()
async def classify_files(app_ctx: Context | None = None) -> str:
    """
    Classify scanned files into categories.

    Returns:
        JSON string with classification results
    """
    if not _scan_state["files"]:
        return json.dumps({"error": "No files scanned. Run scan_files first."})

    classifier = FileClassifier()
    classifications = classifier.classify_files(_scan_state["files"])

    # Store classifications
    _scan_state["classifications"] = classifications

    # Group by category
    grouped = classifier.group_by_category(classifications)

    result = {
        "total_classified": len(classifications),
        "categories": {
            category: len(files) for category, files in grouped.items()
        },
        "samples": {
            category: [f.file_path.split('/')[-1] for f in files[:3]]
            for category, files in grouped.items()
        }
    }

    return json.dumps(result, indent=2)


@app.async_tool()
async def propose_organization(app_ctx: Context | None = None) -> str:
    """
    Generate an organization plan based on classifications.

    Returns:
        Markdown formatted organization plan
    """
    if not _scan_state["classifications"]:
        return "Error: No classifications found. Run classify_files first."

    config = load_config()
    organizer = FileOrganizer(
        organization_rules=config.get("organization_rules", {}),
        delete_duplicates=config.get("delete_duplicates", False)
    )

    plan = organizer.create_plan(
        classifications=_scan_state["classifications"],
        files_metadata=_scan_state["files"],
        duplicates=_scan_state["duplicates"]
    )

    # Store plan
    _scan_state["plan"] = plan

    # Format as markdown
    reporter = Reporter()
    preview = reporter.format_plan_preview(plan)

    return preview


@app.async_tool()
async def execute_plan(dry_run: bool = True, app_ctx: Context | None = None) -> str:
    """
    Execute the organization plan.

    Args:
        dry_run: If True, simulate execution without moving files

    Returns:
        JSON string with execution results
    """
    if not _scan_state["plan"]:
        return json.dumps({"error": "No plan found. Run propose_organization first."})

    config = load_config()
    organizer = FileOrganizer(
        organization_rules=config.get("organization_rules", {}),
        delete_duplicates=config.get("delete_duplicates", False)
    )

    start_time = time.time()
    result = organizer.execute_plan(_scan_state["plan"], dry_run=dry_run)
    execution_time = time.time() - start_time

    # Store result
    _scan_state["result"] = result

    # Generate summary
    reporter = Reporter()
    summary = reporter.generate_summary(
        files=_scan_state["files"],
        classifications=_scan_state["classifications"],
        plan=_scan_state["plan"],
        result=result,
        execution_time=execution_time
    )
    _scan_state["summary"] = summary

    response = {
        "success": result.success,
        "actions_completed": result.actions_completed,
        "actions_failed": result.actions_failed,
        "space_freed_mb": result.space_freed_mb,
        "errors": result.errors,
        "mode": "DRY RUN" if dry_run else "EXECUTED"
    }

    # Add backup manifest path if actual execution occurred
    if not dry_run and organizer.last_manifest_path:
        response["backup_manifest"] = organizer.last_manifest_path

    return json.dumps(response, indent=2)


@app.async_tool()
async def get_summary(app_ctx: Context | None = None) -> str:
    """
    Get markdown summary of the last organization run.

    Returns:
        Markdown formatted summary
    """
    if not _scan_state["summary"]:
        return "No summary available. Complete a full workflow first."

    reporter = Reporter()
    return reporter.format_markdown(_scan_state["summary"])


@app.async_tool()
async def reset_state(app_ctx: Context | None = None) -> str:
    """
    Reset all stored state.

    Returns:
        Confirmation message
    """
    _scan_state["files"] = []
    _scan_state["classifications"] = []
    _scan_state["duplicates"] = {}
    _scan_state["plan"] = None
    _scan_state["result"] = None
    _scan_state["summary"] = None

    return "State reset successfully."


@app.async_tool()
async def list_backups(app_ctx: Context | None = None) -> str:
    """
    List all available backup manifests.

    Returns:
        JSON string with list of available backups
    """
    backup_manager = BackupManager()
    backups = backup_manager.list_backups()

    if not backups:
        return json.dumps({"message": "No backup manifests found"})

    result = {
        "total_backups": len(backups),
        "backups": backups
    }

    return json.dumps(result, indent=2)


@app.async_tool()
async def restore_from_backup(manifest_path: Optional[str] = None, dry_run: bool = True, app_ctx: Context | None = None) -> str:
    """
    Restore files from a backup manifest.

    Args:
        manifest_path: Path to the manifest file. If not provided, uses the most recent backup.
        dry_run: If True, show what would be restored without actually moving files

    Returns:
        JSON string with restoration results
    """
    backup_manager = BackupManager()

    # If no path provided, use most recent backup
    if not manifest_path:
        manifest_path = backup_manager.get_latest_backup()
        if not manifest_path:
            return json.dumps({"error": "No backup manifests found"})

    result = backup_manager.restore_from_manifest(manifest_path, dry_run=dry_run)

    return json.dumps(result, indent=2)


async def run_full_workflow(scan_paths: Optional[List[str]] = None, dry_run: bool = True) -> str:
    """
    Run the complete workflow: scan -> classify -> plan -> execute -> summary

    Args:
        scan_paths: Paths to scan
        dry_run: Whether to do a dry run

    Returns:
        Final summary
    """
    # Step 1: Scan
    print("Step 1: Scanning files...")
    scan_result = await scan_files(scan_paths)
    print(scan_result)

    # Step 2: Classify
    print("\nStep 2: Classifying files...")
    classify_result = await classify_files()
    print(classify_result)

    # Step 3: Propose
    print("\nStep 3: Creating organization plan...")
    plan_preview = await propose_organization()
    print(plan_preview)

    # Step 4: Execute
    print(f"\nStep 4: Executing plan (dry_run={dry_run})...")
    exec_result = await execute_plan(dry_run=dry_run)
    print(exec_result)

    # Step 5: Summary
    print("\nStep 5: Generating summary...")
    summary = await get_summary()
    print(summary)

    return summary


if __name__ == "__main__":
    import asyncio

    async def main():
        async with app.run():
            # Run full workflow as a demo
            await run_full_workflow(dry_run=True)

    asyncio.run(main())
