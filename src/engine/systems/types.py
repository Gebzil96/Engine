from typing import Any, Callable, Dict

FrameContext = Dict[str, object]
UpdateSystem = Callable[[Any, FrameContext], None]
RenderSystem = Callable[[Any, FrameContext], None]
