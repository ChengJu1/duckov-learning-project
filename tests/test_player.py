from __future__ import annotations

import pytest

from duckov_game.domain import Player, WorldBounds


def test_player_moves_right_using_pixels_per_second() -> None:
    player = Player(x=10, y=20, speed=100)

    player.move(1, 0, 0.5, WorldBounds(500, 500))

    assert player.x == pytest.approx(60)
    assert player.y == pytest.approx(20)


def test_diagonal_movement_does_not_increase_speed() -> None:
    player = Player(x=0, y=0, speed=100)

    player.move(1, 1, 1, WorldBounds(500, 500))

    assert player.x == pytest.approx(100 / 2**0.5)
    assert player.y == pytest.approx(100 / 2**0.5)


@pytest.mark.parametrize(
    ("start_x", "start_y", "direction_x", "direction_y", "expected_x", "expected_y"),
    [
        (1, 1, -1, -1, 0, 0),
        (67, 67, 1, 1, 68, 68),
    ],
)
def test_player_stays_fully_inside_world(
    start_x: float,
    start_y: float,
    direction_x: float,
    direction_y: float,
    expected_x: float,
    expected_y: float,
) -> None:
    player = Player(x=start_x, y=start_y, speed=100)

    player.move(direction_x, direction_y, 1, WorldBounds(100, 100))

    assert player.x == expected_x
    assert player.y == expected_y


def test_negative_delta_time_is_rejected() -> None:
    player = Player(x=10, y=10)

    with pytest.raises(ValueError, match="cannot be negative"):
        player.move(1, 0, -0.1, WorldBounds(100, 100))

