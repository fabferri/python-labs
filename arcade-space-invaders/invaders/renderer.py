import pygame

from .config import BLACK, DIM_GREEN, GREEN, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from .sprites import ArcadeSpriteSheet
from .state import GameState


class GameRenderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.SysFont("consolas", 24)
        self.big_font = pygame.font.SysFont("consolas", 44, bold=True)
        self.sprites = ArcadeSpriteSheet()

    def draw(self, state: GameState) -> None:
        self.screen.fill(BLACK)
        self._draw_starfield(state)

        if state.show_intro:
            self._draw_intro()
        elif state.game_over:
            self._draw_hud(state)
            self._draw_game_over()
        else:
            self._draw_hud(state)
            self._draw_bunkers(state)
            self._draw_aliens(state)
            self._draw_mystery_ship(state)
            self._draw_player(state)
            self._draw_bullets(state)
            self._draw_explosions(state)

        pygame.display.flip()

    def _draw_starfield(self, state: GameState) -> None:
        for star in state.starfield:
            color = (30, 88, 45) if star[2] == 1 else (55, 160, 88)
            pygame.draw.rect(self.screen, color, (star[0], star[1], star[2], star[2]))

    def _draw_player(self, state: GameState) -> None:
        if state.player_invuln > 0 and int(state.player_invuln * 15) % 2 == 0:
            return

        sprite = self.sprites.get("player", size=(state.player.w, state.player.h))
        self.screen.blit(sprite, state.player.topleft)

    def _draw_aliens(self, state: GameState) -> None:
        frame = (pygame.time.get_ticks() // 220) % 2
        for alien in state.aliens:
            if not alien.alive:
                continue

            if alien.points >= 40:
                sprite_name = "alien_top"
            elif alien.points >= 20:
                sprite_name = "alien_mid"
            else:
                sprite_name = "alien_bot"

            sprite = self.sprites.get(sprite_name, frame=frame, size=(alien.w, alien.h))
            self.screen.blit(sprite, (int(alien.x), int(alien.y)))

    def _draw_bunkers(self, state: GameState) -> None:
        block_sprite = self.sprites.get("bunker_block")
        for block in state.bunker_blocks:
            sprite = pygame.transform.scale(block_sprite, (block.w, block.h))
            self.screen.blit(sprite, block.topleft)

    def _draw_mystery_ship(self, state: GameState) -> None:
        if not state.mystery_ship:
            return

        sprite = self.sprites.get("ufo", size=(state.mystery_ship.w, state.mystery_ship.h))
        self.screen.blit(sprite, (int(state.mystery_ship.x), int(state.mystery_ship.y)))

    def _draw_bullets(self, state: GameState) -> None:
        for bullet in state.bullets:
            sprite_name = "bullet_enemy" if bullet.from_enemy else "bullet_player"
            sprite = self.sprites.get(sprite_name, size=(4, 10))
            self.screen.blit(sprite, (int(bullet.x - 2), int(bullet.y - 8)))

    def _draw_explosions(self, state: GameState) -> None:
        for explosion in state.explosions:
            progress = explosion.ttl / explosion.max_ttl
            radius = int((1.0 - progress) * 16) + 4
            color = (255, int(210 * progress), int(90 * progress))
            pygame.draw.circle(self.screen, color, (int(explosion.x), int(explosion.y)), radius, width=2)

    def _draw_hud(self, state: GameState) -> None:
        top_bar = self.font.render(f"SCORE {state.score:06d}   WAVE {state.wave}", True, WHITE)
        lives = self.font.render(f"LIVES {state.lives}", True, WHITE)
        self.screen.blit(top_bar, (20, 12))
        self.screen.blit(lives, (SCREEN_WIDTH - lives.get_width() - 20, 12))

        pygame.draw.line(self.screen, DIM_GREEN, (18, 46), (SCREEN_WIDTH - 18, 46), 2)

    def _draw_intro(self) -> None:
        title = self.big_font.render("SPACE INVADERS", True, GREEN)
        subtitle = self.font.render("Press SPACE to Start", True, WHITE)
        
        controls_y = SCREEN_HEIGHT // 2 + 20
        controls = [
            "CONTROLS:",
            "A / LEFT ARROW  - Move Left",
            "D / RIGHT ARROW - Move Right",
            "SPACE - Shoot",
            "M - Toggle Music",
            "ESC - Quit",
        ]
        
        small_font = pygame.font.SysFont("consolas", 18)
        self.screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 60))
        self.screen.blit(subtitle, ((SCREEN_WIDTH - subtitle.get_width()) // 2, 140))
        
        for i, line in enumerate(controls):
            color = GREEN if i == 0 else WHITE
            font = self.font if i == 0 else small_font
            text = font.render(line, True, color)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - 150, controls_y + i * 28))
        
        sound_status = small_font.render("Sound: ON (Press M to toggle)", True, GREEN)
        self.screen.blit(sound_status, (20, SCREEN_HEIGHT - 40))

    def _draw_game_over(self) -> None:
        title = self.big_font.render("GAME OVER", True, RED)
        hint = self.font.render("Press R to restart", True, WHITE)

        self.screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(hint, ((SCREEN_WIDTH - hint.get_width()) // 2, SCREEN_HEIGHT // 2 + 18))
