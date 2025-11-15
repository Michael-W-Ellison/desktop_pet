"""
Phase 12: Obstacle Course Game

An agility course where the pet navigates obstacles.
"""
import random
import time
from typing import Dict, Any, List, Optional
from enum import Enum
from .game_base import MiniGame, GameDifficulty, GameState


class ObstacleType(Enum):
    """Types of obstacles."""
    HURDLE = "hurdle"      # Jump over
    TUNNEL = "tunnel"      # Run through
    WEAVE_POLES = "weave"  # Weave between poles
    A_FRAME = "a_frame"    # Climb and descend
    TIRE_JUMP = "tire"     # Jump through tire
    PAUSE_TABLE = "table"  # Stop and wait
    SEESAW = "seesaw"      # Balance beam


class Obstacle:
    """Represents a single obstacle."""

    def __init__(self, obstacle_id: int, obstacle_type: ObstacleType, difficulty: float):
        """
        Initialize obstacle.

        Args:
            obstacle_id: Unique obstacle ID
            obstacle_type: Type of obstacle
            difficulty: Difficulty rating (0-1)
        """
        self.obstacle_id = obstacle_id
        self.obstacle_type = obstacle_type
        self.difficulty = difficulty
        self.completed = False
        self.time_taken: float = 0.0
        self.penalties: int = 0  # Knock-downs, missed gates, etc.


class ObstacleCourse(MiniGame):
    """
    Obstacle course mini-game.

    Pet navigates through a course of obstacles.
    Score based on speed and accuracy.
    """

    def __init__(self):
        """Initialize obstacle course game."""
        super().__init__(
            game_name="Obstacle Course",
            description="Navigate through obstacles for speed and accuracy!"
        )

        # Game settings
        self.num_obstacles = 6
        self.time_limit = 90.0  # 90 seconds

        # Game state
        self.obstacles: List[Obstacle] = []
        self.current_obstacle_index = 0
        self.total_penalties = 0
        self.perfect_runs = 0  # Obstacles completed without penalties

        # Pet stats
        self.pet_agility: float = 0.5
        self.pet_energy: float = 1.0
        self.pet_training: float = 0.5  # How well trained for obstacles

    def start_game(self, difficulty: GameDifficulty = GameDifficulty.MEDIUM,
                   pet_agility: float = 0.5, pet_energy: float = 1.0,
                   pet_training: float = 0.5):
        """
        Start the obstacle course.

        Args:
            difficulty: Game difficulty
            pet_agility: Pet's agility stat (0-1)
            pet_energy: Pet's energy level (0-1)
            pet_training: Pet's obstacle training (0-1)
        """
        super().start_game(difficulty)

        # Set difficulty parameters
        difficulty_settings = {
            GameDifficulty.EASY: {'obstacles': 4, 'time': 120.0},
            GameDifficulty.MEDIUM: {'obstacles': 6, 'time': 90.0},
            GameDifficulty.HARD: {'obstacles': 8, 'time': 60.0},
            GameDifficulty.EXPERT: {'obstacles': 10, 'time': 45.0}
        }

        settings = difficulty_settings.get(difficulty, difficulty_settings[GameDifficulty.MEDIUM])
        self.num_obstacles = settings['obstacles']
        self.time_limit = settings['time']

        # Reset game state
        self.current_obstacle_index = 0
        self.total_penalties = 0
        self.perfect_runs = 0

        # Set pet stats
        self.pet_agility = pet_agility
        self.pet_energy = pet_energy
        self.pet_training = pet_training

        # Generate course
        self._generate_course()

    def _generate_course(self):
        """Generate random obstacle course."""
        self.obstacles = []

        # All obstacle types
        obstacle_types = list(ObstacleType)

        for i in range(self.num_obstacles):
            # Random obstacle type
            obs_type = random.choice(obstacle_types)

            # Difficulty increases as course progresses
            base_difficulty = 0.3 + (i / self.num_obstacles) * 0.5
            difficulty = min(1.0, base_difficulty)

            obstacle = Obstacle(i, obs_type, difficulty)
            self.obstacles.append(obstacle)

    def attempt_obstacle(self) -> Dict[str, Any]:
        """
        Attempt current obstacle.

        Returns:
            Result of attempt
        """
        if self.state != GameState.PLAYING:
            return {'error': 'game_not_active'}

        if self.current_obstacle_index >= len(self.obstacles):
            return {'error': 'course_completed'}

        obstacle = self.obstacles[self.current_obstacle_index]

        # Calculate success chance
        success_chance = self._calculate_success_chance(obstacle)

        # Determine success
        success = random.random() < success_chance

        # Calculate time taken
        base_time = 3.0  # Base seconds per obstacle
        time_factor = obstacle.difficulty
        time_taken = base_time * (0.5 + time_factor)

        # Agility reduces time
        time_taken *= (1.5 - self.pet_agility * 0.5)

        obstacle.time_taken = time_taken

        # Determine penalties
        penalties = 0
        if not success:
            # Failed - more penalties
            penalties = random.randint(1, 3)
        else:
            # Success but might have minor penalties
            if random.random() < (obstacle.difficulty * 0.3):
                penalties = 1

        obstacle.penalties = penalties
        self.total_penalties += penalties

        # Mark completed
        obstacle.completed = True

        # Calculate points
        points = 0
        if success:
            points = 20

            # Difficulty bonus
            points += int(obstacle.difficulty * 10)

            # Speed bonus
            if time_taken < base_time:
                points += 10

            # No penalties bonus
            if penalties == 0:
                points += 5
                self.perfect_runs += 1

            self.add_score(points)

        # Penalty deduction
        self.add_score(-penalties * 5)

        # Move to next obstacle
        self.current_obstacle_index += 1

        # Check if course completed
        if self.current_obstacle_index >= len(self.obstacles):
            # Calculate final time bonus
            time_remaining = max(0, self.time_limit - self.elapsed_time)
            time_bonus = int(time_remaining * 2)
            self.add_score(time_bonus)

            self.end_game(success=True, reason="course_completed")

        return {
            'success': success,
            'obstacle_type': obstacle.obstacle_type.value,
            'time_taken': time_taken,
            'penalties': penalties,
            'points': points,
            'current_obstacle': self.current_obstacle_index,
            'total_obstacles': len(self.obstacles)
        }

    def _calculate_success_chance(self, obstacle: Obstacle) -> float:
        """Calculate chance of successfully completing obstacle."""
        # Base chance
        chance = 0.5

        # Agility bonus
        chance += self.pet_agility * 0.3

        # Training bonus
        chance += self.pet_training * 0.2

        # Energy affects performance
        if self.pet_energy < 0.3:
            chance *= 0.6
        elif self.pet_energy > 0.8:
            chance *= 1.2

        # Obstacle difficulty
        chance -= obstacle.difficulty * 0.3

        return max(0.1, min(0.95, chance))

    def get_progress(self) -> Dict[str, Any]:
        """Get current game progress."""
        return {
            'current_obstacle': self.current_obstacle_index,
            'total_obstacles': len(self.obstacles),
            'perfect_runs': self.perfect_runs,
            'total_penalties': self.total_penalties,
            'time_remaining': max(0.0, self.time_limit - self.elapsed_time),
            'score': self.score
        }

    def end_game(self, success: bool, reason: str = "completed"):
        """End the obstacle course."""
        result = super().end_game(success, reason)

        # Perfect course (no penalties)
        if success and self.total_penalties == 0:
            result.perfect_score = True
            self.perfect_games += 1
            result.experience_earned += 20

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ObstacleCourse':
        """Deserialize from dictionary."""
        game = cls()
        game.difficulty = GameDifficulty(data.get('difficulty', 'medium'))
        game.high_score = data.get('high_score', 0)
        game.total_plays = data.get('total_plays', 0)
        game.total_wins = data.get('total_wins', 0)
        game.total_losses = data.get('total_losses', 0)
        game.perfect_games = data.get('perfect_games', 0)
        game.total_score_earned = data.get('total_score_earned', 0)
        return game
