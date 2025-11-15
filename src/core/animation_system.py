"""
Phase 10: Animation System

Manages smooth sprite animations with frame transitions and interpolation.
"""
import time
from typing import Dict, Any, List, Optional, Tuple, Callable
from enum import Enum


class AnimationState(Enum):
    """Animation states."""
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    JUMPING = "jumping"
    EATING = "eating"
    DRINKING = "drinking"
    SLEEPING = "sleeping"
    PLAYING = "playing"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SCARED = "scared"
    LOVING = "loving"
    GROOMING = "grooming"
    SCRATCHING = "scratching"
    SITTING = "sitting"
    LYING_DOWN = "lying_down"
    STRETCHING = "stretching"


class AnimationFrame:
    """Represents a single animation frame."""

    def __init__(self, sprite_index: int, duration: float = 0.1,
                 offset: Tuple[int, int] = (0, 0), scale: float = 1.0):
        """
        Initialize animation frame.

        Args:
            sprite_index: Index of sprite to display
            duration: How long this frame displays (seconds)
            offset: Position offset (x, y)
            scale: Scale multiplier
        """
        self.sprite_index = sprite_index
        self.duration = duration
        self.offset = offset
        self.scale = scale


class Animation:
    """Represents a complete animation sequence."""

    def __init__(self, name: str, frames: List[AnimationFrame],
                 loop: bool = True, priority: int = 0):
        """
        Initialize animation.

        Args:
            name: Animation name
            frames: List of animation frames
            loop: Whether animation loops
            priority: Animation priority (higher = more important)
        """
        self.name = name
        self.frames = frames
        self.loop = loop
        self.priority = priority
        self.current_frame = 0
        self.frame_time = 0.0
        self.total_duration = sum(f.duration for f in frames)
        self.completed = False

    def reset(self):
        """Reset animation to start."""
        self.current_frame = 0
        self.frame_time = 0.0
        self.completed = False

    def update(self, dt: float) -> bool:
        """
        Update animation.

        Args:
            dt: Time elapsed in seconds

        Returns:
            True if frame changed
        """
        if self.completed and not self.loop:
            return False

        self.frame_time += dt
        frame_changed = False

        # Check if we need to advance frames
        while self.frame_time >= self.frames[self.current_frame].duration:
            self.frame_time -= self.frames[self.current_frame].duration
            self.current_frame += 1
            frame_changed = True

            # Handle loop or completion
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.completed = True
                    break

        return frame_changed

    def get_current_frame(self) -> AnimationFrame:
        """Get current animation frame."""
        return self.frames[self.current_frame]


class AnimationSystem:
    """
    Manages sprite animations with smooth transitions.

    Features:
    - Multiple animation states (idle, walk, run, etc.)
    - Frame-based animation with timing
    - Smooth state transitions with blending
    - Animation priority system
    - Callback support for animation events
    """

    def __init__(self):
        """Initialize animation system."""
        # Animation library
        self.animations: Dict[str, Animation] = {}

        # Current state
        self.current_animation: Optional[Animation] = None
        self.previous_animation: Optional[Animation] = None
        self.transition_time = 0.0
        self.transition_duration = 0.2  # 200ms blend

        # Animation state
        self.current_state = AnimationState.IDLE
        self.facing_right = True

        # Animation modifiers
        self.animation_speed = 1.0  # Speed multiplier
        self.paused = False

        # Callbacks
        self.on_animation_complete: Optional[Callable] = None
        self.on_frame_change: Optional[Callable] = None

        # Statistics
        self.total_animations_played = 0
        self.state_changes = 0

        # Create default animations
        self._create_default_animations()

    def _create_default_animations(self):
        """Create default animation sequences."""
        # Idle - gentle bobbing
        self.add_animation(Animation(
            name="idle",
            frames=[
                AnimationFrame(0, 0.5, (0, 0)),
                AnimationFrame(0, 0.5, (0, -2)),
                AnimationFrame(0, 0.5, (0, 0)),
                AnimationFrame(0, 0.5, (0, 2)),
            ],
            loop=True,
            priority=0
        ))

        # Walking - 4 frame walk cycle
        self.add_animation(Animation(
            name="walking",
            frames=[
                AnimationFrame(1, 0.15, (0, 0)),
                AnimationFrame(2, 0.15, (0, -1)),
                AnimationFrame(3, 0.15, (0, 0)),
                AnimationFrame(2, 0.15, (0, 1)),
            ],
            loop=True,
            priority=1
        ))

        # Running - faster walk
        self.add_animation(Animation(
            name="running",
            frames=[
                AnimationFrame(4, 0.08, (0, 0)),
                AnimationFrame(5, 0.08, (0, -2)),
                AnimationFrame(6, 0.08, (0, 0)),
                AnimationFrame(5, 0.08, (0, 2)),
            ],
            loop=True,
            priority=2
        ))

        # Jumping - arc motion
        self.add_animation(Animation(
            name="jumping",
            frames=[
                AnimationFrame(7, 0.1, (0, -5)),
                AnimationFrame(8, 0.1, (0, -10)),
                AnimationFrame(9, 0.1, (0, -15)),
                AnimationFrame(9, 0.1, (0, -15)),
                AnimationFrame(8, 0.1, (0, -10)),
                AnimationFrame(7, 0.1, (0, -5)),
            ],
            loop=False,
            priority=3
        ))

        # Eating - chomping
        self.add_animation(Animation(
            name="eating",
            frames=[
                AnimationFrame(10, 0.2, (0, 0)),
                AnimationFrame(11, 0.2, (0, 2)),
                AnimationFrame(10, 0.2, (0, 0)),
                AnimationFrame(11, 0.2, (0, 2)),
            ],
            loop=True,
            priority=2
        ))

        # Sleeping - gentle breathing
        self.add_animation(Animation(
            name="sleeping",
            frames=[
                AnimationFrame(12, 0.8, (0, 0), 1.0),
                AnimationFrame(12, 0.8, (0, 1), 1.02),
                AnimationFrame(12, 0.8, (0, 0), 1.0),
                AnimationFrame(12, 0.8, (0, -1), 0.98),
            ],
            loop=True,
            priority=1
        ))

        # Happy - bouncing
        self.add_animation(Animation(
            name="happy",
            frames=[
                AnimationFrame(13, 0.15, (0, -8)),
                AnimationFrame(14, 0.15, (0, -4)),
                AnimationFrame(13, 0.15, (0, 0)),
                AnimationFrame(14, 0.15, (0, -4)),
            ],
            loop=True,
            priority=2
        ))

        # Sad - drooping
        self.add_animation(Animation(
            name="sad",
            frames=[
                AnimationFrame(15, 1.0, (0, 2), 0.95),
                AnimationFrame(15, 1.0, (0, 3), 0.95),
            ],
            loop=True,
            priority=1
        ))

    def add_animation(self, animation: Animation):
        """
        Add an animation to the library.

        Args:
            animation: Animation to add
        """
        self.animations[animation.name] = animation

    def play_animation(self, animation_name: str, force: bool = False) -> bool:
        """
        Play an animation.

        Args:
            animation_name: Name of animation to play
            force: Force play even if lower priority

        Returns:
            True if animation started
        """
        if animation_name not in self.animations:
            return False

        new_animation = self.animations[animation_name]

        # Check priority unless forced
        if not force and self.current_animation:
            if new_animation.priority < self.current_animation.priority:
                return False

        # Start transition
        self.previous_animation = self.current_animation
        self.current_animation = new_animation
        self.current_animation.reset()
        self.transition_time = 0.0

        self.total_animations_played += 1

        return True

    def set_state(self, state: AnimationState):
        """
        Set animation state.

        Args:
            state: New animation state
        """
        if state == self.current_state:
            return

        self.current_state = state
        self.state_changes += 1

        # Map state to animation
        animation_map = {
            AnimationState.IDLE: "idle",
            AnimationState.WALKING: "walking",
            AnimationState.RUNNING: "running",
            AnimationState.JUMPING: "jumping",
            AnimationState.EATING: "eating",
            AnimationState.SLEEPING: "sleeping",
            AnimationState.HAPPY: "happy",
            AnimationState.SAD: "sad",
        }

        animation_name = animation_map.get(state, "idle")
        self.play_animation(animation_name)

    def update(self, dt: float):
        """
        Update animation system.

        Args:
            dt: Time elapsed in seconds
        """
        if self.paused or not self.current_animation:
            return

        # Apply speed modifier
        effective_dt = dt * self.animation_speed

        # Update transition
        if self.transition_time < self.transition_duration:
            self.transition_time += dt

        # Update current animation
        frame_changed = self.current_animation.update(effective_dt)

        if frame_changed and self.on_frame_change:
            self.on_frame_change(self.current_animation.get_current_frame())

        # Check for completion
        if self.current_animation.completed and self.on_animation_complete:
            self.on_animation_complete(self.current_animation.name)

    def get_current_frame(self) -> Optional[AnimationFrame]:
        """Get current animation frame."""
        if not self.current_animation:
            return None
        return self.current_animation.get_current_frame()

    def get_transition_blend(self) -> float:
        """
        Get current transition blend factor.

        Returns:
            0.0 = fully previous, 1.0 = fully current
        """
        if self.transition_time >= self.transition_duration:
            return 1.0
        return self.transition_time / self.transition_duration

    def set_facing(self, facing_right: bool):
        """
        Set facing direction.

        Args:
            facing_right: True if facing right
        """
        self.facing_right = facing_right

    def set_speed(self, speed: float):
        """
        Set animation speed multiplier.

        Args:
            speed: Speed multiplier (1.0 = normal)
        """
        self.animation_speed = max(0.1, min(5.0, speed))

    def pause(self):
        """Pause animation."""
        self.paused = True

    def resume(self):
        """Resume animation."""
        self.paused = False

    def is_transitioning(self) -> bool:
        """Check if currently transitioning between animations."""
        return self.transition_time < self.transition_duration

    def get_status(self) -> Dict[str, Any]:
        """Get animation system status."""
        current_frame = self.get_current_frame()

        return {
            'current_state': self.current_state.value,
            'current_animation': self.current_animation.name if self.current_animation else None,
            'current_frame_index': self.current_animation.current_frame if self.current_animation else 0,
            'animation_progress': (
                self.current_animation.frame_time / self.current_animation.frames[self.current_animation.current_frame].duration
                if self.current_animation else 0.0
            ),
            'is_transitioning': self.is_transitioning(),
            'transition_blend': self.get_transition_blend(),
            'facing_right': self.facing_right,
            'animation_speed': self.animation_speed,
            'paused': self.paused,
            'total_animations_played': self.total_animations_played,
            'state_changes': self.state_changes,
            'available_animations': list(self.animations.keys())
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'current_state': self.current_state.value,
            'current_animation': self.current_animation.name if self.current_animation else None,
            'facing_right': self.facing_right,
            'animation_speed': self.animation_speed,
            'paused': self.paused,
            'total_animations_played': self.total_animations_played,
            'state_changes': self.state_changes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnimationSystem':
        """Deserialize from dictionary."""
        system = cls()
        system.current_state = AnimationState(data.get('current_state', 'idle'))
        system.facing_right = data.get('facing_right', True)
        system.animation_speed = data.get('animation_speed', 1.0)
        system.paused = data.get('paused', False)
        system.total_animations_played = data.get('total_animations_played', 0)
        system.state_changes = data.get('state_changes', 0)

        # Restore current animation
        current_anim = data.get('current_animation')
        if current_anim and current_anim in system.animations:
            system.play_animation(current_anim, force=True)

        return system
