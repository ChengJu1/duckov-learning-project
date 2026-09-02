"""Game rules that do not depend on pygame or other infrastructure."""

from duckov_game.domain.extraction import ExtractionZone
from duckov_game.domain.geometry import Rectangle
from duckov_game.domain.item import LootItem
from duckov_game.domain.player import Player, WorldBounds
from duckov_game.domain.projectile import Projectile

__all__ = [
    "ExtractionZone",
    "LootItem",
    "Player",
    "Projectile",
    "Rectangle",
    "WorldBounds",
]
