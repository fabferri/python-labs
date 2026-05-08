import unittest

from brickbreaker import config
from brickbreaker.factories import create_initial_state
from brickbreaker.systems import update_world


class SystemTests(unittest.TestCase):
    def test_update_world_returns_idle_when_paused(self) -> None:
        state = create_initial_state()
        state.menu_active = False
        state.started = True
        state.paused = True

        outcome = update_world(state)

        self.assertEqual("idle", outcome)

    def test_ball_bounces_from_left_wall(self) -> None:
        state = create_initial_state()
        state.menu_active = False
        state.started = True
        state.paused = False
        state.high_score = 999999

        state.ball.rect.left = -2
        state.ball.velocity.x = -4
        state.ball.velocity.y = 0

        update_world(state)

        self.assertGreater(state.ball.velocity.x, 0)
        self.assertEqual(0, state.ball.rect.left)

    def test_ball_bounces_from_right_wall(self) -> None:
        state = create_initial_state()
        state.menu_active = False
        state.started = True
        state.paused = False
        state.high_score = 999999

        state.ball.rect.right = config.SCREEN_WIDTH + 2
        state.ball.velocity.x = 4
        state.ball.velocity.y = 0

        update_world(state)

        self.assertLess(state.ball.velocity.x, 0)
        self.assertEqual(config.SCREEN_WIDTH, state.ball.rect.right)

    def test_ball_bounces_from_top_wall(self) -> None:
        state = create_initial_state()
        state.menu_active = False
        state.started = True
        state.paused = False
        state.high_score = 999999

        state.ball.rect.top = -2
        state.ball.velocity.x = 0
        state.ball.velocity.y = -4

        update_world(state)

        self.assertGreater(state.ball.velocity.y, 0)
        self.assertEqual(0, state.ball.rect.top)

    def test_paddle_collision_returns_paddle_outcome(self) -> None:
        state = create_initial_state()
        state.menu_active = False
        state.started = True
        state.paused = False
        state.high_score = 999999

        state.ball.rect.centerx = state.paddle.rect.centerx
        state.ball.rect.bottom = state.paddle.rect.top + 1
        state.ball.velocity.x = 0
        state.ball.velocity.y = 5

        outcome = update_world(state)

        self.assertEqual("paddle", outcome)
        self.assertLess(state.ball.velocity.y, 0)

    def test_brick_collision_removes_brick_and_scores(self) -> None:
        state = create_initial_state()
        state.menu_active = False
        state.started = True
        state.paused = False
        state.high_score = 999999

        target = next(brick for brick in state.bricks if brick.alive)
        state.ball.rect.center = target.rect.center
        state.ball.velocity.x = 0
        state.ball.velocity.y = 0

        before_score = state.score
        outcome = update_world(state)

        self.assertEqual("brick", outcome)
        self.assertFalse(target.alive)
        self.assertGreater(state.score, before_score)

    def test_ball_below_screen_sets_game_over_when_out_of_lives(self) -> None:
        state = create_initial_state()
        state.menu_active = False
        state.started = True
        state.paused = False
        state.lives = 1

        state.ball.rect.top = config.SCREEN_HEIGHT + 10
        state.ball.velocity.x = 0
        state.ball.velocity.y = 0

        outcome = update_world(state)

        self.assertEqual("game-over", outcome)
        self.assertTrue(state.game_over)
        self.assertFalse(state.started)

    def test_ball_below_screen_with_remaining_lives_resets_ball(self) -> None:
        state = create_initial_state()
        state.menu_active = False
        state.started = True
        state.paused = False
        state.lives = 2

        state.ball.rect.top = config.SCREEN_HEIGHT + 10
        state.ball.velocity.x = 0
        state.ball.velocity.y = 0

        outcome = update_world(state)

        self.assertEqual("life-lost", outcome)
        self.assertFalse(state.game_over)
        self.assertEqual(1, state.lives)
        self.assertFalse(state.started)

    def test_level_cleared_when_all_bricks_are_destroyed(self) -> None:
        state = create_initial_state()
        state.menu_active = False
        state.started = True
        state.paused = False
        state.high_score = 999999

        for brick in state.bricks:
            brick.alive = False

        outcome = update_world(state)

        self.assertEqual("level-cleared", outcome)
        self.assertTrue(state.level_cleared)
        self.assertFalse(state.started)


if __name__ == "__main__":
    unittest.main()
