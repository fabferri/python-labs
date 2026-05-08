from typing import Protocol


class AudioPort(Protocol):
    def play(self, key: str) -> None:
        ...

    def play_alien_step(self) -> None:
        ...


class KeyState(Protocol):
    def __getitem__(self, key: int) -> bool:
        ...


class ActionInput(Protocol):
    def pressed(self, action: str) -> bool:
        ...
