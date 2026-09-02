"""Projectile movement rules for the stage-two combat prototype."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from duckov_game.domain.player import WorldBounds


@dataclass(slots=True)
class Projectile:
    """A circular projectile whose position represents its center."""

    x: float
    y: float
    direction_x: float
    direction_y: float
    speed: float = 520.0
    radius: float = 5.0

    def __post_init__(self) -> None:
        if self.speed < 0:
            raise ValueError("projectile speed cannot be negative")
        if self.radius <= 0:
            raise ValueError("projectile radius must be positive")

        direction_length = hypot(self.direction_x, self.direction_y)
        if direction_length == 0:
            raise ValueError("projectile direction cannot be zero")
        self.direction_x /= direction_length
        self.direction_y /= direction_length

    def move(self, delta_seconds: float) -> None:
        """Advance the projectile along its normalized direction."""

        if delta_seconds < 0:
            raise ValueError("delta_seconds cannot be negative")
        self.x += self.direction_x * self.speed * delta_seconds
        self.y += self.direction_y * self.speed * delta_seconds

    def intersects(self, bounds: WorldBounds) -> bool:
        """Return whether any part of the projectile remains in the world."""

        return (
            self.x + self.radius >= 0
            and self.x - self.radius <= bounds.width
            and self.y + self.radius >= 0
            and self.y - self.radius <= bounds.height
        )
