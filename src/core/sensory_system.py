"""
Sensory input system for environmental awareness.

Gives creatures the ability to "sense" their environment:
- Screen layout and icon positions
- Mouse position and velocity
- Time of day and context
- Proximity to objects and edges
"""
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
import datetime
import math
import random
import sys
import time

# Seconds between rescans of the desktop icon layout
ICON_RESCAN_INTERVAL = 60.0


def read_windows_desktop_icons() -> Optional[List[Dict[str, float]]]:
    """
    Read desktop icon positions from the Windows desktop (Explorer's list view).

    The desktop is a SysListView32 control owned by Explorer. Its item positions
    are read by sending LVM_GETITEMPOSITION with a buffer allocated inside
    Explorer's process, then copying the result back.

    Returns:
        List of icon rectangles in screen coordinates, or None if unavailable
    """
    if sys.platform != 'win32':
        return None

    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.WinDLL('user32', use_last_error=True)
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

        user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        user32.FindWindowW.restype = wintypes.HWND
        user32.FindWindowExW.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR]
        user32.FindWindowExW.restype = wintypes.HWND
        user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        user32.SendMessageW.restype = ctypes.c_ssize_t
        user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.VirtualAllocEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t,
                                            wintypes.DWORD, wintypes.DWORD]
        kernel32.VirtualAllocEx.restype = ctypes.c_void_p
        kernel32.VirtualFreeEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_size_t, wintypes.DWORD]
        kernel32.VirtualFreeEx.restype = wintypes.BOOL
        kernel32.ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                                               ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
        kernel32.ReadProcessMemory.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL

        LVM_GETITEMCOUNT = 0x1004
        LVM_GETITEMPOSITION = 0x1010
        LVM_GETITEMSPACING = 0x1033
        PROCESS_VM_OPERATION, PROCESS_VM_READ, PROCESS_VM_WRITE = 0x0008, 0x0010, 0x0020
        MEM_COMMIT, MEM_RELEASE, PAGE_READWRITE = 0x1000, 0x8000, 0x04

        # The icon view lives under Progman, or under a WorkerW window when a
        # wallpaper slideshow or similar is active
        defview = user32.FindWindowExW(user32.FindWindowW('Progman', None), None, 'SHELLDLL_DefView', None)
        worker = None
        while not defview:
            worker = user32.FindWindowExW(None, worker, 'WorkerW', None)
            if not worker:
                return None
            defview = user32.FindWindowExW(worker, None, 'SHELLDLL_DefView', None)
        listview = user32.FindWindowExW(defview, None, 'SysListView32', None)
        if not listview:
            return None

        count = user32.SendMessageW(listview, LVM_GETITEMCOUNT, 0, 0)
        spacing = user32.SendMessageW(listview, LVM_GETITEMSPACING, 0, 0)
        width, height = (spacing & 0xFFFF) or 75, ((spacing >> 16) & 0xFFFF) or 75

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(listview, ctypes.byref(pid))
        process = kernel32.OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE,
                                       False, pid.value)
        if not process:
            return None

        icons = []
        try:
            remote_point = kernel32.VirtualAllocEx(process, None, ctypes.sizeof(wintypes.POINT),
                                                   MEM_COMMIT, PAGE_READWRITE)
            if not remote_point:
                return None
            try:
                point = wintypes.POINT()
                for index in range(count):
                    if not user32.SendMessageW(listview, LVM_GETITEMPOSITION, index, remote_point):
                        continue
                    if kernel32.ReadProcessMemory(process, remote_point, ctypes.byref(point),
                                                  ctypes.sizeof(point), None):
                        icons.append({'x': float(point.x), 'y': float(point.y),
                                      'width': float(width), 'height': float(height)})
            finally:
                kernel32.VirtualFreeEx(process, remote_point, 0, MEM_RELEASE)
        finally:
            kernel32.CloseHandle(process)

        return icons
    except Exception:
        return None


class SensoryEncoder:
    """
    Encodes environmental sensory data into normalized neural network inputs.
    """

    @staticmethod
    def normalize_position(x: float, y: float, screen_width: int = 1920,
                           screen_height: int = 1080) -> Tuple[float, float]:
        """Normalize screen position to 0-1 range."""
        return x / screen_width, y / screen_height

    @staticmethod
    def encode_time_of_day() -> np.ndarray:
        """
        Encode current time into features.

        Returns:
            Array of [hour_normalized, is_morning, is_afternoon, is_evening, is_night]
        """
        now = datetime.datetime.now()
        hour = now.hour

        # Cyclic encoding for hour (sin/cos to capture circularity)
        hour_sin = math.sin(2 * math.pi * hour / 24)
        hour_cos = math.cos(2 * math.pi * hour / 24)

        # Time of day categories
        is_morning = 1.0 if 6 <= hour < 12 else 0.0
        is_afternoon = 1.0 if 12 <= hour < 18 else 0.0
        is_evening = 1.0 if 18 <= hour < 22 else 0.0
        is_night = 1.0 if (22 <= hour or hour < 6) else 0.0

        return np.array([hour_sin, hour_cos, is_morning, is_afternoon, is_evening, is_night])

    @staticmethod
    def encode_day_of_week() -> np.ndarray:
        """Encode day of week (useful for learning player schedule)."""
        now = datetime.datetime.now()
        day = now.weekday()  # 0 = Monday, 6 = Sunday

        # Cyclic encoding
        day_sin = math.sin(2 * math.pi * day / 7)
        day_cos = math.cos(2 * math.pi * day / 7)

        # Weekend indicator
        is_weekend = 1.0 if day >= 5 else 0.0

        return np.array([day_sin, day_cos, is_weekend])

    @staticmethod
    def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    @staticmethod
    def calculate_angle(x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate angle from point 1 to point 2 (in radians)."""
        return math.atan2(y2 - y1, x2 - x1)


class MouseTracker:
    """
    Tracks mouse position and velocity.
    """

    def __init__(self, history_length: int = 10):
        """
        Initialize mouse tracker.

        Args:
            history_length: Number of historical positions to track
        """
        self.history_length = history_length
        self.position_history = []  # List of (x, y, timestamp)
        self.current_position = (0, 0)
        self.current_velocity = (0, 0)

    def update(self, x: float, y: float):
        """
        Update mouse position.

        Args:
            x: Mouse x coordinate
            y: Mouse y coordinate
        """
        import time
        timestamp = time.time()

        self.current_position = (x, y)

        # Add to history
        self.position_history.append((x, y, timestamp))

        # Keep only recent history
        if len(self.position_history) > self.history_length:
            self.position_history = self.position_history[-self.history_length:]

        # Calculate velocity
        if len(self.position_history) >= 2:
            (x1, y1, t1), (x2, y2, t2) = self.position_history[-2:]
            dt = max(t2 - t1, 0.001)  # Avoid division by zero

            self.current_velocity = (
                (x2 - x1) / dt,
                (y2 - y1) / dt
            )

    def get_velocity_magnitude(self) -> float:
        """Get magnitude of mouse velocity (speed)."""
        vx, vy = self.current_velocity
        return math.sqrt(vx ** 2 + vy ** 2)

    def is_moving_fast(self, threshold: float = 100) -> bool:
        """Check if mouse is moving fast."""
        return self.get_velocity_magnitude() > threshold

    def is_approaching(self, target_x: float, target_y: float,
                       threshold_distance: float = 200) -> bool:
        """
        Check if mouse is approaching a target location.

        Args:
            target_x: Target x coordinate
            target_y: Target y coordinate
            threshold_distance: Distance threshold

        Returns:
            True if mouse is approaching
        """
        if len(self.position_history) < 2:
            return False

        # Current distance to target
        current_dist = SensoryEncoder.calculate_distance(
            self.current_position[0], self.current_position[1],
            target_x, target_y
        )

        # Previous distance to target
        prev_x, prev_y, _ = self.position_history[-2]
        prev_dist = SensoryEncoder.calculate_distance(
            prev_x, prev_y, target_x, target_y
        )

        # Approaching if getting closer and within threshold
        return (current_dist < prev_dist and current_dist < threshold_distance)

    def encode(self, creature_x: float, creature_y: float,
               screen_width: int = 1920, screen_height: int = 1080) -> np.ndarray:
        """
        Encode mouse state relative to creature position.

        Returns:
            Array of [mouse_x_norm, mouse_y_norm, velocity_x_norm, velocity_y_norm,
                     distance_to_creature_norm, angle_to_creature, is_approaching, speed_category]
        """
        mx, my = self.current_position
        vx, vy = self.current_velocity

        # Normalize positions
        mx_norm = mx / screen_width
        my_norm = my / screen_height

        # Normalize velocity (assuming max velocity of ~1000 pixels/s)
        vx_norm = np.clip(vx / 1000, -1, 1)
        vy_norm = np.clip(vy / 1000, -1, 1)

        # Distance to creature
        distance = SensoryEncoder.calculate_distance(mx, my, creature_x, creature_y)
        distance_norm = min(distance / 500, 1.0)  # Normalize to 500 pixels

        # Angle from creature to mouse
        angle = SensoryEncoder.calculate_angle(creature_x, creature_y, mx, my)
        angle_sin = math.sin(angle)
        angle_cos = math.cos(angle)

        # Is approaching
        is_approaching = 1.0 if self.is_approaching(creature_x, creature_y) else 0.0

        # Speed category
        speed = self.get_velocity_magnitude()
        speed_slow = 1.0 if speed < 50 else 0.0
        speed_medium = 1.0 if 50 <= speed < 200 else 0.0
        speed_fast = 1.0 if speed >= 200 else 0.0

        return np.array([
            mx_norm, my_norm, vx_norm, vy_norm,
            distance_norm, angle_sin, angle_cos,
            is_approaching, speed_slow, speed_medium, speed_fast
        ])


class ScreenLayoutAnalyzer:
    """
    Analyzes screen layout to detect icons, windows, and obstacles.
    """

    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        """Initialize screen analyzer."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.detected_icons = []  # List of (x, y, width, height)
        self.last_scan_time = 0
        self.icons_are_real = False  # Whether icons came from the desktop or the fallback grid

    def refresh_icons(self):
        """Rescan the desktop icons if the last scan is older than ICON_RESCAN_INTERVAL."""
        if not self.detected_icons or time.time() - self.last_scan_time > ICON_RESCAN_INTERVAL:
            self.detected_icons = self.detect_desktop_icons()

    def detect_desktop_icons(self) -> List[Dict[str, float]]:
        """
        Detect desktop icons.

        On Windows this reads the real icon positions from the desktop. Elsewhere,
        or if reading fails, it assumes a standard icon grid on the left side.

        Returns:
            List of icon positions
        """
        self.last_scan_time = time.time()
        icons = read_windows_desktop_icons()
        if icons is not None:
            self.icons_are_real = True
            return icons

        self.icons_are_real = False
        icons = []

        # Common icon positions on desktop (left side, vertical grid)
        icon_size = 80
        margin = 10
        x = margin
        y = margin

        for i in range(15):  # Assume max 15 icons
            icons.append({
                'x': x,
                'y': y,
                'width': icon_size,
                'height': icon_size
            })

            y += icon_size + margin
            if y > self.screen_height - icon_size:
                x += icon_size + margin
                y = margin

        return icons

    def find_nearest_icon(self, x: float, y: float) -> Optional[Dict[str, float]]:
        """Find nearest icon to given position."""
        self.refresh_icons()

        nearest = None
        min_distance = float('inf')

        for icon in self.detected_icons:
            icon_center_x = icon['x'] + icon['width'] / 2
            icon_center_y = icon['y'] + icon['height'] / 2

            distance = SensoryEncoder.calculate_distance(x, y, icon_center_x, icon_center_y)

            if distance < min_distance:
                min_distance = distance
                nearest = icon

        return nearest

    def get_hiding_spots(self, creature_x: float, creature_y: float,
                         max_distance: float = 300) -> List[Dict[str, float]]:
        """
        Get potential hiding spots (icons) near creature.

        Args:
            creature_x: Creature x position
            creature_y: Creature y position
            max_distance: Maximum distance for hiding spot

        Returns:
            List of nearby hiding spots
        """
        self.refresh_icons()

        hiding_spots = []

        for icon in self.detected_icons:
            icon_center_x = icon['x'] + icon['width'] / 2
            icon_center_y = icon['y'] + icon['height'] / 2

            distance = SensoryEncoder.calculate_distance(
                creature_x, creature_y, icon_center_x, icon_center_y
            )

            if distance <= max_distance:
                hiding_spots.append({
                    'x': icon['x'],
                    'y': icon['y'],
                    'width': icon['width'],
                    'height': icon['height'],
                    'distance': distance
                })

        # Sort by distance
        hiding_spots.sort(key=lambda spot: spot['distance'])

        return hiding_spots


class ProximitySensor:
    """
    Detects proximity to screen edges, icons, and other objects.
    """

    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        """Initialize proximity sensor."""
        self.screen_width = screen_width
        self.screen_height = screen_height

    def get_edge_distances(self, x: float, y: float) -> Dict[str, float]:
        """
        Get distances to screen edges.

        Args:
            x: Position x
            y: Position y

        Returns:
            Dictionary with distances to each edge
        """
        return {
            'top': y,
            'bottom': self.screen_height - y,
            'left': x,
            'right': self.screen_width - x
        }

    def is_near_edge(self, x: float, y: float, threshold: float = 100) -> Dict[str, bool]:
        """Check if position is near any edge."""
        distances = self.get_edge_distances(x, y)

        return {
            edge: distance < threshold
            for edge, distance in distances.items()
        }

    def encode_proximity(self, x: float, y: float,
                         icon_positions: List[Dict[str, float]]) -> np.ndarray:
        """
        Encode proximity information.

        Returns:
            Array of [edge_top_norm, edge_bottom_norm, edge_left_norm, edge_right_norm,
                     nearest_icon_distance_norm, nearest_icon_angle_sin, nearest_icon_angle_cos,
                     icon_count_nearby]
        """
        # Edge distances (normalized)
        edge_distances = self.get_edge_distances(x, y)
        edge_top_norm = min(edge_distances['top'] / 200, 1.0)
        edge_bottom_norm = min(edge_distances['bottom'] / 200, 1.0)
        edge_left_norm = min(edge_distances['left'] / 200, 1.0)
        edge_right_norm = min(edge_distances['right'] / 200, 1.0)

        # Nearest icon
        if icon_positions:
            min_dist = float('inf')
            nearest_icon = None

            for icon in icon_positions:
                icon_x = icon['x'] + icon.get('width', 80) / 2
                icon_y = icon['y'] + icon.get('height', 80) / 2
                dist = SensoryEncoder.calculate_distance(x, y, icon_x, icon_y)

                if dist < min_dist:
                    min_dist = dist
                    nearest_icon = (icon_x, icon_y)

            if nearest_icon:
                icon_dist_norm = min(min_dist / 300, 1.0)
                icon_angle = SensoryEncoder.calculate_angle(x, y, nearest_icon[0], nearest_icon[1])
                icon_angle_sin = math.sin(icon_angle)
                icon_angle_cos = math.cos(icon_angle)

                # Count nearby icons (within 200 pixels)
                icon_count = sum(1 for icon in icon_positions
                                 if SensoryEncoder.calculate_distance(
                                     x, y,
                                     icon['x'] + icon.get('width', 80) / 2,
                                     icon['y'] + icon.get('height', 80) / 2
                                 ) < 200)
            else:
                icon_dist_norm = 1.0
                icon_angle_sin = 0.0
                icon_angle_cos = 1.0
                icon_count = 0
        else:
            icon_dist_norm = 1.0
            icon_angle_sin = 0.0
            icon_angle_cos = 1.0
            icon_count = 0

        return np.array([
            edge_top_norm, edge_bottom_norm, edge_left_norm, edge_right_norm,
            icon_dist_norm, icon_angle_sin, icon_angle_cos,
            min(icon_count / 5.0, 1.0)  # Normalize icon count
        ])


class CompleteSensorySystem:
    """
    Complete sensory system combining all sensors.

    Provides comprehensive environmental awareness for the creature.
    """

    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        """Initialize complete sensory system."""
        self.encoder = SensoryEncoder()
        self.mouse_tracker = MouseTracker()
        self.layout_analyzer = ScreenLayoutAnalyzer(screen_width, screen_height)
        self.proximity_sensor = ProximitySensor(screen_width, screen_height)

        self.screen_width = screen_width
        self.screen_height = screen_height

    def set_screen_size(self, screen_width: int, screen_height: int):
        """Use the actual screen size for layout, edge and mouse sensing."""
        for sensor in (self, self.layout_analyzer, self.proximity_sensor):
            sensor.screen_width = screen_width
            sensor.screen_height = screen_height

    def update_mouse_position(self, x: float, y: float):
        """Update mouse tracking."""
        self.mouse_tracker.update(x, y)

    def get_complete_sensory_input(self, creature_x: float, creature_y: float) -> np.ndarray:
        """
        Get complete sensory input vector for neural networks.

        Args:
            creature_x: Creature x position
            creature_y: Creature y position

        Returns:
            Complete sensory vector (approximately 30 values)
        """
        # Time encoding (6 values)
        time_features = self.encoder.encode_time_of_day()

        # Day of week encoding (3 values)
        day_features = self.encoder.encode_day_of_week()

        # Mouse tracking (11 values)
        mouse_features = self.mouse_tracker.encode(
            creature_x, creature_y,
            self.screen_width, self.screen_height
        )

        # Icon positions (rescanned periodically so layout changes are noticed)
        self.layout_analyzer.refresh_icons()
        icons = self.layout_analyzer.detected_icons

        # Proximity sensing (8 values)
        proximity_features = self.proximity_sensor.encode_proximity(
            creature_x, creature_y, icons
        )

        # Combine all features
        complete_input = np.concatenate([
            time_features,      # 6
            day_features,       # 3
            mouse_features,     # 11
            proximity_features  # 8
        ])  # Total: 28 values

        return complete_input

    def get_state_dict(self, creature_x: float, creature_y: float) -> Dict[str, Any]:
        """
        Get complete state as dictionary for other systems.

        Args:
            creature_x: Creature x position
            creature_y: Creature y position

        Returns:
            Dictionary with all sensory information
        """
        sensory_vector = self.get_complete_sensory_input(creature_x, creature_y)

        # Get edge distances
        edge_distances = self.proximity_sensor.get_edge_distances(creature_x, creature_y)

        # Get nearest hiding spot
        hiding_spots = self.layout_analyzer.get_hiding_spots(creature_x, creature_y)
        nearest_hiding = hiding_spots[0] if hiding_spots else None

        return {
            'sensory_vector': sensory_vector.tolist(),
            'pos_x': creature_x,
            'pos_y': creature_y,
            'mouse_x': self.mouse_tracker.current_position[0],
            'mouse_y': self.mouse_tracker.current_position[1],
            'mouse_velocity': self.mouse_tracker.current_velocity,
            'mouse_speed': self.mouse_tracker.get_velocity_magnitude(),
            'edge_distances': edge_distances,
            'edge_top': edge_distances['top'],
            'edge_bottom': edge_distances['bottom'],
            'edge_left': edge_distances['left'],
            'edge_right': edge_distances['right'],
            'nearest_hiding_spot': nearest_hiding,
            'time_of_day': datetime.datetime.now().hour,
            'is_weekend': datetime.datetime.now().weekday() >= 5
        }


class HidingSpotMemory:
    """
    Learns which hiding spots (desktop icons) work well.

    Each spot keeps a running average of the reward earned while hiding there;
    spots are chosen greedily by that value, with occasional exploration.
    """

    def __init__(self, exploration: float = 0.1):
        self.exploration = exploration
        self.values = {}  # "x,y" -> [average reward (0-1), visits]

    @staticmethod
    def key(spot: Dict[str, float]) -> str:
        return f"{int(spot['x'])},{int(spot['y'])}"

    def value(self, spot: Dict[str, float]) -> float:
        """Learned value of a spot (0.5 if never tried)."""
        return self.values.get(self.key(spot), [0.5, 0])[0]

    def choose(self, spots: List[Dict[str, float]]) -> Optional[Dict[str, float]]:
        """Pick the best-known spot, or a random one some of the time."""
        if not spots:
            return None
        if random.random() < self.exploration:
            return random.choice(spots)
        return max(spots, key=self.value)

    def record(self, spot: Dict[str, float], reward01: float):
        """Update a spot's value with the reward earned while hiding there."""
        value, visits = self.values.get(self.key(spot), [0.5, 0])
        visits += 1
        value += (reward01 - value) / min(visits, 20)
        self.values[self.key(spot)] = [value, visits]

    def to_dict(self) -> Dict[str, Any]:
        return {'values': self.values}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HidingSpotMemory':
        memory = cls()
        memory.values = {k: list(v) for k, v in data.get('values', {}).items()}
        return memory
