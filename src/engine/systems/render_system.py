from array import array

from src.engine.ecs.components.renderable import Renderable
from src.engine.ecs.components.sprite import Sprite
from src.engine.ecs.components.transform import Transform
from src.engine.render_math import build_model, build_view_proj
from src.engine.resources.texture_manager import TextureManager


def render_system(
    world,
    fb_w: int,
    fb_h: int,
    vao,
    u_view_proj,
    u_model,
    texture_manager: TextureManager,
) -> None:
    view_proj = build_view_proj(fb_w, fb_h, world.cam_pos_x, world.cam_pos_y)
    u_view_proj.write(array("f", view_proj).tobytes())

    # Берём только сущности, у которых есть Transform + Renderable + Sprite
    entity_ids = world.registry.query(Transform, Renderable, Sprite)

    # Сортируем по z_index
    entity_ids.sort(key=lambda eid: world.registry.get(eid, Renderable).z_index)

    for eid in entity_ids:
        tr = world.registry.get(eid, Transform)

        sprite = world.registry.get(eid, Sprite)
        tex = texture_manager.get(sprite.texture_path)
        tex.use(location=0)

        model = build_model(
            tr.pos_x,
            tr.pos_y,
            tr.rot,
            tr.scale_x,
            tr.scale_y,
        )
        u_model.write(array("f", model).tobytes())
        vao.render()
