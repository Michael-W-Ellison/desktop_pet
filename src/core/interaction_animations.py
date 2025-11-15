"""
Phase 15: Interaction Animations System

Manages animation states for furniture interactions.
"""
from typing import Dict, Any, List, Optional
from enum import Enum


class InteractionAnimationState(Enum):
    """Animation states for interactions."""
    APPROACH = "approach"        # Walking to furniture
    PREPARE = "prepare"          # Preparing to interact
    INTERACT_LOOP = "interact_loop"  # Main interaction animation (looping)
    INTERACT_ONCE = "interact_once"  # Single interaction animation
    FINISH = "finish"            # Finishing interaction
    RETURN = "return"            # Returning to idle


class AnimationType(Enum):
    """Types of animations."""
    SINGLE = "single"            # Plays once
    LOOP = "loop"                # Loops continuously
    PINGPONG = "pingpong"        # Plays forward then backward


class InteractionAnimation:
    """Represents an animation for an interaction."""

    def __init__(self, animation_id: str, name: str):
        """
        Initialize interaction animation.

        Args:
            animation_id: Unique animation ID
            name: Animation name
        """
        self.animation_id = animation_id
        self.name = name

        # Animation properties
        self.animation_type = AnimationType.LOOP
        self.frame_count = 8           # Number of frames
        self.frame_rate = 12           # Frames per second
        self.current_frame = 0
        self.elapsed_time = 0.0

        # State
        self.playing = False
        self.paused = False
        self.completed = False
        self.loop_count = 0

        # Timing
        self.duration = 0.0            # Calculated from frame_count/frame_rate

    def start(self):
        """Start playing the animation."""
        self.playing = True
        self.paused = False
        self.completed = False
        self.current_frame = 0
        self.elapsed_time = 0.0
        self.loop_count = 0
        self.duration = self.frame_count / self.frame_rate

    def stop(self):
        """Stop the animation."""
        self.playing = False
        self.paused = False
        self.current_frame = 0
        self.elapsed_time = 0.0

    def pause(self):
        """Pause the animation."""
        self.paused = True

    def resume(self):
        """Resume the animation."""
        self.paused = False

    def update(self, delta_time: float):
        """
        Update animation.

        Args:
            delta_time: Time since last update (seconds)
        """
        if not self.playing or self.paused:
            return

        self.elapsed_time += delta_time

        # Calculate current frame
        frame_time = 1.0 / self.frame_rate
        frame_index = int(self.elapsed_time / frame_time)

        if self.animation_type == AnimationType.SINGLE:
            # Play once
            if frame_index >= self.frame_count:
                self.current_frame = self.frame_count - 1
                self.completed = True
                self.playing = False
            else:
                self.current_frame = frame_index

        elif self.animation_type == AnimationType.LOOP:
            # Loop continuously
            if frame_index >= self.frame_count:
                self.loop_count += 1
                self.elapsed_time = 0.0
                frame_index = 0
            self.current_frame = frame_index

        elif self.animation_type == AnimationType.PINGPONG:
            # Ping pong back and forth
            cycle_frames = self.frame_count * 2 - 2
            frame_in_cycle = frame_index % cycle_frames
            if frame_in_cycle < self.frame_count:
                self.current_frame = frame_in_cycle
            else:
                self.current_frame = cycle_frames - frame_in_cycle

            if frame_index >= cycle_frames:
                self.loop_count += 1

    def get_progress(self) -> float:
        """Get animation progress (0-1)."""
        if self.frame_count == 0:
            return 1.0
        return self.current_frame / (self.frame_count - 1)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'animation_id': self.animation_id,
            'name': self.name,
            'animation_type': self.animation_type.value,
            'frame_count': self.frame_count,
            'frame_rate': self.frame_rate,
            'current_frame': self.current_frame,
            'elapsed_time': self.elapsed_time,
            'playing': self.playing,
            'paused': self.paused,
            'completed': self.completed,
            'loop_count': self.loop_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractionAnimation':
        """Deserialize from dictionary."""
        animation = cls(
            animation_id=data['animation_id'],
            name=data['name']
        )
        animation.animation_type = AnimationType(data.get('animation_type', 'loop'))
        animation.frame_count = data.get('frame_count', 8)
        animation.frame_rate = data.get('frame_rate', 12)
        animation.current_frame = data.get('current_frame', 0)
        animation.elapsed_time = data.get('elapsed_time', 0.0)
        animation.playing = data.get('playing', False)
        animation.paused = data.get('paused', False)
        animation.completed = data.get('completed', False)
        animation.loop_count = data.get('loop_count', 0)
        return animation


class InteractionAnimationManager:
    """
    Manages animations for furniture interactions.

    Features:
    - Play interaction animations
    - Manage animation states
    - Transition between animations
    - Synchronize with interactions
    """

    def __init__(self):
        """Initialize interaction animation manager."""
        # Animation library
        self.animations: Dict[str, InteractionAnimation] = {}

        # Current state
        self.current_animation: Optional[InteractionAnimation] = None
        self.current_state = InteractionAnimationState.RETURN
        self.transition_time = 0.0
        self.transition_duration = 0.3  # seconds

        # Interaction-specific animations
        self.interaction_animations = {
            'sleep': {
                'approach': 'walk',
                'prepare': 'sit_down',
                'interact_loop': 'sleep_loop',
                'finish': 'wake_up',
                'return': 'stand_up'
            },
            'eat': {
                'approach': 'walk',
                'prepare': 'sniff',
                'interact_loop': 'eat_loop',
                'finish': 'lick_lips',
                'return': 'walk'
            },
            'play': {
                'approach': 'run',
                'prepare': 'crouch',
                'interact_loop': 'play_loop',
                'finish': 'catch',
                'return': 'walk'
            },
            'scratch': {
                'approach': 'walk',
                'prepare': 'reach_up',
                'interact_loop': 'scratch_loop',
                'finish': 'stretch',
                'return': 'walk'
            },
            'climb': {
                'approach': 'walk',
                'prepare': 'crouch',
                'interact_loop': 'climb_loop',
                'finish': 'land',
                'return': 'walk'
            },
            'sit': {
                'approach': 'walk',
                'prepare': 'turn',
                'interact_loop': 'sit_idle',
                'finish': 'stand_up',
                'return': 'walk'
            }
        }

        # Create default animations
        self._create_default_animations()

        # Statistics
        self.total_animations_played = 0
        self.animation_counts: Dict[str, int] = {}

    def _create_default_animations(self):
        """Create default animation templates."""
        default_anims = [
            ('walk', 8, 12, AnimationType.LOOP),
            ('run', 6, 15, AnimationType.LOOP),
            ('sleep_loop', 4, 6, AnimationType.LOOP),
            ('eat_loop', 6, 10, AnimationType.LOOP),
            ('play_loop', 8, 12, AnimationType.LOOP),
            ('scratch_loop', 6, 10, AnimationType.LOOP),
            ('climb_loop', 8, 12, AnimationType.LOOP),
            ('sit_idle', 4, 8, AnimationType.LOOP),
            ('sit_down', 4, 10, AnimationType.SINGLE),
            ('stand_up', 4, 10, AnimationType.SINGLE),
            ('wake_up', 6, 10, AnimationType.SINGLE),
            ('sniff', 4, 10, AnimationType.SINGLE),
            ('lick_lips', 4, 10, AnimationType.SINGLE),
            ('crouch', 4, 10, AnimationType.SINGLE),
            ('catch', 6, 12, AnimationType.SINGLE),
            ('reach_up', 4, 10, AnimationType.SINGLE),
            ('stretch', 6, 10, AnimationType.SINGLE),
            ('turn', 4, 10, AnimationType.SINGLE),
            ('land', 4, 12, AnimationType.SINGLE)
        ]

        for anim_id, frames, rate, anim_type in default_anims:
            animation = InteractionAnimation(anim_id, anim_id.replace('_', ' ').title())
            animation.frame_count = frames
            animation.frame_rate = rate
            animation.animation_type = anim_type
            self.animations[anim_id] = animation

    def play_animation(self, animation_id: str) -> bool:
        """
        Play an animation.

        Args:
            animation_id: Animation to play

        Returns:
            True if started successfully
        """
        animation = self.animations.get(animation_id)
        if not animation:
            return False

        # Stop current animation
        if self.current_animation:
            self.current_animation.stop()

        # Start new animation
        animation.start()
        self.current_animation = animation

        # Track statistics
        self.total_animations_played += 1
        self.animation_counts[animation_id] = self.animation_counts.get(animation_id, 0) + 1

        return True

    def set_interaction_state(self, interaction_type: str, state: InteractionAnimationState):
        """
        Set animation for interaction state.

        Args:
            interaction_type: Type of interaction
            state: Animation state
        """
        self.current_state = state

        # Get animation for this interaction/state
        interaction_anims = self.interaction_animations.get(interaction_type)
        if not interaction_anims:
            return

        state_key = state.value
        animation_id = interaction_anims.get(state_key, 'walk')

        # Play animation
        self.play_animation(animation_id)

    def update(self, delta_time: float):
        """
        Update current animation.

        Args:
            delta_time: Time since last update (seconds)
        """
        if self.current_animation:
            self.current_animation.update(delta_time)

    def stop_current_animation(self):
        """Stop the current animation."""
        if self.current_animation:
            self.current_animation.stop()
            self.current_animation = None

    def pause_current_animation(self):
        """Pause the current animation."""
        if self.current_animation:
            self.current_animation.pause()

    def resume_current_animation(self):
        """Resume the current animation."""
        if self.current_animation:
            self.current_animation.resume()

    def is_animation_completed(self) -> bool:
        """Check if current animation is completed."""
        if not self.current_animation:
            return True
        return self.current_animation.completed

    def get_current_frame(self) -> int:
        """Get current animation frame."""
        if not self.current_animation:
            return 0
        return self.current_animation.current_frame

    def get_current_animation_name(self) -> str:
        """Get current animation name."""
        if not self.current_animation:
            return "none"
        return self.current_animation.name

    def add_animation(self, animation_id: str, name: str, frame_count: int = 8,
                     frame_rate: int = 12, animation_type: AnimationType = AnimationType.LOOP):
        """
        Add custom animation.

        Args:
            animation_id: Unique animation ID
            name: Animation name
            frame_count: Number of frames
            frame_rate: Frames per second
            animation_type: Type of animation
        """
        animation = InteractionAnimation(animation_id, name)
        animation.frame_count = frame_count
        animation.frame_rate = frame_rate
        animation.animation_type = animation_type
        self.animations[animation_id] = animation

    def get_statistics(self) -> Dict[str, Any]:
        """Get animation statistics."""
        return {
            'total_animations': len(self.animations),
            'total_played': self.total_animations_played,
            'current_animation': self.get_current_animation_name(),
            'current_state': self.current_state.value,
            'animation_counts': self.animation_counts
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'animations': {
                anim_id: anim.to_dict()
                for anim_id, anim in self.animations.items()
            },
            'current_animation_id': (
                self.current_animation.animation_id if self.current_animation else None
            ),
            'current_state': self.current_state.value,
            'transition_time': self.transition_time,
            'total_animations_played': self.total_animations_played,
            'animation_counts': self.animation_counts
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractionAnimationManager':
        """Deserialize from dictionary."""
        manager = cls()

        # Restore animations
        anims_data = data.get('animations', {})
        for anim_id, anim_data in anims_data.items():
            manager.animations[anim_id] = InteractionAnimation.from_dict(anim_data)

        # Restore current animation
        current_anim_id = data.get('current_animation_id')
        if current_anim_id and current_anim_id in manager.animations:
            manager.current_animation = manager.animations[current_anim_id]

        manager.current_state = InteractionAnimationState(data.get('current_state', 'return'))
        manager.transition_time = data.get('transition_time', 0.0)
        manager.total_animations_played = data.get('total_animations_played', 0)
        manager.animation_counts = data.get('animation_counts', {})

        return manager
