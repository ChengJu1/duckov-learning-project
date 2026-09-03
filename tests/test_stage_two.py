"""Multi-run regression using the real game factory, without changing state directly."""

from dataclasses import asdict
from math import hypot

import pytest

from duckov_game.app import WINDOW_SIZE, _create_session
from duckov_game.application import Game, RunStatus
from duckov_game.domain import Rectangle, WorldBounds


def walk_to(game: Game, destination: Rectangle, delta: float) -> None:
    target = (destination.x + destination.width / 2, destination.y + destination.height / 2)
    for _ in range(int(15 / delta)):
        if game.session.status is not RunStatus.ACTIVE:
            return
        center_x, center_y = game.session.player.center
        dx, dy = target[0] - center_x, target[1] - center_y
        distance = hypot(dx, dy)
        if distance < 1e-6:
            return
        game.update(dx, dy, min(delta, distance / game.session.player.speed))
    pytest.fail("player did not reach the destination within 15 simulated seconds")


def win_run(game: Game, delta: float) -> None:
    enemy = game.session.enemy
    assert enemy is not None
    for frame in range(int(10 / delta)):
        if not enemy.health.is_alive:
            break
        game.update(
            0, 0, delta,
            aim_target=enemy.center,
            fire_requested=frame % max(1, round(0.15 / delta)) == 0,
        )
    assert not enemy.health.is_alive
    assert game.session.status is RunStatus.ACTIVE
    walk_to(game, game.session.loot_item.hitbox, delta)
    assert game.session.carried_item_count == 1
    walk_to(game, game.session.extraction_zone.hitbox, delta)
    assert game.session.status is RunStatus.EXTRACTED
    assert game.session.carried_item_count == 0


def assert_finished_run_is_frozen(game: Game) -> None:
    snapshot, stash = asdict(game.session), game.stash_item_count
    game.update(1, 1, 10, aim_target=(0, 0), fire_requested=True)
    assert asdict(game.session) == snapshot
    assert game.stash_item_count == stash


@pytest.mark.parametrize("fps", [30, 60, 120])
def test_default_game_win_loss_win_cycle(fps: int) -> None:
    delta = 1 / fps
    game = Game(session_factory=lambda: _create_session(WorldBounds(*WINDOW_SIZE)))
    fresh_state = asdict(game.session)
    assert game.stash_item_count == 0
    assert not game.start_new_run()

    win_run(game, delta)
    assert game.stash_item_count == 1
    assert_finished_run_is_frozen(game)

    assert game.start_new_run()
    assert asdict(game.session) == fresh_state
    walk_to(game, game.session.loot_item.hitbox, delta)
    assert game.session.carried_item_count == 1
    for _ in range(int(15 / delta)):
        game.update(0, 0, delta)
        if game.session.status is RunStatus.FAILED:
            break
    assert game.session.status is RunStatus.FAILED
    assert game.session.player.health.current == 0
    assert game.session.carried_item_count == 0
    assert game.stash_item_count == 1
    assert_finished_run_is_frozen(game)

    assert game.start_new_run()
    assert asdict(game.session) == fresh_state
    assert game.stash_item_count == 1
    win_run(game, delta)
    assert game.stash_item_count == 2
    assert_finished_run_is_frozen(game)
