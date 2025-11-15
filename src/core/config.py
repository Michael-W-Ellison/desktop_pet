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

# Phase 4: Evolution stages
class EvolutionStage(Enum):
    BABY = "baby"
    JUVENILE = "juvenile"
    ADULT = "adult"
    ELDER = "elder"

# Phase 4: Elemental types
class ElementType(Enum):
    FIRE = "fire"
    WATER = "water"
    EARTH = "earth"
    AIR = "air"
    LIGHT = "light"
    DARK = "dark"
    ELECTRIC = "electric"
    ICE = "ice"
    NATURE = "nature"
    PSYCHIC = "psychic"
    NEUTRAL = "neutral"

# Phase 4: Creature variant types
class VariantType(Enum):
    NORMAL = "normal"
    SHINY = "shiny"
    MYSTIC = "mystic"
    SHADOW = "shadow"
    CRYSTAL = "crystal"

# Creature types (Phase 4: Expanded to 25+ fantastical species)
CREATURE_TYPES = [
    # Original 10
    "dragon",
    "cat",
    "dog",
    "bunny",
    "bird",
    "fox",
    "hamster",
    "owl",
    "penguin",
    "turtle",

    # Phase 4: Fantastical creatures (15 more)
    "phoenix",      # Majestic fire bird
    "sprite",       # Magical fairy creature
    "golem",        # Stone/earth guardian
    "griffin",      # Lion-eagle hybrid
    "unicorn",      # Magical horned horse
    "chimera",      # Multi-headed beast
    "wisp",         # Floating spirit orb
    "kraken",       # Sea monster
    "hydra",        # Multi-headed dragon
    "basilisk",     # Serpent king
    "manticore",    # Scorpion-tailed lion
    "salamander",   # Fire elemental lizard
    "sylph",        # Air spirit
    "undine",       # Water spirit
    "gnome"         # Earth spirit
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

# Phase 4: Species element affinities (which elements each species naturally has)
SPECIES_ELEMENTS = {
    # Original creatures
    "dragon": ElementType.FIRE,
    "cat": ElementType.NEUTRAL,
    "dog": ElementType.NEUTRAL,
    "bunny": ElementType.NATURE,
    "bird": ElementType.AIR,
    "fox": ElementType.FIRE,
    "hamster": ElementType.EARTH,
    "owl": ElementType.PSYCHIC,
    "penguin": ElementType.ICE,
    "turtle": ElementType.WATER,

    # Fantastical creatures
    "phoenix": ElementType.FIRE,
    "sprite": ElementType.LIGHT,
    "golem": ElementType.EARTH,
    "griffin": ElementType.AIR,
    "unicorn": ElementType.LIGHT,
    "chimera": ElementType.FIRE,
    "wisp": ElementType.PSYCHIC,
    "kraken": ElementType.WATER,
    "hydra": ElementType.WATER,
    "basilisk": ElementType.DARK,
    "manticore": ElementType.DARK,
    "salamander": ElementType.FIRE,
    "sylph": ElementType.AIR,
    "undine": ElementType.WATER,
    "gnome": ElementType.EARTH
}

# Phase 4: Element type advantages (rock-paper-scissors style)
ELEMENT_ADVANTAGES = {
    ElementType.FIRE: [ElementType.NATURE, ElementType.ICE],
    ElementType.WATER: [ElementType.FIRE, ElementType.EARTH],
    ElementType.EARTH: [ElementType.ELECTRIC, ElementType.FIRE],
    ElementType.AIR: [ElementType.EARTH, ElementType.NATURE],
    ElementType.LIGHT: [ElementType.DARK, ElementType.PSYCHIC],
    ElementType.DARK: [ElementType.LIGHT, ElementType.PSYCHIC],
    ElementType.ELECTRIC: [ElementType.WATER, ElementType.AIR],
    ElementType.ICE: [ElementType.NATURE, ElementType.WATER],
    ElementType.NATURE: [ElementType.WATER, ElementType.EARTH],
    ElementType.PSYCHIC: [ElementType.FIRE, ElementType.EARTH],
    ElementType.NEUTRAL: []
}

# Phase 4: Evolution requirements for each stage
EVOLUTION_REQUIREMENTS = {
    EvolutionStage.BABY: {
        "min_age_hours": 0,
        "min_happiness": 0,
        "min_bond": 0
    },
    EvolutionStage.JUVENILE: {
        "min_age_hours": 2,
        "min_happiness": 40,
        "min_bond": 30
    },
    EvolutionStage.ADULT: {
        "min_age_hours": 6,
        "min_happiness": 60,
        "min_bond": 60,
        "min_interactions": 50
    },
    EvolutionStage.ELDER: {
        "min_age_hours": 12,
        "min_happiness": 70,
        "min_bond": 80,
        "min_interactions": 100,
        "min_tricks_learned": 3
    }
}

# Phase 4: Stage size multipliers (how big the creature is at each stage)
STAGE_SIZE_MULTIPLIERS = {
    EvolutionStage.BABY: 0.6,
    EvolutionStage.JUVENILE: 0.8,
    EvolutionStage.ADULT: 1.0,
    EvolutionStage.ELDER: 1.2
}

# Phase 4: Variant rarity and effects
VARIANT_RARITY = {
    VariantType.NORMAL: 0.70,    # 70% chance
    VariantType.SHINY: 0.15,     # 15% chance (shimmering colors)
    VariantType.MYSTIC: 0.08,    # 8% chance (magical aura)
    VariantType.SHADOW: 0.05,    # 5% chance (dark powers)
    VariantType.CRYSTAL: 0.02    # 2% chance (very rare, crystalline)
}

# Phase 4: Variant stat modifiers
VARIANT_MODIFIERS = {
    VariantType.NORMAL: {
        "learning_rate": 1.0,
        "happiness_gain": 1.0,
        "bond_gain": 1.0
    },
    VariantType.SHINY: {
        "learning_rate": 1.2,
        "happiness_gain": 1.3,
        "bond_gain": 1.1,
        "sparkle_effect": True
    },
    VariantType.MYSTIC: {
        "learning_rate": 1.5,
        "happiness_gain": 1.2,
        "bond_gain": 1.3,
        "aura_effect": True,
        "trick_proficiency_bonus": 0.1
    },
    VariantType.SHADOW: {
        "learning_rate": 1.3,
        "happiness_gain": 0.8,
        "bond_gain": 1.4,
        "dark_aura": True,
        "intimidation_bonus": 1.5
    },
    VariantType.CRYSTAL: {
        "learning_rate": 1.8,
        "happiness_gain": 1.5,
        "bond_gain": 1.5,
        "crystal_effect": True,
        "legendary_status": True
    }
}

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

# ============ Phase 5: Advanced Bonding Constants ============

# Bonding system settings
BOND_DECAY_RATE = 0.5  # Bond points lost per hour without interaction (after 1 hour)
BOND_DECAY_DELAY = 1.0  # Hours before bond starts decaying
MAX_BOND = 100.0
MIN_BOND = 0.0

# Bond level thresholds
BOND_LEVEL_STRANGER = 20  # 0-20 = Stranger
BOND_LEVEL_ACQUAINTANCE = 40  # 20-40 = Acquaintance
BOND_LEVEL_FRIEND = 60  # 40-60 = Friend
BOND_LEVEL_CLOSE_FRIEND = 80  # 60-80 = Close Friend
BOND_LEVEL_BEST_FRIEND = 100  # 80-100 = Best Friend

# Trust system settings
TRUST_BUILD_RATE = 1.0  # Base trust gain from timely care
TRUST_DECAY_RATE = 3.0  # Trust loss from ignoring distress
MAX_TRUST = 100.0
MIN_TRUST = 0.0
CONSISTENCY_INITIAL = 50.0  # Initial consistency score
RELIABILITY_INITIAL = 50.0  # Initial reliability score

# Emotional state durations (in seconds)
EMOTIONAL_STATE_DURATIONS = {
    'jealousy_min': 300,        # 5 minutes minimum
    'jealousy_max': 900,        # 15 minutes maximum
    'separation_anxiety': 3600,  # 1 hour
    'excited_return_min': 300,   # 5 minutes minimum
    'excited_return_max': 900,   # 15 minutes maximum
    'longing': 1800,            # 30 minutes
    'possessive': 600,          # 10 minutes
    'insecure': 900             # 15 minutes
}

# Separation anxiety thresholds (in hours)
SEPARATION_ANXIETY_THRESHOLD_CLOSE_FRIEND = 2.0  # Close friends miss you after 2 hours
SEPARATION_ANXIETY_THRESHOLD_BEST_FRIEND = 1.0   # Best friends miss you after 1 hour
SEPARATION_ANXIETY_MIN_BOND = 60  # Need at least 60 bond for separation anxiety

# Jealousy settings
JEALOUSY_MIN_BOND = 30  # Need at least 30 bond to feel jealous
JEALOUSY_BASE_CHANCE = {
    'stranger': 0.0,         # Strangers don't get jealous
    'acquaintance': 0.1,     # 10% base chance
    'friend': 0.3,           # 30% base chance
    'close_friend': 0.6,     # 60% base chance
    'best_friend': 0.8       # 80% base chance
}

# Name calling settings
NAME_RECOGNITION_BASE_RESPONSE = 0.7  # 70% max from just knowing name
NAME_RECOGNITION_BOND_BONUS = 0.2    # Up to +20% from bond
NAME_RECOGNITION_TRUST_BONUS = 0.1   # Up to +10% from trust
NAME_RECOGNITION_MAX_CHANCE = 0.95   # 95% maximum response rate
NAME_RECOGNITION_WRONG_NAME_CHANCE = 0.1  # 10% chance to respond to wrong name

# Preference categories and items
TOY_TYPES = [
    'ball', 'rope', 'squeaky_toy', 'feather', 'mouse_toy',
    'puzzle_toy', 'chew_toy', 'laser_pointer', 'plush_toy', 'frisbee'
]

FOOD_TYPES = [
    'kibble', 'wet_food', 'treats', 'vegetables', 'fruit',
    'fish', 'chicken', 'beef', 'cheese', 'peanut_butter'
]

ACTIVITY_TYPES = [
    'playing', 'training', 'petting', 'grooming', 'talking',
    'exploring', 'resting', 'chasing', 'hiding', 'swimming'
]

# Preference system settings
PREFERENCE_INITIAL = 50.0  # Start neutral (0-100 scale)
PREFERENCE_MIN = 0.0       # Absolutely hates it
PREFERENCE_MAX = 100.0     # Absolutely loves it
PREFERENCE_CHANGE_RATE = 10.0  # Base change per experience

# Preference reaction thresholds
PREFERENCE_REACTION_THRESHOLDS = {
    'ecstatic': 80,      # 80-100: Ecstatic
    'happy': 60,         # 60-80: Happy
    'neutral': 40,       # 40-60: Neutral
    'reluctant': 20,     # 20-40: Reluctant
    'refuse': 0          # 0-20: Refuse
}

# ============ Phase 6: Enhanced Training & Commands Constants ============

# Reinforcement effects
REINFORCEMENT_EFFECTS = {
    'verbal_praise': {
        'bond_change': 0.3,
        'trust_change': 0.0,
        'happiness_change': 2.0,
        'learning_boost': 1.1
    },
    'treat': {
        'bond_change': 0.5,
        'trust_change': 0.2,
        'happiness_change': 5.0,
        'learning_boost': 1.3
    },
    'toy_reward': {
        'bond_change': 0.4,
        'trust_change': 0.0,
        'happiness_change': 4.0,
        'learning_boost': 1.2
    },
    'affection': {
        'bond_change': 0.6,
        'trust_change': 0.3,
        'happiness_change': 3.0,
        'learning_boost': 1.1
    },
    'punishment': {
        'bond_change': -0.5,
        'trust_change': -2.0,
        'happiness_change': -5.0,
        'learning_boost': 0.7
    },
    'ignore': {
        'bond_change': 0.0,
        'trust_change': 0.0,
        'happiness_change': -1.0,
        'learning_boost': 0.9
    }
}

# Stubbornness modifiers
STUBBORNNESS_MODIFIERS = {
    'unhappy_minor': 0.2,       # Happiness 30-50
    'unhappy_major': 0.4,       # Happiness < 30
    'low_trust_minor': 0.3,     # Trust 20-40
    'low_trust_major': 0.5,     # Trust < 20
    'low_bond': 0.3,            # Bond < 30
    'hungry_minor': 0.2,        # Hunger 50-70
    'hungry_major': 0.4,        # Hunger > 70
    'tired_minor': 0.3,         # Energy 20-40
    'tired_major': 0.5,         # Energy < 20
    'training_fatigue_minor': 0.2,   # 5-10 recent commands
    'training_fatigue_major': 0.4    # > 10 recent commands
}

# Training progress thresholds
TRAINING_PROFICIENCY_THRESHOLD = 0.7  # Needed to reliably perform trick
TRAINING_MASTERY_THRESHOLD = 0.95     # Fully mastered
TRAINING_FORGETTING_RATE = 0.01       # Proficiency loss per day without practice
TRAINING_FORGETTING_DELAY = 1.0       # Days before skill starts degrading

# Training session limits
MAX_COMMANDS_PER_SESSION = 15         # Optimal training session length
TRAINING_FATIGUE_THRESHOLD = 10       # Commands before fatigue sets in
COMMAND_COOLDOWN_SECONDS = 2          # Minimum time between commands

# Learning rate modifiers by difficulty
LEARNING_RATES_BY_DIFFICULTY = {
    'trivial': 0.33,    # 1/3 - learn in ~3 attempts
    'easy': 0.14,       # 1/7 - learn in ~7 attempts
    'medium': 0.08,     # 1/12 - learn in ~12 attempts
    'hard': 0.04,       # 1/25 - learn in ~25 attempts
    'expert': 0.02      # 1/50 - learn in ~50 attempts
}

# Success rate thresholds for training analytics
SUCCESS_RATE_EXCELLENT = 0.9   # 90%+ success rate
SUCCESS_RATE_GOOD = 0.7        # 70-90% success rate
SUCCESS_RATE_FAIR = 0.5        # 50-70% success rate
SUCCESS_RATE_POOR = 0.3        # 30-50% success rate
# < 30% = needs more practice

# ============================================================================
# PHASE 7: ENHANCED MEMORY SYSTEMS
# ============================================================================

# Autobiographical memory settings
AUTOBIOGRAPHICAL_FIRST_TIME_THRESHOLD = 1  # Must be truly first occurrence
AUTOBIOGRAPHICAL_MEMORY_STRENGTH = 1.0      # First times never fade
AUTOBIOGRAPHICAL_EMOTION_THRESHOLD = 0.3    # Minimum emotional intensity to record

# Favorite memory settings
MAX_FAVORITE_MEMORIES = 20                  # Maximum favorite memories to keep
FAVORITE_MEMORY_HAPPINESS_WEIGHT = 0.6      # Weight of happiness in scoring
FAVORITE_MEMORY_EMOTION_WEIGHT = 0.4        # Weight of emotional intensity
FAVORITE_MEMORY_MIN_SCORE = 0.5             # Minimum score to be considered favorite
FAVORITE_MEMORY_HAPPINESS_THRESHOLD = 70.0  # Minimum happiness to create favorite

# Trauma memory settings
TRAUMA_SEVERITY_LIGHT = 0.3                 # Light trauma (e.g., loud noise)
TRAUMA_SEVERITY_MODERATE = 0.6              # Moderate trauma (e.g., rough handling)
TRAUMA_SEVERITY_SEVERE = 0.9                # Severe trauma (e.g., abandonment)
TRAUMA_TRUST_IMPACT_MULTIPLIER = 10.0       # Severity * 10 = trust loss
TRAUMA_BOND_IMPACT_MULTIPLIER = 5.0         # Severity * 5 = bond loss
TRAUMA_DECAY_RATE = 0.02                    # Decay per day (heals slowly)
TRAUMA_MIN_DECAY_STRENGTH = 0.1             # Trauma strength floor (always some memory)
TRAUMA_HEALING_AMOUNT = 0.05                # Healing from positive experiences
FEAR_TRIGGER_THRESHOLD = 0.3                # Minimum trauma strength to trigger fear

# Associative memory settings
ASSOCIATION_MIN_OCCURRENCES = 3             # Need 3+ occurrences to form pattern
ASSOCIATION_STRENGTH_INCREMENT = 0.15       # Strength gain per occurrence
ASSOCIATION_MAX_STRENGTH = 1.0              # Maximum association strength
ASSOCIATION_DECAY_RATE = 0.01               # Decay per day without reinforcement
ASSOCIATION_CONFIDENCE_THRESHOLD = 0.5      # Minimum strength for prediction
ASSOCIATION_CONTEXT_TYPES = ['location', 'time', 'object', 'weather', 'activity']

# Dream system settings
DREAM_MIN_INTERVAL_HOURS = 2.0              # Minimum hours between dreams
DREAM_MAX_INTERVAL_HOURS = 4.0              # Maximum hours between dreams
DREAM_BASE_PROBABILITY = 0.3                # 30% base chance per sleep check
DREAM_MIN_MEMORIES_FOR_DREAM = 3            # Need at least 3 memories to dream
DREAM_MEMORY_SAMPLE_SIZE = 5                # Number of memories to include in dream
DREAM_EMOTION_BIAS = 0.7                    # Prefer emotional memories (70% weight)
DREAM_CONSOLIDATION_BOOST = 0.1             # Memory strength boost from dreaming
DREAM_NIGHTMARE_THRESHOLD = -0.5            # Emotional valence < -0.5 = nightmare
DREAM_VIVID_THRESHOLD = 0.8                 # Emotional intensity > 0.8 = vivid dream
DREAM_REM_SLEEP_HOURS = 2.0                 # Hours of sleep needed for REM/dreaming

# Memory importance and retention
MEMORY_IMPORTANCE_CRUCIAL = 0.95            # Crucial memories (never fade)
MEMORY_IMPORTANCE_VERY_HIGH = 0.8           # Very important (slow fade)
MEMORY_IMPORTANCE_HIGH = 0.6                # Important (moderate fade)
MEMORY_IMPORTANCE_MEDIUM = 0.4              # Medium importance (normal fade)
MEMORY_IMPORTANCE_LOW = 0.2                 # Low importance (fast fade)
MEMORY_RETENTION_IMPORTANCE_WEIGHT = 0.6    # Weight of importance in retention
MEMORY_RETENTION_AGE_WEIGHT = 0.3           # Weight of age in retention
MEMORY_RETENTION_RECALL_WEIGHT = 0.1        # Weight of recall frequency
MEMORY_AGE_DECAY_RATE = 0.05                # Decay rate per day of age
MEMORY_RECALL_BOOST_PER_RECALL = 0.05       # Boost per recall (max 0.3)
MEMORY_RECALL_BOOST_MAX = 0.3               # Maximum boost from recalls
MEMORY_MIN_RETENTION_PROBABILITY = 0.1      # Minimum 10% retention for all memories

# Memory consolidation during sleep
CONSOLIDATION_SLEEP_HOURS_REQUIRED = 1.0    # Hours of sleep needed for consolidation
CONSOLIDATION_MEMORY_BOOST = 0.15           # Strength boost during consolidation
CONSOLIDATION_PRIORITY_THRESHOLD = 0.5      # Importance threshold for priority consolidation

# Time settings (in seconds)
HUNGER_CHECK_INTERVAL = 60  # Check hunger every minute
BEHAVIOR_UPDATE_INTERVAL = 5  # Update behavior every 5 seconds
ANIMATION_UPDATE_INTERVAL = 0.1  # Update animation every 100ms
SAVE_INTERVAL = 300  # Auto-save every 5 minutes

# Desktop interaction settings
ICON_MOVE_PROBABILITY = 0.05  # 5% chance per behavior update
HIDE_AND_SEEK_DURATION = 30  # seconds
MOUSE_CHASE_DISTANCE = 200  # pixels - how close to chase mouse

# ============================================================================
# PHASE 8: LIVING CREATURE BEHAVIORS
# ============================================================================

# Bathroom needs
BLADDER_FILL_RATE = 8.0                  # Points per hour (~12.5 hours to fill)
BOWEL_FILL_RATE = 4.0                    # Points per hour (~25 hours to fill)
BATHROOM_ACCIDENT_UNHAPPINESS = 10.0     # Happiness loss from accident
BATHROOM_RELIEF_HAPPINESS = 5.0          # Happiness from using bathroom
HOUSE_TRAINING_THRESHOLD = 0.9           # Training level for house-trained status
BLADDER_CONTROL_BABY = 0.3               # Bladder control for babies
BLADDER_CONTROL_YOUNG = 0.5              # Bladder control for young pets
BLADDER_CONTROL_ADULT = 1.0              # Bladder control for adults
BLADDER_CONTROL_SENIOR = 0.8             # Bladder control for seniors
ACCIDENT_RISK_URGENT_THRESHOLD = 0.7     # Bladder/bowel level for accident risk
ACCIDENT_RISK_DESPERATE_THRESHOLD = 0.85 # Level for high accident risk

# Grooming and cleanliness
DIRT_ACCUMULATION_RATE = 1.0             # Cleanliness points lost per hour
BATH_CLEANLINESS_RESTORE = 100.0         # Bath fully restores cleanliness
BRUSHING_CLEANLINESS_GAIN = 30.0         # Brushing adds cleanliness
BATH_HAPPINESS_LIKE = 5.0                # Happiness if likes baths
BATH_HAPPINESS_DISLIKE = -3.0            # Happiness if dislikes baths
BRUSHING_HAPPINESS = 8.0                 # Happiness from brushing
BRUSHING_BOND_GAIN = 0.5                 # Bond increase from brushing
DIRTY_THRESHOLD = 30.0                   # Cleanliness level considered "dirty"
FILTHY_THRESHOLD = 10.0                  # Cleanliness level considered "filthy"
GROOMING_NEEDED_THRESHOLD = 50.0         # When grooming becomes needed

# Health and illness
HEALTH_REGENERATION_RATE = 2.0           # Health points per hour when healthy
ILLNESS_CHANCE_PER_HOUR = 0.001          # Base chance of getting sick per hour
IMMUNITY_BASE = 50.0                     # Starting immunity level
IMMUNITY_MAX = 100.0                     # Maximum immunity
IMMUNITY_MIN = 0.0                       # Minimum immunity
STRESS_ILLNESS_MULTIPLIER = 1.5          # Illness risk multiplier when stressed (>70)
HYGIENE_ILLNESS_MULTIPLIER = 2.0         # Illness risk multiplier when dirty (<30)
VET_RECOVERY_BOOST = 0.3                 # 30% recovery progress from vet visit
VET_DAMAGE_REDUCTION = 0.5               # 50% reduction in illness damage after vet
VET_BASE_COST = 50                       # Base cost for vet visit
VET_PER_ILLNESS_COST = 25                # Additional cost per illness
MEDICINE_DURATION_HOURS = 24.0           # How long medicine lasts
ILLNESS_NATURAL_RECOVERY_RATE = 0.05     # 5% recovery per day without treatment

# Illness damage per hour by severity
ILLNESS_DAMAGE_MILD = 1.0
ILLNESS_DAMAGE_MODERATE = 2.0
ILLNESS_DAMAGE_SEVERE = 4.0
ILLNESS_DAMAGE_CRITICAL = 8.0

# Aging and lifespan
DEFAULT_LIFESPAN_DAYS = 3650             # 10 years default lifespan
AGING_RATE_NORMAL = 1.0                  # Normal aging speed
AGE_EGG_DAYS = 3                         # Days in egg stage
AGE_BABY_DAYS = 30                       # Days in baby stage (up to 1 month)
AGE_CHILD_DAYS = 90                      # Days in child stage (up to 3 months)
AGE_TEEN_DAYS = 180                      # Days in teen stage (up to 6 months)
AGE_ADULT_DAYS = 2555                    # Days in adult stage (up to ~7 years)
AGE_SENIOR_DAYS = 3650                   # Days in senior stage (up to 10 years)
# Elder is anything beyond senior

# Age modifiers for different life stages
BABY_ENERGY_MAX_MODIFIER = 0.6
BABY_HUNGER_RATE_MODIFIER = 1.5
BABY_LEARNING_RATE_MODIFIER = 1.2
CHILD_ACTIVITY_MODIFIER = 1.2
TEEN_ACTIVITY_MODIFIER = 1.3
SENIOR_ENERGY_MAX_MODIFIER = 0.8
SENIOR_ACTIVITY_MODIFIER = 0.7
ELDER_ENERGY_MAX_MODIFIER = 0.6
ELDER_ACTIVITY_MODIFIER = 0.5

# Natural death
DEATH_CHANCE_START_AGE = 1.0             # Start checking for natural death at lifespan
DEATH_CHANCE_PER_YEAR_OVER = 1.0         # Each year over lifespan = 100% added chance

# Breeding and genetics
BREEDING_BASE_SUCCESS_CHANCE = 0.7       # 70% base breeding success
PREGNANCY_DURATION_DAYS = 7.0            # Pregnancy lasts 1 week
LITTER_SIZE_MIN = 1
LITTER_SIZE_MAX = 3
MUTATION_CHANCE = 0.1                    # 10% chance of genetic mutation
BREEDING_ADULT_AGE_REQUIRED = True       # Must be adult to breed
GENETIC_TRAIT_BLEND_VARIATION = 10.0     # +/- variation when blending numerical traits

# Genetics
GENETIC_SIZES = ['small', 'medium', 'large']
GENETIC_COLORS = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'silver', 'gold']
GENETIC_PATTERNS = ['solid', 'striped', 'spotted', 'mixed', 'swirled']
GENETIC_EYE_COLORS = ['brown', 'blue', 'green', 'amber']

# Circadian rhythm
SLEEP_DRIVE_INCREASE_RATE = 5.0          # Points per hour awake
SLEEP_DRIVE_DECREASE_RATE = 15.0         # Points per hour asleep
SLEEP_DRIVE_EXHAUSTED_THRESHOLD = 90.0   # Will definitely sleep
SLEEP_DRIVE_TIRED_THRESHOLD = 60.0       # Likely to sleep at bedtime
SLEEP_DEBT_CRITICAL_HOURS = 8.0          # Hours of sleep debt that forces sleep
SLEEP_CYCLE_DURATION_MINUTES = 90.0      # Length of one sleep cycle (light -> deep -> REM)
NAP_DURATION_THRESHOLD = 2.0             # Hours - anything less is a nap

# Species-specific sleep needs (hours per day)
CAT_DAILY_SLEEP_NEED = 16.0
DOG_DAILY_SLEEP_NEED = 14.0
BIRD_DAILY_SLEEP_NEED = 12.0
HAMSTER_DAILY_SLEEP_NEED = 14.0
RABBIT_DAILY_SLEEP_NEED = 8.0

# Preferred sleep times (hour of day, 0-23)
CAT_PREFERRED_SLEEP_TIME = 22
DOG_PREFERRED_SLEEP_TIME = 21
BIRD_PREFERRED_SLEEP_TIME = 19
HAMSTER_PREFERRED_SLEEP_TIME = 8        # Nocturnal - sleeps during day
RABBIT_PREFERRED_SLEEP_TIME = 20

# Sleep quality factors
SLEEP_QUALITY_NATURAL_WAKE = 1.0
SLEEP_QUALITY_FORCED_WAKE = 0.6
SLEEP_QUALITY_IDEAL_DURATION_HOURS = 6.0
SLEEP_QUALITY_MIN_DURATION_HOURS = 1.0
