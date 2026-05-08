import unittest

from invaders.config import ALIEN_DESCEND, SCREEN_HEIGHT
from invaders.geometry import Rect
from invaders.models import Alien, Bullet
from invaders.state import GameState
from invaders.systems import (
    check_lose_by_descent,
    damage_bunker_at,
    handle_collisions,
    step_aliens,
)


class _SoundStub:
    def __init__(self) -> None:
        self.played: list[str] = []
        self.step_calls = 0

    def play(self, key: str) -> None:
        self.played.append(key)

    def play_alien_step(self) -> None:
        self.step_calls += 1


class SystemsSmokeTests(unittest.TestCase):
    def test_step_aliens_moves_sideways_when_no_wall_hit(self) -> None:
        state = GameState(wave=1, alien_direction=1)
        state.aliens = [Alien(x=140.0, y=90.0, w=30, h=20, points=10, alive=True)]

        sound = _SoundStub()
        step_aliens(state, dt=1.0, sound=sound)

        self.assertEqual(state.aliens[0].x, 148.0)
        self.assertEqual(state.aliens[0].y, 90.0)
        self.assertEqual(state.alien_direction, 1)
        self.assertEqual(sound.step_calls, 1)

    def test_step_aliens_descends_and_flips_at_wall(self) -> None:
        state = GameState(wave=1, alien_direction=1)
        state.aliens = [Alien(x=760.0, y=100.0, w=30, h=20, points=10, alive=True)]

        sound = _SoundStub()
        step_aliens(state, dt=1.0, sound=sound)

        self.assertEqual(state.aliens[0].x, 760.0)
        self.assertEqual(state.aliens[0].y, 100.0 + ALIEN_DESCEND)
        self.assertEqual(state.alien_direction, -1)
        self.assertEqual(sound.step_calls, 1)

    def test_damage_bunker_at_removes_hit_block(self) -> None:
        state = GameState()
        state.bunker_blocks = [Rect(50, 50, 8, 8)]

        damaged = damage_bunker_at(state, x=52, y=52)

        self.assertTrue(damaged)
        self.assertEqual(len(state.bunker_blocks), 0)

    def test_handle_collisions_player_bullet_hits_alien(self) -> None:
        state = GameState(score=0)
        state.player = Rect(100, 520, 48, 20)
        state.aliens = [Alien(x=200.0, y=100.0, w=30, h=20, points=40, alive=True)]
        state.bunker_blocks = []
        state.bullets = [Bullet(x=205.0, y=105.0, dy=-500.0, from_enemy=False)]

        sound = _SoundStub()
        handle_collisions(state, sound)

        self.assertFalse(state.aliens[0].alive)
        self.assertEqual(state.score, 40)
        self.assertEqual(len(state.bullets), 0)
        self.assertIn("alien_hit", sound.played)

    def test_handle_collisions_enemy_bullet_hits_player(self) -> None:
        state = GameState(lives=3)
        state.player = Rect(100, 520, 48, 20)
        state.bunker_blocks = []
        state.bullets = [Bullet(x=state.player.centerx, y=state.player.centery, dy=220.0, from_enemy=True)]

        sound = _SoundStub()
        handle_collisions(state, sound)

        self.assertEqual(state.lives, 2)
        self.assertGreater(state.player_invuln, 0.0)
        self.assertFalse(state.game_over)
        self.assertIn("player_hit", sound.played)

    def test_check_lose_by_descent_triggers_game_over(self) -> None:
        state = GameState(game_over=False)
        state.player = Rect(100, 520, 48, 20)
        state.aliens = [Alien(x=100.0, y=float(state.player.y - 20), w=30, h=20, points=10, alive=True)]

        check_lose_by_descent(state)

        self.assertTrue(state.game_over)

    def test_enemy_bullet_out_of_bounds_is_removed(self) -> None:
        state = GameState(lives=3)
        state.player = Rect(100, 520, 48, 20)
        state.bunker_blocks = []
        state.bullets = [Bullet(x=10.0, y=SCREEN_HEIGHT + 5.0, dy=220.0, from_enemy=True)]

        sound = _SoundStub()
        handle_collisions(state, sound)

        self.assertEqual(len(state.bullets), 0)
        self.assertEqual(state.lives, 3)


if __name__ == "__main__":
    unittest.main()
