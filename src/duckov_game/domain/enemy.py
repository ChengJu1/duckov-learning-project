"""Enemy health and simple, framework-independent pursuit movement."""

from dataclasses import dataclass, field
from math import hypot

from duckov_game.domain.geometry import Rectangle
from duckov_game.domain.health import Health
from duckov_game.domain.player import WorldBounds


@dataclass(slots=True)
class Enemy:
    x: float
    y: float
    width: float = 36.0
    height: float = 36.0
    health: Health = field(default_factory=Health)
    speed: float = 90.0
    stopping_distance: float = 56.0

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("enemy size must be positive")
        if self.speed < 0:
            raise ValueError("enemy speed cannot be negative")
        if self.stopping_distance < 0:
            raise ValueError("stopping_distance cannot be negative")

    @property
    def hitbox(self) -> Rectangle:
        return Rectangle(self.x, self.y, self.width, self.height)

    @property
    def center(self) -> tuple[float, float]:
        return self.x + self.width / 2, self.y + self.height / 2

    def move_toward(
        self,
        target: tuple[float, float],
        delta_seconds: float,
        bounds: WorldBounds,
    ) -> None:
        """Approach a target center without overshooting the stopping distance.

        This is pursuit, not physical collision: targets already too close do
        not push the enemy away. Dead enemies never move.
        """

        if delta_seconds < 0:
            raise ValueError("delta_seconds cannot be negative")
        if self.width > bounds.width or self.height > bounds.height:
            raise ValueError("enemy must fit inside world bounds")
        if not self.health.is_alive:
            return

        center_x, center_y = self.center
        direction_x, direction_y = target[0] - center_x, target[1] - center_y
        distance = hypot(direction_x, direction_y)
        if distance > self.stopping_distance:
            travel = min(self.speed * delta_seconds, distance - self.stopping_distance)
            self.x += direction_x / distance * travel
            self.y += direction_y / distance * travel

        self.x = min(max(self.x, 0.0), bounds.width - self.width)
        self.y = min(max(self.y, 0.0), bounds.height - self.height)
