from pathlib import Path

from src.engine.ecs.components.renderable import Renderable
from src.engine.ecs.components.sprite import Sprite
from src.engine.ecs.components.transform import Transform
from src.engine.scene import Prefab


def build_example_scene() -> list[Prefab]:
    """
    Минимальный scene config: чистые данные (Prefab), которые Scene потом превратит в ECS-сущности.
    """
    return [
        Prefab(
            transform=Transform(pos_x=0.0, pos_y=0.0, rot=0.0, scale_x=1.0, scale_y=1.0),
            renderable=Renderable(z_index=0),
            sprite=Sprite(texture_path=Path("assets/textures/test.png")),
        ),
        Prefab(
            transform=Transform(pos_x=300.0, pos_y=0.0, rot=0.0, scale_x=1.0, scale_y=1.0),
            renderable=Renderable(z_index=1),
            sprite=Sprite(texture_path=Path("assets/textures/test2.png")),
        ),
    ]
