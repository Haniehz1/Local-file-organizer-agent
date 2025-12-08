import re
from typing import List
from file_organizer.models.file_metadata import FileMetadata, FileClassification


class FileClassifier:
    """Classifies files into categories using rule-based logic"""

    # File extension mappings
    CATEGORIES = {
        "Screenshots": {
            "patterns": [r"screenshot", r"screen shot", r"scr\d{8}", r"image\d{8}"],
            "extensions": [".png", ".jpg", ".jpeg"],
        },
        "Images": {
            "extensions": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", ".heic", ".svg"],
            "patterns": []
        },
        "Documents": {
            "extensions": [".doc", ".docx", ".txt", ".rtf", ".odt", ".pages"],
            "patterns": []
        },
        "PDFs": {
            "extensions": [".pdf"],
            "patterns": []
        },
        "Spreadsheets": {
            "extensions": [".xls", ".xlsx", ".csv", ".numbers"],
            "patterns": []
        },
        "Presentations": {
            "extensions": [".ppt", ".pptx", ".key"],
            "patterns": []
        },
        "Archives": {
            "extensions": [".zip", ".tar", ".gz", ".rar", ".7z", ".bz2"],
            "patterns": []
        },
        "Installers": {
            "extensions": [".dmg", ".pkg", ".exe", ".msi", ".deb", ".rpm", ".app"],
            "patterns": [r"setup", r"install", r"installer"]
        },
        "Code": {
            "extensions": [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h",
                          ".rb", ".go", ".rs", ".swift", ".kt", ".cs", ".php", ".html", ".css"],
            "patterns": []
        },
        "Videos": {
            "extensions": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"],
            "patterns": []
        },
        "Audio": {
            "extensions": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
            "patterns": []
        },
    }

    def classify_file(self, file_meta: FileMetadata) -> FileClassification:
        """Classify a single file"""
        filename_lower = file_meta.filename.lower()

        # Check screenshots first (higher priority)
        screenshot_patterns = self.CATEGORIES["Screenshots"]["patterns"]
        screenshot_exts = self.CATEGORIES["Screenshots"]["extensions"]

        if any(re.search(pattern, filename_lower) for pattern in screenshot_patterns):
            if file_meta.extension in screenshot_exts:
                return FileClassification(
                    file_path=file_meta.path,
                    category="Screenshots",
                    confidence=0.95,
                    reason="Filename matches screenshot pattern"
                )

        # Check other categories
        for category, rules in self.CATEGORIES.items():
            if category == "Screenshots":
                continue  # Already checked

            # Check extension match
            if file_meta.extension in rules["extensions"]:
                confidence = 0.9

                # Boost confidence if pattern also matches
                if rules["patterns"]:
                    if any(re.search(pattern, filename_lower) for pattern in rules["patterns"]):
                        confidence = 0.95

                return FileClassification(
                    file_path=file_meta.path,
                    category=category,
                    confidence=confidence,
                    reason=f"Extension {file_meta.extension} matches {category}"
                )

            # Check pattern match (for files without extension match)
            if rules["patterns"]:
                if any(re.search(pattern, filename_lower) for pattern in rules["patterns"]):
                    return FileClassification(
                        file_path=file_meta.path,
                        category=category,
                        confidence=0.7,
                        reason=f"Filename pattern matches {category}"
                    )

        # Default to Unknown
        return FileClassification(
            file_path=file_meta.path,
            category="Unknown",
            confidence=0.5,
            reason="Could not determine category"
        )

    def classify_files(self, files: List[FileMetadata]) -> List[FileClassification]:
        """Classify multiple files"""
        return [self.classify_file(f) for f in files]

    def group_by_category(self, classifications: List[FileClassification]) -> dict[str, List[FileClassification]]:
        """Group classifications by category"""
        grouped = {}
        for classification in classifications:
            if classification.category not in grouped:
                grouped[classification.category] = []
            grouped[classification.category].append(classification)
        return grouped
