from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional

from src.engine.scene import Prefab


@dataclass(slots=True)
class SceneDefinition:
    build: Callable[[], list[Prefab]]
    update: Optional[Callable[[object, dict], None]] = None
    cleanup: Optional[Callable[[object], None]] = None


def get_scene_definition(scene_id: str) -> SceneDefinition:
    """
    Минимальный loader: по строковому id возвращает SceneDefinition.
    """
    if scene_id == "example_scene":
        from src.engine.scenes.example_scene import build_example_scene

        return SceneDefinition(build=build_example_scene)

    raise ValueError(f"Unknown scene_id: {scene_id!r}")
