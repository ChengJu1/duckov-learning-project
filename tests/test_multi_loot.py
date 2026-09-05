from dataclasses import asdict

import pytest

from duckov_game.app import WINDOW_SIZE, _create_session
from duckov_game.application import Game, GameSession, RunStatus
from duckov_game.domain import ExtractionZone, ItemStack, LootItem, Player, WorldBounds


def make_session() -> GameSession:
    return GameSession(
        bounds=WorldBounds(300, 200),
        player=Player(0, 50, width=10, height=10, speed=100),
        loot_items=[
            LootItem(30, 50, item_id="scrap"),
            LootItem(80, 50, item_id="scrap"),
            LootItem(130, 50, item_id="wire", quantity=2),
        ],
        extraction_zone=ExtractionZone(240, 50, 30, 30),
    )


def collect_all(game: Game) -> None:
    for step in (0.3, 0.5, 0.5):
        game.update(1, 0, step)
    assert game.session.backpack.entries == (ItemStack("scrap", 2), ItemStack("wire", 2))


def test_independent_pickups_stack_and_cannot_repeat() -> None:
    game = Game(make_session)
    game.update(1, 0, 0.3)
    assert [loot.is_collected for loot in game.session.loot_items] == [True, False, False]
    game.update(0, 0, 1)
    assert game.session.carried_item_count == 1
    game.update(1, 0, 0.5)
    assert game.session.backpack.entries == (ItemStack("scrap", 2),)
    game.update(1, 0, 0.5)
    game.update(-1, 0, 1)
    assert game.session.carried_item_count == 4
    assert game.session.backpack.quantity_of("wire") == 2


def test_all_items_settle_once_and_restart_restores_each_pickup() -> None:
    game = Game(make_session)
    fresh = asdict(game.session)
    for count in (2, 4):
        collect_all(game)
        game.update(1, 0, 1.1)
        assert game.session.status is RunStatus.EXTRACTED
        assert game.stash.entries == (ItemStack("scrap", count), ItemStack("wire", count))
        game.update(1, 0, 10)
        assert game.stash_item_count == count * 2
        assert game.start_new_run()
        assert asdict(game.session) == fresh


def test_partial_loot_is_enough_to_extract() -> None:
    game = Game(make_session)
    game.update(1, 0, 0.3)
    game.update(1, 0, 2.1)
    assert game.session.status is RunStatus.EXTRACTED
    assert game.stash.entries == (ItemStack("scrap", 1),)
    assert [loot.is_collected for loot in game.session.loot_items] == [True, False, False]


def test_death_loses_all_types_and_restart_restores_pickups() -> None:
    game = Game(make_session)
    game.stash.add("wire", 5)
    fresh = asdict(game.session)
    collect_all(game)
    game.session.player.health.take_damage(100)
    game.update(0, 0, 0)
    assert game.session.status is RunStatus.FAILED
    assert game.session.backpack.entries == ()
    assert game.stash.entries == (ItemStack("wire", 5),)
    assert game.start_new_run()
    assert asdict(game.session) == fresh


def test_overlapping_pickups_are_each_collected_once() -> None:
    session = make_session()
    for loot in session.loot_items:
        loot.x = session.player.x
    session.update(0, 0, 0)
    session.update(0, 0, 0)
    assert session.backpack.entries == (ItemStack("scrap", 2), ItemStack("wire", 2))


def test_empty_map_cannot_extract() -> None:
    session = make_session()
    session.loot_items.clear()
    session.update(1, 0, 2.4)
    assert session.status is RunStatus.ACTIVE


@pytest.mark.parametrize("fps", [30, 60, 120])
def test_real_map_all_pickups_then_extraction(fps: int) -> None:
    game = Game(lambda: _create_session(WorldBounds(*WINDOW_SIZE)))
    # Reuse the existing movement harness, which only submits application inputs.
    from test_stage_two import walk_to

    enemy = game.session.enemy
    assert enemy is not None
    for frame in range(fps * 10):
        if not enemy.health.is_alive:
            break
        game.update(0, 0, 1 / fps, aim_target=enemy.center, fire_requested=frame % 5 == 0)
    assert not enemy.health.is_alive
    for loot in game.session.loot_items:
        walk_to(game, loot.hitbox, 1 / fps)
    assert all(loot.is_collected for loot in game.session.loot_items)
    assert game.session.backpack.entries == (ItemStack("scrap", 2), ItemStack("wire", 2))
    walk_to(game, game.session.extraction_zone.hitbox, 1 / fps)
    assert game.session.status is RunStatus.EXTRACTED
    assert game.stash.entries == (ItemStack("scrap", 2), ItemStack("wire", 2))
