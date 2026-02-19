from __future__ import annotations

from src.engine.launcher.services.engine_runner import EngineRunner
from src.engine.launcher.services.project_service import ProjectService
from src.engine.launcher.services.recent_store import RecentProjectsStore
from src.engine.launcher.ui.tk.main_window import LauncherWindow


class LauncherApp:
    def __init__(self, initial_project: str = "") -> None:
        self._recent_store = RecentProjectsStore()
        self._project_service = ProjectService()
        self._engine_runner = EngineRunner()
        self._initial_project = initial_project

    def run(self) -> None:
        window = LauncherWindow(
            recent_store=self._recent_store,
            project_service=self._project_service,
            engine_runner=self._engine_runner,
            initial_project=self._initial_project,
        )
        window.run()
