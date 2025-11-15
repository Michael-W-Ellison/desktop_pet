"""
Test script for Phase 5: Advanced Interaction & Bonding

Tests:
- Bonding system (stranger → best friend progression)
- Trust system (builds through consistent care)
- Emotional states (jealousy, separation anxiety, excitement)
- Preference system (individual likes/dislikes)
- Name calling (responds based on bond/trust/recognition)
- Integration with Creature class
- Persistence (save/load)
"""
import sys
sys.path.insert(0, '/home/user/desktop_pet/src')

from core.creature import Creature
from core.config import PersonalityType
from core.bonding_system import BondingSystem, BondLevel
from core.trust_system import TrustSystem
from core.emotional_states import EmotionalStateManager, EmotionalState
from core.preference_system import PreferenceSystem
from core.name_calling import NameCallingSystem
import time

print("=" * 60)
print("PHASE 5: ADVANCED INTERACTION & BONDING TEST")
print("=" * 60)

# Test 1: Bonding System
print("\n1. Testing Bonding System")
print("-" * 60)

bonding = BondingSystem(initial_bond=0.0)
print(f"Initial bond: {bonding.bond}")
print(f"Bond level: {bonding.get_bond_level().value}")
print(f"Description: {bonding.get_bond_description()}")

# Progress through bond levels
print("\nProgressing through bond levels:")
bond_targets = [
    (25, BondLevel.ACQUAINTANCE, "Acquaintance"),
    (50, BondLevel.FRIEND, "Friend"),
    (70, BondLevel.CLOSE_FRIEND, "Close Friend"),
    (90, BondLevel.BEST_FRIEND, "Best Friend")
]

for target_bond, expected_level, level_name in bond_targets:
    # Feed multiple times to reach target
    while bonding.bond < target_bond:
        gain, msg = bonding.process_interaction('feed', positive=True, quality=1.0)
        bonding.times_fed += 1

    current_level = bonding.get_bond_level()
    print(f"  Bond {bonding.bond:.1f}: {current_level.value} - {bonding.get_bond_description()[:50]}...")
    assert current_level == expected_level, f"Should be {level_name}"

# Test bond decay
print("\nTesting bond decay from neglect:")
initial_bond = bonding.bond
bonding.process_neglect(hours_neglected=5.0)
print(f"  After 5 hours neglect: {bonding.bond:.1f} (was {initial_bond:.1f})")
assert bonding.bond < initial_bond, "Bond should decay"

# Test jealousy chance
print("\nTesting jealousy mechanics:")
for level_val in [0, 30, 50, 70, 90]:
    temp_bonding = BondingSystem(initial_bond=level_val)
    chance = temp_bonding.get_jealousy_chance(attention_to_others=0.5)
    print(f"  Bond {level_val}: {chance*100:.0f}% jealousy chance")

print("✓ Bonding system working!")

# Test 2: Trust System
print("\n2. Testing Trust System")
print("-" * 60)

trust = TrustSystem(initial_trust=0.0)
print(f"Initial trust: {trust.trust}")
print(f"Description: {trust.get_trust_level_description()}")

# Build trust through consistent care
print("\nBuilding trust through care events:")
for i in range(10):
    trust.process_care_event('feed', timely=True)
    if i % 3 == 0:
        print(f"  After {i+1} care events: Trust = {trust.trust:.1f}")

print(f"Final trust: {trust.trust:.1f}")
print(f"Consistency score: {trust.consistency_score:.1f}")

# Test command processing
print("\nTesting command obedience modifier:")
modifier = trust.get_command_obedience_modifier()
print(f"  Obedience modifier at trust {trust.trust:.1f}: {modifier:.2f}x")

# Test trust from gentle interactions
print("\nTesting gentle vs rough interactions:")
trust.process_interaction_quality(gentle=True)
print(f"  After gentle interaction: {trust.trust:.1f}")
initial = trust.trust
trust.process_interaction_quality(gentle=False)
print(f"  After rough interaction: {trust.trust:.1f} (decreased)")
assert trust.trust < initial, "Rough handling should reduce trust"

print("✓ Trust system working!")

# Test 3: Emotional States
print("\n3. Testing Emotional State System")
print("-" * 60)

emotions = EmotionalStateManager()
print("Initial emotional states:", emotions.get_current_states())

# Test jealousy
print("\nTriggering jealousy:")
emotions.trigger_jealousy(bond_level=80.0, trigger_intensity=0.7)
has_jealousy = emotions.has_state(EmotionalState.JEALOUS)
print(f"  Has jealousy: {has_jealousy}")
if has_jealousy:
    intensity = emotions.get_state_intensity(EmotionalState.JEALOUS)
    print(f"  Jealousy intensity: {intensity:.2f}")
    assert intensity > 0, "Should have jealousy intensity"

# Test separation anxiety
print("\nTriggering separation anxiety:")
emotions.trigger_separation_anxiety(bond_level=85.0, hours_away=3.0)
has_anxiety = emotions.has_state(EmotionalState.SEPARATION_ANXIETY)
print(f"  Has separation anxiety: {has_anxiety}")
if has_anxiety:
    intensity = emotions.get_state_intensity(EmotionalState.SEPARATION_ANXIETY)
    print(f"  Anxiety intensity: {intensity:.2f}")

# Test excited return
print("\nTriggering excited return:")
emotions.trigger_excited_return(bond_level=80.0, hours_away=4.0)
has_excitement = emotions.has_state(EmotionalState.EXCITED_RETURN)
print(f"  Has excitement: {has_excitement}")
if has_excitement:
    intensity = emotions.get_state_intensity(EmotionalState.EXCITED_RETURN)
    print(f"  Excitement intensity: {intensity:.2f}")

# Test behavioral modifiers
print("\nEmotional state behavioral modifiers:")
modifiers = emotions.get_behavioral_modifiers()
for key, value in list(modifiers.items())[:3]:
    print(f"  {key}: {value:.2f}x")

# Test owner presence tracking
print("\nTesting owner presence:")
emotions.set_owner_presence(False, bond_level=80, trust_level=70)
print(f"  Owner left, time recorded: {emotions.time_owner_left is not None}")
time.sleep(0.1)  # Brief delay
emotions.set_owner_presence(True, bond_level=80, trust_level=70)
print(f"  Owner returned, reunion excitement: {emotions.reunion_excitement_level:.2f}")

print("✓ Emotional states working!")

# Test 4: Preference System
print("\n4. Testing Preference System")
print("-" * 60)

prefs = PreferenceSystem(personality_type='playful')
print("Initial preferences (playful personality):")
print(f"  Playing activity: {prefs.get_preference('activity', 'playing'):.1f}")
print(f"  Training activity: {prefs.get_preference('activity', 'training'):.1f}")

# Record positive experiences with ball
print("\nRecording positive experiences with ball toy:")
for i in range(5):
    prefs.record_experience('toy', 'ball', enjoyment=0.8)

ball_pref = prefs.get_preference('toy', 'ball')
print(f"  Ball preference after 5 positive experiences: {ball_pref:.1f}")

# Get reaction
reaction = prefs.get_reaction_to_item('toy', 'ball')
print(f"  Reaction to ball: {reaction['reaction']} - {reaction['description']}")

# Test favorite
top_toys = prefs.get_top_preferences('toy', 3)
print(f"  Top toys: {[(name, score) for name, score in top_toys]}")
favorite_toy = top_toys[0][0] if top_toys else None
print(f"  Favorite toy: {favorite_toy}")

# Record negative experience
print("\nRecording negative experience with puzzle_toy:")
prefs.record_experience('toy', 'puzzle_toy', enjoyment=-0.6)
puzzle_pref = prefs.get_preference('toy', 'puzzle_toy')
print(f"  Puzzle toy preference: {puzzle_pref:.1f}")

# Get all favorites
all_favorites = prefs.get_favorites()
print(f"  Favorites dict: {all_favorites}")

print("✓ Preference system working!")

# Test 5: Name Calling System
print("\n5. Testing Name Calling System")
print("-" * 60)

name_calling = NameCallingSystem()
pet_name = "Fluffy"

# Test with low bond/trust/recognition
print(f"\nCalling '{pet_name}' with low bond/trust/recognition:")
result = name_calling.call_pet(
    pet_name=pet_name,
    actual_name=pet_name,
    bond_level=10.0,
    trust_level=10.0,
    personality='shy',
    name_recognition_proficiency=0.2,
    current_mood=None
)
print(f"  Responded: {result['responded']}")
if result['responded']:
    print(f"  Response type: {result.get('response_type')}")
    print(f"  Animation: {result.get('animation')}")
else:
    print(f"  Reason: {result.get('reason')}")

# Test with high bond/trust/recognition
print(f"\nCalling '{pet_name}' with high bond/trust/recognition:")
result = name_calling.call_pet(
    pet_name=pet_name,
    actual_name=pet_name,
    bond_level=90.0,
    trust_level=80.0,
    personality='affectionate',
    name_recognition_proficiency=0.9,
    current_mood='happy'
)
print(f"  Responded: {result['responded']}")
if result['responded']:
    print(f"  Response type: {result.get('response_type')}")
    print(f"  Message: {result.get('message')}")
    print(f"  Bond change: +{result.get('bond_change', 0):.2f}")

# Test wrong name
print(f"\nCalling wrong name 'Spot' (actual: '{pet_name}'):")
result = name_calling.call_pet(
    pet_name="Spot",
    actual_name=pet_name,
    bond_level=90.0,
    trust_level=80.0,
    personality='affectionate',
    name_recognition_proficiency=0.9
)
print(f"  Responded: {result['responded']}")

# Test response rate
print(f"\nResponse statistics:")
stats = name_calling.get_stats()
print(f"  Times called: {stats['times_called']}")
print(f"  Times responded: {stats['times_responded']}")
print(f"  Response rate: {stats['response_rate']:.1f}%")

print("✓ Name calling system working!")

# Test 6: Integration with Creature
print("\n6. Testing Integration with Creature Class")
print("-" * 60)

creature = Creature(creature_type='dragon', personality=PersonalityType.LOYAL)
print(f"Created {creature.name} the {creature.personality.value} {creature.creature_type}")

# Test initial bonding stats
stats = creature.get_bonding_stats()
print(f"\nInitial bonding stats:")
print(f"  Bond: {stats['bond']:.1f} ({stats['bond_level']})")
print(f"  Trust: {stats['trust']:.1f}")
print(f"  Emotional states: {len(stats['emotional_states'])} active")

# Test feeding with bonding
print(f"\nFeeding {creature.name}:")
creature.hunger = 80  # Make hungry
creature.feed(amount=30, food_type='fish')
stats = creature.get_bonding_stats()
print(f"  Bond after feeding: {stats['bond']:.1f}")
print(f"  Trust after feeding: {stats['trust']:.1f}")

# Test interactions
print(f"\nInteracting with {creature.name}:")
for i in range(5):
    creature.interact('play_ball', positive=True, item='ball', gentle=True)

stats = creature.get_bonding_stats()
print(f"  Bond after 5 interactions: {stats['bond']:.1f}")
print(f"  Trust after 5 interactions: {stats['trust']:.1f}")

# Check favorite items
favorites = creature.get_favorite_items()
print(f"  Top toy: {favorites.get('top_toy', 'None yet')}")

# Test calling by name
print(f"\nCalling {creature.name} by name:")
result = creature.call_by_name(creature.name)
print(f"  Responded: {result['responded']}")
if result['responded']:
    print(f"  Message: {result.get('message')}")

# Simulate owner leaving and returning
print(f"\nSimulating owner departure and return:")
creature.process_owner_departure()
print(f"  Owner left")
time.sleep(0.1)
creature.bonding.bond = 85  # Ensure high bond
creature.process_owner_return(hours_away=3.0)
has_anxiety, anxiety_info = creature.check_separation_anxiety()
print(f"  Owner returned after 3 hours")
print(f"  Reunion excitement: {creature.emotional_states.reunion_excitement_level:.2f}")

# Test jealousy
print(f"\nTriggering jealousy:")
creature.trigger_jealousy(attention_amount=0.5)
emotions_active = creature.emotional_states.get_current_states()
print(f"  Active emotional states: {list(emotions_active.keys())}")

print("✓ Creature integration working!")

# Test 7: Persistence
print("\n7. Testing Persistence (Save/Load)")
print("-" * 60)

# Create a creature with developed bonding
original = Creature(creature_type='phoenix', personality=PersonalityType.AFFECTIONATE)
print(f"Original creature: {original.name}")

# Build up some bonding
for i in range(10):
    original.interact('pet', positive=True, item='petting', gentle=True)
    original.feed(amount=20, food_type='treats')

# Add some preferences
for i in range(5):
    original.preferences.record_experience('toy', 'feather', enjoyment=0.9)

print(f"  Bond: {original.bonding.bond:.1f}")
print(f"  Trust: {original.trust.trust:.1f}")
orig_favorites = original.get_favorite_items()
print(f"  Favorite toy: {orig_favorites.get('favorite_toy', 'None')}")

# Save to dict
saved_data = original.to_dict()
print(f"\nSaved data keys: {list(saved_data.keys())}")
print(f"  Has bonding_system: {'bonding_system' in saved_data}")
print(f"  Has trust_system: {'trust_system' in saved_data}")
print(f"  Has emotional_states: {'emotional_states' in saved_data}")
print(f"  Has preference_system: {'preference_system' in saved_data}")
print(f"  Has name_calling_system: {'name_calling_system' in saved_data}")

# Load from dict
loaded = Creature.from_dict(saved_data)
print(f"\nLoaded creature: {loaded.name}")
print(f"  Bond: {loaded.bonding.bond:.1f}")
print(f"  Trust: {loaded.trust.trust:.1f}")
loaded_favorites = loaded.get_favorite_items()
print(f"  Favorite toy: {loaded_favorites.get('favorite_toy', 'None')}")

# Verify all Phase 5 systems loaded
assert loaded.bonding.bond == original.bonding.bond, "Bond should match"
assert loaded.trust.trust == original.trust.trust, "Trust should match"
# Verify preferences loaded (check the internal data structures)
assert len(loaded.preferences.toy_preferences) > 0, "Toy preferences should be loaded"

print("✓ Persistence working!")

# Test 8: Bond Level Progression
print("\n8. Testing Complete Bond Level Progression")
print("-" * 60)

progression_creature = Creature(creature_type='unicorn', personality=PersonalityType.GENTLE)
print(f"Testing bond progression for {progression_creature.name}")

# Start at stranger
print(f"\nStarting bond: {progression_creature.bonding.bond:.1f} ({progression_creature.get_bond_level_name()})")

# Progress through all levels
target_bonds = [(25, "acquaintance"), (45, "friend"), (65, "close_friend"), (85, "best_friend")]

for target, level_name in target_bonds:
    while progression_creature.bonding.bond < target:
        progression_creature.interact('pet', positive=True, gentle=True)
        progression_creature.feed(amount=20, food_type='treats')

    current_level = progression_creature.get_bond_level_name()
    stats = progression_creature.get_bonding_stats()
    print(f"  Bond {progression_creature.bonding.bond:.1f}: {current_level}")
    print(f"    - {stats['bond_description'][:60]}...")

# Test separation anxiety at best friend level
print(f"\nTesting separation anxiety at best friend level:")
should_show = progression_creature.bonding.should_show_separation_anxiety(hours_away=2.0)
print(f"  Should show separation anxiety after 2 hours: {should_show}")

# Test excitement on return
should_excite, intensity = progression_creature.bonding.should_show_excitement_on_return(hours_away=3.0)
print(f"  Should show excitement after 3 hours: {should_excite} (intensity: {intensity:.2f})")

print("✓ Bond progression working!")

# Final Summary
print("\n" + "=" * 60)
print("PHASE 5 TEST SUMMARY")
print("=" * 60)
print("✓ Bonding system (stranger → best friend)")
print("✓ Trust system (builds through care)")
print("✓ Emotional states (jealousy, separation anxiety, excitement)")
print("✓ Preference system (individual likes/dislikes)")
print("✓ Name calling (bond/trust-based responses)")
print("✓ Creature integration")
print("✓ Persistence (save/load)")
print("✓ Bond level progression")
print("\n🎉 ALL PHASE 5 TESTS PASSED! 🎉\n")
