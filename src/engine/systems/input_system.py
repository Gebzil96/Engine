import math
import glfw

from src.engine.ecs.components.transform import Transform

from .types import FrameContext


def input_system(
    world,
    window,
    dt: float,
    quad_move_speed: float,
    cam_move_speed: float,
    quad_rot_speed: float,
    quad_scale_speed: float,
    min_quad_scale: float,
    max_quad_scale: float,
) -> None:
    # --- Quad movement (WASD) ---
    move_x = 0.0
    move_y = 0.0

    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        move_x -= 1.0
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        move_x += 1.0
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        move_y += 1.0
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        move_y -= 1.0

    if move_x != 0.0 or move_y != 0.0:
        length = math.sqrt(move_x * move_x + move_y * move_y)
        move_x /= length
        move_y /= length

        transform = world.registry.get(world.player_entity, Transform)
        transform.pos_x += move_x * quad_move_speed * dt
        transform.pos_y += move_y * quad_move_speed * dt

    # --- Camera movement (Arrow keys) ---
    cam_move_x = 0.0
    cam_move_y = 0.0

    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
        cam_move_x -= 1.0
    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
        cam_move_x += 1.0
    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        cam_move_y += 1.0
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        cam_move_y -= 1.0

    if cam_move_x != 0.0 or cam_move_y != 0.0:
        length = math.sqrt(cam_move_x * cam_move_x + cam_move_y * cam_move_y)
        cam_move_x /= length
        cam_move_y /= length

        world.cam_pos_x += cam_move_x * cam_move_speed * dt
        world.cam_pos_y += cam_move_y * cam_move_speed * dt

    # --- Quad rotation (Q/E) ---
    transform = world.registry.get(world.player_entity, Transform)

    if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
        transform.rot += quad_rot_speed * dt
    if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
        transform.rot -= quad_rot_speed * dt

    # --- Quad scale (Z/X) ---
    transform = world.registry.get(world.player_entity, Transform)

    if glfw.get_key(window, glfw.KEY_Z) == glfw.PRESS:
        transform.scale_x -= quad_scale_speed * dt
        transform.scale_y -= quad_scale_speed * dt
    if glfw.get_key(window, glfw.KEY_X) == glfw.PRESS:
        transform.scale_x += quad_scale_speed * dt
        transform.scale_y += quad_scale_speed * dt

    transform.scale_x = max(
        min_quad_scale,
        min(max_quad_scale, transform.scale_x),
    )

    transform.scale_y = max(
        min_quad_scale,
        min(max_quad_scale, transform.scale_y),
    )
