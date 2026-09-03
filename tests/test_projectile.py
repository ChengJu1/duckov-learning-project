from __future__ import annotations

import pytest

from duckov_game.domain import Projectile, Rectangle, WorldBounds


def test_projectile_normalizes_direction_and_moves_at_fixed_speed() -> None:
    projectile = Projectile(
        x=10,
        y=20,
        direction_x=3,
        direction_y=4,
        speed=100,
    )

    projectile.move(0.5)

    assert projectile.x == pytest.approx(40)
    assert projectile.y == pytest.approx(60)


def test_projectile_remains_until_it_fully_leaves_world() -> None:
    bounds = WorldBounds(100, 80)

    assert Projectile(104, 40, 1, 0, radius=5).intersects(bounds) is True
    assert Projectile(106, 40, 1, 0, radius=5).intersects(bounds) is False


def test_projectile_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="direction"):
        Projectile(0, 0, 0, 0)
    with pytest.raises(ValueError, match="speed"):
        Projectile(0, 0, 1, 0, speed=-1)
    with pytest.raises(ValueError, match="radius"):
        Projectile(0, 0, 1, 0, radius=0)
    with pytest.raises(ValueError, match="delta_seconds"):
        Projectile(0, 0, 1, 0).move(-0.1)
    with pytest.raises(ValueError, match="damage"):
        Projectile(0, 0, 1, 0, damage=-1)


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        ((0, 55), (200, 55), True),
        ((200, 55), (0, 55), True),
        ((55, 0), (55, 200), True),
        ((55, 200), (55, 0), True),
        ((0, 0), (100, 100), True),
        ((55, 55), (55, 55), True),
        ((0, 0), (0, 0), False),
        ((0, 44), (200, 44), False),
        ((0, 45), (200, 45), True),
        ((0, 0), (40, 40), False),
        ((70, 70), (100, 100), False),
        ((0, 100), (100, 200), False),
    ],
)
def test_swept_projectile_hitbox(
    start: tuple[float, float], end: tuple[float, float], expected: bool
) -> None:
    projectile = Projectile(*end, 1, 0)
    assert projectile.hits(Rectangle(50, 50, 10, 10), start) is expected
