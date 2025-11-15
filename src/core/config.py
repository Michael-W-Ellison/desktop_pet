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

# Learning settings - Basic Network
LEARNING_RATE = 0.001  # Lower for Adam optimizer
NEURAL_NETWORK_LAYERS = [8, 6]  # Basic hidden layers

# Enhanced Learning settings (for sophisticated AI)
USE_ADAM_OPTIMIZER = True  # Use Adam instead of SGD
USE_LEARNING_RATE_SCHEDULE = True  # Decay learning rate over time
GRADIENT_CLIP_NORM = 5.0  # Prevent exploding gradients
ADAM_BETA1 = 0.9  # Momentum parameter
ADAM_BETA2 = 0.999  # RMSprop parameter

# Enhanced architecture settings
ENHANCED_NETWORK_LAYERS = [64, 32, 16, 8]  # Larger, deeper network
USE_DROPOUT = True  # Prevent overfitting
DROPOUT_RATE = 0.25  # 25% dropout
USE_BATCH_NORMALIZATION = True  # Stable training

# AI Complexity levels (for different age groups)
class AIComplexity(Enum):
    SIMPLE = "simple"  # Basic learning, good for younger kids
    MEDIUM = "medium"  # Enhanced learning with memory
    ADVANCED = "advanced"  # Full RL with all networks
    EXPERT = "expert"  # Maximum sophistication with visualization

DEFAULT_AI_COMPLEXITY = AIComplexity.MEDIUM

# Personality types (Phase 3: Expanded to 20+ types)
class PersonalityType(Enum):
    # Original 8
    PLAYFUL = "playful"
    SHY = "shy"
    CURIOUS = "curious"
    LAZY = "lazy"
    ENERGETIC = "energetic"
    MISCHIEVOUS = "mischievous"
    AFFECTIONATE = "affectionate"
    INDEPENDENT = "independent"

    # Phase 3: New personalities (12 more = 20 total)
    CRANKY = "cranky"
    STUBBORN = "stubborn"
    SKITTISH = "skittish"
    BRAVE = "brave"
    GENTLE = "gentle"
    FIERCE = "fierce"
    CLEVER = "clever"
    SILLY = "silly"
    SERIOUS = "serious"
    PATIENT = "patient"
    IMPATIENT = "impatient"
    TRUSTING = "trusting"
    SUSPICIOUS = "suspicious"
    CALM = "calm"
    ANXIOUS = "anxious"
    LOYAL = "loyal"
    SELFISH = "selfish"

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
    # Original 8 personalities
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
    },

    # Phase 3: New personalities
    PersonalityType.CRANKY: {
        "irritability": 1.8,
        "happiness_decay": 1.3,
        "interaction_desire": 0.5,
        "negative_reaction_chance": 0.4
    },
    PersonalityType.STUBBORN: {
        "training_difficulty": 1.6,
        "command_refusal_rate": 0.6,
        "persistence": 1.4,
        "pattern_breaking": 0.3
    },
    PersonalityType.SKITTISH: {
        "hiding_frequency": 1.9,
        "fear_threshold": 0.3,
        "interaction_desire": 0.4,
        "movement_speed": 1.5
    },
    PersonalityType.BRAVE: {
        "exploration_frequency": 1.6,
        "fear_threshold": 1.8,
        "interaction_desire": 1.2,
        "boldness": 1.7
    },
    PersonalityType.GENTLE: {
        "interaction_desire": 1.3,
        "aggression": 0.2,
        "patience": 1.6,
        "happiness_gain": 1.2
    },
    PersonalityType.FIERCE: {
        "aggression": 1.8,
        "boldness": 1.9,
        "energy_consumption": 1.4,
        "territoriality": 1.7
    },
    PersonalityType.CLEVER: {
        "learning_speed": 1.7,
        "problem_solving": 1.8,
        "attention_span": 1.4,
        "trick_proficiency_gain": 1.3
    },
    PersonalityType.SILLY: {
        "random_behavior": 1.9,
        "play_frequency": 1.6,
        "attention_span": 0.5,
        "unpredictability": 1.8
    },
    PersonalityType.SERIOUS: {
        "play_frequency": 0.5,
        "focus": 1.7,
        "routine_preference": 1.6,
        "predictability": 1.8
    },
    PersonalityType.PATIENT: {
        "wait_tolerance": 1.9,
        "irritability": 0.3,
        "training_ease": 1.4,
        "calm_behavior": 1.6
    },
    PersonalityType.IMPATIENT: {
        "wait_tolerance": 0.3,
        "irritability": 1.6,
        "movement_speed": 1.3,
        "attention_span": 0.6
    },
    PersonalityType.TRUSTING: {
        "interaction_desire": 1.7,
        "fear_threshold": 1.5,
        "bonding_speed": 1.6,
        "command_compliance": 1.4
    },
    PersonalityType.SUSPICIOUS: {
        "interaction_desire": 0.5,
        "fear_threshold": 0.6,
        "trust_building": 0.4,
        "hiding_frequency": 1.5
    },
    PersonalityType.CALM: {
        "stress_resistance": 1.8,
        "panic_threshold": 1.9,
        "energy_consumption": 0.8,
        "emotional_stability": 1.7
    },
    PersonalityType.ANXIOUS: {
        "stress_sensitivity": 1.9,
        "panic_threshold": 0.4,
        "hiding_frequency": 1.6,
        "energy_consumption": 1.3
    },
    PersonalityType.LOYAL: {
        "bonding_strength": 1.9,
        "separation_anxiety": 1.7,
        "command_compliance": 1.6,
        "owner_focus": 1.8
    },
    PersonalityType.SELFISH: {
        "resource_guarding": 1.7,
        "sharing_willingness": 0.3,
        "self_focus": 1.8,
        "independence": 1.5
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
