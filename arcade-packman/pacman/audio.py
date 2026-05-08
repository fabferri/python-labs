# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Procedural audio engine and playback controls.

from __future__ import annotations

import io
import math
import wave
from array import array

import pygame


class AudioManager:
    # Initialize object state and dependencies.
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.available = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self._init_mixer()

    # Helper: Init Mixer.
    def _init_mixer(self) -> None:
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=256)
            self.available = True
            self.sounds = {
                "pellet": self._build_tone(880, 0.05, 0.2),
                "rare": self._build_tone(1260, 0.08, 0.24),
                "death": self._build_sweep(520, 140, 0.35, 0.35),
                "win": self._build_chord([523, 659, 784], 0.4, 0.28),
            }
        except pygame.error:
            self.available = False

    # Helper: Build Tone.
    def _build_tone(self, freq_hz: float, seconds: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        count = int(sample_rate * seconds)
        pcm = array("h")
        for i in range(count):
            t = i / sample_rate
            amp = int(32767 * volume)
            sample = int(amp * math.sin(2 * math.pi * freq_hz * t))
            sample = int(sample * (1 - (i / max(1, count - 1))))
            pcm.append(sample)
        return self._sound_from_pcm(pcm, sample_rate)

    # Helper: Build Sweep.
    def _build_sweep(self, start_hz: float, end_hz: float, seconds: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        count = int(sample_rate * seconds)
        pcm = array("h")
        for i in range(count):
            t = i / sample_rate
            f = start_hz + (end_hz - start_hz) * (i / max(1, count - 1))
            amp = int(32767 * volume)
            sample = int(amp * math.sin(2 * math.pi * f * t))
            pcm.append(sample)
        return self._sound_from_pcm(pcm, sample_rate)

    # Helper: Build Chord.
    def _build_chord(self, freqs: list[int], seconds: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        count = int(sample_rate * seconds)
        pcm = array("h")
        for i in range(count):
            t = i / sample_rate
            mixed = sum(math.sin(2 * math.pi * f * t) for f in freqs) / max(1, len(freqs))
            env = 1 - (i / max(1, count - 1))
            sample = int(32767 * volume * env * mixed)
            pcm.append(sample)
        return self._sound_from_pcm(pcm, sample_rate)

    # Helper: Sound From Pcm.
    def _sound_from_pcm(self, pcm: array, sample_rate: int) -> pygame.mixer.Sound:
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(pcm.tobytes())
        buffer.seek(0)
        return pygame.mixer.Sound(file=buffer)

    # Toggle.
    def toggle(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled

    # Play.
    def play(self, key: str) -> None:
        if self.enabled and self.available and key in self.sounds:
            self.sounds[key].play()


