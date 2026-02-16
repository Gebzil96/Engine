import glfw
import moderngl
import time
from pathlib import Path
from array import array
import math
import logging
from datetime import datetime
import sys

EMERGENCY_LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "run.log"
EMERGENCY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def ortho(left, right, bottom, top, near, far):
    return [
        2.0 / (right - left), 0, 0, 0,
        0, 2.0 / (top - bottom), 0, 0,
        0, 0, -2.0 / (far - near), 0,
        -(right + left) / (right - left),
        -(top + bottom) / (top - bottom),
        -(far + near) / (far - near),
        1.0,
    ]

def mat4_identity():
    return [
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0,
    ]


def mat4_translate(tx: float, ty: float, tz: float = 0.0):
    m = mat4_identity()
    # Column-major: translation is in indices 12..14 (same style as ortho() above)
    m[12] = tx
    m[13] = ty
    m[14] = tz
    return m

def mat4_translate_inv(tx: float, ty: float, tz: float = 0.0):
    # Inverse for pure translation is translation by negative values
    return mat4_translate(-tx, -ty, -tz)

def mat4_scale(sx: float, sy: float, sz: float = 1.0):
    m = mat4_identity()
    m[0] = sx
    m[5] = sy
    m[10] = sz
    return m


def mat4_rotate_z(angle_radians: float):
    c = math.cos(angle_radians)
    s = math.sin(angle_radians)
    return [
        c,   s,   0.0, 0.0,
        -s,  c,   0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0,
    ]


def mat4_mul(a, b):
    # Column-major 4x4: out = a * b
    out = [0.0] * 16
    for col in range(4):
        for row in range(4):
            out[col * 4 + row] = (
                a[0 * 4 + row] * b[col * 4 + 0] +
                a[1 * 4 + row] * b[col * 4 + 1] +
                a[2 * 4 + row] * b[col * 4 + 2] +
                a[3 * 4 + row] * b[col * 4 + 3]
            )
    return out

def build_view_proj(fb_w: int, fb_h: int, cam_x: float, cam_y: float):
    projection = ortho(
        -fb_w / 2,
        fb_w / 2,
        -fb_h / 2,
        fb_h / 2,
        -1.0,
        1.0,
    )

    view = mat4_translate_inv(cam_x, cam_y, 0.0)
    return mat4_mul(projection, view)


def build_model(pos_x: float, pos_y: float, rot_rad: float, scale_x: float, scale_y: float):
    t = mat4_translate(pos_x, pos_y, 0.0)
    r = mat4_rotate_z(rot_rad)
    s = mat4_scale(scale_x, scale_y, 1.0)
    return mat4_mul(t, mat4_mul(r, s))

def setup_logging() -> Path:
    # Путь от файла main.py: src/engine/main.py -> корень проекта = parents[2]
    project_root = Path(__file__).resolve().parents[2]

    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_path = logs_dir / "run.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_path, mode="w", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    logging.info("Engine start")
    logging.info("Python version: %s", sys.version)
    logging.info("glfw version: %s", getattr(glfw, "__version__", "unknown"))
    logging.info("moderngl version: %s", getattr(moderngl, "__version__", "unknown"))
    logging.info("Log file: %s", log_path)

    return log_path


def main():
    try:
        setup_logging()
        engine_start_time = time.perf_counter()
        # 1. Инициализация GLFW
        if not glfw.init():
            raise Exception("GLFW не инициализировался")

        # 2. Указываем версию OpenGL (3.3 Core)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        # 3. Создаём окно
        window = glfw.create_window(1280, 720, "Engine", None, None)
        logging.info("Requested window size: %s x %s", 1280, 720)
        if not window:
            glfw.terminate()
            raise Exception("Окно не создалось")

        # 4. Делаем контекст текущим
        glfw.make_context_current(window)
        glfw.swap_interval(0)
        logging.info("VSync: OFF")

        # 5. Создаём ModernGL контекст
        ctx = moderngl.create_context()

        logging.info("OpenGL version: %s", ctx.info["GL_VERSION"])
        logging.info("GPU: %s", ctx.info["GL_RENDERER"])

        # --- Resize -> viewport ---
        last_resize_log_time = 0.0
        last_logged_size = None

        def _on_framebuffer_resize(_window, width: int, height: int) -> None:
            if width <= 0 or height <= 0:
                return

            nonlocal last_resize_log_time, last_logged_size

            ctx.viewport = (0, 0, width, height)

            now = time.perf_counter()
            if (width, height) != last_logged_size and (now - last_resize_log_time) >= 0.25:
                logging.info("Resize: framebuffer %s x %s", width, height)
                last_logged_size = (width, height)
                last_resize_log_time = now

        glfw.set_framebuffer_size_callback(window, _on_framebuffer_resize)

        def _on_window_close(_window) -> None:
            logging.info("Event: window close requested (close button / Alt+F4)")

        glfw.set_window_close_callback(window, _on_window_close)

        fb_w, fb_h = glfw.get_framebuffer_size(window)
        logging.info("Framebuffer size: %s x %s", fb_w, fb_h)
        if fb_w > 0 and fb_h > 0:
            ctx.viewport = (0, 0, fb_w, fb_h)
            last_logged_size = (fb_w, fb_h)

        # Путь от файла main.py: src/engine/main.py -> корень проекта = parents[2]
        project_root = Path(__file__).resolve().parents[2]

        shader_dir = project_root / "assets" / "shaders"
        vert_path = shader_dir / "basic.vert"
        frag_path = shader_dir / "basic.frag"

        logging.info("Shader vertex path: %s", vert_path)
        logging.info("Shader fragment path: %s", frag_path)

        vert_src = vert_path.read_text(encoding="utf-8")
        frag_src = frag_path.read_text(encoding="utf-8")

        logging.info("Shaders loaded OK")

        prog = ctx.program(vertex_shader=vert_src, fragment_shader=frag_src)
        u_view_proj = prog["u_view_proj"]
        u_model = prog["u_model"]

        # --- Simple draw: quad ---
        # 🔧 МОЖНО МЕНЯТЬ
        quad_pos_x = 0.0
        quad_pos_y = 0.0

        # 🔧 МОЖНО МЕНЯТЬ
        QUAD_MOVE_SPEED_PX_PER_SEC = 300.0

        # 🔧 МОЖНО МЕНЯТЬ
        quad_rot_rad = 0.0

        # 🔧 МОЖНО МЕНЯТЬ
        quad_scale_x = 1.0
        quad_scale_y = 1.0

        # 🔧 МОЖНО МЕНЯТЬ
        QUAD_ROT_SPEED_RAD_PER_SEC = 2.5
        QUAD_SCALE_SPEED_PER_SEC = 1.0
        MIN_QUAD_SCALE = 0.1
        MAX_QUAD_SCALE = 8.0

        # --- Camera (view) ---
        # 🔧 МОЖНО МЕНЯТЬ
        cam_pos_x = 0.0
        cam_pos_y = 0.0

        # 🔧 МОЖНО МЕНЯТЬ
        CAM_MOVE_SPEED_PX_PER_SEC = 400.0

        # --- Scene objects (temporary, before ECS) ---
        scene_objects = [
            {
                "pos_x": 0.0,
                "pos_y": 0.0,
                "rot": 0.0,
                "scale_x": 1.0,
                "scale_y": 1.0,
            },
            {
                "pos_x": 300.0,
                "pos_y": 0.0,
                "rot": 0.0,
                "scale_x": 1.0,
                "scale_y": 1.0,
            },
        ]

        quad_vertices = array('f', [
            -50.0, -50.0,
            50.0, -50.0,
            50.0,  50.0,
            -50.0,  50.0,
        ])

        quad_indices = array('I', [
            0, 1, 2,
            2, 3, 0,
        ])

        vbo = ctx.buffer(quad_vertices.tobytes())
        ibo = ctx.buffer(quad_indices.tobytes())

        vao = ctx.vertex_array(
            prog,
            [(vbo, "2f", "in_pos")],
            index_buffer=ibo
        )

        # 🔧 МОЖНО МЕНЯТЬ
        TARGET_FPS = 120
        logging.info("Target FPS: %s", TARGET_FPS)
        target_frame_time = 1.0 / TARGET_FPS

        last_time = time.perf_counter()

        fps_timer = 0.0
        frame_count = 0
        last_logged_fps = 0.0
        last_fps_log_time = 0.0
        last_fps_value = 0.0
        was_minimized = False

        # 6. Главный цикл
        while not glfw.window_should_close(window):
            frame_start = time.perf_counter()
            dt = frame_start - last_time
            last_time = frame_start
            fps_timer += dt
            frame_count += 1

            glfw.poll_events()

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

                quad_pos_x += move_x * QUAD_MOVE_SPEED_PX_PER_SEC * dt
                quad_pos_y += move_y * QUAD_MOVE_SPEED_PX_PER_SEC * dt
            
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

                cam_pos_x += cam_move_x * CAM_MOVE_SPEED_PX_PER_SEC * dt
                cam_pos_y += cam_move_y * CAM_MOVE_SPEED_PX_PER_SEC * dt

            # --- Quad rotation (Q/E) ---
            if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
                quad_rot_rad += QUAD_ROT_SPEED_RAD_PER_SEC * dt
            if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
                quad_rot_rad -= QUAD_ROT_SPEED_RAD_PER_SEC * dt

            # --- Quad scale (Z/X) ---
            if glfw.get_key(window, glfw.KEY_Z) == glfw.PRESS:
                quad_scale_x -= QUAD_SCALE_SPEED_PER_SEC * dt
                quad_scale_y -= QUAD_SCALE_SPEED_PER_SEC * dt
            if glfw.get_key(window, glfw.KEY_X) == glfw.PRESS:
                quad_scale_x += QUAD_SCALE_SPEED_PER_SEC * dt
                quad_scale_y += QUAD_SCALE_SPEED_PER_SEC * dt

            quad_scale_x = max(MIN_QUAD_SCALE, min(MAX_QUAD_SCALE, quad_scale_x))
            quad_scale_y = max(MIN_QUAD_SCALE, min(MAX_QUAD_SCALE, quad_scale_y))

            # Apply controlled transform to the first scene object
            scene_objects[0]["pos_x"] = quad_pos_x
            scene_objects[0]["pos_y"] = quad_pos_y
            scene_objects[0]["rot"] = quad_rot_rad
            scene_objects[0]["scale_x"] = quad_scale_x
            scene_objects[0]["scale_y"] = quad_scale_y

            # Закрытие по Esc
            if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
                logging.info("Event: ESC pressed -> close window")
                glfw.set_window_should_close(window, True)

            # Чистим экран
            ctx.clear(0.05, 0.05, 0.08, 1.0)

            fb_w, fb_h = glfw.get_framebuffer_size(window)
            if fb_w <= 0 or fb_h <= 0:
                # Окно свернули (или размер временно 0x0) — пропускаем кадр, чтобы не падать
                if not was_minimized:
                    logging.info("Window minimized (framebuffer is 0x0) -> rendering paused")
                    was_minimized = True
                glfw.swap_buffers(window)
                continue
            if was_minimized:
                logging.info("Window restored -> rendering resumed (framebuffer %s x %s)", fb_w, fb_h)
                was_minimized = False

            view_proj = build_view_proj(fb_w, fb_h, cam_pos_x, cam_pos_y)
            u_view_proj.write(array('f', view_proj).tobytes())

            for obj in scene_objects:
                model = build_model(
                    obj["pos_x"],
                    obj["pos_y"],
                    obj["rot"],
                    obj["scale_x"],
                    obj["scale_y"],
                )
                u_model.write(array('f', model).tobytes())
                vao.render()

            glfw.swap_buffers(window)

            if fps_timer >= 1.0:
                fps = frame_count / fps_timer
                last_fps_value = fps
                now = time.perf_counter()
                if (now - last_fps_log_time) >= 5.0 and abs(fps - last_logged_fps) > 5.0:
                    logging.info("FPS: %.2f", fps)
                    last_logged_fps = fps
                    last_fps_log_time = now
                glfw.set_window_title(window, f"Engine | FPS: {fps:.2f}")
                fps_timer = 0.0
                frame_count = 0

            while True:
                now = time.perf_counter()
                elapsed = now - frame_start
                remaining = target_frame_time - elapsed
                if remaining <= 0:
                    break

                if remaining > 0.002:
                    time.sleep(remaining - 0.001)
                else:
                    pass

    except Exception:
        logging.exception("CRASH: unhandled exception")
        raise
    finally:
        try:
            run_seconds = time.perf_counter() - engine_start_time
            logging.info(
                "Engine shutdown summary: uptime=%.2fs, frames=%s, last_fps=%.2f",
                run_seconds,
                frame_count,
                last_fps_value,
            )
        except Exception:
            # На случай, если упали очень рано и переменные не создались
            pass

        logging.info("Engine shutdown")
        glfw.terminate()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Если логирование ещё не успело включиться — пишем причину падения “вручную”
        with open(EMERGENCY_LOG_PATH, "a", encoding="utf-8") as f:
            f.write("\n--- EMERGENCY CRASH ---\n")
        logging.exception("EMERGENCY CRASH (before logging fully ready)")
        raise
