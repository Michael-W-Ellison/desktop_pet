"""
Phase 14: Room Decoration System

Manages room appearance, wallpapers, floors, and themes.
"""
import time
from typing import Dict, Any, List, Optional
from enum import Enum


class WallpaperStyle(Enum):
    """Wallpaper/background styles."""
    PLAIN = "plain"                # Solid color
    STRIPES = "stripes"            # Vertical stripes
    POLKA_DOTS = "polka_dots"      # Polka dot pattern
    HEARTS = "hearts"              # Heart pattern
    STARS = "stars"                # Star pattern
    CLOUDS = "clouds"              # Cloud pattern
    FLOWERS = "flowers"            # Floral pattern
    GEOMETRIC = "geometric"        # Geometric shapes
    WOOD = "wood"                  # Wood texture
    BRICK = "brick"                # Brick texture
    STONE = "stone"                # Stone texture
    GRASS = "grass"                # Grass texture
    SPACE = "space"                # Space/galaxy theme
    UNDERWATER = "underwater"      # Underwater theme
    FOREST = "forest"              # Forest theme


class FloorStyle(Enum):
    """Floor styles."""
    CARPET = "carpet"              # Soft carpet
    WOOD = "wood"                  # Wooden floor
    TILE = "tile"                  # Tile floor
    STONE = "stone"                # Stone floor
    GRASS = "grass"                # Grass (outdoor)
    SAND = "sand"                  # Sand (beach)
    SNOW = "snow"                  # Snow (winter)
    CLOUDS = "clouds"              # Clouds (sky)
    WATER = "water"                # Water (pool/ocean)
    MARBLE = "marble"              # Marble floor


class RoomTheme(Enum):
    """Pre-defined room themes."""
    COZY_HOME = "cozy_home"        # Warm, comfortable home
    MODERN = "modern"              # Clean, modern style
    RUSTIC = "rustic"              # Natural, rustic
    PRINCESS = "princess"          # Pink, fancy, royal
    SPACE = "space"                # Outer space theme
    UNDERWATER = "underwater"      # Ocean/aquarium theme
    FOREST = "forest"              # Woodland theme
    BEACH = "beach"                # Beach/tropical theme
    WINTER = "winter"              # Snow/ice theme
    GARDEN = "garden"              # Flower garden theme
    RETRO = "retro"                # Retro/vintage style
    NEON = "neon"                  # Neon/cyberpunk style


class DecorationItem:
    """Represents a decorative room item."""

    def __init__(self, item_id: str, name: str, description: str = ""):
        """
        Initialize decoration item.

        Args:
            item_id: Unique item ID
            name: Item name
            description: Item description
        """
        self.item_id = item_id
        self.name = name
        self.description = description

        # Properties
        self.unlocked = True
        self.unlock_cost = 0
        self.times_used = 0
        self.favorite = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'item_id': self.item_id,
            'name': self.name,
            'description': self.description,
            'unlocked': self.unlocked,
            'unlock_cost': self.unlock_cost,
            'times_used': self.times_used,
            'favorite': self.favorite
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecorationItem':
        """Deserialize from dictionary."""
        item = cls(
            item_id=data['item_id'],
            name=data['name'],
            description=data.get('description', '')
        )
        item.unlocked = data.get('unlocked', True)
        item.unlock_cost = data.get('unlock_cost', 0)
        item.times_used = data.get('times_used', 0)
        item.favorite = data.get('favorite', False)
        return item


class RoomDecoration:
    """
    Manages room decoration and appearance.

    Features:
    - Wallpaper selection
    - Floor selection
    - Background effects
    - Room themes
    - Lighting
    - Color customization
    """

    def __init__(self):
        """Initialize room decoration."""
        # Wallpaper
        self.wallpaper_style = WallpaperStyle.PLAIN
        self.wallpaper_color = "220,220,220"   # Light gray
        self.wallpaper_secondary_color = "200,200,200"

        # Floor
        self.floor_style = FloorStyle.WOOD
        self.floor_color = "139,90,43"         # Brown wood
        self.floor_secondary_color = "101,67,33"

        # Background
        self.background_image: Optional[str] = None
        self.background_opacity = 1.0          # 0-1
        self.background_blur = 0               # 0-10

        # Lighting
        self.ambient_light_color = "255,255,255"  # White
        self.ambient_light_intensity = 1.0     # 0-1
        self.shadow_intensity = 0.5            # 0-1

        # Effects
        self.particle_effects: List[str] = []  # e.g., "snow", "rain", "sparkles"
        self.weather_effect: Optional[str] = None

        # Active theme
        self.active_theme = RoomTheme.COZY_HOME

        # Available decorations
        self.available_wallpapers: Dict[str, DecorationItem] = {}
        self.available_floors: Dict[str, DecorationItem] = {}

        # Statistics
        self.decoration_changes = 0
        self.themes_applied = 0
        self.favorite_theme = RoomTheme.COZY_HOME

        # Create default decorations
        self._create_default_decorations()

    def _create_default_decorations(self):
        """Create default wallpapers and floors."""
        # Wallpapers
        wallpapers = [
            ('wp_plain_white', 'Plain White', 'Simple white wallpaper'),
            ('wp_plain_blue', 'Plain Blue', 'Light blue wallpaper'),
            ('wp_plain_pink', 'Plain Pink', 'Soft pink wallpaper'),
            ('wp_stripes_blue', 'Blue Stripes', 'Blue and white stripes'),
            ('wp_dots_pink', 'Pink Polka Dots', 'Pink polka dots on white'),
            ('wp_hearts', 'Hearts Pattern', 'Cute heart pattern'),
            ('wp_stars', 'Stars Pattern', 'Starry pattern'),
            ('wp_flowers', 'Floral Pattern', 'Pretty flower pattern'),
            ('wp_clouds', 'Cloudy Sky', 'Blue sky with clouds'),
            ('wp_space', 'Space Theme', 'Galaxy and stars'),
        ]

        for wp_id, name, desc in wallpapers:
            self.available_wallpapers[wp_id] = DecorationItem(wp_id, name, desc)

        # Floors
        floors = [
            ('floor_wood_light', 'Light Wood', 'Light wooden floor'),
            ('floor_wood_dark', 'Dark Wood', 'Dark wooden floor'),
            ('floor_carpet_blue', 'Blue Carpet', 'Soft blue carpet'),
            ('floor_carpet_pink', 'Pink Carpet', 'Soft pink carpet'),
            ('floor_tile_white', 'White Tile', 'Clean white tiles'),
            ('floor_tile_checkered', 'Checkered Tile', 'Black and white checkered'),
            ('floor_grass', 'Grass', 'Green grass floor'),
            ('floor_sand', 'Sand', 'Sandy beach floor'),
            ('floor_marble', 'Marble', 'Elegant marble floor'),
        ]

        for floor_id, name, desc in floors:
            self.available_floors[floor_id] = DecorationItem(floor_id, name, desc)

    def set_wallpaper_style(self, style: WallpaperStyle):
        """Set wallpaper pattern style."""
        self.wallpaper_style = style
        self.decoration_changes += 1

    def set_wallpaper_color(self, r: int, g: int, b: int):
        """Set wallpaper primary color."""
        self.wallpaper_color = f"{r},{g},{b}"
        self.decoration_changes += 1

    def set_wallpaper_secondary_color(self, r: int, g: int, b: int):
        """Set wallpaper secondary color (for patterns)."""
        self.wallpaper_secondary_color = f"{r},{g},{b}"
        self.decoration_changes += 1

    def set_floor_style(self, style: FloorStyle):
        """Set floor style."""
        self.floor_style = style
        self.decoration_changes += 1

    def set_floor_color(self, r: int, g: int, b: int):
        """Set floor primary color."""
        self.floor_color = f"{r},{g},{b}"
        self.decoration_changes += 1

    def set_floor_secondary_color(self, r: int, g: int, b: int):
        """Set floor secondary color."""
        self.floor_secondary_color = f"{r},{g},{b}"
        self.decoration_changes += 1

    def set_lighting(self, r: int, g: int, b: int, intensity: float = 1.0):
        """
        Set ambient lighting.

        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            intensity: Light intensity (0-1)
        """
        self.ambient_light_color = f"{r},{g},{b}"
        self.ambient_light_intensity = max(0.0, min(1.0, intensity))
        self.decoration_changes += 1

    def set_shadow_intensity(self, intensity: float):
        """Set shadow intensity (0-1)."""
        self.shadow_intensity = max(0.0, min(1.0, intensity))
        self.decoration_changes += 1

    def add_particle_effect(self, effect: str):
        """Add particle effect (snow, rain, sparkles, etc.)."""
        if effect not in self.particle_effects:
            self.particle_effects.append(effect)
            self.decoration_changes += 1

    def remove_particle_effect(self, effect: str):
        """Remove particle effect."""
        if effect in self.particle_effects:
            self.particle_effects.remove(effect)
            self.decoration_changes += 1

    def clear_particle_effects(self):
        """Remove all particle effects."""
        self.particle_effects.clear()
        self.decoration_changes += 1

    def set_weather_effect(self, weather: Optional[str]):
        """Set weather effect (sunny, rainy, snowy, etc.)."""
        self.weather_effect = weather
        self.decoration_changes += 1

    def apply_theme(self, theme: RoomTheme):
        """
        Apply a pre-defined room theme.

        Args:
            theme: Theme to apply
        """
        self.active_theme = theme
        self.favorite_theme = theme
        self.themes_applied += 1

        # Define theme settings
        themes = {
            RoomTheme.COZY_HOME: {
                'wallpaper': WallpaperStyle.PLAIN,
                'wallpaper_color': "245,222,179",  # Wheat
                'floor': FloorStyle.WOOD,
                'floor_color': "139,90,43",        # Brown
                'light': "255,250,205",            # Lemon chiffon
                'effects': []
            },
            RoomTheme.MODERN: {
                'wallpaper': WallpaperStyle.PLAIN,
                'wallpaper_color': "240,240,240",  # Light gray
                'floor': FloorStyle.TILE,
                'floor_color': "200,200,200",      # Gray
                'light': "255,255,255",            # White
                'effects': []
            },
            RoomTheme.PRINCESS: {
                'wallpaper': WallpaperStyle.HEARTS,
                'wallpaper_color': "255,182,193",  # Light pink
                'floor': FloorStyle.CARPET,
                'floor_color': "255,192,203",      # Pink
                'light': "255,218,224",            # Pink light
                'effects': ['sparkles']
            },
            RoomTheme.SPACE: {
                'wallpaper': WallpaperStyle.SPACE,
                'wallpaper_color': "25,25,112",    # Midnight blue
                'floor': FloorStyle.CLOUDS,
                'floor_color': "70,70,120",        # Dark blue
                'light': "138,43,226",             # Blue violet
                'effects': ['stars']
            },
            RoomTheme.UNDERWATER: {
                'wallpaper': WallpaperStyle.UNDERWATER,
                'wallpaper_color': "0,105,148",    # Deep blue
                'floor': FloorStyle.WATER,
                'floor_color': "135,206,250",      # Light blue
                'light': "0,191,255",              # Deep sky blue
                'effects': ['bubbles']
            },
            RoomTheme.FOREST: {
                'wallpaper': WallpaperStyle.FOREST,
                'wallpaper_color': "34,139,34",    # Forest green
                'floor': FloorStyle.GRASS,
                'floor_color': "107,142,35",       # Olive green
                'light': "144,238,144",            # Light green
                'effects': ['leaves']
            },
            RoomTheme.BEACH: {
                'wallpaper': WallpaperStyle.CLOUDS,
                'wallpaper_color': "135,206,235",  # Sky blue
                'floor': FloorStyle.SAND,
                'floor_color': "238,214,175",      # Sand
                'light': "255,255,200",            # Sunny
                'effects': []
            },
            RoomTheme.WINTER: {
                'wallpaper': WallpaperStyle.PLAIN,
                'wallpaper_color': "176,224,230",  # Powder blue
                'floor': FloorStyle.SNOW,
                'floor_color': "255,250,250",      # Snow white
                'light': "230,230,250",            # Lavender
                'effects': ['snow']
            },
            RoomTheme.GARDEN: {
                'wallpaper': WallpaperStyle.FLOWERS,
                'wallpaper_color': "152,251,152",  # Pale green
                'floor': FloorStyle.GRASS,
                'floor_color': "124,252,0",        # Lawn green
                'light': "255,255,224",            # Light yellow
                'effects': ['butterflies']
            },
            RoomTheme.NEON: {
                'wallpaper': WallpaperStyle.GEOMETRIC,
                'wallpaper_color': "25,25,25",     # Dark gray
                'floor': FloorStyle.TILE,
                'floor_color': "50,50,50",         # Darker gray
                'light': "0,255,255",              # Cyan
                'effects': ['neon_lights']
            }
        }

        settings = themes.get(theme)
        if settings:
            self.wallpaper_style = settings['wallpaper']
            self.wallpaper_color = settings['wallpaper_color']
            self.floor_style = settings['floor']
            self.floor_color = settings['floor_color']
            self.ambient_light_color = settings['light']
            self.particle_effects = settings['effects'].copy()

        self.decoration_changes += 1

    def unlock_wallpaper(self, wallpaper_id: str) -> bool:
        """Unlock a wallpaper."""
        wallpaper = self.available_wallpapers.get(wallpaper_id)
        if wallpaper:
            wallpaper.unlocked = True
            return True
        return False

    def unlock_floor(self, floor_id: str) -> bool:
        """Unlock a floor."""
        floor = self.available_floors.get(floor_id)
        if floor:
            floor.unlocked = True
            return True
        return False

    def get_unlocked_wallpapers(self) -> List[DecorationItem]:
        """Get all unlocked wallpapers."""
        return [wp for wp in self.available_wallpapers.values() if wp.unlocked]

    def get_unlocked_floors(self) -> List[DecorationItem]:
        """Get all unlocked floors."""
        return [floor for floor in self.available_floors.values() if floor.unlocked]

    def get_room_summary(self) -> Dict[str, Any]:
        """Get summary of current room appearance."""
        return {
            'wallpaper': {
                'style': self.wallpaper_style.value,
                'color': self.wallpaper_color,
                'secondary_color': self.wallpaper_secondary_color
            },
            'floor': {
                'style': self.floor_style.value,
                'color': self.floor_color,
                'secondary_color': self.floor_secondary_color
            },
            'lighting': {
                'color': self.ambient_light_color,
                'intensity': self.ambient_light_intensity,
                'shadow_intensity': self.shadow_intensity
            },
            'effects': {
                'particles': self.particle_effects,
                'weather': self.weather_effect
            },
            'theme': self.active_theme.value
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get decoration statistics."""
        return {
            'decoration_changes': self.decoration_changes,
            'themes_applied': self.themes_applied,
            'favorite_theme': self.favorite_theme.value,
            'active_theme': self.active_theme.value,
            'unlocked_wallpapers': len(self.get_unlocked_wallpapers()),
            'total_wallpapers': len(self.available_wallpapers),
            'unlocked_floors': len(self.get_unlocked_floors()),
            'total_floors': len(self.available_floors),
            'active_effects': len(self.particle_effects)
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'wallpaper_style': self.wallpaper_style.value,
            'wallpaper_color': self.wallpaper_color,
            'wallpaper_secondary_color': self.wallpaper_secondary_color,
            'floor_style': self.floor_style.value,
            'floor_color': self.floor_color,
            'floor_secondary_color': self.floor_secondary_color,
            'background_image': self.background_image,
            'background_opacity': self.background_opacity,
            'background_blur': self.background_blur,
            'ambient_light_color': self.ambient_light_color,
            'ambient_light_intensity': self.ambient_light_intensity,
            'shadow_intensity': self.shadow_intensity,
            'particle_effects': self.particle_effects,
            'weather_effect': self.weather_effect,
            'active_theme': self.active_theme.value,
            'available_wallpapers': {
                wp_id: wp.to_dict()
                for wp_id, wp in self.available_wallpapers.items()
            },
            'available_floors': {
                floor_id: floor.to_dict()
                for floor_id, floor in self.available_floors.items()
            },
            'decoration_changes': self.decoration_changes,
            'themes_applied': self.themes_applied,
            'favorite_theme': self.favorite_theme.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RoomDecoration':
        """Deserialize from dictionary."""
        decoration = cls()

        decoration.wallpaper_style = WallpaperStyle(data.get('wallpaper_style', 'plain'))
        decoration.wallpaper_color = data.get('wallpaper_color', "220,220,220")
        decoration.wallpaper_secondary_color = data.get('wallpaper_secondary_color', "200,200,200")
        decoration.floor_style = FloorStyle(data.get('floor_style', 'wood'))
        decoration.floor_color = data.get('floor_color', "139,90,43")
        decoration.floor_secondary_color = data.get('floor_secondary_color', "101,67,33")
        decoration.background_image = data.get('background_image')
        decoration.background_opacity = data.get('background_opacity', 1.0)
        decoration.background_blur = data.get('background_blur', 0)
        decoration.ambient_light_color = data.get('ambient_light_color', "255,255,255")
        decoration.ambient_light_intensity = data.get('ambient_light_intensity', 1.0)
        decoration.shadow_intensity = data.get('shadow_intensity', 0.5)
        decoration.particle_effects = data.get('particle_effects', [])
        decoration.weather_effect = data.get('weather_effect')
        decoration.active_theme = RoomTheme(data.get('active_theme', 'cozy_home'))

        # Restore wallpapers
        wallpapers_data = data.get('available_wallpapers', {})
        for wp_id, wp_data in wallpapers_data.items():
            decoration.available_wallpapers[wp_id] = DecorationItem.from_dict(wp_data)

        # Restore floors
        floors_data = data.get('available_floors', {})
        for floor_id, floor_data in floors_data.items():
            decoration.available_floors[floor_id] = DecorationItem.from_dict(floor_data)

        decoration.decoration_changes = data.get('decoration_changes', 0)
        decoration.themes_applied = data.get('themes_applied', 0)
        decoration.favorite_theme = RoomTheme(data.get('favorite_theme', 'cozy_home'))

        return decoration
