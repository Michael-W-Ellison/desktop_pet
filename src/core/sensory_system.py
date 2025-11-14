"""
Sensory input system for environmental awareness.

Gives creatures the ability to "sense" their environment:
- Screen layout and icon positions
- Mouse position and velocity
- Time of day and context
- Proximity to objects and edges
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
import datetime
import math


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

    def detect_desktop_icons(self) -> List[Dict[str, float]]:
        """
        Detect desktop icons (Windows-specific, simplified version).

        In a full implementation, this would use Windows API to get actual icon positions.
        For now, we'll simulate common icon positions.

        Returns:
            List of icon positions
        """
        # Simplified: Assume standard desktop icon grid
        # Real implementation would use win32api to get actual positions
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
        if not self.detected_icons:
            self.detected_icons = self.detect_desktop_icons()

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
        if not self.detected_icons:
            self.detected_icons = self.detect_desktop_icons()

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

        # Icon positions
        icons = self.layout_analyzer.detected_icons
        if not icons:
            icons = self.layout_analyzer.detect_desktop_icons()

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
