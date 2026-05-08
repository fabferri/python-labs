# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Player and ghost entity movement and behavior models.

from __future__ import annotations

import random

import pygame


Vec2 = pygame.math.Vector2


# Helper: Tile Center.
def _tile_center(tile_x: int, tile_y: int, tile_size: int) -> Vec2:
    return Vec2((tile_x + 0.5) * tile_size, (tile_y + 0.5) * tile_size)


# Helper: Wrap Horizontal.
def _wrap_horizontal(position: Vec2, direction: Vec2, tile_size: int, level_width_tiles: int, tunnel_rows: set[int] | None) -> None:
    if abs(direction.x) == 0:
        return
    if tunnel_rows is not None:
        tile_y = int(position.y // tile_size)
        if tile_y not in tunnel_rows:
            return
    min_center = -tile_size * 0.5
    max_center = (level_width_tiles * tile_size) + (tile_size * 0.5)
    if position.x < min_center:
        position.x = max_center
    elif position.x > max_center:
        position.x = min_center


class Player:
    # Initialize object state and dependencies.
    def __init__(self, spawn_tile: tuple[int, int], tile_size: int, speed: float):
        self.tile_size = tile_size
        self.speed = speed
        self.radius = tile_size // 2 - 2
        self.turn_tolerance = 3.0
        self.spawn(spawn_tile)

    # Spawn.
    def spawn(self, spawn_tile: tuple[int, int]) -> None:
        self.position = Vec2((spawn_tile[0] + 0.5) * self.tile_size, (spawn_tile[1] + 0.5) * self.tile_size)
        self.direction = Vec2(0, 0)
        self.next_direction = Vec2(0, 0)

    @property
    # Tile.
    def tile(self) -> tuple[int, int]:
        return int(self.position.x // self.tile_size), int(self.position.y // self.tile_size)

    # Helper: Is Near Tile Center.
    def _is_near_tile_center(self) -> bool:
        tile_x, tile_y = self.tile
        center = _tile_center(tile_x, tile_y, self.tile_size)
        return self.position.distance_to(center) <= self.turn_tolerance

    # Helper: Snap To Tile Center.
    def _snap_to_tile_center(self) -> None:
        tile_x, tile_y = self.tile
        center = _tile_center(tile_x, tile_y, self.tile_size)
        if abs(self.direction.x) > 0:
            self.position.y = center.y
        elif abs(self.direction.y) > 0:
            self.position.x = center.x
        else:
            self.position = center

    # Helper: Can Occupy.
    def _can_occupy(self, position: Vec2, direction: Vec2, walls: set[tuple[int, int]]) -> bool:
        if direction.length_squared() == 0:
            return True

        forward = direction.normalize() * self.radius
        if abs(direction.x) > 0:
            offsets = [Vec2(0, 0), Vec2(0, self.radius - 1), Vec2(0, -self.radius + 1)]
        else:
            offsets = [Vec2(0, 0), Vec2(self.radius - 1, 0), Vec2(-self.radius + 1, 0)]

        for offset in offsets:
            probe = position + forward + offset
            probe_tile = int(probe.x // self.tile_size), int(probe.y // self.tile_size)
            if probe_tile in walls:
                return False
        return True

    # Helper: Can Move.
    def _can_move(self, direction: Vec2, walls: set[tuple[int, int]]) -> bool:
        if direction.length_squared() == 0:
            return True
        return self._can_occupy(self.position, direction, walls)

    # Set the next movement direction requested by input.
    def set_next_direction(self, x: int, y: int) -> None:
        self.next_direction = Vec2(x, y)

    # Update.
    def update(
        self,
        dt: float,
        walls: set[tuple[int, int]],
        level_width_tiles: int | None = None,
        tunnel_rows: set[int] | None = None,
    ) -> None:
        if self._is_near_tile_center():
            self._snap_to_tile_center()
            if self._can_move(self.next_direction, walls):
                self.direction = self.next_direction
            elif not self._can_move(self.direction, walls):
                self.direction = Vec2(0, 0)

        if not self._can_move(self.direction, walls):
            return

        remaining = self.speed * dt
        while remaining > 0:
            step = min(2.0, remaining)
            candidate = self.position + self.direction * step
            if not self._can_occupy(candidate, self.direction, walls):
                break
            self.position = candidate
            if level_width_tiles is not None:
                _wrap_horizontal(self.position, self.direction, self.tile_size, level_width_tiles, tunnel_rows)
            remaining -= step

        if self.direction.length_squared() > 0:
            self._snap_to_tile_center()


class Ghost:
    # Initialize object state and dependencies.
    def __init__(
        self,
        spawn_tile: tuple[int, int],
        tile_size: int,
        speed: float,
        color: tuple[int, int, int],
        sprite_index: int = 0,
        chase_bias: float = 0.8,
    ):
        self.tile_size = tile_size
        self.speed = speed
        self.color = color
        self.sprite_index = sprite_index
        self.chase_bias = max(0.0, min(1.0, chase_bias))
        self.radius = tile_size // 2 - 3
        self.spawn(spawn_tile)
        self._decision_counter = 0

    # Spawn.
    def spawn(self, spawn_tile: tuple[int, int]) -> None:
        self.position = Vec2((spawn_tile[0] + 0.5) * self.tile_size, (spawn_tile[1] + 0.5) * self.tile_size)
        self.direction = Vec2(1, 0)
        self._decision_counter = 0

    @property
    # Tile.
    def tile(self) -> tuple[int, int]:
        return int(self.position.x // self.tile_size), int(self.position.y // self.tile_size)

    # Helper: Can Move.
    def _can_move(self, direction: Vec2, walls: set[tuple[int, int]]) -> bool:
        """Check if we can move in a direction."""
        if direction.length_squared() == 0:
            return False
        # Test at a reasonable distance ahead (half tile)
        test_pos = self.position + direction * (self.tile_size * 0.4)
        test_tile = int(test_pos.x // self.tile_size), int(test_pos.y // self.tile_size)
        return test_tile not in walls

    # Helper: Get Valid Directions.
    def _get_valid_directions(self, walls: set[tuple[int, int]]) -> list[Vec2]:
        """Get all valid directions from current position."""
        options = [Vec2(1, 0), Vec2(-1, 0), Vec2(0, 1), Vec2(0, -1)]
        return [d for d in options if self._can_move(d, walls)]

    # Helper: Decide Direction.
    def _decide_direction(self, walls: set[tuple[int, int]], target_tile: tuple[int, int] | None) -> None:
        """Make a new direction decision at an intersection."""
        valid = self._get_valid_directions(walls)
        if not valid:
            return  # Keep current direction

        # Prefer not to reverse
        reverse = -self.direction
        no_reverse = [d for d in valid if d != reverse]
        if no_reverse:
            valid = no_reverse

        # Chase or scatter
        if target_tile and random.random() < self.chase_bias:
            # Chase: pick direction closest to target
            def dist_to_target(direction: Vec2) -> float:
                next_tile = (self.tile[0] + int(direction.x), self.tile[1] + int(direction.y))
                dx = target_tile[0] - next_tile[0]
                dy = target_tile[1] - next_tile[1]
                return dx * dx + dy * dy

            self.direction = min(valid, key=dist_to_target)
        else:
            # Scatter: random direction
            self.direction = random.choice(valid)

    # Update.
    def update(
        self,
        dt: float,
        walls: set[tuple[int, int]],
        target_tile: tuple[int, int] | None = None,
        level_width_tiles: int | None = None,
        tunnel_rows: set[int] | None = None,
    ) -> None:
        # Periodically make decisions at intersections (every 8 frames or so)
        self._decision_counter += 1
        
        # Check if near tile center
        center_dist_x = abs((self.position.x % self.tile_size) - self.tile_size / 2)
        center_dist_y = abs((self.position.y % self.tile_size) - self.tile_size / 2)
        at_intersection = center_dist_x < 3.0 and center_dist_y < 3.0
        
        if at_intersection and self._decision_counter > 6:
            self._decision_counter = 0
            # Snap to center for clean alignment
            self.position = Vec2(
                (self.tile[0] + 0.5) * self.tile_size,
                (self.tile[1] + 0.5) * self.tile_size,
            )
            self._decide_direction(walls, target_tile)

        # Always try to move in current direction
        if self._can_move(self.direction, walls):
            self.position += self.direction * self.speed * dt
            if level_width_tiles is not None:
                _wrap_horizontal(self.position, self.direction, self.tile_size, level_width_tiles, tunnel_rows)
        else:
            # Blocked: try to find another direction immediately
            valid = self._get_valid_directions(walls)
            if valid:
                # Pick closest to current direction or target
                if target_tile and random.random() < self.chase_bias:
                    # Score.
                    def score(d: Vec2) -> float:
                        next_t = (self.tile[0] + int(d.x), self.tile[1] + int(d.y))
                        dx = target_tile[0] - next_t[0]
                        dy = target_tile[1] - next_t[1]
                        return dx * dx + dy * dy
                    self.direction = min(valid, key=score)
                else:
                    self.direction = valid[0]
                self.position += self.direction * self.speed * dt
                if level_width_tiles is not None:
                    _wrap_horizontal(self.position, self.direction, self.tile_size, level_width_tiles, tunnel_rows)


