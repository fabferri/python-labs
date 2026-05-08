import unittest
from unittest.mock import patch

from invaders.geometry import Rect
from invaders.models import Alien, Bullet, Explosion, MysteryShip
from invaders.services import PlayerController, WaveManager, WorldUpdater
from invaders.state import GameState


class _SoundStub:
    def __init__(self) -> None:
        self.played: list[str] = []

    def play(self, key: str) -> None:
        self.played.append(key)

    def play_alien_step(self) -> None:
        return


class _ControlStub:
    def __init__(self, pressed_actions: set[str] | None = None) -> None:
        self._pressed_actions = pressed_actions or set()

    def pressed(self, action: str) -> bool:
        return action in self._pressed_actions


class ServiceTests(unittest.TestCase):
    def test_player_controller_moves_and_fires(self) -> None:
        controller = PlayerController()
        state = GameState()
        state.player = Rect(100, 520, 48, 20)
        sound = _SoundStub()
        controls = _ControlStub({"move_right", "shoot"})

        controller.update(state, dt=0.1, controls=controls, sound=sound)

        self.assertGreater(state.player.x, 100)
        self.assertEqual(len(state.bullets), 1)
        self.assertIn("shoot", sound.played)

    def test_player_controller_does_not_exceed_two_player_bullets(self) -> None:
        controller = PlayerController()
        state = GameState()
        state.player = Rect(100, 520, 48, 20)
        sound = _SoundStub()
        controls = _ControlStub({"shoot"})

        state.bullets.append(Bullet(x=110, y=510, dy=-500, from_enemy=False))
        state.bullets.append(Bullet(x=120, y=500, dy=-500, from_enemy=False))

        controller.update(state, dt=0.016, controls=controls, sound=sound)

        self.assertEqual(len([b for b in state.bullets if not b.from_enemy]), 2)
        self.assertEqual(sound.played, [])

    def test_wave_manager_triggers_callback_after_flash(self) -> None:
        manager = WaveManager()
        state = GameState(game_over=False)
        state.aliens = [Alien(x=10, y=10, w=10, h=10, points=10, alive=False)]
        called = {"value": False}

        def _next_wave() -> None:
            called["value"] = True

        manager.update(state, dt=0.8, on_next_wave=_next_wave)

        self.assertTrue(called["value"])
        self.assertEqual(state.victory_flash, 0.0)

    def test_world_updater_cleans_up_expired_explosions_and_offscreen_ship(self) -> None:
        updater = WorldUpdater()
        state = GameState()
        state.aliens = []
        state.mystery_ship = MysteryShip(x=-100, y=40, w=50, h=20, dx=-50)
        state.explosions = [Explosion(x=10, y=10, ttl=0.01, max_ttl=0.01)]
        sound = _SoundStub()

        with patch("invaders.services.step_aliens", return_value=None), patch(
            "invaders.services.try_enemy_fire", return_value=None
        ), patch("invaders.services.handle_collisions", return_value=None), patch(
            "invaders.services.check_lose_by_descent", return_value=None
        ):
            updater.update(state, dt=0.02, sound=sound)

        self.assertEqual(state.explosions, [])
        self.assertIsNone(state.mystery_ship)


if __name__ == "__main__":
    unittest.main()
