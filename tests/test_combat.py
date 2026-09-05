"""Attack timing, death priority, and both run settlement paths."""

from dataclasses import asdict

import pytest

from duckov_game.application import Game, GameSession, RunStatus
from duckov_game.domain import Enemy, ExtractionZone, LootItem, Player, Projectile, WorldBounds


def make_combat_session() -> GameSession:
    return GameSession(
        bounds=WorldBounds(240, 160),
        player=Player(20, 60, width=10, height=10, speed=100),
        enemy=Enemy(60, 60, width=10, height=10, speed=0),
        loot_items=[LootItem(100, 60, width=10, height=10)],
        extraction_zone=ExtractionZone(180, 60, width=20, height=20),
    )


def test_player_and_enemy_health_are_independent() -> None:
    first, second, enemy = Player(0, 0), Player(0, 0), Enemy(0, 0)
    first.health.take_damage(20)
    assert first.health.current == 80
    assert second.health.current == enemy.health.current == 100


def test_attack_requires_full_interval_and_repeats() -> None:
    session = make_combat_session()
    session.update(0, 0, 0)
    session.update(0, 0, 0.99)
    assert session.player.health.current == 100
    assert session.enemy is not None
    assert session.enemy.attack_progress == pytest.approx(0.99)
    session.update(0, 0, 0.01)
    assert session.player.health.current == 80
    assert session.enemy.attack_progress == pytest.approx(0)
    session.update(0, 0, 1)
    assert session.player.health.current == 60


@pytest.mark.parametrize("frame_count", [1, 10, 30, 60, 120])
def test_stationary_attack_timing_does_not_depend_on_frame_count(frame_count: int) -> None:
    session = make_combat_session()
    for _ in range(frame_count):
        session.update(0, 0, 2 / frame_count)
    assert session.player.health.current == 60
    assert session.enemy is not None
    assert session.enemy.attack_progress == pytest.approx(0)


def test_large_step_preserves_partial_attack_interval() -> None:
    session = make_combat_session()
    session.update(0, 0, 2.5)
    assert session.player.health.current == 60
    session.update(0, 0, 0.5)
    assert session.player.health.current == 40


def test_leaving_range_cancels_windup_and_return_requires_full_interval() -> None:
    session = make_combat_session()
    session.update(0, 0, 0.9)
    session.player.x = 200
    session.update(0, 0, 10)
    assert session.player.health.current == 100
    assert session.enemy is not None
    assert session.enemy.attack_progress == 0
    session.player.x = 20
    session.update(0, 0, 0.9)
    assert session.player.health.current == 100
    session.update(0, 0, 0.1)
    assert session.player.health.current == 80


@pytest.mark.parametrize(("distance", "health"), [(64, 80), (64.01, 100), (0, 80)])
def test_attack_range_uses_center_distance(distance: float, health: int) -> None:
    session = make_combat_session()
    assert session.enemy is not None
    session.enemy.x = session.player.x + distance
    session.update(0, 0, 1)
    assert session.player.health.current == health


def test_approach_time_is_not_counted_as_time_already_in_range() -> None:
    session = make_combat_session()
    assert session.enemy is not None
    session.enemy.x = 180
    session.enemy.speed = 90
    session.update(0, 0, 10)
    assert session.player.health.current == 100
    assert session.enemy.attack_progress == 0
    session.update(0, 0, 1)
    assert session.player.health.current == 80


def test_dead_enemy_cannot_attack() -> None:
    session = make_combat_session()
    assert session.enemy is not None
    session.enemy.health.take_damage(100)
    session.update(0, 0, 10)
    assert session.player.health.current == 100


def test_enemy_killed_by_projectile_cannot_attack_on_same_frame() -> None:
    session = make_combat_session()
    assert session.enemy is not None
    session.enemy.health.take_damage(75)
    session.player.health.take_damage(80)
    session.update(0, 0, 0.9)
    session.update(0, 0, 0.1, aim_target=session.enemy.center, fire_requested=True)
    assert not session.enemy.health.is_alive
    assert session.player.health.current == 20
    assert session.status is RunStatus.ACTIVE


def test_dead_target_does_not_receive_attacks() -> None:
    session = make_combat_session()
    assert session.enemy is not None
    session.player.health.take_damage(100)
    session.enemy.attack(session.player, 10)
    assert session.player.health.current == 0
    assert session.enemy.attack_progress == 0


def test_death_discards_carried_loot_and_freezes_all_session_state() -> None:
    session = make_combat_session()
    session.backpack.add("scrap", 1)
    session.loot_items[0].is_collected = True
    session.projectiles.append(Projectile(20, 140, 1, 0, speed=0))
    session.update(0, 0, 5)
    assert session.status is RunStatus.FAILED
    assert session.player.health.current == 0
    assert session.carried_item_count == 0
    frozen = asdict(session)
    session.update(1, 1, 10, aim_target=(0, 0), fire_requested=True)
    assert asdict(session) == frozen


def test_player_dead_at_frame_start_cannot_move_fire_or_pick_up() -> None:
    session = make_combat_session()
    session.player.health.take_damage(100)
    session.update(1, 0, 1, fire_requested=True)
    assert session.status is RunStatus.FAILED
    assert session.player.x == 20
    assert session.projectiles == []
    assert not session.loot_items[0].is_collected


def test_lethal_attack_prevents_pickup_on_same_frame() -> None:
    session = make_combat_session()
    session.loot_items[0].x = session.player.x
    session.player.health.take_damage(80)
    session.update(0, 0, 1)
    assert session.status is RunStatus.FAILED
    assert not session.loot_items[0].is_collected


def test_death_at_extraction_never_adds_to_or_reduces_stash() -> None:
    game = Game(session_factory=make_combat_session)
    game.stash.add("scrap", 7)
    game.session.backpack.add("scrap", 1)
    game.session.extraction_zone = ExtractionZone(20, 60, 20, 20)
    game.session.player.health.take_damage(80)
    game.update(0, 0, 1)
    assert game.session.status is RunStatus.FAILED
    assert game.stash_item_count == 7
    for _ in range(3):
        game.update(0, 0, 1)
    assert game.stash_item_count == 7


def test_surviving_attack_can_extract_and_then_freezes_health_and_stash() -> None:
    game = Game(session_factory=make_combat_session)
    game.stash.add("scrap", 7)
    game.session.backpack.add("scrap", 1)
    game.session.extraction_zone = ExtractionZone(20, 60, 20, 20)
    game.update(0, 0, 1)
    assert game.session.player.health.current == 80
    assert game.session.status is RunStatus.EXTRACTED
    assert game.stash_item_count == 8
    frozen = asdict(game.session)
    game.update(1, 0, 10, fire_requested=True)
    assert asdict(game.session) == frozen
    assert game.stash_item_count == 8
    assert game.start_new_run()
    assert game.session.player.health.current == 100
    assert game.stash_item_count == 8


def test_failed_run_restart_restores_health_position_loot_and_attack_timer() -> None:
    game = Game(session_factory=make_combat_session)
    game.stash.add("scrap", 7)
    old_session = game.session
    old_session.backpack.add("scrap", 1)
    old_session.loot_items[0].is_collected = True
    old_session.player.x = 30
    assert old_session.enemy is not None
    old_session.enemy.health.take_damage(25)
    old_session.projectiles.append(Projectile(0, 140, 1, 0, speed=0))
    game.update(0, 0, 5.3)
    assert game.start_new_run()
    session = game.session
    assert session is not old_session
    assert session.status is RunStatus.ACTIVE
    assert session.player.health.current == 100
    assert (session.player.x, session.player.y) == (20, 60)
    assert session.enemy is not None
    assert session.enemy.health.current == 100
    assert (session.enemy.x, session.enemy.y) == (60, 60)
    assert session.enemy.attack_progress == 0
    assert session.projectiles == []
    assert not session.loot_items[0].is_collected
    assert session.carried_item_count == 0
    assert game.stash_item_count == 7
    game.update(0, 0, 0.99)
    assert session.player.health.current == 100
    assert not game.start_new_run()


def test_attack_rejects_invalid_parameters() -> None:
    with pytest.raises(ValueError, match="attack_damage"):
        Enemy(0, 0, attack_damage=0)
    with pytest.raises(ValueError, match="attack_interval"):
        Enemy(0, 0, attack_interval=0)
    with pytest.raises(ValueError, match="attack_range"):
        Enemy(0, 0, attack_range=-1)
    with pytest.raises(ValueError, match="delta_seconds"):
        Enemy(0, 0).attack(Player(0, 0), -1)
