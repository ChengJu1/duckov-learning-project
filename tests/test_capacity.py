from dataclasses import asdict

import pytest

from duckov_game.app import WINDOW_SIZE, _create_session
from duckov_game.application import Game, RunStatus
from duckov_game.domain import Inventory, ItemStack, WorldBounds
from test_multi_loot import make_session


@pytest.mark.parametrize("capacity", [-1, True, 1.5, "3"])
def test_invalid_capacity(capacity: object) -> None:
    with pytest.raises(ValueError, match="capacity"):
        Inventory(capacity=capacity)


def test_capacity_counts_units_and_rejects_whole_bundle() -> None:
    inventory = Inventory(capacity=3)
    inventory.add("scrap", 2)
    assert not inventory.can_add("wire", 2)
    before = inventory.entries
    with pytest.raises(ValueError, match="capacity"):
        inventory.add("wire", 2)
    assert inventory.entries == before
    inventory.add("wire", 1)
    assert inventory.total_count == 3
    assert not inventory.can_add("scrap")
    inventory.remove("scrap", 1)
    assert inventory.can_add("wire")
    inventory.clear()
    assert inventory.capacity == 3
    assert inventory.can_add("wire", 3)


def test_zero_and_unlimited_capacity() -> None:
    assert not Inventory(capacity=0).can_add("scrap")
    stash = Inventory()
    stash.add("scrap", 1000)
    assert stash.total_count == 1000


def test_failed_transfer_preserves_both_inventories() -> None:
    source, target = Inventory(), Inventory(capacity=3)
    source.add("wire", 2)
    target.add("scrap", 2)
    before = source.entries, target.entries
    with pytest.raises(ValueError, match="capacity"):
        source.transfer_all_to(target)
    assert (source.entries, target.entries) == before
    target.remove("scrap")
    source.transfer_all_to(target)
    assert source.entries == ()
    assert target.entries == (ItemStack("scrap", 1), ItemStack("wire", 2))


def test_blocked_pickup_stays_and_can_be_retried_after_space_freed() -> None:
    session = make_session()
    session.backpack = Inventory(capacity=3)
    session.backpack.add("scrap", 2)
    session.update(1, 0, 1.3)
    assert session.pickup_blocked
    assert not session.loot_items[2].is_collected
    session.update(0, 0, 1)
    assert session.backpack.entries == (ItemStack("scrap", 2),)
    session.backpack.remove("scrap")
    session.update(0, 0, 0)
    assert not session.pickup_blocked
    assert session.loot_items[2].is_collected
    assert session.carried_item_count == 3


def test_leaving_rejected_pickup_clears_feedback() -> None:
    session = make_session()
    session.backpack = Inventory(capacity=0)
    session.update(1, 0, 0.3)
    assert session.pickup_blocked
    session.update(-1, 0, 0.3)
    assert not session.pickup_blocked


def test_overlapping_pickups_follow_list_order_and_keep_overflow() -> None:
    session = make_session()
    session.backpack = Inventory(capacity=3)
    for loot in session.loot_items:
        loot.x = session.player.x
    session.update(0, 0, 0)
    assert [loot.is_collected for loot in session.loot_items] == [True, True, False]
    assert session.backpack.entries == (ItemStack("scrap", 2),)


@pytest.mark.parametrize("failed", [False, True])
def test_full_backpack_settlement_and_restart(failed: bool) -> None:
    def factory():
        session = make_session()
        session.backpack = Inventory(capacity=3)
        return session

    game = Game(factory)
    fresh = asdict(game.session)
    game.stash.add("wire", 10)
    game.update(1, 0, 1.3)  # wire x2 first
    game.update(-1, 0, 0.5)  # scrap x1 fills the last unit
    assert game.session.carried_item_count == 3
    if failed:
        game.session.player.health.take_damage(100)
        game.update(0, 0, 0)
        assert game.session.status is RunStatus.FAILED
        assert game.stash.entries == (ItemStack("wire", 10),)
    else:
        game.update(1, 0, 1.6)
        assert game.session.status is RunStatus.EXTRACTED
        assert game.stash.entries == (ItemStack("scrap", 1), ItemStack("wire", 12))
    assert game.session.backpack.entries == ()
    assert game.start_new_run()
    assert asdict(game.session) == fresh


def test_default_map_uses_three_units_and_unlimited_stash() -> None:
    game = Game(lambda: _create_session(WorldBounds(*WINDOW_SIZE)))
    assert game.session.backpack.capacity == 3
    assert game.stash.capacity is None
