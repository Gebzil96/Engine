from __future__ import annotations

from pathlib import Path


class ProjectService:
    def validate_project_dir(self, path: str) -> tuple[bool, str]:
        p = Path(path)
        if not p.exists():
            return False, "Папка не существует"
        if not p.is_dir():
            return False, "Это не папка"
        return True, ""
