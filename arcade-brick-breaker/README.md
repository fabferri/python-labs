# Brick Breaker Arcade (Python)

A modular Brick Breaker game inspired by classic arcade gameplay.

## Features

- Start menu screen
- Pause/resume with `ESC`
- Multi-level progression with increased difficulty
- Retro generated sound effects (no constant background tone)
- Persistent high score saved to `high_score.json`

## Quick Start (Windows PowerShell)

From the project root:

```powershell
.\start_game.ps1
```

## Controls

- Move paddle: `Left/Right` or `A/D`
- Start game / Launch ball: `Space`
- Next level after clear: `Space`
- Pause / Resume: `ESC`
- Return to menu after game over / level clear: `ESC`
- Toggle sound effects: `M`

## Tech

- Python 3.11+
- pygame

## Project Structure

- `main.py`: thin entry point that starts the game
- `brickbreaker/config.py`: gameplay constants and palette
- `brickbreaker/models.py`: entity dataclasses (`Paddle`, `Ball`, `Brick`)
- `brickbreaker/state.py`: single mutable game state container
- `brickbreaker/factories.py`: object/state creation and high score persistence
- `brickbreaker/ports.py`: protocol interfaces for input/audio dependencies
- `brickbreaker/input.py`: `pygame` key adapter to semantic actions
- `brickbreaker/services.py`: orchestrates player input, action handling, and world updates
- `brickbreaker/systems.py`: deterministic gameplay systems (physics, collisions, scoring)
- `brickbreaker/audio.py`: generated arcade-style audio manager
- `brickbreaker/renderer.py`: all drawing and HUD rendering
- `brickbreaker/game.py`: runtime orchestration loop and wiring
- `requirements.txt`: Python dependencies
- `start_game.ps1`: creates/uses `.venv`, installs deps, starts the game

## Architecture Boundaries

### Dependency Direction

```text
runtime/orchestration (game.py, main.py)
		    ↑
	    adapters (input.py, renderer.py, audio.py)
		    ↑
	    services (services.py)
		    ↑
	    domain (state.py, models.py, systems.py, factories.py, config.py)
```

### Layer Responsibilities

- Domain layer: `state.py`, `models.py`, `systems.py`, `factories.py`, `config.py`
- Service layer: `services.py`
- Adapter layer: `input.py`, `renderer.py`, `audio.py`
- Runtime/orchestration: `game.py`, `main.py`

## Unit Tests

Run all unit tests (default):

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Run all unit tests with verbose output:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Run one test file:

```powershell
python -m unittest tests.test_systems -v
```

Run one test class:

```powershell
python -m unittest tests.test_services.ServiceTests -v
```

Run one specific test method:

```powershell
python -m unittest tests.test_input.InputTests.test_action_for_key_maps_space_to_start_launch -v
```

Run tests using `.venv` Python directly:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

Stop on first failure:

```powershell
python -m unittest discover -s tests -p "test_*.py" -f
```

Show buffered output only for failing tests:

```powershell
python -m unittest discover -s tests -p "test_*.py" -b
```

### Unit Test Scope

**`tests/test_input.py`** — 5 tests

| Test | What it verifies |
|---|---|
| `test_pressed_reports_true_for_mapped_action` | Correct key → action mapping |
| `test_action_for_key_maps_space_to_start_launch` | SPACE maps to `start_launch` |
| `test_pressed_returns_false_for_unknown_action` | Unknown actions return false |
| `test_action_for_key_returns_none_for_unmapped_key` | Unmapped key returns `None` |
| `test_action_for_key_supports_custom_keymap` | Custom keymap override works |

**`tests/test_services.py`** — 7 tests

| Test | What it verifies |
|---|---|
| `test_start_action_from_menu_starts_game` | Menu → active game transition |
| `test_toggle_sfx_action_flips_state` | SFX flag toggles correctly |
| `test_pause_menu_toggles_pause_when_game_running` | Pause/resume cycle |
| `test_pause_menu_returns_to_menu_after_game_over` | Game over → back to menu |
| `test_start_launch_advances_from_level_cleared` | Level progression |
| `test_player_controller_moves_left_and_clamps_at_screen_edge` | Left boundary clamping |
| `test_player_controller_moves_right_and_clamps_at_screen_edge` | Right boundary clamping |

**`tests/test_systems.py`** — 9 tests

| Test | What it verifies |
|---|---|
| `test_update_world_returns_idle_when_paused` | No updates while paused |
| `test_ball_bounces_from_left_wall` | Left wall reflection |
| `test_ball_bounces_from_right_wall` | Right wall reflection |
| `test_ball_bounces_from_top_wall` | Top wall reflection |
| `test_paddle_collision_returns_paddle_outcome` | Paddle bounce + velocity inversion |
| `test_brick_collision_removes_brick_and_scores` | Brick destroyed + score incremented |
| `test_ball_below_screen_sets_game_over_when_out_of_lives` | Last life → game over |
| `test_ball_below_screen_with_remaining_lives_resets_ball` | Life lost, ball resets |
| `test_level_cleared_when_all_bricks_are_destroyed` | All bricks gone → level cleared |

### Common Issues

- `ModuleNotFoundError`: run tests from project root (same folder as `main.py`).
- Wrong interpreter: prefer `.\.venv\Scripts\python.exe` if your shell is not using `.venv`.
- Failing local dependency setup: run `pip install -r requirements.txt` again in the active virtual environment.

### Recommended Local Test Workflow

Fast check while coding:

```powershell
python -m unittest tests.test_systems -v
```

Full verification before commit:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

If a failure appears and you want to isolate quickly:

```powershell
python -m unittest tests.test_systems.SystemTests.test_paddle_collision_returns_paddle_outcome -v
```

## Run (Windows PowerShell)

```powershell
cd c:\Users\fabferri\Desktop\arcade-brick-braker
.\start_game.ps1
```

## Manual Virtual Environment Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## Continuous Integration

GitHub Actions runs unit tests automatically for pushes and pull requests targeting `main`, plus manual runs via workflow dispatch.

- Workflow: `.github/workflows/tests.yml`
- Python matrix: `3.11`, `3.12`, `3.13`


`Tag: arcade, game, python` <br>
`date: 08-05-2026`
