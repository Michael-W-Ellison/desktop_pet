"""
Particle Effects System for Desktop Pet

Renders visual particle effects for elements (fire, water, etc.) and variants (shiny, mystic, etc.).
Uses PIL to generate particle effects that can be composited onto the creature sprite.
"""
from typing import List, Tuple, Dict, Any
from PIL import Image, ImageDraw
import random
import math
import time


class Particle:
    """Represents a single particle in an effect."""

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color: Tuple[int, int, int, int], size: int, lifetime: float):
        """
        Initialize a particle.

        Args:
            x, y: Position
            vx, vy: Velocity
            color: RGBA color tuple
            size: Particle size in pixels
            lifetime: How long particle lives in seconds
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.age = 0.0

    def update(self, dt: float):
        """Update particle position and age."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt

    def is_alive(self) -> bool:
        """Check if particle is still alive."""
        return self.age < self.lifetime

    def get_alpha(self) -> int:
        """Get current alpha based on age (fades out)."""
        life_ratio = 1.0 - (self.age / self.lifetime)
        return int(self.color[3] * life_ratio)


class ParticleEffect:
    """Base class for particle effects."""

    def __init__(self, duration: float = 2.0):
        """
        Initialize particle effect.

        Args:
            duration: How long the effect lasts in seconds
        """
        self.particles: List[Particle] = []
        self.duration = duration
        self.elapsed = 0.0
        self.active = True

    def update(self, dt: float):
        """Update all particles."""
        self.elapsed += dt

        # Update existing particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)

        # Generate new particles if still active
        if self.elapsed < self.duration:
            self.generate_particles(dt)
        elif len(self.particles) == 0:
            self.active = False

    def generate_particles(self, dt: float):
        """Override in subclasses to generate particles."""
        pass

    def render(self, size: Tuple[int, int]) -> Image.Image:
        """
        Render particles to an image.

        Args:
            size: Image size (width, height)

        Returns:
            RGBA image with particles
        """
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        for particle in self.particles:
            x = int(particle.x)
            y = int(particle.y)
            alpha = particle.get_alpha()

            if alpha > 0:
                color = particle.color[:3] + (alpha,)
                size = particle.size

                # Draw particle as a circle
                draw.ellipse(
                    [x - size, y - size, x + size, y + size],
                    fill=color
                )

        return img


class FlameEffect(ParticleEffect):
    """Fire/flame particle effect."""

    def __init__(self, center_x: int, center_y: int):
        super().__init__(duration=999999)  # Continuous effect
        self.center_x = center_x
        self.center_y = center_y
        self.spawn_rate = 15  # Particles per second

    def generate_particles(self, dt: float):
        """Generate fire particles rising upward."""
        num_particles = int(self.spawn_rate * dt) + (1 if random.random() < (self.spawn_rate * dt) % 1 else 0)

        for _ in range(num_particles):
            # Spawn at bottom, rise up
            x = self.center_x + random.randint(-15, 15)
            y = self.center_y + random.randint(-10, 10)

            # Upward velocity with some horizontal spread
            vx = random.uniform(-10, 10)
            vy = random.uniform(-50, -80)  # Rise

            # Fire colors: red to yellow
            if random.random() < 0.7:
                color = (255, random.randint(50, 150), 0, 200)  # Orange
            else:
                color = (255, 255, 0, 180)  # Yellow

            size = random.randint(2, 5)
            lifetime = random.uniform(0.3, 0.7)

            self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))


class WaterDropEffect(ParticleEffect):
    """Water droplets effect."""

    def __init__(self, center_x: int, center_y: int):
        super().__init__(duration=999999)
        self.center_x = center_x
        self.center_y = center_y
        self.spawn_rate = 12

    def generate_particles(self, dt: float):
        """Generate water droplets."""
        num_particles = int(self.spawn_rate * dt) + (1 if random.random() < (self.spawn_rate * dt) % 1 else 0)

        for _ in range(num_particles):
            # Spawn around creature
            angle = random.uniform(0, 2 * math.pi)
            radius = random.randint(20, 40)
            x = self.center_x + math.cos(angle) * radius
            y = self.center_y + math.sin(angle) * radius

            # Fall downward
            vx = random.uniform(-5, 5)
            vy = random.uniform(20, 40)  # Gravity

            # Blue water colors
            color = (random.randint(0, 100), random.randint(150, 255), 255, 180)

            size = random.randint(2, 4)
            lifetime = random.uniform(0.5, 1.0)

            self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))


class SparkleEffect(ParticleEffect):
    """Sparkles for shiny variants."""

    def __init__(self, center_x: int, center_y: int):
        super().__init__(duration=999999)
        self.center_x = center_x
        self.center_y = center_y
        self.spawn_rate = 8

    def generate_particles(self, dt: float):
        """Generate sparkle particles."""
        num_particles = int(self.spawn_rate * dt) + (1 if random.random() < (self.spawn_rate * dt) % 1 else 0)

        for _ in range(num_particles):
            # Spawn around creature
            x = self.center_x + random.randint(-50, 50)
            y = self.center_y + random.randint(-50, 50)

            # Float upward slowly
            vx = random.uniform(-10, 10)
            vy = random.uniform(-20, -5)

            # Bright white/yellow sparkles
            if random.random() < 0.5:
                color = (255, 255, 255, 255)  # White
            else:
                color = (255, 255, 200, 255)  # Pale yellow

            size = random.randint(1, 3)
            lifetime = random.uniform(0.4, 0.8)

            self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))


class MysticalAuraEffect(ParticleEffect):
    """Mystical purple/blue aura for mystic variants."""

    def __init__(self, center_x: int, center_y: int):
        super().__init__(duration=999999)
        self.center_x = center_x
        self.center_y = center_y
        self.spawn_rate = 10
        self.time = 0

    def generate_particles(self, dt: float):
        """Generate mystical aura particles that orbit."""
        self.time += dt
        num_particles = int(self.spawn_rate * dt) + (1 if random.random() < (self.spawn_rate * dt) % 1 else 0)

        for _ in range(num_particles):
            # Orbit around creature
            angle = self.time + random.uniform(0, 2 * math.pi)
            radius = 30 + 10 * math.sin(self.time * 2)

            x = self.center_x + math.cos(angle) * radius
            y = self.center_y + math.sin(angle) * radius

            # Orbital velocity
            vx = -math.sin(angle) * 20
            vy = math.cos(angle) * 20

            # Purple/magenta colors
            color = (random.randint(150, 255), random.randint(0, 100), random.randint(200, 255), 150)

            size = random.randint(2, 4)
            lifetime = random.uniform(0.6, 1.2)

            self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))


class ShadowAuraEffect(ParticleEffect):
    """Dark shadow aura for shadow variants."""

    def __init__(self, center_x: int, center_y: int):
        super().__init__(duration=999999)
        self.center_x = center_x
        self.center_y = center_y
        self.spawn_rate = 8

    def generate_particles(self, dt: float):
        """Generate shadow particles."""
        num_particles = int(self.spawn_rate * dt) + (1 if random.random() < (self.spawn_rate * dt) % 1 else 0)

        for _ in range(num_particles):
            # Spawn around creature
            x = self.center_x + random.randint(-40, 40)
            y = self.center_y + random.randint(-40, 40)

            # Drift slowly
            vx = random.uniform(-15, 15)
            vy = random.uniform(-5, 5)

            # Dark purple/black colors
            color = (random.randint(30, 80), 0, random.randint(50, 100), 120)

            size = random.randint(3, 6)
            lifetime = random.uniform(0.8, 1.5)

            self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))


class CrystalGleamEffect(ParticleEffect):
    """Crystalline gleaming effect for crystal variants."""

    def __init__(self, center_x: int, center_y: int):
        super().__init__(duration=999999)
        self.center_x = center_x
        self.center_y = center_y
        self.spawn_rate = 6

    def generate_particles(self, dt: float):
        """Generate crystal gleam particles."""
        num_particles = int(self.spawn_rate * dt) + (1 if random.random() < (self.spawn_rate * dt) % 1 else 0)

        for _ in range(num_particles):
            # Spawn near creature
            x = self.center_x + random.randint(-45, 45)
            y = self.center_y + random.randint(-45, 45)

            # Gentle movement
            vx = random.uniform(-8, 8)
            vy = random.uniform(-8, 8)

            # Cyan/white crystalline colors
            color = (random.randint(150, 255), random.randint(200, 255), 255, 200)

            size = random.randint(2, 5)
            lifetime = random.uniform(0.5, 1.0)

            self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))


class LightningEffect(ParticleEffect):
    """Electric/lightning particles for electric element."""

    def __init__(self, center_x: int, center_y: int):
        super().__init__(duration=999999)
        self.center_x = center_x
        self.center_y = center_y
        self.spawn_rate = 10

    def generate_particles(self, dt: float):
        """Generate electric sparks."""
        num_particles = int(self.spawn_rate * dt) + (1 if random.random() < (self.spawn_rate * dt) % 1 else 0)

        for _ in range(num_particles):
            # Spawn around creature
            x = self.center_x + random.randint(-30, 30)
            y = self.center_y + random.randint(-30, 30)

            # Erratic movement
            vx = random.uniform(-60, 60)
            vy = random.uniform(-60, 60)

            # Bright yellow electric colors
            color = (255, 255, random.randint(0, 100), 220)

            size = random.randint(1, 3)
            lifetime = random.uniform(0.1, 0.3)  # Very short-lived

            self.particles.append(Particle(x, y, vx, vy, color, size, lifetime))


class ParticleEffectManager:
    """Manages multiple particle effects."""

    def __init__(self):
        """Initialize the particle effect manager."""
        self.effects: Dict[str, ParticleEffect] = {}

    def add_effect(self, effect_name: str, center_x: int, center_y: int):
        """
        Add a particle effect.

        Args:
            effect_name: Type of effect
            center_x, center_y: Center position
        """
        effect_classes = {
            'flames': FlameEffect,
            'water_drops': WaterDropEffect,
            'sparkles': SparkleEffect,
            'mystical_aura': MysticalAuraEffect,
            'shadow_aura': ShadowAuraEffect,
            'crystal_gleam': CrystalGleamEffect,
            'lightning': LightningEffect,
            'snowflakes': WaterDropEffect,  # Similar to water but could be customized
            'leaves': WaterDropEffect,  # Could be customized
            'rocks': WaterDropEffect,  # Could be customized
            'wind_swirls': SparkleEffect,  # Could be customized
            'energy_rings': MysticalAuraEffect,  # Similar to mystical
            'stars': SparkleEffect  # Similar to sparkles
        }

        effect_class = effect_classes.get(effect_name, SparkleEffect)
        self.effects[effect_name] = effect_class(center_x, center_y)

    def remove_effect(self, effect_name: str):
        """Remove an effect."""
        if effect_name in self.effects:
            del self.effects[effect_name]

    def update(self, dt: float):
        """Update all effects."""
        for effect_name in list(self.effects.keys()):
            effect = self.effects[effect_name]
            effect.update(dt)

            # Remove inactive effects
            if not effect.active:
                del self.effects[effect_name]

    def render(self, size: Tuple[int, int]) -> Image.Image:
        """
        Render all effects to a single image.

        Args:
            size: Image size

        Returns:
            Composite RGBA image with all effects
        """
        # Create base transparent image
        result = Image.new('RGBA', size, (0, 0, 0, 0))

        # Composite all effect images
        for effect in self.effects.values():
            effect_img = effect.render(size)
            result = Image.alpha_composite(result, effect_img)

        return result

    def has_effects(self) -> bool:
        """Check if there are any active effects."""
        return len(self.effects) > 0
