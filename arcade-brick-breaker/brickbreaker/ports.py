from __future__ import annotations

from typing import Protocol


class KeyState(Protocol):
    def __getitem__(self, key: int) -> bool:
        ...


class ActionInput(Protocol):
    def pressed(self, action: str) -> bool:
        ...


class AudioPort(Protocol):
    def play_hit(self) -> None:
        ...

    def play_paddle(self) -> None:
        ...

    def play_lose_life(self) -> None:
        ...

    def play_level_clear(self) -> None:
        ...

    def play_start(self) -> None:
        ...
