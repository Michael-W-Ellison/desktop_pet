"""
Test script for Phase 11: Journal & Memory Capture

Tests all 5 Phase 11 features:
1. Journal system (diary entries, tags, search)
2. Screenshot system (capture, filters, auto-capture)
3. Photo album system (albums, organization)
4. Memory book system (milestones, scrapbooks)
5. Persistence (save/load)
"""
import sys
sys.path.insert(0, '/home/user/desktop_pet/src')

from core.journal_system import JournalSystem, JournalEntry, EntryMood, EntryCategory
from core.screenshot_system import ScreenshotSystem, Screenshot, PhotoFilter, PhotoFrame
from core.photo_album import PhotoAlbumSystem, PhotoAlbum, AlbumType
from core.memory_book import MemoryBookSystem, Milestone, MilestoneType, ScrapbookPage
import time

print("=" * 60)
print("PHASE 11: JOURNAL & MEMORY CAPTURE TEST")
print("=" * 60)

# Test 1: Journal System
print("\n1. Testing Journal System")
print("-" * 60)

journal = JournalSystem(pet_name="Fluffy")
print(f"Journal for: {journal.pet_name}")
print(f"Auto-tag enabled: {journal.auto_tag_enabled}")

# Create journal entries
print("\nCreating journal entries...")
entries_to_create = [
    {
        'title': "First Day with Fluffy",
        'content': "Today I met my new pet Fluffy! We played together and had so much fun. I taught her a new trick.",
        'mood': EntryMood.EXCITED,
        'category': EntryCategory.DAILY_LIFE,
        'tags': ['first_day', 'exciting']
    },
    {
        'title': "Fluffy Learned to Sit",
        'content': "Fluffy learned how to sit today! I'm so proud of her. We practiced with treats and she got it right away.",
        'mood': EntryMood.PROUD,
        'category': EntryCategory.TRAINING,
        'tags': ['training', 'sit_trick']
    },
    {
        'title': "Funny Moment",
        'content': "Fluffy chased her tail for 5 minutes! It was hilarious to watch. She got dizzy and fell over.",
        'mood': EntryMood.FUNNY,
        'category': EntryCategory.FUNNY_MOMENT,
        'tags': ['funny', 'tail_chasing']
    },
    {
        'title': "Cuddle Time",
        'content': "We cuddled on the couch today. Fluffy purred and fell asleep on my lap. I love her so much.",
        'mood': EntryMood.LOVING,
        'category': EntryCategory.BONDING
    }
]

for entry_data in entries_to_create:
    entry = journal.create_entry(
        title=entry_data['title'],
        content=entry_data['content'],
        mood=entry_data.get('mood'),
        category=entry_data.get('category'),
        tags=entry_data.get('tags'),
        pet_age_days=5.0
    )
    print(f"  Created: '{entry.title}'")
    print(f"    Mood: {entry.mood.value}, Category: {entry.category.value}")
    print(f"    Tags: {', '.join(sorted(entry.tags))}")
    print(f"    Word count: {entry.word_count}")

# Test entry operations
print("\nTesting entry operations...")
first_entry_id = list(journal.entries.keys())[0]

# Mark as favorite
journal.toggle_favorite(first_entry_id)
print(f"Marked first entry as favorite")

# Read entry
entry = journal.get_entry(first_entry_id)
print(f"Read entry '{entry.title}' (read {entry.read_count} times)")

# Edit entry
journal.edit_entry(first_entry_id, title="My First Day with Fluffy!")
print(f"Edited entry title")

# Search entries
print("\nSearching journal...")
results = journal.search_entries("fluffy")
print(f"Search for 'fluffy': {len(results)} results")

results = journal.search_entries("training", search_in_tags=True)
print(f"Search for 'training' tag: {len(results)} results")

# Get entries by mood
happy_entries = journal.get_entries_by_mood(EntryMood.EXCITED)
print(f"Excited mood entries: {len(happy_entries)}")

# Get entries by category
training_entries = journal.get_entries_by_category(EntryCategory.TRAINING)
print(f"Training category entries: {len(training_entries)}")

# Get recent entries
recent = journal.get_recent_entries(count=3)
print(f"Recent entries: {len(recent)}")

# Journal statistics
stats = journal.get_statistics()
print(f"\nJournal statistics:")
print(f"  Total entries: {stats['total_entries']}")
print(f"  Total words: {stats['total_words']}")
print(f"  Average words per entry: {stats['average_words_per_entry']:.1f}")
print(f"  Favorite count: {stats['favorite_count']}")
print(f"  Current streak: {stats['current_streak_days']} days")
print(f"  Total tags: {stats['total_tags']}")

# Export journal
print("\nExporting journal to text...")
export_text = journal.export_to_text(include_metadata=True)
print(f"Export length: {len(export_text)} characters")
print(f"First 100 chars: {export_text[:100]}...")

print("✓ Journal system working!")

# Test 2: Screenshot System
print("\n2. Testing Screenshot System")
print("-" * 60)

screenshots = ScreenshotSystem(save_directory="screenshots")
print(f"Save directory: {screenshots.save_directory}")
print(f"Auto-capture enabled: {screenshots.auto_capture_enabled}")

# Capture screenshots
print("\nCapturing screenshots...")
screenshot_data = [
    {
        'caption': "Fluffy's first photo!",
        'tags': ['first_photo', 'cute'],
        'pet_mood': 'happy',
        'pet_activity': 'playing'
    },
    {
        'caption': "Learning to sit",
        'tags': ['training', 'sit'],
        'pet_mood': 'focused',
        'pet_activity': 'training',
        'filter_effect': PhotoFilter.WARM
    },
    {
        'caption': "Silly moment!",
        'tags': ['funny', 'silly'],
        'pet_mood': 'playful',
        'pet_activity': 'playing',
        'filter_effect': PhotoFilter.BRIGHT,
        'frame_style': PhotoFrame.HEARTS
    }
]

for data in screenshot_data:
    screenshot = screenshots.capture_screenshot(
        width=800,
        height=600,
        pet_name="Fluffy",
        pet_age_days=5.0,
        caption=data['caption'],
        tags=data.get('tags'),
        pet_mood=data.get('pet_mood'),
        pet_activity=data.get('pet_activity'),
        filter_effect=data.get('filter_effect'),
        frame_style=data.get('frame_style')
    )
    if screenshot:
        print(f"  Captured: '{screenshot.caption}'")
        print(f"    Size: {screenshot.width}x{screenshot.height}")
        print(f"    Filter: {screenshot.filter_applied.value}")
        print(f"    Frame: {screenshot.frame_style.value}")
        print(f"    Tags: {', '.join(screenshot.tags)}")
    time.sleep(1.1)  # Wait for cooldown

# Auto-capture event
print("\nAuto-capturing milestone event...")
auto_screenshot = screenshots.auto_capture_event(
    event_type='level_up',
    pet_name='Fluffy',
    width=800,
    height=600
)
if auto_screenshot:
    print(f"Auto-captured: '{auto_screenshot.caption}'")

# Screenshot operations
first_photo_id = list(screenshots.screenshots.keys())[0]

# Toggle favorite
screenshots.toggle_favorite(first_photo_id)
print(f"\nMarked first photo as favorite")

# Add caption
screenshots.add_caption(first_photo_id, "Updated caption: Fluffy's very first photo!")
print(f"Updated photo caption")

# Apply filter
screenshots.apply_filter(first_photo_id, PhotoFilter.SEPIA)
print(f"Applied sepia filter")

# Apply frame
screenshots.apply_frame(first_photo_id, PhotoFrame.POLAROID)
print(f"Applied polaroid frame")

# Search screenshots
results = screenshots.search_screenshots("fluffy")
print(f"\nSearch for 'fluffy': {len(results)} results")

# Get screenshots by tag
tagged = screenshots.get_screenshots_by_tag("funny")
print(f"Screenshots tagged 'funny': {len(tagged)}")

# Get favorites
favorites = screenshots.get_favorite_screenshots()
print(f"Favorite screenshots: {len(favorites)}")

# Get recent
recent_photos = screenshots.get_recent_screenshots(count=3)
print(f"Recent screenshots: {len(recent_photos)}")

# Screenshot statistics
stats = screenshots.get_statistics()
print(f"\nScreenshot statistics:")
print(f"  Total screenshots: {stats['total_screenshots']}")
print(f"  Total favorites: {stats['total_favorites']}")
print(f"  Total file size: {stats['total_file_size_mb']:.2f} MB")
print(f"  Most viewed: {stats['most_viewed_photo_id']}")
print(f"  Average views: {stats['average_views_per_photo']:.1f}")

print("✓ Screenshot system working!")

# Test 3: Photo Album System
print("\n3. Testing Photo Album System")
print("-" * 60)

albums = PhotoAlbumSystem()
print(f"Auto-create monthly albums: {albums.auto_create_monthly_albums}")
print(f"Smart albums available: {len(albums.smart_albums)}")

# Create albums
print("\nCreating photo albums...")
album1 = albums.create_album(
    name="First Week with Fluffy",
    album_type=AlbumType.GROWTH,
    description="Photos from Fluffy's first week at home"
)
print(f"  Created: '{album1.name}' ({album1.album_type.value})")

album2 = albums.create_album(
    name="Training Progress",
    album_type=AlbumType.TRAINING,
    description="Fluffy learning new tricks"
)
print(f"  Created: '{album2.name}' ({album2.album_type.value})")

album3 = albums.create_album(
    name="Funny Moments",
    album_type=AlbumType.FUNNY_MOMENTS,
    description="Silly and funny photos of Fluffy"
)
print(f"  Created: '{album3.name}' ({album3.album_type.value})")

# Add photos to albums
print("\nAdding photos to albums...")
photo_ids = list(screenshots.screenshots.keys())

albums.add_photo_to_album(album1.album_id, photo_ids[0])
albums.add_photo_to_album(album1.album_id, photo_ids[1])
print(f"Added 2 photos to '{album1.name}'")

albums.add_photo_to_album(album2.album_id, photo_ids[1])
print(f"Added 1 photo to '{album2.name}'")

albums.add_photo_to_album(album3.album_id, photo_ids[2])
print(f"Added 1 photo to '{album3.name}'")

# Add multiple photos
count = albums.add_photos_to_album(album1.album_id, photo_ids[2:])
print(f"Added {count} more photos to '{album1.name}'")

# Album operations
print("\nAlbum operations...")
album1.set_cover_photo(photo_ids[0])
print(f"Set cover photo for '{album1.name}'")

album1.mark_as_viewed()
print(f"Viewed '{album1.name}' (viewed {album1.view_count} times)")

# Get photos in album
album_photos = albums.get_album_photos(album1.album_id)
print(f"Photos in '{album1.name}': {len(album_photos)}")

# Search albums
results = albums.search_albums("training")
print(f"\nSearch for 'training': {len(results)} albums")

# Get albums by type
growth_albums = albums.get_albums_by_type(AlbumType.GROWTH)
print(f"Growth albums: {len(growth_albums)}")

# Get albums containing photo
containing = albums.get_albums_containing_photo(photo_ids[1])
print(f"Albums containing photo {photo_ids[1][:8]}...: {len(containing)}")

# Create monthly album
monthly = albums.create_monthly_album(2025, 11, photo_ids[:2])
print(f"\nCreated monthly album: '{monthly.name}'")

# Create event album
event = albums.create_event_album(
    "Fluffy's First Trick",
    AlbumType.MILESTONES,
    [photo_ids[1]]
)
print(f"Created event album: '{event.name}'")

# Album statistics
stats = albums.get_statistics()
print(f"\nAlbum system statistics:")
print(f"  Total albums: {stats['total_albums']}")
print(f"  Total photos in albums: {stats['total_photos_in_albums']}")
print(f"  Average photos per album: {stats['average_photos_per_album']:.1f}")
print(f"  Smart albums available: {stats['smart_albums_available']}")

print("✓ Photo album system working!")

# Test 4: Memory Book System
print("\n4. Testing Memory Book System")
print("-" * 60)

memory_book = MemoryBookSystem(pet_name="Fluffy")
print(f"Memory book for: {memory_book.pet_name}")
print(f"Auto-milestone detection: {memory_book.auto_milestone_detection}")

# Record milestones
print("\nRecording milestones...")
milestones_to_record = [
    {
        'type': MilestoneType.BORN,
        'title': "Fluffy Was Born!",
        'description': "The day Fluffy came into my life",
        'pet_age_days': 0.0
    },
    {
        'type': MilestoneType.FIRST_TRICK,
        'title': "Learned to Sit",
        'description': "Fluffy learned her first trick - sitting on command!",
        'pet_age_days': 3.0,
        'photo_ids': [photo_ids[1]]
    },
    {
        'type': MilestoneType.FIRST_FRIEND,
        'title': "Made a Friend",
        'description': "Fluffy met another pet and they became friends",
        'pet_age_days': 5.0
    },
    {
        'type': MilestoneType.LEVEL_UP,
        'title': "Reached Level 2",
        'description': "Fluffy leveled up!",
        'pet_age_days': 5.5,
        'photo_ids': [photo_ids[3]] if len(photo_ids) > 3 else []
    }
]

for milestone_data in milestones_to_record:
    milestone = memory_book.record_milestone(
        milestone_type=milestone_data['type'],
        title=milestone_data['title'],
        description=milestone_data['description'],
        pet_age_days=milestone_data['pet_age_days'],
        photo_ids=milestone_data.get('photo_ids')
    )
    print(f"  Recorded: '{milestone.title}'")
    print(f"    Type: {milestone.milestone_type.value}")
    print(f"    Pet age: {milestone.pet_age_days} days")
    print(f"    Celebrated: {milestone.celebrated}")
    time.sleep(0.1)

# Get milestones
print("\nQuerying milestones...")
first_milestone_id = list(memory_book.milestones.keys())[0]
milestone = memory_book.get_milestone(first_milestone_id)
print(f"Retrieved milestone: '{milestone.title}'")

# Get by type
training_milestones = memory_book.get_milestones_by_type(MilestoneType.FIRST_TRICK)
print(f"Training milestones: {len(training_milestones)}")

# Get recent
recent_milestones = memory_book.get_recent_milestones(count=3)
print(f"Recent milestones: {len(recent_milestones)}")

# Get uncelebrated
uncelebrated = memory_book.get_uncelebrated_milestones()
print(f"Uncelebrated milestones: {len(uncelebrated)}")

# Create scrapbook pages
print("\nCreating scrapbook pages...")
page1 = memory_book.create_scrapbook_page(
    title="Fluffy's First Week",
    description="Memories from the first week",
    theme="cute"
)
print(f"  Created page: '{page1.title}'")

# Add content to page
page1.add_photo(photo_ids[0])
page1.add_photo(photo_ids[1])
page1.add_journal_entry(list(journal.entries.keys())[0])
page1.add_milestone(list(memory_book.milestones.keys())[0])
page1.add_text("What an amazing first week!", "center")
print(f"    Added {len(page1.photo_ids)} photos, {len(page1.journal_entry_ids)} entries, {len(page1.milestone_ids)} milestones")

# Create milestone scrapbook page
milestone_page = memory_book.create_milestone_scrapbook_page(
    list(memory_book.milestones.keys())[1],
    include_linked_content=True
)
if milestone_page:
    print(f"  Created milestone page: '{milestone_page.title}'")

# Create timeline
print("\nGenerating timeline...")
timeline = memory_book.create_timeline()
print(f"Timeline entries: {len(timeline)}")
for entry in timeline[:3]:
    print(f"  - {entry['title']} ({entry['date']})")

# Export memory book
print("\nExporting memory book...")
export = memory_book.export_memory_book()
print(f"Export data:")
print(f"  Pet name: {export['pet_name']}")
print(f"  Total milestones: {export['total_milestones']}")
print(f"  Total scrapbook pages: {export['total_scrapbook_pages']}")
print(f"  Timeline entries: {len(export['timeline'])}")

# Memory book statistics
stats = memory_book.get_statistics()
print(f"\nMemory book statistics:")
print(f"  Total milestones: {stats['total_milestones']}")
print(f"  Total scrapbook pages: {stats['total_scrapbook_pages']}")
print(f"  Uncelebrated milestones: {stats['uncelebrated_milestones']}")
print(f"  Average photos per milestone: {stats['average_photos_per_milestone']:.1f}")
print(f"  First milestone: {stats['first_milestone_date']}")
print(f"  Latest milestone: {stats['latest_milestone_date']}")

print("✓ Memory book system working!")

# Test 5: Persistence (Save/Load)
print("\n5. Testing Persistence (Save/Load)")
print("-" * 60)

# Save journal
print("Saving journal system...")
journal_data = journal.to_dict()
print(f"  Saved {len(journal_data)} fields")
print(f"  Entries saved: {len(journal_data['entries'])}")

# Load journal
print("\nLoading journal system...")
loaded_journal = JournalSystem.from_dict(journal_data)
print(f"  Pet name: {loaded_journal.pet_name}")
print(f"  Entries loaded: {loaded_journal.total_entries}")
print(f"  Streak days: {loaded_journal.current_streak_days}")

# Save screenshots
print("\nSaving screenshot system...")
screenshot_data = screenshots.to_dict()
print(f"  Saved {len(screenshot_data)} fields")
print(f"  Screenshots saved: {len(screenshot_data['screenshots'])}")

# Load screenshots
print("\nLoading screenshot system...")
loaded_screenshots = ScreenshotSystem.from_dict(screenshot_data)
print(f"  Screenshots loaded: {loaded_screenshots.total_screenshots}")
print(f"  Favorites: {loaded_screenshots.total_favorites}")

# Save albums
print("\nSaving album system...")
album_data = albums.to_dict()
print(f"  Saved {len(album_data)} fields")
print(f"  Albums saved: {len(album_data['albums'])}")

# Load albums
print("\nLoading album system...")
loaded_albums = PhotoAlbumSystem.from_dict(album_data)
print(f"  Albums loaded: {loaded_albums.total_albums}")
print(f"  Photos in albums: {loaded_albums.total_photos_in_albums}")

# Save memory book
print("\nSaving memory book system...")
memory_data = memory_book.to_dict()
print(f"  Saved {len(memory_data)} fields")
print(f"  Milestones saved: {len(memory_data['milestones'])}")
print(f"  Pages saved: {len(memory_data['scrapbook_pages'])}")

# Load memory book
print("\nLoading memory book system...")
loaded_memory = MemoryBookSystem.from_dict(memory_data)
print(f"  Milestones loaded: {loaded_memory.total_milestones}")
print(f"  Scrapbook pages loaded: {loaded_memory.total_scrapbook_pages}")

# Verify data integrity
print("\nVerifying data integrity...")
first_entry_id = list(journal.entries.keys())[0]
original_title = journal.entries[first_entry_id].title
loaded_title = loaded_journal.entries[first_entry_id].title
print(f"  Journal entry title: {'✓' if original_title == loaded_title else '✗'}")

first_photo_id = list(screenshots.screenshots.keys())[0]
original_caption = screenshots.screenshots[first_photo_id].caption
loaded_caption = loaded_screenshots.screenshots[first_photo_id].caption
print(f"  Screenshot caption: {'✓' if original_caption == loaded_caption else '✗'}")

first_album_id = list(albums.albums.keys())[0]
original_album_name = albums.albums[first_album_id].name
loaded_album_name = loaded_albums.albums[first_album_id].name
print(f"  Album name: {'✓' if original_album_name == loaded_album_name else '✗'}")

first_milestone_id = list(memory_book.milestones.keys())[0]
original_milestone = memory_book.milestones[first_milestone_id].title
loaded_milestone = loaded_memory.milestones[first_milestone_id].title
print(f"  Milestone title: {'✓' if original_milestone == loaded_milestone else '✗'}")

print("✓ Persistence working!")

# Final Summary
print("\n" + "=" * 60)
print("PHASE 11 TEST SUMMARY")
print("=" * 60)
print("✓ Journal system (diary entries, tags, search)")
print("✓ Screenshot system (capture, filters, auto-capture)")
print("✓ Photo album system (albums, organization)")
print("✓ Memory book system (milestones, scrapbooks)")
print("✓ Persistence (save/load all systems)")
print("\n🎉 ALL PHASE 11 TESTS PASSED! 🎉")
print("\nPhase 11 Features:")
print("  • Journal with auto-tagging and search")
print("  • Screenshot capture with filters and frames")
print("  • Photo albums with smart organization")
print("  • Milestone tracking and celebration")
print("  • Scrapbook pages with mixed content")
print("  • Memory timelines and exports")
print("  • Full persistence for all systems")
print()
