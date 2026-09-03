"""Game-wide state that persists across individual runs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from duckov_game.application.session import GameSession, RunStatus

SessionFactory = Callable[[], GameSession]


@dataclass(slots=True)
class Game:
    """Own persistent progression and the current run."""

    session_factory: SessionFactory
    stash_item_count: int = 0
    session: GameSession = field(init=False)

    def __post_init__(self) -> None:
        if self.stash_item_count < 0:
            raise ValueError("stash_item_count cannot be negative")
        self.session = self.session_factory()

    def update(
        self,
        direction_x: float,
        direction_y: float,
        delta_seconds: float,
        *,
        aim_target: tuple[float, float] | None = None,
        fire_requested: bool = False,
    ) -> None:
        """Advance the current run and settle a new extraction once."""

        previous_status = self.session.status
        self.session.update(
            direction_x,
            direction_y,
            delta_seconds,
            aim_target=aim_target,
            fire_requested=fire_requested,
        )

        if (
            previous_status is RunStatus.ACTIVE
            and self.session.status is RunStatus.EXTRACTED
        ):
            self.stash_item_count += self.session.carried_item_count
            self.session.carried_item_count = 0

    def start_new_run(self) -> bool:
        """Replace a completed run with fresh state, preserving the stash."""

        if self.session.status not in (RunStatus.EXTRACTED, RunStatus.FAILED):
            return False

        self.session = self.session_factory()
        return True
