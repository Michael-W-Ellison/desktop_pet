"""
Phase 11: Photo Album System

Organizes screenshots into albums and collections.
"""
import time
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum


class AlbumType(Enum):
    """Type of photo album."""
    GENERAL = "general"
    MILESTONES = "milestones"
    TRAINING = "training"
    FUNNY_MOMENTS = "funny_moments"
    GROWTH = "growth"
    FRIENDS = "friends"
    ADVENTURES = "adventures"
    FAVORITES = "favorites"
    DAILY_LIFE = "daily_life"
    SPECIAL_EVENTS = "special_events"


class SortOrder(Enum):
    """Photo sort order."""
    DATE_NEWEST = "date_newest"
    DATE_OLDEST = "date_oldest"
    MOST_VIEWED = "most_viewed"
    ALPHABETICAL = "alphabetical"
    RANDOM = "random"


class PhotoAlbum:
    """Represents a photo album/collection."""

    def __init__(self, album_id: str, name: str, album_type: AlbumType = AlbumType.GENERAL):
        """
        Initialize photo album.

        Args:
            album_id: Unique album identifier
            name: Album name
            album_type: Type of album
        """
        self.album_id = album_id
        self.name = name
        self.album_type = album_type
        self.description: str = ""
        self.created_timestamp = time.time()
        self.created_date_string = datetime.fromtimestamp(
            self.created_timestamp
        ).strftime("%Y-%m-%d")

        # Photo management
        self.photo_ids: List[str] = []
        self.cover_photo_id: Optional[str] = None

        # Organization
        self.tags: Set[str] = set()
        self.is_favorite: bool = False

        # Access
        self.view_count: int = 0
        self.last_viewed: float = 0.0

    def add_photo(self, photo_id: str):
        """Add a photo to the album."""
        if photo_id not in self.photo_ids:
            self.photo_ids.append(photo_id)

            # Auto-set cover photo if first photo
            if not self.cover_photo_id:
                self.cover_photo_id = photo_id

    def remove_photo(self, photo_id: str) -> bool:
        """Remove a photo from the album."""
        if photo_id in self.photo_ids:
            self.photo_ids.remove(photo_id)

            # Update cover photo if needed
            if self.cover_photo_id == photo_id:
                self.cover_photo_id = self.photo_ids[0] if self.photo_ids else None

            return True
        return False

    def set_cover_photo(self, photo_id: str) -> bool:
        """Set the album cover photo."""
        if photo_id in self.photo_ids:
            self.cover_photo_id = photo_id
            return True
        return False

    def mark_as_viewed(self):
        """Mark album as viewed."""
        self.view_count += 1
        self.last_viewed = time.time()

    def get_photo_count(self) -> int:
        """Get number of photos in album."""
        return len(self.photo_ids)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'album_id': self.album_id,
            'name': self.name,
            'album_type': self.album_type.value,
            'description': self.description,
            'created_timestamp': self.created_timestamp,
            'created_date_string': self.created_date_string,
            'photo_ids': self.photo_ids,
            'cover_photo_id': self.cover_photo_id,
            'tags': list(self.tags),
            'is_favorite': self.is_favorite,
            'view_count': self.view_count,
            'last_viewed': self.last_viewed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhotoAlbum':
        """Deserialize from dictionary."""
        album = cls(
            album_id=data['album_id'],
            name=data['name'],
            album_type=AlbumType(data['album_type'])
        )
        album.description = data.get('description', '')
        album.created_timestamp = data['created_timestamp']
        album.created_date_string = data['created_date_string']
        album.photo_ids = data.get('photo_ids', [])
        album.cover_photo_id = data.get('cover_photo_id')
        album.tags = set(data.get('tags', []))
        album.is_favorite = data.get('is_favorite', False)
        album.view_count = data.get('view_count', 0)
        album.last_viewed = data.get('last_viewed', 0.0)
        return album


class PhotoAlbumSystem:
    """
    Manages photo albums and collections.

    Features:
    - Create and organize photo albums
    - Automatic album creation (by month, event, etc.)
    - Smart albums (favorites, recent, etc.)
    - Album slideshow
    - Export albums
    - Share albums
    """

    def __init__(self):
        """Initialize photo album system."""
        # Album storage
        self.albums: Dict[str, PhotoAlbum] = {}
        self.album_order: List[str] = []

        # Smart albums (auto-populated)
        self.smart_albums: Dict[str, Dict[str, Any]] = {}

        # Statistics
        self.total_albums = 0
        self.total_photos_in_albums = 0

        # Settings
        self.auto_create_monthly_albums = True
        self.auto_create_event_albums = True
        self.default_sort_order = SortOrder.DATE_NEWEST

        # Create default smart albums
        self._create_default_smart_albums()

    def _create_default_smart_albums(self):
        """Create default smart albums."""
        self.smart_albums = {
            'all_photos': {
                'name': 'All Photos',
                'description': 'All captured photos',
                'filter': lambda screenshot: True
            },
            'favorites': {
                'name': 'Favorites',
                'description': 'Favorite photos',
                'filter': lambda screenshot: screenshot.favorite
            },
            'recent': {
                'name': 'Recent',
                'description': 'Photos from the last 7 days',
                'filter': lambda screenshot: (time.time() - screenshot.timestamp) <= (7 * 24 * 3600)
            },
            'this_month': {
                'name': 'This Month',
                'description': 'Photos from this month',
                'filter': lambda screenshot: (
                    datetime.fromtimestamp(screenshot.timestamp).strftime("%Y-%m") ==
                    datetime.now().strftime("%Y-%m")
                )
            }
        }

    def create_album(self, name: str, album_type: AlbumType = AlbumType.GENERAL,
                    description: str = "") -> PhotoAlbum:
        """
        Create a new photo album.

        Args:
            name: Album name
            album_type: Type of album
            description: Album description

        Returns:
            Created album
        """
        # Generate album ID
        album_id = f"album_{int(time.time() * 1000)}"

        # Create album
        album = PhotoAlbum(album_id, name, album_type)
        album.description = description

        # Store album
        self.albums[album_id] = album
        self.album_order.append(album_id)
        self.total_albums += 1

        return album

    def get_album(self, album_id: str) -> Optional[PhotoAlbum]:
        """Get an album by ID."""
        album = self.albums.get(album_id)
        if album:
            album.mark_as_viewed()
        return album

    def delete_album(self, album_id: str, delete_photos: bool = False) -> bool:
        """
        Delete an album.

        Args:
            album_id: Album to delete
            delete_photos: Also delete photos (not recommended)

        Returns:
            True if deleted
        """
        if album_id not in self.albums:
            return False

        album = self.albums[album_id]

        # Update statistics
        self.total_photos_in_albums -= len(album.photo_ids)

        # Remove from storage
        del self.albums[album_id]
        self.album_order.remove(album_id)
        self.total_albums -= 1

        return True

    def add_photo_to_album(self, album_id: str, photo_id: str) -> bool:
        """Add a photo to an album."""
        album = self.albums.get(album_id)
        if not album:
            return False

        # Check if already in album
        if photo_id in album.photo_ids:
            return False

        album.add_photo(photo_id)
        self.total_photos_in_albums += 1
        return True

    def remove_photo_from_album(self, album_id: str, photo_id: str) -> bool:
        """Remove a photo from an album."""
        album = self.albums.get(album_id)
        if not album:
            return False

        if album.remove_photo(photo_id):
            self.total_photos_in_albums -= 1
            return True
        return False

    def add_photos_to_album(self, album_id: str, photo_ids: List[str]) -> int:
        """
        Add multiple photos to an album.

        Args:
            album_id: Album ID
            photo_ids: List of photo IDs

        Returns:
            Number of photos added
        """
        count = 0
        for photo_id in photo_ids:
            if self.add_photo_to_album(album_id, photo_id):
                count += 1
        return count

    def get_album_photos(self, album_id: str,
                        sort_order: Optional[SortOrder] = None) -> List[str]:
        """
        Get photos in an album.

        Args:
            album_id: Album ID
            sort_order: How to sort photos

        Returns:
            List of photo IDs
        """
        album = self.albums.get(album_id)
        if not album:
            return []

        # For now, return in order added
        # In a full implementation, would sort based on sort_order
        return album.photo_ids.copy()

    def search_albums(self, query: str) -> List[PhotoAlbum]:
        """Search albums by name or description."""
        query_lower = query.lower()
        results = []

        for album in self.albums.values():
            if query_lower in album.name.lower():
                results.append(album)
            elif query_lower in album.description.lower():
                results.append(album)

        return results

    def get_albums_by_type(self, album_type: AlbumType) -> List[PhotoAlbum]:
        """Get all albums of a specific type."""
        return [a for a in self.albums.values() if a.album_type == album_type]

    def get_albums_containing_photo(self, photo_id: str) -> List[PhotoAlbum]:
        """Get all albums containing a specific photo."""
        return [
            album for album in self.albums.values()
            if photo_id in album.photo_ids
        ]

    def create_monthly_album(self, year: int, month: int,
                           photo_ids: Optional[List[str]] = None) -> PhotoAlbum:
        """
        Create an album for a specific month.

        Args:
            year: Year
            month: Month (1-12)
            photo_ids: Photos to add (optional)

        Returns:
            Created album
        """
        month_name = datetime(year, month, 1).strftime("%B %Y")
        album = self.create_album(
            name=month_name,
            album_type=AlbumType.DAILY_LIFE,
            description=f"Photos from {month_name}"
        )

        if photo_ids:
            self.add_photos_to_album(album.album_id, photo_ids)

        return album

    def create_event_album(self, event_name: str, event_type: AlbumType,
                          photo_ids: Optional[List[str]] = None) -> PhotoAlbum:
        """
        Create an album for a specific event.

        Args:
            event_name: Name of event
            event_type: Type of event album
            photo_ids: Photos to add (optional)

        Returns:
            Created album
        """
        album = self.create_album(
            name=event_name,
            album_type=event_type,
            description=f"Photos from {event_name}"
        )

        if photo_ids:
            self.add_photos_to_album(album.album_id, photo_ids)

        return album

    def get_smart_album_photos(self, smart_album_id: str,
                              screenshot_system: Any) -> List[str]:
        """
        Get photos for a smart album.

        Args:
            smart_album_id: Smart album identifier
            screenshot_system: Screenshot system to query

        Returns:
            List of photo IDs matching smart album criteria
        """
        smart_album = self.smart_albums.get(smart_album_id)
        if not smart_album:
            return []

        filter_func = smart_album['filter']
        matching_photos = [
            photo_id for photo_id, screenshot in screenshot_system.screenshots.items()
            if filter_func(screenshot)
        ]

        return matching_photos

    def get_slideshow_order(self, album_id: str,
                           sort_order: Optional[SortOrder] = None) -> List[str]:
        """
        Get photo order for slideshow.

        Args:
            album_id: Album ID
            sort_order: Sort order for slideshow

        Returns:
            Ordered list of photo IDs
        """
        return self.get_album_photos(album_id, sort_order)

    def export_album_list(self, album_id: str) -> Dict[str, Any]:
        """
        Export album information.

        Args:
            album_id: Album to export

        Returns:
            Album data dictionary
        """
        album = self.get_album(album_id)
        if not album:
            return {}

        return {
            'album_name': album.name,
            'album_type': album.album_type.value,
            'description': album.description,
            'created_date': album.created_date_string,
            'photo_count': album.get_photo_count(),
            'cover_photo_id': album.cover_photo_id,
            'photo_ids': album.photo_ids
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get album system statistics."""
        return {
            'total_albums': self.total_albums,
            'total_photos_in_albums': self.total_photos_in_albums,
            'albums_by_type': {
                album_type.value: len(self.get_albums_by_type(album_type))
                for album_type in AlbumType
            },
            'average_photos_per_album': (
                self.total_photos_in_albums / self.total_albums
                if self.total_albums > 0 else 0
            ),
            'most_viewed_album': max(
                self.albums.values(),
                key=lambda a: a.view_count,
                default=None
            ).album_id if self.albums else None,
            'newest_album': self.album_order[-1] if self.album_order else None,
            'smart_albums_available': len(self.smart_albums)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'albums': {
                album_id: album.to_dict()
                for album_id, album in self.albums.items()
            },
            'album_order': self.album_order,
            'total_albums': self.total_albums,
            'total_photos_in_albums': self.total_photos_in_albums,
            'auto_create_monthly_albums': self.auto_create_monthly_albums,
            'auto_create_event_albums': self.auto_create_event_albums,
            'default_sort_order': self.default_sort_order.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhotoAlbumSystem':
        """Deserialize from dictionary."""
        system = cls()

        # Restore albums
        albums_data = data.get('albums', {})
        for album_id, album_data in albums_data.items():
            system.albums[album_id] = PhotoAlbum.from_dict(album_data)

        system.album_order = data.get('album_order', [])
        system.total_albums = data.get('total_albums', 0)
        system.total_photos_in_albums = data.get('total_photos_in_albums', 0)
        system.auto_create_monthly_albums = data.get('auto_create_monthly_albums', True)
        system.auto_create_event_albums = data.get('auto_create_event_albums', True)
        system.default_sort_order = SortOrder(data.get('default_sort_order', 'date_newest'))

        return system
