"""In-memory quantities keyed by item identifier; no capacity or equipment rules."""

from __future__ import annotations

from dataclasses import dataclass, field

from duckov_game.domain.item import ItemStack


@dataclass(slots=True)
class Inventory:
    _quantities: dict[str, int] = field(default_factory=dict, init=False, repr=False)

    @property
    def total_count(self) -> int:
        return sum(self._quantities.values())

    @property
    def entries(self) -> tuple[ItemStack, ...]:
        """Return an immutable, sorted snapshot, not the internal dictionary."""

        return tuple(ItemStack(key, value) for key, value in sorted(self._quantities.items()))

    def quantity_of(self, item_id: str) -> int:
        ItemStack(item_id)
        return self._quantities.get(item_id, 0)

    def add(self, item_id: str, quantity: int = 1) -> None:
        stack = ItemStack(item_id, quantity)
        self._quantities[stack.item_id] = self._quantities.get(stack.item_id, 0) + stack.quantity

    def remove(self, item_id: str, quantity: int = 1) -> None:
        stack = ItemStack(item_id, quantity)
        current = self._quantities.get(stack.item_id, 0)
        if current < stack.quantity:
            raise ValueError("not enough items to remove")
        remaining = current - stack.quantity
        if remaining:
            self._quantities[stack.item_id] = remaining
        else:
            del self._quantities[stack.item_id]

    def clear(self) -> None:
        self._quantities.clear()

    def transfer_all_to(self, target: Inventory) -> None:
        """Merge quantities into a different inventory and empty this one."""

        if target is self:
            raise ValueError("cannot transfer inventory to itself")
        merged = target._quantities.copy()
        for item_id, quantity in self._quantities.items():
            merged[item_id] = merged.get(item_id, 0) + quantity
        target._quantities = merged
        self.clear()
