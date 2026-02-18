from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.engine.ecs.components.renderable import Renderable
from src.engine.ecs.components.sprite import Sprite
from src.engine.ecs.components.transform import Transform


@dataclass(slots=True)
class Prefab:
    transform: Optional[Transform] = None
    renderable: Optional[Renderable] = None
    sprite: Optional[Sprite] = None


class Scene:
    def __init__(self, registry):
        self.registry = registry
        self.entities: list[int] = []

    def spawn_prefab(self, prefab: Prefab) -> int:
        """Создаёт entity из Prefab."""
        eid = self.registry.create_entity()
        self.entities.append(eid)

        if prefab.transform is not None:
            self.registry.add(eid, prefab.transform)

        if prefab.renderable is not None:
            self.registry.add(eid, prefab.renderable)

        if prefab.sprite is not None:
            self.registry.add(eid, prefab.sprite)

        return eid

    def spawn_prefabs(self, prefabs: list[Prefab]) -> list[int]:
        spawned: list[int] = []
        for prefab in prefabs:
            spawned.append(self.spawn_prefab(prefab))
        return spawned
