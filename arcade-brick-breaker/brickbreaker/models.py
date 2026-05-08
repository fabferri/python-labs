from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class Paddle:
    rect: pygame.Rect
    speed: int


@dataclass
class Ball:
    rect: pygame.Rect
    velocity: pygame.Vector2


@dataclass
class Brick:
    rect: pygame.Rect
    color: tuple[int, int, int]
    alive: bool = True
