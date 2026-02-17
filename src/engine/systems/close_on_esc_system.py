import logging
import glfw

from .types import FrameContext


def close_on_esc_system(world, ctx: FrameContext) -> None:
    window = ctx["window"]
    # Закрытие по Esc (как система обновления)
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        logging.info("Event: ESC pressed -> close window")
        glfw.set_window_should_close(window, True)
