from __future__ import annotations

import sys
from pathlib import Path

# Добавляем <repo_root>/src в sys.path, чтобы работали импорты вида `engine...`
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
