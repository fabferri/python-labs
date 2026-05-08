import random

import pygame

from .audio import SoundEngine
from .config import FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from .factories import create_starfield, spawn_aliens, spawn_bunkers
from .geometry import Rect
from .input import PygameActionInput
from .renderer import GameRenderer
from .services import PlayerController, WaveManager, WorldUpdater
from .state import GameState


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Space Invaders Arcade")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.sound = SoundEngine()
        self.renderer = GameRenderer(self.screen)
        self.player_controller = PlayerController()
        self.world_updater = WorldUpdater()
        self.wave_manager = WaveManager()
        self.sound.start_background()

        self.state = GameState()
        self.state.starfield = create_starfield()
        self.state.show_intro = True

    def reset(self, full_reset: bool = False, skip_intro: bool = False) -> None:
        if full_reset:
            self.state.score = 0
            self.state.wave = 1
            self.state.lives = 3
        else:
            self.state.wave += 1

        self.state.player = Rect(SCREEN_WIDTH // 2 - 24, SCREEN_HEIGHT - 46, 48, 20)
        self.state.player_cooldown = 0.0
        self.state.player_invuln = 0.0

        self.state.bullets.clear()
        self.state.explosions.clear()

        self.state.aliens = spawn_aliens()
        self.state.alien_direction = 1
        self.state.alien_step_timer = 0.0
        self.state.enemy_fire_timer = 0.5

        self.state.bunker_blocks = spawn_bunkers()

        self.state.mystery_ship = None
        self.state.mystery_spawn_timer = random.uniform(8.0, 14.0)

        self.state.game_over = False
        if skip_intro:
            self.state.show_intro = False
        self.state.victory_flash = 0.0

    def _update_player(self, dt: float, controls: PygameActionInput) -> None:
        self.player_controller.update(self.state, dt, controls, self.sound)

    def _update_world(self, dt: float) -> None:
        self.world_updater.update(self.state, dt, self.sound)
        self.wave_manager.update(self.state, dt, on_next_wave=lambda: self.reset(full_reset=False, skip_intro=True))

    def _update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        controls = PygameActionInput(keys)

        if self.state.show_intro:
            if controls.pressed("start_game"):
                self.reset(full_reset=True, skip_intro=True)
            return

        if self.state.game_over:
            if controls.pressed("restart"):
                self.reset(full_reset=True, skip_intro=True)
            return

        self._update_player(dt, controls)
        self._update_world(dt)

    def run(self) -> None:
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    action = PygameActionInput.action_for_key(event.key)
                    if action == "quit":
                        running = False
                    elif action == "toggle_music":
                        self.sound.toggle_background()

            self._update(dt)
            self.renderer.draw(self.state)

        self.sound.stop_background()
        pygame.quit()
