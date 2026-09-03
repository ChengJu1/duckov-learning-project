import pytest

from duckov_game.domain import Enemy, Health, Rectangle


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
