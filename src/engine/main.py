import glfw
import moderngl
import time

def main():
    # 1. Инициализация GLFW
    if not glfw.init():
        raise Exception("GLFW не инициализировался")

    # 2. Указываем версию OpenGL (3.3 Core)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    # 3. Создаём окно
    window = glfw.create_window(1280, 720, "Engine", None, None)
    if not window:
        glfw.terminate()
        raise Exception("Окно не создалось")

    # 4. Делаем контекст текущим
    glfw.make_context_current(window)

    # 5. Создаём ModernGL контекст
    ctx = moderngl.create_context()

    # 🔧 МОЖНО МЕНЯТЬ
    TARGET_FPS = 120
    target_frame_time = 1.0 / TARGET_FPS

    last_time = time.perf_counter()

    # 6. Главный цикл
    while not glfw.window_should_close(window):
        frame_start = time.perf_counter()
        dt = frame_start - last_time
        last_time = frame_start
        glfw.poll_events()

        # Чистим экран тёмным цветом
        ctx.clear(0.05, 0.05, 0.08, 1.0)

        glfw.swap_buffers(window)

        frame_end = time.perf_counter()
        frame_time = frame_end - frame_start
        sleep_time = target_frame_time - frame_time
        if sleep_time > 0:
            time.sleep(sleep_time)


    glfw.terminate()


if __name__ == "__main__":
    main()
