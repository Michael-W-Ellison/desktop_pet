"""
Phase 11: Memory Book System

Tracks pet milestones and creates digital scrapbooks of memories.
"""
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class MilestoneType(Enum):
    """Types of milestones."""
    # Life stages
    BORN = "born"
    HATCHED = "hatched"
    EVOLVED = "evolved"
    BIRTHDAY = "birthday"

    # Learning
    FIRST_TRICK = "first_trick"
    MASTERED_TRICK = "mastered_trick"
    ALL_TRICKS_LEARNED = "all_tricks_learned"

    # Social
    FIRST_FRIEND = "first_friend"
    BEST_FRIEND = "best_friend"
    PACK_LEADER = "pack_leader"

    # Achievements
    LEVEL_UP = "level_up"
    MAX_LEVEL = "max_level"
    FIRST_EVOLUTION = "first_evolution"
    PERFECT_DAY = "perfect_day"

    # Health
    FIRST_BATH = "first_bath"
    RECOVERED_ILLNESS = "recovered_illness"
    PERFECT_HEALTH_WEEK = "perfect_health_week"

    # Bonding
    MAX_TRUST = "max_trust"
    FIRST_CUDDLE = "first_cuddle"
    ANNIVERSARY = "anniversary"

    # Special
    CUSTOM = "custom"


class Milestone:
    """Represents a memorable milestone."""

    def __init__(self, milestone_id: str, milestone_type: MilestoneType,
                 title: str, description: str = ""):
        """
        Initialize milestone.

        Args:
            milestone_id: Unique milestone identifier
            milestone_type: Type of milestone
            title: Milestone title
            description: Milestone description
        """
        self.milestone_id = milestone_id
        self.milestone_type = milestone_type
        self.title = title
        self.description = description
        self.timestamp = time.time()
        self.date_string = datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")

        # Metadata
        self.pet_age_days: Optional[float] = None
        self.pet_name: str = ""

        # Linked content
        self.linked_photo_ids: List[str] = []
        self.linked_journal_entry_ids: List[str] = []

        # Celebration
        self.celebrated: bool = False
        self.celebration_date: Optional[float] = None

    def link_photo(self, photo_id: str):
        """Link a photo to this milestone."""
        if photo_id not in self.linked_photo_ids:
            self.linked_photo_ids.append(photo_id)

    def link_journal_entry(self, entry_id: str):
        """Link a journal entry to this milestone."""
        if entry_id not in self.linked_journal_entry_ids:
            self.linked_journal_entry_ids.append(entry_id)

    def mark_as_celebrated(self):
        """Mark milestone as celebrated."""
        self.celebrated = True
        self.celebration_date = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'milestone_id': self.milestone_id,
            'milestone_type': self.milestone_type.value,
            'title': self.title,
            'description': self.description,
            'timestamp': self.timestamp,
            'date_string': self.date_string,
            'pet_age_days': self.pet_age_days,
            'pet_name': self.pet_name,
            'linked_photo_ids': self.linked_photo_ids,
            'linked_journal_entry_ids': self.linked_journal_entry_ids,
            'celebrated': self.celebrated,
            'celebration_date': self.celebration_date
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Milestone':
        """Deserialize from dictionary."""
        milestone = cls(
            milestone_id=data['milestone_id'],
            milestone_type=MilestoneType(data['milestone_type']),
            title=data['title'],
            description=data.get('description', '')
        )
        milestone.timestamp = data['timestamp']
        milestone.date_string = data['date_string']
        milestone.pet_age_days = data.get('pet_age_days')
        milestone.pet_name = data.get('pet_name', '')
        milestone.linked_photo_ids = data.get('linked_photo_ids', [])
        milestone.linked_journal_entry_ids = data.get('linked_journal_entry_ids', [])
        milestone.celebrated = data.get('celebrated', False)
        milestone.celebration_date = data.get('celebration_date')
        return milestone


class ScrapbookPage:
    """Represents a page in the memory book."""

    def __init__(self, page_id: str, title: str):
        """
        Initialize scrapbook page.

        Args:
            page_id: Unique page identifier
            title: Page title
        """
        self.page_id = page_id
        self.title = title
        self.description: str = ""
        self.created_timestamp = time.time()

        # Content (can mix photos, journal entries, milestones)
        self.photo_ids: List[str] = []
        self.journal_entry_ids: List[str] = []
        self.milestone_ids: List[str] = []
        self.text_blocks: List[Dict[str, str]] = []  # {text, position}

        # Styling
        self.background_color: str = "#FFFFFF"
        self.theme: str = "default"

    def add_photo(self, photo_id: str):
        """Add a photo to the page."""
        if photo_id not in self.photo_ids:
            self.photo_ids.append(photo_id)

    def add_journal_entry(self, entry_id: str):
        """Add a journal entry reference to the page."""
        if entry_id not in self.journal_entry_ids:
            self.journal_entry_ids.append(entry_id)

    def add_milestone(self, milestone_id: str):
        """Add a milestone reference to the page."""
        if milestone_id not in self.milestone_ids:
            self.milestone_ids.append(milestone_id)

    def add_text(self, text: str, position: str = "center"):
        """Add a text block to the page."""
        self.text_blocks.append({'text': text, 'position': position})

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'page_id': self.page_id,
            'title': self.title,
            'description': self.description,
            'created_timestamp': self.created_timestamp,
            'photo_ids': self.photo_ids,
            'journal_entry_ids': self.journal_entry_ids,
            'milestone_ids': self.milestone_ids,
            'text_blocks': self.text_blocks,
            'background_color': self.background_color,
            'theme': self.theme
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScrapbookPage':
        """Deserialize from dictionary."""
        page = cls(
            page_id=data['page_id'],
            title=data['title']
        )
        page.description = data.get('description', '')
        page.created_timestamp = data['created_timestamp']
        page.photo_ids = data.get('photo_ids', [])
        page.journal_entry_ids = data.get('journal_entry_ids', [])
        page.milestone_ids = data.get('milestone_ids', [])
        page.text_blocks = data.get('text_blocks', [])
        page.background_color = data.get('background_color', '#FFFFFF')
        page.theme = data.get('theme', 'default')
        return page


class MemoryBookSystem:
    """
    Manages pet milestones and creates digital scrapbooks.

    Features:
    - Track important milestones
    - Auto-detect achievements
    - Create scrapbook pages
    - Link photos and journal entries
    - Generate memory timelines
    - Export memory books
    """

    def __init__(self, pet_name: str = "Pet"):
        """
        Initialize memory book system.

        Args:
            pet_name: Name of the pet
        """
        self.pet_name = pet_name

        # Milestone storage
        self.milestones: Dict[str, Milestone] = {}
        self.milestone_order: List[str] = []  # Chronological

        # Scrapbook storage
        self.scrapbook_pages: Dict[str, ScrapbookPage] = {}
        self.page_order: List[str] = []  # Book order

        # Statistics
        self.total_milestones = 0
        self.total_scrapbook_pages = 0
        self.milestones_by_type: Dict[str, int] = {}

        # Settings
        self.auto_milestone_detection = True
        self.auto_celebration = True

    def record_milestone(self, milestone_type: MilestoneType, title: str,
                        description: str = "", pet_age_days: Optional[float] = None,
                        photo_ids: Optional[List[str]] = None,
                        auto_celebrate: bool = True) -> Milestone:
        """
        Record a milestone.

        Args:
            milestone_type: Type of milestone
            title: Milestone title
            description: Milestone description
            pet_age_days: Pet's age when milestone achieved
            photo_ids: Photos to link
            auto_celebrate: Automatically mark as celebrated

        Returns:
            Created milestone
        """
        # Generate milestone ID
        milestone_id = f"milestone_{int(time.time() * 1000)}"

        # Create milestone
        milestone = Milestone(
            milestone_id=milestone_id,
            milestone_type=milestone_type,
            title=title,
            description=description
        )

        milestone.pet_name = self.pet_name
        milestone.pet_age_days = pet_age_days

        # Link photos
        if photo_ids:
            for photo_id in photo_ids:
                milestone.link_photo(photo_id)

        # Auto-celebrate if enabled
        if auto_celebrate and self.auto_celebration:
            milestone.mark_as_celebrated()

        # Store milestone
        self.milestones[milestone_id] = milestone
        self.milestone_order.append(milestone_id)

        # Update statistics
        self.total_milestones += 1
        type_name = milestone_type.value
        if type_name not in self.milestones_by_type:
            self.milestones_by_type[type_name] = 0
        self.milestones_by_type[type_name] += 1

        return milestone

    def get_milestone(self, milestone_id: str) -> Optional[Milestone]:
        """Get a milestone by ID."""
        return self.milestones.get(milestone_id)

    def get_milestones_by_type(self, milestone_type: MilestoneType) -> List[Milestone]:
        """Get all milestones of a specific type."""
        return [
            m for m in self.milestones.values()
            if m.milestone_type == milestone_type
        ]

    def get_recent_milestones(self, count: int = 5) -> List[Milestone]:
        """Get most recent milestones."""
        recent_ids = self.milestone_order[-count:]
        return [self.milestones[mid] for mid in reversed(recent_ids)]

    def get_uncelebrated_milestones(self) -> List[Milestone]:
        """Get milestones that haven't been celebrated yet."""
        return [m for m in self.milestones.values() if not m.celebrated]

    def create_scrapbook_page(self, title: str, description: str = "",
                             theme: str = "default") -> ScrapbookPage:
        """
        Create a new scrapbook page.

        Args:
            title: Page title
            description: Page description
            theme: Visual theme

        Returns:
            Created page
        """
        # Generate page ID
        page_id = f"page_{int(time.time() * 1000)}"

        # Create page
        page = ScrapbookPage(page_id, title)
        page.description = description
        page.theme = theme

        # Store page
        self.scrapbook_pages[page_id] = page
        self.page_order.append(page_id)
        self.total_scrapbook_pages += 1

        return page

    def get_scrapbook_page(self, page_id: str) -> Optional[ScrapbookPage]:
        """Get a scrapbook page by ID."""
        return self.scrapbook_pages.get(page_id)

    def delete_scrapbook_page(self, page_id: str) -> bool:
        """Delete a scrapbook page."""
        if page_id not in self.scrapbook_pages:
            return False

        del self.scrapbook_pages[page_id]
        self.page_order.remove(page_id)
        self.total_scrapbook_pages -= 1

        return True

    def create_milestone_scrapbook_page(self, milestone_id: str,
                                       include_linked_content: bool = True) -> Optional[ScrapbookPage]:
        """
        Create a scrapbook page for a milestone.

        Args:
            milestone_id: Milestone to create page for
            include_linked_content: Include linked photos/entries

        Returns:
            Created page or None
        """
        milestone = self.get_milestone(milestone_id)
        if not milestone:
            return None

        # Create page
        page = self.create_scrapbook_page(
            title=milestone.title,
            description=milestone.description,
            theme="milestone"
        )

        # Add milestone
        page.add_milestone(milestone_id)

        # Add linked content
        if include_linked_content:
            for photo_id in milestone.linked_photo_ids:
                page.add_photo(photo_id)

            for entry_id in milestone.linked_journal_entry_ids:
                page.add_journal_entry(entry_id)

        # Add date text
        page.add_text(f"Achieved on {milestone.date_string}", "top")

        return page

    def create_timeline(self, start_date: Optional[float] = None,
                       end_date: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Create a timeline of milestones.

        Args:
            start_date: Start timestamp (None = all)
            end_date: End timestamp (None = all)

        Returns:
            List of timeline entries
        """
        timeline = []

        for milestone_id in self.milestone_order:
            milestone = self.milestones[milestone_id]

            # Filter by date range
            if start_date and milestone.timestamp < start_date:
                continue
            if end_date and milestone.timestamp > end_date:
                continue

            timeline.append({
                'milestone_id': milestone_id,
                'type': milestone.milestone_type.value,
                'title': milestone.title,
                'date': milestone.date_string,
                'timestamp': milestone.timestamp,
                'pet_age_days': milestone.pet_age_days,
                'photo_count': len(milestone.linked_photo_ids),
                'celebrated': milestone.celebrated
            })

        return timeline

    def export_memory_book(self, include_photos: bool = False) -> Dict[str, Any]:
        """
        Export the entire memory book.

        Args:
            include_photos: Include photo data (not just IDs)

        Returns:
            Memory book data
        """
        return {
            'pet_name': self.pet_name,
            'created_date': datetime.now().strftime("%Y-%m-%d"),
            'total_milestones': self.total_milestones,
            'total_scrapbook_pages': self.total_scrapbook_pages,
            'milestones': [
                self.milestones[mid].to_dict()
                for mid in self.milestone_order
            ],
            'scrapbook_pages': [
                self.scrapbook_pages[pid].to_dict()
                for pid in self.page_order
            ],
            'timeline': self.create_timeline()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory book statistics."""
        return {
            'total_milestones': self.total_milestones,
            'total_scrapbook_pages': self.total_scrapbook_pages,
            'milestones_by_type': self.milestones_by_type.copy(),
            'uncelebrated_milestones': len(self.get_uncelebrated_milestones()),
            'average_photos_per_milestone': (
                sum(len(m.linked_photo_ids) for m in self.milestones.values()) /
                self.total_milestones if self.total_milestones > 0 else 0
            ),
            'average_content_per_page': (
                sum(
                    len(p.photo_ids) + len(p.journal_entry_ids) + len(p.milestone_ids)
                    for p in self.scrapbook_pages.values()
                ) / self.total_scrapbook_pages if self.total_scrapbook_pages > 0 else 0
            ),
            'first_milestone_date': (
                self.milestones[self.milestone_order[0]].date_string
                if self.milestone_order else None
            ),
            'latest_milestone_date': (
                self.milestones[self.milestone_order[-1]].date_string
                if self.milestone_order else None
            )
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'pet_name': self.pet_name,
            'milestones': {
                mid: milestone.to_dict()
                for mid, milestone in self.milestones.items()
            },
            'milestone_order': self.milestone_order,
            'scrapbook_pages': {
                pid: page.to_dict()
                for pid, page in self.scrapbook_pages.items()
            },
            'page_order': self.page_order,
            'total_milestones': self.total_milestones,
            'total_scrapbook_pages': self.total_scrapbook_pages,
            'milestones_by_type': self.milestones_by_type,
            'auto_milestone_detection': self.auto_milestone_detection,
            'auto_celebration': self.auto_celebration
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryBookSystem':
        """Deserialize from dictionary."""
        system = cls(pet_name=data.get('pet_name', 'Pet'))

        # Restore milestones
        milestones_data = data.get('milestones', {})
        for mid, milestone_data in milestones_data.items():
            system.milestones[mid] = Milestone.from_dict(milestone_data)

        system.milestone_order = data.get('milestone_order', [])

        # Restore scrapbook pages
        pages_data = data.get('scrapbook_pages', {})
        for pid, page_data in pages_data.items():
            system.scrapbook_pages[pid] = ScrapbookPage.from_dict(page_data)

        system.page_order = data.get('page_order', [])
        system.total_milestones = data.get('total_milestones', 0)
        system.total_scrapbook_pages = data.get('total_scrapbook_pages', 0)
        system.milestones_by_type = data.get('milestones_by_type', {})
        system.auto_milestone_detection = data.get('auto_milestone_detection', True)
        system.auto_celebration = data.get('auto_celebration', True)

        return system
