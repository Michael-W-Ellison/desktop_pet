"""
Main entry point for the Desktop Pal application.
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction,
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QFrame, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from PIL import ImageQt

from core.pet_manager import PetManager
from core.installation import InstallationManager
from ui.pet_window import PetWindow
from ui.sprite_generator import SpriteGenerator
from ui.first_run_wizard import show_first_run_wizard


class SettingsDialog(QDialog):
    """Settings dialog for installation options."""

    def __init__(self, install_manager: InstallationManager, parent=None):
        super().__init__(parent)
        self.install_manager = install_manager
        self.setWindowTitle("Desktop Pal Settings")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        """Set up the settings dialog UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Title
        title = QLabel("<b>Installation Settings</b>")
        title.setStyleSheet("font-size: 12pt;")
        layout.addWidget(title)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Desktop shortcut
        self.desktop_checkbox = QCheckBox("Desktop shortcut")
        self.desktop_checkbox.setChecked(self.install_manager.has_desktop_shortcut())
        layout.addWidget(self.desktop_checkbox)

        # Start Menu shortcut
        self.start_menu_checkbox = QCheckBox("Start Menu entry")
        self.start_menu_checkbox.setChecked(self.install_manager.has_start_menu_shortcut())
        layout.addWidget(self.start_menu_checkbox)

        # Startup option
        self.startup_checkbox = QCheckBox("Start with Windows")
        self.startup_checkbox.setChecked(self.install_manager.is_startup_enabled())
        layout.addWidget(self.startup_checkbox)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_settings)
        apply_btn.setDefault(True)
        button_layout.addWidget(apply_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def apply_settings(self):
        """Apply the selected settings."""
        results = []

        # Desktop shortcut
        has_desktop = self.install_manager.has_desktop_shortcut()
        want_desktop = self.desktop_checkbox.isChecked()
        if want_desktop and not has_desktop:
            if self.install_manager.create_desktop_shortcut():
                results.append("Desktop shortcut created")
            else:
                results.append("Failed to create desktop shortcut")
        elif not want_desktop and has_desktop:
            if self.install_manager.remove_desktop_shortcut():
                results.append("Desktop shortcut removed")

        # Start Menu shortcut
        has_start = self.install_manager.has_start_menu_shortcut()
        want_start = self.start_menu_checkbox.isChecked()
        if want_start and not has_start:
            if self.install_manager.create_start_menu_shortcut():
                results.append("Start Menu entry created")
            else:
                results.append("Failed to create Start Menu entry")
        elif not want_start and has_start:
            if self.install_manager.remove_start_menu_shortcut():
                results.append("Start Menu entry removed")

        # Startup
        has_startup = self.install_manager.is_startup_enabled()
        want_startup = self.startup_checkbox.isChecked()
        if want_startup and not has_startup:
            if self.install_manager.enable_startup():
                results.append("Windows startup enabled")
            else:
                results.append("Failed to enable startup")
        elif not want_startup and has_startup:
            if self.install_manager.disable_startup():
                results.append("Windows startup disabled")

        if results:
            QMessageBox.information(
                self,
                "Settings Applied",
                "\n".join(results)
            )

        self.accept()


class DesktopPetApp:
    """Main application class for the desktop pal."""

    def __init__(self):
        """Initialize the application."""
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # Initialize installation manager
        self.install_manager = InstallationManager()

        # Show first-run wizard if needed
        if self.install_manager.is_first_run():
            if not show_first_run_wizard(self.install_manager):
                # User cancelled wizard completely
                sys.exit(0)

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

        settings_action = QAction("Settings", self.app)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)

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

    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self.install_manager)
        dialog.exec_()

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
