# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Typed models used across gameplay modules.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DifficultyConfig:
    name: str
    ghost_speed_multiplier: float
    ghost_chase_bias: float


@dataclass(frozen=True)
class PelletType:
    score: int
    ratio: float

