import pygame

from .config import GREEN, RED, WHITE


class ArcadeSpriteSheet:
    def __init__(self) -> None:
        self._cache: dict[tuple[str, int, int, int], pygame.Surface] = {}
        self._base = self._build_base_sprites()

    def get(self, name: str, frame: int = 0, size: tuple[int, int] | None = None) -> pygame.Surface:
        source = self._base[name]
        if isinstance(source, list):
            frame_surface = source[frame % len(source)]
        else:
            frame_surface = source

        if size is None:
            return frame_surface

        key = (name, frame, size[0], size[1])
        if key not in self._cache:
            self._cache[key] = pygame.transform.scale(frame_surface, size)
        return self._cache[key]

    def _build_base_sprites(self) -> dict[str, pygame.Surface | list[pygame.Surface]]:
        return {
            "player": self._make_sprite(
                [
                    ".....G.....",
                    "....GGG....",
                    "...GGGGG...",
                    "..GGGGGGG..",
                    ".GGGGGGGGG.",
                    "GGGGGGGGGGG",
                    "GGG..G..GGG",
                    "GG.......GG",
                ]
            ),
            "alien_top": [
                self._make_sprite(
                    [
                        "...GGGGG...",
                        "..G.....G..",
                        ".G.G...G.G.",
                        ".GGGGGGGGG.",
                        "GG.GGGGG.GG",
                        "GGGGGGGGGGG",
                        "..GG...GG..",
                        ".GG.....GG.",
                    ]
                ),
                self._make_sprite(
                    [
                        "...GGGGG...",
                        "..G.....G..",
                        ".G.G...G.G.",
                        ".GGGGGGGGG.",
                        "GG.GGGGG.GG",
                        "GGGGGGGGGGG",
                        ".GG.G.G.GG.",
                        "G.........G",
                    ]
                ),
            ],
            "alien_mid": [
                self._make_sprite(
                    [
                        "...GGGGG...",
                        ".GGGGGGGGG.",
                        "GG.GGGGG.GG",
                        "GGGGGGGGGGG",
                        "GGG.GGG.GGG",
                        ".GGGGGGGGG.",
                        ".G.G...G.G.",
                        "G...G.G...G",
                    ]
                ),
                self._make_sprite(
                    [
                        "...GGGGG...",
                        ".GGGGGGGGG.",
                        "GG.GGGGG.GG",
                        "GGGGGGGGGGG",
                        "GGG.GGG.GGG",
                        ".GGGGGGGGG.",
                        "..G.G.G.G..",
                        ".GG.....GG.",
                    ]
                ),
            ],
            "alien_bot": [
                self._make_sprite(
                    [
                        "..GGGGGGG..",
                        ".GGGGGGGGG.",
                        "GGGGGGGGGGG",
                        "GG.GGGGG.GG",
                        "GGGGGGGGGGG",
                        "..GG...GG..",
                        ".GG.G.G.GG.",
                        "G..G...G..G",
                    ]
                ),
                self._make_sprite(
                    [
                        "..GGGGGGG..",
                        ".GGGGGGGGG.",
                        "GGGGGGGGGGG",
                        "GG.GGGGG.GG",
                        "GGGGGGGGGGG",
                        ".GG.....GG.",
                        "..GG...GG..",
                        ".G.......G.",
                    ]
                ),
            ],
            "ufo": self._make_sprite(
                [
                    "......RRRR......",
                    "....RRRRRRRR....",
                    "..RRRRRRRRRRRR..",
                    ".RRRWWWWWWWWRRR.",
                    "RRRWRRWWRRWRRWRR",
                    "RRRRRRRRRRRRRRRR",
                    "..RR..RRRR..RR..",
                ],
                palette={"R": RED, "W": WHITE},
            ),
            "bunker_block": self._make_sprite(
                [
                    "GGGG",
                    "G..G",
                    "G..G",
                    "GGGG",
                ],
                palette={"G": GREEN},
            ),
            "bullet_player": self._make_sprite(
                [
                    "W",
                    "W",
                    "W",
                    "W",
                    "W",
                ],
                palette={"W": WHITE},
            ),
            "bullet_enemy": self._make_sprite(
                [
                    "R",
                    "R",
                    "R",
                    "R",
                    "R",
                ],
                palette={"R": RED},
            ),
        }

    def _make_sprite(
        self,
        pattern: list[str],
        palette: dict[str, tuple[int, int, int]] | None = None,
    ) -> pygame.Surface:
        if palette is None:
            palette = {"G": GREEN}

        height = len(pattern)
        width = len(pattern[0]) if height else 0
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        for y, row in enumerate(pattern):
            for x, symbol in enumerate(row):
                color = palette.get(symbol)
                if color is not None:
                    surface.set_at((x, y), color)

        return surface
