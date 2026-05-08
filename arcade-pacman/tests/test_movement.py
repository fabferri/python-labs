# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Tests for player and ghost movement behavior.

from __future__ import annotations

import unittest

import pygame

from pacman.entities import Ghost, Player


class TestPlayerMovement(unittest.TestCase):
    # Validate Player Stops Before Wall behavior.
    def test_player_stops_before_wall(self) -> None:
        player = Player((1, 1), tile_size=24, speed=120.0)
        walls = {(2, 1)}

        player.set_next_direction(1, 0)
        for _ in range(10):
            player.update(1 / 60, walls)

        self.assertLess(player.position.x + player.radius, 2 * 24)

    # Validate Player Can Turn At Intersection behavior.
    def test_player_can_turn_at_intersection(self) -> None:
        player = Player((1, 1), tile_size=24, speed=120.0)
        walls: set[tuple[int, int]] = set()

        player.direction = pygame.math.Vector2(0, -1)
        player.position = pygame.math.Vector2(36, 36)
        player.set_next_direction(1, 0)
        player.update(1 / 60, walls)

        self.assertEqual(tuple(player.direction), (1.0, 0.0))

    # Validate Player Wraps Horizontally Through Tunnel behavior.
    def test_player_wraps_horizontally_through_tunnel(self) -> None:
        player = Player((1, 1), tile_size=24, speed=120.0)
        walls: set[tuple[int, int]] = set()

        player.direction = pygame.math.Vector2(-1, 0)
        player.next_direction = pygame.math.Vector2(-1, 0)
        player.position = pygame.math.Vector2(-13, 36)

        player.update(1 / 60, walls, level_width_tiles=28, tunnel_rows={1})

        self.assertGreater(player.position.x, 28 * 24)


class TestGhostMovement(unittest.TestCase):
    # Validate Ghost Wraps Horizontally Through Tunnel Row behavior.
    def test_ghost_wraps_horizontally_through_tunnel_row(self) -> None:
        ghost = Ghost((1, 1), tile_size=24, speed=95.0, color=(255, 0, 0))
        walls: set[tuple[int, int]] = set()

        ghost.direction = pygame.math.Vector2(-1, 0)
        ghost.position = pygame.math.Vector2(-13, 36)

        ghost.update(1 / 60, walls, level_width_tiles=28, tunnel_rows={1})

        self.assertGreater(ghost.position.x, 28 * 24)


if __name__ == "__main__":
    unittest.main()

