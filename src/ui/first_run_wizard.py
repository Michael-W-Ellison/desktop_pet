"""
First-run wizard for Desktop Pal.

Shows on first launch to help users configure their installation
and learn about the application.
"""
from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QPushButton, QFrame, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor

from core.installation import InstallationManager


class WelcomePage(QWizardPage):
    """Welcome page introducing the application."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Welcome to Desktop Pal!")
        self.setSubTitle("Your new virtual companion awaits")

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Welcome message
        welcome_label = QLabel(
            "Thank you for choosing Desktop Pal!\n\n"
            "You're about to hatch your very own virtual companion that will "
            "live on your desktop. Your pet will:\n\n"
            "  - Learn from your interactions and develop a unique personality\n"
            "  - Play games and perform tricks\n"
            "  - Form memories and bonds with you\n"
            "  - Evolve and grow over time\n\n"
            "This wizard will help you set up Desktop Pal for the best experience."
        )
        welcome_label.setWordWrap(True)
        welcome_label.setStyleSheet("font-size: 11pt;")
        layout.addWidget(welcome_label)

        # Spacer
        layout.addStretch()

        # Tip box
        tip_frame = QFrame()
        tip_frame.setStyleSheet("""
            QFrame {
                background-color: #E8F4FD;
                border: 1px solid #B8D4E8;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        tip_layout = QVBoxLayout(tip_frame)
        tip_label = QLabel(
            "<b>Tip:</b> Your pet needs care! Remember to feed it regularly "
            "and interact with it to keep it happy."
        )
        tip_label.setWordWrap(True)
        tip_layout.addWidget(tip_label)
        layout.addWidget(tip_frame)

        self.setLayout(layout)


class ShortcutPage(QWizardPage):
    """Page for configuring shortcuts and startup options."""

    def __init__(self, install_manager: InstallationManager, parent=None):
        super().__init__(parent)
        self.install_manager = install_manager
        self.setTitle("Installation Options")
        self.setSubTitle("Choose how you'd like to access Desktop Pal")

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Desktop shortcut option
        self.desktop_checkbox = QCheckBox("Create Desktop shortcut")
        self.desktop_checkbox.setChecked(True)
        self.desktop_checkbox.setStyleSheet("font-size: 11pt;")
        desktop_desc = QLabel(
            "Adds a shortcut to your Desktop for easy access"
        )
        desktop_desc.setStyleSheet("color: #666; margin-left: 25px; font-size: 10pt;")
        layout.addWidget(self.desktop_checkbox)
        layout.addWidget(desktop_desc)

        layout.addSpacing(10)

        # Start Menu shortcut option
        self.start_menu_checkbox = QCheckBox("Create Start Menu entry")
        self.start_menu_checkbox.setChecked(True)
        self.start_menu_checkbox.setStyleSheet("font-size: 11pt;")
        start_desc = QLabel(
            "Adds Desktop Pal to your Start Menu programs"
        )
        start_desc.setStyleSheet("color: #666; margin-left: 25px; font-size: 10pt;")
        layout.addWidget(self.start_menu_checkbox)
        layout.addWidget(start_desc)

        layout.addSpacing(10)

        # Startup option
        self.startup_checkbox = QCheckBox("Start with Windows")
        self.startup_checkbox.setChecked(False)
        self.startup_checkbox.setStyleSheet("font-size: 11pt;")
        startup_desc = QLabel(
            "Automatically launch Desktop Pal when you log in to Windows"
        )
        startup_desc.setStyleSheet("color: #666; margin-left: 25px; font-size: 10pt;")
        layout.addWidget(self.startup_checkbox)
        layout.addWidget(startup_desc)

        layout.addStretch()

        # Info box
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF9E6;
                border: 1px solid #E6D9A6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_label = QLabel(
            "<b>Note:</b> You can change these settings later from the "
            "pet's right-click menu under 'Settings'."
        )
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        layout.addWidget(info_frame)

        self.setLayout(layout)

        # Register fields for access in other pages
        self.registerField("desktop_shortcut", self.desktop_checkbox)
        self.registerField("start_menu_shortcut", self.start_menu_checkbox)
        self.registerField("startup_enabled", self.startup_checkbox)


class QuickTipsPage(QWizardPage):
    """Page showing quick tips for getting started."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Quick Tips")
        self.setSubTitle("Learn the basics of caring for your pet")

        layout = QVBoxLayout()
        layout.setSpacing(15)

        tips = [
            ("Right-click your pet", "Access the menu for feeding, playing, and viewing stats"),
            ("Double-click the egg", "Hatch your pet when it first appears"),
            ("Drag your pet", "Move it anywhere on your desktop"),
            ("System tray icon", "Quick access when your pet is hidden"),
            ("Feed regularly", "Hunger increases over time - don't let it starve!"),
            ("Play and interact", "Your pet learns from interactions and develops preferences"),
        ]

        for title, description in tips:
            tip_layout = QHBoxLayout()

            bullet = QLabel("\u2022")
            bullet.setStyleSheet("font-size: 14pt; color: #4A90D9;")
            bullet.setFixedWidth(20)
            tip_layout.addWidget(bullet)

            text_layout = QVBoxLayout()
            title_label = QLabel(f"<b>{title}</b>")
            title_label.setStyleSheet("font-size: 11pt;")
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #666; font-size: 10pt;")
            text_layout.addWidget(title_label)
            text_layout.addWidget(desc_label)
            text_layout.setSpacing(2)

            tip_layout.addLayout(text_layout)
            layout.addLayout(tip_layout)

        layout.addStretch()

        # Ready message
        ready_label = QLabel(
            "<i>Click 'Finish' to complete setup and meet your new pet!</i>"
        )
        ready_label.setAlignment(Qt.AlignCenter)
        ready_label.setStyleSheet("font-size: 11pt; color: #4A90D9;")
        layout.addWidget(ready_label)

        self.setLayout(layout)


class SetupProgressPage(QWizardPage):
    """Page showing setup progress."""

    def __init__(self, install_manager: InstallationManager, parent=None):
        super().__init__(parent)
        self.install_manager = install_manager
        self.setTitle("Setting Up")
        self.setSubTitle("Please wait while Desktop Pal is configured...")
        self.setup_complete = False

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Preparing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 11pt;")
        layout.addWidget(self.status_label)

        # Results frame (hidden initially)
        self.results_frame = QFrame()
        self.results_frame.setStyleSheet("""
            QFrame {
                background-color: #E8F8E8;
                border: 1px solid #A8D8A8;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        self.results_layout = QVBoxLayout(self.results_frame)
        self.results_label = QLabel("")
        self.results_label.setWordWrap(True)
        self.results_layout.addWidget(self.results_label)
        self.results_frame.hide()
        layout.addWidget(self.results_frame)

        layout.addStretch()

        self.setLayout(layout)

    def initializePage(self):
        """Called when the page is shown - start the setup process."""
        # Use a timer to start setup after the page is displayed
        QTimer.singleShot(500, self.run_setup)

    def run_setup(self):
        """Run the setup process."""
        results = []
        total_steps = 3
        current_step = 0

        # Step 1: Desktop shortcut
        if self.field("desktop_shortcut"):
            self.status_label.setText("Creating Desktop shortcut...")
            self.progress_bar.setValue(int((current_step / total_steps) * 100))
            QTimer.singleShot(100, lambda: None)  # Allow UI update

            if self.install_manager.create_desktop_shortcut():
                results.append(("\u2713", "Desktop shortcut created", "green"))
            else:
                results.append(("\u2717", "Desktop shortcut failed", "red"))
        current_step += 1
        self.progress_bar.setValue(int((current_step / total_steps) * 100))

        # Step 2: Start Menu shortcut
        if self.field("start_menu_shortcut"):
            self.status_label.setText("Creating Start Menu entry...")

            if self.install_manager.create_start_menu_shortcut():
                results.append(("\u2713", "Start Menu entry created", "green"))
            else:
                results.append(("\u2717", "Start Menu entry failed", "red"))
        current_step += 1
        self.progress_bar.setValue(int((current_step / total_steps) * 100))

        # Step 3: Startup
        if self.field("startup_enabled"):
            self.status_label.setText("Configuring Windows startup...")

            if self.install_manager.enable_startup():
                results.append(("\u2713", "Windows startup enabled", "green"))
            else:
                results.append(("\u2717", "Windows startup failed", "red"))
        current_step += 1
        self.progress_bar.setValue(100)

        # Show results
        self.status_label.setText("Setup complete!")

        if results:
            results_html = "<br>".join([
                f'<span style="color: {color};">{icon}</span> {text}'
                for icon, text, color in results
            ])
        else:
            results_html = "No additional setup was required."

        self.results_label.setText(results_html)
        self.results_frame.show()

        # Mark first run as complete
        self.install_manager.mark_first_run_complete()
        self.setup_complete = True

        # Enable the Finish button
        self.completeChanged.emit()

    def isComplete(self):
        """Check if the page is complete."""
        return self.setup_complete


class FirstRunWizard(QWizard):
    """First-run setup wizard for Desktop Pal."""

    def __init__(self, install_manager: InstallationManager = None, parent=None):
        super().__init__(parent)
        self.install_manager = install_manager or InstallationManager()

        self.setWindowTitle("Desktop Pal Setup")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(550, 450)

        # Set button text
        self.setButtonText(QWizard.NextButton, "Next >")
        self.setButtonText(QWizard.BackButton, "< Back")
        self.setButtonText(QWizard.FinishButton, "Finish")
        self.setButtonText(QWizard.CancelButton, "Skip Setup")

        # Add pages
        self.addPage(WelcomePage())
        self.shortcut_page = ShortcutPage(self.install_manager)
        self.addPage(self.shortcut_page)
        self.addPage(QuickTipsPage())
        self.progress_page = SetupProgressPage(self.install_manager)
        self.addPage(self.progress_page)

        # Style the wizard
        self.setStyleSheet("""
            QWizard {
                background-color: #FFFFFF;
            }
            QWizardPage {
                background-color: #FFFFFF;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
            }
        """)

    def accept(self):
        """Called when Finish is clicked."""
        super().accept()

    def reject(self):
        """Called when Cancel/Skip is clicked."""
        reply = QMessageBox.question(
            self,
            "Skip Setup?",
            "Are you sure you want to skip setup?\n\n"
            "You can configure these options later from the pet's Settings menu.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Mark first run complete even if skipped
            self.install_manager.mark_first_run_complete()
            super().reject()


def show_first_run_wizard(install_manager: InstallationManager = None) -> bool:
    """
    Show the first-run wizard if this is the first run.

    Args:
        install_manager: InstallationManager instance (optional)

    Returns:
        True if wizard was completed or skipped, False if cancelled
    """
    manager = install_manager or InstallationManager()

    if not manager.is_first_run():
        return True  # Not first run, no wizard needed

    wizard = FirstRunWizard(manager)
    result = wizard.exec_()

    return result == QWizard.Accepted or manager.config.get('first_run_complete', False)
