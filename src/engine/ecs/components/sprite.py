from __future__ import annotations

from dataclasses import dataclass

# Path больше не нужен: храним путь строкой


@dataclass(slots=True)
class Sprite:
    """
    Компонент спрайта.
    Хранит путь к текстуре (asset), а не сам объект ModernGL.
    """

    texture_path: str
