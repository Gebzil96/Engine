from array import array

from src.engine.ecs.components.transform import Transform
from src.engine.render_math import build_model, build_view_proj

from .types import FrameContext


def render_system(
    world,
    fb_w: int,
    fb_h: int,
    vao,
    u_view_proj,
    u_model,
) -> None:
    view_proj = build_view_proj(fb_w, fb_h, world.cam_pos_x, world.cam_pos_y)
    u_view_proj.write(array("f", view_proj).tobytes())

    transforms = world.registry.get_all(Transform)

    for _eid, tr in transforms.items():
        model = build_model(
            tr.pos_x,
            tr.pos_y,
            tr.rot,
            tr.scale_x,
            tr.scale_y,
        )

        u_model.write(array("f", model).tobytes())
        vao.render()
