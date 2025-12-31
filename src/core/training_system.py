"""
Training and Trick Learning System for Desktop Pal

Allows the pet to:
1. Learn explicit commands (sit, stay, fetch, dance, etc.)
2. Recognize its name and respond
3. Remember trained behaviors
4. Show personality in learning (stubborn, eager, etc.)
5. Require practice to master tricks
6. Forget tricks if not practiced

Phase 6 Enhancements:
7. 25+ commands (expanded from 12)
8. Positive and negative reinforcement
9. Advanced stubbornness based on mood, trust, bond, hunger, energy
10. Detailed training progress tracking
"""
import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from .config import PersonalityType


class TrickDifficulty(Enum):
    """How hard a trick is to learn."""
    TRIVIAL = 1      # 1-3 attempts to learn
    EASY = 2         # 3-7 attempts
    MEDIUM = 3       # 7-15 attempts
    HARD = 4         # 15-30 attempts
    EXPERT = 5       # 30+ attempts


class TrickCategory(Enum):
    """Categories of tricks."""
    BASIC = "basic"           # Sit, stay, come
    MOVEMENT = "movement"     # Dance, spin, jump
    INTERACTIVE = "interactive"  # Fetch, bring, give
    EXPRESSIVE = "expressive"    # Play dead, bow, wave
    ADVANCED = "advanced"     # Complex combinations


class Trick:
    """Represents a learnable trick."""

    def __init__(self, name: str, difficulty: TrickDifficulty,
                 category: TrickCategory, description: str,
                 success_threshold: float = 0.7):
        """
        Initialize a trick.

        Args:
            name: Trick name (e.g., "sit", "dance")
            difficulty: How hard it is to learn
            category: Category of trick
            description: Human-readable description
            success_threshold: Proficiency needed to perform reliably (0-1)
        """
        self.name = name
        self.difficulty = difficulty
        self.category = category
        self.description = description
        self.success_threshold = success_threshold

        # Learning progress
        self.proficiency = 0.0  # Current skill level (0-1)
        self.practice_count = 0  # Total practice attempts
        self.success_count = 0   # Successful attempts
        self.last_practiced = None  # Timestamp
        self.last_success = None

        # Decay settings
        self.decay_rate = 0.01  # How fast skill degrades without practice

    def practice(self, personality_modifier: float = 1.0,
                mood_modifier: float = 1.0) -> Tuple[bool, float]:
        """
        Practice the trick.

        Args:
            personality_modifier: How personality affects learning (0.5-1.5)
            mood_modifier: How current mood affects learning (0.5-1.5)

        Returns:
            Tuple of (success, proficiency_gain)
        """
        self.practice_count += 1
        self.last_practiced = time.time()

        # Calculate learning rate based on difficulty
        base_learning_rate = 1.0 / (self.difficulty.value * 10)

        # Apply modifiers
        effective_learning_rate = base_learning_rate * personality_modifier * mood_modifier

        # Add randomness (sometimes you just get it!)
        randomness = np.random.normal(0, 0.1)
        proficiency_gain = effective_learning_rate + randomness

        # Update proficiency
        old_proficiency = self.proficiency
        self.proficiency = min(1.0, self.proficiency + proficiency_gain)

        # Determine success (easier as proficiency increases)
        success_chance = self.proficiency * 0.7 + 0.1  # 10% minimum chance
        success = np.random.random() < success_chance

        if success:
            self.success_count += 1
            self.last_success = time.time()
            # Bonus learning from success
            self.proficiency = min(1.0, self.proficiency + 0.02)

        return success, proficiency_gain

    def decay_skill(self, days_since_practice: float):
        """
        Decay skill level due to lack of practice.

        Args:
            days_since_practice: Days since last practice
        """
        if days_since_practice > 1:
            decay = self.decay_rate * days_since_practice
            self.proficiency = max(0.0, self.proficiency - decay)

    def can_perform(self) -> bool:
        """Check if trick can be performed reliably."""
        return self.proficiency >= self.success_threshold

    def is_mastered(self) -> bool:
        """Check if trick is fully mastered."""
        return self.proficiency >= 0.95

    def to_dict(self) -> Dict[str, Any]:
        """Serialize trick."""
        return {
            'name': self.name,
            'difficulty': self.difficulty.value,
            'category': self.category.value,
            'description': self.description,
            'success_threshold': self.success_threshold,
            'proficiency': self.proficiency,
            'practice_count': self.practice_count,
            'success_count': self.success_count,
            'last_practiced': self.last_practiced,
            'last_success': self.last_success,
            'decay_rate': self.decay_rate
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Trick':
        """Deserialize trick."""
        trick = cls(
            name=data['name'],
            difficulty=TrickDifficulty(data['difficulty']),
            category=TrickCategory(data['category']),
            description=data['description'],
            success_threshold=data['success_threshold']
        )
        trick.proficiency = data['proficiency']
        trick.practice_count = data['practice_count']
        trick.success_count = data['success_count']
        trick.last_practiced = data['last_practiced']
        trick.last_success = data['last_success']
        trick.decay_rate = data['decay_rate']
        return trick


class CommandRecognition:
    """
    Recognizes and learns voice/text commands.

    Uses fuzzy matching to understand variations of commands.
    """

    def __init__(self):
        """Initialize command recognition."""
        # Phase 6: Expanded command aliases (25 commands)
        self.command_aliases = {
            # Original 12
            'sit': ['sit', 'sit down', 'take a seat', 'park it'],
            'stay': ['stay', 'stay there', 'wait', 'hold'],
            'come': ['come', 'come here', 'here', 'to me'],
            'fetch': ['fetch', 'get it', 'bring it', 'retrieve'],
            'dance': ['dance', 'boogie', 'shake it', 'groove'],
            'spin': ['spin', 'turn around', 'twirl', 'rotate'],
            'jump': ['jump', 'hop', 'leap', 'bounce'],
            'play_dead': ['play dead', 'dead', 'bang'],
            'bow': ['bow', 'take a bow', 'curtsy'],
            'wave': ['wave', 'say hi', 'hello', 'greet'],
            'shake': ['shake', 'paw', 'shake hands'],
            'roll_over': ['roll over', 'roll', 'barrel roll'],

            # Phase 6: New commands (13 more)
            'speak': ['speak', 'bark', 'talk', 'say something'],
            'quiet': ['quiet', 'shh', 'silence', 'hush'],
            'heel': ['heel', 'walk with me', 'follow', 'stay close'],
            'drop_it': ['drop it', 'drop', 'let go', 'release'],
            'leave_it': ['leave it', 'ignore', 'don\'t touch', 'no'],
            'high_five': ['high five', 'give me five', 'slap hands'],
            'crawl': ['crawl', 'belly crawl', 'commando', 'low'],
            'back_up': ['back up', 'backwards', 'reverse', 'back'],
            'circle': ['circle', 'go around', 'orbit', 'loop'],
            'kiss': ['kiss', 'give kiss', 'smooch', 'lick'],
            'hug': ['hug', 'cuddle', 'embrace', 'snuggle'],
            'find_it': ['find it', 'search', 'seek', 'look for'],
            'go_to_bed': ['go to bed', 'bedtime', 'sleep', 'rest'],

            # Expert-level
            'balance': ['balance', 'hold it', 'nose balance'],
            'weave': ['weave', 'between legs', 'figure eight'],
        }

        # Learned custom commands
        self.custom_commands = {}

    def recognize_command(self, text: str) -> Optional[str]:
        """
        Recognize a command from text input.

        Args:
            text: Command text (case-insensitive)

        Returns:
            Recognized command name or None
        """
        text_lower = text.lower().strip()

        # Check built-in commands
        for command, aliases in self.command_aliases.items():
            if any(alias in text_lower for alias in aliases):
                return command

        # Check custom commands
        for command, aliases in self.custom_commands.items():
            if any(alias in text_lower for alias in aliases):
                return command

        return None

    def add_custom_command(self, command_name: str, aliases: List[str]):
        """
        Add a custom command.

        Args:
            command_name: Name of the command
            aliases: List of text variations
        """
        self.custom_commands[command_name] = [a.lower().strip() for a in aliases]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize command recognition."""
        return {
            'custom_commands': self.custom_commands
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandRecognition':
        """Deserialize command recognition."""
        recognizer = cls()
        recognizer.custom_commands = data.get('custom_commands', {})
        return recognizer


class NameRecognition:
    """
    Recognizes when the pet's name is spoken.

    Learns to respond to its name with personality-appropriate reactions.
    """

    def __init__(self, pet_name: str):
        """
        Initialize name recognition.

        Args:
            pet_name: The pet's name
        """
        self.pet_name = pet_name.lower()
        self.recognition_count = 0
        self.last_recognized = None
        self.recognition_proficiency = 0.0  # How well it responds to its name

    def check_for_name(self, text: str) -> bool:
        """
        Check if text contains the pet's name.

        Args:
            text: Text to check

        Returns:
            True if name is present
        """
        if self.pet_name in text.lower():
            self.recognition_count += 1
            self.last_recognized = time.time()

            # Improve recognition proficiency
            self.recognition_proficiency = min(1.0, self.recognition_proficiency + 0.05)

            return True
        return False

    def get_name_response(self, personality: PersonalityType) -> str:
        """
        Get an appropriate response to hearing its name.

        Args:
            personality: Pet's personality type

        Returns:
            Response type (for animation/behavior)
        """
        if self.recognition_proficiency < 0.3:
            # Still learning name - might not respond
            if np.random.random() < 0.5:
                return 'ignore'

        # Personality-based responses (Phase 3: All 25 types)
        responses = {
            # Original 8
            PersonalityType.PLAYFUL: ['jump', 'spin', 'excited'],
            PersonalityType.SHY: ['peek', 'slow_approach', 'timid'],
            PersonalityType.ENERGETIC: ['run_over', 'bounce', 'hyperactive'],
            PersonalityType.LAZY: ['look', 'slow_turn', 'minimal'],
            PersonalityType.CURIOUS: ['tilt_head', 'investigate', 'interested'],
            PersonalityType.INDEPENDENT: ['acknowledge', 'brief_look', 'casual'],
            PersonalityType.AFFECTIONATE: ['rush_over', 'devoted', 'immediate'],
            PersonalityType.MISCHIEVOUS: ['playful_ignore', 'tease', 'game'],

            # Phase 3: New personalities
            PersonalityType.CRANKY: ['grunt', 'reluctant_look', 'annoyed'],
            PersonalityType.STUBBORN: ['stand_ground', 'defiant_stare', 'resistant'],
            PersonalityType.SKITTISH: ['flinch', 'nervous_peek', 'startled'],
            PersonalityType.BRAVE: ['confident_stride', 'bold_approach', 'fearless'],
            PersonalityType.GENTLE: ['soft_approach', 'tender_look', 'calm_response'],
            PersonalityType.FIERCE: ['aggressive_stance', 'territorial', 'intense_stare'],
            PersonalityType.CLEVER: ['knowing_look', 'calculated_approach', 'smart_response'],
            PersonalityType.SILLY: ['goofy_dance', 'clumsy_rush', 'derpy_wiggle'],
            PersonalityType.SERIOUS: ['formal_acknowledgment', 'composed_look', 'dignified'],
            PersonalityType.PATIENT: ['wait_calmly', 'peaceful_approach', 'serene'],
            PersonalityType.IMPATIENT: ['dash_over', 'hurried_response', 'restless'],
            PersonalityType.TRUSTING: ['immediate_trust', 'open_approach', 'welcoming'],
            PersonalityType.SUSPICIOUS: ['wary_glance', 'cautious_peek', 'distrustful'],
            PersonalityType.CALM: ['peaceful_turn', 'relaxed_acknowledgment', 'tranquil'],
            PersonalityType.ANXIOUS: ['worried_look', 'nervous_response', 'tense'],
            PersonalityType.LOYAL: ['devoted_rush', 'faithful_approach', 'dedicated'],
            PersonalityType.SELFISH: ['dismissive_glance', 'self_focused', 'aloof']
        }

        if personality in responses:
            return np.random.choice(responses[personality])

        return 'look'  # Default response

    def to_dict(self) -> Dict[str, Any]:
        """Serialize name recognition."""
        return {
            'pet_name': self.pet_name,
            'recognition_count': self.recognition_count,
            'last_recognized': self.last_recognized,
            'recognition_proficiency': self.recognition_proficiency
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NameRecognition':
        """Deserialize name recognition."""
        recognizer = cls(pet_name=data['pet_name'])
        recognizer.recognition_count = data['recognition_count']
        recognizer.last_recognized = data['last_recognized']
        recognizer.recognition_proficiency = data['recognition_proficiency']
        return recognizer


class TrainingSystem:
    """
    Complete training system for desktop pal.

    Manages:
    - Trick library and learning
    - Command recognition
    - Name recognition
    - Personality-based learning modifiers
    - Practice schedules and skill decay
    """

    # Phase 6: Expanded tricks library (25 total)
    STANDARD_TRICKS = {
        # Original 12
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

    def __init__(self, creature_name: str, personality: PersonalityType):
        """
        Initialize training system.

        Args:
            creature_name: Name of the pet
            personality: Pet's personality type
        """
        self.personality = personality
        self.learned_tricks = {}  # Tricks currently being learned or mastered
        self.command_recognition = CommandRecognition()
        self.name_recognition = NameRecognition(creature_name)

        # Personality-based learning modifiers
        self.learning_modifiers = self._get_personality_modifiers()

        # Phase 6: Enhanced training systems
        try:
            from .enhanced_training import (
                ReinforcementSystem, StubbornessCalculator, TrainingProgressTracker
            )
            self.reinforcement = ReinforcementSystem()
            self.stubbornness_calc = StubbornessCalculator()
            self.progress_tracker = TrainingProgressTracker()
            self.phase6_enabled = True
        except ImportError:
            # Phase 6 not available
            self.reinforcement = None
            self.stubbornness_calc = None
            self.progress_tracker = None
            self.phase6_enabled = False

    def _get_personality_modifiers(self) -> Dict[str, float]:
        """
        Get learning rate modifiers based on personality (Phase 3: All 25 types).

        Returns:
            Dictionary of modifiers
        """
        modifiers = {
            # Original 8 personalities
            PersonalityType.PLAYFUL: {'learning_rate': 1.2, 'stubbornness': 0.3},
            PersonalityType.SHY: {'learning_rate': 0.8, 'stubbornness': 0.5},
            PersonalityType.ENERGETIC: {'learning_rate': 1.3, 'stubbornness': 0.2},
            PersonalityType.LAZY: {'learning_rate': 0.7, 'stubbornness': 0.6},
            PersonalityType.CURIOUS: {'learning_rate': 1.4, 'stubbornness': 0.1},
            PersonalityType.INDEPENDENT: {'learning_rate': 0.9, 'stubbornness': 0.7},
            PersonalityType.AFFECTIONATE: {'learning_rate': 1.1, 'stubbornness': 0.2},
            PersonalityType.MISCHIEVOUS: {'learning_rate': 1.0, 'stubbornness': 0.8},

            # Phase 3: New personalities
            PersonalityType.CRANKY: {'learning_rate': 0.6, 'stubbornness': 0.9},
            PersonalityType.STUBBORN: {'learning_rate': 0.5, 'stubbornness': 0.95},
            PersonalityType.SKITTISH: {'learning_rate': 0.7, 'stubbornness': 0.6},
            PersonalityType.BRAVE: {'learning_rate': 1.2, 'stubbornness': 0.3},
            PersonalityType.GENTLE: {'learning_rate': 1.1, 'stubbornness': 0.2},
            PersonalityType.FIERCE: {'learning_rate': 0.9, 'stubbornness': 0.8},
            PersonalityType.CLEVER: {'learning_rate': 1.7, 'stubbornness': 0.2},
            PersonalityType.SILLY: {'learning_rate': 0.8, 'stubbornness': 0.5},
            PersonalityType.SERIOUS: {'learning_rate': 1.3, 'stubbornness': 0.3},
            PersonalityType.PATIENT: {'learning_rate': 1.4, 'stubbornness': 0.1},
            PersonalityType.IMPATIENT: {'learning_rate': 0.9, 'stubbornness': 0.7},
            PersonalityType.TRUSTING: {'learning_rate': 1.4, 'stubbornness': 0.1},
            PersonalityType.SUSPICIOUS: {'learning_rate': 0.8, 'stubbornness': 0.8},
            PersonalityType.CALM: {'learning_rate': 1.2, 'stubbornness': 0.2},
            PersonalityType.ANXIOUS: {'learning_rate': 0.6, 'stubbornness': 0.7},
            PersonalityType.LOYAL: {'learning_rate': 1.5, 'stubbornness': 0.05},
            PersonalityType.SELFISH: {'learning_rate': 0.7, 'stubbornness': 0.85},
        }

        return modifiers.get(self.personality, {'learning_rate': 1.0, 'stubbornness': 0.5})

    def start_learning_trick(self, trick_name: str) -> Tuple[bool, str]:
        """
        Start learning a new trick.

        Args:
            trick_name: Name of trick to learn

        Returns:
            Tuple of (success, message)
        """
        if trick_name in self.learned_tricks:
            return False, f"Already know or learning '{trick_name}'"

        if trick_name not in self.STANDARD_TRICKS:
            return False, f"Unknown trick '{trick_name}'"

        # Clone the standard trick
        trick = Trick(
            self.STANDARD_TRICKS[trick_name].name,
            self.STANDARD_TRICKS[trick_name].difficulty,
            self.STANDARD_TRICKS[trick_name].category,
            self.STANDARD_TRICKS[trick_name].description,
            self.STANDARD_TRICKS[trick_name].success_threshold
        )

        self.learned_tricks[trick_name] = trick
        return True, f"Started learning '{trick_name}'!"

    def practice_trick(self, trick_name: str, mood: float = 0.5) -> Tuple[bool, str, float]:
        """
        Practice a trick.

        Args:
            trick_name: Name of trick to practice
            mood: Current mood (0-1), affects learning

        Returns:
            Tuple of (success, message, proficiency_gain)
        """
        if trick_name not in self.learned_tricks:
            return False, f"Haven't started learning '{trick_name}' yet", 0.0

        trick = self.learned_tricks[trick_name]

        # Check stubbornness - sometimes pet refuses
        if np.random.random() < self.learning_modifiers['stubbornness']:
            return False, "Refused to practice (feeling stubborn!)", 0.0

        # Calculate mood modifier (happy pets learn better)
        mood_modifier = 0.5 + mood * 0.5  # Range: 0.5 to 1.0

        # Practice the trick
        success, gain = trick.practice(
            personality_modifier=self.learning_modifiers['learning_rate'],
            mood_modifier=mood_modifier
        )

        if success:
            if trick.is_mastered():
                message = f"✨ Mastered '{trick_name}'! (proficiency: {trick.proficiency:.1%})"
            elif trick.can_perform():
                message = f"✓ Successfully performed '{trick_name}' (proficiency: {trick.proficiency:.1%})"
            else:
                message = f"Did '{trick_name}'! Still learning... (proficiency: {trick.proficiency:.1%})"
        else:
            message = f"Tried '{trick_name}' but failed (proficiency: {trick.proficiency:.1%})"

        return success, message, gain

    def perform_trick(self, trick_name: str) -> Tuple[bool, str]:
        """
        Attempt to perform a learned trick.

        Args:
            trick_name: Name of trick to perform

        Returns:
            Tuple of (success, message)
        """
        if trick_name not in self.learned_tricks:
            return False, f"Don't know trick '{trick_name}'"

        trick = self.learned_tricks[trick_name]

        if not trick.can_perform():
            return False, f"Haven't practiced '{trick_name}' enough yet (proficiency: {trick.proficiency:.1%})"

        # Success chance based on proficiency
        success_chance = trick.proficiency * 0.9 + 0.1
        success = np.random.random() < success_chance

        if success:
            trick.last_success = time.time()
            return True, f"Performed '{trick_name}' successfully!"
        else:
            return False, f"Attempted '{trick_name}' but fumbled it"

    def process_command(self, text: str, current_mood: float = 0.5) -> Tuple[bool, str, Optional[str]]:
        """
        Process a text command.

        Args:
            text: Command text
            current_mood: Current mood affects compliance

        Returns:
            Tuple of (success, message, action_to_perform)
        """
        # Check for name first
        heard_name = self.name_recognition.check_for_name(text)

        if heard_name and np.random.random() < 0.3:
            # Sometimes just responds to name
            response = self.name_recognition.get_name_response(self.personality)
            return True, f"Heard name! Responding: {response}", response

        # Recognize command
        command = self.command_recognition.recognize_command(text)

        if not command:
            return False, "Didn't understand that command", None

        # Try to perform the trick
        success, message = self.perform_trick(command)

        if success:
            return True, message, command
        else:
            # Offer to practice if don't know it yet
            if command not in self.learned_tricks:
                self.start_learning_trick(command)
                return False, f"Don't know '{command}' yet, but started learning it!", None
            else:
                return False, message, None

    def update_skill_decay(self):
        """Update all tricks with skill decay from lack of practice."""
        now = time.time()

        for trick in self.learned_tricks.values():
            if trick.last_practiced:
                days_since = (now - trick.last_practiced) / (24 * 3600)
                if days_since > 1:
                    trick.decay_skill(days_since)

    def get_known_tricks(self) -> List[str]:
        """Get list of all tricks pet knows (can perform)."""
        return [name for name, trick in self.learned_tricks.items() if trick.can_perform()]

    def get_learning_tricks(self) -> List[str]:
        """Get list of tricks currently being learned."""
        return [name for name, trick in self.learned_tricks.items() if not trick.can_perform()]

    def get_mastered_tricks(self) -> List[str]:
        """Get list of fully mastered tricks."""
        return [name for name, trick in self.learned_tricks.items() if trick.is_mastered()]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize training system."""
        data = {
            'personality': self.personality.value,
            'learned_tricks': {name: trick.to_dict() for name, trick in self.learned_tricks.items()},
            'command_recognition': self.command_recognition.to_dict(),
            'name_recognition': self.name_recognition.to_dict(),
            'phase6_enabled': self.phase6_enabled
        }

        # Phase 6: Save enhanced training systems
        if self.phase6_enabled:
            if self.reinforcement:
                data['reinforcement'] = self.reinforcement.to_dict()
            if self.progress_tracker:
                data['progress_tracker'] = self.progress_tracker.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrainingSystem':
        """Deserialize training system."""
        personality = PersonalityType(data['personality'])
        pet_name = data['name_recognition']['pet_name']

        system = cls(creature_name=pet_name, personality=personality)

        # Restore learned tricks
        for name, trick_data in data['learned_tricks'].items():
            system.learned_tricks[name] = Trick.from_dict(trick_data)

        # Restore command and name recognition
        system.command_recognition = CommandRecognition.from_dict(data['command_recognition'])
        system.name_recognition = NameRecognition.from_dict(data['name_recognition'])

        # Phase 6: Restore enhanced training systems
        if data.get('phase6_enabled', False) and system.phase6_enabled:
            if 'reinforcement' in data:
                from .enhanced_training import ReinforcementSystem
                system.reinforcement = ReinforcementSystem.from_dict(data['reinforcement'])

            if 'progress_tracker' in data:
                from .enhanced_training import TrainingProgressTracker
                system.progress_tracker = TrainingProgressTracker.from_dict(data['progress_tracker'])

        return system
