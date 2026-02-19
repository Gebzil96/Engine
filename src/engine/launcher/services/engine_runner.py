from __future__ import annotations

import subprocess
import sys
from pathlib import Path


class EngineRunner:
    def launch_engine(self, project_path: str) -> None:
        # Запускаем ВТОРОЙ процесс через тот же entrypoint run_engine.pyw
        project_root = Path(__file__).resolve().parents[3]
        # .../src/engine/launcher/services -> root
        entry = project_root / "run_engine.pyw"

        # pythonw.exe обычно уже в sys.executable, если ты запускаешь .pyw
        cmd = [sys.executable, str(entry), "--engine", "--project", project_path]
        subprocess.Popen(cmd, cwd=str(project_root))
