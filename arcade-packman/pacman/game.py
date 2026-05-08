# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Runtime orchestration for input, updates, and rendering.

from __future__ import annotations

import pygame

from .audio import AudioManager
from .config import CFG, DIFFICULTIES, PELLET_TYPES
from .entities import Player
from .input import PygameActionInput
from .level import get_level_count, load_level
from .player_service import PlayerController
from .renderer import GameRenderer
from .session_service import SessionService
from .sprites import SpriteBank
from .state import GameState
from .storage import load_high_score, save_high_score
from .world_service import WorldUpdater


class Game:
    # Initialize runtime dependencies and starting game state.
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(CFG.title)
        self.screen = pygame.display.set_mode((CFG.screen_width, CFG.screen_height))
        self.clock = pygame.time.Clock()

        self.audio = AudioManager(enabled=CFG.audio_enabled)
        self.sprites = SpriteBank(CFG.tile_size)
        self.renderer = GameRenderer(self.screen)
        self.session = SessionService()
        self.player_controller = PlayerController()
        self.world_updater = WorldUpdater()

        level = load_level(0)
        player_spawn = level.player_spawns[0] if level.player_spawns else (14, 18)
        player = Player(player_spawn, CFG.tile_size, CFG.player_speed)
        self.state = GameState(
            level_count=get_level_count(),
            level=level,
            player=player,
            player_spawn=player_spawn,
            high_score=load_high_score(),
            pellets={pellet_type: set() for pellet_type in PELLET_TYPES},
        )
        self.session.load_current_level(self.state)

    # Handle one keydown action based on the current game state.
    def _handle_keydown(self, event: pygame.event.Event, action: str | None) -> bool:
        if action == "quit":
            return False

        if action == "toggle_audio":
            self.audio.toggle()

        if self.state.game_state == "menu":
            if action == "toggle_audio_menu":
                self.audio.toggle()
            elif action == "start_game":
                self.session.start_new_game(self.state)
            elif action == "difficulty_next":
                self.state.selected_difficulty = (self.state.selected_difficulty + 1) % len(DIFFICULTIES)
            elif action == "difficulty_prev":
                self.state.selected_difficulty = (self.state.selected_difficulty - 1) % len(DIFFICULTIES)
            elif action == "difficulty_easy":
                self.state.selected_difficulty = 0
            elif action == "difficulty_normal":
                self.state.selected_difficulty = 1
            elif action == "difficulty_hard":
                self.state.selected_difficulty = 2
            elif action == "next_theme":
                self.state.selected_theme = (self.state.selected_theme + 1) % len(self.sprites.pacman_styles)
        elif self.state.game_state in ("game_over", "campaign_win") and action == "restart":
            self.state.game_state = "menu"
        else:
            if event.type == pygame.KEYDOWN:
                self.player_controller.handle_action(self.state, action)

        return True

    # Process queued pygame events and translate them into actions.
    def _process_events(self) -> bool:
        running = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                action = PygameActionInput.action_for_key(event.key)
                running = self._handle_keydown(event, action)
                if not running:
                    return False
        return True

    # Advance game simulation by one frame.
    def _update(self) -> None:
        events = self.world_updater.update(self.state, PELLET_TYPES)

        for sound_key in events.sounds:
            self.audio.play(sound_key)
        if events.high_score_changed:
            save_high_score(self.state.high_score)
        if events.request_load_current_level:
            self.session.load_current_level(self.state)
        elif events.request_reset_positions:
            self.session.reset_positions(self.state)

    # Render the current frame.
    def _draw(self) -> None:
        self.renderer.draw(
            state=self.state,
            sprites=self.sprites,
            sound_enabled=self.audio.enabled,
            difficulty_name=self.session.current_difficulty(self.state).name,
            theme_name=self.session.current_theme_name(self.state, self.sprites.pacman_theme_names),
            pellet_types=PELLET_TYPES,
        )

    # Run the main game loop until exit.
    def run(self) -> None:
        running = True
        while running:
            self.state.dt = self.clock.tick(CFG.fps) / 1000.0
            self.state.elapsed_time += self.state.dt

            running = self._process_events()
            if not running:
                break

            self._update()
            self._draw()

        pygame.quit()


# Convenience entrypoint that runs the Game loop.
def run() -> None:
    Game().run()

