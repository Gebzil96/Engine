from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Transform:
    pos_x: float = 0.0
    pos_y: float = 0.0
    rot: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
