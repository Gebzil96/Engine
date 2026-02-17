from __future__ import annotations
from dataclasses import dataclass
import moderngl


@dataclass(slots=True)
class Sprite:
    """
    Компонент спрайта.
    Хранит ссылку на текстуру ModernGL.
    """
    texture: moderngl.Texture
