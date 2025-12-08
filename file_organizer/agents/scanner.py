import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List
from file_organizer.models.file_metadata import FileMetadata


class FileScanner:
    """Scans directories and collects file metadata"""

    def __init__(self, compute_hashes: bool = True, only_top_level: bool = False):
        self.compute_hashes = compute_hashes
        self.only_top_level = only_top_level  # If True, only scan files in top level, skip subdirectories
        self.scanned_files: List[FileMetadata] = []

    def scan_paths(self, paths: List[str]) -> List[FileMetadata]:
        """Scan multiple paths and return file metadata"""
        all_files = []

        for path_str in paths:
            # Expand ~ and resolve path
            path = Path(path_str).expanduser().resolve()

            if not path.exists():
                print(f"Warning: Path does not exist: {path}")
                continue

            if path.is_file():
                metadata = self._get_file_metadata(path)
                if metadata:
                    all_files.append(metadata)
            elif path.is_dir():
                if self.only_top_level:
                    # Only scan files directly in this directory, don't recurse
                    all_files.extend(self._scan_top_level_only(path))
                else:
                    all_files.extend(self._scan_directory(path))

        self.scanned_files = all_files
        return all_files

    def _scan_top_level_only(self, directory: Path) -> List[FileMetadata]:
        """Scan only files directly in the directory (no recursion into subdirectories)"""
        files = []

        try:
            for item in directory.iterdir():
                # Skip hidden files
                if item.name.startswith('.'):
                    continue

                # Only process files, skip all directories
                if item.is_file():
                    metadata = self._get_file_metadata(item)
                    if metadata:
                        files.append(metadata)
                # Directories are completely ignored
        except PermissionError:
            print(f"Permission denied: {directory}")
        except Exception as e:
            print(f"Error scanning {directory}: {e}")

        return files

    def _scan_directory(self, directory: Path) -> List[FileMetadata]:
        """Recursively scan a directory"""
        files = []

        # Folders to always skip
        SKIP_FOLDERS = {
            'venv', 'env', '.venv', '.env',  # Virtual environments
            'node_modules', '.git', '.svn',  # Package managers & version control
            '__pycache__', '.pytest_cache',  # Python caches
            'Library', 'Applications',        # System folders (macOS)
            '.Trash', 'System Volume Information'  # System folders
        }

        try:
            for item in directory.iterdir():
                # Skip hidden files and system folders
                if item.name.startswith('.'):
                    continue

                # Skip known folders that should never be organized
                if item.name in SKIP_FOLDERS:
                    continue

                if item.is_file():
                    metadata = self._get_file_metadata(item)
                    if metadata:
                        files.append(metadata)
                elif item.is_dir():
                    # Recursively scan subdirectories
                    files.extend(self._scan_directory(item))
        except PermissionError:
            print(f"Permission denied: {directory}")
        except Exception as e:
            print(f"Error scanning {directory}: {e}")

        return files

    def _get_file_metadata(self, file_path: Path) -> FileMetadata | None:
        """Extract metadata from a single file"""
        try:
            stat = file_path.stat()

            metadata = FileMetadata(
                path=str(file_path),
                filename=file_path.name,
                extension=file_path.suffix.lower(),
                size_bytes=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_ctime),
                modified_at=datetime.fromtimestamp(stat.st_mtime),
                hash=self._compute_hash(file_path) if self.compute_hashes else None
            )

            return metadata

        except Exception as e:
            print(f"Error reading metadata for {file_path}: {e}")
            return None

    def _compute_hash(self, file_path: Path) -> str | None:
        """Compute SHA256 hash of file"""
        try:
            # Skip large files (> 100MB)
            if file_path.stat().st_size > 100 * 1024 * 1024:
                return None

            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error computing hash for {file_path}: {e}")
            return None

    def find_duplicates(self) -> dict[str, List[FileMetadata]]:
        """Find duplicate files based on hash"""
        hash_map = {}

        for file_meta in self.scanned_files:
            if file_meta.hash:
                if file_meta.hash not in hash_map:
                    hash_map[file_meta.hash] = []
                hash_map[file_meta.hash].append(file_meta)

        # Return only hashes with multiple files
        duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
        return duplicates
