from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from pathlib import Path


class FileMetadata(BaseModel):
    """Metadata for a single file"""
    path: str
    filename: str
    extension: str
    size_bytes: int
    created_at: datetime
    modified_at: datetime
    hash: Optional[str] = None
    mime_type: Optional[str] = None

    @property
    def size_mb(self) -> float:
        return round(self.size_bytes / (1024 * 1024), 2)


class FileClassification(BaseModel):
    """Classification result for a file"""
    file_path: str
    category: str
    confidence: float = 1.0
    reason: Optional[str] = None
    suggested_name: Optional[str] = None


class OrganizationAction(BaseModel):
    """Single file organization action"""
    source_path: str
    action: str  # "move", "delete", "rename", "skip"
    destination_path: Optional[str] = None
    reason: str
    category: str


class OrganizationPlan(BaseModel):
    """Complete organization plan"""
    actions: list[OrganizationAction] = Field(default_factory=list)
    total_files: int = 0
    files_to_move: int = 0
    files_to_delete: int = 0
    estimated_space_freed_mb: float = 0.0

    def add_action(self, action: OrganizationAction):
        self.actions.append(action)
        if action.action == "move":
            self.files_to_move += 1
        elif action.action == "delete":
            self.files_to_delete += 1


class ExecutionResult(BaseModel):
    """Result of executing organization plan"""
    success: bool
    actions_completed: int = 0
    actions_failed: int = 0
    errors: list[str] = Field(default_factory=list)
    space_freed_mb: float = 0.0


class ScanSummary(BaseModel):
    """Summary of scan and organization"""
    total_files_scanned: int = 0
    files_moved: int = 0
    files_deleted: int = 0
    duplicates_found: int = 0
    space_freed_mb: float = 0.0
    categories: dict[str, int] = Field(default_factory=dict)
    execution_time_seconds: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
