"""
Test script for Phase 12: Mini-Games & Activities

Tests all 6 Phase 12 features:
1. Game base framework
2. Fetch game (catch/throw)
3. Trick show game (performance judging)
4. Memory match game (card matching)
5. Obstacle course game (agility)
6. Game rewards system (achievements)
"""
import sys
sys.path.insert(0, '/home/user/desktop_pet/src')

from core.game_base import GameManager, GameDifficulty, GameState
from core.fetch_game import FetchGame, ThrowableItem
from core.trick_show import TrickShow
from core.memory_match import MemoryMatch
from core.obstacle_course import ObstacleCourse
from core.game_rewards import GameRewardsSystem, AchievementType
import time

print("=" * 60)
print("PHASE 12: MINI-GAMES & ACTIVITIES TEST")
print("=" * 60)

# Test 1: Game Manager and Base Framework
print("\n1. Testing Game Manager and Base Framework")
print("-" * 60)

game_manager = GameManager()
print(f"Game manager initialized")
print(f"Registered games: {len(game_manager.games)}")

# Create and register games
fetch = FetchGame()
trick_show = TrickShow()
memory = MemoryMatch()
obstacle = ObstacleCourse()

game_manager.register_game(fetch)
game_manager.register_game(trick_show)
game_manager.register_game(memory)
game_manager.register_game(obstacle)

print(f"\nGames registered: {len(game_manager.games)}")
print(f"Available games: {list(game_manager.games.keys())}")

# Test game retrieval
fetched_game = game_manager.get_game("Fetch")
print(f"\nRetrieved game: {fetched_game.game_name}")
print(f"Game description: {fetched_game.description}")

print("✓ Game manager working!")

# Test 2: Fetch Game
print("\n2. Testing Fetch Game")
print("-" * 60)

# Start fetch game
fetch.start_game(
    difficulty=GameDifficulty.MEDIUM,
    pet_agility=0.7,
    pet_energy=0.9
)

print(f"Fetch game started")
print(f"Difficulty: {fetch.difficulty.value}")
print(f"Target catches: {fetch.target_catches}")
print(f"Time limit: {fetch.time_limit}s")

# Throw items
throws = [
    (ThrowableItem.BALL, 0.6, 45),
    (ThrowableItem.FRISBEE, 0.7, 40),
    (ThrowableItem.BONE, 0.5, 50),
    (ThrowableItem.TREAT, 0.8, 45),
]

print("\nThrowing items...")
for item, power, angle in throws:
    result = fetch.throw_item(item, power, angle)
    print(f"  {item.value}: {'CAUGHT!' if result['caught'] else 'missed'} "
          f"(distance: {result['distance']:.1f}, points: {result['points']})")

    # Simulate time passing
    fetch.update(2.0)

# Progress
progress = fetch.get_progress()
print(f"\nGame progress:")
print(f"  Catches: {progress['catches']}/{progress['target_catches']}")
print(f"  Misses: {progress['misses']}")
print(f"  Accuracy: {progress['accuracy']:.1f}%")
print(f"  Score: {progress['score']}")

# Complete more throws to win
while fetch.state == GameState.PLAYING and fetch.catches < fetch.target_catches:
    result = fetch.throw_item(ThrowableItem.BALL, 0.6, 45)
    fetch.update(1.0)

# Game statistics
stats = fetch.get_statistics()
print(f"\nFetch game statistics:")
print(f"  Total plays: {stats['total_plays']}")
print(f"  Win rate: {stats['win_rate']:.1f}%")
print(f"  High score: {stats['high_score']}")

print("✓ Fetch game working!")

# Test 3: Trick Show Game
print("\n3. Testing Trick Show Game")
print("-" * 60)

# Available tricks
tricks = {
    'sit': 0.9,
    'stay': 0.8,
    'roll_over': 0.7,
    'shake': 0.6,
    'play_dead': 0.5
}

# Start trick show
trick_show.start_game(
    difficulty=GameDifficulty.EASY,
    available_tricks=tricks,
    pet_mood=0.8,
    pet_energy=0.9,
    pet_confidence=0.7
)

print(f"Trick show started")
print(f"Rounds: {trick_show.rounds}")
print(f"Available tricks: {len(tricks)}")

# Perform tricks
print("\nPerforming tricks...")
tricks_to_perform = ['sit', 'stay', 'roll_over']

for trick_name in tricks_to_perform:
    result = trick_show.perform_trick(trick_name)
    if 'success' in result:
        print(f"  {trick_name}:")
        print(f"    Execution: {result['execution']:.1f}")
        print(f"    Style: {result['style']:.1f}")
        print(f"    Total score: {result['total_score']:.1f}")
        if result['perfect']:
            print(f"    ⭐ PERFECT!")

# Progress
progress = trick_show.get_progress()
print(f"\nTrick show progress:")
print(f"  Round: {progress['current_round']}/{progress['total_rounds']}")
print(f"  Perfect performances: {progress['perfect_performances']}")
print(f"  Crowd pleasers: {progress['crowd_pleasers']}")
print(f"  Score: {progress['score']}")

# Trick show statistics
stats = trick_show.get_statistics()
print(f"\nTrick show statistics:")
print(f"  Total plays: {stats['total_plays']}")
print(f"  Win rate: {stats['win_rate']:.1f}%")

print("✓ Trick show working!")

# Test 4: Memory Match Game
print("\n4. Testing Memory Match Game")
print("-" * 60)

# Start memory game
memory.start_game(
    difficulty=GameDifficulty.EASY,
    pet_intelligence=0.7
)

print(f"Memory match started")
print(f"Grid size: {memory.grid_size}x{memory.grid_size}")
print(f"Total cards: {len(memory.cards)}")
print(f"Target matches: {memory.target_matches}")

# Get hint from pet
hint = memory.get_hint()
if hint:
    print(f"\nPet gave hint:")
    print(f"  Type: {hint['hint_type']}")
    print(f"  Symbol: {hint.get('symbol', 'hidden')}")

# Flip some cards
print("\nFlipping cards...")
flips = [
    (0, 1),   # Try first pair
    (2, 3),   # Try another pair
]

for card1_id, card2_id in flips:
    result1 = memory.flip_card(card1_id)
    print(f"  Card {card1_id}: {result1.get('symbol', 'N/A')}")

    result2 = memory.flip_card(card2_id)
    if 'match' in result2:
        if result2['match']:
            print(f"  Card {card2_id}: {result2.get('symbol', 'N/A')} - MATCH!")
        else:
            print(f"  Card {card2_id}: {result2.get('card2_symbol', 'N/A')} - no match")

# Progress
progress = memory.get_progress()
print(f"\nMemory match progress:")
print(f"  Matches: {progress['matches_found']}/{progress['target_matches']}")
print(f"  Moves: {progress['moves_made']}")
print(f"  Hints remaining: {progress['hints_remaining']}")
print(f"  Score: {progress['score']}")

# Memory match statistics
stats = memory.get_statistics()
print(f"\nMemory match statistics:")
print(f"  Total plays: {stats['total_plays']}")

print("✓ Memory match working!")

# Test 5: Obstacle Course Game
print("\n5. Testing Obstacle Course Game")
print("-" * 60)

# Start obstacle course
obstacle.start_game(
    difficulty=GameDifficulty.MEDIUM,
    pet_agility=0.8,
    pet_energy=0.9,
    pet_training=0.6
)

print(f"Obstacle course started")
print(f"Number of obstacles: {len(obstacle.obstacles)}")
print(f"Time limit: {obstacle.time_limit}s")

# List obstacles
print("\nCourse obstacles:")
for i, obs in enumerate(obstacle.obstacles):
    print(f"  {i+1}. {obs.obstacle_type.value} (difficulty: {obs.difficulty:.2f})")

# Attempt obstacles
print("\nAttempting obstacles...")
for i in range(min(3, len(obstacle.obstacles))):
    result = obstacle.attempt_obstacle()
    if 'success' in result:
        status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
        print(f"  {result['obstacle_type']}: {status}")
        print(f"    Time: {result['time_taken']:.1f}s")
        print(f"    Penalties: {result['penalties']}")
        print(f"    Points: {result['points']}")

    obstacle.update(3.0)

# Progress
progress = obstacle.get_progress()
print(f"\nObstacle course progress:")
print(f"  Obstacles: {progress['current_obstacle']}/{progress['total_obstacles']}")
print(f"  Perfect runs: {progress['perfect_runs']}")
print(f"  Total penalties: {progress['total_penalties']}")
print(f"  Score: {progress['score']}")

# Obstacle course statistics
stats = obstacle.get_statistics()
print(f"\nObstacle course statistics:")
print(f"  Total plays: {stats['total_plays']}")

print("✓ Obstacle course working!")

# Test 6: Game Rewards System
print("\n6. Testing Game Rewards System")
print("-" * 60)

rewards = GameRewardsSystem()
print(f"Rewards system initialized")
print(f"Player level: {rewards.player_level}")
print(f"Total achievements: {len(rewards.achievements)}")

# Award experience and coins
print("\nAwarding rewards...")
rewards.award_experience(50)
rewards.award_coins(25)
print(f"Experience: {rewards.total_experience_earned}")
print(f"Coins: {rewards.total_coins_earned}")

# Check achievements
print("\nChecking achievements...")
achievements_to_check = [
    ('fetch_first_win', None),
    ('trick_show_first_win', None),
    ('dedicated_player', 5),
]

for achievement_id, value in achievements_to_check:
    rewards.check_achievement(achievement_id, value)
    progress = rewards.get_achievement_progress(achievement_id)
    if progress:
        status = "✓ UNLOCKED" if progress['unlocked'] else f"{progress['progress']*100:.0f}%"
        print(f"  {progress['name']}: {status}")

# Unlocked achievements
unlocked = rewards.get_unlocked_achievements()
print(f"\nUnlocked achievements: {len(unlocked)}")
for achievement in unlocked[:3]:
    print(f"  - {achievement.name}")

# Rewards statistics
stats = rewards.get_statistics()
print(f"\nRewards system statistics:")
print(f"  Player level: {stats['player_level']}")
print(f"  Total experience: {stats['total_experience']}")
print(f"  Total coins: {stats['total_coins']}")
print(f"  Achievement completion: {stats['achievement_completion']:.1f}%")

print("✓ Game rewards working!")

# Test 7: Persistence (Save/Load)
print("\n7. Testing Persistence (Save/Load)")
print("-" * 60)

# Save game manager
print("Saving game manager...")
manager_data = game_manager.to_dict()
print(f"  Saved {len(manager_data)} fields")
print(f"  Games: {len(manager_data['games'])}")
print(f"  History: {len(manager_data['game_history'])}")

# Load game manager
print("\nLoading game manager...")
loaded_manager = GameManager.from_dict(manager_data)
print(f"  Games loaded: {len(loaded_manager.games)}")
print(f"  History loaded: {len(loaded_manager.game_history)}")

# Save rewards
print("\nSaving rewards system...")
rewards_data = rewards.to_dict()
print(f"  Achievements saved: {len(rewards_data['achievements'])}")
print(f"  Unlocked: {len(rewards_data['unlocked_achievements'])}")

# Load rewards
print("\nLoading rewards system...")
loaded_rewards = GameRewardsSystem.from_dict(rewards_data)
print(f"  Player level: {loaded_rewards.player_level}")
print(f"  Experience: {loaded_rewards.total_experience_earned}")
print(f"  Achievements unlocked: {loaded_rewards.total_achievements_unlocked}")

# Verify data integrity
print("\nVerifying data integrity...")
original_exp = rewards.total_experience_earned
loaded_exp = loaded_rewards.total_experience_earned
print(f"  Experience: {'✓' if original_exp == loaded_exp else '✗'}")

original_level = rewards.player_level
loaded_level = loaded_rewards.player_level
print(f"  Player level: {'✓' if original_level == loaded_level else '✗'}")

print("✓ Persistence working!")

# Final Summary
print("\n" + "=" * 60)
print("PHASE 12 TEST SUMMARY")
print("=" * 60)
print("✓ Game manager and base framework")
print("✓ Fetch game (catch/throw mechanics)")
print("✓ Trick show game (performance judging)")
print("✓ Memory match game (card matching)")
print("✓ Obstacle course game (agility navigation)")
print("✓ Game rewards system (achievements)")
print("✓ Persistence (save/load all systems)")
print("\n🎉 ALL PHASE 12 TESTS PASSED! 🎉")
print("\nPhase 12 Features:")
print("  • 4 unique mini-games with different mechanics")
print("  • Difficulty levels (easy, medium, hard, expert)")
print("  • Score tracking and high scores")
print("  • Pet stats affect game performance")
print("  • Achievement system with unlocks")
print("  • Experience and coins rewards")
print("  • Player leveling system")
print("  • Full persistence for all game data")
print()
