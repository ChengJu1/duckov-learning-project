"""Loot item state for the stage-one prototype."""

from __future__ import annotations

from dataclasses import dataclass

from duckov_game.domain.geometry import Rectangle


@dataclass(frozen=True, slots=True)
class ItemStack:
    """An immutable item identifier and a positive integer quantity."""

    item_id: str
    quantity: int = 1

    def __post_init__(self) -> None:
        if (
            not isinstance(self.item_id, str)
            or not self.item_id
            or self.item_id.strip() != self.item_id
        ):
            raise ValueError("item_id must be a nonempty string without surrounding whitespace")
        if type(self.quantity) is not int or self.quantity <= 0:
            raise ValueError("quantity must be a positive integer")


@dataclass(slots=True)
class LootItem:
    """A single item that can be collected once per run."""

    x: float
    y: float
    width: float = 24.0
    height: float = 24.0
    is_collected: bool = False
    item_id: str = "scrap"
    quantity: int = 1

    def __post_init__(self) -> None:
        ItemStack(self.item_id, self.quantity)

    @property
    def hitbox(self) -> Rectangle:
        return Rectangle(self.x, self.y, self.width, self.height)
