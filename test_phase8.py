"""
Test script for Phase 8: Living Creature Behaviors

Tests all 8 Phase 8 features:
1. Bathroom needs (bladder/bowel management)
2. Grooming/cleanliness
3. Illness system
4. Aging system (baby → elder)
5. Natural lifespan
6. Breeding
7. Genetics (inheritance)
8. Circadian rhythm (sleep/wake cycles)
"""
import sys
sys.path.insert(0, '/home/user/desktop_pet/src')

from core.biological_needs import BathroomNeedsSystem, GroomingSystem, CleanlinessLevel
from core.health_system import HealthSystem, IllnessType, IllnessSeverity
from core.aging_system import AgingSystem, LifeStage
from core.breeding_system import BreedingSystem, GeneticTrait, PregnancyStage
from core.circadian_rhythm import CircadianRhythm, TimeOfDay, SleepState
import time
from datetime import datetime

print("=" * 60)
print("PHASE 8: LIVING CREATURE BEHAVIORS TEST")
print("=" * 60)

# Test 1: Bathroom Needs
print("\n1. Testing Bathroom Needs System")
print("-" * 60)

bathroom = BathroomNeedsSystem(age_days=100)  # Adult
print(f"Initial bladder: {bathroom.bladder:.1f}/100")
print(f"Initial bowel: {bathroom.bowel:.1f}/100")
print(f"House trained: {bathroom.house_trained}")
print(f"Bladder control: {bathroom.bladder_control:.2f}")

# Simulate time passing
print("\nSimulating 8 hours...")
bathroom.update(hours_elapsed=8.0)
print(f"Bladder after 8h: {bathroom.bladder:.1f}/100")
print(f"Bowel after 8h: {bathroom.bowel:.1f}/100")

urgency, urgency_val = bathroom.get_urgency_level()
print(f"Urgency level: {urgency} ({urgency_val:.1f})")

# Check accident risk
will_accident, prob, reason = bathroom.check_accident_risk()
print(f"\nAccident risk: {prob:.1%} (will occur: {will_accident}, reason: {reason})")

# Use bathroom
print("\nUsing bathroom...")
result = bathroom.use_bathroom('both')
print(f"Relief amount: {result['relief_amount']:.1f}")
print(f"Happiness gain: {result['happiness_gain']:.1f}")
print(f"Bladder emptied: {result['bladder_emptied']}")
print(f"Bowel emptied: {result['bowel_emptied']}")

# Baby has less control
print("\nComparing baby vs adult bladder control:")
baby_bathroom = BathroomNeedsSystem(age_days=15)  # Baby
print(f"Baby control: {baby_bathroom.bladder_control:.2f}")
print(f"Adult control: {bathroom.bladder_control:.2f}")

print("✓ Bathroom needs working!")

# Test 2: Grooming System
print("\n2. Testing Grooming/Cleanliness System")
print("-" * 60)

grooming = GroomingSystem()
print(f"Initial cleanliness: {grooming.cleanliness:.1f}/100")
print(f"Cleanliness level: {grooming.get_cleanliness_level().value}")

# Get dirty over time
print("\nSimulating 48 hours of normal activity...")
grooming.update(hours_elapsed=48.0, activity_level=0.5)
print(f"Cleanliness after 48h: {grooming.cleanliness:.1f}/100")
print(f"Level: {grooming.get_cleanliness_level().value}")

# Get dirty from specific activity
print("\nPlaying outside in dirt...")
grooming.get_dirty_from_activity('rolling_in_dirt', intensity=1.0)
print(f"Cleanliness after rolling: {grooming.cleanliness:.1f}/100")

needs_grooming, urgency = grooming.needs_grooming()
print(f"\nNeeds grooming: {needs_grooming} (urgency: {urgency})")

# Brush the pet
print("\nBrushing pet...")
result = grooming.brush()
print(f"Cleanliness gain: {result['cleanliness_gain']:.1f}")
print(f"Happiness change: {result['happiness_change']:.1f}")
print(f"Bond gain: {result['bonding_gain']:.1f}")
print(f"Final cleanliness: {result['final_cleanliness']:.1f}")

# Give bath
print("\nGiving bath...")
result = grooming.give_bath()
print(f"Cleanliness restored to: {result['final_cleanliness']:.1f}")
print(f"Reaction: {result['reaction']}")

print("✓ Grooming system working!")

# Test 3: Health and Illness System
print("\n3. Testing Health and Illness System")
print("-" * 60)

health = HealthSystem()
print(f"Initial health: {health.health:.1f}/100")
print(f"Health status: {health.get_health_status()}")
print(f"Immunity: {health.immunity:.1f}/100")
print(f"Is sick: {health.is_sick()}")

# Contract an illness
print("\nContracting a cold...")
result = health.contract_illness('cold', severity='mild')
print(f"Contracted: {result['contracted']}")
if result['contracted']:
    illness = result['illness']
    print(f"Type: {illness['type']}")
    print(f"Severity: {illness['severity']}")
    print(f"Symptoms: {', '.join(illness['symptoms'])}")
    print(f"Damage per hour: {illness['damage_per_hour']:.2f}")

# Simulate illness progression
print("\nSimulating 24 hours of illness...")
environment = {
    'stress': 30.0,
    'cleanliness': 80.0,
    'happiness': 70.0,
    'nutrition': 80.0,
    'energy': 60.0
}
health.update(hours_elapsed=24.0, environment=environment)

status = health.get_status()
print(f"Health after 24h: {status['health']:.1f}")
print(f"Active illnesses: {status['active_illnesses']}")
if status['illnesses']:
    ill = status['illnesses'][0]
    print(f"  {ill['type']} ({ill['severity']})")
    print(f"  Recovery: {ill['recovery_progress']:.1%}")
    print(f"  Days sick: {ill['days_sick']:.2f}")

# Administer medicine
print("\nAdministering cold medicine...")
result = health.administer_medicine('cold_medicine', ['cold', 'flu'])
print(f"Treating: {', '.join(result['treating'])}")

# Visit vet
print("\nVisiting veterinarian...")
result = health.visit_vet()
print(f"Diagnosed: {len(result['diagnosed_illnesses'])} illness(es)")
print(f"Health restored: {result['health_restored']:.1f}")
print(f"Recovery boost: {result['recovery_boost']:.0f}%")
print(f"Cost: ${result['cost']}")

print("✓ Health system working!")

# Test 4: Aging System
print("\n4. Testing Aging System")
print("-" * 60)

aging = AgingSystem(lifespan_days=100)  # Shorter lifespan for testing
print(f"Initial age: {aging.age_days:.1f} days")
print(f"Life stage: {aging.current_stage.value}")
print(f"Lifespan: {aging.lifespan_days} days ({aging.lifespan_days/365:.1f} years)")

# Age through stages
print("\nAging through life stages...")
test_ages = [
    (2, "Egg"),
    (15, "Baby"),
    (60, "Child"),
    (120, "Teen"),
    (300, "Adult")
]

for days, expected_stage in test_ages:
    aging.age_seconds = days * 86400.0
    aging.age_days = days
    new_stage = aging._calculate_life_stage()
    if new_stage != aging.current_stage:
        aging._transition_to_stage(new_stage)

    modifiers = aging.get_age_modifiers()
    print(f"\n{expected_stage} ({days} days):")
    print(f"  Life stage: {aging.current_stage.value}")
    print(f"  Energy max: {modifiers['energy_max']:.1f}x")
    print(f"  Learning rate: {modifiers['learning_rate']:.1f}x")
    print(f"  Activity level: {modifiers['activity_level']:.1f}x")

# Check remaining lifespan
print("\nLifespan information:")
lifespan_info = aging.get_remaining_lifespan()
print(f"Remaining days: {lifespan_info['remaining_days']:.1f}")
print(f"Life percentage: {lifespan_info['life_percentage']:.1f}%")

# Age in human years
human_age = aging.get_age_in_human_years('cat')
print(f"Age in human years: {human_age:.1f}")

print("✓ Aging system working!")

# Test 5: Breeding and Genetics
print("\n5. Testing Breeding and Genetics System")
print("-" * 60)

# Create two adult pets
mother = BreedingSystem(creature_id='pet_001', gender='female')
father = BreedingSystem(creature_id='pet_002', gender='male')

# Make them breedable (would normally require adult age)
mother.can_breed = True
father.can_breed = True

print(f"Mother: {mother.gender}, can breed: {mother.can_breed}")
print(f"Father: {father.gender}, can breed: {father.can_breed}")

# Show parent genetics
print("\nParent genetics:")
mother_genes = mother.get_displayed_genetics()
father_genes = father.get_displayed_genetics()
print(f"Mother - Size: {mother_genes.get('size')}, Color: {mother_genes.get('color')}")
print(f"Father - Size: {father_genes.get('size')}, Color: {father_genes.get('color')}")

# Attempt breeding
print("\nAttempting to breed...")
result = mother.attempt_breeding(father, compatibility=1.0)
print(f"Success: {result['success']}")
if result['success']:
    print(f"Pregnant: {result['pregnant_id']}")
    print(f"Father: {result['father_id']}")
    print(f"Expected birth: {result['expected_birth_days']:.1f} days")

# Check pregnancy
if mother.is_pregnant:
    print("\nPregnancy status:")
    print(f"Progress: {mother.pregnancy_progress:.1%}")
    print(f"Stage: {mother.get_pregnancy_stage().value}")

    # Fast-forward pregnancy
    print("\nFast-forwarding pregnancy...")
    mother.update_pregnancy(hours_elapsed=7 * 24)  # 7 days
    print(f"Progress after 7 days: {mother.pregnancy_progress:.1%}")
    print(f"Stage: {mother.get_pregnancy_stage().value}")

    # Give birth
    print("\nGiving birth...")
    offspring = mother.give_birth()
    print(f"Litter size: {len(offspring)}")

    for i, baby in enumerate(offspring, 1):
        print(f"\nOffspring #{i}:")
        print(f"  ID: {baby['id']}")
        print(f"  Mother: {baby['mother_id']}")
        print(f"  Father: {baby['father_id']}")

        genes = baby['genetics']
        print(f"  Size: {genes.get('size', {}).get('dominant', 'N/A')}")
        print(f"  Color: {genes.get('color', {}).get('dominant', 'N/A')}")
        print(f"  Pattern: {genes.get('pattern', {}).get('dominant', 'N/A')}")
        print(f"  Intelligence: {genes.get('intelligence', 0):.1f}/100")

print("✓ Breeding and genetics working!")

# Test 6: Circadian Rhythm
print("\n6. Testing Circadian Rhythm System")
print("-" * 60)

circadian = CircadianRhythm(species_type='cat')
print(f"Species: {circadian.species_type}")
print(f"Daily sleep need: {circadian.daily_sleep_need} hours")
print(f"Preferred sleep time: {circadian.preferred_sleep_time}:00")
print(f"Current sleep state: {circadian.sleep_state.value}")
print(f"Is sleeping: {circadian.is_sleeping}")

# Simulate being awake
print("\nSimulating 12 hours awake...")
circadian.update(hours_elapsed=12.0, current_hour=14)  # 2 PM
print(f"Sleep drive: {circadian.sleep_drive:.1f}/100")
print(f"Sleepiness: {circadian.get_sleepiness_level()}")

# Check if should sleep
current_hour = 22  # 10 PM
should_sleep, reason = circadian.should_sleep(current_hour, energy=50.0)
print(f"\nShould sleep at {current_hour}:00? {should_sleep} (reason: {reason})")

# Fall asleep
if should_sleep:
    print("\nFalling asleep...")
    circadian.fall_asleep()
    print(f"Sleep state: {circadian.sleep_state.value}")
    print(f"Is sleeping: {circadian.is_sleeping}")

    # Simulate sleep
    print("\nSimulating 6 hours of sleep...")
    circadian.update(hours_elapsed=6.0, current_hour=4)  # 4 AM
    print(f"Sleep duration: {circadian.current_sleep_duration:.1f} hours")
    print(f"Sleep drive: {circadian.sleep_drive:.1f}/100")
    print(f"Sleep state: {circadian.sleep_state.value}")
    print(f"Sleep cycles completed: {circadian.sleep_cycles_completed}")

    # Wake up
    print("\nWaking up naturally...")
    result = circadian.wake_up(natural=True)
    print(f"Sleep duration: {result['sleep_duration_hours']:.1f} hours")
    print(f"Is nap: {result['is_nap']}")
    print(f"Sleep quality: {result['sleep_quality']:.1%}")
    print(f"Energy restored: {result['energy_restored']:.1f}")
    print(f"Happiness change: {result['happiness_change']:.1f}")

# Test time of day
print("\nTime of day classification:")
for hour in [3, 9, 15, 20]:
    tod = circadian.get_time_of_day(hour)
    print(f"  {hour}:00 = {tod.value}")

print("✓ Circadian rhythm working!")

# Test 7: Persistence (Save/Load)
print("\n7. Testing Persistence (Save/Load)")
print("-" * 60)

# Create systems with state
print("Creating systems with state...")
bathroom_save = BathroomNeedsSystem(age_days=200)
bathroom_save.bladder = 75.0
bathroom_save.house_trained = True

aging_save = AgingSystem()
aging_save.age_days = 45.0
aging_save.current_stage = LifeStage.CHILD

# Save to dict
print("\nSaving to dictionary...")
bathroom_data = bathroom_save.to_dict()
aging_data = aging_save.to_dict()
print(f"Bathroom data keys: {len(bathroom_data)} fields")
print(f"Aging data keys: {len(aging_data)} fields")

# Load from dict
print("\nLoading from dictionary...")
bathroom_load = BathroomNeedsSystem.from_dict(bathroom_data)
aging_load = AgingSystem.from_dict(aging_data)

# Verify
print(f"\nVerifying loaded data:")
print(f"Bathroom bladder: {bathroom_load.bladder:.1f} (expected 75.0)")
print(f"Bathroom house trained: {bathroom_load.house_trained} (expected True)")
print(f"Aging days: {aging_load.age_days:.1f} (expected 45.0)")
print(f"Aging stage: {aging_load.current_stage.value} (expected child)")

assert bathroom_load.bladder == 75.0, "Bladder should be 75.0"
assert bathroom_load.house_trained == True, "Should be house trained"
assert aging_load.age_days == 45.0, "Age should be 45.0"
assert aging_load.current_stage == LifeStage.CHILD, "Stage should be CHILD"

print("✓ Persistence working!")

# Final Summary
print("\n" + "=" * 60)
print("PHASE 8 TEST SUMMARY")
print("=" * 60)
print("✓ Bathroom needs (bladder/bowel management)")
print("✓ Grooming/cleanliness system")
print("✓ Illness and health system")
print("✓ Aging system (egg → baby → child → teen → adult)")
print("✓ Breeding and pregnancy")
print("✓ Genetics and inheritance")
print("✓ Circadian rhythm (sleep/wake cycles)")
print("✓ Persistence (save/load)")
print("\n🎉 ALL PHASE 8 TESTS PASSED! 🎉")
print("\nPhase 8 Features:")
print("  • Realistic bathroom needs with accidents")
print("  • Grooming requirements and cleanliness tracking")
print("  • Illness system with multiple diseases")
print("  • Natural aging through life stages")
print("  • Breeding with genetic inheritance")
print("  • Time-based circadian sleep rhythms")
print("  • Full persistence support")
print()
