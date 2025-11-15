"""
Main entry point for the Desktop Pet application.
"""
import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from PIL import ImageQt

from core.pet_manager import PetManager
from ui.pet_window import PetWindow
from ui.sprite_generator import SpriteGenerator


class DesktopPetApp:
    """Main application class for the desktop pet."""

    def __init__(self):
        """Initialize the application."""
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Create pet manager
        self.pet_manager = PetManager()

        # Create system tray icon
        self.create_tray_icon()

        # Create pet window
        self.pet_window = PetWindow(self.pet_manager)
        self.pet_manager.set_pet_window(self.pet_window)
        self.pet_window.show()

    def create_tray_icon(self):
        """Create system tray icon."""
        # Generate icon based on state
        if self.pet_manager.is_egg:
            icon_sprite = SpriteGenerator.generate_egg_sprite((64, 64))
        else:
            icon_sprite = SpriteGenerator.generate_shelter_sprite((64, 64))

        # Convert to QIcon
        qimage = ImageQt.ImageQt(icon_sprite)
        pixmap = QPixmap.fromImage(qimage)
        icon = QIcon(pixmap)

        # Create tray icon
        self.tray_icon = QSystemTrayIcon(icon, self.app)

        # Create context menu
        tray_menu = QMenu()

        show_action = QAction("Show Pet", self.app)
        show_action.triggered.connect(self.show_pet)
        tray_menu.addAction(show_action)

        if self.pet_manager.creature:
            feed_action = QAction("Feed", self.app)
            feed_action.triggered.connect(self.pet_manager.feed_creature)
            tray_menu.addAction(feed_action)

            stats_action = QAction("Stats", self.app)
            stats_action.triggered.connect(self.pet_manager.show_stats)
            tray_menu.addAction(stats_action)

        tray_menu.addSeparator()

        exit_action = QAction("Exit", self.app)
        exit_action.triggered.connect(self.exit_app)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Double-click to show/hide pet
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.pet_window.isVisible():
                self.pet_window.hide()
            else:
                self.pet_window.show()

    def show_pet(self):
        """Show the pet window."""
        self.pet_window.show()
        self.pet_window.raise_()
        self.pet_window.activateWindow()

    def exit_app(self):
        """Exit the application."""
        self.pet_manager.exit_application()

    def run(self):
        """Run the application."""
        return self.app.exec_()


def main():
    """Main function."""
    app = DesktopPetApp()
    sys.exit(app.run())


if __name__ == '__main__':
    main()
