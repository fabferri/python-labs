from dataclasses import dataclass


@dataclass
class Bullet:
    x: float
    y: float
    dy: float
    from_enemy: bool


@dataclass
class Alien:
    x: float
    y: float
    w: int
    h: int
    points: int
    alive: bool = True


@dataclass
class Explosion:
    x: float
    y: float
    ttl: float
    max_ttl: float


@dataclass
class MysteryShip:
    x: float
    y: float
    w: int
    h: int
    dx: float
    alive: bool = True
