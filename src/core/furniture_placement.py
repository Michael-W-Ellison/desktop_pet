"""
Phase 14: Furniture Placement System

Manages furniture positioning and room layouts.
"""
import time
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class FurnitureCategory(Enum):
    """Furniture categories."""
    BED = "bed"                    # Pet beds
    FOOD_BOWL = "food_bowl"        # Food and water bowls
    TOY_BOX = "toy_box"            # Toy storage
    SCRATCHING = "scratching"      # Scratching posts
    PERCH = "perch"                # Perches, cat trees
    DECORATION = "decoration"      # Decorative items
    PLANT = "plant"                # Plants
    LIGHTING = "lighting"          # Lamps, lights
    SEATING = "seating"            # Cushions, chairs
    STORAGE = "storage"            # Shelves, cabinets


class FurnitureSize(Enum):
    """Furniture size categories."""
    TINY = "tiny"                  # 1x1 grid
    SMALL = "small"                # 1x2 or 2x2 grid
    MEDIUM = "medium"              # 2x3 or 3x3 grid
    LARGE = "large"                # 3x4 or 4x4 grid
    XLARGE = "xlarge"              # 4x5+ grid


class PlacedFurniture:
    """Represents a piece of furniture placed in the room."""

    def __init__(self, furniture_id: str, item_id: str, name: str,
                 category: FurnitureCategory, size: FurnitureSize):
        """
        Initialize placed furniture.

        Args:
            furniture_id: Unique placement ID
            item_id: Item type ID
            name: Furniture name
            category: Furniture category
            size: Furniture size
        """
        self.furniture_id = furniture_id
        self.item_id = item_id
        self.name = name
        self.category = category
        self.size = size

        # Position (grid coordinates)
        self.x = 0
        self.y = 0
        self.z_index = 0  # Layering order

        # Rotation (0, 90, 180, 270 degrees)
        self.rotation = 0

        # Size (grid units)
        self.width = 1
        self.height = 1

        # State
        self.locked = False            # Prevent accidental moving
        self.visible = True
        self.interactable = True

        # Placement info
        self.placed_timestamp = time.time()
        self.times_moved = 0

    def set_position(self, x: int, y: int):
        """Set furniture position."""
        self.x = x
        self.y = y
        self.times_moved += 1

    def rotate(self, degrees: int = 90):
        """Rotate furniture."""
        self.rotation = (self.rotation + degrees) % 360
        # Swap width/height if rotating 90 or 270
        if degrees % 180 != 0:
            self.width, self.height = self.height, self.width

    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Get furniture bounding box (x1, y1, x2, y2)."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def occupies_position(self, x: int, y: int) -> bool:
        """Check if furniture occupies a position."""
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'furniture_id': self.furniture_id,
            'item_id': self.item_id,
            'name': self.name,
            'category': self.category.value,
            'size': self.size.value,
            'x': self.x,
            'y': self.y,
            'z_index': self.z_index,
            'rotation': self.rotation,
            'width': self.width,
            'height': self.height,
            'locked': self.locked,
            'visible': self.visible,
            'interactable': self.interactable,
            'placed_timestamp': self.placed_timestamp,
            'times_moved': self.times_moved
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlacedFurniture':
        """Deserialize from dictionary."""
        furniture = cls(
            furniture_id=data['furniture_id'],
            item_id=data['item_id'],
            name=data['name'],
            category=FurnitureCategory(data['category']),
            size=FurnitureSize(data['size'])
        )
        furniture.x = data.get('x', 0)
        furniture.y = data.get('y', 0)
        furniture.z_index = data.get('z_index', 0)
        furniture.rotation = data.get('rotation', 0)
        furniture.width = data.get('width', 1)
        furniture.height = data.get('height', 1)
        furniture.locked = data.get('locked', False)
        furniture.visible = data.get('visible', True)
        furniture.interactable = data.get('interactable', True)
        furniture.placed_timestamp = data.get('placed_timestamp', time.time())
        furniture.times_moved = data.get('times_moved', 0)
        return furniture


class FurniturePlacement:
    """
    Manages furniture placement in the room.

    Features:
    - Place furniture at coordinates
    - Move and rotate furniture
    - Collision detection
    - Grid-based positioning
    - Layering (z-index)
    - Room layouts/presets
    """

    def __init__(self, room_width: int = 20, room_height: int = 15):
        """
        Initialize furniture placement system.

        Args:
            room_width: Room width in grid units
            room_height: Room height in grid units
        """
        # Room dimensions
        self.room_width = room_width
        self.room_height = room_height

        # Placed furniture
        self.placed_furniture: Dict[str, PlacedFurniture] = {}

        # Grid settings
        self.grid_size = 32  # Pixels per grid unit
        self.snap_to_grid = True

        # Placement counter for unique IDs
        self._placement_counter = 0

        # Statistics
        self.total_placements = 0
        self.total_moves = 0
        self.total_removals = 0

    def place_furniture(self, item_id: str, name: str, category: FurnitureCategory,
                       size: FurnitureSize, x: int, y: int,
                       width: int = 1, height: int = 1) -> Optional[PlacedFurniture]:
        """
        Place furniture in the room.

        Args:
            item_id: Item type ID
            name: Furniture name
            category: Furniture category
            size: Furniture size
            x: X coordinate
            y: Y coordinate
            width: Width in grid units
            height: Height in grid units

        Returns:
            PlacedFurniture if successful, None otherwise
        """
        # Snap to grid if enabled
        if self.snap_to_grid:
            x = round(x)
            y = round(y)

        # Check if position is valid
        if not self._is_position_valid(x, y, width, height):
            return None

        # Check for collisions
        if self._check_collision(x, y, width, height):
            return None

        # Generate unique ID
        self._placement_counter += 1
        furniture_id = f"placed_{self._placement_counter}_{int(time.time())}"

        # Create placed furniture
        furniture = PlacedFurniture(furniture_id, item_id, name, category, size)
        furniture.set_position(x, y)
        furniture.width = width
        furniture.height = height
        furniture.z_index = len(self.placed_furniture)  # Layer on top

        # Add to collection
        self.placed_furniture[furniture_id] = furniture
        self.total_placements += 1

        return furniture

    def move_furniture(self, furniture_id: str, new_x: int, new_y: int) -> bool:
        """
        Move furniture to new position.

        Args:
            furniture_id: Furniture to move
            new_x: New X coordinate
            new_y: New Y coordinate

        Returns:
            True if successful
        """
        furniture = self.placed_furniture.get(furniture_id)
        if not furniture or furniture.locked:
            return False

        # Snap to grid
        if self.snap_to_grid:
            new_x = round(new_x)
            new_y = round(new_y)

        # Check if new position is valid
        if not self._is_position_valid(new_x, new_y, furniture.width, furniture.height):
            return False

        # Check for collisions (excluding self)
        if self._check_collision(new_x, new_y, furniture.width, furniture.height,
                                 exclude_id=furniture_id):
            return False

        # Move furniture
        furniture.set_position(new_x, new_y)
        self.total_moves += 1

        return True

    def rotate_furniture(self, furniture_id: str, degrees: int = 90) -> bool:
        """
        Rotate furniture.

        Args:
            furniture_id: Furniture to rotate
            degrees: Rotation degrees (90, 180, 270)

        Returns:
            True if successful
        """
        furniture = self.placed_furniture.get(furniture_id)
        if not furniture or furniture.locked:
            return False

        # Calculate new dimensions after rotation
        new_width = furniture.width
        new_height = furniture.height
        if degrees % 180 != 0:
            new_width, new_height = new_height, new_width

        # Check if rotation causes collision
        if self._check_collision(furniture.x, furniture.y, new_width, new_height,
                                 exclude_id=furniture_id):
            return False

        # Rotate
        furniture.rotate(degrees)
        return True

    def remove_furniture(self, furniture_id: str) -> bool:
        """Remove furniture from room."""
        if furniture_id in self.placed_furniture:
            furniture = self.placed_furniture[furniture_id]
            if not furniture.locked:
                del self.placed_furniture[furniture_id]
                self.total_removals += 1
                return True
        return False

    def lock_furniture(self, furniture_id: str, locked: bool = True):
        """Lock or unlock furniture to prevent moving."""
        furniture = self.placed_furniture.get(furniture_id)
        if furniture:
            furniture.locked = locked

    def set_z_index(self, furniture_id: str, z_index: int):
        """Set furniture layering order."""
        furniture = self.placed_furniture.get(furniture_id)
        if furniture:
            furniture.z_index = z_index

    def bring_to_front(self, furniture_id: str):
        """Bring furniture to front (highest z-index)."""
        furniture = self.placed_furniture.get(furniture_id)
        if furniture:
            max_z = max((f.z_index for f in self.placed_furniture.values()), default=0)
            furniture.z_index = max_z + 1

    def send_to_back(self, furniture_id: str):
        """Send furniture to back (lowest z-index)."""
        furniture = self.placed_furniture.get(furniture_id)
        if furniture:
            min_z = min((f.z_index for f in self.placed_furniture.values()), default=0)
            furniture.z_index = min_z - 1

    def _is_position_valid(self, x: int, y: int, width: int, height: int) -> bool:
        """Check if position is within room bounds."""
        return (0 <= x and x + width <= self.room_width and
                0 <= y and y + height <= self.room_height)

    def _check_collision(self, x: int, y: int, width: int, height: int,
                        exclude_id: Optional[str] = None) -> bool:
        """
        Check if position collides with existing furniture.

        Args:
            x: X coordinate
            y: Y coordinate
            width: Width
            height: Height
            exclude_id: Furniture ID to exclude from check

        Returns:
            True if collision detected
        """
        for furniture_id, furniture in self.placed_furniture.items():
            if furniture_id == exclude_id:
                continue

            # Check bounding box overlap
            if not (x + width <= furniture.x or
                   x >= furniture.x + furniture.width or
                   y + height <= furniture.y or
                   y >= furniture.y + furniture.height):
                return True

        return False

    def get_furniture_at_position(self, x: int, y: int) -> List[PlacedFurniture]:
        """Get all furniture at a position (sorted by z-index)."""
        furniture_list = [
            f for f in self.placed_furniture.values()
            if f.occupies_position(x, y)
        ]
        furniture_list.sort(key=lambda f: f.z_index, reverse=True)
        return furniture_list

    def get_furniture_by_category(self, category: FurnitureCategory) -> List[PlacedFurniture]:
        """Get all placed furniture of a category."""
        return [
            f for f in self.placed_furniture.values()
            if f.category == category
        ]

    def clear_room(self):
        """Remove all furniture."""
        self.placed_furniture.clear()

    def get_room_capacity(self) -> float:
        """Get percentage of room occupied by furniture (0-100)."""
        total_cells = self.room_width * self.room_height
        occupied_cells = sum(
            f.width * f.height
            for f in self.placed_furniture.values()
        )
        return (occupied_cells / total_cells * 100) if total_cells > 0 else 0.0

    def get_layout_summary(self) -> Dict[str, Any]:
        """Get summary of current layout."""
        categories = {}
        for furniture in self.placed_furniture.values():
            cat = furniture.category.value
            categories[cat] = categories.get(cat, 0) + 1

        return {
            'total_items': len(self.placed_furniture),
            'room_capacity': self.get_room_capacity(),
            'items_by_category': categories,
            'room_size': {
                'width': self.room_width,
                'height': self.room_height
            }
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get placement statistics."""
        return {
            'total_placements': self.total_placements,
            'total_moves': self.total_moves,
            'total_removals': self.total_removals,
            'current_items': len(self.placed_furniture),
            'room_capacity': self.get_room_capacity(),
            'locked_items': sum(1 for f in self.placed_furniture.values() if f.locked)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'room_width': self.room_width,
            'room_height': self.room_height,
            'placed_furniture': {
                furn_id: furn.to_dict()
                for furn_id, furn in self.placed_furniture.items()
            },
            'grid_size': self.grid_size,
            'snap_to_grid': self.snap_to_grid,
            'placement_counter': self._placement_counter,
            'total_placements': self.total_placements,
            'total_moves': self.total_moves,
            'total_removals': self.total_removals
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FurniturePlacement':
        """Deserialize from dictionary."""
        placement = cls(
            room_width=data.get('room_width', 20),
            room_height=data.get('room_height', 15)
        )

        # Restore furniture
        furniture_data = data.get('placed_furniture', {})
        for furn_id, furn_data in furniture_data.items():
            placement.placed_furniture[furn_id] = PlacedFurniture.from_dict(furn_data)

        placement.grid_size = data.get('grid_size', 32)
        placement.snap_to_grid = data.get('snap_to_grid', True)
        placement._placement_counter = data.get('placement_counter', 0)
        placement.total_placements = data.get('total_placements', 0)
        placement.total_moves = data.get('total_moves', 0)
        placement.total_removals = data.get('total_removals', 0)

        return placement
