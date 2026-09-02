"""State and use cases for one run of the game."""

from __future__ import annotations

from dataclasses import dataclass

from duckov_game.domain import LootItem, Player, WorldBounds


@dataclass(slots=True)
class GameSession:
    """Own all mutable state for the current run."""

    bounds: WorldBounds
    player: Player
    loot_item: LootItem
    carried_item_count: int = 0

    def update(
        self,
        direction_x: float,
        direction_y: float,
        delta_seconds: float,
    ) -> None:
        """Advance movement and resolve automatic item pickup."""

        self.player.move(direction_x, direction_y, delta_seconds, self.bounds)

        if (
            not self.loot_item.is_collected
            and self.player.hitbox.overlaps(self.loot_item.hitbox)
        ):
            self.loot_item.is_collected = True
            self.carried_item_count += 1

