from __future__ import annotations

import pytest

from duckov_game.app import run


def test_window_runs_for_two_frames(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")

    assert run(max_frames=2) == 0


def test_max_frames_must_be_positive() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        run(max_frames=0)

