from __future__ import annotations

from src.engine.launcher.app import LauncherApp


def run_launcher_app(initial_project: str = "") -> None:
    app = LauncherApp(initial_project=initial_project)
    app.run()
