from __future__ import annotations

import array
import math

import pygame


def _build_tone(frequency: float, duration: float, volume: float = 0.25, sample_rate: int = 44100) -> pygame.mixer.Sound:
    sample_count = max(1, int(sample_rate * duration))
    samples = array.array("h")
    amplitude = int(32767 * volume)

    for i in range(sample_count):
        t = i / sample_rate
        sample = int(amplitude * math.sin(2 * math.pi * frequency * t))
        samples.append(sample)

    return pygame.mixer.Sound(buffer=samples)


class AudioManager:
    def __init__(self) -> None:
        self.enabled = False
        self.hit_sound: pygame.mixer.Sound | None = None
        self.paddle_sound: pygame.mixer.Sound | None = None
        self.lose_life_sound: pygame.mixer.Sound | None = None
        self.level_clear_sound: pygame.mixer.Sound | None = None
        self.start_sound: pygame.mixer.Sound | None = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1)
            self.enabled = True
        except pygame.error:
            self.enabled = False
            return

        self.hit_sound = _build_tone(700.0, 0.04, 0.22)
        self.paddle_sound = _build_tone(420.0, 0.05, 0.20)
        self.lose_life_sound = _build_tone(170.0, 0.26, 0.25)
        self.level_clear_sound = _build_tone(940.0, 0.20, 0.22)
        self.start_sound = _build_tone(560.0, 0.12, 0.18)

    def play_hit(self) -> None:
        if self.enabled and self.hit_sound:
            self.hit_sound.play()

    def play_paddle(self) -> None:
        if self.enabled and self.paddle_sound:
            self.paddle_sound.play()

    def play_lose_life(self) -> None:
        if self.enabled and self.lose_life_sound:
            self.lose_life_sound.play()

    def play_level_clear(self) -> None:
        if self.enabled and self.level_clear_sound:
            self.level_clear_sound.play()

    def play_start(self) -> None:
        if self.enabled and self.start_sound:
            self.start_sound.play()
