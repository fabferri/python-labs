# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Global gameplay configuration and tuning constants.

from dataclasses import dataclass

from .models import DifficultyConfig, PelletType


@dataclass(frozen=True)
class GameConfig:
    title: str = "Pacman Arcade"
    screen_width: int = 672
    screen_height: int = 744
    tile_size: int = 24
    fps: int = 60
    player_speed: float = 120.0
    ghost_speed: float = 95.0
    audio_enabled: bool = True


CFG = GameConfig()


DIFFICULTIES = (
    DifficultyConfig(name="EASY", ghost_speed_multiplier=0.85, ghost_chase_bias=0.55),
    DifficultyConfig(name="NORMAL", ghost_speed_multiplier=1.0, ghost_chase_bias=0.75),
    DifficultyConfig(name="HARD", ghost_speed_multiplier=1.15, ghost_chase_bias=0.9),
)


PELLET_TYPES: dict[str, PelletType] = {
    "common": PelletType(score=10, ratio=0.66),
    "bonus": PelletType(score=25, ratio=0.15),
    "rare": PelletType(score=50, ratio=0.10),
    "treasure": PelletType(score=100, ratio=0.04),
    "super": PelletType(score=200, ratio=0.01),
    "crystal": PelletType(score=350, ratio=0.02),
}

