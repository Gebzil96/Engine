from src.engine.ecs.components.transform import Transform
from src.engine.ecs.components.renderable import Renderable
from src.engine.ecs.components.sprite import Sprite

class Scene:
    def __init__(self, registry):
        self.registry = registry
        self.entities: list[int] = []
    
    def spawn_prefab(self, data: dict) -> int:
        """
        Создаёт entity из "данных" (словаря).
        Сейчас поддерживаем: Transform, Renderable, Sprite.
        """
        eid = self.registry.create_entity()
        self.entities.append(eid)

        # Transform
        tr_data = data.get("transform")
        if tr_data is not None:
            self.registry.add(
                eid,
                Transform(
                    pos_x=float(tr_data.get("pos_x", 0.0)),
                    pos_y=float(tr_data.get("pos_y", 0.0)),
                    rot=float(tr_data.get("rot", 0.0)),
                    scale_x=float(tr_data.get("scale_x", 1.0)),
                    scale_y=float(tr_data.get("scale_y", 1.0)),
                ),
            )

        # Renderable
        rend_data = data.get("renderable")
        if rend_data is not None:
            self.registry.add(
                eid,
                Renderable(
                    z_index=int(rend_data.get("z_index", 0)),
                ),
            )

        # Sprite
        spr_data = data.get("sprite")
        if spr_data is not None:
            tex_path = spr_data.get("texture_path")
            if tex_path is None:
                raise ValueError("Prefab sprite.texture_path is required")
            self.registry.add(eid, Sprite(texture_path=tex_path))

        return eid    

    def spawn_example(self, player_texture_path, e2_texture_path):
        player = self.spawn_prefab(
            {
                "transform": {
                    "pos_x": 0.0,
                    "pos_y": 0.0,
                    "rot": 0.0,
                    "scale_x": 1.0,
                    "scale_y": 1.0,
                },
                "renderable": {"z_index": 0},
                "sprite": {"texture_path": player_texture_path},
            }
        )

        e2 = self.spawn_prefab(
            {
                "transform": {
                    "pos_x": 300.0,
                    "pos_y": 0.0,
                    "rot": 0.0,
                    "scale_x": 1.0,
                    "scale_y": 1.0,
                },
                "renderable": {"z_index": 1},
                "sprite": {"texture_path": e2_texture_path},
            }
        )

        return player, e2
