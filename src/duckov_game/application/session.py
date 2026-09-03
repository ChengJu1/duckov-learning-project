"""State and use cases for one run of the game."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from duckov_game.domain import (
    Enemy,
    ExtractionZone,
    LootItem,
    Player,
    Projectile,
    WorldBounds,
)


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
    projectiles: list[Projectile] = field(default_factory=list)
    carried_item_count: int = 0
    status: RunStatus = RunStatus.ACTIVE
    enemy: Enemy | None = None

    def update(
        self,
        direction_x: float,
        direction_y: float,
        delta_seconds: float,
        *,
        aim_target: tuple[float, float] | None = None,
        fire_requested: bool = False,
    ) -> None:
        """Advance movement, combat, pickup, and extraction in a fixed order."""

        if self.status is not RunStatus.ACTIVE:
            return

        self.player.move(direction_x, direction_y, delta_seconds, self.bounds)
        if aim_target is not None:
            self.player.aim_at(*aim_target)
        if fire_requested:
            center_x, center_y = self.player.center
            self.projectiles.append(
                Projectile(
                    x=center_x,
                    y=center_y,
                    direction_x=self.player.aim_x,
                    direction_y=self.player.aim_y,
                )
            )

        remaining_projectiles = []
        for projectile in self.projectiles:
            start = (projectile.x, projectile.y)
            projectile.move(delta_seconds)
            if (
                self.enemy is not None
                and self.enemy.health.is_alive
                and projectile.hits(self.enemy.hitbox, start)
            ):
                self.enemy.health.take_damage(projectile.damage)
                continue
            if projectile.intersects(self.bounds):
                remaining_projectiles.append(projectile)
        self.projectiles = remaining_projectiles

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
