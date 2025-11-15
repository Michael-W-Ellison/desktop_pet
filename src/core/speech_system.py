"""
Phase 10: Speech System

Generates procedural "pet speech" (gibberish language) based on phoneme patterns.
"""
import random
import time
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class SpeechMood(Enum):
    """Speech mood affects tone and pattern."""
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    ANGRY = "angry"
    CONFUSED = "confused"
    SLEEPY = "sleepy"
    LOVING = "loving"
    PLAYFUL = "playful"
    NEUTRAL = "neutral"


class SpeechType(Enum):
    """Type of speech utterance."""
    GREETING = "greeting"      # Hello, hi
    GOODBYE = "goodbye"        # Bye, see you
    HUNGRY = "hungry"          # Want food
    PLAYFUL = "playful"        # Let's play
    LOVE = "love"              # I love you
    HAPPY = "happy"            # Yay, woohoo
    SAD = "sad"                # Sad expressions
    QUESTION = "question"      # Asking something
    EXCLAMATION = "exclamation"  # Wow, oh no
    NAME_CALL = "name_call"    # Calling owner
    COMPLAINT = "complaint"    # Whining, complaining
    PRAISE = "praise"          # Good, yes


class PhonemeSet:
    """Defines phoneme patterns for a language."""

    def __init__(self, name: str, consonants: List[str], vowels: List[str],
                 syllable_patterns: List[str], emphasis_chars: str = "!"):
        """
        Initialize phoneme set.

        Args:
            name: Language name
            consonants: List of consonant sounds
            vowels: List of vowel sounds
            syllable_patterns: Patterns like "CV", "CVC", "V"
            emphasis_chars: Characters for emphasis
        """
        self.name = name
        self.consonants = consonants
        self.vowels = vowels
        self.syllable_patterns = syllable_patterns
        self.emphasis_chars = emphasis_chars

    def generate_syllable(self) -> str:
        """Generate a single syllable."""
        pattern = random.choice(self.syllable_patterns)
        syllable = ""

        for char in pattern:
            if char == 'C':
                syllable += random.choice(self.consonants)
            elif char == 'V':
                syllable += random.choice(self.vowels)

        return syllable


class SpeechSystem:
    """
    Generates procedural pet speech (gibberish language).

    Features:
    - Creature-specific phoneme patterns
    - Mood-based speech variations
    - Consistent "words" for common concepts
    - Emphasis and intonation
    - Speech bubbles with text
    - Procedural pronunciation
    """

    def __init__(self, creature_type: str = "cat", language_seed: Optional[int] = None):
        """
        Initialize speech system.

        Args:
            creature_type: Type of creature
            language_seed: Random seed for consistent language
        """
        self.creature_type = creature_type

        # Set random seed for consistent language
        if language_seed is not None:
            random.seed(language_seed)

        # Phoneme set for this creature
        self.phoneme_set = self._create_phoneme_set(creature_type)

        # Vocabulary (consistent "words" for concepts)
        self.vocabulary: Dict[str, str] = {}
        self._generate_vocabulary()

        # Speech settings
        self.speech_rate = 1.0  # Speed multiplier
        self.verbosity = 0.7  # How much they talk (0-1)
        self.expressiveness = 0.8  # How much emphasis (0-1)

        # Current speech
        self.current_speech: Optional[str] = None
        self.speech_start_time = 0.0
        self.speech_duration = 0.0

        # Statistics
        self.total_utterances = 0
        self.utterances_by_type: Dict[str, int] = {}

        # Restore random state
        if language_seed is not None:
            random.seed()

    def _create_phoneme_set(self, creature_type: str) -> PhonemeSet:
        """
        Create phoneme set for creature type.

        Args:
            creature_type: Type of creature

        Returns:
            PhonemeSet for this creature
        """
        # Different creatures have different speech patterns
        phoneme_sets = {
            'cat': PhonemeSet(
                name='Cat-speak',
                consonants=['m', 'n', 'r', 'w', 'y', 'p', 'b'],
                vowels=['a', 'e', 'i', 'o', 'u', 'ow', 'aw', 'ee'],
                syllable_patterns=['CV', 'V', 'CVC', 'VC'],
                emphasis_chars='~!'
            ),
            'dog': PhonemeSet(
                name='Dog-speak',
                consonants=['w', 'r', 'f', 'b', 'g', 'h', 'd', 'f'],
                vowels=['a', 'o', 'u', 'oo', 'aw', 'uh'],
                syllable_patterns=['CV', 'CVC', 'V'],
                emphasis_chars='!'
            ),
            'bird': PhonemeSet(
                name='Bird-speak',
                consonants=['ch', 'p', 't', 'k', 'r', 's', 'w'],
                vowels=['ee', 'i', 'e', 'a', 'u'],
                syllable_patterns=['CV', 'V', 'CCV'],
                emphasis_chars='♪!'
            ),
            'dragon': PhonemeSet(
                name='Dragon-speak',
                consonants=['r', 'g', 'k', 'z', 's', 'th', 'v'],
                vowels=['a', 'o', 'u', 'aa', 'oo'],
                syllable_patterns=['CVC', 'CV', 'CVCC'],
                emphasis_chars='!~'
            ),
            'rabbit': PhonemeSet(
                name='Rabbit-speak',
                consonants=['n', 'm', 'p', 'f', 'th', 'b'],
                vowels=['i', 'e', 'u', 'ee', 'oo'],
                syllable_patterns=['CV', 'CVC', 'V'],
                emphasis_chars='~'
            )
        }

        return phoneme_sets.get(creature_type, phoneme_sets['cat'])

    def _generate_vocabulary(self):
        """Generate consistent vocabulary for common concepts."""
        # Generate "words" for common concepts
        concepts = [
            # Greetings & social
            'hello', 'goodbye', 'yes', 'no', 'please', 'thank_you',
            # Needs
            'food', 'water', 'play', 'sleep', 'bathroom',
            # Emotions
            'happy', 'sad', 'love', 'angry', 'scared', 'excited',
            # Requests
            'want', 'need', 'give', 'come', 'go',
            # Objects
            'toy', 'bed', 'owner', 'friend',
            # Questions
            'what', 'where', 'why', 'how', 'when'
        ]

        for concept in concepts:
            # Generate 1-3 syllable word for this concept
            syllable_count = random.randint(1, 3)
            word = ""
            for _ in range(syllable_count):
                word += self.phoneme_set.generate_syllable()
            self.vocabulary[concept] = word

    def generate_speech(self, speech_type: SpeechType, mood: SpeechMood = SpeechMood.NEUTRAL,
                       intensity: float = 0.5) -> str:
        """
        Generate speech for a situation.

        Args:
            speech_type: Type of speech
            mood: Mood of speech
            intensity: Intensity (0-1)

        Returns:
            Generated speech text
        """
        utterance = self._generate_utterance(speech_type, mood, intensity)

        # Apply mood modifiers
        utterance = self._apply_mood_effects(utterance, mood, intensity)

        # Record statistics
        self.total_utterances += 1
        type_name = speech_type.value
        if type_name not in self.utterances_by_type:
            self.utterances_by_type[type_name] = 0
        self.utterances_by_type[type_name] += 1

        # Set current speech
        self.current_speech = utterance
        self.speech_start_time = time.time()
        # Duration based on length (roughly 4 chars per second)
        self.speech_duration = len(utterance) / (4.0 * self.speech_rate)

        return utterance

    def _generate_utterance(self, speech_type: SpeechType, mood: SpeechMood,
                           intensity: float) -> str:
        """Generate base utterance."""
        # Map speech types to vocabulary words and patterns
        if speech_type == SpeechType.GREETING:
            words = [self.vocabulary.get('hello', 'meow')]
            if mood == SpeechMood.EXCITED:
                words.append(words[0])  # Repeat for excitement

        elif speech_type == SpeechType.GOODBYE:
            words = [self.vocabulary.get('goodbye', 'mew')]

        elif speech_type == SpeechType.HUNGRY:
            words = [
                self.vocabulary.get('want', 'nya'),
                self.vocabulary.get('food', 'nom')
            ]

        elif speech_type == SpeechType.PLAYFUL:
            words = [self.vocabulary.get('play', 'yay')]
            if random.random() < intensity:
                words.append(self.vocabulary.get('come', 'nya'))

        elif speech_type == SpeechType.LOVE:
            words = [
                self.vocabulary.get('love', 'purr'),
                self.vocabulary.get('owner', 'mew')
            ]

        elif speech_type == SpeechType.HAPPY:
            words = [self.vocabulary.get('happy', 'yay')]
            # More syllables when happier
            if intensity > 0.7:
                words.append(words[0])

        elif speech_type == SpeechType.SAD:
            words = [self.vocabulary.get('sad', 'mew')]

        elif speech_type == SpeechType.QUESTION:
            words = [
                self.vocabulary.get('what', 'nya'),
                '?'
            ]

        elif speech_type == SpeechType.EXCLAMATION:
            # Random excited syllables
            syllable_count = random.randint(2, 4)
            word = ""
            for _ in range(syllable_count):
                word += self.phoneme_set.generate_syllable()
            words = [word]

        elif speech_type == SpeechType.NAME_CALL:
            words = [
                self.vocabulary.get('owner', 'mew'),
                self.vocabulary.get('come', 'nya')
            ]

        elif speech_type == SpeechType.COMPLAINT:
            words = [self.vocabulary.get('want', 'nya')]
            # Whiny repetition
            words.append(words[0])

        elif speech_type == SpeechType.PRAISE:
            words = [self.vocabulary.get('yes', 'ya')]
            words.append(self.vocabulary.get('happy', 'yay'))

        else:
            # Generate random utterance
            syllable_count = random.randint(2, 5)
            word = ""
            for _ in range(syllable_count):
                word += self.phoneme_set.generate_syllable()
            words = [word]

        # Join words
        utterance = " ".join(str(w) for w in words)
        return utterance

    def _apply_mood_effects(self, utterance: str, mood: SpeechMood,
                           intensity: float) -> str:
        """Apply mood-based effects to utterance."""
        # Capitalization based on intensity
        if intensity > 0.7:
            utterance = utterance.upper()
        elif intensity > 0.4:
            utterance = utterance.capitalize()

        # Add emphasis characters
        if self.expressiveness > 0.5:
            emphasis_count = int(intensity * 3)

            if mood in [SpeechMood.EXCITED, SpeechMood.HAPPY, SpeechMood.PLAYFUL]:
                utterance += self.phoneme_set.emphasis_chars[0] * emphasis_count
            elif mood in [SpeechMood.ANGRY]:
                utterance += '!' * emphasis_count
            elif mood == SpeechMood.CONFUSED:
                utterance += '?'
            elif mood == SpeechMood.LOVING:
                utterance += '♥' * min(emphasis_count, 2)
            elif mood == SpeechMood.SLEEPY:
                utterance += '...'

        # Elongate vowels for some moods
        if mood == SpeechMood.SLEEPY and random.random() < 0.5:
            # Stretch vowels
            for vowel in ['a', 'e', 'i', 'o', 'u']:
                utterance = utterance.replace(vowel, vowel * 2)

        return utterance

    def speak(self, speech_type: SpeechType, mood: Optional[SpeechMood] = None,
             intensity: float = 0.5) -> Dict[str, Any]:
        """
        Make pet speak.

        Args:
            speech_type: Type of speech
            mood: Speech mood (defaults to neutral)
            intensity: Intensity (0-1)

        Returns:
            Speech data including text and duration
        """
        if mood is None:
            mood = SpeechMood.NEUTRAL

        # Check verbosity (sometimes pets don't speak)
        if random.random() > self.verbosity:
            return {
                'spoke': False,
                'reason': 'not_verbose'
            }

        text = self.generate_speech(speech_type, mood, intensity)

        return {
            'spoke': True,
            'text': text,
            'speech_type': speech_type.value,
            'mood': mood.value,
            'intensity': intensity,
            'duration': self.speech_duration,
            'phonemes': len(text.replace(' ', ''))
        }

    def is_speaking(self) -> bool:
        """Check if currently speaking."""
        if not self.current_speech:
            return False
        return time.time() - self.speech_start_time < self.speech_duration

    def get_current_speech(self) -> Optional[str]:
        """Get current speech text if speaking."""
        if self.is_speaking():
            return self.current_speech
        return None

    def set_verbosity(self, verbosity: float):
        """
        Set how much the pet talks.

        Args:
            verbosity: Verbosity level (0-1)
        """
        self.verbosity = max(0.0, min(1.0, verbosity))

    def set_expressiveness(self, expressiveness: float):
        """
        Set how expressive the speech is.

        Args:
            expressiveness: Expressiveness level (0-1)
        """
        self.expressiveness = max(0.0, min(1.0, expressiveness))

    def translate_to_speech(self, concept: str) -> str:
        """
        Translate a concept to pet speech.

        Args:
            concept: Concept to translate

        Returns:
            Pet speech word
        """
        return self.vocabulary.get(concept, self._generate_random_word())

    def _generate_random_word(self, syllables: Optional[int] = None) -> str:
        """Generate a random word."""
        if syllables is None:
            syllables = random.randint(1, 3)

        word = ""
        for _ in range(syllables):
            word += self.phoneme_set.generate_syllable()
        return word

    def get_status(self) -> Dict[str, Any]:
        """Get speech system status."""
        return {
            'creature_type': self.creature_type,
            'language': self.phoneme_set.name,
            'vocabulary_size': len(self.vocabulary),
            'is_speaking': self.is_speaking(),
            'current_speech': self.get_current_speech(),
            'verbosity': self.verbosity,
            'expressiveness': self.expressiveness,
            'speech_rate': self.speech_rate,
            'total_utterances': self.total_utterances,
            'utterances_by_type': self.utterances_by_type.copy()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'creature_type': self.creature_type,
            'vocabulary': self.vocabulary.copy(),
            'speech_rate': self.speech_rate,
            'verbosity': self.verbosity,
            'expressiveness': self.expressiveness,
            'total_utterances': self.total_utterances,
            'utterances_by_type': self.utterances_by_type.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpeechSystem':
        """Deserialize from dictionary."""
        system = cls(creature_type=data.get('creature_type', 'cat'))
        system.vocabulary = data.get('vocabulary', {})
        system.speech_rate = data.get('speech_rate', 1.0)
        system.verbosity = data.get('verbosity', 0.7)
        system.expressiveness = data.get('expressiveness', 0.8)
        system.total_utterances = data.get('total_utterances', 0)
        system.utterances_by_type = data.get('utterances_by_type', {})
        return system
