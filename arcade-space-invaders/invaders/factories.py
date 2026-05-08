import random

from .config import (
    ALIEN_COLS,
    ALIEN_ROWS,
    ALIEN_START_X,
    ALIEN_START_Y,
    ALIEN_X_GAP,
    ALIEN_Y_GAP,
    BUNKER_BLOCK_SIZE,
    BUNKER_COUNT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from .geometry import Rect
from .models import Alien


def create_starfield(star_count: int = 90) -> list[list[int]]:
    return [
        [random.randint(0, SCREEN_WIDTH - 1), random.randint(0, SCREEN_HEIGHT - 1), random.randint(1, 2)]
        for _ in range(star_count)
    ]


def spawn_aliens() -> list[Alien]:
    aliens: list[Alien] = []
    for row in range(ALIEN_ROWS):
        for col in range(ALIEN_COLS):
            x = ALIEN_START_X + col * ALIEN_X_GAP
            y = ALIEN_START_Y + row * ALIEN_Y_GAP

            if row == 0:
                w, h, points = 30, 20, 40
            elif row < 3:
                w, h, points = 32, 22, 20
            else:
                w, h, points = 34, 24, 10

            aliens.append(Alien(float(x), float(y), w, h, points))
    return aliens


def spawn_bunkers() -> list[Rect]:
    shape = [
        "  ######  ",
        " ######## ",
        "##########",
        "###    ###",
        "##      ##",
    ]

    total_width = BUNKER_COUNT * 10 * BUNKER_BLOCK_SIZE
    spacing = (SCREEN_WIDTH - total_width) // (BUNKER_COUNT + 1)
    top = SCREEN_HEIGHT - 140

    blocks: list[Rect] = []
    for b in range(BUNKER_COUNT):
        base_x = spacing + b * (10 * BUNKER_BLOCK_SIZE + spacing)
        for r, row in enumerate(shape):
            for c, ch in enumerate(row):
                if ch == "#":
                    blocks.append(
                        Rect(
                            base_x + c * BUNKER_BLOCK_SIZE,
                            top + r * BUNKER_BLOCK_SIZE,
                            BUNKER_BLOCK_SIZE,
                            BUNKER_BLOCK_SIZE,
                        )
                    )
    return blocks
