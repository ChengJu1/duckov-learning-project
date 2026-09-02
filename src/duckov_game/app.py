"""Window lifecycle for the first executable milestone."""

from __future__ import annotations

import pygame

WINDOW_SIZE = (960, 540)
WINDOW_TITLE = "Duckov Learning Project"
BACKGROUND_COLOR = (28, 32, 40)
TARGET_FPS = 60


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
        frame_count = 0
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill(BACKGROUND_COLOR)
            pygame.display.flip()
            clock.tick(TARGET_FPS)

            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                running = False
    finally:
        pygame.quit()

    return 0

