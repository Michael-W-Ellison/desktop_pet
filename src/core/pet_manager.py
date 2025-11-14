"""
Main pet manager coordinating creature behavior, UI, and game logic.
"""
import time
import random
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QApplication
from .creature import Creature
from .neural_network import BehaviorLearner
from .persistence import PetDataManager
from .config import (
    BehaviorState, HUNGER_CHECK_INTERVAL, BEHAVIOR_UPDATE_INTERVAL,
    SAVE_INTERVAL, MOUSE_CHASE_DISTANCE, BALL_SPEED, FEED_AMOUNT
)


class PetManager:
    """Manages the desktop pet's behavior, state, and interactions."""

    def __init__(self):
        """Initialize the pet manager."""
        self.creature = None
        self.learner = None
        self.pet_window = None
        self.is_egg = True
        self.last_update_time = time.time()

        # Data manager
        self.data_manager = PetDataManager()

        # Timers
        self.hunger_timer = None
        self.behavior_timer = None
        self.save_timer = None
        self.mouse_chase_timer = None

        # Load saved state
        self.load_state()

    def load_state(self):
        """Load saved pet state from file."""
        data = self.data_manager.load()

        if data:
            game_state = data.get('game_state', {})
            self.is_egg = game_state.get('is_egg', True)

            if not self.is_egg and data.get('creature'):
                self.creature = data['creature']
                self.learner = data.get('learner')

                if self.learner is None:
                    # Create new learner if not saved
                    self.learner = BehaviorLearner(self.creature)

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
            'last_save_time': time.time()
        }

        self.data_manager.save(self.creature, self.learner, game_state)

    def hatch_egg(self):
        """Hatch a new creature from the egg."""
        if not self.is_egg:
            return

        # Create new creature
        self.creature = Creature()
        self.learner = BehaviorLearner(self.creature)
        self.is_egg = False

        # Start timers
        self.start_timers()

        # Show welcome message
        self.show_hatch_message()

        # Save state
        self.save_state()

    def show_hatch_message(self):
        """Show message when creature hatches."""
        if self.creature:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("A New Friend!")
            msg.setText(f"Your egg has hatched!\n\n"
                       f"Meet {self.creature.name}, a {self.creature.personality.value} "
                       f"{self.creature.creature_type}!\n\n"
                       f"Take good care of your new friend!")
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

        # Behavior timer
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
        """Update creature behavior based on AI and personality."""
        if not self.creature or not self.pet_window:
            return

        # Decide next behavior
        if self.creature.should_sleep():
            self.creature.set_state(BehaviorState.SLEEPING)
            self.creature.velocity = [0, 0]
        else:
            # Use neural network to decide activity
            best_activity = self.learner.get_best_activity()

            # Map activity to behavior
            if best_activity == 'mouse_chase':
                self.creature.set_state(BehaviorState.CHASING)
            elif best_activity == 'hide_and_seek':
                if random.random() < 0.5:
                    self.creature.set_state(BehaviorState.HIDING)
                else:
                    self.creature.set_state(BehaviorState.SEEKING)
            elif best_activity == 'ball_play':
                self.creature.set_state(BehaviorState.PLAYING)
            else:
                # Random idle behavior
                if random.random() < 0.3:
                    self.creature.set_state(BehaviorState.WALKING)
                    # Random walk
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
        cursor_pos = QApplication.instance().desktop().cursor().pos()
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

        self.creature.feed(FEED_AMOUNT)

        # Learn from feeding
        self.learner.learn_from_interaction('being_fed', True)

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
        from ..ui.pet_window import BallWindow

        # Create ball with random velocity
        velocity = [
            random.uniform(-BALL_SPEED, BALL_SPEED),
            random.uniform(-BALL_SPEED, -BALL_SPEED/2)  # Throw upward
        ]

        ball = BallWindow(self, velocity)

        # Creature notices and might chase
        if self.creature:
            enjoyment = random.random()
            self.interact('ball_play', enjoyment > 0.3)

            if enjoyment > 0.5:
                self.creature.set_state(BehaviorState.PLAYING)

    def interact(self, interaction_type: str, positive: bool = True):
        """Record an interaction with the creature."""
        if not self.creature or not self.learner:
            return

        self.creature.interact(interaction_type, positive)
        self.learner.learn_from_interaction(interaction_type, positive)
        self.save_state()

    def show_stats(self):
        """Show creature statistics."""
        if not self.creature:
            return

        age_minutes = int(self.creature.age / 60)
        age_hours = age_minutes // 60
        age_minutes = age_minutes % 60

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(f"{self.creature.name}'s Stats")
        msg.setText(
            f"Name: {self.creature.name}\n"
            f"Type: {self.creature.creature_type.capitalize()}\n"
            f"Personality: {self.creature.personality.value.capitalize()}\n\n"
            f"Age: {age_hours}h {age_minutes}m\n"
            f"Hunger: {self.creature.hunger:.1f}/100\n"
            f"Happiness: {self.creature.happiness:.1f}/100\n"
            f"Energy: {self.creature.energy:.1f}/100\n\n"
            f"Favorite Activity: {self.creature.get_preferred_activity().replace('_', ' ').title()}"
        )
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
