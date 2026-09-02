"""Loot item state for the stage-one prototype."""

from __future__ import annotations

from dataclasses import dataclass

from duckov_game.domain.geometry import Rectangle


@dataclass(slots=True)
class LootItem:
    """A single item that can be collected once per run."""

    x: float
    y: float
    width: float = 24.0
    height: float = 24.0
    is_collected: bool = False

    @property
    def hitbox(self) -> Rectangle:
        return Rectangle(self.x, self.y, self.width, self.height)

