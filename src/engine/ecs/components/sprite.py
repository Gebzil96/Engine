from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass(slots=True)
class Sprite:
    """
    Компонент спрайта.
    Хранит путь к текстуре (asset), а не сам объект ModernGL.
    """
    texture_path: Path
