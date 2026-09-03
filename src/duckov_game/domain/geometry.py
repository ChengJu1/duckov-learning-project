"""Small geometry primitives shared by game rules."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Rectangle:
    """Axis-aligned rectangle whose position is its top-left corner."""

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("rectangle size must be positive")

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def overlaps(self, other: Rectangle) -> bool:
        """Return whether two rectangles have an area of intersection."""

        return (
            self.x < other.right
            and self.right > other.x
            and self.y < other.bottom
            and self.bottom > other.y
        )

    def intersects_segment(
        self, start: tuple[float, float], end: tuple[float, float]
    ) -> bool:
        """Clip a segment to both axes; touching the boundary counts as a hit."""

        enter, leave = 0.0, 1.0
        for origin, destination, lower, upper in (
            (start[0], end[0], self.x, self.right),
            (start[1], end[1], self.y, self.bottom),
        ):
            delta = destination - origin
            if delta == 0:
                if not lower <= origin <= upper:
                    return False
                continue
            first, last = sorted(((lower - origin) / delta, (upper - origin) / delta))
            enter = max(enter, first)
            leave = min(leave, last)
            if enter > leave:
                return False
        return True
