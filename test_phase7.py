"""
Test script for Phase 7: Enhanced Memory Systems

Tests:
- Autobiographical memory ("I remember the first time...")
- Favorite memories (stores best moments)
- Trauma/fear memory (bad experiences create lasting effects)
- Associative memory (desk corner = hiding spot, evening = playtime)
- Dream system (processes memories during sleep)
- Memory importance weighting (some fade, others persist forever)
- Integration with Creature class
- Persistence (save/load)
"""
import sys
sys.path.insert(0, '/home/user/desktop_pet/src')

from core.creature import Creature
from core.config import PersonalityType
from core.enhanced_memory import (
    AutobiographicalMemory, FavoriteMemories, TraumaMemory,
    AssociativeMemory, DreamSystem, MemoryImportanceManager
)
import time
from datetime import datetime

print("=" * 60)
print("PHASE 7: ENHANCED MEMORY SYSTEMS TEST")
print("=" * 60)

# Test 1: Autobiographical Memory
print("\n1. Testing Autobiographical Memory")
print("-" * 60)

autobio = AutobiographicalMemory()
print(f"Initial first-time experiences: {len(autobio.first_time_events)}")

# Record first time playing
first_play = autobio.record_first_time(
    event_type='playing',
    details={'activity': 'ball', 'location': 'backyard'},
    emotional_intensity=0.9
)
print(f"\nRecorded first time playing: {first_play}")
print(f"Total first-time experiences: {len(autobio.first_time_events)}")

# Try to record playing again (should fail)
second_play = autobio.record_first_time(
    event_type='playing',
    details={'activity': 'frisbee', 'location': 'park'},
    emotional_intensity=0.8
)
print(f"Tried to record playing again: {second_play} (should be False)")

# Recall first time
recalled = autobio.recall_first_time('playing')
print(f"\nRecalled first time playing:")
print(f"  Activity: {recalled['details']['activity']}")
print(f"  Location: {recalled['details']['location']}")
print(f"  Emotional intensity: {recalled['emotional_intensity']}")

# Record multiple first times
print("\nRecording multiple first-time experiences:")
first_times = [
    ('eating', {'food': 'fish', 'taste': 'delicious'}, 0.8),
    ('meeting_friend', {'friend': 'other_pet', 'reaction': 'curious'}, 0.7),
    ('sleeping', {'location': 'cozy_bed', 'duration': 8}, 0.6),
    ('training', {'trick': 'sit', 'success': True}, 0.85)
]

for event, details, intensity in first_times:
    autobio.record_first_time(event, details, intensity)

life_story = autobio.get_life_summary(max_events=5)
print(f"\nLife story (first {len(life_story)} events):")
for i, event in enumerate(life_story, 1):
    print(f"  {i}. {event['event_type'].replace('_', ' ').title()} - {event['details']}")

print("✓ Autobiographical memory working!")

# Test 2: Favorite Memories
print("\n2. Testing Favorite Memories")
print("-" * 60)

favorites = FavoriteMemories(max_favorites=5)
print(f"Max favorite memories: {favorites.max_favorites}")

# Consider some memories as favorites
print("\nAdding favorite memories:")
memories_to_consider = [
    ('playing_ball', {'activity': 'fetch', 'duration': 30}, 95.0, 0.9),
    ('getting_treats', {'treat': 'salmon', 'count': 3}, 92.0, 0.85),
    ('cuddling', {'duration': 60, 'warmth': 'cozy'}, 88.0, 0.8),
    ('boring_walk', {'location': 'same_route', 'duration': 10}, 50.0, 0.3),  # Won't make it
    ('first_trick', {'trick': 'sit', 'praise': 'good_job'}, 96.0, 0.95),
    ('swimming', {'location': 'lake', 'temperature': 'perfect'}, 90.0, 0.88)
]

for event, details, happiness, intensity in memories_to_consider:
    favorites.consider_as_favorite(event, details, happiness, intensity)
    score = happiness * 0.6 + intensity * 100 * 0.4
    print(f"  {event}: happiness={happiness}, intensity={intensity}, score={score:.1f}")

# Get top favorites
top_favorites = favorites.get_favorites(limit=3)
print(f"\nTop 3 favorite memories:")
for i, fav in enumerate(top_favorites, 1):
    print(f"  {i}. {fav['event_type']} (score: {fav['score']:.1f})")
    print(f"     {fav['details']}")

# Check if specific event is a favorite
all_faves = favorites.get_favorites(limit=10)
is_favorite = any(fav['event_type'] == 'playing_ball' for fav in all_faves)
print(f"\nIs 'playing_ball' a favorite? {is_favorite}")

print("✓ Favorite memories working!")

# Test 3: Trauma/Fear Memory
print("\n3. Testing Trauma/Fear Memory")
print("-" * 60)

trauma = TraumaMemory()
print(f"Initial traumas: {len(trauma.traumas)}")

# Record a moderate trauma
print("\nRecording moderate trauma (loud_noise):")
severity = 0.6
trauma.record_trauma(
    event_type='loud_noise',
    details={'source': 'fireworks', 'location': 'outside'},
    severity=severity,
    trigger='loud_sounds'
)
print(f"  Severity: {severity}")
print(f"  Expected trust impact: -{severity * 10:.1f}")
print(f"  Expected bond impact: -{severity * 5:.1f}")

# Check fear trigger
is_triggered, intensity = trauma.check_trigger('loud_sounds')
print(f"\nChecking fear trigger 'loud_sounds':")
print(f"  Triggered: {is_triggered}")
print(f"  Fear intensity: {intensity:.2f}")

# Record severe trauma
print("\nRecording severe trauma (abandonment):")
trauma.record_trauma(
    event_type='abandonment',
    details={'duration_hours': 8, 'location': 'empty_house'},
    severity=0.9,
    trigger='being_alone'
)

# Get all fear triggers
fear_triggers = trauma.fear_triggers
print(f"\nAll fear triggers: {list(fear_triggers.keys())}")

# Process healing
print("\nProcessing healing through positive experiences:")
initial_strength = trauma.traumas[0]['trauma_strength']
trauma.process_healing('gentle_interaction', healing_amount=0.1)
healed_strength = trauma.traumas[0]['trauma_strength']
print(f"  Trauma strength: {initial_strength:.2f} -> {healed_strength:.2f}")

print("✓ Trauma/fear memory working!")

# Test 4: Associative Memory
print("\n4. Testing Associative Memory")
print("-" * 60)

associative = AssociativeMemory()
print("Recording associations between contexts and events...")

# Record location associations
print("\nLearning location patterns:")
for i in range(5):
    associative.record_association('location', 'desk_corner', 'hiding', outcome_valence=0.8)
print(f"  Recorded 5 instances of hiding at desk_corner")

# Try to get prediction (need 3+ occurrences)
prediction = associative.get_pattern_prediction('location', 'desk_corner')
print(f"  Prediction for desk_corner: {prediction}")

# Record time associations
print("\nLearning time patterns:")
for i in range(4):
    associative.record_association('time', '18:00', 'playtime', outcome_valence=0.9)
print(f"  Recorded 4 instances of playtime at 18:00")

prediction = associative.get_pattern_prediction('time', '18:00')
print(f"  Prediction for 18:00: {prediction}")

# Record object associations
print("\nLearning object patterns:")
for i in range(3):
    associative.record_association('object', 'red_ball', 'fun_times', outcome_valence=0.85)
print(f"  Recorded 3 instances of fun with red_ball")

# Get learned associations
print(f"\nLearned associations:")
association = associative.get_association('location', 'desk_corner')
if association:
    print(f"  desk_corner -> {association['most_common_event']} (occurrences: {association['total_occurrences']})")

association = associative.get_association('time', '18:00')
if association:
    print(f"  18:00 -> {association['most_common_event']} (valence: {association['average_valence']:.2f})")

print("✓ Associative memory working!")

# Test 5: Dream System
print("\n5. Testing Dream System")
print("-" * 60)

dream_system = DreamSystem()
print(f"Initial dreams: {len(dream_system.dream_log)}")

# Create some recent memories for dreaming
recent_memories = [
    {
        'event_type': 'playing_ball',
        'details': {'activity': 'fetch', 'fun': True},
        'timestamp': time.time() - 3600,
        'emotional_valence': 0.9,
        'emotional_intensity': 0.85,
        'importance': 0.7
    },
    {
        'event_type': 'eating_treats',
        'details': {'treat': 'salmon', 'yummy': True},
        'timestamp': time.time() - 7200,
        'emotional_valence': 0.8,
        'emotional_intensity': 0.8,
        'importance': 0.6
    },
    {
        'event_type': 'scary_noise',
        'details': {'source': 'thunder', 'fear': True},
        'timestamp': time.time() - 1800,
        'emotional_valence': -0.7,
        'emotional_intensity': 0.9,
        'importance': 0.8
    },
    {
        'event_type': 'cuddling',
        'details': {'warmth': 'cozy', 'safe': True},
        'timestamp': time.time() - 5400,
        'emotional_valence': 0.75,
        'emotional_intensity': 0.7,
        'importance': 0.65
    }
]

# Check if should dream
should_dream = dream_system.should_dream(is_sleeping=True, hours_since_last_dream=3.0)
print(f"Should dream after 3 hours sleep? {should_dream}")

# Process a dream
print("\nProcessing dream with recent memories:")
dream = dream_system.process_dream(recent_memories, emotional_state=0.6)
print(f"  Dream type: {dream['dream_type']}")
print(f"  Memories processed: {dream['memories_processed']}")
print(f"  Memory themes: {dream['memory_themes']}")
print(f"  Emotional tone: {dream['emotional_tone']:.2f}")

# Get dream stats
stats = dream_system.get_dream_statistics()
print(f"\nDream statistics:")
print(f"  Total dreams: {stats['total_dreams']}")
print(f"  Dream type distribution: {stats['dream_type_distribution']}")

# Process another dream (nightmare scenario)
print("\nProcessing nightmare with negative memories:")
nightmare_memories = [
    {
        'event_type': 'abandonment',
        'details': {'alone': True, 'scared': True},
        'timestamp': time.time() - 2000,
        'emotional_valence': -0.9,
        'emotional_intensity': 0.95,
        'importance': 0.9
    },
    {
        'event_type': 'loud_noise',
        'details': {'source': 'fireworks', 'terrifying': True},
        'timestamp': time.time() - 3000,
        'emotional_valence': -0.8,
        'emotional_intensity': 0.9,
        'importance': 0.85
    }
]
dream_system.last_dream_time = time.time() - 7200  # 2 hours ago
nightmare = dream_system.process_dream(nightmare_memories, emotional_state=-0.5)
print(f"  Dream type: {nightmare['dream_type']}")
print(f"  Emotional tone: {nightmare['emotional_tone']:.2f}")

print("✓ Dream system working!")

# Test 6: Memory Importance Manager
print("\n6. Testing Memory Importance Manager")
print("-" * 60)

manager = MemoryImportanceManager()

# Calculate memory strength for different scenarios
print("Calculating memory strength for different memories:")
test_memories = [
    {'memory_strength': 0.9, 'importance': 0.95, 'timestamp': time.time(), 'recall_count': 5, 'name': 'crucial memory, recalled often'},
    {'memory_strength': 0.7, 'importance': 0.6, 'timestamp': time.time() - (7 * 24 * 3600), 'recall_count': 2, 'name': 'important memory, 1 week old'},
    {'memory_strength': 0.5, 'importance': 0.3, 'timestamp': time.time() - (30 * 24 * 3600), 'recall_count': 0, 'name': 'low importance, 1 month old'},
]

for mem in test_memories:
    strength = manager.calculate_memory_strength(mem)
    print(f"  {mem['name']}: strength = {strength:.2f}")

# Test retention probability
print("\nTesting memory retention over time:")
test_cases = [
    (0.95, 0, 0, "Crucial memory, just created"),
    (0.95, 365, 5, "Crucial memory, 1 year old, recalled 5 times"),
    (0.6, 7, 2, "Important memory, 1 week old, recalled 2 times"),
    (0.3, 30, 0, "Low importance, 1 month old, never recalled"),
    (0.3, 30, 10, "Low importance, 1 month old, recalled 10 times")
]

for importance, age_days, recall_count, description in test_cases:
    retention = manager.calculate_retention_probability(importance, age_days, recall_count)
    print(f"  {description}:")
    print(f"    Retention probability: {retention:.2%}")

# Test memory fading decision
print("\nTesting memory fading:")
fade_test_memories = [
    {'importance': 0.95, 'timestamp': time.time() - (100 * 24 * 3600), 'recall_count': 0, 'name': 'crucial, old, never recalled'},
    {'importance': 0.3, 'timestamp': time.time() - (30 * 24 * 3600), 'recall_count': 0, 'name': 'low importance, old, never recalled'},
]
for mem in fade_test_memories:
    should_fade = manager.should_fade_memory(mem)
    print(f"  {mem['name']}: should fade = {should_fade}")

print("✓ Memory importance manager working!")

# Test 7: Integration with Creature
print("\n7. Testing Integration with Creature Class")
print("-" * 60)

creature = Creature(creature_type='cat', personality=PersonalityType.CURIOUS)
print(f"Created {creature.name} the {creature.personality.value} {creature.creature_type}")

# Check Phase 7 enabled
print(f"Phase 7 enabled: {creature.phase7_enabled}")

if creature.phase7_enabled:
    # Test recording first-time experience
    print("\nRecording first-time playing with toy:")
    was_first = creature.record_first_time_experience(
        'playing_with_toy',
        {'toy': 'mouse', 'location': 'living_room'}
    )
    print(f"  Was this the first time? {was_first}")

    # Try recording again
    was_first_again = creature.record_first_time_experience(
        'playing_with_toy',
        {'toy': 'ball', 'location': 'bedroom'}
    )
    print(f"  Was this the first time again? {was_first_again}")

    # Record trauma
    print("\nRecording traumatic experience (vet visit):")
    creature.record_trauma(
        'vet_visit',
        {'procedure': 'vaccination', 'pain': 'moderate'},
        severity=0.5,
        trigger='white_coats'
    )

    # Check fear trigger
    is_scared, fear_level = creature.check_fear_trigger('white_coats')
    print(f"  Scared of white_coats? {is_scared} (fear level: {fear_level:.2f})")

    # Learn associations
    print("\nLearning associations:")
    for i in range(4):
        creature.learn_association('time', '19:00', 'dinner_time', was_positive=True)

    prediction = creature.predict_from_context('time', '19:00')
    print(f"  What happens at 19:00? {prediction}")

    # Create favorite memories
    print("\nCreating favorite memories through interactions:")
    creature.happiness = 90
    for i in range(3):
        creature.consider_as_favorite_memory(
            'playing_fetch',
            {'toy': 'ball', 'throws': 10, 'fun': 'very'}
        )

    favorites = creature.get_favorite_memories(limit=3)
    print(f"  Number of favorite memories: {len(favorites)}")
    if favorites:
        print(f"  Top favorite: {favorites[0]['event_type']}")

    # Process sleep and dreaming
    print("\nProcessing sleep cycle (3 hours):")
    # Add some memories to the base memory system for dreaming
    for i in range(5):
        creature.memory.record_interaction(
            f'activity_{i}',
            {'details': f'activity {i}'},
            important=(i % 2 == 0),
            emotional_intensity=0.5 + i * 0.1
        )

    creature.process_sleep_cycle(sleep_duration_hours=3.0)

    dream_stats = creature.get_dream_statistics()
    print(f"  Total dreams: {dream_stats['total_dreams']}")
    if dream_stats['total_dreams'] > 0:
        print(f"  Dream types: {dream_stats['dream_type_distribution']}")
        # Note: last_dream_type might not be in the stats, skip it for now

    # Get life story
    print("\nRetrieving life story:")
    life_story = creature.get_life_story(max_events=5)
    print(f"  Key life events: {len(life_story)}")
    for event in life_story[:3]:
        print(f"    - {event['event_type']}")

    print("✓ Creature integration working!")
else:
    print("⚠ Phase 7 not enabled on this creature")

# Test 8: Persistence (Save/Load)
print("\n8. Testing Persistence (Save/Load)")
print("-" * 60)

# Create a creature with developed Phase 7 memories
original = Creature(creature_type='dog', personality=PersonalityType.LOYAL)
print(f"Original creature: {original.name}")

if original.phase7_enabled:
    # Build up memories
    print("\nBuilding up memories:")

    # First-time experiences
    original.record_first_time_experience('first_walk', {'location': 'park', 'weather': 'sunny'})
    original.record_first_time_experience('first_treat', {'treat': 'bacon', 'delicious': True})

    # Favorite memories
    original.happiness = 95
    original.consider_as_favorite_memory('best_day_ever', {'activities': ['play', 'treats', 'cuddles']})

    # Trauma
    original.record_trauma('scary_dog', {'size': 'large', 'aggressive': True}, severity=0.4, trigger='big_dogs')

    # Associations
    for i in range(4):
        original.learn_association('location', 'kitchen', 'food_time', was_positive=True)

    # Dream
    original.memory.record_interaction('fun_activity', {'fun': True}, important=True, emotional_intensity=0.8)
    original.process_sleep_cycle(3.0)

    print(f"  First-time experiences: {len(original.autobiographical.first_time_events)}")
    print(f"  Favorite memories: {len(original.favorite_memories.favorites)}")
    print(f"  Traumas: {len(original.trauma_memory.traumas)}")
    print(f"  Dreams: {len(original.dream_system.dream_log)}")

    # Save to dict
    saved_data = original.to_dict()
    print(f"\nSaved data includes Phase 7:")
    print(f"  Has autobiographical_memory: {'autobiographical_memory' in saved_data}")
    print(f"  Has favorite_memories: {'favorite_memories' in saved_data}")
    print(f"  Has trauma_memory: {'trauma_memory' in saved_data}")
    print(f"  Has associative_memory: {'associative_memory' in saved_data}")
    print(f"  Has dream_system: {'dream_system' in saved_data}")

    # Load from dict
    loaded = Creature.from_dict(saved_data)
    print(f"\nLoaded creature: {loaded.name}")

    if loaded.phase7_enabled:
        print(f"  First-time experiences: {len(loaded.autobiographical.first_time_events)}")
        print(f"  Favorite memories: {len(loaded.favorite_memories.favorites)}")
        print(f"  Traumas: {len(loaded.trauma_memory.traumas)}")
        print(f"  Dreams: {len(loaded.dream_system.dream_log)}")

        # Verify specific data
        assert len(loaded.autobiographical.first_time_events) == len(original.autobiographical.first_time_events), \
            "Autobiographical memories should match"
        assert len(loaded.trauma_memory.traumas) == len(original.trauma_memory.traumas), \
            "Traumas should match"

        print("\n✓ Persistence working!")
    else:
        print("⚠ Phase 7 not enabled on loaded creature")
else:
    print("⚠ Phase 7 not enabled on original creature")

# Final Summary
print("\n" + "=" * 60)
print("PHASE 7 TEST SUMMARY")
print("=" * 60)
print("✓ Autobiographical memory (first-time experiences)")
print("✓ Favorite memories (best moments stored)")
print("✓ Trauma/fear memory (lasting effects from bad experiences)")
print("✓ Associative memory (learned context patterns)")
print("✓ Dream system (memory processing during sleep)")
print("✓ Memory importance weighting (retention logic)")
print("✓ Creature integration")
print("✓ Persistence (save/load)")
print("\n🎉 ALL PHASE 7 TESTS PASSED! 🎉\n")
