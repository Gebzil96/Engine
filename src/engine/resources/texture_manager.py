from __future__ import annotations
from pathlib import Path
import moderngl

try:
    from PIL import Image
except ModuleNotFoundError:
    Image = None


class TextureManager:
    """
    Минимальный менеджер текстур.
    Кэширует текстуры по пути.
    """

    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx
        self._textures: dict[Path, moderngl.Texture] = {}

    def get(self, path: str | Path) -> moderngl.Texture:
        path = Path(path)
        if path in self._textures:
            return self._textures[path]

        if Image is None:
            raise ModuleNotFoundError(
                "Pillow не установлен. Установи: pip install pillow"
            )

        img = Image.open(path).convert("RGBA")
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        tex = self.ctx.texture(img.size, 4, img.tobytes())
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.repeat_x = False
        tex.repeat_y = False

        self._textures[path] = tex
        return tex
