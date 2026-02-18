from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Prefab:
    components: tuple[object, ...] = ()


class Scene:
    def __init__(self, registry):
        self.registry = registry
        self.entities: list[int] = []

    def spawn_prefab(self, prefab: Prefab) -> int:
        """Создаёт entity из Prefab (набор компонентов)."""
        eid = self.registry.create_entity()
        self.entities.append(eid)

        for component in prefab.components:
            self.registry.add(eid, component)

        return eid

    def spawn_prefabs(self, prefabs: list[Prefab]) -> list[int]:
        spawned: list[int] = []
        for prefab in prefabs:
            spawned.append(self.spawn_prefab(prefab))
        return spawned
