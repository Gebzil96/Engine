from __future__ import annotations

from typing import Any, Dict, Type, TypeVar

from .entity import EntityFactory, EntityId

T = TypeVar("T")


class Registry:
    def __init__(self) -> None:
        self._entities = EntityFactory()
        # components[type(component)][entity_id] = component_instance
        self._components: Dict[Type[Any], Dict[EntityId, Any]] = {}

    def create_entity(self) -> EntityId:
        return self._entities.create()

    def add(self, entity: EntityId, component: Any) -> None:
        ctype = type(component)
        bucket = self._components.setdefault(ctype, {})
        bucket[entity] = component

    def has(self, entity: EntityId, component_type: Type[Any]) -> bool:
        bucket = self._components.get(component_type)
        if bucket is None:
            return False
        return entity in bucket

    def get(self, entity: EntityId, component_type: Type[T]) -> T:
        bucket = self._components.get(component_type)
        if bucket is None or entity not in bucket:
            raise KeyError(f"Entity {entity} has no component {component_type.__name__}")
        return bucket[entity]

    def remove(self, entity: EntityId, component_type: Type[Any]) -> None:
        bucket = self._components.get(component_type)
        if not bucket:
            return
        bucket.pop(entity, None)
        if not bucket:
            self._components.pop(component_type, None)
    
    def get_all(self, component_type: Type[T]) -> Dict[EntityId, T]:
        bucket = self._components.get(component_type)
        if bucket is None:
            return {}
        return bucket
    
    def query(self, *component_types: Type[Any]) -> list[EntityId]:
        """
        Вернуть список entity_id, у которых есть ВСЕ указанные компоненты.
        Пример: registry.query(Transform, Renderable)
        """
        if not component_types:
            return []

        # Берём бакеты компонентов
        buckets: list[Dict[EntityId, Any]] = []
        for ct in component_types:
            bucket = self._components.get(ct)
            if not bucket:
                return []
            buckets.append(bucket)

        # Идём по самому маленькому бакету (быстрее)
        buckets.sort(key=len)
        base = buckets[0]
        others = buckets[1:]

        result: list[EntityId] = []
        for eid in base.keys():
            ok = True
            for b in others:
                if eid not in b:
                    ok = False
                    break
            if ok:
                result.append(eid)

        return result
    
