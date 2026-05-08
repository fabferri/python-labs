from __future__ import annotations

import sys

import pygame

from . import config
from .audio import AudioManager
from .factories import create_initial_state
from .input import PygameActionInput
from .renderer import GameRenderer
from .services import EventController, PlayerController, WorldUpdater


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Brick Breaker Arcade")
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.audio = AudioManager()
        self.renderer = GameRenderer(self.screen)
        self.player_controller = PlayerController()
        self.event_controller = EventController()
        self.world_updater = WorldUpdater()

        self.state = create_initial_state()

    def _play_action_sound(self, action: str | None) -> None:
        if not self.state.sfx_enabled or not action:
            return

        if action in {"start", "launch", "restart", "next-level", "sfx-on"}:
            self.audio.play_start()

    def _play_world_sound(self, outcome: str) -> None:
        if not self.state.sfx_enabled:
            return

        if outcome == "brick":
            self.audio.play_hit()
        elif outcome == "paddle":
            self.audio.play_paddle()
        elif outcome in {"life-lost", "game-over"}:
            self.audio.play_lose_life()
        elif outcome == "level-cleared":
            self.audio.play_level_clear()

    def run(self) -> None:
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    action_name = PygameActionInput.action_for_key(event.key)
                    action_result = self.event_controller.handle_action(self.state, action_name)
                    self._play_action_sound(action_result)

            controls = PygameActionInput(pygame.key.get_pressed())
            self.player_controller.update(self.state, controls)
            outcome = self.world_updater.update(self.state)
            self._play_world_sound(outcome)

            self.renderer.draw(self.state)
            self.clock.tick(config.FPS)

        pygame.quit()
        sys.exit()
