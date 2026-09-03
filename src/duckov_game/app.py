"""Window lifecycle for the first executable milestone."""

from __future__ import annotations

import pygame

from duckov_game.application import Game, GameSession, RunStatus
from duckov_game.domain import Enemy, ExtractionZone, Inventory, LootItem, Player, WorldBounds

WINDOW_SIZE = (960, 540)
WINDOW_TITLE = "Duckov Learning Project"
BACKGROUND_COLOR = (28, 32, 40)
PLAY_AREA_COLOR = (46, 52, 64)
PLAY_AREA_BORDER_COLOR = (100, 112, 132)
PLAYER_COLOR = (245, 193, 66)
AIM_COLOR = (255, 239, 170)
PROJECTILE_COLOR = (255, 246, 205)
ENEMY_COLOR = (225, 85, 85)
ATTACK_COLOR = (255, 155, 70)
LOOT_COLOR = (72, 201, 176)
EXTRACTION_COLOR = (76, 156, 255)
SUCCESS_COLOR = (143, 227, 136)
TEXT_COLOR = (225, 230, 238)
TARGET_FPS = 60
PLAYER_SIZE = 32.0
PLAYER_SPEED = 240.0
ENEMY_SPEED = 90.0
LOOT_SIZE = 24.0
EXTRACTION_SIZE = (64.0, 112.0)
AIM_LINE_LENGTH = 48.0


def _inventory_summary(inventory: Inventory) -> str:
    return ", ".join(f"{entry.item_id} x{entry.quantity}" for entry in inventory.entries) or "empty"


def _read_movement_direction(keys: pygame.key.ScancodeWrapper) -> tuple[int, int]:
    direction_x = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(
        keys[pygame.K_a] or keys[pygame.K_LEFT]
    )
    direction_y = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(
        keys[pygame.K_w] or keys[pygame.K_UP]
    )
    return direction_x, direction_y


def _create_session(world_bounds: WorldBounds) -> GameSession:
    return GameSession(
        bounds=world_bounds,
        player=Player(
            x=(world_bounds.width - PLAYER_SIZE) / 2,
            y=(world_bounds.height - PLAYER_SIZE) / 2,
            width=PLAYER_SIZE,
            height=PLAYER_SIZE,
            speed=PLAYER_SPEED,
        ),
        loot_item=LootItem(
            x=world_bounds.width * 0.75,
            y=(world_bounds.height - LOOT_SIZE) / 2,
            width=LOOT_SIZE,
            height=LOOT_SIZE,
            item_id="scrap",
            quantity=1,
        ),
        extraction_zone=ExtractionZone(
            x=40,
            y=(world_bounds.height - EXTRACTION_SIZE[1]) / 2,
            width=EXTRACTION_SIZE[0],
            height=EXTRACTION_SIZE[1],
        ),
        enemy=Enemy(
            x=world_bounds.width * 0.72,
            y=world_bounds.height * 0.32,
            speed=ENEMY_SPEED,
        ),
    )


def run(*, max_frames: int | None = None) -> int:
    """Run the game window.

    ``max_frames`` exists for automated smoke tests. Normal runs leave it as
    ``None`` and continue until the user closes the window.
    """

    if max_frames is not None and max_frames < 1:
        raise ValueError("max_frames must be at least 1")

    pygame.init()
    try:
        screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption(WINDOW_TITLE)
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 28)
        world_bounds = WorldBounds(*WINDOW_SIZE)
        game = Game(session_factory=lambda: _create_session(world_bounds))
        frame_count = 0
        running = True
        damage_flash_seconds = 0.0

        while running:
            delta_seconds = clock.tick(TARGET_FPS) / 1000.0
            fire_requested = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    if game.start_new_run():
                        damage_flash_seconds = 0.0
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    fire_requested = True

            direction_x, direction_y = _read_movement_direction(
                pygame.key.get_pressed()
            )
            previous_health = game.session.player.health.current
            game.update(
                direction_x,
                direction_y,
                delta_seconds,
                aim_target=pygame.mouse.get_pos(),
                fire_requested=fire_requested,
            )
            session = game.session
            damage_flash_seconds = max(0.0, damage_flash_seconds - delta_seconds)
            if session.player.health.current < previous_health:
                damage_flash_seconds = 0.15

            screen.fill(BACKGROUND_COLOR)
            pygame.draw.rect(screen, PLAY_AREA_COLOR, screen.get_rect())
            pygame.draw.rect(
                screen, PLAY_AREA_BORDER_COLOR, screen.get_rect(), width=4
            )
            if session.enemy is not None and session.enemy.health.is_alive:
                enemy = session.enemy
                enemy_rect = pygame.Rect(
                    round(enemy.x), round(enemy.y), round(enemy.width), round(enemy.height)
                )
                pygame.draw.rect(screen, ENEMY_COLOR, enemy_rect)
                pygame.draw.rect(
                    screen, BACKGROUND_COLOR,
                    pygame.Rect(enemy_rect.x, enemy_rect.y - 10, enemy_rect.width, 6),
                )
                pygame.draw.rect(
                    screen, SUCCESS_COLOR,
                    pygame.Rect(
                        enemy_rect.x, enemy_rect.y - 10,
                        round(enemy_rect.width * enemy.health.current / enemy.health.maximum), 6,
                    ),
                )
                pygame.draw.rect(
                    screen, ATTACK_COLOR,
                    pygame.Rect(
                        enemy_rect.x, enemy_rect.y - 16,
                        round(enemy_rect.width * enemy.attack_progress), 4,
                    ),
                )
            pygame.draw.rect(
                screen,
                EXTRACTION_COLOR,
                pygame.Rect(
                    round(session.extraction_zone.x),
                    round(session.extraction_zone.y),
                    round(session.extraction_zone.width),
                    round(session.extraction_zone.height),
                ),
                width=4,
            )
            pygame.draw.rect(
                screen,
                ENEMY_COLOR if damage_flash_seconds > 0 else PLAYER_COLOR,
                pygame.Rect(
                    round(session.player.x),
                    round(session.player.y),
                    round(session.player.width),
                    round(session.player.height),
                ),
            )
            player_center_x, player_center_y = session.player.center
            pygame.draw.line(
                screen,
                AIM_COLOR,
                (round(player_center_x), round(player_center_y)),
                (
                    round(player_center_x + session.player.aim_x * AIM_LINE_LENGTH),
                    round(player_center_y + session.player.aim_y * AIM_LINE_LENGTH),
                ),
                width=4,
            )
            for projectile in session.projectiles:
                pygame.draw.circle(
                    screen,
                    PROJECTILE_COLOR,
                    (round(projectile.x), round(projectile.y)),
                    round(projectile.radius),
                )
            if not session.loot_item.is_collected:
                pygame.draw.rect(
                    screen,
                    LOOT_COLOR,
                    pygame.Rect(
                        round(session.loot_item.x),
                        round(session.loot_item.y),
                        round(session.loot_item.width),
                        round(session.loot_item.height),
                    ),
                )
            instructions = font.render(
                "WASD move | Mouse aim | Left click fire | Collect then extract",
                True,
                TEXT_COLOR,
            )
            screen.blit(instructions, (16, 16))
            carried_text = font.render(
                f"Carried items: {session.carried_item_count} ({_inventory_summary(session.backpack)})",
                True, TEXT_COLOR,
            )
            screen.blit(carried_text, (16, 48))
            stash_text = font.render(
                f"Stash items: {game.stash_item_count} ({_inventory_summary(game.stash)})",
                True, TEXT_COLOR,
            )
            screen.blit(stash_text, (16, 80))
            if session.enemy is not None:
                health = session.enemy.health
                enemy_text = font.render(
                    f"Enemy HP: {health.current}/{health.maximum}"
                    if health.is_alive else "Enemy defeated",
                    True, TEXT_COLOR,
                )
                screen.blit(enemy_text, (16, 112))
            player_health = session.player.health
            player_health_text = font.render(
                f"Player HP: {player_health.current}/{player_health.maximum}",
                True, TEXT_COLOR,
            )
            screen.blit(player_health_text, (16, 144))
            pygame.draw.rect(screen, BACKGROUND_COLOR, pygame.Rect(16, 172, 160, 8))
            pygame.draw.rect(
                screen, SUCCESS_COLOR,
                pygame.Rect(16, 172, round(160 * player_health.current / player_health.maximum), 8),
            )
            attack_hint = font.render(
                "Keep your distance! Orange bar = enemy attack wind-up", True, TEXT_COLOR
            )
            screen.blit(attack_hint, (16, WINDOW_SIZE[1] - 28))
            if session.status is RunStatus.EXTRACTED:
                success_text = font.render(
                    "EXTRACTION SUCCESS - press R for a new run",
                    True,
                    SUCCESS_COLOR,
                )
                success_rect = success_text.get_rect(
                    center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 48)
                )
                screen.blit(success_text, success_rect)
            elif session.status is RunStatus.FAILED:
                failure_text = font.render(
                    "YOU DIED - carried loot lost - press R for a new run",
                    True, ENEMY_COLOR,
                )
                failure_rect = failure_text.get_rect(
                    center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 48)
                )
                screen.blit(failure_text, failure_rect)
            pygame.display.flip()

            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                running = False
    finally:
        pygame.quit()

    return 0
