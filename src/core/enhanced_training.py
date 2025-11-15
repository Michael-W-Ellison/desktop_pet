"""
Phase 6: Enhanced Training & Command System

Adds advanced training features:
- 20+ commands (expanded from original 12)
- Stubbornness based on mood, trust, bond, hunger, energy
- Positive reinforcement (treats, praise, rewards)
- Negative reinforcement (affects trust and bond)
- Enhanced training progress tracking
- Skill degradation (integrated from existing system)
"""
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from .training_system import Trick, TrickDifficulty, TrickCategory


class ReinforcementType(Enum):
    """Types of reinforcement during training."""
    NONE = "none"              # No reinforcement
    VERBAL_PRAISE = "verbal_praise"  # "Good job!", "Well done!"
    TREAT = "treat"            # Food reward
    TOY_REWARD = "toy_reward"  # Play with favorite toy
    AFFECTION = "affection"    # Pet, cuddle, praise
    PUNISHMENT = "punishment"  # Scolding (negative reinforcement)
    IGNORE = "ignore"          # No response (extinction)


class CommandComplexity(Enum):
    """How complex a command sequence is."""
    SIMPLE = 1      # Single action (sit, stay)
    MODERATE = 2    # Two-step action (come then sit)
    COMPLEX = 3     # Multi-step sequence (fetch, bring, drop)
    CHAIN = 4       # Complex command chain


# Phase 6: Extended command library (20+ commands)
EXTENDED_COMMANDS = {
    # Original 12 (from Phase 2)
    'sit': Trick('sit', TrickDifficulty.EASY, TrickCategory.BASIC,
                "Pet sits down and stays still"),
    'stay': Trick('stay', TrickDifficulty.MEDIUM, TrickCategory.BASIC,
                 "Pet stays in place until released"),
    'come': Trick('come', TrickDifficulty.EASY, TrickCategory.BASIC,
                 "Pet comes to you when called"),
    'fetch': Trick('fetch', TrickDifficulty.MEDIUM, TrickCategory.INTERACTIVE,
                  "Pet retrieves and brings back items"),
    'dance': Trick('dance', TrickDifficulty.MEDIUM, TrickCategory.MOVEMENT,
                  "Pet performs a little dance"),
    'spin': Trick('spin', TrickDifficulty.EASY, TrickCategory.MOVEMENT,
                 "Pet spins in a circle"),
    'jump': Trick('jump', TrickDifficulty.EASY, TrickCategory.MOVEMENT,
                 "Pet jumps up in the air"),
    'play_dead': Trick('play_dead', TrickDifficulty.HARD, TrickCategory.EXPRESSIVE,
                      "Pet plays dead convincingly"),
    'bow': Trick('bow', TrickDifficulty.MEDIUM, TrickCategory.EXPRESSIVE,
                "Pet performs a bow"),
    'wave': Trick('wave', TrickDifficulty.MEDIUM, TrickCategory.EXPRESSIVE,
                 "Pet waves hello or goodbye"),
    'shake': Trick('shake', TrickDifficulty.EASY, TrickCategory.INTERACTIVE,
                  "Pet offers paw for handshake"),
    'roll_over': Trick('roll_over', TrickDifficulty.HARD, TrickCategory.MOVEMENT,
                      "Pet rolls over completely"),

    # Phase 6: New commands (13 more = 25 total)
    'speak': Trick('speak', TrickDifficulty.EASY, TrickCategory.EXPRESSIVE,
                  "Pet makes a sound on command"),
    'quiet': Trick('quiet', TrickDifficulty.MEDIUM, TrickCategory.BASIC,
                  "Pet stops making noise"),
    'heel': Trick('heel', TrickDifficulty.HARD, TrickCategory.BASIC,
                 "Pet walks closely at your side"),
    'drop_it': Trick('drop_it', TrickDifficulty.MEDIUM, TrickCategory.INTERACTIVE,
                    "Pet drops what's in its mouth"),
    'leave_it': Trick('leave_it', TrickDifficulty.HARD, TrickCategory.BASIC,
                     "Pet ignores items or distractions"),
    'high_five': Trick('high_five', TrickDifficulty.EASY, TrickCategory.INTERACTIVE,
                      "Pet gives a high five"),
    'crawl': Trick('crawl', TrickDifficulty.HARD, TrickCategory.MOVEMENT,
                  "Pet crawls on belly"),
    'back_up': Trick('back_up', TrickDifficulty.MEDIUM, TrickCategory.MOVEMENT,
                    "Pet walks backwards"),
    'circle': Trick('circle', TrickDifficulty.MEDIUM, TrickCategory.MOVEMENT,
                   "Pet walks in a circle around you"),
    'kiss': Trick('kiss', TrickDifficulty.EASY, TrickCategory.EXPRESSIVE,
                 "Pet gives affectionate kiss"),
    'hug': Trick('hug', TrickDifficulty.MEDIUM, TrickCategory.EXPRESSIVE,
                "Pet gives a hug"),
    'find_it': Trick('find_it', TrickDifficulty.HARD, TrickCategory.INTERACTIVE,
                    "Pet searches for hidden items"),
    'go_to_bed': Trick('go_to_bed', TrickDifficulty.MEDIUM, TrickCategory.BASIC,
                      "Pet goes to designated rest area"),

    # Expert-level tricks
    'balance': Trick('balance', TrickDifficulty.EXPERT, TrickCategory.ADVANCED,
                    "Pet balances object on nose"),
    'weave': Trick('weave', TrickDifficulty.EXPERT, TrickCategory.ADVANCED,
                  "Pet weaves through your legs while walking"),
}


class ReinforcementSystem:
    """
    Manages positive and negative reinforcement during training.

    Tracks:
    - Reinforcement history
    - Effectiveness of different reinforcement types
    - Effects on trust, bond, and learning rate
    """

    def __init__(self):
        """Initialize reinforcement system."""
        self.reinforcement_history = []  # List of (timestamp, type, command, success)
        self.total_treats_given = 0
        self.total_praise_given = 0
        self.total_punishments = 0

        # Track effectiveness by reinforcement type
        self.effectiveness = {
            ReinforcementType.VERBAL_PRAISE: {'uses': 0, 'successes': 0},
            ReinforcementType.TREAT: {'uses': 0, 'successes': 0},
            ReinforcementType.TOY_REWARD: {'uses': 0, 'successes': 0},
            ReinforcementType.AFFECTION: {'uses': 0, 'successes': 0},
            ReinforcementType.PUNISHMENT: {'uses': 0, 'successes': 0},
            ReinforcementType.IGNORE: {'uses': 0, 'successes': 0},
        }

    def apply_reinforcement(self, reinforcement_type: ReinforcementType,
                          command: str, success: bool,
                          personality_traits: Dict[str, float]) -> Dict[str, Any]:
        """
        Apply reinforcement and calculate effects.

        Args:
            reinforcement_type: Type of reinforcement
            command: Command being reinforced
            success: Whether command was successful
            personality_traits: Personality modifiers

        Returns:
            Dictionary with effects (trust_change, bond_change, happiness_change, learning_boost)
        """
        now = time.time()
        self.reinforcement_history.append((now, reinforcement_type.value, command, success))

        # Track effectiveness
        if reinforcement_type in self.effectiveness:
            self.effectiveness[reinforcement_type]['uses'] += 1
            if success:
                self.effectiveness[reinforcement_type]['successes'] += 1

        effects = {
            'trust_change': 0.0,
            'bond_change': 0.0,
            'happiness_change': 0.0,
            'learning_boost': 1.0,
            'message': ''
        }

        if reinforcement_type == ReinforcementType.VERBAL_PRAISE:
            self.total_praise_given += 1
            effects['bond_change'] = 0.3
            effects['happiness_change'] = 2.0
            effects['learning_boost'] = 1.1
            effects['message'] = "Appreciated the praise!"

        elif reinforcement_type == ReinforcementType.TREAT:
            self.total_treats_given += 1
            effects['bond_change'] = 0.5
            effects['happiness_change'] = 5.0
            effects['learning_boost'] = 1.3
            effects['trust_change'] = 0.2
            effects['message'] = "Loved the treat! Very motivated!"

        elif reinforcement_type == ReinforcementType.TOY_REWARD:
            effects['bond_change'] = 0.4
            effects['happiness_change'] = 4.0
            effects['learning_boost'] = 1.2
            effects['message'] = "Excited about toy time!"

        elif reinforcement_type == ReinforcementType.AFFECTION:
            effects['bond_change'] = 0.6
            effects['happiness_change'] = 3.0
            effects['learning_boost'] = 1.1
            effects['trust_change'] = 0.3
            effects['message'] = "Feeling loved and appreciated!"

        elif reinforcement_type == ReinforcementType.PUNISHMENT:
            self.total_punishments += 1
            effects['trust_change'] = -2.0  # Significant trust damage
            effects['bond_change'] = -0.5
            effects['happiness_change'] = -5.0
            effects['learning_boost'] = 0.7  # Learns slower when scared
            effects['message'] = "Frightened and confused..."

        elif reinforcement_type == ReinforcementType.IGNORE:
            effects['happiness_change'] = -1.0
            effects['learning_boost'] = 0.9
            effects['message'] = "Feeling ignored..."

        return effects

    def get_most_effective_reinforcement(self) -> ReinforcementType:
        """Get the most effective reinforcement type based on history."""
        best_type = ReinforcementType.VERBAL_PRAISE
        best_rate = 0.0

        for rtype, data in self.effectiveness.items():
            if data['uses'] > 5:  # Need enough samples
                success_rate = data['successes'] / data['uses']
                if success_rate > best_rate:
                    best_rate = success_rate
                    best_type = rtype

        return best_type

    def to_dict(self) -> Dict[str, Any]:
        """Serialize reinforcement system."""
        return {
            'reinforcement_history': self.reinforcement_history[-100:],  # Keep last 100
            'total_treats_given': self.total_treats_given,
            'total_praise_given': self.total_praise_given,
            'total_punishments': self.total_punishments,
            'effectiveness': {k.value: v for k, v in self.effectiveness.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReinforcementSystem':
        """Deserialize reinforcement system."""
        system = cls()
        system.reinforcement_history = data.get('reinforcement_history', [])
        system.total_treats_given = data.get('total_treats_given', 0)
        system.total_praise_given = data.get('total_praise_given', 0)
        system.total_punishments = data.get('total_punishments', 0)

        if 'effectiveness' in data:
            for key_str, value in data['effectiveness'].items():
                rtype = ReinforcementType(key_str)
                system.effectiveness[rtype] = value

        return system


class StubbornessCalculator:
    """
    Calculates stubbornness/refusal chance based on multiple factors.

    Considers:
    - Personality (base stubbornness)
    - Current mood/happiness
    - Trust level
    - Bond level
    - Physical state (hunger, energy)
    - Recent training history (fatigue)
    """

    @staticmethod
    def calculate_refusal_chance(
        base_stubbornness: float,  # From personality (0-1)
        happiness: float,           # 0-100
        trust: float,               # 0-100
        bond: float,                # 0-100
        hunger: float,              # 0-100 (higher = hungrier)
        energy: float,              # 0-100
        recent_commands: int        # Commands in last 5 minutes
    ) -> Tuple[float, str]:
        """
        Calculate probability of refusing a command.

        Returns:
            Tuple of (refusal_chance 0-1, reason_if_refused)
        """
        # Start with personality base
        refusal = base_stubbornness
        reason = "just feeling stubborn"

        # Happiness affects compliance (unhappy = more stubborn)
        if happiness < 30:
            refusal += 0.4
            reason = "too unhappy to cooperate"
        elif happiness < 50:
            refusal += 0.2
            reason = "not in the mood"
        elif happiness > 80:
            refusal -= 0.1  # Happy pets are more compliant

        # Trust significantly affects obedience
        if trust < 20:
            refusal += 0.5
            reason = "doesn't trust you enough"
        elif trust < 40:
            refusal += 0.3
        elif trust > 80:
            refusal -= 0.2  # High trust = high obedience

        # Bond affects willingness to please
        if bond < 30:
            refusal += 0.3
            reason = "not bonded enough to care"
        elif bond > 70:
            refusal -= 0.15  # Wants to make you happy

        # Physical needs affect compliance
        if hunger > 70:
            refusal += 0.4
            reason = "too hungry to focus"
        elif hunger > 50:
            refusal += 0.2

        if energy < 20:
            refusal += 0.5
            reason = "too tired to perform"
        elif energy < 40:
            refusal += 0.3

        # Training fatigue (too many commands recently)
        if recent_commands > 10:
            refusal += 0.4
            reason = "exhausted from too much training"
        elif recent_commands > 5:
            refusal += 0.2

        # Clamp to 0-1 range
        refusal = max(0.0, min(0.95, refusal))  # Max 95% refusal

        return refusal, reason

    @staticmethod
    def will_comply(refusal_chance: float) -> bool:
        """Determine if pet will comply based on refusal chance."""
        return random.random() > refusal_chance


class TrainingProgressTracker:
    """
    Tracks detailed training progress and analytics.

    Provides:
    - Learning curves for each trick
    - Training session statistics
    - Command success rates over time
    - Optimal training time predictions
    """

    def __init__(self):
        """Initialize progress tracker."""
        self.training_sessions = []  # List of session data
        self.command_history = []    # Detailed command history
        self.learning_curves = {}    # trick_name: [(timestamp, proficiency)]
        self.session_start = None
        self.current_session_commands = 0

    def start_session(self):
        """Start a new training session."""
        self.session_start = time.time()
        self.current_session_commands = 0

    def end_session(self) -> Dict[str, Any]:
        """
        End current training session.

        Returns:
            Session statistics
        """
        if self.session_start is None:
            return {}

        duration = time.time() - self.session_start
        session_data = {
            'start_time': self.session_start,
            'duration_seconds': duration,
            'commands_practiced': self.current_session_commands,
            'timestamp': time.time()
        }

        self.training_sessions.append(session_data)
        self.session_start = None
        self.current_session_commands = 0

        return session_data

    def record_command(self, command: str, success: bool, proficiency: float):
        """Record a command attempt."""
        self.current_session_commands += 1
        self.command_history.append({
            'timestamp': time.time(),
            'command': command,
            'success': success,
            'proficiency': proficiency
        })

        # Update learning curve
        if command not in self.learning_curves:
            self.learning_curves[command] = []

        self.learning_curves[command].append((time.time(), proficiency))

        # Keep last 100 points per trick
        if len(self.learning_curves[command]) > 100:
            self.learning_curves[command] = self.learning_curves[command][-100:]

    def get_success_rate(self, command: str, last_n: int = 10) -> float:
        """Get success rate for a command over last N attempts."""
        attempts = [h for h in self.command_history if h['command'] == command][-last_n:]
        if not attempts:
            return 0.0

        successes = sum(1 for a in attempts if a['success'])
        return successes / len(attempts)

    def get_learning_velocity(self, command: str) -> float:
        """
        Get how fast a trick is being learned (proficiency gain per session).

        Returns:
            Average proficiency gain per training session
        """
        if command not in self.learning_curves or len(self.learning_curves[command]) < 2:
            return 0.0

        curve = self.learning_curves[command]

        # Calculate average gain over last 5 data points
        recent = curve[-5:]
        if len(recent) < 2:
            return 0.0

        total_gain = recent[-1][1] - recent[0][1]
        time_span = recent[-1][0] - recent[0][0]

        if time_span == 0:
            return 0.0

        # Normalize to per-hour rate
        return (total_gain / time_span) * 3600

    def get_training_stats(self) -> Dict[str, Any]:
        """Get comprehensive training statistics."""
        total_sessions = len(self.training_sessions)
        total_commands = len(self.command_history)

        if not total_commands:
            return {
                'total_sessions': 0,
                'total_commands': 0,
                'overall_success_rate': 0.0
            }

        successes = sum(1 for h in self.command_history if h['success'])

        return {
            'total_sessions': total_sessions,
            'total_commands': total_commands,
            'overall_success_rate': successes / total_commands if total_commands > 0 else 0.0,
            'commands_per_session': total_commands / total_sessions if total_sessions > 0 else 0.0,
            'tricks_in_progress': len(self.learning_curves)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize tracker."""
        return {
            'training_sessions': self.training_sessions[-50:],  # Last 50 sessions
            'command_history': self.command_history[-200:],     # Last 200 commands
            'learning_curves': {k: v[-50:] for k, v in self.learning_curves.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrainingProgressTracker':
        """Deserialize tracker."""
        tracker = cls()
        tracker.training_sessions = data.get('training_sessions', [])
        tracker.command_history = data.get('command_history', [])
        tracker.learning_curves = data.get('learning_curves', {})
        return tracker
