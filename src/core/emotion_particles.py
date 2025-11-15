"""
Phase 10: Emotion Particle System

Manages emotion-based visual particles (hearts, stars, sweat, etc.).
"""
import time
import random
import math
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class EmotionType(Enum):
    """Emotion particle types."""
    HEARTS = "hearts"              # Love, happiness
    STARS = "stars"                # Excitement, wonder
    SPARKLES = "sparkles"          # Joy, magic
    SWEAT = "sweat"                # Nervousness, effort
    TEARS = "tears"                # Sadness, crying
    ANGER_MARKS = "anger_marks"    # Anger, frustration
    QUESTION_MARKS = "question"    # Confusion, curiosity
    EXCLAMATION = "exclamation"    # Surprise, alert
    ZZZ = "zzz"                    # Sleeping, tired
    MUSICAL_NOTES = "music"        # Happy, playful
    BROKEN_HEART = "broken_heart"  # Heartbreak, rejection
    STINK_LINES = "stink"          # Dirty, smelly
    DIZZY_STARS = "dizzy"          # Dizzy, confused
    LIGHTNING = "lightning"        # Energy, power
    FOOD_ICONS = "food"            # Hungry, eating


class EmotionParticle:
    """Represents a single emotion particle."""

    def __init__(self, x: float, y: float, particle_type: EmotionType,
                 velocity: Tuple[float, float] = (0, 0),
                 lifetime: float = 2.0, size: float = 1.0):
        """
        Initialize emotion particle.

        Args:
            x, y: Starting position
            particle_type: Type of emotion particle
            velocity: (vx, vy) velocity
            lifetime: How long particle exists (seconds)
            size: Size multiplier
        """
        self.x = x
        self.y = y
        self.particle_type = particle_type
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.age = 0.0
        self.size = size
        self.rotation = 0.0
        self.rotation_speed = random.uniform(-180, 180)  # degrees/sec
        self.alpha = 1.0

    def update(self, dt: float):
        """Update particle position and state."""
        self.age += dt

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Apply gravity for some types
        if self.particle_type in [EmotionType.TEARS, EmotionType.SWEAT, EmotionType.BROKEN_HEART]:
            self.vy += 100 * dt  # Gravity

        # Update rotation
        self.rotation += self.rotation_speed * dt

        # Fade out near end of life
        life_remaining = 1.0 - (self.age / self.lifetime)
        if life_remaining < 0.3:
            self.alpha = life_remaining / 0.3
        else:
            self.alpha = 1.0

    def is_alive(self) -> bool:
        """Check if particle is still alive."""
        return self.age < self.lifetime

    def get_render_data(self) -> Dict[str, Any]:
        """Get rendering data for this particle."""
        return {
            'x': self.x,
            'y': self.y,
            'type': self.particle_type.value,
            'size': self.size,
            'rotation': self.rotation,
            'alpha': self.alpha,
            'age': self.age,
            'lifetime': self.lifetime
        }


class EmotionParticleEmitter:
    """Emits emotion particles based on pet state."""

    def __init__(self):
        """Initialize emotion particle emitter."""
        self.particles: List[EmotionParticle] = []
        self.active_emotions: Dict[EmotionType, float] = {}  # emotion: intensity
        self.emission_cooldowns: Dict[EmotionType, float] = {}  # emission timers

        # Emission rates (particles per second at full intensity)
        self.emission_rates = {
            EmotionType.HEARTS: 3.0,
            EmotionType.STARS: 5.0,
            EmotionType.SPARKLES: 10.0,
            EmotionType.SWEAT: 2.0,
            EmotionType.TEARS: 4.0,
            EmotionType.ANGER_MARKS: 3.0,
            EmotionType.QUESTION_MARKS: 1.5,
            EmotionType.EXCLAMATION: 2.0,
            EmotionType.ZZZ: 0.5,
            EmotionType.MUSICAL_NOTES: 3.0,
            EmotionType.BROKEN_HEART: 1.0,
            EmotionType.STINK_LINES: 2.0,
            EmotionType.DIZZY_STARS: 4.0,
            EmotionType.LIGHTNING: 3.0,
            EmotionType.FOOD_ICONS: 2.0
        }

        # Statistics
        self.total_particles_emitted = 0
        self.particles_by_type: Dict[str, int] = {}

    def trigger_emotion(self, emotion_type: EmotionType, intensity: float = 1.0,
                       duration: float = 2.0):
        """
        Trigger an emotion particle effect.

        Args:
            emotion_type: Type of emotion to display
            intensity: Intensity of emotion (0-1)
            duration: How long to emit particles (seconds)
        """
        self.active_emotions[emotion_type] = {
            'intensity': max(0.0, min(1.0, intensity)),
            'duration': duration,
            'elapsed': 0.0
        }

    def emit_particle(self, emotion_type: EmotionType, position: Tuple[float, float],
                     intensity: float = 1.0):
        """
        Emit a single emotion particle.

        Args:
            emotion_type: Type of particle
            position: (x, y) spawn position
            intensity: Intensity affects velocity and size
        """
        x, y = position

        # Determine particle behavior based on type
        if emotion_type == EmotionType.HEARTS:
            # Float upward with gentle drift
            vx = random.uniform(-20, 20)
            vy = random.uniform(-60, -40) * intensity
            lifetime = random.uniform(1.5, 2.5)
            size = random.uniform(0.8, 1.2) * intensity

        elif emotion_type == EmotionType.STARS:
            # Burst outward
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 100) * intensity
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(1.0, 2.0)
            size = random.uniform(0.7, 1.3) * intensity

        elif emotion_type == EmotionType.SPARKLES:
            # Quick, small, upward
            vx = random.uniform(-30, 30)
            vy = random.uniform(-80, -40)
            lifetime = random.uniform(0.5, 1.0)
            size = random.uniform(0.4, 0.8) * intensity

        elif emotion_type == EmotionType.SWEAT:
            # Drop down from head
            vx = random.uniform(-10, 10)
            vy = 0  # Starts stationary, gravity pulls down
            lifetime = random.uniform(0.8, 1.5)
            size = random.uniform(0.6, 1.0)

        elif emotion_type == EmotionType.TEARS:
            # Fall from eyes
            vx = random.uniform(-5, 5)
            vy = 0
            lifetime = random.uniform(1.0, 2.0)
            size = random.uniform(0.5, 0.8)

        elif emotion_type == EmotionType.ANGER_MARKS:
            # Pop up above head
            vx = random.uniform(-15, 15)
            vy = random.uniform(-40, -20)
            lifetime = random.uniform(1.0, 1.5)
            size = random.uniform(0.8, 1.2)

        elif emotion_type == EmotionType.QUESTION_MARKS:
            # Float slowly upward
            vx = random.uniform(-10, 10)
            vy = -30
            lifetime = random.uniform(2.0, 3.0)
            size = 1.0

        elif emotion_type == EmotionType.EXCLAMATION:
            # Quick pop
            vx = random.uniform(-20, 20)
            vy = random.uniform(-60, -30)
            lifetime = random.uniform(0.8, 1.2)
            size = 1.2

        elif emotion_type == EmotionType.ZZZ:
            # Slow diagonal drift
            vx = random.uniform(10, 30)
            vy = random.uniform(-20, -10)
            lifetime = random.uniform(2.0, 3.0)
            size = random.uniform(0.6, 1.0)

        elif emotion_type == EmotionType.MUSICAL_NOTES:
            # Bounce upward
            vx = random.uniform(-25, 25)
            vy = random.uniform(-70, -50)
            lifetime = random.uniform(1.5, 2.5)
            size = random.uniform(0.7, 1.0)

        elif emotion_type == EmotionType.BROKEN_HEART:
            # Fall with pieces
            vx = random.uniform(-30, 30)
            vy = random.uniform(-20, 0)
            lifetime = random.uniform(1.5, 2.5)
            size = 1.2

        elif emotion_type == EmotionType.STINK_LINES:
            # Waft upward in curves
            vx = random.uniform(-10, 10)
            vy = random.uniform(-40, -25)
            lifetime = random.uniform(2.0, 3.0)
            size = random.uniform(0.6, 1.0)

        elif emotion_type == EmotionType.DIZZY_STARS:
            # Circle around head
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            vx = math.cos(angle) * 20
            vy = math.sin(angle) * 20
            lifetime = random.uniform(2.0, 3.0)
            size = 0.8

        elif emotion_type == EmotionType.LIGHTNING:
            # Quick flash
            vx = 0
            vy = 0
            lifetime = random.uniform(0.3, 0.6)
            size = random.uniform(1.2, 1.8)

        elif emotion_type == EmotionType.FOOD_ICONS:
            # Float toward mouth
            vx = random.uniform(-10, 10)
            vy = random.uniform(10, 30)
            lifetime = random.uniform(1.0, 1.5)
            size = random.uniform(0.7, 1.0)

        else:
            # Default behavior
            vx = random.uniform(-20, 20)
            vy = random.uniform(-50, -30)
            lifetime = 2.0
            size = 1.0

        # Create and add particle
        particle = EmotionParticle(
            x=x + random.uniform(-10, 10),  # Slight spawn offset
            y=y + random.uniform(-10, 10),
            particle_type=emotion_type,
            velocity=(vx, vy),
            lifetime=lifetime,
            size=size
        )

        self.particles.append(particle)
        self.total_particles_emitted += 1

        # Track by type
        type_name = emotion_type.value
        if type_name not in self.particles_by_type:
            self.particles_by_type[type_name] = 0
        self.particles_by_type[type_name] += 1

    def update(self, dt: float, pet_position: Tuple[float, float]):
        """
        Update all particles and emit new ones.

        Args:
            dt: Time elapsed (seconds)
            pet_position: (x, y) position of pet center
        """
        # Update existing particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)

        # Update active emotions and emit particles
        for emotion_type, emotion_data in list(self.active_emotions.items()):
            emotion_data['elapsed'] += dt

            # Check if emotion expired
            if emotion_data['elapsed'] >= emotion_data['duration']:
                del self.active_emotions[emotion_type]
                continue

            # Update cooldown
            if emotion_type not in self.emission_cooldowns:
                self.emission_cooldowns[emotion_type] = 0.0

            self.emission_cooldowns[emotion_type] += dt

            # Emit particles based on rate and intensity
            emission_rate = self.emission_rates.get(emotion_type, 1.0)
            intensity = emotion_data['intensity']
            particles_per_second = emission_rate * intensity

            interval = 1.0 / particles_per_second if particles_per_second > 0 else float('inf')

            # Emit particles if cooldown expired
            while self.emission_cooldowns[emotion_type] >= interval:
                self.emission_cooldowns[emotion_type] -= interval
                self.emit_particle(emotion_type, pet_position, intensity)

    def clear_particles(self, emotion_type: Optional[EmotionType] = None):
        """
        Clear particles.

        Args:
            emotion_type: If specified, only clear this type
        """
        if emotion_type:
            self.particles = [p for p in self.particles if p.particle_type != emotion_type]
        else:
            self.particles.clear()

    def get_particles(self, emotion_type: Optional[EmotionType] = None) -> List[EmotionParticle]:
        """
        Get active particles.

        Args:
            emotion_type: If specified, only return this type

        Returns:
            List of particles
        """
        if emotion_type:
            return [p for p in self.particles if p.particle_type == emotion_type]
        return self.particles.copy()

    def get_particle_count(self, emotion_type: Optional[EmotionType] = None) -> int:
        """
        Get count of active particles.

        Args:
            emotion_type: If specified, count only this type

        Returns:
            Particle count
        """
        if emotion_type:
            return len([p for p in self.particles if p.particle_type == emotion_type])
        return len(self.particles)

    def get_status(self) -> Dict[str, Any]:
        """Get emotion particle system status."""
        return {
            'active_particles': len(self.particles),
            'active_emotions': len(self.active_emotions),
            'emotion_types': [e.value for e in self.active_emotions.keys()],
            'total_emitted': self.total_particles_emitted,
            'particles_by_type': self.particles_by_type.copy(),
            'particles_breakdown': {
                ptype.value: self.get_particle_count(ptype)
                for ptype in EmotionType
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'total_particles_emitted': self.total_particles_emitted,
            'particles_by_type': self.particles_by_type.copy(),
            'active_emotions': {
                emotion.value: data for emotion, data in self.active_emotions.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionParticleEmitter':
        """Deserialize from dictionary."""
        emitter = cls()
        emitter.total_particles_emitted = data.get('total_particles_emitted', 0)
        emitter.particles_by_type = data.get('particles_by_type', {})

        # Restore active emotions
        active_emotions = data.get('active_emotions', {})
        for emotion_str, emotion_data in active_emotions.items():
            emotion_type = EmotionType(emotion_str)
            emitter.active_emotions[emotion_type] = emotion_data

        return emitter
