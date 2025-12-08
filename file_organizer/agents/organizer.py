import os
import shutil
from pathlib import Path
from typing import List, Dict
from file_organizer.models.file_metadata import (
    FileMetadata,
    FileClassification,
    OrganizationPlan,
    OrganizationAction,
    ExecutionResult
)
from file_organizer.agents.backup import BackupManager


class FileOrganizer:
    """Creates and executes organization plans"""

    def __init__(self, organization_rules: Dict[str, str], delete_duplicates: bool = False):
        self.organization_rules = organization_rules
        self.delete_duplicates = delete_duplicates
        self.backup_manager = BackupManager()
        self.last_manifest_path = None

    def create_plan(
        self,
        classifications: List[FileClassification],
        files_metadata: List[FileMetadata],
        duplicates: Dict[str, List[FileMetadata]] = None
    ) -> OrganizationPlan:
        """Create an organization plan based on classifications"""
        plan = OrganizationPlan(total_files=len(files_metadata))

        # Create lookup for metadata
        metadata_lookup = {fm.path: fm for fm in files_metadata}

        # Process regular files
        for classification in classifications:
            file_meta = metadata_lookup.get(classification.file_path)
            if not file_meta:
                continue

            # Skip unknown files
            if classification.category == "Unknown":
                plan.add_action(OrganizationAction(
                    source_path=file_meta.path,
                    action="skip",
                    reason="Unknown file type - requires manual review",
                    category=classification.category
                ))
                continue

            # Get destination folder from rules
            dest_base = self.organization_rules.get(classification.category)
            if not dest_base:
                plan.add_action(OrganizationAction(
                    source_path=file_meta.path,
                    action="skip",
                    reason=f"No organization rule for {classification.category}",
                    category=classification.category
                ))
                continue

            # Expand home directory
            dest_base = Path(dest_base).expanduser()

            # Create destination path
            dest_path = dest_base / file_meta.filename

            plan.add_action(OrganizationAction(
                source_path=file_meta.path,
                action="move",
                destination_path=str(dest_path),
                reason=f"Classified as {classification.category}",
                category=classification.category
            ))

        # Handle duplicates
        if duplicates and self.delete_duplicates:
            for hash_val, dup_files in duplicates.items():
                # Keep first file, mark others for deletion
                for dup_file in dup_files[1:]:
                    plan.add_action(OrganizationAction(
                        source_path=dup_file.path,
                        action="delete",
                        reason="Duplicate file",
                        category="Duplicates"
                    ))
                    plan.estimated_space_freed_mb += dup_file.size_mb

        return plan

    def execute_plan(self, plan: OrganizationPlan, dry_run: bool = False) -> ExecutionResult:
        """Execute the organization plan"""
        result = ExecutionResult(success=True)

        # Create backup manifest before executing (unless dry run)
        if not dry_run:
            actions_list = [
                {
                    "action": action.action,
                    "source_path": action.source_path,
                    "destination_path": action.destination_path,
                    "category": action.category
                }
                for action in plan.actions
            ]
            self.last_manifest_path = self.backup_manager.create_backup_manifest(actions_list)

        for action in plan.actions:
            try:
                if action.action == "skip":
                    continue

                if dry_run:
                    print(f"[DRY RUN] Would {action.action}: {action.source_path}")
                    result.actions_completed += 1
                    continue

                if action.action == "move":
                    self._move_file(action.source_path, action.destination_path)
                    result.actions_completed += 1

                elif action.action == "delete":
                    size_mb = Path(action.source_path).stat().st_size / (1024 * 1024)
                    self._delete_file(action.source_path)
                    result.space_freed_mb += size_mb
                    result.actions_completed += 1

            except Exception as e:
                result.actions_failed += 1
                result.errors.append(f"Failed to {action.action} {action.source_path}: {str(e)}")
                result.success = False

        return result

    def _move_file(self, source: str, destination: str):
        """Move a file to destination, creating directories if needed"""
        source_path = Path(source)
        dest_path = Path(destination)

        # Create destination directory
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle name collision
        if dest_path.exists():
            dest_path = self._get_unique_path(dest_path)

        # Move file
        shutil.move(str(source_path), str(dest_path))
        print(f"Moved: {source_path.name} -> {dest_path}")

    def _delete_file(self, file_path: str):
        """Delete a file"""
        path = Path(file_path)
        path.unlink()
        print(f"Deleted: {path.name}")

    def _get_unique_path(self, path: Path) -> Path:
        """Generate a unique file path if file exists"""
        counter = 1
        stem = path.stem
        suffix = path.suffix

        while path.exists():
            path = path.parent / f"{stem}_{counter}{suffix}"
            counter += 1

        return path
