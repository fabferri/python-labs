# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Utility script for generating sprite assets.

from __future__ import annotations

from pathlib import Path

import pygame


# Ensure Dirs.
def ensure_dirs(root: Path) -> Path:
    sprites_dir = root / "assets" / "sprites"
    sprites_dir.mkdir(parents=True, exist_ok=True)
    return sprites_dir


# Draw Pacman Frames.
def draw_pacman_frames(sprites_dir: Path) -> None:
    frame_size = 32
    frame_count = 4
    sheet = pygame.Surface((frame_size * frame_count, frame_size), pygame.SRCALPHA)
    mouth_angles = [8, 18, 32, 24]

    for i, mouth in enumerate(mouth_angles):
        frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
        center = (frame_size // 2, frame_size // 2)
        radius = 13

        # Main body, border, and lower shading for a stronger arcade look.
        pygame.draw.circle(frame, (255, 230, 64), center, radius)
        pygame.draw.circle(frame, (227, 177, 20), center, radius, width=1)
        pygame.draw.circle(frame, (240, 192, 35), (center[0], center[1] + 2), radius - 3)

        # Upper highlight gives the sprite a more polished volume.
        highlight = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
        pygame.draw.ellipse(highlight, (255, 255, 220, 80), (7, 5, 13, 8))
        frame.blit(highlight, (0, 0))

        start = mouth
        end = 360 - mouth
        p1 = center
        p2 = (
            center[0] + int(radius * pygame.math.Vector2(1, 0).rotate(start).x),
            center[1] - int(radius * pygame.math.Vector2(1, 0).rotate(start).y),
        )
        p3 = (
            center[0] + int(radius * pygame.math.Vector2(1, 0).rotate(end).x),
            center[1] - int(radius * pygame.math.Vector2(1, 0).rotate(end).y),
        )
        pygame.draw.polygon(frame, (0, 0, 0, 0), [p1, p2, p3])

        # Small mouth edge pixels to reduce jagged look while opening.
        pygame.draw.line(frame, (227, 177, 20), p1, p2, width=1)
        pygame.draw.line(frame, (227, 177, 20), p1, p3, width=1)

        # Eye and tiny specular dot.
        pygame.draw.circle(frame, (22, 22, 22), (frame_size // 2 + 4, frame_size // 2 - 7), 2)
        pygame.draw.circle(frame, (240, 240, 240), (frame_size // 2 + 5, frame_size // 2 - 8), 1)

        sheet.blit(frame, (i * frame_size, 0))

    pygame.image.save(sheet, sprites_dir / "pacman_sheet.png")


# Draw Pacman Frames Alt.
def draw_pacman_frames_alt(sprites_dir: Path) -> None:
    frame_size = 32
    frame_count = 4
    sheet = pygame.Surface((frame_size * frame_count, frame_size), pygame.SRCALPHA)
    mouth_angles = [10, 20, 30, 18]

    for i, mouth in enumerate(mouth_angles):
        frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
        center = (frame_size // 2, frame_size // 2)
        radius = 13

        # Neon style body with cyan rim.
        pygame.draw.circle(frame, (255, 240, 95), center, radius)
        pygame.draw.circle(frame, (90, 255, 255), center, radius, width=2)
        pygame.draw.circle(frame, (255, 214, 64), (center[0], center[1] + 1), radius - 4)

        start = mouth
        end = 360 - mouth
        p1 = center
        p2 = (
            center[0] + int(radius * pygame.math.Vector2(1, 0).rotate(start).x),
            center[1] - int(radius * pygame.math.Vector2(1, 0).rotate(start).y),
        )
        p3 = (
            center[0] + int(radius * pygame.math.Vector2(1, 0).rotate(end).x),
            center[1] - int(radius * pygame.math.Vector2(1, 0).rotate(end).y),
        )
        pygame.draw.polygon(frame, (0, 0, 0, 0), [p1, p2, p3])

        # Accent around mouth and stylized eye.
        pygame.draw.line(frame, (90, 255, 255), p1, p2, width=1)
        pygame.draw.line(frame, (90, 255, 255), p1, p3, width=1)
        pygame.draw.circle(frame, (18, 18, 34), (frame_size // 2 + 4, frame_size // 2 - 7), 2)
        pygame.draw.circle(frame, (130, 255, 255), (frame_size // 2 + 3, frame_size // 2 - 8), 1)

        sheet.blit(frame, (i * frame_size, 0))

    pygame.image.save(sheet, sprites_dir / "pacman_sheet_alt.png")


# Draw Ghost Sheet.
def draw_ghost_sheet(sprites_dir: Path) -> None:
    frame_size = 32
    colors = [
        (255, 82, 82),
        (82, 255, 255),
        (255, 184, 82),
        (255, 82, 235),
    ]
    frame_count = 2
    sheet = pygame.Surface((frame_size * frame_count, frame_size * len(colors)), pygame.SRCALPHA)

    for row, color in enumerate(colors):
        for col in range(frame_count):
            frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
            y_bob = 1 if col == 0 else -1

            body = pygame.Rect(6, 8 + y_bob, 20, 18)
            pygame.draw.ellipse(frame, color, (6, 4 + y_bob, 20, 14))
            pygame.draw.rect(frame, color, body)

            for i in range(4):
                x = 8 + i * 5
                y = 25 + (1 if (i + col) % 2 == 0 else -1)
                pygame.draw.circle(frame, color, (x, y), 3)

            pygame.draw.circle(frame, (255, 255, 255), (12, 14 + y_bob), 3)
            pygame.draw.circle(frame, (255, 255, 255), (20, 14 + y_bob), 3)
            pygame.draw.circle(frame, (40, 70, 180), (13, 14 + y_bob), 1)
            pygame.draw.circle(frame, (40, 70, 180), (21, 14 + y_bob), 1)

            sheet.blit(frame, (col * frame_size, row * frame_size))

    pygame.image.save(sheet, sprites_dir / "ghost_sheet.png")


# Draw Ghost Sheet Alt.
def draw_ghost_sheet_alt(sprites_dir: Path) -> None:
    frame_size = 32
    colors = [
        (80, 255, 210),
        (112, 206, 255),
        (255, 130, 235),
        (186, 120, 255),
    ]
    frame_count = 2
    sheet = pygame.Surface((frame_size * frame_count, frame_size * len(colors)), pygame.SRCALPHA)

    for row, color in enumerate(colors):
        for col in range(frame_count):
            frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
            y_bob = 1 if col == 0 else -1

            body = pygame.Rect(6, 8 + y_bob, 20, 18)
            pygame.draw.ellipse(frame, color, (6, 4 + y_bob, 20, 14))
            pygame.draw.rect(frame, color, body)

            # Neon edge glow stroke.
            pygame.draw.ellipse(frame, (220, 255, 255), (6, 4 + y_bob, 20, 14), width=1)
            pygame.draw.rect(frame, (220, 255, 255), body, width=1)

            for i in range(4):
                x = 8 + i * 5
                y = 25 + (1 if (i + col) % 2 == 0 else -1)
                pygame.draw.circle(frame, color, (x, y), 3)

            pygame.draw.circle(frame, (255, 255, 255), (12, 14 + y_bob), 3)
            pygame.draw.circle(frame, (255, 255, 255), (20, 14 + y_bob), 3)
            pygame.draw.circle(frame, (32, 34, 90), (13, 14 + y_bob), 1)
            pygame.draw.circle(frame, (32, 34, 90), (21, 14 + y_bob), 1)

            sheet.blit(frame, (col * frame_size, row * frame_size))

    pygame.image.save(sheet, sprites_dir / "ghost_sheet_alt.png")


# Draw Common Pellet Sheet.
def draw_common_pellet_sheet(sprites_dir: Path) -> None:
    frame_size = 20
    frame_count = 3
    sheet = pygame.Surface((frame_size * frame_count, frame_size), pygame.SRCALPHA)

    specs = [(6, 3, 80), (7, 3, 110), (8, 4, 145)]
    for i, (glow, core, alpha) in enumerate(specs):
        frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
        pygame.draw.circle(frame, (255, 210, 120, alpha), (10, 10), glow)
        pygame.draw.circle(frame, (255, 238, 165, 240), (10, 10), core)
        sheet.blit(frame, (i * frame_size, 0))

    pygame.image.save(sheet, sprites_dir / "pellet_common_sheet.png")


# Draw Common Pellet Sheet B.
def draw_common_pellet_sheet_b(sprites_dir: Path) -> None:
    frame_size = 20
    frame_count = 3
    sheet = pygame.Surface((frame_size * frame_count, frame_size), pygame.SRCALPHA)

    specs = [(5, 2, 90), (6, 3, 120), (7, 3, 150)]
    for i, (glow, core, alpha) in enumerate(specs):
        frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
        pygame.draw.circle(frame, (255, 188, 98, alpha), (10, 10), glow)
        pygame.draw.circle(frame, (255, 228, 150, 245), (10, 10), core)
        pygame.draw.circle(frame, (255, 255, 220, 120), (9, 9), 1)
        sheet.blit(frame, (i * frame_size, 0))

    pygame.image.save(sheet, sprites_dir / "pellet_common_sheet_b.png")


# Draw Common Pellet Sheet C.
def draw_common_pellet_sheet_c(sprites_dir: Path) -> None:
    frame_size = 20
    frame_count = 3
    sheet = pygame.Surface((frame_size * frame_count, frame_size), pygame.SRCALPHA)

    specs = [(6, 2, 85), (7, 3, 115), (8, 4, 145)]
    for i, (glow, core, alpha) in enumerate(specs):
        frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
        pygame.draw.circle(frame, (255, 206, 140, alpha), (10, 10), glow)
        diamond = [(10, 6), (13, 10), (10, 14), (7, 10)]
        pygame.draw.polygon(frame, (255, 244, 185, 235), diamond)
        pygame.draw.circle(frame, (255, 228, 150, 150), (10, 10), core, width=1)
        sheet.blit(frame, (i * frame_size, 0))

    pygame.image.save(sheet, sprites_dir / "pellet_common_sheet_c.png")


# Draw Rare Pellet Sheet.
def draw_rare_pellet_sheet(sprites_dir: Path) -> None:
    frame_size = 20
    frame_count = 3
    sheet = pygame.Surface((frame_size * frame_count, frame_size), pygame.SRCALPHA)

    specs = [(7, 3, 95), (8, 4, 135), (9, 5, 170)]
    for i, (glow, core, alpha) in enumerate(specs):
        frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
        pygame.draw.circle(frame, (180, 180, 255, alpha), (10, 10), glow)
        points = [
            (10, 4),
            (12, 8),
            (16, 8),
            (13, 11),
            (14, 15),
            (10, 13),
            (6, 15),
            (7, 11),
            (4, 8),
            (8, 8),
        ]
        pygame.draw.polygon(frame, (255, 250, 255, 250), points)
        pygame.draw.circle(frame, (170, 255, 255, 220), (10, 10), core, width=1)
        sheet.blit(frame, (i * frame_size, 0))

    pygame.image.save(sheet, sprites_dir / "pellet_rare_sheet.png")


# Draw Rare Pellet Sheet B.
def draw_rare_pellet_sheet_b(sprites_dir: Path) -> None:
    frame_size = 20
    frame_count = 3
    sheet = pygame.Surface((frame_size * frame_count, frame_size), pygame.SRCALPHA)

    specs = [(8, 3, 115), (9, 4, 155), (10, 5, 190)]
    for i, (glow, core, alpha) in enumerate(specs):
        frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
        pygame.draw.circle(frame, (198, 170, 255, alpha), (10, 10), glow)
        points = [(10, 3), (13, 8), (17, 9), (13, 12), (12, 17), (10, 13), (8, 17), (7, 12), (3, 9), (7, 8)]
        pygame.draw.polygon(frame, (255, 230, 255, 255), points)
        pygame.draw.circle(frame, (200, 255, 255, 220), (10, 10), core, width=1)
        sheet.blit(frame, (i * frame_size, 0))

    pygame.image.save(sheet, sprites_dir / "pellet_rare_sheet_b.png")


# Draw Common Pellet Sheet Alt.
def draw_common_pellet_sheet_alt(sprites_dir: Path) -> None:
    frame_size = 20
    frame_count = 3
    sheet = pygame.Surface((frame_size * frame_count, frame_size), pygame.SRCALPHA)

    specs = [(6, 3, 95), (7, 3, 125), (8, 4, 165)]
    for i, (glow, core, alpha) in enumerate(specs):
        frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
        pygame.draw.circle(frame, (120, 240, 255, alpha), (10, 10), glow)
        pygame.draw.circle(frame, (205, 255, 255, 245), (10, 10), core)
        pygame.draw.circle(frame, (120, 255, 255, 170), (10, 10), core + 1, width=1)
        sheet.blit(frame, (i * frame_size, 0))

    pygame.image.save(sheet, sprites_dir / "pellet_common_sheet_alt.png")


# Draw Common Pellet Sheet Alt B.
def draw_common_pellet_sheet_alt_b(sprites_dir: Path) -> None:
    frame_size = 20
    frame_count = 3
    sheet = pygame.Surface((frame_size * frame_count, frame_size), pygame.SRCALPHA)

    specs = [(6, 2, 100), (7, 3, 130), (8, 3, 170)]
    for i, (glow, core, alpha) in enumerate(specs):
        frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
        pygame.draw.circle(frame, (120, 255, 235, alpha), (10, 10), glow)
        pygame.draw.rect(frame, (210, 255, 255, 240), pygame.Rect(8, 8, 4, 4), border_radius=1)
        pygame.draw.circle(frame, (150, 255, 255, 160), (10, 10), core, width=1)
        sheet.blit(frame, (i * frame_size, 0))

    pygame.image.save(sheet, sprites_dir / "pellet_common_sheet_alt_b.png")


# Draw Rare Pellet Sheet Alt.
def draw_rare_pellet_sheet_alt(sprites_dir: Path) -> None:
    frame_size = 20
    frame_count = 3
    sheet = pygame.Surface((frame_size * frame_count, frame_size), pygame.SRCALPHA)

    specs = [(7, 3, 110), (8, 4, 150), (9, 5, 180)]
    for i, (glow, core, alpha) in enumerate(specs):
        frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
        pygame.draw.circle(frame, (255, 130, 240, alpha), (10, 10), glow)
        points = [
            (10, 3),
            (13, 8),
            (17, 8),
            (14, 11),
            (15, 16),
            (10, 13),
            (5, 16),
            (6, 11),
            (3, 8),
            (7, 8),
        ]
        pygame.draw.polygon(frame, (255, 220, 255, 255), points)
        pygame.draw.circle(frame, (255, 180, 255, 220), (10, 10), core, width=1)
        sheet.blit(frame, (i * frame_size, 0))

    pygame.image.save(sheet, sprites_dir / "pellet_rare_sheet_alt.png")


# Draw Rare Pellet Sheet Alt B.
def draw_rare_pellet_sheet_alt_b(sprites_dir: Path) -> None:
    frame_size = 20
    frame_count = 3
    sheet = pygame.Surface((frame_size * frame_count, frame_size), pygame.SRCALPHA)

    specs = [(8, 3, 125), (9, 4, 160), (10, 5, 200)]
    for i, (glow, core, alpha) in enumerate(specs):
        frame = pygame.Surface((frame_size, frame_size), pygame.SRCALPHA)
        pygame.draw.circle(frame, (255, 150, 245, alpha), (10, 10), glow)
        points = [(10, 2), (14, 8), (18, 8), (15, 12), (16, 17), (10, 14), (4, 17), (5, 12), (2, 8), (6, 8)]
        pygame.draw.polygon(frame, (255, 210, 255, 255), points)
        pygame.draw.circle(frame, (255, 180, 255, 230), (10, 10), core, width=1)
        sheet.blit(frame, (i * frame_size, 0))

    pygame.image.save(sheet, sprites_dir / "pellet_rare_sheet_alt_b.png")


# Draw Pellet Sheet Compat.
def draw_pellet_sheet_compat(sprites_dir: Path) -> None:
    # Compatibility output for existing references.
    frame_size = 20
    frame_count = 3
    sheet = pygame.Surface((frame_size * frame_count, frame_size), pygame.SRCALPHA)
    src = pygame.image.load((sprites_dir / "pellet_common_sheet.png").as_posix())
    sheet.blit(src, (0, 0))
    pygame.image.save(sheet, sprites_dir / "pellet_sheet.png")


# Main.
def main() -> None:
    pygame.init()
    try:
        root = Path(__file__).resolve().parents[1]
        sprites_dir = ensure_dirs(root)
        draw_pacman_frames(sprites_dir)
        draw_pacman_frames_alt(sprites_dir)
        draw_ghost_sheet(sprites_dir)
        draw_ghost_sheet_alt(sprites_dir)
        draw_common_pellet_sheet(sprites_dir)
        draw_common_pellet_sheet_b(sprites_dir)
        draw_common_pellet_sheet_c(sprites_dir)
        draw_rare_pellet_sheet(sprites_dir)
        draw_rare_pellet_sheet_b(sprites_dir)
        draw_common_pellet_sheet_alt(sprites_dir)
        draw_common_pellet_sheet_alt_b(sprites_dir)
        draw_rare_pellet_sheet_alt(sprites_dir)
        draw_rare_pellet_sheet_alt_b(sprites_dir)
        draw_pellet_sheet_compat(sprites_dir)
        print(f"Generated sprites in: {sprites_dir}")
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()

