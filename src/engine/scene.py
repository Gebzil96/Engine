from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Prefab:
    components: tuple[object, ...] = ()
    role: str | None = None  # метка сущности внутри сцены (scene-aware spawn)

class Scene:
    def __init__(self, registry):
        self.registry = registry
        self.entities: list[int] = []
        self.role_entities: dict[str, int] = {}
    
    def clear(self) -> None:
        # Удаляем сущности сцены из ECS, чтобы компоненты не залипали
        for eid in self.entities:
            self.registry.destroy_entity(eid)

        self.entities.clear()
        self.role_entities.clear()

    def spawn_prefab(self, prefab: Prefab) -> int:
        """Создаёт entity из Prefab (набор компонентов)."""
        eid = self.registry.create_entity()
        self.entities.append(eid)

        for component in prefab.components:
            self.registry.add(eid, component)

        if prefab.role is not None:
            if prefab.role in self.role_entities:
                raise RuntimeError(f"Duplicate prefab role: {prefab.role!r}")
            self.role_entities[prefab.role] = eid

        return eid

    def spawn_prefabs(self, prefabs: list[Prefab]) -> list[int]:
        spawned: list[int] = []
        for prefab in prefabs:
            spawned.append(self.spawn_prefab(prefab))
        return spawned
    
    def get_entity_by_role(self, role: str) -> int | None:
        return self.role_entities.get(role)
