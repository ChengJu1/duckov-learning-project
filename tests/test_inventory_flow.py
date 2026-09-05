from duckov_game.application import Game, GameSession, RunStatus
from duckov_game.domain import ExtractionZone, ItemStack, LootItem, Player, WorldBounds


def make_session(item_id: str = "scrap", quantity: int = 1) -> GameSession:
    return GameSession(
        bounds=WorldBounds(200, 100),
        player=Player(0, 10, width=10, height=10, speed=100),
        loot_items=[LootItem(30, 10, width=10, height=10, item_id=item_id, quantity=quantity)],
        extraction_zone=ExtractionZone(150, 10, 20, 20),
    )


def test_pickup_preserves_identity_and_quantity_without_duplication() -> None:
    session = make_session("wire", 3)
    session.update(1, 0, 0.3)
    session.update(0, 0, 0)
    assert session.loot_items[0].is_collected
    assert session.backpack.entries == (ItemStack("wire", 3),)
    assert session.carried_item_count == 3


def test_multiple_item_types_settle_correctly_across_runs_and_survive_failure() -> None:
    drops = iter((ItemStack("scrap", 2), ItemStack("wire", 3), ItemStack("scrap", 1), ItemStack("wire", 4)))

    def factory() -> GameSession:
        drop = next(drops)
        return make_session(drop.item_id, drop.quantity)

    game = Game(session_factory=factory)
    expected_runs = (
        (ItemStack("scrap", 2),),
        (ItemStack("scrap", 2), ItemStack("wire", 3)),
        (ItemStack("scrap", 3), ItemStack("wire", 3)),
    )
    for expected in expected_runs:
        game.update(1, 0, 0.3)
        assert game.session.carried_item_count == game.session.loot_items[0].quantity
        game.update(1, 0, 1.2)
        assert game.session.status is RunStatus.EXTRACTED
        assert game.session.backpack.entries == ()
        assert game.stash.entries == expected
        assert game.stash_item_count == sum(entry.quantity for entry in expected)
        game.update(0, 0, 1)
        assert game.stash.entries == expected
        assert game.start_new_run()
        assert game.session.backpack.entries == ()

    game.update(1, 0, 0.3)
    assert game.session.backpack.entries == (ItemStack("wire", 4),)
    game.session.player.health.take_damage(100)
    game.update(0, 0, 0)
    assert game.session.status is RunStatus.FAILED
    assert game.session.backpack.entries == ()
    assert game.stash.entries == expected_runs[-1]


def test_success_moves_all_types_not_only_the_last_pickup() -> None:
    game = Game(session_factory=make_session)
    game.stash.add("wire", 5)
    game.session.backpack.add("wire", 2)
    game.update(1, 0, 0.3)
    assert game.session.carried_item_count == 3
    game.update(1, 0, 1.2)
    assert game.stash.entries == (ItemStack("scrap", 1), ItemStack("wire", 7))
    old_backpack = game.session.backpack
    assert game.start_new_run()
    assert game.session.backpack is not old_backpack
    assert game.session.backpack is not game.stash
    old_backpack.add("scrap", 100)
    assert game.session.backpack.entries == ()
    assert game.stash.quantity_of("scrap") == 1


def test_death_clears_all_backpack_types_but_not_stash() -> None:
    game = Game(session_factory=make_session)
    game.stash.add("wire", 7)
    game.session.backpack.add("scrap", 2)
    game.session.backpack.add("wire", 3)
    game.session.player.health.take_damage(100)
    game.update(0, 0, 0)
    assert game.session.backpack.entries == ()
    assert game.stash.entries == (ItemStack("wire", 7),)
    assert game.start_new_run()
    assert game.session.backpack.entries == ()
    assert game.stash.entries == (ItemStack("wire", 7),)


def test_empty_backpack_cannot_extract_and_instances_do_not_share_inventory() -> None:
    first, second = make_session(), make_session()
    first.update(1, 0, 1.5)
    assert first.player.x == 150
    assert first.status is RunStatus.ACTIVE
    first.backpack.add("wire", 2)
    assert second.backpack.total_count == 0
    game_one, game_two = Game(make_session), Game(make_session)
    game_one.stash.add("scrap", 2)
    assert game_two.stash.total_count == 0
