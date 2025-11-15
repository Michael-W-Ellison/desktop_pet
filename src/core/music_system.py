"""
Phase 10: Music System

Manages mood-based background music with smooth transitions.
"""
import time
import random
from typing import Dict, Any, List, Optional
from enum import Enum


class MusicMood(Enum):
    """Music mood categories."""
    HAPPY = "happy"          # Upbeat, cheerful
    CALM = "calm"            # Peaceful, relaxed
    PLAYFUL = "playful"      # Energetic, fun
    SAD = "sad"              # Melancholic, somber
    MYSTERIOUS = "mysterious"  # Ambient, ethereal
    ENERGETIC = "energetic"  # Fast-paced, exciting
    SLEEPY = "sleepy"        # Gentle, drowsy
    LOVING = "loving"        # Warm, affectionate
    ANXIOUS = "anxious"      # Tense, worried


class MusicTrack:
    """Represents a music track."""

    def __init__(self, track_id: str, mood: MusicMood, file_path: str,
                 duration: float = 120.0, bpm: int = 120,
                 intensity: float = 0.5):
        """
        Initialize music track.

        Args:
            track_id: Unique track identifier
            mood: Music mood
            file_path: Path to audio file
            duration: Track length in seconds
            bpm: Beats per minute
            intensity: Intensity level (0-1)
        """
        self.track_id = track_id
        self.mood = mood
        self.file_path = file_path
        self.duration = duration
        self.bpm = bpm
        self.intensity = intensity
        self.play_count = 0
        self.last_played = 0.0


class MusicSystem:
    """
    Manages mood-based background music with smooth transitions.

    Features:
    - Mood-based track selection
    - Smooth crossfading between tracks
    - Dynamic tempo adjustments
    - Volume ducking for sound effects
    - Playlist management
    - Adaptive music intensity
    """

    def __init__(self):
        """Initialize music system."""
        # Music library
        self.tracks: Dict[str, MusicTrack] = {}
        self.tracks_by_mood: Dict[MusicMood, List[MusicTrack]] = {}

        # Playback state
        self.current_track: Optional[MusicTrack] = None
        self.next_track: Optional[MusicTrack] = None
        self.current_mood = MusicMood.CALM
        self.playback_position = 0.0

        # Transition state
        self.is_transitioning = False
        self.transition_time = 0.0
        self.transition_duration = 3.0  # 3 second crossfade

        # Volume controls
        self.music_volume = 0.7
        self.master_volume = 1.0
        self.ducking_volume = 1.0  # Reduced when sounds play

        # Settings
        self.music_enabled = True
        self.shuffle_mode = True
        self.auto_mood_change = True
        self.loop_track = False

        # Mood history (for intelligent track selection)
        self.mood_history: List[Tuple[MusicMood, float]] = []  # (mood, timestamp)
        self.mood_change_cooldown = 30.0  # Min seconds between mood changes

        # Statistics
        self.total_tracks_played = 0
        self.total_playtime = 0.0
        self.tracks_by_mood_count: Dict[str, int] = {}

        # Create default track library
        self._create_track_library()

    def _create_track_library(self):
        """Create default music track library."""
        default_tracks = [
            # Happy tracks
            ('happy_1', MusicMood.HAPPY, 'happy_tune.mp3', 150.0, 140, 0.7),
            ('happy_2', MusicMood.HAPPY, 'sunshine_day.mp3', 180.0, 130, 0.6),
            ('happy_3', MusicMood.HAPPY, 'joyful_bounce.mp3', 120.0, 145, 0.8),

            # Calm tracks
            ('calm_1', MusicMood.CALM, 'peaceful_meadow.mp3', 240.0, 80, 0.3),
            ('calm_2', MusicMood.CALM, 'gentle_breeze.mp3', 200.0, 75, 0.4),
            ('calm_3', MusicMood.CALM, 'tranquil_waters.mp3', 220.0, 70, 0.3),

            # Playful tracks
            ('playful_1', MusicMood.PLAYFUL, 'bouncy_fun.mp3', 140.0, 160, 0.8),
            ('playful_2', MusicMood.PLAYFUL, 'silly_games.mp3', 130.0, 155, 0.7),
            ('playful_3', MusicMood.PLAYFUL, 'happy_paws.mp3', 110.0, 150, 0.6),

            # Sad tracks
            ('sad_1', MusicMood.SAD, 'melancholy_rain.mp3', 200.0, 60, 0.4),
            ('sad_2', MusicMood.SAD, 'lonely_hearts.mp3', 180.0, 65, 0.3),

            # Sleepy tracks
            ('sleepy_1', MusicMood.SLEEPY, 'lullaby_dreams.mp3', 240.0, 50, 0.2),
            ('sleepy_2', MusicMood.SLEEPY, 'night_whispers.mp3', 260.0, 45, 0.2),
            ('sleepy_3', MusicMood.SLEEPY, 'sleepy_time.mp3', 220.0, 55, 0.3),

            # Energetic tracks
            ('energetic_1', MusicMood.ENERGETIC, 'power_play.mp3', 120.0, 180, 0.9),
            ('energetic_2', MusicMood.ENERGETIC, 'action_time.mp3', 130.0, 170, 0.8),

            # Loving tracks
            ('loving_1', MusicMood.LOVING, 'warm_embrace.mp3', 190.0, 90, 0.5),
            ('loving_2', MusicMood.LOVING, 'heartfelt.mp3', 210.0, 85, 0.4),

            # Mysterious tracks
            ('mysterious_1', MusicMood.MYSTERIOUS, 'ethereal_mist.mp3', 240.0, 100, 0.5),

            # Anxious tracks
            ('anxious_1', MusicMood.ANXIOUS, 'nervous_energy.mp3', 150.0, 140, 0.6),
        ]

        for track_id, mood, filename, duration, bpm, intensity in default_tracks:
            track = MusicTrack(
                track_id=track_id,
                mood=mood,
                file_path=f"assets/music/{filename}",
                duration=duration,
                bpm=bpm,
                intensity=intensity
            )
            self.add_track(track)

    def add_track(self, track: MusicTrack):
        """
        Add a music track to the library.

        Args:
            track: Track to add
        """
        self.tracks[track.track_id] = track

        # Add to mood index
        if track.mood not in self.tracks_by_mood:
            self.tracks_by_mood[track.mood] = []
        self.tracks_by_mood[track.mood].append(track)

    def set_mood(self, mood: MusicMood, force: bool = False):
        """
        Set current music mood.

        Args:
            mood: Desired music mood
            force: Force change even if on cooldown
        """
        # Check cooldown unless forced
        if not force and self.mood_history:
            last_change_time = self.mood_history[-1][1]
            if time.time() - last_change_time < self.mood_change_cooldown:
                return

        # Don't change if already this mood
        if mood == self.current_mood and self.current_track:
            return

        self.current_mood = mood
        self.mood_history.append((mood, time.time()))

        # Select and play track for this mood
        if self.music_enabled:
            self._select_and_play_track(mood)

    def _select_and_play_track(self, mood: MusicMood):
        """
        Select and play a track for the given mood.

        Args:
            mood: Music mood
        """
        # Get available tracks for this mood
        available_tracks = self.tracks_by_mood.get(mood, [])
        if not available_tracks:
            # Fallback to calm music
            available_tracks = self.tracks_by_mood.get(MusicMood.CALM, [])
            if not available_tracks:
                return

        # Select track
        if self.shuffle_mode:
            # Avoid playing same track twice in a row
            if len(available_tracks) > 1 and self.current_track:
                available_tracks = [t for t in available_tracks if t != self.current_track]
            track = random.choice(available_tracks)
        else:
            # Pick least recently played
            track = min(available_tracks, key=lambda t: t.last_played)

        # Start transition to new track
        self.next_track = track
        if self.current_track:
            self.is_transitioning = True
            self.transition_time = 0.0
        else:
            # No current track, start immediately
            self._switch_to_next_track()

    def _switch_to_next_track(self):
        """Switch to the next track."""
        if not self.next_track:
            return

        self.current_track = self.next_track
        self.next_track = None
        self.playback_position = 0.0
        self.is_transitioning = False
        self.transition_time = 0.0

        # Update statistics
        self.current_track.play_count += 1
        self.current_track.last_played = time.time()
        self.total_tracks_played += 1

        mood_name = self.current_track.mood.value
        if mood_name not in self.tracks_by_mood_count:
            self.tracks_by_mood_count[mood_name] = 0
        self.tracks_by_mood_count[mood_name] += 1

    def update(self, dt: float):
        """
        Update music system.

        Args:
            dt: Time elapsed in seconds
        """
        if not self.music_enabled or not self.current_track:
            return

        # Update transition
        if self.is_transitioning:
            self.transition_time += dt
            if self.transition_time >= self.transition_duration:
                self._switch_to_next_track()

        # Update playback position
        self.playback_position += dt
        self.total_playtime += dt

        # Check if track finished
        if self.playback_position >= self.current_track.duration:
            if self.loop_track:
                self.playback_position = 0.0
            else:
                # Auto-select next track
                self._select_and_play_track(self.current_mood)

    def get_volume(self) -> float:
        """
        Get current music volume.

        Returns:
            Effective volume (0-1)
        """
        # Apply ducking
        effective_volume = self.music_volume * self.ducking_volume * self.master_volume

        # Apply crossfade if transitioning
        if self.is_transitioning:
            fade_progress = self.transition_time / self.transition_duration
            # Crossfade curve (fade out current, fade in next)
            effective_volume *= (1.0 - fade_progress)

        return effective_volume

    def duck_volume(self, duck_amount: float = 0.5, duration: float = 0.5):
        """
        Temporarily reduce music volume (for sound effects).

        Args:
            duck_amount: Target ducking multiplier (0-1)
            duration: Duck duration in seconds
        """
        self.ducking_volume = duck_amount
        # In a real implementation, this would smoothly restore over 'duration'

    def restore_volume(self):
        """Restore full music volume after ducking."""
        self.ducking_volume = 1.0

    def set_volume(self, volume: float):
        """
        Set music volume.

        Args:
            volume: Volume (0-1)
        """
        self.music_volume = max(0.0, min(1.0, volume))

    def enable_music(self):
        """Enable background music."""
        self.music_enabled = True
        if not self.current_track:
            self._select_and_play_track(self.current_mood)

    def disable_music(self):
        """Disable background music."""
        self.music_enabled = False
        self.current_track = None
        self.next_track = None
        self.is_transitioning = False

    def skip_track(self):
        """Skip to next track."""
        if self.music_enabled:
            self._select_and_play_track(self.current_mood)

    def get_mood_from_emotions(self, happiness: float, energy: float,
                               stress: float) -> MusicMood:
        """
        Determine music mood from emotional state.

        Args:
            happiness: Happiness level (0-100)
            energy: Energy level (0-100)
            stress: Stress level (0-100)

        Returns:
            Appropriate music mood
        """
        # High stress
        if stress > 70:
            return MusicMood.ANXIOUS

        # Low energy (sleeping/tired)
        if energy < 20:
            return MusicMood.SLEEPY

        # High happiness, high energy
        if happiness > 70 and energy > 60:
            return MusicMood.PLAYFUL

        # High happiness, moderate energy
        if happiness > 70:
            return MusicMood.HAPPY

        # Low happiness
        if happiness < 30:
            return MusicMood.SAD

        # Very high energy
        if energy > 80:
            return MusicMood.ENERGETIC

        # Moderate happiness and energy
        if 40 <= happiness <= 70 and 30 <= energy <= 70:
            return MusicMood.CALM

        # Moderate happiness, low energy
        if 50 <= happiness <= 80 and energy < 40:
            return MusicMood.LOVING

        # Default
        return MusicMood.CALM

    def get_status(self) -> Dict[str, Any]:
        """Get music system status."""
        return {
            'music_enabled': self.music_enabled,
            'current_mood': self.current_mood.value,
            'current_track': self.current_track.track_id if self.current_track else None,
            'track_progress': (
                self.playback_position / self.current_track.duration
                if self.current_track else 0.0
            ),
            'is_transitioning': self.is_transitioning,
            'music_volume': self.music_volume,
            'effective_volume': self.get_volume(),
            'shuffle_mode': self.shuffle_mode,
            'total_tracks': len(self.tracks),
            'total_tracks_played': self.total_tracks_played,
            'total_playtime_hours': self.total_playtime / 3600.0,
            'tracks_by_mood_count': self.tracks_by_mood_count.copy()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'current_mood': self.current_mood.value,
            'music_enabled': self.music_enabled,
            'music_volume': self.music_volume,
            'shuffle_mode': self.shuffle_mode,
            'loop_track': self.loop_track,
            'total_tracks_played': self.total_tracks_played,
            'total_playtime': self.total_playtime,
            'tracks_by_mood_count': self.tracks_by_mood_count.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MusicSystem':
        """Deserialize from dictionary."""
        system = cls()
        system.current_mood = MusicMood(data.get('current_mood', 'calm'))
        system.music_enabled = data.get('music_enabled', True)
        system.music_volume = data.get('music_volume', 0.7)
        system.shuffle_mode = data.get('shuffle_mode', True)
        system.loop_track = data.get('loop_track', False)
        system.total_tracks_played = data.get('total_tracks_played', 0)
        system.total_playtime = data.get('total_playtime', 0.0)
        system.tracks_by_mood_count = data.get('tracks_by_mood_count', {})

        # Start music if enabled
        if system.music_enabled:
            system._select_and_play_track(system.current_mood)

        return system
