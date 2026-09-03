from __future__ import annotations

import pytest

from duckov_game.app import run
from duckov_game import app
from duckov_game.application import RunStatus
from duckov_game.domain import WorldBounds


def test_window_runs_for_two_frames(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")

    assert run(max_frames=2) == 0


def test_max_frames_must_be_positive() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        run(max_frames=0)


@pytest.mark.parametrize("status", [RunStatus.EXTRACTED, RunStatus.FAILED])
def test_terminal_run_screen_renders(monkeypatch: pytest.MonkeyPatch, status: RunStatus) -> None:
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    session = app._create_session(WorldBounds(*app.WINDOW_SIZE))
    session.status = status
    if status is RunStatus.FAILED:
        session.player.health.take_damage(100)
    monkeypatch.setattr(app, "_create_session", lambda bounds: session)
    assert run(max_frames=2) == 0
