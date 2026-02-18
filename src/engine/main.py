import glfw
import moderngl
import time
from pathlib import Path
from array import array
import logging

try:
    from PIL import Image
except ModuleNotFoundError:
    Image = None

import sys
from src.engine.systems.types import FrameContext
from src.engine.systems.make_systems import make_systems
from src.engine.resources.texture_manager import TextureManager
from src.engine.scene import Scene
from src.engine.scenes.loader import get_scene_builder

# --- ECS (Entity + Component Registry) ---
try:
    # Обычный запуск через run_engine.pyw: from src.engine.main import main
    from src.engine.ecs.registry import Registry
    from src.engine.ecs.components.transform import Transform
    from src.engine.ecs.components.renderable import Renderable
except ModuleNotFoundError:
    # На всякий случай: если main.py запустили напрямую, добавим корень проекта в sys.path
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from src.engine.ecs.registry import Registry
    from src.engine.ecs.components.transform import Transform
    from src.engine.ecs.components.renderable import Renderable

EMERGENCY_LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "run.log"
EMERGENCY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Matrix helpers moved to src/engine/render_math.py (no behavior change)

class World:
    def __init__(self):
        # --- Camera ---
        self.cam_pos_x = 0.0
        self.cam_pos_y = 0.0

        # --- ECS core ---
        self.registry = Registry()

        # --- Scene ---
        self.scene = Scene(self.registry)

        # Сущности спавним позже в main(), когда текстуры уже загружены
        self.player_entity: int | None = None
        self.e2_entity: int | None = None

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

def load_texture_rgba(ctx, path: Path):
    if Image is None:
        raise ModuleNotFoundError(
            "Pillow не установлен. Установи: pip install pillow"
        )

    img = Image.open(path).convert("RGBA")
    # OpenGL ожидает начало координат снизу-слева, PNG обычно сверху-слева
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    tex = ctx.texture(img.size, 4, img.tobytes())
    tex.filter = (moderngl.NEAREST, moderngl.NEAREST)  # пиксельный стиль
    tex.repeat_x = False
    tex.repeat_y = False
    return tex


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
        world = World()
        texture_manager = TextureManager(ctx)

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

        texture_path = project_root / "assets" / "textures" / "test.png"
        logging.info("Texture path: %s", texture_path)

        tex0 = texture_manager.get(texture_path)
        logging.info("Texture loaded OK: %s", texture_path.name)

        texture_path2 = project_root / "assets" / "textures" / "test2.png"
        logging.info("Texture2 path: %s", texture_path2)

        tex1 = texture_manager.get(texture_path2)
        logging.info("Texture2 loaded OK: %s", texture_path2.name)

        # --- Scene: спавним сущности теперь, когда текстуры уже загружены ---
        # 🔧 МОЖНО МЕНЯТЬ
        SCENE_ID = "example_scene"

        scene_builder = get_scene_builder(SCENE_ID)
        prefabs = scene_builder()
        spawned = world.scene.spawn_prefabs(prefabs)

        world.player_entity = spawned[0] if len(spawned) > 0 else None
        world.e2_entity = spawned[1] if len(spawned) > 1 else None

        prog = ctx.program(vertex_shader=vert_src, fragment_shader=frag_src)
        u_view_proj = prog["u_view_proj"]
        u_model = prog["u_model"]
        u_tex = prog["u_tex"]
        u_tex.value = 0  # texture unit 0


        # 🔧 МОЖНО МЕНЯТЬ
        QUAD_MOVE_SPEED_PX_PER_SEC = 300.0

        # 🔧 МОЖНО МЕНЯТЬ
        QUAD_ROT_SPEED_RAD_PER_SEC = 2.5
        QUAD_SCALE_SPEED_PER_SEC = 1.0
        MIN_QUAD_SCALE = 0.1
        MAX_QUAD_SCALE = 8.0

        # --- Camera (view) ---
        # 🔧 МОЖНО МЕНЯТЬ
        CAM_MOVE_SPEED_PX_PER_SEC = 400.0

        quad_vertices = array("f", [
            # x, y,   u, v
            -50.0, -50.0, 0.0, 0.0,
            50.0, -50.0, 1.0, 0.0,
            50.0,  50.0, 1.0, 1.0,
            -50.0,  50.0, 0.0, 1.0,
        ])

        quad_indices = array('I', [
            0, 1, 2,
            2, 3, 0,
        ])

        vbo = ctx.buffer(quad_vertices.tobytes())
        ibo = ctx.buffer(quad_indices.tobytes())

        vao = ctx.vertex_array(
            prog, [(vbo, "2f 2f", "in_pos", "in_uv")], index_buffer=ibo
        )

        # 🔧 МОЖНО МЕНЯТЬ
        TARGET_FPS = 120
        logging.info("Target FPS: %s", TARGET_FPS)
        target_frame_time = 1.0 / TARGET_FPS

        update_systems, render_systems = make_systems(
            QUAD_MOVE_SPEED_PX_PER_SEC,
            CAM_MOVE_SPEED_PX_PER_SEC,
            QUAD_ROT_SPEED_RAD_PER_SEC,
            QUAD_SCALE_SPEED_PER_SEC,
            MIN_QUAD_SCALE,
            MAX_QUAD_SCALE,
        )

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

            frame_ctx: FrameContext = {
                "window": window,
                "dt": dt,
                "texture_manager": texture_manager,
            }

            for sys_update in update_systems:
                sys_update(world, frame_ctx)

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
            
            frame_ctx["fb_w"] = fb_w
            frame_ctx["fb_h"] = fb_h
            frame_ctx["vao"] = vao
            frame_ctx["u_view_proj"] = u_view_proj
            frame_ctx["u_model"] = u_model

            for sys_render in render_systems:
                sys_render(world, frame_ctx)

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
