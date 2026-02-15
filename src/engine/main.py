import glfw
import moderngl


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

    # 6. Главный цикл
    while not glfw.window_should_close(window):
        glfw.poll_events()

        # Чистим экран тёмным цветом
        ctx.clear(0.05, 0.05, 0.08, 1.0)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
