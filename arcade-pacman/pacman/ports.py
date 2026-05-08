# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Protocol interfaces for adapter abstractions.

from __future__ import annotations

from typing import Protocol


class AudioPort(Protocol):
    enabled: bool

    # Toggle.
    def toggle(self) -> bool:
        ...

    # Play.
    def play(self, key: str) -> None:
        ...


class KeyState(Protocol):
    # Helper: Getitem.
    def __getitem__(self, key: int) -> bool:
        ...


class ActionInput(Protocol):
    # Pressed.
    def pressed(self, action: str) -> bool:
        ...


