"""
Main pet manager coordinating creature behavior, UI, and game logic with enhanced AI.
"""
import time
import random
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMessageBox, QApplication
from .creature import Creature
from .enhanced_behavior_learner import EnhancedBehaviorLearner
from .sensory_system import CompleteSensorySystem
from .persistence import PetDataManager
from .config import (
    BehaviorState, HUNGER_CHECK_INTERVAL, BEHAVIOR_UPDATE_INTERVAL,
    SAVE_INTERVAL, MOUSE_CHASE_DISTANCE, BALL_SPEED, FEED_AMOUNT,
    DEFAULT_AI_COMPLEXITY, AIComplexity
)


class PetManager:
    """Manages the desktop pet's behavior, state, and interactions with enhanced AI."""

    def __init__(self, ai_complexity: AIComplexity = DEFAULT_AI_COMPLEXITY):
        """
        Initialize the pet manager.

        Args:
            ai_complexity: AI complexity level (SIMPLE, MEDIUM, ADVANCED, EXPERT)
        """
        self.creature = None
        self.learner = None
        self.pet_window = None
        self.is_egg = True
        self.last_update_time = time.time()
        self.ai_complexity = ai_complexity

        # Enhanced AI systems
        self.sensory_system = None
        if ai_complexity != AIComplexity.SIMPLE:
            # Initialize sensory system for all non-simple modes
            self.sensory_system = CompleteSensorySystem()

        # Data manager
        self.data_manager = PetDataManager()

        # Timers
        self.hunger_timer = None
        self.behavior_timer = None
        self.save_timer = None
        self.mouse_chase_timer = None
        self.sensory_update_timer = None

        # Behavioral state tracking
        self.current_decision = None
        self.last_behavior_update = time.time()

        # Load saved state
        self.load_state()

    def load_state(self):
        """Load saved pet state from file."""
        data = self.data_manager.load()

        if data:
            game_state = data.get('game_state', {})
            self.is_egg = game_state.get('is_egg', True)

            # Load AI complexity if saved
            if 'ai_complexity' in game_state:
                from .config import AIComplexity
                complexity_str = game_state['ai_complexity']
                self.ai_complexity = AIComplexity(complexity_str)

            if not self.is_egg and data.get('creature'):
                self.creature = data['creature']

                # Create enhanced learner
                if data.get('learner'):
                    self.learner = EnhancedBehaviorLearner.from_dict(
                        self.creature,
                        data['learner']
                    )
                else:
                    # Create new enhanced learner
                    self.learner = EnhancedBehaviorLearner(
                        self.creature,
                        self.ai_complexity
                    )

                # Reinitialize sensory system if needed
                if self.ai_complexity != AIComplexity.SIMPLE and self.sensory_system is None:
                    self.sensory_system = CompleteSensorySystem()

                # Check if creature died from starvation
                current_time = time.time()
                time_elapsed = current_time - self.creature.last_fed_time

                # Calculate hunger accumulated during offline time
                minutes_elapsed = time_elapsed / 60.0
                hunger_accumulated = self.creature.hunger + (0.1 * minutes_elapsed)

                if hunger_accumulated >= 100:
                    # Creature died from starvation
                    self.show_death_message()
                    self.creature = None
                    self.learner = None
                    self.is_egg = True
                else:
                    # Update creature with accumulated hunger
                    self.creature.hunger = min(100, hunger_accumulated)

    def save_state(self):
        """Save current pet state to file."""
        game_state = {
            'is_egg': self.is_egg,
            'last_save_time': time.time(),
            'ai_complexity': self.ai_complexity.value
        }

        self.data_manager.save(self.creature, self.learner, game_state)

    def hatch_egg(self):
        """Hatch a new creature from the egg."""
        if not self.is_egg:
            return

        # Create new creature
        self.creature = Creature()

        # Create enhanced behavior learner with configured AI complexity
        self.learner = EnhancedBehaviorLearner(
            self.creature,
            self.ai_complexity
        )

        self.is_egg = False

        # Initialize sensory system if needed
        if self.ai_complexity != AIComplexity.SIMPLE and self.sensory_system is None:
            self.sensory_system = CompleteSensorySystem()

        # Start timers
        self.start_timers()

        # Show welcome message
        self.show_hatch_message()

        # Save state
        self.save_state()

    def show_hatch_message(self):
        """Show message when creature hatches."""
        if self.creature:
            complexity_info = ""
            if self.ai_complexity == AIComplexity.SIMPLE:
                complexity_info = "\n\n[AI: Simple Mode]"
            elif self.ai_complexity == AIComplexity.MEDIUM:
                complexity_info = "\n\n[AI: Medium Mode - With Memory]"
            elif self.ai_complexity == AIComplexity.ADVANCED:
                complexity_info = "\n\n[AI: Advanced Mode - Full Intelligence]"
            elif self.ai_complexity == AIComplexity.EXPERT:
                complexity_info = "\n\n[AI: Expert Mode - Maximum Sophistication]"

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("A New Friend!")
            msg.setText(f"Your egg has hatched!\n\n"
                       f"Meet {self.creature.name}, a {self.creature.personality.value} "
                       f"{self.creature.creature_type}!\n\n"
                       f"Take good care of your new friend!{complexity_info}")
            msg.exec_()

    def show_death_message(self):
        """Show message when creature dies."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Goodbye...")
        msg.setText(f"Your creature has passed on due to starvation.\n\n"
                   f"They left behind an egg for you.\n\n"
                   f"Take better care of the next one!")
        msg.exec_()

    def start_timers(self):
        """Start all update timers."""
        # Hunger timer
        self.hunger_timer = QTimer()
        self.hunger_timer.timeout.connect(self.update_hunger)
        self.hunger_timer.start(HUNGER_CHECK_INTERVAL * 1000)

        # Behavior timer (AI decision-making)
        self.behavior_timer = QTimer()
        self.behavior_timer.timeout.connect(self.update_behavior)
        self.behavior_timer.start(BEHAVIOR_UPDATE_INTERVAL * 1000)

        # Save timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_state)
        self.save_timer.start(SAVE_INTERVAL * 1000)

        # Mouse chase timer
        self.mouse_chase_timer = QTimer()
        self.mouse_chase_timer.timeout.connect(self.check_mouse_chase)
        self.mouse_chase_timer.start(500)  # Check twice per second

        # Sensory update timer (for advanced AI modes)
        if self.sensory_system:
            self.sensory_update_timer = QTimer()
            self.sensory_update_timer.timeout.connect(self.update_sensory_inputs)
            self.sensory_update_timer.start(100)  # Update 10 times per second

    def stop_timers(self):
        """Stop all timers."""
        if self.hunger_timer:
            self.hunger_timer.stop()
        if self.behavior_timer:
            self.behavior_timer.stop()
        if self.save_timer:
            self.save_timer.stop()
        if self.mouse_chase_timer:
            self.mouse_chase_timer.stop()
        if self.sensory_update_timer:
            self.sensory_update_timer.stop()

    def update_sensory_inputs(self):
        """Update sensory system with current mouse position and environment."""
        if not self.sensory_system or not self.pet_window:
            return

        # Get current mouse position
        cursor = QCursor()
        mouse_pos = cursor.pos()

        # Update sensory system
        self.sensory_system.update_mouse_position(mouse_pos.x(), mouse_pos.y())

        # Update learner with sensory data
        if self.learner and hasattr(self.learner, 'update_sensory_inputs'):
            self.learner.update_sensory_inputs(mouse_pos.x(), mouse_pos.y())

    def update_hunger(self):
        """Update creature hunger level."""
        if not self.creature:
            return

        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time

        self.creature.update(delta_time)

        # Check if creature is starving
        if self.creature.is_starving():
            self.creature_died()

    def update_behavior(self):
        """Update creature behavior using enhanced AI decision-making."""
        if not self.creature or not self.pet_window or not self.learner:
            return

        # Simple sleep check (all AI levels)
        if self.creature.should_sleep():
            self.creature.set_state(BehaviorState.SLEEPING)
            self.creature.velocity = [0, 0]
            return

        # Get behavioral decision from enhanced learner
        try:
            decision = self.learner.get_behavioral_decision()
            self.current_decision = decision

            # Extract activity from decision
            activity = decision.get('activity', 'idle')

            # Map activity to behavior state
            self._apply_activity_decision(activity, decision)

            # Apply movement from advanced AI (if available)
            if 'velocity_x' in decision and 'velocity_y' in decision:
                if decision.get('should_move', False):
                    # Use AI-determined velocity
                    self.creature.velocity = [
                        decision['velocity_x'],
                        decision['velocity_y']
                    ]
                else:
                    self.creature.velocity = [0, 0]
            else:
                # Fallback to simple random movement for idle/explore
                if activity in ['explore', 'idle'] and random.random() < 0.3:
                    speed = 2 * self.creature.trait_modifiers.get('movement_speed', 1.0)
                    self.creature.velocity = [
                        random.uniform(-speed, speed),
                        random.uniform(-speed, speed)
                    ]

        except Exception as e:
            # Fallback to simple behavior if AI fails
            print(f"AI decision error: {e}")
            self._fallback_behavior()

    def _apply_activity_decision(self, activity: str, decision: dict):
        """
        Apply activity decision to creature state.

        Args:
            activity: Activity name (e.g., 'mouse_chase', 'hide_and_seek')
            decision: Full decision dictionary from AI
        """
        # Map activities to behavior states
        activity_state_map = {
            'mouse_chase': BehaviorState.CHASING,
            'ball_play': BehaviorState.PLAYING,
            'hide': BehaviorState.HIDING,
            'seek': BehaviorState.SEEKING,
            'hide_and_seek': BehaviorState.HIDING if random.random() < 0.5 else BehaviorState.SEEKING,
            'explore': BehaviorState.WALKING,
            'sleep': BehaviorState.SLEEPING,
            'idle': BehaviorState.IDLE,
            'eat': BehaviorState.EATING,
        }

        new_state = activity_state_map.get(activity, BehaviorState.IDLE)
        self.creature.set_state(new_state)

        # Special handling for specific activities
        if activity == 'mouse_chase':
            # Will be handled by check_mouse_chase
            pass
        elif activity == 'hide':
            # Move toward nearest icon (if sensory system available)
            if self.sensory_system and self.pet_window:
                state = self.sensory_system.get_state_dict(
                    self.creature.position[0],
                    self.creature.position[1]
                )
                hiding_spot = state.get('nearest_hiding_spot')
                if hiding_spot:
                    # Move toward hiding spot
                    dx = hiding_spot['x'] - self.creature.position[0]
                    dy = hiding_spot['y'] - self.creature.position[1]
                    distance = (dx**2 + dy**2)**0.5
                    if distance > 10:
                        speed = 3
                        self.creature.velocity = [
                            (dx / distance) * speed,
                            (dy / distance) * speed
                        ]

    def _fallback_behavior(self):
        """Fallback to simple random behavior if AI fails."""
        if random.random() < 0.3:
            self.creature.set_state(BehaviorState.WALKING)
            speed = 2 * self.creature.trait_modifiers.get('movement_speed', 1.0)
            self.creature.velocity = [
                random.uniform(-speed, speed),
                random.uniform(-speed, speed)
            ]
        else:
            self.creature.set_state(BehaviorState.IDLE)
            self.creature.velocity = [0, 0]

    def check_mouse_chase(self):
        """Check if creature should chase the mouse cursor."""
        if not self.creature or not self.pet_window:
            return

        if self.creature.current_state != BehaviorState.CHASING:
            return

        # Get mouse position
        cursor_pos = QCursor.pos()
        pet_pos = self.pet_window.pos()

        # Calculate distance to mouse
        dx = cursor_pos.x() - (pet_pos.x() + 64)  # Center of pet
        dy = cursor_pos.y() - (pet_pos.y() + 64)
        distance = (dx**2 + dy**2)**0.5

        if distance < MOUSE_CHASE_DISTANCE and distance > 10:
            # Move towards mouse
            speed = 3 * self.creature.trait_modifiers.get('movement_speed', 1.0)
            self.creature.velocity = [
                (dx / distance) * speed,
                (dy / distance) * speed
            ]
        else:
            # Stop chasing
            self.creature.velocity = [0, 0]

    def creature_died(self):
        """Handle creature death."""
        self.show_death_message()

        # Reset to egg
        self.creature = None
        self.learner = None
        self.is_egg = True

        # Stop timers
        self.stop_timers()

        # Update UI
        if self.pet_window:
            self.pet_window.update_sprite()

        # Save state
        self.save_state()

    def feed_creature(self):
        """Feed the creature."""
        if not self.creature:
            return

        old_hunger = self.creature.hunger
        self.creature.feed(FEED_AMOUNT)

        # Enhanced learning with outcome information
        outcome = {
            'hunger_before': old_hunger,
            'hunger_after': self.creature.hunger,
            'happiness_change': 5,
            'enjoyment': 1.0,
            'positive': True
        }

        self.learner.learn_from_interaction('being_fed', True, outcome)

        # Show message
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Fed!")
        msg.setText(f"{self.creature.name} enjoyed the food!\n\n"
                   f"Hunger: {self.creature.hunger:.1f}/100")
        msg.exec_()

        self.save_state()

    def play_ball(self):
        """Throw a ball for the creature to play with."""
        if not self.pet_window:
            return

        # Import here to avoid circular dependency
        from ui.pet_window import BallWindow

        # Create ball with random velocity
        velocity = [
            random.uniform(-BALL_SPEED, BALL_SPEED),
            random.uniform(-BALL_SPEED, -BALL_SPEED/2)  # Throw upward
        ]

        ball = BallWindow(self, velocity)

        # Creature notices and might chase
        if self.creature:
            enjoyment = random.random()
            positive = enjoyment > 0.3

            # Enhanced outcome information
            outcome = {
                'enjoyment': enjoyment,
                'positive': positive,
                'activity': 'ball_play',
                'state_before_dict': {
                    'hunger': self.creature.hunger,
                    'energy': self.creature.energy,
                    'happiness': self.creature.happiness
                }
            }

            self.interact('ball_play', positive, outcome)

            if enjoyment > 0.5:
                self.creature.set_state(BehaviorState.PLAYING)

    def interact(self, interaction_type: str, positive: bool = True, outcome: dict = None):
        """
        Record an interaction with the creature.

        Args:
            interaction_type: Type of interaction
            positive: Whether interaction was positive
            outcome: Additional outcome information for advanced learning
        """
        if not self.creature or not self.learner:
            return

        self.creature.interact(interaction_type, positive)

        # Use enhanced learning with outcome data
        self.learner.learn_from_interaction(interaction_type, positive, outcome or {})

        self.save_state()

    def show_stats(self):
        """Show creature statistics with enhanced AI information."""
        if not self.creature:
            return

        age_minutes = int(self.creature.age / 60)
        age_hours = age_minutes // 60
        age_minutes = age_minutes % 60

        # Build stats message
        stats_text = (
            f"Name: {self.creature.name}\n"
            f"Type: {self.creature.creature_type.capitalize()}\n"
            f"Personality: {self.creature.personality.value.capitalize()}\n\n"
            f"Age: {age_hours}h {age_minutes}m\n"
            f"Hunger: {self.creature.hunger:.1f}/100\n"
            f"Happiness: {self.creature.happiness:.1f}/100\n"
            f"Energy: {self.creature.energy:.1f}/100\n\n"
        )

        # Add AI-specific information
        if self.ai_complexity == AIComplexity.SIMPLE:
            stats_text += f"Favorite Activity: {self.creature.get_preferred_activity().replace('_', ' ').title()}\n"
            stats_text += f"\n[AI: Simple Mode]"
        elif self.ai_complexity in [AIComplexity.MEDIUM, AIComplexity.ADVANCED, AIComplexity.EXPERT]:
            # Show current decision
            if self.current_decision:
                activity = self.current_decision.get('activity', 'unknown')
                stats_text += f"Current Activity: {activity.replace('_', ' ').title()}\n"

                # Show emotions for advanced modes
                if self.ai_complexity in [AIComplexity.ADVANCED, AIComplexity.EXPERT]:
                    emotions = self.current_decision.get('emotions', {})
                    if emotions:
                        stats_text += "\nEmotional State:\n"
                        for emotion, value in emotions.items():
                            stats_text += f"  {emotion.capitalize()}: {value:.2f}\n"

        # Add complexity indicator
        stats_text += f"\n[AI Complexity: {self.ai_complexity.value.capitalize()}]"

        # Add learning stats for expert mode
        if self.ai_complexity == AIComplexity.EXPERT and self.learner:
            interactions = self.learner.total_interactions
            stats_text += f"\n[Total Interactions: {interactions}]"

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(f"{self.creature.name}'s Stats")
        msg.setText(stats_text)
        msg.exec_()

    def exit_application(self):
        """Exit the application."""
        self.save_state()
        QApplication.instance().quit()

    def set_pet_window(self, window):
        """Set the pet window reference."""
        self.pet_window = window

        if self.creature and not self.is_egg:
            self.start_timers()
