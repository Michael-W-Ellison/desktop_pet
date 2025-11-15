"""
Phase 12: Trick Show Game

A game where the pet performs tricks and gets judged on quality.
"""
import random
import time
from typing import Dict, Any, List, Optional
from enum import Enum
from .game_base import MiniGame, GameDifficulty, GameState


class JudgeCriteria(Enum):
    """Judging criteria for trick performance."""
    EXECUTION = "execution"  # How well trick was performed
    STYLE = "style"          # Flair and presentation
    DIFFICULTY = "difficulty"  # Trick difficulty
    ENTHUSIASM = "enthusiasm"  # Pet's energy and excitement


class TrickPerformance:
    """Represents a single trick performance."""

    def __init__(self, trick_name: str, proficiency: float):
        """
        Initialize trick performance.

        Args:
            trick_name: Name of trick performed
            proficiency: Pet's proficiency in trick (0-1)
        """
        self.trick_name = trick_name
        self.proficiency = proficiency
        self.timestamp = time.time()

        # Scores
        self.execution_score: float = 0.0
        self.style_score: float = 0.0
        self.difficulty_score: float = 0.0
        self.enthusiasm_score: float = 0.0
        self.total_score: float = 0.0

        # Judging
        self.perfect_execution: bool = False
        self.crowd_pleaser: bool = False


class TrickShow(MiniGame):
    """
    Trick show mini-game.

    Pet performs tricks and gets judged by criteria.
    High scores come from:
    - Trick proficiency
    - Trick variety
    - Difficult tricks
    - Pet's mood/energy
    """

    def __init__(self):
        """Initialize trick show game."""
        super().__init__(
            game_name="Trick Show",
            description="Perform tricks and impress the judges!"
        )

        # Game settings
        self.rounds = 5  # Number of tricks to perform
        self.time_per_round = 15.0  # Seconds per trick

        # Game state
        self.current_round = 0
        self.performances: List[TrickPerformance] = []
        self.tricks_used: List[str] = []  # Track variety

        # Available tricks (provided when starting)
        self.available_tricks: Dict[str, float] = {}  # trick_name: proficiency

        # Pet state
        self.pet_mood: float = 0.5
        self.pet_energy: float = 1.0
        self.pet_confidence: float = 0.5

        # Judging
        self.perfect_performances = 0
        self.crowd_pleasers = 0
        self.variety_bonus = 0

    def start_game(self, difficulty: GameDifficulty = GameDifficulty.MEDIUM,
                   available_tricks: Optional[Dict[str, float]] = None,
                   pet_mood: float = 0.5, pet_energy: float = 1.0,
                   pet_confidence: float = 0.5):
        """
        Start the trick show.

        Args:
            difficulty: Game difficulty
            available_tricks: Dict of trick_name: proficiency
            pet_mood: Pet's current mood (0-1)
            pet_energy: Pet's energy level (0-1)
            pet_confidence: Pet's confidence (0-1)
        """
        super().start_game(difficulty)

        # Set difficulty parameters
        difficulty_settings = {
            GameDifficulty.EASY: {'rounds': 3, 'time': 20.0},
            GameDifficulty.MEDIUM: {'rounds': 5, 'time': 15.0},
            GameDifficulty.HARD: {'rounds': 7, 'time': 12.0},
            GameDifficulty.EXPERT: {'rounds': 10, 'time': 10.0}
        }

        settings = difficulty_settings.get(difficulty, difficulty_settings[GameDifficulty.MEDIUM])
        self.rounds = settings['rounds']
        self.time_per_round = settings['time']

        # Reset game state
        self.current_round = 0
        self.performances = []
        self.tricks_used = []
        self.perfect_performances = 0
        self.crowd_pleasers = 0
        self.variety_bonus = 0

        # Set tricks and pet state
        self.available_tricks = available_tricks or {'sit': 0.5, 'stay': 0.3}
        self.pet_mood = pet_mood
        self.pet_energy = pet_energy
        self.pet_confidence = pet_confidence

    def perform_trick(self, trick_name: str) -> Dict[str, Any]:
        """
        Perform a trick.

        Args:
            trick_name: Name of trick to perform

        Returns:
            Performance result
        """
        if self.state != GameState.PLAYING:
            return {'error': 'game_not_active'}

        if trick_name not in self.available_tricks:
            return {'error': 'trick_not_known'}

        proficiency = self.available_tricks[trick_name]

        # Create performance
        performance = TrickPerformance(trick_name, proficiency)

        # Judge the performance
        self._judge_performance(performance)

        # Record performance
        self.performances.append(performance)
        if trick_name not in self.tricks_used:
            self.tricks_used.append(trick_name)

        # Add score
        self.add_score(int(performance.total_score))

        # Track perfect performances
        if performance.perfect_execution:
            self.perfect_performances += 1

        if performance.crowd_pleaser:
            self.crowd_pleasers += 1

        # Advance round
        self.current_round += 1

        # Check for completion
        if self.current_round >= self.rounds:
            # Calculate variety bonus
            if len(self.tricks_used) == len(self.available_tricks):
                self.variety_bonus = 50  # Bonus for using all tricks
                self.add_score(self.variety_bonus)

            self.end_game(success=True, reason="completed")

        return {
            'success': True,
            'trick': trick_name,
            'execution': performance.execution_score,
            'style': performance.style_score,
            'difficulty': performance.difficulty_score,
            'enthusiasm': performance.enthusiasm_score,
            'total_score': performance.total_score,
            'perfect': performance.perfect_execution,
            'crowd_pleaser': performance.crowd_pleaser
        }

    def _judge_performance(self, performance: TrickPerformance):
        """
        Judge a trick performance.

        Args:
            performance: Performance to judge
        """
        # Execution score (based on proficiency)
        base_execution = performance.proficiency * 100

        # Random variance (±10%)
        variance = random.uniform(-10, 10)
        execution = max(0, min(100, base_execution + variance))

        # Confidence affects execution
        execution *= (0.7 + self.pet_confidence * 0.3)

        performance.execution_score = execution

        # Style score (based on mood and energy)
        style = (self.pet_mood * 50) + (self.pet_energy * 50)
        style_variance = random.uniform(-15, 15)
        performance.style_score = max(0, min(100, style + style_variance))

        # Difficulty score (based on trick complexity)
        # Harder tricks get more points
        difficulty_factor = 1.0 - performance.proficiency  # Less proficiency = harder
        performance.difficulty_score = (difficulty_factor * 50) + 50

        # Enthusiasm score (energy and mood)
        enthusiasm = ((self.pet_energy * 60) + (self.pet_mood * 40))
        enthusiasm_variance = random.uniform(-10, 10)
        performance.enthusiasm_score = max(0, min(100, enthusiasm + enthusiasm_variance))

        # Calculate total score (weighted average)
        weights = {
            'execution': 0.4,
            'style': 0.25,
            'difficulty': 0.2,
            'enthusiasm': 0.15
        }

        total = (
            performance.execution_score * weights['execution'] +
            performance.style_score * weights['style'] +
            performance.difficulty_score * weights['difficulty'] +
            performance.enthusiasm_score * weights['enthusiasm']
        )

        performance.total_score = total

        # Check for perfect execution
        if execution >= 95:
            performance.perfect_execution = True

        # Check for crowd pleaser (high style + enthusiasm)
        if performance.style_score >= 80 and performance.enthusiasm_score >= 80:
            performance.crowd_pleaser = True

    def skip_trick(self) -> bool:
        """
        Skip current trick (penalty).

        Returns:
            True if skipped
        """
        if self.state != GameState.PLAYING:
            return False

        # Penalty for skipping
        self.add_score(-10)

        # Advance round
        self.current_round += 1

        # Check for completion
        if self.current_round >= self.rounds:
            self.end_game(success=True, reason="completed")

        return True

    def get_progress(self) -> Dict[str, Any]:
        """Get current game progress."""
        return {
            'current_round': self.current_round,
            'total_rounds': self.rounds,
            'performances': len(self.performances),
            'perfect_performances': self.perfect_performances,
            'crowd_pleasers': self.crowd_pleasers,
            'tricks_used': len(self.tricks_used),
            'variety_bonus': self.variety_bonus,
            'score': self.score,
            'average_score': (
                sum(p.total_score for p in self.performances) / len(self.performances)
                if self.performances else 0.0
            )
        }

    def end_game(self, success: bool, reason: str = "completed"):
        """
        End the trick show.

        Args:
            success: Whether player won
            reason: Reason for ending

        Returns:
            Game result
        """
        result = super().end_game(success, reason)

        # Perfect game bonus
        if self.perfect_performances == self.rounds:
            result.perfect_score = True
            self.perfect_games += 1
            result.experience_earned += 25
            result.coins_earned += 15

        # Variety bonus
        if self.variety_bonus > 0:
            result.experience_earned += 10

        return result

    def get_leaderboard_entry(self) -> Dict[str, Any]:
        """Get entry for leaderboard."""
        return {
            'score': self.score,
            'rounds': self.rounds,
            'perfect_performances': self.perfect_performances,
            'crowd_pleasers': self.crowd_pleasers,
            'variety_bonus': self.variety_bonus,
            'average_performance': (
                sum(p.total_score for p in self.performances) / len(self.performances)
                if self.performances else 0.0
            )
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = super().to_dict()
        data.update({
            'rounds': self.rounds,
            'perfect_performances': self.perfect_performances,
            'crowd_pleasers': self.crowd_pleasers
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrickShow':
        """Deserialize from dictionary."""
        game = cls()
        # Load base class data
        game.difficulty = GameDifficulty(data.get('difficulty', 'medium'))
        game.high_score = data.get('high_score', 0)
        game.total_plays = data.get('total_plays', 0)
        game.total_wins = data.get('total_wins', 0)
        game.total_losses = data.get('total_losses', 0)
        game.perfect_games = data.get('perfect_games', 0)
        game.total_score_earned = data.get('total_score_earned', 0)
        # Load trick show specific data
        game.rounds = data.get('rounds', 5)
        return game
