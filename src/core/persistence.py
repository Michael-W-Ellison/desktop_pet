"""
Persistence layer for saving and loading creature state.
"""
import json
import os
from typing import Optional, Dict, Any
from .creature import Creature
from .neural_network import BehaviorLearner
from .config import DATA_FILE


class PetDataManager:
    """Manages saving and loading of pet data."""

    def __init__(self, data_file: str = DATA_FILE):
        """
        Initialize the data manager.

        Args:
            data_file: Path to the data file
        """
        self.data_file = data_file

    def save(self, creature: Optional[Creature], learner: Optional[BehaviorLearner],
             game_state: Dict[str, Any]):
        """
        Save creature and game state to file.

        Args:
            creature: Creature instance (None if egg state)
            learner: BehaviorLearner instance (None if egg state)
            game_state: Additional game state (e.g., is_egg, last_save_time)
        """
        data = {
            'game_state': game_state,
            'creature': creature.to_dict() if creature else None,
            'learner': learner.to_dict() if learner else None
        }

        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self) -> Optional[Dict[str, Any]]:
        """
        Load creature and game state from file.

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
                    result['learner'] = BehaviorLearner.from_dict(creature, data['learner'])

            return result

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading save data: {e}")
            return None

    def delete(self):
        """Delete the save file."""
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def exists(self) -> bool:
        """Check if save file exists."""
        return os.path.exists(self.data_file)
