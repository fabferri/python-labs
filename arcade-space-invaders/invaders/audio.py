import math
import random
from array import array

import pygame


class SoundEngine:
    def __init__(self) -> None:
        self.enabled = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.alien_step_cycle = 0
        self.background_on = True

        try:
            pygame.mixer.pre_init(44100, -16, 1, 512)
            pygame.mixer.init()
            self.enabled = True
            self._build_sounds()
        except pygame.error:
            self.enabled = False

    def _tone(
        self,
        frequency: float,
        duration: float,
        volume: float = 0.3,
        wave_type: str = "square",
        decay: bool = False,
    ) -> pygame.mixer.Sound:
        sample_rate = 44100
        sample_count = max(1, int(duration * sample_rate))
        samples = array("h")

        for i in range(sample_count):
            t = i / sample_rate
            amp = volume
            if decay:
                amp *= max(0.0, 1.0 - (i / sample_count))

            if wave_type == "square":
                value = 1.0 if math.sin(2.0 * math.pi * frequency * t) >= 0 else -1.0
            elif wave_type == "saw":
                frac = (t * frequency) % 1.0
                value = 2.0 * frac - 1.0
            elif wave_type == "noise":
                value = random.uniform(-1.0, 1.0)
            else:
                value = math.sin(2.0 * math.pi * frequency * t)

            samples.append(int(32767 * amp * value))

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _chirp(
        self,
        start_freq: float,
        end_freq: float,
        duration: float,
        volume: float = 0.3,
    ) -> pygame.mixer.Sound:
        sample_rate = 44100
        sample_count = max(1, int(duration * sample_rate))
        samples = array("h")

        for i in range(sample_count):
            progress = i / sample_count
            freq = start_freq + (end_freq - start_freq) * progress
            t = i / sample_rate
            amp = volume * (1.0 - progress)
            value = math.sin(2.0 * math.pi * freq * t)
            samples.append(int(32767 * amp * value))

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _build_sounds(self) -> None:
        self.sounds["shoot"] = self._chirp(1200, 380, 0.12, volume=0.22)
        self.sounds["alien_hit"] = self._tone(220, 0.08, volume=0.28, wave_type="square", decay=True)
        self.sounds["player_hit"] = self._chirp(260, 90, 0.25, volume=0.34)
        self.sounds["ufo"] = self._tone(420, 0.3, volume=0.14, wave_type="saw")
        self.sounds["step_0"] = self._tone(180, 0.06, volume=0.16, wave_type="square")
        self.sounds["step_1"] = self._tone(210, 0.06, volume=0.16, wave_type="square")
        self.sounds["step_2"] = self._tone(240, 0.06, volume=0.16, wave_type="square")
        self.sounds["step_3"] = self._tone(270, 0.06, volume=0.16, wave_type="square")
        self.sounds["bg_loop"] = self._build_background_loop()

    def _build_background_loop(self) -> pygame.mixer.Sound:
        sample_rate = 44100
        beat_duration = 0.22
        notes = [92.5, 110.0, 82.4, 73.4, 92.5, 110.0, 82.4, 65.4]
        loop_duration = beat_duration * len(notes)
        sample_count = max(1, int(loop_duration * sample_rate))
        samples = array("h")

        for i in range(sample_count):
            t = i / sample_rate
            beat_index = int(t / beat_duration) % len(notes)
            note = notes[beat_index]

            in_beat = (t % beat_duration) / beat_duration
            envelope = (1.0 - in_beat) ** 1.9

            square_bass = 1.0 if math.sin(2.0 * math.pi * note * t) >= 0 else -1.0
            sub = math.sin(2.0 * math.pi * (note / 2.0) * t)

            click = 0.0
            if in_beat < 0.08:
                click = random.uniform(-1.0, 1.0) * (1.0 - in_beat / 0.08)

            value = (0.68 * square_bass + 0.24 * sub) * envelope + 0.08 * click
            samples.append(int(32767 * 0.14 * value))

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, key: str) -> None:
        if self.enabled and key in self.sounds:
            self.sounds[key].play()

    def play_alien_step(self) -> None:
        if not self.enabled:
            return
        key = f"step_{self.alien_step_cycle}"
        self.play(key)
        self.alien_step_cycle = (self.alien_step_cycle + 1) % 4

    def start_background(self) -> None:
        if not self.enabled or not self.background_on:
            return
        self.sounds["bg_loop"].play(loops=-1)

    def stop_background(self) -> None:
        if not self.enabled:
            return
        self.sounds["bg_loop"].stop()

    def toggle_background(self) -> None:
        self.background_on = not self.background_on
        if self.background_on:
            self.start_background()
        else:
            self.stop_background()
