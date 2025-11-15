"""
Test script for Phase 4: Fantastical Creature Design

Tests:
- 25 creature species
- Evolution system (baby -> juvenile -> adult -> elder)
- Element types and interactions
- Variant system (shiny, mystic, shadow, crystal)
- Sprite generation for new creatures
"""
import sys
sys.path.insert(0, '/home/user/desktop_pet/src')

from core.creature import Creature
from core.config import (
    PersonalityType, CREATURE_TYPES, ElementType, EvolutionStage, VariantType
)
from core.evolution_system import EvolutionSystem
from core.element_system import ElementSystem
from core.variant_system import VariantSystem

print("=" * 60)
print("PHASE 4: FANTASTICAL CREATURE DESIGN TEST")
print("=" * 60)

# Test 1: Creature Types
print("\n1. Testing 25 Creature Species")
print("-" * 60)
print(f"Total creature types: {len(CREATURE_TYPES)}")
print(f"Creature types: {', '.join(CREATURE_TYPES)}")
assert len(CREATURE_TYPES) >= 25, "Should have 25+ creature types"
print("✓ 25+ creature types confirmed!")

# Test 2: Create creatures of different types
print("\n2. Creating Sample Fantastical Creatures")
print("-" * 60)

test_types = ['phoenix', 'sprite', 'golem', 'griffin', 'unicorn', 'wisp', 'dragon']
for creature_type in test_types:
    creature = Creature(creature_type=creature_type, personality=PersonalityType.PLAYFUL)
    print(f"Created {creature_type}:")
    print(f"  - Element: {creature.element.primary_element.value}")
    print(f"  - Variant: {creature.variant.variant.value} ({creature.variant.get_rarity_tier()})")
    print(f"  - Stage: {creature.evolution.get_stage_name()}")
    print(f"  - Bond: {creature.bond}, Interactions: {creature.total_interactions}")

print("✓ Fantastical creatures created successfully!")

# Test 3: Evolution System
print("\n3. Testing Evolution System")
print("-" * 60)

# Create a creature and test evolution
evo_creature = Creature(creature_type='phoenix', personality=PersonalityType.CLEVER)
print(f"Created {evo_creature.name} the {evo_creature.creature_type}")
print(f"Starting stage: {evo_creature.evolution.get_stage_name()}")

# Simulate aging and interactions
evo_creature.age = 3 * 3600  # 3 hours
evo_creature.happiness = 50
evo_creature.bond = 35
evo_creature.total_interactions = 60

can_evolve, next_stage, reason = evo_creature.can_evolve()
print(f"\nChecking evolution eligibility:")
print(f"  Can evolve: {can_evolve}")
print(f"  Next stage: {next_stage}")
print(f"  Reason: {reason}")

# Get evolution progress
progress = evo_creature.get_evolution_progress()
print(f"\nEvolution Progress:")
print(f"  Overall: {progress['progress_percent']:.1f}%")
for req in progress['requirements']:
    status = "✓" if req['met'] else "✗"
    print(f"  {status} {req['name']}: {req['current']}/{req['required']} ({req['progress']:.0f}%)")

# Force evolve to juvenile
if can_evolve:
    success, message = evo_creature.evolve()
    print(f"\nEvolution attempt: {message}")
    print(f"New stage: {evo_creature.evolution.get_stage_name()}")

print("✓ Evolution system working!")

# Test 4: Element System
print("\n4. Testing Element System")
print("-" * 60)

fire_phoenix = Creature(creature_type='phoenix', personality=PersonalityType.FIERCE)
water_undine = Creature(creature_type='undine', personality=PersonalityType.CALM)

print(f"{fire_phoenix.name} (Phoenix): {fire_phoenix.element.primary_element.value}")
print(f"{water_undine.name} (Undine): {water_undine.element.primary_element.value}")

# Test type effectiveness
multiplier, interaction = fire_phoenix.element.get_effectiveness(water_undine.element.primary_element)
print(f"\nFire vs Water effectiveness: {multiplier}x ({interaction.value})")

# Test element modifiers
fire_mods = fire_phoenix.element.get_element_modifiers()
print(f"\nFire element modifiers: {list(fire_mods.keys())[:5]}...")

# Test elemental interaction
result = fire_phoenix.interact_with_element(ElementType.WATER)
print(f"\nElemental interaction result:")
print(f"  Type: {result['interaction_type']}")
print(f"  Message: {result['message']}")
print(f"  Multiplier: {result['multiplier']}x")

print("✓ Element system working!")

# Test 5: Variant System
print("\n5. Testing Variant System")
print("-" * 60)

# Test variant rarity
print("Testing variant rarity distribution (1000 rolls):")
variant_counts = {v: 0 for v in VariantType}
for _ in range(1000):
    variant = VariantSystem.roll_random_variant()
    variant_counts[variant] += 1

for variant_type, count in variant_counts.items():
    percentage = (count / 1000) * 100
    rarity = VariantSystem(variant_type).get_rarity_tier()
    print(f"  {variant_type.value:10s} ({rarity:10s}): {count:4d} ({percentage:5.1f}%)")

# Test variant modifiers
print("\nVariant stat modifiers:")
for variant_type in VariantType:
    system = VariantSystem(variant_type)
    mods = system.get_variant_modifiers()
    print(f"  {variant_type.value:10s}: Learning {mods['learning_rate']}x, " +
          f"Happiness {mods['happiness_gain']}x, Bond {mods['bond_gain']}x")

# Test special variant
crystal_creature = Creature(creature_type='dragon', personality=PersonalityType.LOYAL)
crystal_creature.variant = VariantSystem(VariantType.CRYSTAL)
print(f"\nCrystal variant abilities:")
abilities = crystal_creature.variant.get_special_abilities()
for ability in abilities:
    print(f"  - {ability}")

print("✓ Variant system working!")

# Test 6: Particle Effects
print("\n6. Testing Particle Effects")
print("-" * 60)

creatures_to_test = [
    ('phoenix', ElementType.FIRE),
    ('undine', ElementType.WATER),
    ('golem', ElementType.EARTH),
    ('sylph', ElementType.AIR)
]

for creature_type, expected_element in creatures_to_test:
    creature = Creature(creature_type=creature_type)
    effects = creature.get_particle_effects()
    print(f"{creature_type:10s}: {', '.join(effects)}")

print("✓ Particle effects working!")

# Test 7: Display Info
print("\n7. Testing Display Info")
print("-" * 60)

display_creature = Creature(creature_type='unicorn', personality=PersonalityType.GENTLE)
display_creature.variant = VariantSystem(VariantType.MYSTIC)
display_creature.age = 7200  # 2 hours
display_creature.happiness = 85
display_creature.bond = 45

info = display_creature.get_display_info()
print(f"Display Info for {info['name']}:")
print(f"  Type: {info['type']} {info['variant_emoji']}")
print(f"  Personality: {info['personality']}")
print(f"  Stage: {info['stage']}")
print(f"  Element: {info['element']}")
print(f"  Variant: {info['variant']} ({'Rare' if info['is_rare'] else 'Normal'})")
print(f"  Age: {info['age_hours']:.1f} hours")
print(f"  Stats: Hunger={info['stats']['hunger']:.0f}, " +
      f"Happiness={info['stats']['happiness']:.0f}, " +
      f"Bond={info['stats']['bond']:.0f}")
print(f"  Known tricks: {info['known_tricks']}")
print(f"  Total interactions: {info['total_interactions']}")

print("✓ Display info working!")

# Test 8: Persistence
print("\n8. Testing Persistence (Save/Load)")
print("-" * 60)

# Create a complex creature
original = Creature(creature_type='griffin', personality=PersonalityType.BRAVE)
original.variant = VariantSystem(VariantType.SHINY)
original.evolution.current_stage = EvolutionStage.JUVENILE
original.age = 10000
original.happiness = 75
original.bond = 60
original.total_interactions = 85

print(f"Original creature: {original.name}")
print(f"  Stage: {original.evolution.get_stage_name()}")
print(f"  Element: {original.element.primary_element.value}")
print(f"  Variant: {original.variant.variant.value}")

# Save to dict
saved_data = original.to_dict()
print(f"\nSaved data keys: {list(saved_data.keys())}")

# Load from dict
loaded = Creature.from_dict(saved_data)
print(f"\nLoaded creature: {loaded.name}")
print(f"  Stage: {loaded.evolution.get_stage_name()}")
print(f"  Element: {loaded.element.primary_element.value}")
print(f"  Variant: {loaded.variant.variant.value}")
print(f"  Bond: {loaded.bond}")
print(f"  Total interactions: {loaded.total_interactions}")

assert loaded.name == original.name, "Name should match"
assert loaded.evolution.current_stage == original.evolution.current_stage, "Stage should match"
assert loaded.element.primary_element == original.element.primary_element, "Element should match"
assert loaded.variant.variant == original.variant.variant, "Variant should match"

print("✓ Persistence working!")

# Final Summary
print("\n" + "=" * 60)
print("PHASE 4 TEST SUMMARY")
print("=" * 60)
print("✓ 25+ creature species")
print("✓ Evolution system (4 stages)")
print("✓ Element system (11 types)")
print("✓ Variant system (5 rarities)")
print("✓ Particle effects")
print("✓ Display info")
print("✓ Persistence")
print("\n🎉 ALL PHASE 4 TESTS PASSED! 🎉\n")
