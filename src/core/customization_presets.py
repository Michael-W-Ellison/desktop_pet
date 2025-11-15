"""
Phase 14: Customization Presets System

Allows saving and loading pet outfits and room layouts.
"""
import time
from typing import Dict, Any, List, Optional
from enum import Enum


class PresetType(Enum):
    """Types of presets."""
    OUTFIT = "outfit"              # Pet appearance preset
    ROOM = "room"                  # Room decoration preset
    COMPLETE = "complete"          # Both outfit and room


class CustomizationPreset:
    """Represents a saved customization preset."""

    def __init__(self, preset_id: str, name: str, preset_type: PresetType):
        """
        Initialize preset.

        Args:
            preset_id: Unique preset ID
            name: Preset name
            preset_type: Type of preset
        """
        self.preset_id = preset_id
        self.name = name
        self.preset_type = preset_type
        self.description: str = ""

        # Saved data
        self.pet_data: Optional[Dict[str, Any]] = None
        self.room_data: Optional[Dict[str, Any]] = None
        self.furniture_data: Optional[Dict[str, Any]] = None

        # Metadata
        self.created_timestamp = time.time()
        self.modified_timestamp = time.time()
        self.times_applied = 0
        self.favorite = False
        self.tags: List[str] = []

        # Thumbnail/preview (would be image data in real implementation)
        self.thumbnail: Optional[str] = None

    def update_data(self, pet_data: Optional[Dict[str, Any]] = None,
                   room_data: Optional[Dict[str, Any]] = None,
                   furniture_data: Optional[Dict[str, Any]] = None):
        """Update preset data."""
        if pet_data is not None:
            self.pet_data = pet_data
        if room_data is not None:
            self.room_data = room_data
        if furniture_data is not None:
            self.furniture_data = furniture_data

        self.modified_timestamp = time.time()

    def apply(self):
        """Record that preset was applied."""
        self.times_applied += 1

    def add_tag(self, tag: str):
        """Add tag to preset."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str):
        """Remove tag from preset."""
        if tag in self.tags:
            self.tags.remove(tag)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'preset_id': self.preset_id,
            'name': self.name,
            'preset_type': self.preset_type.value,
            'description': self.description,
            'pet_data': self.pet_data,
            'room_data': self.room_data,
            'furniture_data': self.furniture_data,
            'created_timestamp': self.created_timestamp,
            'modified_timestamp': self.modified_timestamp,
            'times_applied': self.times_applied,
            'favorite': self.favorite,
            'tags': self.tags,
            'thumbnail': self.thumbnail
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomizationPreset':
        """Deserialize from dictionary."""
        preset = cls(
            preset_id=data['preset_id'],
            name=data['name'],
            preset_type=PresetType(data['preset_type'])
        )
        preset.description = data.get('description', '')
        preset.pet_data = data.get('pet_data')
        preset.room_data = data.get('room_data')
        preset.furniture_data = data.get('furniture_data')
        preset.created_timestamp = data.get('created_timestamp', time.time())
        preset.modified_timestamp = data.get('modified_timestamp', time.time())
        preset.times_applied = data.get('times_applied', 0)
        preset.favorite = data.get('favorite', False)
        preset.tags = data.get('tags', [])
        preset.thumbnail = data.get('thumbnail')
        return preset


class CustomizationPresets:
    """
    Manages customization presets.

    Features:
    - Save pet outfit presets
    - Save room decoration presets
    - Save complete looks (outfit + room)
    - Quick-apply presets
    - Organize with tags
    - Favorite presets
    """

    def __init__(self):
        """Initialize presets system."""
        # Stored presets
        self.presets: Dict[str, CustomizationPreset] = {}

        # Quick access
        self.favorite_presets: List[str] = []  # preset_ids
        self.recent_presets: List[str] = []    # preset_ids (most recent first)

        # Settings
        self.max_presets = 50
        self.max_recent = 10

        # Statistics
        self.total_presets_created = 0
        self.total_presets_applied = 0
        self.total_presets_deleted = 0
        self.most_used_preset: Optional[str] = None

        # Preset counter for unique IDs
        self._preset_counter = 0

    def create_preset(self, name: str, preset_type: PresetType,
                     description: str = "") -> Optional[CustomizationPreset]:
        """
        Create a new preset.

        Args:
            name: Preset name
            preset_type: Type of preset
            description: Preset description

        Returns:
            CustomizationPreset if successful
        """
        # Check if at max capacity
        if len(self.presets) >= self.max_presets:
            return None

        # Generate unique ID
        self._preset_counter += 1
        preset_id = f"preset_{self._preset_counter}_{int(time.time())}"

        # Create preset
        preset = CustomizationPreset(preset_id, name, preset_type)
        preset.description = description

        # Store preset
        self.presets[preset_id] = preset
        self.total_presets_created += 1

        return preset

    def save_outfit_preset(self, name: str, pet_customization: Any,
                          description: str = "") -> Optional[CustomizationPreset]:
        """
        Save current pet outfit as preset.

        Args:
            name: Preset name
            pet_customization: PetCustomization instance
            description: Preset description

        Returns:
            Created preset
        """
        preset = self.create_preset(name, PresetType.OUTFIT, description)
        if preset:
            preset.update_data(pet_data=pet_customization.to_dict())
            self._add_to_recent(preset.preset_id)
        return preset

    def save_room_preset(self, name: str, room_decoration: Any,
                        furniture_placement: Any,
                        description: str = "") -> Optional[CustomizationPreset]:
        """
        Save current room layout as preset.

        Args:
            name: Preset name
            room_decoration: RoomDecoration instance
            furniture_placement: FurniturePlacement instance
            description: Preset description

        Returns:
            Created preset
        """
        preset = self.create_preset(name, PresetType.ROOM, description)
        if preset:
            preset.update_data(
                room_data=room_decoration.to_dict(),
                furniture_data=furniture_placement.to_dict()
            )
            self._add_to_recent(preset.preset_id)
        return preset

    def save_complete_preset(self, name: str, pet_customization: Any,
                           room_decoration: Any, furniture_placement: Any,
                           description: str = "") -> Optional[CustomizationPreset]:
        """
        Save complete look (outfit + room).

        Args:
            name: Preset name
            pet_customization: PetCustomization instance
            room_decoration: RoomDecoration instance
            furniture_placement: FurniturePlacement instance
            description: Preset description

        Returns:
            Created preset
        """
        preset = self.create_preset(name, PresetType.COMPLETE, description)
        if preset:
            preset.update_data(
                pet_data=pet_customization.to_dict(),
                room_data=room_decoration.to_dict(),
                furniture_data=furniture_placement.to_dict()
            )
            self._add_to_recent(preset.preset_id)
        return preset

    def apply_preset(self, preset_id: str) -> Optional[Dict[str, Any]]:
        """
        Apply a preset.

        Args:
            preset_id: Preset to apply

        Returns:
            Preset data to apply
        """
        preset = self.presets.get(preset_id)
        if not preset:
            return None

        # Record application
        preset.apply()
        self.total_presets_applied += 1
        self._add_to_recent(preset_id)
        self._update_most_used()

        # Return data to apply
        return {
            'preset_type': preset.preset_type,
            'pet_data': preset.pet_data,
            'room_data': preset.room_data,
            'furniture_data': preset.furniture_data
        }

    def update_preset(self, preset_id: str, pet_customization: Any = None,
                     room_decoration: Any = None,
                     furniture_placement: Any = None) -> bool:
        """
        Update existing preset with current state.

        Args:
            preset_id: Preset to update
            pet_customization: PetCustomization instance (optional)
            room_decoration: RoomDecoration instance (optional)
            furniture_placement: FurniturePlacement instance (optional)

        Returns:
            True if successful
        """
        preset = self.presets.get(preset_id)
        if not preset:
            return False

        # Update data based on preset type
        if preset.preset_type == PresetType.OUTFIT and pet_customization:
            preset.update_data(pet_data=pet_customization.to_dict())
        elif preset.preset_type == PresetType.ROOM and room_decoration and furniture_placement:
            preset.update_data(
                room_data=room_decoration.to_dict(),
                furniture_data=furniture_placement.to_dict()
            )
        elif preset.preset_type == PresetType.COMPLETE:
            pet_data = pet_customization.to_dict() if pet_customization else None
            room_data = room_decoration.to_dict() if room_decoration else None
            furniture_data = furniture_placement.to_dict() if furniture_placement else None
            preset.update_data(
                pet_data=pet_data,
                room_data=room_data,
                furniture_data=furniture_data
            )

        return True

    def delete_preset(self, preset_id: str) -> bool:
        """Delete a preset."""
        if preset_id in self.presets:
            del self.presets[preset_id]
            self.total_presets_deleted += 1

            # Remove from favorites and recent
            if preset_id in self.favorite_presets:
                self.favorite_presets.remove(preset_id)
            if preset_id in self.recent_presets:
                self.recent_presets.remove(preset_id)

            return True
        return False

    def set_favorite(self, preset_id: str, favorite: bool = True):
        """Mark preset as favorite."""
        preset = self.presets.get(preset_id)
        if preset:
            preset.favorite = favorite

            if favorite and preset_id not in self.favorite_presets:
                self.favorite_presets.append(preset_id)
            elif not favorite and preset_id in self.favorite_presets:
                self.favorite_presets.remove(preset_id)

    def _add_to_recent(self, preset_id: str):
        """Add preset to recent list."""
        # Remove if already in list
        if preset_id in self.recent_presets:
            self.recent_presets.remove(preset_id)

        # Add to front
        self.recent_presets.insert(0, preset_id)

        # Trim to max size
        if len(self.recent_presets) > self.max_recent:
            self.recent_presets = self.recent_presets[:self.max_recent]

    def _update_most_used(self):
        """Update most used preset."""
        if not self.presets:
            return

        most_used = max(
            self.presets.values(),
            key=lambda p: p.times_applied
        )

        if most_used.times_applied > 0:
            self.most_used_preset = most_used.preset_id

    def get_preset(self, preset_id: str) -> Optional[CustomizationPreset]:
        """Get preset by ID."""
        return self.presets.get(preset_id)

    def get_presets_by_type(self, preset_type: PresetType) -> List[CustomizationPreset]:
        """Get all presets of a type."""
        return [
            preset for preset in self.presets.values()
            if preset.preset_type == preset_type
        ]

    def get_favorite_presets(self) -> List[CustomizationPreset]:
        """Get all favorite presets."""
        return [
            self.presets[pid] for pid in self.favorite_presets
            if pid in self.presets
        ]

    def get_recent_presets(self) -> List[CustomizationPreset]:
        """Get recently used presets."""
        return [
            self.presets[pid] for pid in self.recent_presets
            if pid in self.presets
        ]

    def get_presets_by_tag(self, tag: str) -> List[CustomizationPreset]:
        """Get presets with a specific tag."""
        return [
            preset for preset in self.presets.values()
            if tag in preset.tags
        ]

    def search_presets(self, query: str) -> List[CustomizationPreset]:
        """Search presets by name or description."""
        query_lower = query.lower()
        return [
            preset for preset in self.presets.values()
            if query_lower in preset.name.lower() or
               query_lower in preset.description.lower()
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get presets statistics."""
        return {
            'total_presets': len(self.presets),
            'outfit_presets': len(self.get_presets_by_type(PresetType.OUTFIT)),
            'room_presets': len(self.get_presets_by_type(PresetType.ROOM)),
            'complete_presets': len(self.get_presets_by_type(PresetType.COMPLETE)),
            'favorite_presets': len(self.favorite_presets),
            'total_created': self.total_presets_created,
            'total_applied': self.total_presets_applied,
            'total_deleted': self.total_presets_deleted,
            'most_used_preset': self.most_used_preset,
            'capacity_usage': (len(self.presets) / self.max_presets * 100)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'presets': {
                preset_id: preset.to_dict()
                for preset_id, preset in self.presets.items()
            },
            'favorite_presets': self.favorite_presets,
            'recent_presets': self.recent_presets,
            'max_presets': self.max_presets,
            'max_recent': self.max_recent,
            'total_presets_created': self.total_presets_created,
            'total_presets_applied': self.total_presets_applied,
            'total_presets_deleted': self.total_presets_deleted,
            'most_used_preset': self.most_used_preset,
            'preset_counter': self._preset_counter
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomizationPresets':
        """Deserialize from dictionary."""
        presets_system = cls()

        # Restore presets
        presets_data = data.get('presets', {})
        for preset_id, preset_data in presets_data.items():
            presets_system.presets[preset_id] = CustomizationPreset.from_dict(preset_data)

        presets_system.favorite_presets = data.get('favorite_presets', [])
        presets_system.recent_presets = data.get('recent_presets', [])
        presets_system.max_presets = data.get('max_presets', 50)
        presets_system.max_recent = data.get('max_recent', 10)
        presets_system.total_presets_created = data.get('total_presets_created', 0)
        presets_system.total_presets_applied = data.get('total_presets_applied', 0)
        presets_system.total_presets_deleted = data.get('total_presets_deleted', 0)
        presets_system.most_used_preset = data.get('most_used_preset')
        presets_system._preset_counter = data.get('preset_counter', 0)

        return presets_system
