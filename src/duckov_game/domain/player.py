"""Player movement rules for the stage-one prototype."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from duckov_game.domain.geometry import Rectangle


@dataclass(frozen=True, slots=True)
class WorldBounds:
    """Rectangular playable area measured in pixels."""

    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("world bounds must be positive")


@dataclass(slots=True)
class Player:
    """Player state whose position is the rectangle's top-left corner."""

    x: float
    y: float
    width: float = 32.0
    height: float = 32.0
    speed: float = 240.0
    aim_x: float = 1.0
    aim_y: float = 0.0

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("player size must be positive")
        if self.speed < 0:
            raise ValueError("player speed cannot be negative")
        aim_length = hypot(self.aim_x, self.aim_y)
        if aim_length == 0:
            raise ValueError("initial aim direction cannot be zero")
        self.aim_x /= aim_length
        self.aim_y /= aim_length

    @property
    def hitbox(self) -> Rectangle:
        return Rectangle(self.x, self.y, self.width, self.height)

    @property
    def center(self) -> tuple[float, float]:
        return self.x + self.width / 2, self.y + self.height / 2

    def aim_at(self, target_x: float, target_y: float) -> None:
        """Aim from the player's center toward a target position."""

        center_x, center_y = self.center
        direction_x = target_x - center_x
        direction_y = target_y - center_y
        direction_length = hypot(direction_x, direction_y)

        if direction_length == 0:
            return

        self.aim_x = direction_x / direction_length
        self.aim_y = direction_y / direction_length

    def move(
        self,
        direction_x: float,
        direction_y: float,
        delta_seconds: float,
        bounds: WorldBounds,
    ) -> None:
        """Move in a direction and keep the whole player inside ``bounds``."""

        if delta_seconds < 0:
            raise ValueError("delta_seconds cannot be negative")
        if self.width > bounds.width or self.height > bounds.height:
            raise ValueError("player must fit inside world bounds")

        direction_length = hypot(direction_x, direction_y)
        if direction_length > 0:
            distance = self.speed * delta_seconds
            self.x += direction_x / direction_length * distance
            self.y += direction_y / direction_length * distance

        self.x = min(max(self.x, 0.0), bounds.width - self.width)
        self.y = min(max(self.y, 0.0), bounds.height - self.height)
