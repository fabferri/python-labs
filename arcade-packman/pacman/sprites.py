# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Sprite loading, slicing, and draw helper utilities.

from __future__ import annotations

from pathlib import Path

import pygame


Vec2 = pygame.math.Vector2


# Helper: load a sprite sheet with alpha transparency.
def _load_sheet(path: Path) -> pygame.Surface:
    return pygame.image.load(path.as_posix()).convert_alpha()


# Helper: load an optional sprite sheet or use fallback surface.
def _load_optional_sheet(path: Path, fallback: pygame.Surface) -> pygame.Surface:
    return _load_sheet(path) if path.exists() else fallback


class SpriteBank:
    # Initialize object state and dependencies.
    def __init__(self, tile_size: int):
        root = Path(__file__).resolve().parent.parent / "assets" / "sprites"
        self.tile_size = tile_size

        pacman_sheet = _load_sheet(root / "pacman_sheet.png")
        pacman_sheet_alt = _load_sheet(root / "pacman_sheet_alt.png") if (root / "pacman_sheet_alt.png").exists() else pacman_sheet
        ghost_sheet = _load_sheet(root / "ghost_sheet.png")
        ghost_sheet_alt = _load_sheet(root / "ghost_sheet_alt.png") if (root / "ghost_sheet_alt.png").exists() else ghost_sheet
        common_base = _load_sheet(root / "pellet_common_sheet.png") if (root / "pellet_common_sheet.png").exists() else _load_sheet(root / "pellet_sheet.png")
        common_b = _load_optional_sheet(root / "pellet_common_sheet_b.png", common_base)
        common_c = _load_optional_sheet(root / "pellet_common_sheet_c.png", common_base)
        rare_base = _load_optional_sheet(root / "pellet_rare_sheet.png", common_base)
        rare_b = _load_optional_sheet(root / "pellet_rare_sheet_b.png", rare_base)

        common_alt = _load_optional_sheet(root / "pellet_common_sheet_alt.png", common_base)
        common_alt_b = _load_optional_sheet(root / "pellet_common_sheet_alt_b.png", common_alt)
        rare_alt = _load_optional_sheet(root / "pellet_rare_sheet_alt.png", rare_base)
        rare_alt_b = _load_optional_sheet(root / "pellet_rare_sheet_alt_b.png", rare_alt)

        style_a = self._slice_row(pacman_sheet, 32, 32, 4)
        style_b = self._slice_row(pacman_sheet_alt, 32, 32, 4)
        style_a = [pygame.transform.smoothscale(f, (tile_size, tile_size)) for f in style_a]
        style_b = [pygame.transform.smoothscale(f, (tile_size, tile_size)) for f in style_b]
        self.pacman_styles = [style_a, style_b]
        self.pacman_theme_names = ["CLASSIC", "NEON"]

        ghost_rows: list[list[pygame.Surface]] = []
        for row in range(4):
            frames = self._slice_row(ghost_sheet, 32, 32, 2, row=row)
            frames = [pygame.transform.smoothscale(f, (tile_size, tile_size)) for f in frames]
            ghost_rows.append(frames)
        ghost_rows_alt: list[list[pygame.Surface]] = []
        for row in range(4):
            frames = self._slice_row(ghost_sheet_alt, 32, 32, 2, row=row)
            frames = [pygame.transform.smoothscale(f, (tile_size, tile_size)) for f in frames]
            ghost_rows_alt.append(frames)
        self.ghost_styles = [ghost_rows, ghost_rows_alt]

        self.pellet_common_styles = [
            [
                self._slice_row(common_base, 20, 20, 3),
                self._slice_row(common_b, 20, 20, 3),
                self._slice_row(common_c, 20, 20, 3),
            ],
            [
                self._slice_row(common_alt, 20, 20, 3),
                self._slice_row(common_alt_b, 20, 20, 3),
            ],
        ]
        self.pellet_rare_styles = [
            [
                self._slice_row(rare_base, 20, 20, 3),
                self._slice_row(rare_b, 20, 20, 3),
            ],
            [
                self._slice_row(rare_alt, 20, 20, 3),
                self._slice_row(rare_alt_b, 20, 20, 3),
            ],
        ]

    # Helper: slice one row of animation frames from a sprite sheet.
    def _slice_row(
        self,
        sheet: pygame.Surface,
        frame_w: int,
        frame_h: int,
        count: int,
        row: int = 0,
    ) -> list[pygame.Surface]:
        frames: list[pygame.Surface] = []
        y = row * frame_h
        for i in range(count):
            rect = pygame.Rect(i * frame_w, y, frame_w, frame_h)
            frames.append(sheet.subsurface(rect).copy())
        return frames


# Helper: convert movement direction to sprite rotation angle.
def _direction_angle(direction: Vec2) -> float:
    if direction.length_squared() == 0:
        return 0.0
    if abs(direction.x) > abs(direction.y):
        return 0.0 if direction.x > 0 else 180.0
    return 90.0 if direction.y < 0 else 270.0


# Draw Pacman sprite using direction and animation frame.
def draw_pacman(
    screen: pygame.Surface,
    bank: SpriteBank,
    center: tuple[int, int],
    direction: Vec2,
    time_s: float,
    style_index: int = 0,
) -> None:
    cycle = [0, 1, 2, 3, 2, 1]
    styles = bank.pacman_styles[style_index % len(bank.pacman_styles)]
    frame = styles[cycle[int(time_s * 14) % len(cycle)]]
    rotated = pygame.transform.rotate(frame, -_direction_angle(direction))
    rect = rotated.get_rect(center=center)
    screen.blit(rotated, rect)


# Draw one ghost sprite frame.
def draw_ghost(
    screen: pygame.Surface,
    bank: SpriteBank,
    center: tuple[int, int],
    ghost_sprite_index: int,
    time_s: float,
    theme_index: int = 0,
) -> None:
    ghost_rows = bank.ghost_styles[theme_index % len(bank.ghost_styles)]
    row = ghost_sprite_index % len(ghost_rows)
    frames = ghost_rows[row]
    frame = frames[int(time_s * 8) % len(frames)]
    rect = frame.get_rect(center=center)
    screen.blit(frame, rect)


# Draw a pellet sprite variant for the given type.
def draw_pellet(
    screen: pygame.Surface,
    bank: SpriteBank,
    center: tuple[int, int],
    time_s: float,
    kind: str = "common",
    theme_index: int = 0,
    variant_index: int = 0,
) -> None:
    if kind == "crystal":
        _draw_crystal_pellet(screen, center, time_s, theme_index, bank.tile_size)
        return

    styles = bank.pellet_common_styles if kind in ("common", "bonus") else bank.pellet_rare_styles
    theme_styles = styles[theme_index % len(styles)]
    frames = theme_styles[variant_index % len(theme_styles)]
    frame = frames[int(time_s * 10) % len(frames)]

    if kind == "bonus":
        frame = pygame.transform.smoothscale(frame, (max(10, bank.tile_size - 6), max(10, bank.tile_size - 6)))
    elif kind in ("treasure", "super"):
        scale = bank.tile_size if kind == "treasure" else bank.tile_size + 2
        frame = pygame.transform.smoothscale(frame, (scale, scale))

    rect = frame.get_rect(center=center)
    screen.blit(frame, rect)


# Helper: draw the special crystal pellet with a pulse effect.
def _draw_crystal_pellet(
    screen: pygame.Surface,
    center: tuple[int, int],
    time_s: float,
    theme_index: int,
    tile_size: int,
) -> None:
    pulse = 1.0 + (0.12 * ((int(time_s * 8) % 2) * 2 - 1))
    radius = max(5, int((tile_size * 0.34) * pulse))
    palette = [
        ((110, 255, 245), (20, 160, 190), (210, 255, 255)),
        ((255, 150, 80), (200, 70, 20), (255, 235, 170)),
    ][theme_index % 2]
    outer, inner, sparkle = palette

    points = [
        (center[0], center[1] - radius),
        (center[0] + radius - 2, center[1]),
        (center[0], center[1] + radius),
        (center[0] - radius + 2, center[1]),
    ]
    pygame.draw.polygon(screen, outer, points)
    inner_points = [
        (center[0], center[1] - radius + 3),
        (center[0] + radius - 4, center[1]),
        (center[0], center[1] + radius - 3),
        (center[0] - radius + 4, center[1]),
    ]
    pygame.draw.polygon(screen, inner, inner_points)
    pygame.draw.line(screen, sparkle, (center[0], center[1] - radius + 2), (center[0], center[1] + radius - 2), 1)
    pygame.draw.line(screen, sparkle, (center[0] - radius + 3, center[1]), (center[0] + radius - 3, center[1]), 1)

