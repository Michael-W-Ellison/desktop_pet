"""
Phase 11: Screenshot System

Captures screenshots/photos of the desktop pet for the photo album.
"""
import time
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class PhotoFilter(Enum):
    """Photo filters/effects."""
    NONE = "none"
    SEPIA = "sepia"
    GRAYSCALE = "grayscale"
    VINTAGE = "vintage"
    BRIGHT = "bright"
    WARM = "warm"
    COOL = "cool"
    DREAMY = "dreamy"


class PhotoFrame(Enum):
    """Photo frame styles."""
    NONE = "none"
    SIMPLE = "simple"
    DECORATED = "decorated"
    POLAROID = "polaroid"
    SCRAPBOOK = "scrapbook"
    HEARTS = "hearts"
    STARS = "stars"


class Screenshot:
    """Represents a captured screenshot/photo."""

    def __init__(self, photo_id: str, file_path: str, width: int, height: int):
        """
        Initialize screenshot.

        Args:
            photo_id: Unique photo identifier
            file_path: Path to saved image file
            width: Image width in pixels
            height: Image height in pixels
        """
        self.photo_id = photo_id
        self.file_path = file_path
        self.width = width
        self.height = height
        self.timestamp = time.time()
        self.date_string = datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")

        # Metadata
        self.caption: str = ""
        self.tags: List[str] = []
        self.pet_name: str = ""
        self.pet_age_days: Optional[float] = None
        self.pet_mood: Optional[str] = None
        self.pet_activity: Optional[str] = None

        # Photo effects
        self.filter_applied: PhotoFilter = PhotoFilter.NONE
        self.frame_style: PhotoFrame = PhotoFrame.NONE

        # Organization
        self.album_ids: List[str] = []  # Which albums contain this photo
        self.favorite: bool = False
        self.view_count: int = 0

        # File info
        self.file_size_bytes: int = 0
        self.thumbnail_path: Optional[str] = None

    def add_to_album(self, album_id: str):
        """Add photo to an album."""
        if album_id not in self.album_ids:
            self.album_ids.append(album_id)

    def remove_from_album(self, album_id: str):
        """Remove photo from an album."""
        if album_id in self.album_ids:
            self.album_ids.remove(album_id)

    def increment_views(self):
        """Increment view count."""
        self.view_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'photo_id': self.photo_id,
            'file_path': self.file_path,
            'width': self.width,
            'height': self.height,
            'timestamp': self.timestamp,
            'date_string': self.date_string,
            'caption': self.caption,
            'tags': self.tags,
            'pet_name': self.pet_name,
            'pet_age_days': self.pet_age_days,
            'pet_mood': self.pet_mood,
            'pet_activity': self.pet_activity,
            'filter_applied': self.filter_applied.value,
            'frame_style': self.frame_style.value,
            'album_ids': self.album_ids,
            'favorite': self.favorite,
            'view_count': self.view_count,
            'file_size_bytes': self.file_size_bytes,
            'thumbnail_path': self.thumbnail_path
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Screenshot':
        """Deserialize from dictionary."""
        screenshot = cls(
            photo_id=data['photo_id'],
            file_path=data['file_path'],
            width=data['width'],
            height=data['height']
        )
        screenshot.timestamp = data['timestamp']
        screenshot.date_string = data['date_string']
        screenshot.caption = data.get('caption', '')
        screenshot.tags = data.get('tags', [])
        screenshot.pet_name = data.get('pet_name', '')
        screenshot.pet_age_days = data.get('pet_age_days')
        screenshot.pet_mood = data.get('pet_mood')
        screenshot.pet_activity = data.get('pet_activity')
        screenshot.filter_applied = PhotoFilter(data.get('filter_applied', 'none'))
        screenshot.frame_style = PhotoFrame(data.get('frame_style', 'none'))
        screenshot.album_ids = data.get('album_ids', [])
        screenshot.favorite = data.get('favorite', False)
        screenshot.view_count = data.get('view_count', 0)
        screenshot.file_size_bytes = data.get('file_size_bytes', 0)
        screenshot.thumbnail_path = data.get('thumbnail_path')
        return screenshot


class ScreenshotSystem:
    """
    Manages screenshot capture and photo storage.

    Features:
    - Capture pet screenshots
    - Apply filters and frames
    - Auto-capture on special moments
    - Organize photos by date/event
    - Generate thumbnails
    - Export photos
    """

    def __init__(self, save_directory: str = "screenshots"):
        """
        Initialize screenshot system.

        Args:
            save_directory: Directory to save screenshots
        """
        self.save_directory = save_directory

        # Photo storage
        self.screenshots: Dict[str, Screenshot] = {}
        self.screenshot_order: List[str] = []  # Chronological order

        # Auto-capture settings
        self.auto_capture_enabled = True
        self.auto_capture_events = {
            'level_up': True,
            'evolution': True,
            'new_trick': True,
            'milestone': True,
            'funny_moment': True,
            'rare_emotion': True
        }

        # Capture settings
        self.default_filter = PhotoFilter.NONE
        self.default_frame = PhotoFrame.NONE
        self.auto_thumbnail = True
        self.thumbnail_size = (200, 200)

        # Statistics
        self.total_screenshots = 0
        self.total_favorites = 0
        self.total_file_size_bytes = 0
        self.most_viewed_photo_id: Optional[str] = None
        self.most_viewed_count = 0

        # Capture history
        self.last_capture_time = 0.0
        self.capture_cooldown = 1.0  # Min seconds between captures

    def capture_screenshot(self, width: int = 800, height: int = 600,
                          pet_name: str = "", pet_age_days: Optional[float] = None,
                          pet_mood: Optional[str] = None,
                          pet_activity: Optional[str] = None,
                          caption: str = "",
                          tags: Optional[List[str]] = None,
                          filter_effect: Optional[PhotoFilter] = None,
                          frame_style: Optional[PhotoFrame] = None,
                          auto_save: bool = True) -> Optional[Screenshot]:
        """
        Capture a screenshot of the pet.

        Args:
            width: Screenshot width
            height: Screenshot height
            pet_name: Name of pet in screenshot
            pet_age_days: Pet's age
            pet_mood: Pet's current mood
            pet_activity: What pet was doing
            caption: Photo caption
            tags: Photo tags
            filter_effect: Filter to apply
            frame_style: Frame style to apply
            auto_save: Automatically save to disk

        Returns:
            Screenshot object or None if on cooldown
        """
        # Check cooldown
        if time.time() - self.last_capture_time < self.capture_cooldown:
            return None

        # Generate photo ID
        photo_id = f"photo_{int(time.time() * 1000)}"

        # Generate file path
        date_folder = datetime.now().strftime("%Y-%m-%d")
        filename = f"{photo_id}.png"
        file_path = os.path.join(self.save_directory, date_folder, filename)

        # Create screenshot object
        screenshot = Screenshot(
            photo_id=photo_id,
            file_path=file_path,
            width=width,
            height=height
        )

        # Set metadata
        screenshot.pet_name = pet_name
        screenshot.pet_age_days = pet_age_days
        screenshot.pet_mood = pet_mood
        screenshot.pet_activity = pet_activity
        screenshot.caption = caption
        screenshot.tags = tags or []

        # Apply effects
        screenshot.filter_applied = filter_effect or self.default_filter
        screenshot.frame_style = frame_style or self.default_frame

        # In a real implementation, this would actually capture and save the image
        # For now, we'll simulate file size
        screenshot.file_size_bytes = width * height * 4  # Rough estimate for RGBA

        # Generate thumbnail path
        if self.auto_thumbnail:
            thumbnail_filename = f"{photo_id}_thumb.png"
            screenshot.thumbnail_path = os.path.join(
                self.save_directory, date_folder, "thumbnails", thumbnail_filename
            )

        # Store screenshot
        self.screenshots[photo_id] = screenshot
        self.screenshot_order.append(photo_id)

        # Update statistics
        self.total_screenshots += 1
        self.total_file_size_bytes += screenshot.file_size_bytes
        self.last_capture_time = time.time()

        return screenshot

    def auto_capture_event(self, event_type: str, **kwargs) -> Optional[Screenshot]:
        """
        Automatically capture screenshot for an event.

        Args:
            event_type: Type of event
            **kwargs: Additional metadata for capture

        Returns:
            Screenshot if captured, None otherwise
        """
        if not self.auto_capture_enabled:
            return None

        if not self.auto_capture_events.get(event_type, False):
            return None

        # Generate caption based on event
        captions = {
            'level_up': f"{kwargs.get('pet_name', 'Pet')} leveled up!",
            'evolution': f"{kwargs.get('pet_name', 'Pet')} evolved!",
            'new_trick': f"{kwargs.get('pet_name', 'Pet')} learned {kwargs.get('trick_name', 'a new trick')}!",
            'milestone': f"Milestone: {kwargs.get('milestone_name', 'Achievement unlocked')}!",
            'funny_moment': f"Funny moment captured!",
            'rare_emotion': f"{kwargs.get('pet_name', 'Pet')} showed {kwargs.get('emotion', 'a rare emotion')}!"
        }

        caption = captions.get(event_type, "Special moment captured!")

        # Generate tags
        tags = [event_type, 'auto_capture']
        if 'additional_tags' in kwargs:
            tags.extend(kwargs['additional_tags'])

        return self.capture_screenshot(
            caption=caption,
            tags=tags,
            **{k: v for k, v in kwargs.items() if k in [
                'width', 'height', 'pet_name', 'pet_age_days', 'pet_mood', 'pet_activity'
            ]}
        )

    def get_screenshot(self, photo_id: str) -> Optional[Screenshot]:
        """
        Get a screenshot by ID.

        Args:
            photo_id: Photo identifier

        Returns:
            Screenshot or None
        """
        screenshot = self.screenshots.get(photo_id)
        if screenshot:
            screenshot.increment_views()

            # Update most viewed
            if screenshot.view_count > self.most_viewed_count:
                self.most_viewed_count = screenshot.view_count
                self.most_viewed_photo_id = photo_id

        return screenshot

    def delete_screenshot(self, photo_id: str) -> bool:
        """
        Delete a screenshot.

        Args:
            photo_id: Photo to delete

        Returns:
            True if deleted
        """
        if photo_id not in self.screenshots:
            return False

        screenshot = self.screenshots[photo_id]

        # Update statistics
        self.total_file_size_bytes -= screenshot.file_size_bytes
        if screenshot.favorite:
            self.total_favorites -= 1

        # Remove from storage
        del self.screenshots[photo_id]
        self.screenshot_order.remove(photo_id)
        self.total_screenshots -= 1

        # In a real implementation, delete the actual file
        # os.remove(screenshot.file_path)

        return True

    def toggle_favorite(self, photo_id: str) -> bool:
        """Toggle screenshot favorite status."""
        screenshot = self.screenshots.get(photo_id)
        if not screenshot:
            return False

        screenshot.favorite = not screenshot.favorite

        if screenshot.favorite:
            self.total_favorites += 1
        else:
            self.total_favorites -= 1

        return screenshot.favorite

    def add_caption(self, photo_id: str, caption: str) -> bool:
        """Add or update photo caption."""
        screenshot = self.screenshots.get(photo_id)
        if not screenshot:
            return False

        screenshot.caption = caption
        return True

    def add_tag(self, photo_id: str, tag: str) -> bool:
        """Add a tag to a photo."""
        screenshot = self.screenshots.get(photo_id)
        if not screenshot:
            return False

        if tag not in screenshot.tags:
            screenshot.tags.append(tag)

        return True

    def apply_filter(self, photo_id: str, filter_effect: PhotoFilter) -> bool:
        """Apply a filter to a photo."""
        screenshot = self.screenshots.get(photo_id)
        if not screenshot:
            return False

        screenshot.filter_applied = filter_effect
        # In a real implementation, re-process the image with the filter
        return True

    def apply_frame(self, photo_id: str, frame_style: PhotoFrame) -> bool:
        """Apply a frame to a photo."""
        screenshot = self.screenshots.get(photo_id)
        if not screenshot:
            return False

        screenshot.frame_style = frame_style
        # In a real implementation, re-process the image with the frame
        return True

    def search_screenshots(self, query: str) -> List[Screenshot]:
        """Search screenshots by caption or tags."""
        query_lower = query.lower()
        results = []

        for screenshot in self.screenshots.values():
            # Search in caption
            if query_lower in screenshot.caption.lower():
                results.append(screenshot)
                continue

            # Search in tags
            if any(query_lower in tag.lower() for tag in screenshot.tags):
                results.append(screenshot)
                continue

        return results

    def get_screenshots_by_tag(self, tag: str) -> List[Screenshot]:
        """Get all screenshots with a specific tag."""
        return [
            s for s in self.screenshots.values()
            if tag.lower() in [t.lower() for t in s.tags]
        ]

    def get_favorite_screenshots(self) -> List[Screenshot]:
        """Get all favorite screenshots."""
        return [s for s in self.screenshots.values() if s.favorite]

    def get_recent_screenshots(self, count: int = 10) -> List[Screenshot]:
        """Get most recent screenshots."""
        recent_ids = self.screenshot_order[-count:]
        return [self.screenshots[photo_id] for photo_id in reversed(recent_ids)]

    def get_screenshots_by_date_range(self, start_timestamp: float,
                                     end_timestamp: float) -> List[Screenshot]:
        """Get screenshots within a date range."""
        return [
            s for s in self.screenshots.values()
            if start_timestamp <= s.timestamp <= end_timestamp
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get screenshot statistics."""
        return {
            'total_screenshots': self.total_screenshots,
            'total_favorites': self.total_favorites,
            'total_file_size_mb': self.total_file_size_bytes / (1024 * 1024),
            'most_viewed_photo_id': self.most_viewed_photo_id,
            'most_viewed_count': self.most_viewed_count,
            'average_views_per_photo': (
                sum(s.view_count for s in self.screenshots.values()) / self.total_screenshots
                if self.total_screenshots > 0 else 0
            ),
            'photos_by_filter': {
                filter_type.value: len([
                    s for s in self.screenshots.values()
                    if s.filter_applied == filter_type
                ])
                for filter_type in PhotoFilter
            },
            'photos_by_frame': {
                frame_type.value: len([
                    s for s in self.screenshots.values()
                    if s.frame_style == frame_type
                ])
                for frame_type in PhotoFrame
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'save_directory': self.save_directory,
            'screenshots': {
                photo_id: screenshot.to_dict()
                for photo_id, screenshot in self.screenshots.items()
            },
            'screenshot_order': self.screenshot_order,
            'auto_capture_enabled': self.auto_capture_enabled,
            'auto_capture_events': self.auto_capture_events,
            'default_filter': self.default_filter.value,
            'default_frame': self.default_frame.value,
            'auto_thumbnail': self.auto_thumbnail,
            'thumbnail_size': self.thumbnail_size,
            'total_screenshots': self.total_screenshots,
            'total_favorites': self.total_favorites,
            'total_file_size_bytes': self.total_file_size_bytes,
            'most_viewed_photo_id': self.most_viewed_photo_id,
            'most_viewed_count': self.most_viewed_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScreenshotSystem':
        """Deserialize from dictionary."""
        system = cls(save_directory=data.get('save_directory', 'screenshots'))

        # Restore screenshots
        screenshots_data = data.get('screenshots', {})
        for photo_id, screenshot_data in screenshots_data.items():
            system.screenshots[photo_id] = Screenshot.from_dict(screenshot_data)

        system.screenshot_order = data.get('screenshot_order', [])
        system.auto_capture_enabled = data.get('auto_capture_enabled', True)
        system.auto_capture_events = data.get('auto_capture_events', {})
        system.default_filter = PhotoFilter(data.get('default_filter', 'none'))
        system.default_frame = PhotoFrame(data.get('default_frame', 'none'))
        system.auto_thumbnail = data.get('auto_thumbnail', True)
        system.thumbnail_size = tuple(data.get('thumbnail_size', (200, 200)))
        system.total_screenshots = data.get('total_screenshots', 0)
        system.total_favorites = data.get('total_favorites', 0)
        system.total_file_size_bytes = data.get('total_file_size_bytes', 0)
        system.most_viewed_photo_id = data.get('most_viewed_photo_id')
        system.most_viewed_count = data.get('most_viewed_count', 0)

        return system
