from datetime import datetime
from typing import List, Dict
from file_organizer.models.file_metadata import (
    FileMetadata,
    FileClassification,
    OrganizationPlan,
    ExecutionResult,
    ScanSummary
)


class Reporter:
    """Generates summary reports"""

    def generate_summary(
        self,
        files: List[FileMetadata],
        classifications: List[FileClassification],
        plan: OrganizationPlan,
        result: ExecutionResult,
        execution_time: float
    ) -> ScanSummary:
        """Generate a summary of the organization process"""

        # Count categories
        category_counts = {}
        for classification in classifications:
            cat = classification.category
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Count duplicates
        duplicates_count = sum(1 for action in plan.actions if action.category == "Duplicates")

        summary = ScanSummary(
            total_files_scanned=len(files),
            files_moved=plan.files_to_move,
            files_deleted=result.actions_completed if result else 0,
            duplicates_found=duplicates_count,
            space_freed_mb=result.space_freed_mb if result else 0.0,
            categories=category_counts,
            execution_time_seconds=execution_time,
            timestamp=datetime.now()
        )

        return summary

    def format_markdown(self, summary: ScanSummary) -> str:
        """Format summary as markdown"""

        chaos_before = min(10, summary.total_files_scanned / 50)
        chaos_after = max(0, chaos_before - (summary.files_moved / 20))

        report = f"""# File Organizer - Cleanup Summary

**Timestamp:** {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

---

## Statistics

- **Total files scanned:** {summary.total_files_scanned}
- **Files moved:** {summary.files_moved}
- **Duplicates removed:** {summary.duplicates_found}
- **Disk space recovered:** {summary.space_freed_mb:.2f} MB
- **Execution time:** {summary.execution_time_seconds:.2f} seconds

---

## File Categories

"""
        for category, count in sorted(summary.categories.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{category}:** {count} files\n"

        report += f"""
---

## Chaos Index

- **Before:** {chaos_before:.1f} / 10
- **After:** {chaos_after:.1f} / 10
- **Improvement:** {chaos_before - chaos_after:.1f} points

---

✨ *Organization complete!*
"""
        return report

    def format_plan_preview(self, plan: OrganizationPlan) -> str:
        """Format plan as readable preview"""
        preview = f"""# Organization Plan Preview

**Total files:** {plan.total_files}
**Files to move:** {plan.files_to_move}
**Files to delete:** {plan.files_to_delete}
**Estimated space freed:** {plan.estimated_space_freed_mb:.2f} MB

---

## Actions by Category

"""
        # Group actions by category
        by_category = {}
        for action in plan.actions:
            if action.category not in by_category:
                by_category[action.category] = []
            by_category[action.category].append(action)

        for category, actions in sorted(by_category.items()):
            preview += f"\n### {category} ({len(actions)} files)\n\n"
            for action in actions[:5]:  # Show first 5
                source_name = action.source_path.split('/')[-1]
                if action.action == "move":
                    dest_name = action.destination_path.split('/')[-2:] if action.destination_path else "?"
                    preview += f"- Move `{source_name}` → `{'/'.join(dest_name)}`\n"
                elif action.action == "delete":
                    preview += f"- Delete `{source_name}`\n"
                elif action.action == "skip":
                    preview += f"- Skip `{source_name}` - {action.reason}\n"

            if len(actions) > 5:
                preview += f"\n*... and {len(actions) - 5} more*\n"

        return preview
