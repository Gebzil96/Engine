from pathlib import Path

from src.engine.ecs.components.renderable import Renderable
from src.engine.ecs.components.sprite import Sprite
from src.engine.ecs.components.transform import Transform
from src.engine.scene import Prefab

import math


def build_example_scene() -> list[Prefab]:
    """
    Минимальный scene config: Prefab = набор компонентов.
    """
    return [
        Prefab(
            role="player",
            components=(
                Transform(pos_x=0.0, pos_y=0.0, rot=0.0, scale_x=1.0, scale_y=1.0),
                Renderable(z_index=0),
                Sprite(texture_path=Path("assets/textures/test.png")),
            )
        ),
        Prefab(
            role="mover",
            components=(
                Transform(pos_x=300.0, pos_y=0.0, rot=0.0, scale_x=1.0, scale_y=1.0),
                Renderable(z_index=1),
                Sprite(texture_path=Path("assets/textures/test2.png")),
            )
        ),
    ]

def update_example_scene(world, frame_ctx: dict) -> None:
    """
    Демонстрация SceneDefinition.update():
    двигаем вторую сущность (e2_entity) по X туда-сюда, чтобы было видно, что lifecycle работает.
    """
    eid = world.scene.get_entity_by_role("mover")
    if eid is None:
        return

    dt = float(frame_ctx.get("dt", 0.0))

    # Время храним прямо в world (без новых компонентов и без новых систем)
    t = float(getattr(world, "_example_scene_t", 0.0)) + dt
    setattr(world, "_example_scene_t", t)

    # Амплитуда/скорость — 🔧 МОЖНО МЕНЯТЬ
    base_x = 300.0
    amplitude = 120.0
    speed = 2.0  # rad/sec

    # Берём Transform и двигаем
    from src.engine.ecs.components.transform import Transform

    tr = world.registry.get(eid, Transform)
    tr.pos_x = base_x + math.sin(t * speed) * amplitude
