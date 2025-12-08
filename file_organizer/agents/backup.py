import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict


class BackupManager:
    """Manages backup and restore operations for file organization"""

    def __init__(self, backup_dir: str = "~/.file_organizer_backups"):
        self.backup_dir = Path(backup_dir).expanduser()
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup_manifest(self, actions: List[Dict]) -> str:
        """
        Create a backup manifest file that records all file movements

        Args:
            actions: List of actions with source and destination paths

        Returns:
            Path to the manifest file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        manifest_path = self.backup_dir / f"manifest_{timestamp}.json"

        manifest = {
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "actions": []
        }

        for action in actions:
            if action.get("action") == "move":
                manifest["actions"].append({
                    "action": "move",
                    "source": action["source_path"],
                    "destination": action["destination_path"],
                    "category": action.get("category", "Unknown")
                })
            elif action.get("action") == "delete":
                manifest["actions"].append({
                    "action": "delete",
                    "source": action["source_path"],
                    "category": action.get("category", "Unknown")
                })

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"✅ Backup manifest created: {manifest_path}")
        return str(manifest_path)

    def restore_from_manifest(self, manifest_path: str, dry_run: bool = True) -> Dict:
        """
        Restore files from a backup manifest

        Args:
            manifest_path: Path to the manifest file
            dry_run: If True, only show what would be restored

        Returns:
            Dict with restoration results
        """
        manifest_path = Path(manifest_path)

        if not manifest_path.exists():
            return {"error": f"Manifest not found: {manifest_path}"}

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        results = {
            "success": True,
            "restored": 0,
            "failed": 0,
            "errors": []
        }

        print(f"\n{'=' * 60}")
        print(f"{'DRY RUN - ' if dry_run else ''}RESTORING from manifest: {manifest['datetime']}")
        print(f"{'=' * 60}\n")

        # Reverse the actions (undo in reverse order)
        for action in reversed(manifest["actions"]):
            if action["action"] == "move":
                source = Path(action["destination"])  # Current location
                dest = Path(action["source"])  # Original location

                if not source.exists():
                    error = f"File not found (may have been moved/deleted): {source}"
                    results["errors"].append(error)
                    results["failed"] += 1
                    print(f"❌ {error}")
                    continue

                if dry_run:
                    print(f"[DRY RUN] Would restore: {source.name}")
                    print(f"           From: {source}")
                    print(f"           To:   {dest}\n")
                    results["restored"] += 1
                else:
                    try:
                        # Create parent directory if needed
                        dest.parent.mkdir(parents=True, exist_ok=True)

                        # Move file back
                        shutil.move(str(source), str(dest))
                        print(f"✅ Restored: {dest.name}")
                        results["restored"] += 1
                    except Exception as e:
                        error = f"Failed to restore {source}: {str(e)}"
                        results["errors"].append(error)
                        results["failed"] += 1
                        results["success"] = False
                        print(f"❌ {error}")

        print(f"\n{'=' * 60}")
        print(f"Restoration {'Preview' if dry_run else 'Complete'}")
        print(f"Files to restore: {results['restored']}")
        print(f"Failed: {results['failed']}")
        print(f"{'=' * 60}\n")

        if not dry_run and results["success"]:
            print(f"✅ All files restored to their original locations!")

        return results

    def list_backups(self) -> List[Dict]:
        """List all available backup manifests"""
        manifests = []

        for manifest_file in sorted(self.backup_dir.glob("manifest_*.json"), reverse=True):
            try:
                with open(manifest_file, "r") as f:
                    data = json.load(f)
                    manifests.append({
                        "path": str(manifest_file),
                        "timestamp": data["timestamp"],
                        "datetime": data["datetime"],
                        "num_actions": len(data["actions"])
                    })
            except Exception as e:
                print(f"Warning: Could not read {manifest_file}: {e}")

        return manifests

    def get_latest_backup(self) -> str | None:
        """Get the path to the most recent backup manifest"""
        backups = self.list_backups()
        if backups:
            return backups[0]["path"]
        return None
