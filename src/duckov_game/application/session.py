"""State and use cases for one run of the game."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from duckov_game.domain import ExtractionZone, LootItem, Player, WorldBounds


class RunStatus(Enum):
    ACTIVE = auto()
    EXTRACTED = auto()


@dataclass(slots=True)
class GameSession:
    """Own all mutable state for the current run."""

    bounds: WorldBounds
    player: Player
    loot_item: LootItem
    extraction_zone: ExtractionZone
    carried_item_count: int = 0
    status: RunStatus = RunStatus.ACTIVE

    def update(
        self,
        direction_x: float,
        direction_y: float,
        delta_seconds: float,
    ) -> None:
        """Advance movement, pickup, and extraction in a fixed order."""

        if self.status is not RunStatus.ACTIVE:
            return

        self.player.move(direction_x, direction_y, delta_seconds, self.bounds)

        if (
            not self.loot_item.is_collected
            and self.player.hitbox.overlaps(self.loot_item.hitbox)
        ):
            self.loot_item.is_collected = True
            self.carried_item_count += 1

        if (
            self.carried_item_count > 0
            and self.player.hitbox.overlaps(self.extraction_zone.hitbox)
        ):
            self.status = RunStatus.EXTRACTED
