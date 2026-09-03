"""Minimal health rules shared by damageable actors."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Health:
    maximum: int = 100
    current: int = field(init=False)

    def __post_init__(self) -> None:
        if self.maximum <= 0:
            raise ValueError("maximum health must be positive")
        self.current = self.maximum

    @property
    def is_alive(self) -> bool:
        return self.current > 0

    def take_damage(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("damage cannot be negative")
        self.current = max(0, self.current - amount)
