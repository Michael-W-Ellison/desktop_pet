"""
Phase 12: Game Base Framework

Base classes and framework for mini-games and activities.
"""
import time
from typing import Dict, Any, List, Optional, Callable
from enum import Enum


class GameDifficulty(Enum):
    """Game difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class GameState(Enum):
    """Game states."""
    NOT_STARTED = "not_started"
    READY = "ready"
    PLAYING = "playing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class GameResult:
    """Represents the result of a game session."""

    def __init__(self, game_name: str, success: bool, score: int = 0):
        """
        Initialize game result.

        Args:
            game_name: Name of the game
            success: Whether player succeeded
            score: Final score
        """
        self.game_name = game_name
        self.success = success
        self.score = score
        self.timestamp = time.time()
        self.duration_seconds: float = 0.0
        self.difficulty: GameDifficulty = GameDifficulty.MEDIUM

        # Rewards earned
        self.experience_earned: int = 0
        self.coins_earned: int = 0
        self.bonding_gained: float = 0.0

        # Statistics
        self.perfect_score: bool = False
        self.new_high_score: bool = False
        self.achievements_unlocked: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'game_name': self.game_name,
            'success': self.success,
            'score': self.score,
            'timestamp': self.timestamp,
            'duration_seconds': self.duration_seconds,
            'difficulty': self.difficulty.value,
            'experience_earned': self.experience_earned,
            'coins_earned': self.coins_earned,
            'bonding_gained': self.bonding_gained,
            'perfect_score': self.perfect_score,
            'new_high_score': self.new_high_score,
            'achievements_unlocked': self.achievements_unlocked
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameResult':
        """Deserialize from dictionary."""
        result = cls(
            game_name=data['game_name'],
            success=data['success'],
            score=data['score']
        )
        result.timestamp = data['timestamp']
        result.duration_seconds = data['duration_seconds']
        result.difficulty = GameDifficulty(data['difficulty'])
        result.experience_earned = data['experience_earned']
        result.coins_earned = data['coins_earned']
        result.bonding_gained = data['bonding_gained']
        result.perfect_score = data['perfect_score']
        result.new_high_score = data['new_high_score']
        result.achievements_unlocked = data['achievements_unlocked']
        return result


class MiniGame:
    """Base class for mini-games."""

    def __init__(self, game_name: str, description: str = ""):
        """
        Initialize mini-game.

        Args:
            game_name: Name of the game
            description: Game description
        """
        self.game_name = game_name
        self.description = description

        # Game state
        self.state = GameState.NOT_STARTED
        self.difficulty = GameDifficulty.MEDIUM
        self.score = 0
        self.high_score = 0

        # Timing
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.time_limit: Optional[float] = None  # Seconds
        self.elapsed_time: float = 0.0

        # Statistics
        self.total_plays = 0
        self.total_wins = 0
        self.total_losses = 0
        self.perfect_games = 0
        self.total_score_earned = 0

        # Callbacks
        self.on_game_start: Optional[Callable] = None
        self.on_game_end: Optional[Callable] = None
        self.on_score_change: Optional[Callable] = None

    def start_game(self, difficulty: GameDifficulty = GameDifficulty.MEDIUM):
        """
        Start the game.

        Args:
            difficulty: Game difficulty
        """
        self.difficulty = difficulty
        self.state = GameState.PLAYING
        self.score = 0
        self.start_time = time.time()
        self.elapsed_time = 0.0
        self.total_plays += 1

        if self.on_game_start:
            self.on_game_start()

    def update(self, dt: float):
        """
        Update game state.

        Args:
            dt: Time elapsed in seconds
        """
        if self.state != GameState.PLAYING:
            return

        self.elapsed_time += dt

        # Check time limit
        if self.time_limit and self.elapsed_time >= self.time_limit:
            self.end_game(success=False, reason="time_up")

    def pause_game(self):
        """Pause the game."""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED

    def resume_game(self):
        """Resume the game."""
        if self.state == GameState.PAUSED:
            self.state = GameState.PLAYING

    def end_game(self, success: bool, reason: str = "completed") -> GameResult:
        """
        End the game and return results.

        Args:
            success: Whether player succeeded
            reason: Reason for ending

        Returns:
            Game result
        """
        self.end_time = time.time()
        self.state = GameState.COMPLETED if success else GameState.FAILED

        # Update statistics
        if success:
            self.total_wins += 1
        else:
            self.total_losses += 1

        self.total_score_earned += self.score

        # Check for high score
        new_high_score = False
        if self.score > self.high_score:
            self.high_score = self.score
            new_high_score = True

        # Create result
        result = GameResult(
            game_name=self.game_name,
            success=success,
            score=self.score
        )
        result.duration_seconds = self.elapsed_time
        result.difficulty = self.difficulty
        result.new_high_score = new_high_score

        # Calculate rewards
        self._calculate_rewards(result)

        if self.on_game_end:
            self.on_game_end(result)

        return result

    def _calculate_rewards(self, result: GameResult):
        """
        Calculate rewards for game result.

        Args:
            result: Game result to add rewards to
        """
        # Base rewards
        base_exp = 10
        base_coins = 5
        base_bonding = 1.0

        # Difficulty multipliers
        difficulty_multipliers = {
            GameDifficulty.EASY: 0.5,
            GameDifficulty.MEDIUM: 1.0,
            GameDifficulty.HARD: 1.5,
            GameDifficulty.EXPERT: 2.0
        }

        multiplier = difficulty_multipliers.get(self.difficulty, 1.0)

        if result.success:
            result.experience_earned = int(base_exp * multiplier)
            result.coins_earned = int(base_coins * multiplier)
            result.bonding_gained = base_bonding * multiplier

            # Score bonus
            if result.score > 0:
                score_bonus = result.score // 10
                result.experience_earned += score_bonus
                result.coins_earned += score_bonus // 2

    def add_score(self, points: int):
        """
        Add to score.

        Args:
            points: Points to add
        """
        self.score += points

        if self.on_score_change:
            self.on_score_change(self.score)

    def get_win_rate(self) -> float:
        """
        Get win rate percentage.

        Returns:
            Win rate (0-100)
        """
        if self.total_plays == 0:
            return 0.0
        return (self.total_wins / self.total_plays) * 100

    def get_statistics(self) -> Dict[str, Any]:
        """Get game statistics."""
        return {
            'game_name': self.game_name,
            'total_plays': self.total_plays,
            'total_wins': self.total_wins,
            'total_losses': self.total_losses,
            'win_rate': self.get_win_rate(),
            'high_score': self.high_score,
            'perfect_games': self.perfect_games,
            'total_score_earned': self.total_score_earned,
            'average_score': (
                self.total_score_earned / self.total_plays
                if self.total_plays > 0 else 0
            )
        }

    def reset_statistics(self):
        """Reset game statistics."""
        self.total_plays = 0
        self.total_wins = 0
        self.total_losses = 0
        self.perfect_games = 0
        self.total_score_earned = 0
        # Keep high_score

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'game_name': self.game_name,
            'description': self.description,
            'difficulty': self.difficulty.value,
            'high_score': self.high_score,
            'total_plays': self.total_plays,
            'total_wins': self.total_wins,
            'total_losses': self.total_losses,
            'perfect_games': self.perfect_games,
            'total_score_earned': self.total_score_earned
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MiniGame':
        """Deserialize from dictionary."""
        game = cls(
            game_name=data['game_name'],
            description=data.get('description', '')
        )
        game.difficulty = GameDifficulty(data.get('difficulty', 'medium'))
        game.high_score = data.get('high_score', 0)
        game.total_plays = data.get('total_plays', 0)
        game.total_wins = data.get('total_wins', 0)
        game.total_losses = data.get('total_losses', 0)
        game.perfect_games = data.get('perfect_games', 0)
        game.total_score_earned = data.get('total_score_earned', 0)
        return game


class GameManager:
    """Manages all mini-games."""

    def __init__(self):
        """Initialize game manager."""
        self.games: Dict[str, MiniGame] = {}
        self.game_history: List[GameResult] = []
        self.current_game: Optional[MiniGame] = None

        # Statistics
        self.total_games_played = 0
        self.total_experience_earned = 0
        self.total_coins_earned = 0
        self.favorite_game: Optional[str] = None

    def register_game(self, game: MiniGame):
        """
        Register a game.

        Args:
            game: Game to register
        """
        self.games[game.game_name] = game

    def get_game(self, game_name: str) -> Optional[MiniGame]:
        """Get a game by name."""
        return self.games.get(game_name)

    def start_game(self, game_name: str,
                   difficulty: GameDifficulty = GameDifficulty.MEDIUM) -> bool:
        """
        Start a game.

        Args:
            game_name: Name of game to start
            difficulty: Game difficulty

        Returns:
            True if started successfully
        """
        game = self.get_game(game_name)
        if not game:
            return False

        self.current_game = game
        game.start_game(difficulty)
        return True

    def end_current_game(self, success: bool, reason: str = "completed") -> Optional[GameResult]:
        """
        End the current game.

        Args:
            success: Whether player succeeded
            reason: Reason for ending

        Returns:
            Game result or None
        """
        if not self.current_game:
            return None

        result = self.current_game.end_game(success, reason)

        # Record result
        self.game_history.append(result)
        self.total_games_played += 1
        self.total_experience_earned += result.experience_earned
        self.total_coins_earned += result.coins_earned

        # Update favorite game
        self._update_favorite_game()

        self.current_game = None
        return result

    def _update_favorite_game(self):
        """Update favorite game based on play count."""
        if not self.games:
            return

        most_played = max(
            self.games.values(),
            key=lambda g: g.total_plays
        )

        if most_played.total_plays > 0:
            self.favorite_game = most_played.game_name

    def get_game_statistics(self, game_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific game."""
        game = self.get_game(game_name)
        if not game:
            return None
        return game.get_statistics()

    def get_all_statistics(self) -> Dict[str, Any]:
        """Get overall game statistics."""
        return {
            'total_games_played': self.total_games_played,
            'total_experience_earned': self.total_experience_earned,
            'total_coins_earned': self.total_coins_earned,
            'favorite_game': self.favorite_game,
            'games_registered': len(self.games),
            'game_history_length': len(self.game_history)
        }

    def get_recent_results(self, count: int = 10) -> List[GameResult]:
        """Get recent game results."""
        return self.game_history[-count:]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'games': {
                name: game.to_dict()
                for name, game in self.games.items()
            },
            'game_history': [
                result.to_dict() for result in self.game_history
            ],
            'total_games_played': self.total_games_played,
            'total_experience_earned': self.total_experience_earned,
            'total_coins_earned': self.total_coins_earned,
            'favorite_game': self.favorite_game
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameManager':
        """Deserialize from dictionary."""
        manager = cls()

        # Restore games
        games_data = data.get('games', {})
        for name, game_data in games_data.items():
            game = MiniGame.from_dict(game_data)
            manager.games[name] = game

        # Restore history
        history_data = data.get('game_history', [])
        for result_data in history_data:
            result = GameResult.from_dict(result_data)
            manager.game_history.append(result)

        manager.total_games_played = data.get('total_games_played', 0)
        manager.total_experience_earned = data.get('total_experience_earned', 0)
        manager.total_coins_earned = data.get('total_coins_earned', 0)
        manager.favorite_game = data.get('favorite_game')

        return manager
