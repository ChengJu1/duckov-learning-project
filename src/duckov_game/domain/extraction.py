"""Extraction-zone state for the stage-one prototype."""

from __future__ import annotations

from dataclasses import dataclass

from duckov_game.domain.geometry import Rectangle


@dataclass(frozen=True, slots=True)
class ExtractionZone:
    """A rectangular area that ends the current run when entered."""

    x: float
    y: float
    width: float
    height: float

    @property
    def hitbox(self) -> Rectangle:
        return Rectangle(self.x, self.y, self.width, self.height)

