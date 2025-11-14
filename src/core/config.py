"""
Configuration and constants for the Desktop Pet application.
"""
import os
from enum import Enum

# Application settings
APP_NAME = "Desktop Pet"
VERSION = "1.0.0"
DATA_FILE = "pet_data.json"

# Window settings
PET_SIZE = (128, 128)
TOY_SIZE = (64, 64)
FPS = 30
ANIMATION_SPEED = 150  # milliseconds per frame

# Physics settings
GRAVITY = 0.5
BOUNCE_DAMPING = 0.8
FRICTION = 0.95
BALL_SPEED = 15

# Creature settings
HUNGER_DECAY_RATE = 0.1  # Hunger increases by this amount per minute
STARVATION_THRESHOLD = 100  # Creature dies when hunger reaches this
MAX_HUNGER = 100
FEED_AMOUNT = 30  # How much feeding reduces hunger

# Learning settings
LEARNING_RATE = 0.01
NEURAL_NETWORK_LAYERS = [10, 8, 6]  # Hidden layers

# Personality types
class PersonalityType(Enum):
    PLAYFUL = "playful"
    SHY = "shy"
    CURIOUS = "curious"
    LAZY = "lazy"
    ENERGETIC = "energetic"
    MISCHIEVOUS = "mischievous"
    AFFECTIONATE = "affectionate"
    INDEPENDENT = "independent"

# Creature types (Pokemon-style animals)
CREATURE_TYPES = [
    "dragon",
    "cat",
    "dog",
    "bunny",
    "bird",
    "fox",
    "hamster",
    "owl",
    "penguin",
    "turtle"
]

# Behavior states
class BehaviorState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    PLAYING = "playing"
    EATING = "eating"
    SLEEPING = "sleeping"
    CHASING = "chasing"
    HIDING = "hiding"
    SEEKING = "seeking"

# Color palettes for creature variation
COLOR_PALETTES = [
    ["#FF6B6B", "#FFE66D", "#4ECDC4"],  # Red-Yellow-Cyan
    ["#A8E6CF", "#FFD3B6", "#FFAAA5"],  # Mint-Peach-Pink
    ["#95E1D3", "#F38181", "#AA96DA"],  # Teal-Coral-Purple
    ["#FECA57", "#FF6B6B", "#48DBFB"],  # Yellow-Red-Blue
    ["#DDA15E", "#BC6C25", "#FEFAE0"],  # Brown-Tan-Cream
    ["#B8B8FF", "#FFB3BA", "#BAFFC9"],  # Lavender-Pink-Mint
]

# Personality trait modifiers (how personality affects behavior)
PERSONALITY_TRAITS = {
    PersonalityType.PLAYFUL: {
        "play_frequency": 1.5,
        "energy_consumption": 1.2,
        "interaction_desire": 1.3
    },
    PersonalityType.SHY: {
        "play_frequency": 0.6,
        "hiding_frequency": 1.8,
        "interaction_desire": 0.7
    },
    PersonalityType.CURIOUS: {
        "exploration_frequency": 1.7,
        "attention_span": 0.8,
        "interaction_desire": 1.1
    },
    PersonalityType.LAZY: {
        "sleep_frequency": 1.8,
        "movement_speed": 0.7,
        "energy_consumption": 0.8
    },
    PersonalityType.ENERGETIC: {
        "movement_speed": 1.4,
        "play_frequency": 1.3,
        "energy_consumption": 1.5
    },
    PersonalityType.MISCHIEVOUS: {
        "icon_movement_frequency": 2.0,
        "play_frequency": 1.2,
        "interaction_desire": 1.2
    },
    PersonalityType.AFFECTIONATE: {
        "mouse_following_frequency": 1.6,
        "interaction_desire": 1.5,
        "happiness_gain": 1.3
    },
    PersonalityType.INDEPENDENT: {
        "interaction_desire": 0.6,
        "self_play_frequency": 1.4,
        "exploration_frequency": 1.3
    }
}

# Time settings (in seconds)
HUNGER_CHECK_INTERVAL = 60  # Check hunger every minute
BEHAVIOR_UPDATE_INTERVAL = 5  # Update behavior every 5 seconds
ANIMATION_UPDATE_INTERVAL = 0.1  # Update animation every 100ms
SAVE_INTERVAL = 300  # Auto-save every 5 minutes

# Desktop interaction settings
ICON_MOVE_PROBABILITY = 0.05  # 5% chance per behavior update
HIDE_AND_SEEK_DURATION = 30  # seconds
MOUSE_CHASE_DISTANCE = 200  # pixels - how close to chase mouse
