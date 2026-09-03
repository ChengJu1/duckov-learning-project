from dataclasses import FrozenInstanceError

import pytest

from duckov_game.domain import Inventory, ItemStack, LootItem


def test_same_items_stack_and_different_items_remain_separate() -> None:
    inventory = Inventory()
    assert inventory.total_count == 0
    assert inventory.quantity_of("scrap") == 0
    inventory.add("scrap", 2)
    inventory.add("wire", 3)
    inventory.add("scrap")
    assert inventory.total_count == 6
    assert inventory.entries == (ItemStack("scrap", 3), ItemStack("wire", 3))


def test_remove_updates_quantity_and_removes_empty_entry() -> None:
    inventory = Inventory()
    inventory.add("scrap", 3)
    inventory.remove("scrap", 2)
    assert inventory.quantity_of("scrap") == 1
    inventory.remove("scrap")
    assert inventory.entries == ()
    assert inventory.total_count == 0


def test_insufficient_removal_does_not_change_inventory() -> None:
    inventory = Inventory()
    inventory.add("scrap", 2)
    for item_id, quantity in (("scrap", 3), ("wire", 1)):
        with pytest.raises(ValueError, match="not enough"):
            inventory.remove(item_id, quantity)
        assert inventory.entries == (ItemStack("scrap", 2),)


@pytest.mark.parametrize("item_id", ["", " ", " scrap", "scrap ", None, 123])
def test_invalid_item_ids_are_rejected_without_mutation(item_id: object) -> None:
    inventory = Inventory()
    inventory.add("scrap", 1)
    for operation in (inventory.add, inventory.remove, inventory.quantity_of):
        with pytest.raises(ValueError, match="item_id"):
            operation(item_id)
    with pytest.raises(ValueError, match="item_id"):
        LootItem(0, 0, item_id=item_id)
    assert inventory.entries == (ItemStack("scrap"),)


@pytest.mark.parametrize("quantity", [0, -1, 1.5, True, "2", None])
def test_invalid_quantities_are_rejected_without_mutation(quantity: object) -> None:
    inventory = Inventory()
    inventory.add("scrap", 2)
    for operation in (inventory.add, inventory.remove):
        with pytest.raises(ValueError, match="quantity"):
            operation("scrap", quantity)
    with pytest.raises(ValueError, match="quantity"):
        LootItem(0, 0, quantity=quantity)
    assert inventory.entries == (ItemStack("scrap", 2),)


def test_entries_are_immutable_detached_sorted_snapshots() -> None:
    inventory = Inventory()
    inventory.add("wire", 2)
    inventory.add("scrap", 1)
    snapshot = inventory.entries
    assert snapshot == (ItemStack("scrap", 1), ItemStack("wire", 2))
    with pytest.raises(FrozenInstanceError):
        snapshot[0].quantity = 99
    inventory.add("scrap")
    assert snapshot[0].quantity == 1
    assert inventory.quantity_of("scrap") == 2


def test_transfer_merges_contents_clears_source_and_does_not_alias() -> None:
    backpack, stash = Inventory(), Inventory()
    backpack.add("scrap", 2)
    backpack.add("wire", 3)
    stash.add("scrap", 5)
    stash.add("food", 1)
    backpack.transfer_all_to(stash)
    expected = (ItemStack("food", 1), ItemStack("scrap", 7), ItemStack("wire", 3))
    assert stash.entries == expected
    assert backpack.entries == ()
    backpack.transfer_all_to(stash)
    assert stash.entries == expected
    backpack.add("scrap", 10)
    backpack.clear()
    assert stash.entries == expected


def test_self_transfer_is_rejected_without_losing_items() -> None:
    inventory = Inventory()
    inventory.add("scrap", 2)
    with pytest.raises(ValueError, match="itself"):
        inventory.transfer_all_to(inventory)
    assert inventory.entries == (ItemStack("scrap", 2),)
