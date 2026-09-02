from __future__ import annotations

from duckov_game.application import Game, GameSession, RunStatus
from duckov_game.domain import ExtractionZone, LootItem, Player, WorldBounds


def make_extractable_session() -> GameSession:
    return GameSession(
        bounds=WorldBounds(200, 100),
        player=Player(x=50, y=10, width=10, height=10),
        loot_item=LootItem(x=50, y=10, width=10, height=10),
        extraction_zone=ExtractionZone(x=50, y=10, width=20, height=20),
    )


def make_active_session() -> GameSession:
    return GameSession(
        bounds=WorldBounds(200, 100),
        player=Player(x=0, y=10, width=10, height=10),
        loot_item=LootItem(x=50, y=10, width=10, height=10),
        extraction_zone=ExtractionZone(x=150, y=10, width=20, height=20),
    )


def test_extraction_moves_carried_item_to_stash() -> None:
    game = Game(session_factory=make_extractable_session)

    game.update(0, 0, 0)

    assert game.session.status is RunStatus.EXTRACTED
    assert game.session.carried_item_count == 0
    assert game.stash_item_count == 1


def test_completed_run_is_not_settled_twice() -> None:
    game = Game(session_factory=make_extractable_session)

    game.update(0, 0, 0)
    game.update(0, 0, 0)

    assert game.stash_item_count == 1


def test_new_run_restores_session_and_preserves_stash() -> None:
    game = Game(session_factory=make_extractable_session)
    game.update(0, 0, 0)
    completed_session = game.session

    started = game.start_new_run()

    assert started is True
    assert game.session is not completed_session
    assert game.session.status is RunStatus.ACTIVE
    assert game.session.loot_item.is_collected is False
    assert game.session.carried_item_count == 0
    assert game.stash_item_count == 1


def test_active_run_cannot_be_restarted() -> None:
    game = Game(session_factory=make_active_session)
    active_session = game.session

    started = game.start_new_run()

    assert started is False
    assert game.session is active_session
    assert game.stash_item_count == 0

