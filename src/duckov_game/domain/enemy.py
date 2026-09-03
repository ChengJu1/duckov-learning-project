"""A stationary target with a rectangular hitbox and health."""

from dataclasses import dataclass, field

from duckov_game.domain.geometry import Rectangle
from duckov_game.domain.health import Health


@dataclass(slots=True)
class Enemy:
    x: float
    y: float
    width: float = 36.0
    height: float = 36.0
    health: Health = field(default_factory=Health)

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("enemy size must be positive")

    @property
    def hitbox(self) -> Rectangle:
        return Rectangle(self.x, self.y, self.width, self.height)
