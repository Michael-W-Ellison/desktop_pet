"""
Installation and shortcut management for Desktop Pal.

Handles:
- Desktop shortcut creation
- Start Menu entry creation
- Windows startup registration
- First-run detection
"""
import os
import sys
import json
from pathlib import Path
from typing import Optional, Tuple


class InstallationManager:
    """Manages installation, shortcuts, and startup configuration."""

    # Configuration file for tracking installation state
    CONFIG_FILE = "install_config.json"

    def __init__(self):
        """Initialize the installation manager."""
        self.app_name = "Desktop Pal"
        self.app_exe = self._get_executable_path()
        self.app_dir = os.path.dirname(self.app_exe)
        self.config_path = os.path.join(self.app_dir, self.CONFIG_FILE)
        self.config = self._load_config()

    def _get_executable_path(self) -> str:
        """Get the path to the executable or script."""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return sys.executable
        else:
            # Running as script
            return os.path.abspath(sys.argv[0])

    def _load_config(self) -> dict:
        """Load installation configuration."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {
            'first_run_complete': False,
            'desktop_shortcut': False,
            'start_menu_shortcut': False,
            'startup_enabled': False,
            'install_date': None
        }

    def _save_config(self):
        """Save installation configuration."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save install config: {e}")

    def is_first_run(self) -> bool:
        """Check if this is the first run of the application."""
        return not self.config.get('first_run_complete', False)

    def mark_first_run_complete(self):
        """Mark the first run as complete."""
        from datetime import datetime
        self.config['first_run_complete'] = True
        self.config['install_date'] = datetime.now().isoformat()
        self._save_config()

    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return sys.platform == 'win32'

    def get_desktop_path(self) -> Optional[str]:
        """Get the user's Desktop folder path."""
        if self.is_windows():
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
                )
                desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
                winreg.CloseKey(key)
                return desktop_path
            except (ImportError, OSError):
                # Fallback to common path
                return os.path.join(os.path.expanduser("~"), "Desktop")
        else:
            # Linux/Mac
            return os.path.join(os.path.expanduser("~"), "Desktop")

    def get_start_menu_path(self) -> Optional[str]:
        """Get the user's Start Menu Programs folder path."""
        if not self.is_windows():
            return None
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            )
            programs_path, _ = winreg.QueryValueEx(key, "Programs")
            winreg.CloseKey(key)
            return programs_path
        except (ImportError, OSError):
            # Fallback to common path
            return os.path.join(
                os.path.expanduser("~"),
                "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs"
            )

    def get_startup_path(self) -> Optional[str]:
        """Get the Windows Startup folder path."""
        if not self.is_windows():
            return None
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            )
            startup_path, _ = winreg.QueryValueEx(key, "Startup")
            winreg.CloseKey(key)
            return startup_path
        except (ImportError, OSError):
            # Fallback to common path
            return os.path.join(
                os.path.expanduser("~"),
                "AppData", "Roaming", "Microsoft", "Windows", "Start Menu",
                "Programs", "Startup"
            )

    def create_shortcut(self, shortcut_path: str, target_path: str,
                        description: str = "", icon_path: Optional[str] = None,
                        working_dir: Optional[str] = None) -> bool:
        """
        Create a Windows shortcut (.lnk file).

        Args:
            shortcut_path: Full path for the shortcut file
            target_path: Path to the target executable
            description: Shortcut description
            icon_path: Path to icon file (optional)
            working_dir: Working directory for the shortcut

        Returns:
            True if successful, False otherwise
        """
        if not self.is_windows():
            return self._create_linux_shortcut(shortcut_path, target_path, description)

        try:
            # Use Windows COM to create shortcut
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target_path
            shortcut.Description = description
            shortcut.WorkingDirectory = working_dir or os.path.dirname(target_path)
            if icon_path:
                shortcut.IconLocation = icon_path
            shortcut.save()
            return True
        except ImportError:
            # Try alternative method using PowerShell
            return self._create_shortcut_powershell(
                shortcut_path, target_path, description, working_dir
            )
        except Exception as e:
            print(f"Error creating shortcut: {e}")
            return False

    def _create_shortcut_powershell(self, shortcut_path: str, target_path: str,
                                     description: str, working_dir: Optional[str]) -> bool:
        """Create shortcut using PowerShell as fallback."""
        import subprocess
        working_dir = working_dir or os.path.dirname(target_path)

        # PowerShell script to create shortcut
        ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target_path}"
$Shortcut.Description = "{description}"
$Shortcut.WorkingDirectory = "{working_dir}"
$Shortcut.Save()
'''
        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"PowerShell shortcut creation failed: {e}")
            return False

    def _create_linux_shortcut(self, shortcut_path: str, target_path: str,
                                description: str) -> bool:
        """Create a .desktop file for Linux."""
        desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Desktop Pal
Comment={description}
Exec=python3 "{target_path}"
Icon={os.path.join(os.path.dirname(target_path), 'icon.png')}
Terminal=false
Categories=Game;
"""
        try:
            # Change extension to .desktop
            if shortcut_path.endswith('.lnk'):
                shortcut_path = shortcut_path[:-4] + '.desktop'

            with open(shortcut_path, 'w') as f:
                f.write(desktop_entry)
            os.chmod(shortcut_path, 0o755)
            return True
        except Exception as e:
            print(f"Error creating Linux shortcut: {e}")
            return False

    def create_desktop_shortcut(self) -> bool:
        """Create a shortcut on the user's Desktop."""
        desktop_path = self.get_desktop_path()
        if not desktop_path or not os.path.exists(desktop_path):
            print("Desktop folder not found")
            return False

        shortcut_name = f"{self.app_name}.lnk"
        shortcut_path = os.path.join(desktop_path, shortcut_name)

        success = self.create_shortcut(
            shortcut_path=shortcut_path,
            target_path=self.app_exe,
            description="Your adorable desktop companion!",
            working_dir=self.app_dir
        )

        if success:
            self.config['desktop_shortcut'] = True
            self._save_config()

        return success

    def create_start_menu_shortcut(self) -> bool:
        """Create a shortcut in the Start Menu."""
        start_menu_path = self.get_start_menu_path()
        if not start_menu_path:
            print("Start Menu not available on this platform")
            return False

        # Create app folder in Start Menu
        app_folder = os.path.join(start_menu_path, self.app_name)
        os.makedirs(app_folder, exist_ok=True)

        shortcut_path = os.path.join(app_folder, f"{self.app_name}.lnk")

        success = self.create_shortcut(
            shortcut_path=shortcut_path,
            target_path=self.app_exe,
            description="Your adorable desktop companion!",
            working_dir=self.app_dir
        )

        if success:
            self.config['start_menu_shortcut'] = True
            self._save_config()

        return success

    def enable_startup(self) -> bool:
        """Enable the application to run at Windows startup."""
        if not self.is_windows():
            return self._enable_linux_autostart()

        startup_path = self.get_startup_path()
        if not startup_path or not os.path.exists(startup_path):
            print("Startup folder not found")
            return False

        shortcut_path = os.path.join(startup_path, f"{self.app_name}.lnk")

        success = self.create_shortcut(
            shortcut_path=shortcut_path,
            target_path=self.app_exe,
            description="Desktop Pal - Auto Start",
            working_dir=self.app_dir
        )

        if success:
            self.config['startup_enabled'] = True
            self._save_config()

        return success

    def disable_startup(self) -> bool:
        """Disable the application from running at Windows startup."""
        if not self.is_windows():
            return self._disable_linux_autostart()

        startup_path = self.get_startup_path()
        if not startup_path:
            return False

        shortcut_path = os.path.join(startup_path, f"{self.app_name}.lnk")

        try:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            self.config['startup_enabled'] = False
            self._save_config()
            return True
        except OSError as e:
            print(f"Error removing startup shortcut: {e}")
            return False

    def _enable_linux_autostart(self) -> bool:
        """Enable autostart on Linux using .desktop file in autostart."""
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)

        desktop_file = os.path.join(autostart_dir, "desktop-pet.desktop")
        return self._create_linux_shortcut(desktop_file, self.app_exe,
                                           "Desktop Pal - Auto Start")

    def _disable_linux_autostart(self) -> bool:
        """Disable autostart on Linux."""
        autostart_file = os.path.expanduser("~/.config/autostart/desktop-pet.desktop")
        try:
            if os.path.exists(autostart_file):
                os.remove(autostart_file)
            self.config['startup_enabled'] = False
            self._save_config()
            return True
        except OSError as e:
            print(f"Error removing autostart file: {e}")
            return False

    def is_startup_enabled(self) -> bool:
        """Check if startup is currently enabled."""
        return self.config.get('startup_enabled', False)

    def has_desktop_shortcut(self) -> bool:
        """Check if desktop shortcut exists."""
        desktop_path = self.get_desktop_path()
        if not desktop_path:
            return False
        shortcut_path = os.path.join(desktop_path, f"{self.app_name}.lnk")
        return os.path.exists(shortcut_path)

    def has_start_menu_shortcut(self) -> bool:
        """Check if Start Menu shortcut exists."""
        start_menu_path = self.get_start_menu_path()
        if not start_menu_path:
            return False
        shortcut_path = os.path.join(start_menu_path, self.app_name,
                                     f"{self.app_name}.lnk")
        return os.path.exists(shortcut_path)

    def remove_desktop_shortcut(self) -> bool:
        """Remove the desktop shortcut."""
        desktop_path = self.get_desktop_path()
        if not desktop_path:
            return False

        shortcut_path = os.path.join(desktop_path, f"{self.app_name}.lnk")
        try:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            self.config['desktop_shortcut'] = False
            self._save_config()
            return True
        except OSError as e:
            print(f"Error removing desktop shortcut: {e}")
            return False

    def remove_start_menu_shortcut(self) -> bool:
        """Remove the Start Menu shortcut."""
        start_menu_path = self.get_start_menu_path()
        if not start_menu_path:
            return False

        app_folder = os.path.join(start_menu_path, self.app_name)
        try:
            import shutil
            if os.path.exists(app_folder):
                shutil.rmtree(app_folder)
            self.config['start_menu_shortcut'] = False
            self._save_config()
            return True
        except OSError as e:
            print(f"Error removing Start Menu shortcut: {e}")
            return False

    def uninstall_shortcuts(self) -> Tuple[bool, bool, bool]:
        """
        Remove all shortcuts and startup entries.

        Returns:
            Tuple of (desktop_removed, start_menu_removed, startup_removed)
        """
        desktop_ok = self.remove_desktop_shortcut()
        start_menu_ok = self.remove_start_menu_shortcut()
        startup_ok = self.disable_startup()
        return desktop_ok, start_menu_ok, startup_ok

    def get_installation_status(self) -> dict:
        """Get current installation status."""
        return {
            'first_run_complete': self.config.get('first_run_complete', False),
            'install_date': self.config.get('install_date'),
            'desktop_shortcut': self.has_desktop_shortcut(),
            'start_menu_shortcut': self.has_start_menu_shortcut(),
            'startup_enabled': self.is_startup_enabled(),
            'platform': sys.platform,
            'executable': self.app_exe,
            'app_directory': self.app_dir
        }
