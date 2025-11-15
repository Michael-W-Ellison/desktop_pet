"""
Phase 10: Sound System

Manages creature-specific sounds and sound effects.
"""
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class SoundCategory(Enum):
    """Sound effect categories."""
    VOICE = "voice"              # Creature vocalizations
    MOVEMENT = "movement"        # Walking, jumping, etc.
    EATING = "eating"            # Eating, drinking sounds
    INTERACTION = "interaction"  # Petting, playing sounds
    EMOTION = "emotion"          # Happy, sad, angry sounds
    ENVIRONMENT = "environment"  # Ambient sounds
    UI = "ui"                    # UI feedback sounds
    SPECIAL = "special"          # Special effects


class SoundEvent(Enum):
    """Sound event types."""
    # Voice
    IDLE_CHIRP = "idle_chirp"
    HAPPY_CHIRP = "happy_chirp"
    SAD_WHINE = "sad_whine"
    ANGRY_GROWL = "angry_growl"
    EXCITED_YIP = "excited_yip"
    PURR = "purr"
    ROAR = "roar"
    SQUEAK = "squeak"

    # Movement
    FOOTSTEP = "footstep"
    JUMP = "jump"
    LAND = "land"
    FLAP_WINGS = "flap_wings"
    SPLASH = "splash"

    # Eating
    EATING_CRUNCH = "eating_crunch"
    DRINKING = "drinking"
    GULP = "gulp"
    BURP = "burp"

    # Interaction
    PET = "pet"
    PLAY = "play"
    CUDDLE = "cuddle"
    SCRATCH = "scratch"

    # Emotion
    LAUGH = "laugh"
    CRY = "cry"
    SIGH = "sigh"
    GASP = "gasp"
    SNEEZE = "sneeze"
    YAWN = "yawn"
    SNORE = "snore"

    # Special
    LEVEL_UP = "level_up"
    ACHIEVEMENT = "achievement"
    MAGIC = "magic"
    SPARKLE = "sparkle"


class Sound:
    """Represents a sound that can be played."""

    def __init__(self, sound_id: str, event: SoundEvent, category: SoundCategory,
                 file_path: Optional[str] = None,
                 volume: float = 1.0, pitch_variance: float = 0.1):
        """
        Initialize sound.

        Args:
            sound_id: Unique sound identifier
            event: Sound event type
            category: Sound category
            file_path: Path to audio file (or None for procedural)
            volume: Default volume (0-1)
            pitch_variance: Random pitch variation (0-1)
        """
        self.sound_id = sound_id
        self.event = event
        self.category = category
        self.file_path = file_path
        self.volume = volume
        self.pitch_variance = pitch_variance
        self.play_count = 0
        self.last_played = 0.0


class SoundInstance:
    """Represents a currently playing sound."""

    def __init__(self, sound: Sound, volume: float, pitch: float):
        """
        Initialize sound instance.

        Args:
            sound: Sound being played
            volume: Playback volume
            pitch: Playback pitch
        """
        self.sound = sound
        self.volume = volume
        self.pitch = pitch
        self.start_time = time.time()
        self.duration = 1.0  # Default duration
        self.finished = False

    def update(self, dt: float):
        """Update sound instance."""
        if time.time() - self.start_time >= self.duration:
            self.finished = True


class SoundSystem:
    """
    Manages creature sounds and sound effects.

    Features:
    - Creature-specific sound libraries
    - Contextual sound playback
    - Volume control and mixing
    - Sound cooldowns to prevent spam
    - Pitch variance for variety
    - Distance-based attenuation
    """

    def __init__(self, creature_type: str = "cat"):
        """
        Initialize sound system.

        Args:
            creature_type: Type of creature for species-specific sounds
        """
        self.creature_type = creature_type

        # Sound library
        self.sounds: Dict[str, Sound] = {}

        # Currently playing sounds
        self.playing_sounds: List[SoundInstance] = []

        # Volume controls
        self.master_volume = 1.0
        self.category_volumes: Dict[SoundCategory, float] = {
            cat: 1.0 for cat in SoundCategory
        }

        # Sound cooldowns (prevent spam)
        self.cooldowns: Dict[SoundEvent, float] = {}
        self.min_cooldown = 0.1  # Minimum time between same sounds

        # Settings
        self.muted = False
        self.max_concurrent_sounds = 8

        # Statistics
        self.total_sounds_played = 0
        self.sounds_by_category: Dict[str, int] = {}

        # Create creature-specific sound library
        self._create_sound_library()

    def _create_sound_library(self):
        """Create sound library for this creature type."""
        # Different creatures have different sounds
        creature_sounds = {
            'cat': {
                SoundEvent.IDLE_CHIRP: {'volume': 0.6, 'pitch_variance': 0.15},
                SoundEvent.PURR: {'volume': 0.5, 'pitch_variance': 0.05},
                SoundEvent.HAPPY_CHIRP: {'volume': 0.7, 'pitch_variance': 0.2},
                SoundEvent.SAD_WHINE: {'volume': 0.6, 'pitch_variance': 0.1},
                SoundEvent.ANGRY_GROWL: {'volume': 0.8, 'pitch_variance': 0.15},
            },
            'dog': {
                SoundEvent.IDLE_CHIRP: {'volume': 0.7, 'pitch_variance': 0.2},
                SoundEvent.HAPPY_CHIRP: {'volume': 0.9, 'pitch_variance': 0.25},
                SoundEvent.SAD_WHINE: {'volume': 0.7, 'pitch_variance': 0.15},
                SoundEvent.ANGRY_GROWL: {'volume': 0.9, 'pitch_variance': 0.1},
                SoundEvent.EXCITED_YIP: {'volume': 0.8, 'pitch_variance': 0.3},
            },
            'bird': {
                SoundEvent.IDLE_CHIRP: {'volume': 0.6, 'pitch_variance': 0.3},
                SoundEvent.HAPPY_CHIRP: {'volume': 0.7, 'pitch_variance': 0.35},
                SoundEvent.SQUEAK: {'volume': 0.5, 'pitch_variance': 0.25},
                SoundEvent.FLAP_WINGS: {'volume': 0.4, 'pitch_variance': 0.1},
            },
            'dragon': {
                SoundEvent.ROAR: {'volume': 1.0, 'pitch_variance': 0.1},
                SoundEvent.ANGRY_GROWL: {'volume': 0.9, 'pitch_variance': 0.15},
                SoundEvent.PURR: {'volume': 0.7, 'pitch_variance': 0.05},
                SoundEvent.FLAP_WINGS: {'volume': 0.6, 'pitch_variance': 0.1},
            }
        }

        # Get sounds for this creature (or use default)
        creature_specific = creature_sounds.get(self.creature_type, creature_sounds['cat'])

        # Add creature-specific voice sounds
        for event, params in creature_specific.items():
            sound_id = f"{self.creature_type}_{event.value}"
            self.add_sound(Sound(
                sound_id=sound_id,
                event=event,
                category=SoundCategory.VOICE,
                file_path=f"assets/sounds/{self.creature_type}/{event.value}.wav",
                volume=params['volume'],
                pitch_variance=params['pitch_variance']
            ))

        # Add universal sounds (all creatures)
        universal_sounds = [
            (SoundEvent.FOOTSTEP, SoundCategory.MOVEMENT, 0.3, 0.2),
            (SoundEvent.JUMP, SoundCategory.MOVEMENT, 0.5, 0.15),
            (SoundEvent.LAND, SoundCategory.MOVEMENT, 0.4, 0.15),
            (SoundEvent.EATING_CRUNCH, SoundCategory.EATING, 0.6, 0.2),
            (SoundEvent.DRINKING, SoundCategory.EATING, 0.5, 0.1),
            (SoundEvent.GULP, SoundCategory.EATING, 0.5, 0.15),
            (SoundEvent.PET, SoundCategory.INTERACTION, 0.4, 0.1),
            (SoundEvent.PLAY, SoundCategory.INTERACTION, 0.6, 0.2),
            (SoundEvent.YAWN, SoundCategory.EMOTION, 0.6, 0.15),
            (SoundEvent.SNEEZE, SoundCategory.EMOTION, 0.7, 0.2),
            (SoundEvent.SNORE, SoundCategory.EMOTION, 0.4, 0.1),
            (SoundEvent.LEVEL_UP, SoundCategory.SPECIAL, 0.8, 0.0),
            (SoundEvent.ACHIEVEMENT, SoundCategory.SPECIAL, 0.7, 0.0),
            (SoundEvent.MAGIC, SoundCategory.SPECIAL, 0.6, 0.1),
            (SoundEvent.SPARKLE, SoundCategory.SPECIAL, 0.5, 0.15),
        ]

        for event, category, volume, pitch_var in universal_sounds:
            sound_id = f"universal_{event.value}"
            self.add_sound(Sound(
                sound_id=sound_id,
                event=event,
                category=category,
                file_path=f"assets/sounds/universal/{event.value}.wav",
                volume=volume,
                pitch_variance=pitch_var
            ))

    def add_sound(self, sound: Sound):
        """
        Add a sound to the library.

        Args:
            sound: Sound to add
        """
        self.sounds[sound.sound_id] = sound

    def play_sound(self, event: SoundEvent, volume_override: Optional[float] = None,
                   pitch_override: Optional[float] = None,
                   ignore_cooldown: bool = False) -> bool:
        """
        Play a sound effect.

        Args:
            event: Sound event to play
            volume_override: Override default volume
            pitch_override: Override pitch (1.0 = normal)
            ignore_cooldown: Ignore cooldown timer

        Returns:
            True if sound played
        """
        if self.muted:
            return False

        # Check cooldown
        if not ignore_cooldown:
            if event in self.cooldowns:
                if time.time() - self.cooldowns[event] < self.min_cooldown:
                    return False

        # Find matching sound
        matching_sounds = [s for s in self.sounds.values() if s.event == event]
        if not matching_sounds:
            return False

        # Pick random matching sound (for variety)
        sound = random.choice(matching_sounds)

        # Check max concurrent sounds
        if len(self.playing_sounds) >= self.max_concurrent_sounds:
            # Remove oldest sound
            self.playing_sounds.pop(0)

        # Calculate final volume
        category_volume = self.category_volumes.get(sound.category, 1.0)
        if volume_override is not None:
            final_volume = volume_override * category_volume * self.master_volume
        else:
            final_volume = sound.volume * category_volume * self.master_volume

        # Calculate pitch with variance
        if pitch_override is not None:
            final_pitch = pitch_override
        else:
            pitch_variation = random.uniform(-sound.pitch_variance, sound.pitch_variance)
            final_pitch = 1.0 + pitch_variation

        # Create sound instance
        instance = SoundInstance(sound, final_volume, final_pitch)
        self.playing_sounds.append(instance)

        # Update statistics
        sound.play_count += 1
        sound.last_played = time.time()
        self.total_sounds_played += 1

        category_name = sound.category.value
        if category_name not in self.sounds_by_category:
            self.sounds_by_category[category_name] = 0
        self.sounds_by_category[category_name] += 1

        # Set cooldown
        self.cooldowns[event] = time.time()

        return True

    def play_random_voice(self, emotion: Optional[str] = None) -> bool:
        """
        Play a random voice sound.

        Args:
            emotion: Optional emotion filter (happy, sad, angry, etc.)

        Returns:
            True if sound played
        """
        voice_sounds = [s for s in self.sounds.values() if s.category == SoundCategory.VOICE]

        # Filter by emotion if specified
        if emotion:
            emotion_events = {
                'happy': [SoundEvent.HAPPY_CHIRP, SoundEvent.PURR, SoundEvent.EXCITED_YIP, SoundEvent.LAUGH],
                'sad': [SoundEvent.SAD_WHINE, SoundEvent.CRY, SoundEvent.SIGH],
                'angry': [SoundEvent.ANGRY_GROWL, SoundEvent.ROAR],
                'neutral': [SoundEvent.IDLE_CHIRP, SoundEvent.SQUEAK],
            }
            allowed_events = emotion_events.get(emotion, [])
            voice_sounds = [s for s in voice_sounds if s.event in allowed_events]

        if not voice_sounds:
            return False

        sound = random.choice(voice_sounds)
        return self.play_sound(sound.event)

    def update(self, dt: float):
        """
        Update sound system.

        Args:
            dt: Time elapsed in seconds
        """
        # Update playing sounds
        for instance in self.playing_sounds[:]:
            instance.update(dt)
            if instance.finished:
                self.playing_sounds.remove(instance)

    def set_master_volume(self, volume: float):
        """
        Set master volume.

        Args:
            volume: Volume (0-1)
        """
        self.master_volume = max(0.0, min(1.0, volume))

    def set_category_volume(self, category: SoundCategory, volume: float):
        """
        Set volume for a sound category.

        Args:
            category: Sound category
            volume: Volume (0-1)
        """
        self.category_volumes[category] = max(0.0, min(1.0, volume))

    def mute(self):
        """Mute all sounds."""
        self.muted = True

    def unmute(self):
        """Unmute sounds."""
        self.muted = False

    def stop_all_sounds(self):
        """Stop all currently playing sounds."""
        self.playing_sounds.clear()

    def get_playing_count(self, category: Optional[SoundCategory] = None) -> int:
        """
        Get count of currently playing sounds.

        Args:
            category: Optional category filter

        Returns:
            Number of playing sounds
        """
        if category:
            return len([s for s in self.playing_sounds if s.sound.category == category])
        return len(self.playing_sounds)

    def get_status(self) -> Dict[str, Any]:
        """Get sound system status."""
        return {
            'creature_type': self.creature_type,
            'master_volume': self.master_volume,
            'muted': self.muted,
            'playing_sounds': len(self.playing_sounds),
            'total_sounds_in_library': len(self.sounds),
            'total_sounds_played': self.total_sounds_played,
            'sounds_by_category': self.sounds_by_category.copy(),
            'category_volumes': {cat.value: vol for cat, vol in self.category_volumes.items()},
            'max_concurrent_sounds': self.max_concurrent_sounds
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'creature_type': self.creature_type,
            'master_volume': self.master_volume,
            'muted': self.muted,
            'category_volumes': {cat.value: vol for cat, vol in self.category_volumes.items()},
            'total_sounds_played': self.total_sounds_played,
            'sounds_by_category': self.sounds_by_category.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SoundSystem':
        """Deserialize from dictionary."""
        system = cls(creature_type=data.get('creature_type', 'cat'))
        system.master_volume = data.get('master_volume', 1.0)
        system.muted = data.get('muted', False)
        system.total_sounds_played = data.get('total_sounds_played', 0)
        system.sounds_by_category = data.get('sounds_by_category', {})

        # Restore category volumes
        category_volumes = data.get('category_volumes', {})
        for cat_str, vol in category_volumes.items():
            category = SoundCategory(cat_str)
            system.category_volumes[category] = vol

        return system
