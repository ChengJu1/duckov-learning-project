from __future__ import annotations

import pytest

from duckov_game.application import GameSession, RunStatus
from duckov_game.domain import Enemy, ExtractionZone, LootItem, Player, Projectile, WorldBounds


def make_session(
    *, player_x: float = 0, loot_x: float = 50, extraction_x: float = 150
) -> GameSession:
    return GameSession(
        bounds=WorldBounds(200, 100),
        player=Player(x=player_x, y=10, width=10, height=10, speed=100),
        loot_items=[LootItem(x=loot_x, y=10, width=10, height=10)],
        extraction_zone=ExtractionZone(
            x=extraction_x, y=10, width=20, height=20
        ),
    )


def test_item_is_not_collected_without_overlap() -> None:
    session = make_session()

    session.update(0, 0, 0)

    assert session.loot_items[0].is_collected is False
    assert session.carried_item_count == 0


def test_player_collects_item_after_moving_into_it() -> None:
    session = make_session()

    session.update(1, 0, 0.5)

    assert session.loot_items[0].is_collected is True
    assert session.carried_item_count == 1


def test_collected_item_cannot_be_counted_twice() -> None:
    session = make_session(player_x=50)

    session.update(0, 0, 0)
    session.update(0, 0, 0)

    assert session.loot_items[0].is_collected is True
    assert session.carried_item_count == 1


def test_touching_edges_does_not_count_as_overlap() -> None:
    session = make_session(player_x=40, loot_x=50)

    session.update(0, 0, 0)

    assert session.loot_items[0].is_collected is False
    assert session.carried_item_count == 0


def test_entering_extraction_zone_completes_run() -> None:
    session = make_session(player_x=120, loot_x=150, extraction_x=150)

    session.update(1, 0, 0.3)

    assert session.carried_item_count == 1
    assert session.status is RunStatus.EXTRACTED


def test_player_cannot_extract_without_loot() -> None:
    session = make_session(player_x=150, loot_x=50, extraction_x=150)

    session.update(0, 0, 0)

    assert session.carried_item_count == 0
    assert session.status is RunStatus.ACTIVE


def test_staying_outside_extraction_zone_keeps_run_active() -> None:
    session = make_session()

    session.update(0, 0, 0)

    assert session.status is RunStatus.ACTIVE


def test_extracted_run_no_longer_changes() -> None:
    session = make_session(player_x=150, loot_x=150, extraction_x=150)
    session.update(0, 0, 0)
    position_at_extraction = (session.player.x, session.player.y)

    session.update(-1, 0, 0.5)

    assert session.status is RunStatus.EXTRACTED
    assert (session.player.x, session.player.y) == position_at_extraction
    assert session.loot_items[0].is_collected is True
    assert session.carried_item_count == 1


def test_fire_request_creates_one_projectile_along_current_aim() -> None:
    session = make_session()

    session.update(0, 0, 0, aim_target=(5, 100), fire_requested=True)

    assert len(session.projectiles) == 1
    projectile = session.projectiles[0]
    assert (projectile.x, projectile.y) == (5, 15)
    assert projectile.direction_x == pytest.approx(0)
    assert projectile.direction_y == pytest.approx(1)


def test_no_fire_request_does_not_create_projectile() -> None:
    session = make_session()

    session.update(0, 0, 0)

    assert session.projectiles == []


def test_projectile_moves_and_is_removed_after_leaving_world() -> None:
    session = make_session()
    session.update(0, 0, 0, fire_requested=True)

    session.update(0, 0, 1)

    assert session.projectiles == []


def test_extracted_run_cannot_fire_projectiles() -> None:
    session = make_session(player_x=150, loot_x=150, extraction_x=150)
    session.update(0, 0, 0)

    session.update(0, 0, 0, fire_requested=True)

    assert session.status is RunStatus.EXTRACTED
    assert session.projectiles == []


def test_hit_consumes_projectile_and_deals_damage_only_once() -> None:
    session = make_session()
    session.enemy = Enemy(100, 10, width=10, height=10, speed=0)
    session.update(0, 0, 0.2, aim_target=(105, 15), fire_requested=True)
    assert session.enemy.health.current == 75
    assert session.projectiles == []
    session.update(0, 0, 0.2)
    assert session.enemy.health.current == 75


def test_projectile_hits_before_out_of_bounds_cleanup_even_during_long_frame() -> None:
    session = make_session()
    session.enemy = Enemy(100, 10, speed=0)
    session.update(0, 0, 1, fire_requested=True)
    assert session.enemy.health.current == 75
    assert session.projectiles == []


def test_miss_does_not_damage_enemy() -> None:
    session = make_session()
    session.enemy = Enemy(100, 50, speed=0)
    session.update(0, 0, 0.2, fire_requested=True)
    assert session.enemy.health.current == 100
    assert len(session.projectiles) == 1


def test_four_hits_defeat_enemy_and_dead_enemy_does_not_absorb_shots() -> None:
    session = make_session()
    session.enemy = Enemy(100, 10, speed=0)
    for expected_hp in (75, 50, 25, 0):
        session.update(0, 0, 0.2, fire_requested=True)
        assert session.enemy.health.current == expected_hp
        assert session.projectiles == []
    session.update(0, 0, 0.2, fire_requested=True)
    assert not session.enemy.health.is_alive
    assert len(session.projectiles) == 1


def test_same_frame_hits_stop_at_death() -> None:
    session = make_session()
    session.enemy = Enemy(100, 10, speed=0)
    session.enemy.health.take_damage(75)
    session.projectiles = [Projectile(5, 15, 1, 0), Projectile(5, 15, 1, 0)]
    session.update(0, 0, 0.2)
    assert session.enemy.health.current == 0
    assert len(session.projectiles) == 1


def test_live_enemy_does_not_block_extraction_and_combat_freezes_afterward() -> None:
    session = make_session(player_x=150, loot_x=150, extraction_x=150)
    session.enemy = Enemy(100, 10)
    session.projectiles = [Projectile(5, 15, 1, 0)]
    session.update(0, 0, 0)
    assert session.status is RunStatus.EXTRACTED
    session.update(0, 0, 1, fire_requested=True)
    assert session.enemy.health.current == 100
    assert len(session.projectiles) == 1
    assert session.projectiles[0].x == 5
    assert (session.enemy.x, session.enemy.y) == (100, 10)


def test_enemy_pursues_player_after_player_moves() -> None:
    session = make_session()
    session.enemy = Enemy(150, 10, width=10, height=10, speed=40, stopping_distance=10)
    session.update(1, 0, 0.5)
    assert session.player.x == 50
    assert session.enemy.x == pytest.approx(130)
    assert session.enemy.y == pytest.approx(10)


def test_enemy_killed_this_frame_does_not_take_a_final_step() -> None:
    session = make_session()
    session.enemy = Enemy(100, 10, width=10, height=10)
    session.enemy.health.take_damage(75)
    session.update(0, 0, 0.2, fire_requested=True)
    assert not session.enemy.health.is_alive
    assert (session.enemy.x, session.enemy.y) == (100, 10)
    session.update(1, 0, 0.1)
    assert (session.enemy.x, session.enemy.y) == (100, 10)


def test_moving_enemy_can_still_be_hit_four_times() -> None:
    session = make_session()
    session.enemy = Enemy(100, 10, width=10, height=10)
    for expected in (75, 50, 25, 0):
        target = session.enemy.center
        session.update(0, 0, 0.2, aim_target=target, fire_requested=True)
        assert session.enemy.health.current == expected
        assert session.projectiles == []
