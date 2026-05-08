from dataclasses import dataclass, field

from .geometry import Rect
from .models import Alien, Bullet, Explosion, MysteryShip


@dataclass
class GameState:
    score: int = 0
    wave: int = 1
    lives: int = 3

    player: Rect = field(default_factory=lambda: Rect(0, 0, 48, 20))
    player_cooldown: float = 0.0
    player_invuln: float = 0.0

    bullets: list[Bullet] = field(default_factory=list)
    explosions: list[Explosion] = field(default_factory=list)
    aliens: list[Alien] = field(default_factory=list)
    bunker_blocks: list[Rect] = field(default_factory=list)

    alien_direction: int = 1
    alien_step_timer: float = 0.0
    enemy_fire_timer: float = 0.5

    mystery_ship: MysteryShip | None = None
    mystery_spawn_timer: float = 10.0

    game_over: bool = False
    victory_flash: float = 0.0
    show_intro: bool = True

    starfield: list[list[int]] = field(default_factory=list)
