"""Game rules that do not depend on pygame or other infrastructure."""

from duckov_game.domain.geometry import Rectangle
from duckov_game.domain.item import LootItem
from duckov_game.domain.player import Player, WorldBounds

__all__ = ["LootItem", "Player", "Rectangle", "WorldBounds"]

