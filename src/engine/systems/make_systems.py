from .types import UpdateSystem, RenderSystem
from .input_system import input_system
from .close_on_esc_system import close_on_esc_system
from .render_system import render_system


def make_systems(
    quad_move_speed: float,
    cam_move_speed: float,
    quad_rot_speed: float,
    quad_scale_speed: float,
    min_quad_scale: float,
    max_quad_scale: float,
) -> tuple[list[UpdateSystem], list[RenderSystem]]:
    update_systems: list[UpdateSystem] = [
        lambda w, c: input_system(
            w,
            c["window"],
            c["dt"],
            quad_move_speed,
            cam_move_speed,
            quad_rot_speed,
            quad_scale_speed,
            min_quad_scale,
            max_quad_scale,
        ),
        close_on_esc_system,
    ]

    render_systems: list[RenderSystem] = [
        lambda w, c: render_system(
            w,
            c["fb_w"],
            c["fb_h"],
            c["vao"],
            c["u_view_proj"],
            c["u_model"],
        )
    ]

    return update_systems, render_systems
