"""
Phase 12: Fetch Game

A fetch/catch game where the pet catches thrown objects.
"""
import random
import time
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from .game_base import MiniGame, GameDifficulty, GameState


class ThrowableItem(Enum):
    """Items that can be thrown."""
    BALL = "ball"
    FRISBEE = "frisbee"
    STICK = "stick"
    TOY = "toy"
    BONE = "bone"
    TREAT = "treat"


class FetchGame(MiniGame):
    """
    Fetch/catch mini-game.

    The pet tries to catch thrown objects. Success depends on:
    - Pet's agility and energy
    - Throw accuracy
    - Difficulty level
    """

    def __init__(self):
        """Initialize fetch game."""
        super().__init__(
            game_name="Fetch",
            description="Throw objects for your pet to catch!"
        )

        # Game settings
        self.target_catches = 10  # Catches needed to win
        self.time_limit = 60.0  # 60 seconds

        # Game state
        self.catches = 0
        self.misses = 0
        self.perfect_catches = 0  # Caught on first try
        self.throws_made = 0
        self.current_item: Optional[ThrowableItem] = None

        # Throw mechanics
        self.throw_power: float = 0.5  # 0-1
        self.throw_angle: float = 45.0  # degrees
        self.throw_distance: float = 0.0  # calculated

        # Pet stats (provided when starting game)
        self.pet_agility: float = 0.5
        self.pet_energy: float = 1.0

    def start_game(self, difficulty: GameDifficulty = GameDifficulty.MEDIUM,
                   pet_agility: float = 0.5, pet_energy: float = 1.0):
        """
        Start the fetch game.

        Args:
            difficulty: Game difficulty
            pet_agility: Pet's agility stat (0-1)
            pet_energy: Pet's energy level (0-1)
        """
        super().start_game(difficulty)

        # Set difficulty parameters
        difficulty_settings = {
            GameDifficulty.EASY: {'target': 5, 'time': 90.0},
            GameDifficulty.MEDIUM: {'target': 10, 'time': 60.0},
            GameDifficulty.HARD: {'target': 15, 'time': 45.0},
            GameDifficulty.EXPERT: {'target': 20, 'time': 30.0}
        }

        settings = difficulty_settings.get(difficulty, difficulty_settings[GameDifficulty.MEDIUM])
        self.target_catches = settings['target']
        self.time_limit = settings['time']

        # Reset game state
        self.catches = 0
        self.misses = 0
        self.perfect_catches = 0
        self.throws_made = 0
        self.current_item = None

        # Set pet stats
        self.pet_agility = pet_agility
        self.pet_energy = pet_energy

    def throw_item(self, item: ThrowableItem, power: float = 0.5,
                   angle: float = 45.0) -> Dict[str, Any]:
        """
        Throw an item for the pet to catch.

        Args:
            item: Item to throw
            power: Throw power (0-1)
            angle: Throw angle in degrees (0-90)

        Returns:
            Result of the throw
        """
        if self.state != GameState.PLAYING:
            return {'error': 'game_not_active'}

        self.throws_made += 1
        self.current_item = item
        self.throw_power = max(0.0, min(1.0, power))
        self.throw_angle = max(0.0, min(90.0, angle))

        # Calculate throw distance
        self.throw_distance = self._calculate_throw_distance()

        # Determine if pet catches it
        catch_result = self._attempt_catch()

        if catch_result['caught']:
            self.catches += 1
            self.add_score(catch_result['points'])

            if catch_result['perfect']:
                self.perfect_catches += 1

            # Check for win
            if self.catches >= self.target_catches:
                self.end_game(success=True, reason="target_reached")
        else:
            self.misses += 1

        return catch_result

    def _calculate_throw_distance(self) -> float:
        """Calculate how far the throw goes."""
        # Physics simulation (simplified)
        # Distance = power * angle factor
        angle_radians = (self.throw_angle / 180.0) * 3.14159
        angle_factor = 2 * angle_radians  # Simplified

        # Optimal angle is 45 degrees
        optimal_angle = 45.0
        angle_penalty = abs(self.throw_angle - optimal_angle) / optimal_angle

        distance = self.throw_power * (1.0 - angle_penalty * 0.5) * 100.0

        return distance

    def _attempt_catch(self) -> Dict[str, Any]:
        """
        Determine if pet catches the thrown item.

        Returns:
            Catch result dictionary
        """
        # Base catch chance
        catch_chance = 0.5

        # Pet agility bonus
        catch_chance += self.pet_agility * 0.3

        # Pet energy affects performance
        if self.pet_energy < 0.3:
            catch_chance *= 0.7  # Tired pet
        elif self.pet_energy > 0.8:
            catch_chance *= 1.2  # Energetic pet

        # Throw quality affects catch chance
        # Good throws (40-60 units) are easier
        if 40 <= self.throw_distance <= 60:
            catch_chance += 0.2
        elif self.throw_distance < 20 or self.throw_distance > 80:
            catch_chance -= 0.3  # Too short or too far

        # Item type affects difficulty
        item_difficulty = {
            ThrowableItem.BALL: 1.0,
            ThrowableItem.FRISBEE: 0.8,
            ThrowableItem.STICK: 0.9,
            ThrowableItem.TOY: 1.0,
            ThrowableItem.BONE: 1.1,
            ThrowableItem.TREAT: 1.2  # Highly motivated!
        }

        catch_chance *= item_difficulty.get(self.current_item, 1.0)

        # Clamp to 0-1
        catch_chance = max(0.0, min(1.0, catch_chance))

        # Determine if caught
        caught = random.random() < catch_chance

        # Calculate points
        points = 0
        perfect = False

        if caught:
            # Base points
            points = 10

            # Distance bonus (optimal throws get more points)
            if 40 <= self.throw_distance <= 60:
                points += 5
                perfect = True

            # Difficulty bonus
            difficulty_multiplier = {
                GameDifficulty.EASY: 1.0,
                GameDifficulty.MEDIUM: 1.5,
                GameDifficulty.HARD: 2.0,
                GameDifficulty.EXPERT: 2.5
            }
            points = int(points * difficulty_multiplier.get(self.difficulty, 1.0))

        return {
            'caught': caught,
            'perfect': perfect,
            'points': points,
            'catch_chance': catch_chance,
            'distance': self.throw_distance,
            'item': self.current_item.value if self.current_item else None
        }

    def update(self, dt: float):
        """
        Update game state.

        Args:
            dt: Time elapsed
        """
        super().update(dt)

        # Pet gets slightly tired during game
        self.pet_energy = max(0.2, self.pet_energy - dt * 0.01)

    def get_progress(self) -> Dict[str, Any]:
        """Get current game progress."""
        return {
            'catches': self.catches,
            'target_catches': self.target_catches,
            'misses': self.misses,
            'perfect_catches': self.perfect_catches,
            'accuracy': (
                (self.catches / self.throws_made * 100)
                if self.throws_made > 0 else 0.0
            ),
            'time_remaining': max(0.0, self.time_limit - self.elapsed_time),
            'score': self.score
        }

    def end_game(self, success: bool, reason: str = "completed"):
        """
        End the fetch game.

        Args:
            success: Whether player won
            reason: Reason for ending

        Returns:
            Game result
        """
        result = super().end_game(success, reason)

        # Check for perfect game
        if success and self.misses == 0:
            result.perfect_score = True
            self.perfect_games += 1

        # Accuracy bonus
        if self.throws_made > 0:
            accuracy = self.catches / self.throws_made
            if accuracy > 0.8:
                result.experience_earned += 10
                result.coins_earned += 5

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = super().to_dict()
        data.update({
            'target_catches': self.target_catches,
            'catches': self.catches,
            'misses': self.misses,
            'perfect_catches': self.perfect_catches
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FetchGame':
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
        # Load fetch game specific data
        game.target_catches = data.get('target_catches', 10)
        return game
