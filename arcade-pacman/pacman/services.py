# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Compatibility re-export for split service modules.

from .player_service import PlayerController
from .session_service import SessionService
from .world_service import WorldUpdater

__all__ = ["SessionService", "PlayerController", "WorldUpdater"]

