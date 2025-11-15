"""
Phase 11: Journal System

Allows users (kids) to write diary entries about their pet's life and adventures.
"""
import time
import json
from typing import Dict, Any, List, Optional, Set
from enum import Enum
from datetime import datetime


class EntryMood(Enum):
    """Mood of journal entry."""
    HAPPY = "happy"
    EXCITED = "excited"
    PROUD = "proud"
    LOVING = "loving"
    FUNNY = "funny"
    SAD = "sad"
    WORRIED = "worried"
    SURPRISED = "surprised"
    CALM = "calm"
    THOUGHTFUL = "thoughtful"


class EntryCategory(Enum):
    """Category of journal entry."""
    DAILY_LIFE = "daily_life"
    MILESTONE = "milestone"
    TRAINING = "training"
    FUNNY_MOMENT = "funny_moment"
    BONDING = "bonding"
    ADVENTURE = "adventure"
    ACHIEVEMENT = "achievement"
    GROWTH = "growth"
    FRIENDSHIP = "friendship"
    CHALLENGE = "challenge"


class JournalEntry:
    """Represents a single journal entry."""

    def __init__(self, entry_id: str, title: str, content: str,
                 author: str = "Owner", mood: Optional[EntryMood] = None,
                 category: Optional[EntryCategory] = None):
        """
        Initialize journal entry.

        Args:
            entry_id: Unique entry identifier
            title: Entry title
            content: Entry text content
            author: Who wrote the entry
            mood: Mood of the entry
            category: Entry category
        """
        self.entry_id = entry_id
        self.title = title
        self.content = content
        self.author = author
        self.mood = mood or EntryMood.HAPPY
        self.category = category or EntryCategory.DAILY_LIFE
        self.timestamp = time.time()
        self.date_string = datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%d %H:%M:%S")

        # Metadata
        self.tags: Set[str] = set()
        self.linked_photos: List[str] = []  # Photo IDs
        self.linked_events: List[str] = []  # Event IDs
        self.pet_age_days: Optional[float] = None
        self.pet_mood: Optional[str] = None

        # Engagement
        self.favorite: bool = False
        self.read_count: int = 0
        self.last_read_time: float = 0.0

        # Statistics
        self.word_count: int = len(content.split())
        self.character_count: int = len(content)

    def add_tag(self, tag: str):
        """Add a tag to the entry."""
        self.tags.add(tag.lower())

    def remove_tag(self, tag: str):
        """Remove a tag from the entry."""
        self.tags.discard(tag.lower())

    def link_photo(self, photo_id: str):
        """Link a photo to this entry."""
        if photo_id not in self.linked_photos:
            self.linked_photos.append(photo_id)

    def link_event(self, event_id: str):
        """Link an event to this entry."""
        if event_id not in self.linked_events:
            self.linked_events.append(event_id)

    def mark_as_read(self):
        """Mark entry as read."""
        self.read_count += 1
        self.last_read_time = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'entry_id': self.entry_id,
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'mood': self.mood.value,
            'category': self.category.value,
            'timestamp': self.timestamp,
            'date_string': self.date_string,
            'tags': list(self.tags),
            'linked_photos': self.linked_photos,
            'linked_events': self.linked_events,
            'pet_age_days': self.pet_age_days,
            'pet_mood': self.pet_mood,
            'favorite': self.favorite,
            'read_count': self.read_count,
            'last_read_time': self.last_read_time,
            'word_count': self.word_count,
            'character_count': self.character_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JournalEntry':
        """Deserialize from dictionary."""
        entry = cls(
            entry_id=data['entry_id'],
            title=data['title'],
            content=data['content'],
            author=data.get('author', 'Owner'),
            mood=EntryMood(data['mood']),
            category=EntryCategory(data['category'])
        )
        entry.timestamp = data['timestamp']
        entry.date_string = data['date_string']
        entry.tags = set(data.get('tags', []))
        entry.linked_photos = data.get('linked_photos', [])
        entry.linked_events = data.get('linked_events', [])
        entry.pet_age_days = data.get('pet_age_days')
        entry.pet_mood = data.get('pet_mood')
        entry.favorite = data.get('favorite', False)
        entry.read_count = data.get('read_count', 0)
        entry.last_read_time = data.get('last_read_time', 0.0)
        entry.word_count = data.get('word_count', 0)
        entry.character_count = data.get('character_count', 0)
        return entry


class JournalSystem:
    """
    Manages the pet owner's journal/diary.

    Features:
    - Write diary entries about pet experiences
    - Organize entries by date, mood, category
    - Tag and search entries
    - Link entries to photos and events
    - Mark favorite entries
    - Export journal to various formats
    - Reading statistics and streaks
    """

    def __init__(self, pet_name: str = "Pet"):
        """
        Initialize journal system.

        Args:
            pet_name: Name of the pet for journal context
        """
        self.pet_name = pet_name

        # Entries storage
        self.entries: Dict[str, JournalEntry] = {}
        self.entry_order: List[str] = []  # Chronological order

        # Organization
        self.tags: Set[str] = set()
        self.categories_used: Set[EntryCategory] = set()

        # Statistics
        self.total_entries = 0
        self.total_words_written = 0
        self.total_characters_written = 0
        self.favorite_count = 0
        self.current_streak_days = 0
        self.longest_streak_days = 0
        self.last_entry_date: Optional[str] = None

        # Settings
        self.auto_link_photos = True
        self.auto_tag_enabled = True
        self.daily_reminder = True

    def create_entry(self, title: str, content: str, author: str = "Owner",
                    mood: Optional[EntryMood] = None,
                    category: Optional[EntryCategory] = None,
                    tags: Optional[List[str]] = None,
                    pet_age_days: Optional[float] = None,
                    pet_mood: Optional[str] = None) -> JournalEntry:
        """
        Create a new journal entry.

        Args:
            title: Entry title
            content: Entry content
            author: Who wrote it
            mood: Entry mood
            category: Entry category
            tags: List of tags
            pet_age_days: Pet's age when entry written
            pet_mood: Pet's mood when entry written

        Returns:
            Created journal entry
        """
        # Generate entry ID
        entry_id = f"entry_{int(time.time() * 1000)}"

        # Create entry
        entry = JournalEntry(
            entry_id=entry_id,
            title=title,
            content=content,
            author=author,
            mood=mood,
            category=category
        )

        # Add metadata
        entry.pet_age_days = pet_age_days
        entry.pet_mood = pet_mood

        # Add tags
        if tags:
            for tag in tags:
                entry.add_tag(tag)
                self.tags.add(tag.lower())

        # Auto-tag based on content (simple keyword matching)
        if self.auto_tag_enabled:
            auto_tags = self._generate_auto_tags(content)
            for tag in auto_tags:
                entry.add_tag(tag)
                self.tags.add(tag)

        # Store entry
        self.entries[entry_id] = entry
        self.entry_order.append(entry_id)

        # Update category tracking
        self.categories_used.add(entry.category)

        # Update statistics
        self.total_entries += 1
        self.total_words_written += entry.word_count
        self.total_characters_written += entry.character_count

        # Update streak
        self._update_writing_streak(entry)

        return entry

    def _generate_auto_tags(self, content: str) -> List[str]:
        """Generate automatic tags from content."""
        content_lower = content.lower()
        auto_tags = []

        # Keyword matching
        tag_keywords = {
            'playing': ['play', 'game', 'toy', 'fun'],
            'eating': ['eat', 'food', 'hungry', 'snack', 'meal'],
            'sleeping': ['sleep', 'nap', 'tired', 'dream'],
            'training': ['train', 'learn', 'teach', 'trick'],
            'bonding': ['love', 'cuddle', 'hug', 'bond'],
            'health': ['sick', 'vet', 'medicine', 'healthy'],
            'growing': ['grow', 'bigger', 'change', 'evolve'],
            'achievement': ['achieve', 'success', 'proud', 'accomplished'],
            'funny': ['funny', 'hilarious', 'laugh', 'silly'],
            'adventure': ['adventure', 'explore', 'discover', 'journey']
        }

        for tag, keywords in tag_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                auto_tags.append(tag)

        return auto_tags

    def _update_writing_streak(self, entry: JournalEntry):
        """Update writing streak statistics."""
        entry_date = datetime.fromtimestamp(entry.timestamp).strftime("%Y-%m-%d")

        if self.last_entry_date:
            # Check if consecutive day
            last_date = datetime.strptime(self.last_entry_date, "%Y-%m-%d")
            current_date = datetime.strptime(entry_date, "%Y-%m-%d")
            days_diff = (current_date - last_date).days

            if days_diff == 1:
                # Consecutive day - increment streak
                self.current_streak_days += 1
            elif days_diff == 0:
                # Same day - no change
                pass
            else:
                # Streak broken - reset
                self.current_streak_days = 1
        else:
            # First entry
            self.current_streak_days = 1

        # Update longest streak
        if self.current_streak_days > self.longest_streak_days:
            self.longest_streak_days = self.current_streak_days

        self.last_entry_date = entry_date

    def get_entry(self, entry_id: str) -> Optional[JournalEntry]:
        """Get an entry by ID."""
        entry = self.entries.get(entry_id)
        if entry:
            entry.mark_as_read()
        return entry

    def edit_entry(self, entry_id: str, title: Optional[str] = None,
                  content: Optional[str] = None) -> bool:
        """
        Edit an existing entry.

        Args:
            entry_id: Entry to edit
            title: New title (if provided)
            content: New content (if provided)

        Returns:
            True if edited successfully
        """
        entry = self.entries.get(entry_id)
        if not entry:
            return False

        if title:
            entry.title = title

        if content:
            entry.content = content
            entry.word_count = len(content.split())
            entry.character_count = len(content)

        return True

    def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry."""
        if entry_id not in self.entries:
            return False

        entry = self.entries[entry_id]

        # Update statistics
        self.total_words_written -= entry.word_count
        self.total_characters_written -= entry.character_count
        if entry.favorite:
            self.favorite_count -= 1

        # Remove from storage
        del self.entries[entry_id]
        self.entry_order.remove(entry_id)
        self.total_entries -= 1

        return True

    def toggle_favorite(self, entry_id: str) -> bool:
        """Toggle entry favorite status."""
        entry = self.entries.get(entry_id)
        if not entry:
            return False

        entry.favorite = not entry.favorite

        if entry.favorite:
            self.favorite_count += 1
        else:
            self.favorite_count -= 1

        return entry.favorite

    def search_entries(self, query: str, search_in_content: bool = True,
                      search_in_tags: bool = True) -> List[JournalEntry]:
        """
        Search for entries.

        Args:
            query: Search query
            search_in_content: Search in entry content
            search_in_tags: Search in tags

        Returns:
            List of matching entries
        """
        query_lower = query.lower()
        results = []

        for entry in self.entries.values():
            # Search in title
            if query_lower in entry.title.lower():
                results.append(entry)
                continue

            # Search in content
            if search_in_content and query_lower in entry.content.lower():
                results.append(entry)
                continue

            # Search in tags
            if search_in_tags:
                if any(query_lower in tag for tag in entry.tags):
                    results.append(entry)
                    continue

        return results

    def get_entries_by_mood(self, mood: EntryMood) -> List[JournalEntry]:
        """Get all entries with a specific mood."""
        return [e for e in self.entries.values() if e.mood == mood]

    def get_entries_by_category(self, category: EntryCategory) -> List[JournalEntry]:
        """Get all entries in a category."""
        return [e for e in self.entries.values() if e.category == category]

    def get_entries_by_tag(self, tag: str) -> List[JournalEntry]:
        """Get all entries with a specific tag."""
        tag_lower = tag.lower()
        return [e for e in self.entries.values() if tag_lower in e.tags]

    def get_favorite_entries(self) -> List[JournalEntry]:
        """Get all favorite entries."""
        return [e for e in self.entries.values() if e.favorite]

    def get_recent_entries(self, count: int = 10) -> List[JournalEntry]:
        """Get most recent entries."""
        recent_ids = self.entry_order[-count:]
        return [self.entries[entry_id] for entry_id in reversed(recent_ids)]

    def get_entries_by_date_range(self, start_timestamp: float,
                                  end_timestamp: float) -> List[JournalEntry]:
        """Get entries within a date range."""
        return [
            e for e in self.entries.values()
            if start_timestamp <= e.timestamp <= end_timestamp
        ]

    def export_to_text(self, include_metadata: bool = True) -> str:
        """
        Export journal to plain text.

        Args:
            include_metadata: Include entry metadata

        Returns:
            Text representation of journal
        """
        lines = []
        lines.append(f"=== Journal for {self.pet_name} ===\n")
        lines.append(f"Total Entries: {self.total_entries}\n")
        lines.append(f"Total Words: {self.total_words_written}\n")
        lines.append(f"Current Streak: {self.current_streak_days} days\n")
        lines.append("\n" + "=" * 60 + "\n\n")

        for entry_id in self.entry_order:
            entry = self.entries[entry_id]

            lines.append(f"Date: {entry.date_string}\n")
            lines.append(f"Title: {entry.title}\n")

            if include_metadata:
                lines.append(f"Author: {entry.author}\n")
                lines.append(f"Mood: {entry.mood.value}\n")
                lines.append(f"Category: {entry.category.value}\n")
                if entry.tags:
                    lines.append(f"Tags: {', '.join(sorted(entry.tags))}\n")
                if entry.favorite:
                    lines.append("⭐ FAVORITE\n")

            lines.append("\n" + entry.content + "\n")
            lines.append("\n" + "-" * 60 + "\n\n")

        return "".join(lines)

    def get_statistics(self) -> Dict[str, Any]:
        """Get journal statistics."""
        return {
            'total_entries': self.total_entries,
            'total_words': self.total_words_written,
            'total_characters': self.total_characters_written,
            'favorite_count': self.favorite_count,
            'current_streak_days': self.current_streak_days,
            'longest_streak_days': self.longest_streak_days,
            'average_words_per_entry': (
                self.total_words_written / self.total_entries
                if self.total_entries > 0 else 0
            ),
            'total_tags': len(self.tags),
            'categories_used': len(self.categories_used),
            'entries_by_mood': {
                mood.value: len(self.get_entries_by_mood(mood))
                for mood in EntryMood
            },
            'entries_by_category': {
                category.value: len(self.get_entries_by_category(category))
                for category in EntryCategory
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'pet_name': self.pet_name,
            'entries': {
                entry_id: entry.to_dict()
                for entry_id, entry in self.entries.items()
            },
            'entry_order': self.entry_order,
            'tags': list(self.tags),
            'categories_used': [cat.value for cat in self.categories_used],
            'total_entries': self.total_entries,
            'total_words_written': self.total_words_written,
            'total_characters_written': self.total_characters_written,
            'favorite_count': self.favorite_count,
            'current_streak_days': self.current_streak_days,
            'longest_streak_days': self.longest_streak_days,
            'last_entry_date': self.last_entry_date,
            'auto_link_photos': self.auto_link_photos,
            'auto_tag_enabled': self.auto_tag_enabled,
            'daily_reminder': self.daily_reminder
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JournalSystem':
        """Deserialize from dictionary."""
        system = cls(pet_name=data.get('pet_name', 'Pet'))

        # Restore entries
        entries_data = data.get('entries', {})
        for entry_id, entry_data in entries_data.items():
            system.entries[entry_id] = JournalEntry.from_dict(entry_data)

        system.entry_order = data.get('entry_order', [])
        system.tags = set(data.get('tags', []))
        system.categories_used = {
            EntryCategory(cat) for cat in data.get('categories_used', [])
        }
        system.total_entries = data.get('total_entries', 0)
        system.total_words_written = data.get('total_words_written', 0)
        system.total_characters_written = data.get('total_characters_written', 0)
        system.favorite_count = data.get('favorite_count', 0)
        system.current_streak_days = data.get('current_streak_days', 0)
        system.longest_streak_days = data.get('longest_streak_days', 0)
        system.last_entry_date = data.get('last_entry_date')
        system.auto_link_photos = data.get('auto_link_photos', True)
        system.auto_tag_enabled = data.get('auto_tag_enabled', True)
        system.daily_reminder = data.get('daily_reminder', True)

        return system
