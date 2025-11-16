"""
Transparent overlay window for displaying the desktop pet.
"""
from PyQt5.QtWidgets import QWidget, QLabel, QMenu, QAction, QApplication
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from PyQt5.QtGui import QPixmap, QCursor, QPainter, QImage
from PIL import ImageQt
import random
from ui.sprite_generator import SpriteGenerator
from core.config import BehaviorState, PET_SIZE, FPS, ANIMATION_UPDATE_INTERVAL


class PetWindow(QWidget):
    """Transparent window that displays the desktop pet."""

    def __init__(self, pet_manager):
        """
        Initialize the pet window.

        Args:
            pet_manager: The PetManager instance controlling the pet
        """
        super().__init__()
        self.pet_manager = pet_manager
        self.dragging = False
        self.drag_position = QPoint()

        self.init_ui()
        self.update_sprite()

        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(int(ANIMATION_UPDATE_INTERVAL * 1000))

        # Mouse tracking timer for sensory system
        # This tracks global cursor position for AI environmental awareness
        self.mouse_tracking_timer = QTimer()
        self.mouse_tracking_timer.timeout.connect(self.update_mouse_tracking)
        self.mouse_tracking_timer.start(100)  # Update every 100ms

    def init_ui(self):
        """Initialize the UI."""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setFixedSize(*PET_SIZE)

        # Label to display the sprite
        self.sprite_label = QLabel(self)
        self.sprite_label.setFixedSize(*PET_SIZE)

        # Position at saved location or center of screen
        if self.pet_manager.creature:
            x, y = self.pet_manager.creature.position
            self.move(int(x), int(y))
        else:
            # Center on screen
            screen_geometry = QApplication.desktop().screenGeometry()
            self.move(
                screen_geometry.width() // 2 - PET_SIZE[0] // 2,
                screen_geometry.height() // 2 - PET_SIZE[1] // 2
            )

    def update_sprite(self):
        """Update the displayed sprite based on creature state."""
        if not self.pet_manager.creature:
            # Show egg
            sprite = SpriteGenerator.generate_egg_sprite(PET_SIZE)
        else:
            # Show creature
            creature = self.pet_manager.creature
            sprite = SpriteGenerator.generate_creature_sprite(
                creature.creature_type,
                creature.color_palette,
                PET_SIZE,
                creature.facing_right
            )

        # Convert PIL Image to QPixmap
        qimage = ImageQt.ImageQt(sprite)
        pixmap = QPixmap.fromImage(qimage)
        self.sprite_label.setPixmap(pixmap)

    def update_animation(self):
        """Update animation frame."""
        if self.pet_manager.creature:
            # Update sprite based on facing direction
            creature = self.pet_manager.creature
            if creature.velocity[0] > 0:
                creature.facing_right = True
            elif creature.velocity[0] < 0:
                creature.facing_right = False

            self.update_sprite()

            # Update position based on velocity
            new_x = self.x() + int(creature.velocity[0])
            new_y = self.y() + int(creature.velocity[1])

            # Keep within screen bounds
            screen = QApplication.desktop().screenGeometry()
            new_x = max(0, min(new_x, screen.width() - PET_SIZE[0]))
            new_y = max(0, min(new_y, screen.height() - PET_SIZE[1]))

            self.move(new_x, new_y)
            creature.position = [new_x, new_y]

    def update_mouse_tracking(self):
        """
        Update mouse position for sensory system.

        Tracks global cursor position and feeds it to the AI's sensory system
        for environmental awareness (used by MEDIUM, ADVANCED, and EXPERT AI modes).
        """
        # Get global cursor position
        cursor_pos = QCursor.pos()
        mouse_x = cursor_pos.x()
        mouse_y = cursor_pos.y()

        # Update sensory system in pet manager
        if hasattr(self.pet_manager, 'update_sensory_inputs'):
            self.pet_manager.update_sensory_inputs(mouse_x, mouse_y)

    def mousePressEvent(self, event):
        """Handle mouse press for dragging and interaction."""
        if event.button() == Qt.LeftButton:
            # Start dragging
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

            # Interact with creature
            if self.pet_manager.creature:
                self.pet_manager.interact('pet')

        elif event.button() == Qt.RightButton:
            # Show context menu
            self.show_context_menu(event.globalPos())

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if self.dragging and event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)

            # Update creature position
            if self.pet_manager.creature:
                self.pet_manager.creature.position = [new_pos.x(), new_pos.y()]
                self.pet_manager.creature.velocity = [0, 0]  # Stop movement when dragged

            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """Handle double-click for hatching egg."""
        if event.button() == Qt.LeftButton:
            if not self.pet_manager.creature:
                # Hatch the egg!
                self.pet_manager.hatch_egg()
                self.update_sprite()

    def show_context_menu(self, position):
        """Show context menu with pet actions."""
        menu = QMenu()

        if self.pet_manager.creature:
            # Creature is alive - show interaction options
            feed_action = QAction("Feed", self)
            feed_action.triggered.connect(self.pet_manager.feed_creature)
            menu.addAction(feed_action)

            play_action = QAction("Play with Ball", self)
            play_action.triggered.connect(self.pet_manager.play_ball)
            menu.addAction(play_action)

            menu.addSeparator()

            stats_action = QAction("Show Stats", self)
            stats_action.triggered.connect(self.pet_manager.show_stats)
            menu.addAction(stats_action)
        else:
            # Egg state
            hatch_action = QAction("Hatch Egg", self)
            hatch_action.triggered.connect(lambda: (self.pet_manager.hatch_egg(), self.update_sprite()))
            menu.addAction(hatch_action)

        menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.pet_manager.exit_application)
        menu.addAction(exit_action)

        menu.exec_(position)


class BallWindow(QWidget):
    """Transparent window for the ball toy."""

    def __init__(self, pet_manager, initial_velocity):
        """
        Initialize the ball window.

        Args:
            pet_manager: The PetManager instance
            initial_velocity: Initial velocity [vx, vy] for the ball
        """
        super().__init__()
        self.pet_manager = pet_manager
        self.velocity = initial_velocity

        from ..core.config import TOY_SIZE, GRAVITY, BOUNCE_DAMPING, FRICTION

        self.size = TOY_SIZE
        self.gravity = GRAVITY
        self.bounce_damping = BOUNCE_DAMPING
        self.friction = FRICTION

        self.init_ui()

        # Physics timer
        self.physics_timer = QTimer()
        self.physics_timer.timeout.connect(self.update_physics)
        self.physics_timer.start(1000 // FPS)

    def init_ui(self):
        """Initialize the UI."""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(*self.size)

        # Generate ball sprite
        sprite = SpriteGenerator.generate_ball_sprite(self.size)
        qimage = ImageQt.ImageQt(sprite)
        pixmap = QPixmap.fromImage(qimage)

        label = QLabel(self)
        label.setPixmap(pixmap)
        label.setFixedSize(*self.size)

        # Start at pet position
        if self.pet_manager.pet_window:
            pet_pos = self.pet_manager.pet_window.pos()
            self.move(pet_pos.x(), pet_pos.y())

        self.show()

    def update_physics(self):
        """Update ball physics."""
        # Apply gravity
        self.velocity[1] += self.gravity

        # Apply friction
        self.velocity[0] *= self.friction

        # Update position
        new_x = self.x() + int(self.velocity[0])
        new_y = self.y() + int(self.velocity[1])

        # Screen bounds
        screen = QApplication.desktop().screenGeometry()

        # Bounce off walls
        if new_x <= 0 or new_x >= screen.width() - self.size[0]:
            self.velocity[0] = -self.velocity[0] * self.bounce_damping
            new_x = max(0, min(new_x, screen.width() - self.size[0]))

        if new_y <= 0 or new_y >= screen.height() - self.size[1]:
            self.velocity[1] = -self.velocity[1] * self.bounce_damping
            new_y = max(0, min(new_y, screen.height() - self.size[1]))

            # Stop if velocity is too low (ball has settled)
            if abs(self.velocity[1]) < 1 and new_y >= screen.height() - self.size[1] - 5:
                self.velocity = [0, 0]

        self.move(new_x, new_y)

        # Check if ball has stopped moving
        if abs(self.velocity[0]) < 0.1 and abs(self.velocity[1]) < 0.1:
            # Ball has stopped - remove it after a delay
            QTimer.singleShot(3000, self.close)

        # Check collision with pet
        if self.pet_manager.pet_window:
            pet_rect = self.pet_manager.pet_window.geometry()
            ball_rect = self.geometry()

            if pet_rect.intersects(ball_rect):
                # Pet caught the ball!
                self.pet_manager.interact('ball_play', positive=True)
                self.close()
