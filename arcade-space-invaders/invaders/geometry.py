from dataclasses import dataclass


@dataclass
class Rect:
    x: float
    y: float
    w: int
    h: int

    @property
    def width(self) -> int:
        return self.w

    @property
    def height(self) -> int:
        return self.h

    @property
    def centerx(self) -> int:
        return int(self.x + self.w / 2)

    @property
    def centery(self) -> int:
        return int(self.y + self.h / 2)

    @property
    def topleft(self) -> tuple[int, int]:
        return int(self.x), int(self.y)

    def collidepoint(self, px: float, py: float) -> bool:
        return self.x <= px < self.x + self.w and self.y <= py < self.y + self.h
