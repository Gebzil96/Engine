from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

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

    def _prefab_from_dict(self, data: dict) -> Prefab:
        """
        Временная совместимость со старым форматом dict-prefab.
        Наружу (в сценах) больше не используем магические строки.
        """
        prefab = Prefab()

        tr_data = data.get("transform")
        if tr_data is not None:
            prefab.transform = Transform(
                pos_x=float(tr_data.get("pos_x", 0.0)),
                pos_y=float(tr_data.get("pos_y", 0.0)),
                rot=float(tr_data.get("rot", 0.0)),
                scale_x=float(tr_data.get("scale_x", 1.0)),
                scale_y=float(tr_data.get("scale_y", 1.0)),
            )

        rend_data = data.get("renderable")
        if rend_data is not None:
            prefab.renderable = Renderable(
                z_index=int(rend_data.get("z_index", 0)),
            )

        spr_data = data.get("sprite")
        if spr_data is not None:
            tex_path = spr_data.get("texture_path")
            if tex_path is None:
                raise ValueError("Prefab sprite.texture_path is required")
            prefab.sprite = Sprite(texture_path=Path(str(tex_path)))

        return prefab

    def spawn_prefab(self, prefab: Union[Prefab, dict]) -> int:
        """
        Создаёт entity из Prefab.
        (dict поддерживается временно, чтобы ничего не сломать резко)
        """
        if isinstance(prefab, dict):
            prefab = self._prefab_from_dict(prefab)

        eid = self.registry.create_entity()
        self.entities.append(eid)

        if prefab.transform is not None:
            self.registry.add(eid, prefab.transform)

        if prefab.renderable is not None:
            self.registry.add(eid, prefab.renderable)

        if prefab.sprite is not None:
            self.registry.add(eid, prefab.sprite)

        return eid

    def spawn_prefabs(self, prefabs: list[Union[Prefab, dict]]) -> list[int]:
        spawned: list[int] = []
        for prefab in prefabs:
            spawned.append(self.spawn_prefab(prefab))
        return spawned
