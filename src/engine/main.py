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
    glfw.swap_interval(0)  # VSync OFF (кап FPS будем делать сами)

    # 5. Создаём ModernGL контекст
    ctx = moderngl.create_context()

    # 🔧 МОЖНО МЕНЯТЬ
    TARGET_FPS = 120
    target_frame_time = 1.0 / TARGET_FPS

    last_time = time.perf_counter()

    fps_timer = 0.0
    frame_count = 0

    # 6. Главный цикл
    while not glfw.window_should_close(window):
        frame_start = time.perf_counter()
        dt = frame_start - last_time
        last_time = frame_start
        fps_timer += dt
        frame_count += 1

        glfw.poll_events()

        # Чистим экран тёмным цветом
        ctx.clear(0.05, 0.05, 0.08, 1.0)

        glfw.swap_buffers(window)

        if fps_timer >= 1.0:
            fps = frame_count / fps_timer
            glfw.set_window_title(window, f"Engine | FPS: {fps:.2f}")
            fps_timer = 0.0
            frame_count = 0

        # Кап FPS (Windows sleep неточный): сначала поспим почти до цели, потом "докрутим" spin-ожиданием
        while True:
            now = time.perf_counter()
            elapsed = now - frame_start
            remaining = target_frame_time - elapsed
            if remaining <= 0:
                break

            # если осталось больше ~2мс — можно поспать
            if remaining > 0.002:
                time.sleep(remaining - 0.001)
            else:
                # последние ~2мс ждём без sleep для точности
                pass

    glfw.terminate()


if __name__ == "__main__":
    main()
