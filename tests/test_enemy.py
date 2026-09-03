import pytest
from math import hypot

from duckov_game.domain import Enemy, Health, Rectangle, WorldBounds


def test_health_loses_damage_and_clamps_at_zero() -> None:
    health = Health(100)
    health.take_damage(25)
    assert health.current == 75
    assert health.is_alive
    health.take_damage(100)
    health.take_damage(25)
    assert health.current == 0
    assert not health.is_alive


def test_health_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="positive"):
        Health(0)
    with pytest.raises(ValueError, match="negative"):
        Health().take_damage(-1)


def test_enemies_have_independent_health_and_correct_hitboxes() -> None:
    first, second = Enemy(10, 20), Enemy(30, 40)
    first.health.take_damage(25)
    assert second.health.current == 100
    assert first.hitbox == Rectangle(10, 20, 36, 36)
    with pytest.raises(ValueError, match="size"):
        Enemy(0, 0, width=0)


@pytest.mark.parametrize("offset", [(500, 0), (0, 500), (300, 400), (-60, -80)])
def test_pursuit_has_same_speed_in_every_direction(offset: tuple[int, int]) -> None:
    enemy = Enemy(100, 100, speed=100)
    center_x, center_y = enemy.center
    target = (center_x + offset[0], center_y + offset[1])
    enemy.move_toward(target, 0.25, WorldBounds(1000, 1000))
    length = hypot(*offset)
    assert enemy.x == pytest.approx(100 + offset[0] / length * 25)
    assert enemy.y == pytest.approx(100 + offset[1] / length * 25)


def test_large_step_stops_at_distance_without_overshooting_or_jitter() -> None:
    enemy = Enemy(100, 100)
    target = (218, 118)
    bounds = WorldBounds(500, 500)
    enemy.move_toward(target, 10, bounds)
    assert enemy.center == pytest.approx((162, 118))
    position = (enemy.x, enemy.y)
    for _ in range(30):
        enemy.move_toward(target, 1 / 60, bounds)
    assert (enemy.x, enemy.y) == position


@pytest.mark.parametrize("target", [(118, 118), (130, 118)])
def test_close_or_overlapping_target_does_not_move_enemy(target: tuple[int, int]) -> None:
    enemy = Enemy(100, 100)
    enemy.move_toward(target, 1, WorldBounds(500, 500))
    assert (enemy.x, enemy.y) == (100, 100)


def test_enemy_resumes_pursuit_when_target_moves_away() -> None:
    enemy = Enemy(100, 100)
    bounds = WorldBounds(500, 500)
    enemy.move_toward((150, 118), 1, bounds)
    assert enemy.x == 100
    enemy.move_toward((300, 118), 0.5, bounds)
    assert enemy.x == pytest.approx(145)


def test_pursuit_is_independent_of_frame_count_for_fixed_target() -> None:
    single, many = Enemy(100, 100), Enemy(100, 100)
    target, bounds = (500, 600), WorldBounds(1000, 1000)
    single.move_toward(target, 1, bounds)
    for _ in range(60):
        many.move_toward(target, 1 / 60, bounds)
    assert many.center == pytest.approx(single.center)


@pytest.mark.parametrize(
    ("target", "expected"),
    [((-500, 48), (0, 30)), ((500, 48), (164, 30)),
     ((68, -500), (50, 0)), ((68, 500), (50, 64))],
)
def test_enemy_stays_fully_inside_bounds(
    target: tuple[int, int], expected: tuple[int, int]
) -> None:
    enemy = Enemy(50, 30, stopping_distance=0)
    enemy.move_toward(target, 100, WorldBounds(200, 100))
    assert (enemy.x, enemy.y) == pytest.approx(expected)


def test_dead_enemy_does_not_move() -> None:
    enemy = Enemy(100, 100)
    enemy.health.take_damage(100)
    enemy.move_toward((400, 400), 10, WorldBounds(500, 500))
    assert (enemy.x, enemy.y) == (100, 100)


def test_zero_speed_and_zero_time_do_not_move_enemy() -> None:
    for enemy, delta in ((Enemy(100, 100, speed=0), 1), (Enemy(100, 100), 0)):
        enemy.move_toward((400, 400), delta, WorldBounds(500, 500))
        assert (enemy.x, enemy.y) == (100, 100)


def test_pursuit_rejects_invalid_parameters() -> None:
    with pytest.raises(ValueError, match="speed"):
        Enemy(0, 0, speed=-1)
    with pytest.raises(ValueError, match="stopping_distance"):
        Enemy(0, 0, stopping_distance=-1)
    with pytest.raises(ValueError, match="delta_seconds"):
        Enemy(0, 0).move_toward((100, 100), -1, WorldBounds(200, 200))
    with pytest.raises(ValueError, match="fit"):
        Enemy(0, 0).move_toward((100, 100), 1, WorldBounds(20, 20))
