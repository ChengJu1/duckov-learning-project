from __future__ import annotations

from duckov_game.application import GameSession
from duckov_game.domain import LootItem, Player, WorldBounds


def make_session(*, player_x: float = 0, loot_x: float = 50) -> GameSession:
    return GameSession(
        bounds=WorldBounds(200, 100),
        player=Player(x=player_x, y=10, width=10, height=10, speed=100),
        loot_item=LootItem(x=loot_x, y=10, width=10, height=10),
    )


def test_item_is_not_collected_without_overlap() -> None:
    session = make_session()

    session.update(0, 0, 0)

    assert session.loot_item.is_collected is False
    assert session.carried_item_count == 0


def test_player_collects_item_after_moving_into_it() -> None:
    session = make_session()

    session.update(1, 0, 0.5)

    assert session.loot_item.is_collected is True
    assert session.carried_item_count == 1


def test_collected_item_cannot_be_counted_twice() -> None:
    session = make_session(player_x=50)

    session.update(0, 0, 0)
    session.update(0, 0, 0)

    assert session.loot_item.is_collected is True
    assert session.carried_item_count == 1


def test_touching_edges_does_not_count_as_overlap() -> None:
    session = make_session(player_x=40, loot_x=50)

    session.update(0, 0, 0)

    assert session.loot_item.is_collected is False
    assert session.carried_item_count == 0

