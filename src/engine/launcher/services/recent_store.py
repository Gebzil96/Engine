from __future__ import annotations

import json
import os
from pathlib import Path

from src.engine.launcher.domain.models import ProjectRef


class RecentProjectsStore:
    def __init__(self) -> None:
        self._path = self._default_store_path()

    def load(self) -> list[ProjectRef]:
        if not self._path.exists():
            return []
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            items = data.get("recent", [])
            result: list[ProjectRef] = []
            for p in items:
                if isinstance(p, str) and p.strip():
                    result.append(ProjectRef(path=p))
            return result
        except Exception:
            # если файл битый — не падаем, просто считаем что recent пустой
            return []

    def save(self, items: list[ProjectRef]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {"recent": [i.path for i in items]}
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def push_front(self, project_path: str, limit: int = 20) -> None:
        project_path = project_path.strip()
        if not project_path:
            return

        items = self.load()
        # убрать дубликаты (case-insensitive для Windows путей)
        normalized = project_path.lower()
        items = [i for i in items if i.path.lower() != normalized]
        items.insert(0, ProjectRef(path=project_path))
        self.save(items[:limit])

    @staticmethod
    def _default_store_path() -> Path:
        # Windows: %APPDATA%
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "Engine" / "recent_projects.json"
        # fallback
        return Path.home() / ".engine" / "recent_projects.json"
