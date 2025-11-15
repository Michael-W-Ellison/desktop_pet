"""
Phase 12: Game Rewards System

Manages achievements, rewards, and progression from mini-games.
"""
import time
from typing import Dict, Any, List, Optional
from enum import Enum


class AchievementType(Enum):
    """Types of achievements."""
    FIRST_WIN = "first_win"              # Win first game
    PERFECT_GAME = "perfect_game"        # Perfect score
    HIGH_SCORER = "high_scorer"          # Reach high score
    SPEEDRUN = "speedrun"                # Complete quickly
    PERSISTENCE = "persistence"          # Play many times
    VARIETY = "variety"                  # Play all games
    MASTER = "master"                    # Master a game
    STREAK = "streak"                    # Win streak


class Achievement:
    """Represents a game achievement."""

    def __init__(self, achievement_id: str, name: str, description: str,
                 achievement_type: AchievementType):
        """
        Initialize achievement.

        Args:
            achievement_id: Unique achievement ID
            name: Achievement name
            description: Achievement description
            achievement_type: Type of achievement
        """
        self.achievement_id = achievement_id
        self.name = name
        self.description = description
        self.achievement_type = achievement_type
        self.unlocked = False
        self.unlock_timestamp: Optional[float] = None
        self.progress: float = 0.0  # 0-1
        self.target_value: int = 1
        self.current_value: int = 0

        # Rewards
        self.experience_reward: int = 50
        self.coins_reward: int = 25

    def unlock(self):
        """Unlock the achievement."""
        if not self.unlocked:
            self.unlocked = True
            self.unlock_timestamp = time.time()
            self.progress = 1.0

    def update_progress(self, value: int):
        """Update progress toward achievement."""
        self.current_value = value
        self.progress = min(1.0, value / self.target_value)

        if self.progress >= 1.0:
            self.unlock()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'achievement_id': self.achievement_id,
            'name': self.name,
            'description': self.description,
            'achievement_type': self.achievement_type.value,
            'unlocked': self.unlocked,
            'unlock_timestamp': self.unlock_timestamp,
            'progress': self.progress,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'experience_reward': self.experience_reward,
            'coins_reward': self.coins_reward
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Achievement':
        """Deserialize from dictionary."""
        achievement = cls(
            achievement_id=data['achievement_id'],
            name=data['name'],
            description=data['description'],
            achievement_type=AchievementType(data['achievement_type'])
        )
        achievement.unlocked = data['unlocked']
        achievement.unlock_timestamp = data.get('unlock_timestamp')
        achievement.progress = data['progress']
        achievement.target_value = data['target_value']
        achievement.current_value = data['current_value']
        achievement.experience_reward = data['experience_reward']
        achievement.coins_reward = data['coins_reward']
        return achievement


class GameRewardsSystem:
    """
    Manages achievements and rewards from mini-games.

    Features:
    - Track achievements across all games
    - Award experience and coins
    - Unlock special rewards
    - Track player progression
    """

    def __init__(self):
        """Initialize game rewards system."""
        # Achievements
        self.achievements: Dict[str, Achievement] = {}
        self.unlocked_achievements: List[str] = []

        # Progression
        self.total_experience_earned = 0
        self.total_coins_earned = 0
        self.player_level = 1
        self.experience_to_next_level = 100

        # Statistics
        self.total_achievements_unlocked = 0
        self.achievement_points = 0

        # Create default achievements
        self._create_default_achievements()

    def _create_default_achievements(self):
        """Create default achievements."""
        achievements = [
            # First wins
            Achievement(
                'fetch_first_win',
                'First Fetch',
                'Win your first game of Fetch',
                AchievementType.FIRST_WIN
            ),
            Achievement(
                'trick_show_first_win',
                'Show Off',
                'Win your first Trick Show',
                AchievementType.FIRST_WIN
            ),
            Achievement(
                'memory_first_win',
                'Sharp Memory',
                'Win your first Memory Match game',
                AchievementType.FIRST_WIN
            ),
            Achievement(
                'obstacle_first_win',
                'Agility Master',
                'Complete your first Obstacle Course',
                AchievementType.FIRST_WIN
            ),

            # Perfect games
            Achievement(
                'perfect_fetch',
                'Perfect Catcher',
                'Complete Fetch with no misses',
                AchievementType.PERFECT_GAME
            ),
            Achievement(
                'perfect_trick_show',
                'Flawless Performance',
                'Get perfect scores in every Trick Show round',
                AchievementType.PERFECT_GAME
            ),

            # Persistence
            Achievement(
                'dedicated_player',
                'Dedicated Player',
                'Play 50 mini-games',
                AchievementType.PERSISTENCE
            ),

            # Variety
            Achievement(
                'well_rounded',
                'Well-Rounded',
                'Win at least one game of each type',
                AchievementType.VARIETY
            ),
        ]

        # Set target values
        achievements[6].target_value = 50  # Play 50 games

        for achievement in achievements:
            self.achievements[achievement.achievement_id] = achievement

    def award_experience(self, amount: int):
        """
        Award experience points.

        Args:
            amount: Experience to award
        """
        self.total_experience_earned += amount

        # Check for level up
        while self.total_experience_earned >= self.experience_to_next_level:
            self._level_up()

    def award_coins(self, amount: int):
        """
        Award coins.

        Args:
            amount: Coins to award
        """
        self.total_coins_earned += amount

    def _level_up(self):
        """Level up the player."""
        self.player_level += 1
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)

    def check_achievement(self, achievement_id: str, value: Optional[int] = None):
        """
        Check and potentially unlock an achievement.

        Args:
            achievement_id: Achievement to check
            value: Optional progress value
        """
        achievement = self.achievements.get(achievement_id)
        if not achievement or achievement.unlocked:
            return

        if value is not None:
            achievement.update_progress(value)
        else:
            achievement.unlock()

        if achievement.unlocked and achievement_id not in self.unlocked_achievements:
            self.unlocked_achievements.append(achievement_id)
            self.total_achievements_unlocked += 1

            # Award rewards
            self.award_experience(achievement.experience_reward)
            self.award_coins(achievement.coins_reward)

    def get_achievement_progress(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        """Get progress for an achievement."""
        achievement = self.achievements.get(achievement_id)
        if not achievement:
            return None

        return {
            'name': achievement.name,
            'description': achievement.description,
            'unlocked': achievement.unlocked,
            'progress': achievement.progress,
            'current_value': achievement.current_value,
            'target_value': achievement.target_value
        }

    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        return [
            self.achievements[aid]
            for aid in self.unlocked_achievements
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get rewards system statistics."""
        return {
            'player_level': self.player_level,
            'total_experience': self.total_experience_earned,
            'experience_to_next_level': self.experience_to_next_level,
            'total_coins': self.total_coins_earned,
            'total_achievements': len(self.achievements),
            'unlocked_achievements': self.total_achievements_unlocked,
            'achievement_completion': (
                (self.total_achievements_unlocked / len(self.achievements) * 100)
                if self.achievements else 0.0
            )
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'achievements': {
                aid: achievement.to_dict()
                for aid, achievement in self.achievements.items()
            },
            'unlocked_achievements': self.unlocked_achievements,
            'total_experience_earned': self.total_experience_earned,
            'total_coins_earned': self.total_coins_earned,
            'player_level': self.player_level,
            'experience_to_next_level': self.experience_to_next_level,
            'total_achievements_unlocked': self.total_achievements_unlocked
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameRewardsSystem':
        """Deserialize from dictionary."""
        system = cls()

        # Restore achievements
        achievements_data = data.get('achievements', {})
        for aid, achievement_data in achievements_data.items():
            system.achievements[aid] = Achievement.from_dict(achievement_data)

        system.unlocked_achievements = data.get('unlocked_achievements', [])
        system.total_experience_earned = data.get('total_experience_earned', 0)
        system.total_coins_earned = data.get('total_coins_earned', 0)
        system.player_level = data.get('player_level', 1)
        system.experience_to_next_level = data.get('experience_to_next_level', 100)
        system.total_achievements_unlocked = data.get('total_achievements_unlocked', 0)

        return system
