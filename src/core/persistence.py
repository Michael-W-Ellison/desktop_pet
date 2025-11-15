"""
Persistence layer for saving and loading creature state.

Updated to support EnhancedBehaviorLearner with all sophisticated AI systems:
- LSTM networks with hidden states and sequence buffers
- NetworkCoordinator with specialized networks (Movement, Activity, Emotion, Social)
- Reinforcement learning agents with Q-networks and experience replay
- Sensory system state
"""
import json
import os
from typing import Optional, Dict, Any
from .creature import Creature
from .enhanced_behavior_learner import EnhancedBehaviorLearner
from .config import DATA_FILE


class PetDataManager:
    """Manages saving and loading of pet data with sophisticated AI systems."""

    def __init__(self, data_file: str = DATA_FILE):
        """
        Initialize the data manager.

        Args:
            data_file: Path to the data file
        """
        self.data_file = data_file

    def save(self, creature: Optional[Creature], learner: Optional[EnhancedBehaviorLearner],
             game_state: Dict[str, Any]):
        """
        Save creature and game state to file.

        This saves all sophisticated AI components:
        - Creature state (stats, position, personality, etc.)
        - EnhancedBehaviorLearner state (including all neural networks)
        - Game state (is_egg, last_save_time, AI complexity, etc.)

        Args:
            creature: Creature instance (None if egg state)
            learner: EnhancedBehaviorLearner instance (None if egg state)
            game_state: Additional game state (e.g., is_egg, last_save_time, ai_complexity)
        """
        data = {
            'game_state': game_state,
            'creature': creature.to_dict() if creature else None,
            'learner': learner.to_dict() if learner else None
        }

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.data_file) if os.path.dirname(self.data_file) else '.', exist_ok=True)

        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving pet data: {e}")
            # Try to save a backup without indent (might help with large files)
            try:
                with open(self.data_file, 'w') as f:
                    json.dump(data, f)
            except Exception as e2:
                print(f"Critical error: Could not save pet data: {e2}")

    def load(self) -> Optional[Dict[str, Any]]:
        """
        Load creature and game state from file.

        This loads all sophisticated AI components and reconstructs:
        - Creature instance with full state
        - EnhancedBehaviorLearner with all trained networks
        - Game state including AI complexity level

        Returns:
            Dictionary with 'creature', 'learner', and 'game_state' keys, or None if no save exists
        """
        if not os.path.exists(self.data_file):
            return None

        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)

            result = {
                'game_state': data.get('game_state', {}),
                'creature': None,
                'learner': None
            }

            # Recreate creature if data exists
            if data.get('creature'):
                creature = Creature.from_dict(data['creature'])
                result['creature'] = creature

                # Recreate learner if data exists
                if data.get('learner'):
                    try:
                        result['learner'] = EnhancedBehaviorLearner.from_dict(creature, data['learner'])
                    except Exception as e:
                        print(f"Error loading EnhancedBehaviorLearner: {e}")
                        print("Attempting to create new learner with saved complexity level...")

                        # Fallback: Create new learner with same complexity
                        from .config import AIComplexity, DEFAULT_AI_COMPLEXITY
                        complexity_str = data['learner'].get('complexity', DEFAULT_AI_COMPLEXITY.value)
                        try:
                            complexity = AIComplexity(complexity_str)
                            result['learner'] = EnhancedBehaviorLearner(creature, complexity)
                            print(f"Created new learner with {complexity.value} complexity")
                        except Exception as e2:
                            print(f"Fallback also failed: {e2}")
                            result['learner'] = None

            return result

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading save data: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error loading save data: {e}")
            return None

    def delete(self):
        """Delete the save file."""
        if os.path.exists(self.data_file):
            try:
                os.remove(self.data_file)
            except Exception as e:
                print(f"Error deleting save file: {e}")

    def exists(self) -> bool:
        """Check if save file exists."""
        return os.path.exists(self.data_file)

    def get_file_size(self) -> Optional[int]:
        """
        Get the size of the save file in bytes.

        Returns:
            File size in bytes, or None if file doesn't exist
        """
        if self.exists():
            try:
                return os.path.getsize(self.data_file)
            except Exception:
                return None
        return None
