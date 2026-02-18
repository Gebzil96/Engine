from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Renderable:
    # 🔧 МОЖНО МЕНЯТЬ: порядок отрисовки (меньше -> раньше)
    z_index: int = 0
