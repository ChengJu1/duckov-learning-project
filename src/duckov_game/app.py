"""Window lifecycle for the first executable milestone."""

from __future__ import annotations

import pygame

from duckov_game.domain import Player, WorldBounds

WINDOW_SIZE = (960, 540)
WINDOW_TITLE = "Duckov Learning Project"
BACKGROUND_COLOR = (28, 32, 40)
PLAY_AREA_COLOR = (46, 52, 64)
PLAY_AREA_BORDER_COLOR = (100, 112, 132)
PLAYER_COLOR = (245, 193, 66)
TEXT_COLOR = (225, 230, 238)
TARGET_FPS = 60
PLAYER_SIZE = 32.0
PLAYER_SPEED = 240.0


def _read_movement_direction(keys: pygame.key.ScancodeWrapper) -> tuple[int, int]:
    direction_x = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(
        keys[pygame.K_a] or keys[pygame.K_LEFT]
    )
    direction_y = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(
        keys[pygame.K_w] or keys[pygame.K_UP]
    )
    return direction_x, direction_y


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
        player = Player(
            x=(world_bounds.width - PLAYER_SIZE) / 2,
            y=(world_bounds.height - PLAYER_SIZE) / 2,
            width=PLAYER_SIZE,
            height=PLAYER_SIZE,
            speed=PLAYER_SPEED,
        )
        frame_count = 0
        running = True

        while running:
            delta_seconds = clock.tick(TARGET_FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            direction_x, direction_y = _read_movement_direction(
                pygame.key.get_pressed()
            )
            player.move(direction_x, direction_y, delta_seconds, world_bounds)

            screen.fill(BACKGROUND_COLOR)
            pygame.draw.rect(screen, PLAY_AREA_COLOR, screen.get_rect())
            pygame.draw.rect(
                screen, PLAY_AREA_BORDER_COLOR, screen.get_rect(), width=4
            )
            pygame.draw.rect(
                screen,
                PLAYER_COLOR,
                pygame.Rect(
                    round(player.x),
                    round(player.y),
                    round(player.width),
                    round(player.height),
                ),
            )
            instructions = font.render(
                "Move: WASD or Arrow Keys", True, TEXT_COLOR
            )
            screen.blit(instructions, (16, 16))
            pygame.display.flip()

            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                running = False
    finally:
        pygame.quit()

    return 0
