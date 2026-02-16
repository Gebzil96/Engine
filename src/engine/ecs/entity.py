from __future__ import annotations

EntityId = int


class EntityFactory:
    def __init__(self) -> None:
        self._next_id: int = 1  # 🔧 МОЖНО МЕНЯТЬ: стартовый ID (0 зарезервирован)

    def create(self) -> EntityId:
        eid = self._next_id
        self._next_id += 1
        return eid
