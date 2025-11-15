"""
Phase 13: Shop System

Manages the shop where players can purchase items with coins.
"""
import time
import random
from typing import Dict, Any, List, Optional
from enum import Enum


class ItemCategory(Enum):
    """Item categories."""
    FOOD = "food"
    TREAT = "treat"
    TOY = "toy"
    ACCESSORY = "accessory"
    FURNITURE = "furniture"
    GROOMING = "grooming"
    MEDICINE = "medicine"
    DECORATION = "decoration"
    SPECIAL = "special"


class ItemRarity(Enum):
    """Item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class ShopItem:
    """Represents an item in the shop."""

    def __init__(self, item_id: str, name: str, category: ItemCategory,
                 price: int, description: str = ""):
        """
        Initialize shop item.

        Args:
            item_id: Unique item identifier
            name: Item name
            category: Item category
            price: Price in coins
            description: Item description
        """
        self.item_id = item_id
        self.name = name
        self.category = category
        self.price = price
        self.description = description
        self.rarity = ItemRarity.COMMON

        # Stock
        self.unlimited_stock = True
        self.stock_quantity = 0  # Only used if not unlimited
        self.max_per_purchase = 10

        # Effects (what the item does)
        self.effects: Dict[str, float] = {}  # effect_type: value
        # Examples: hunger_restore: 20, happiness_boost: 10, energy_restore: 15

        # Metadata
        self.on_sale = False
        self.sale_percentage = 0.0
        self.required_level = 1
        self.times_purchased = 0

    def get_sale_price(self) -> int:
        """Get price including any sale discount."""
        if self.on_sale and self.sale_percentage > 0:
            discount = self.price * (self.sale_percentage / 100)
            return int(self.price - discount)
        return self.price

    def is_available(self) -> bool:
        """Check if item is available for purchase."""
        if self.unlimited_stock:
            return True
        return self.stock_quantity > 0

    def can_purchase(self, quantity: int = 1) -> bool:
        """Check if can purchase quantity."""
        if quantity > self.max_per_purchase:
            return False
        if self.unlimited_stock:
            return True
        return self.stock_quantity >= quantity

    def purchase(self, quantity: int = 1) -> bool:
        """
        Purchase item (reduce stock).

        Args:
            quantity: Quantity to purchase

        Returns:
            True if successful
        """
        if not self.can_purchase(quantity):
            return False

        if not self.unlimited_stock:
            self.stock_quantity -= quantity

        self.times_purchased += quantity
        return True

    def restock(self, quantity: int):
        """Add stock."""
        if not self.unlimited_stock:
            self.stock_quantity += quantity

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'item_id': self.item_id,
            'name': self.name,
            'category': self.category.value,
            'price': self.price,
            'description': self.description,
            'rarity': self.rarity.value,
            'unlimited_stock': self.unlimited_stock,
            'stock_quantity': self.stock_quantity,
            'max_per_purchase': self.max_per_purchase,
            'effects': self.effects,
            'on_sale': self.on_sale,
            'sale_percentage': self.sale_percentage,
            'required_level': self.required_level,
            'times_purchased': self.times_purchased
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShopItem':
        """Deserialize from dictionary."""
        item = cls(
            item_id=data['item_id'],
            name=data['name'],
            category=ItemCategory(data['category']),
            price=data['price'],
            description=data.get('description', '')
        )
        item.rarity = ItemRarity(data.get('rarity', 'common'))
        item.unlimited_stock = data.get('unlimited_stock', True)
        item.stock_quantity = data.get('stock_quantity', 0)
        item.max_per_purchase = data.get('max_per_purchase', 10)
        item.effects = data.get('effects', {})
        item.on_sale = data.get('on_sale', False)
        item.sale_percentage = data.get('sale_percentage', 0.0)
        item.required_level = data.get('required_level', 1)
        item.times_purchased = data.get('times_purchased', 0)
        return item


class ShopSystem:
    """
    Manages the shop and item purchases.

    Features:
    - Browse items by category
    - Purchase items with coins
    - Sales and discounts
    - Limited stock items
    - Daily shop refresh
    - Featured items
    """

    def __init__(self):
        """Initialize shop system."""
        # Shop inventory
        self.items: Dict[str, ShopItem] = {}
        self.featured_items: List[str] = []  # Item IDs

        # Shop settings
        self.shop_level = 1
        self.daily_refresh_enabled = True
        self.last_refresh_date: Optional[str] = None

        # Statistics
        self.total_sales = 0
        self.total_revenue = 0
        self.most_popular_item: Optional[str] = None

        # Create default shop items
        self._create_default_items()

    def _create_default_items(self):
        """Create default shop items."""
        # Food items
        food_items = [
            ('kibble', 'Kibble', ItemCategory.FOOD, 5, 'Basic pet food', {'hunger_restore': 20}),
            ('premium_food', 'Premium Food', ItemCategory.FOOD, 15, 'High quality food', {'hunger_restore': 50, 'happiness_boost': 5}),
            ('gourmet_meal', 'Gourmet Meal', ItemCategory.FOOD, 30, 'Delicious gourmet meal', {'hunger_restore': 80, 'happiness_boost': 15}),
        ]

        # Treats
        treat_items = [
            ('bone_treat', 'Bone Treat', ItemCategory.TREAT, 10, 'Tasty bone', {'happiness_boost': 10}),
            ('cookie', 'Cookie', ItemCategory.TREAT, 8, 'Sweet cookie', {'happiness_boost': 8}),
            ('special_treat', 'Special Treat', ItemCategory.TREAT, 25, 'Extra special treat', {'happiness_boost': 20, 'bonding_boost': 5}),
        ]

        # Toys
        toy_items = [
            ('ball', 'Ball', ItemCategory.TOY, 15, 'Bouncy ball', {'happiness_boost': 15}),
            ('rope_toy', 'Rope Toy', ItemCategory.TOY, 20, 'Tug rope', {'happiness_boost': 18}),
            ('squeaky_toy', 'Squeaky Toy', ItemCategory.TOY, 25, 'Makes fun sounds', {'happiness_boost': 22}),
            ('puzzle_toy', 'Puzzle Toy', ItemCategory.TOY, 40, 'Mental stimulation', {'happiness_boost': 25, 'intelligence_boost': 5}),
        ]

        # Accessories
        accessory_items = [
            ('collar_basic', 'Basic Collar', ItemCategory.ACCESSORY, 30, 'Simple collar', {}),
            ('collar_fancy', 'Fancy Collar', ItemCategory.ACCESSORY, 60, 'Stylish collar', {}),
            ('bow_tie', 'Bow Tie', ItemCategory.ACCESSORY, 45, 'Classy bow tie', {}),
            ('bandana', 'Bandana', ItemCategory.ACCESSORY, 35, 'Cool bandana', {}),
        ]

        # Furniture
        furniture_items = [
            ('bed_basic', 'Basic Bed', ItemCategory.FURNITURE, 50, 'Comfy bed', {'energy_restore': 10}),
            ('bed_luxury', 'Luxury Bed', ItemCategory.FURNITURE, 120, 'Very comfy bed', {'energy_restore': 25}),
            ('scratching_post', 'Scratching Post', ItemCategory.FURNITURE, 40, 'For scratching', {'happiness_boost': 5}),
        ]

        # Grooming
        grooming_items = [
            ('brush', 'Brush', ItemCategory.GROOMING, 20, 'Grooming brush', {'cleanliness_boost': 20}),
            ('shampoo', 'Shampoo', ItemCategory.GROOMING, 15, 'Pet shampoo', {'cleanliness_boost': 40}),
        ]

        # Medicine
        medicine_items = [
            ('health_potion', 'Health Potion', ItemCategory.MEDICINE, 50, 'Restores health', {'health_restore': 30}),
            ('energy_drink', 'Energy Drink', ItemCategory.MEDICINE, 35, 'Restores energy', {'energy_restore': 40}),
        ]

        # Combine all items
        all_items = food_items + treat_items + toy_items + accessory_items + furniture_items + grooming_items + medicine_items

        # Create items
        for item_id, name, category, price, desc, effects in all_items:
            item = ShopItem(item_id, name, category, price, desc)
            item.effects = effects
            self.add_item(item)

        # Set some items as rare
        self.items['gourmet_meal'].rarity = ItemRarity.RARE
        self.items['puzzle_toy'].rarity = ItemRarity.RARE
        self.items['bed_luxury'].rarity = ItemRarity.EPIC
        self.items['special_treat'].rarity = ItemRarity.UNCOMMON

    def add_item(self, item: ShopItem):
        """Add item to shop."""
        self.items[item.item_id] = item

    def get_item(self, item_id: str) -> Optional[ShopItem]:
        """Get item by ID."""
        return self.items.get(item_id)

    def get_items_by_category(self, category: ItemCategory) -> List[ShopItem]:
        """Get all items in a category."""
        return [item for item in self.items.values() if item.category == category]

    def get_items_by_rarity(self, rarity: ItemRarity) -> List[ShopItem]:
        """Get all items of a rarity."""
        return [item for item in self.items.values() if item.rarity == rarity]

    def get_affordable_items(self, balance: int) -> List[ShopItem]:
        """Get items player can afford."""
        return [
            item for item in self.items.values()
            if item.get_sale_price() <= balance and item.is_available()
        ]

    def purchase_item(self, item_id: str, quantity: int = 1) -> Optional[Dict[str, Any]]:
        """
        Purchase an item.

        Args:
            item_id: Item to purchase
            quantity: Quantity to purchase

        Returns:
            Purchase result or None
        """
        item = self.get_item(item_id)
        if not item:
            return None

        if not item.is_available():
            return {'error': 'out_of_stock'}

        if not item.can_purchase(quantity):
            return {'error': 'quantity_exceeded'}

        # Calculate total cost
        unit_price = item.get_sale_price()
        total_cost = unit_price * quantity

        # Purchase (stock reduction happens here)
        if item.purchase(quantity):
            # Update statistics
            self.total_sales += quantity
            self.total_revenue += total_cost

            # Update most popular
            self._update_most_popular()

            return {
                'success': True,
                'item_id': item_id,
                'item_name': item.name,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_cost': total_cost,
                'on_sale': item.on_sale
            }

        return {'error': 'purchase_failed'}

    def _update_most_popular(self):
        """Update most popular item."""
        if not self.items:
            return

        most_popular = max(
            self.items.values(),
            key=lambda item: item.times_purchased
        )

        if most_popular.times_purchased > 0:
            self.most_popular_item = most_popular.item_id

    def set_sale(self, item_id: str, percentage: float) -> bool:
        """
        Put item on sale.

        Args:
            item_id: Item to discount
            percentage: Discount percentage (0-100)

        Returns:
            True if successful
        """
        item = self.get_item(item_id)
        if not item:
            return False

        item.on_sale = True
        item.sale_percentage = max(0.0, min(100.0, percentage))
        return True

    def clear_sale(self, item_id: str) -> bool:
        """Remove item from sale."""
        item = self.get_item(item_id)
        if not item:
            return False

        item.on_sale = False
        item.sale_percentage = 0.0
        return True

    def refresh_shop(self):
        """Refresh shop (restock, new sales, featured items)."""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        # Only refresh once per day
        if self.last_refresh_date == today:
            return

        # Restock limited items
        for item in self.items.values():
            if not item.unlimited_stock:
                item.restock(random.randint(5, 20))

        # Clear old sales
        for item in self.items.values():
            item.on_sale = False
            item.sale_percentage = 0.0

        # Random sales
        num_sales = random.randint(2, 5)
        sale_items = random.sample(list(self.items.values()), min(num_sales, len(self.items)))
        for item in sale_items:
            discount = random.choice([10, 15, 20, 25, 30])
            item.on_sale = True
            item.sale_percentage = discount

        # Featured items
        self.featured_items = [
            item.item_id for item in random.sample(list(self.items.values()), min(3, len(self.items)))
        ]

        self.last_refresh_date = today

    def get_featured_items(self) -> List[ShopItem]:
        """Get featured items."""
        return [self.items[item_id] for item_id in self.featured_items if item_id in self.items]

    def get_sale_items(self) -> List[ShopItem]:
        """Get items currently on sale."""
        return [item for item in self.items.values() if item.on_sale]

    def get_statistics(self) -> Dict[str, Any]:
        """Get shop statistics."""
        return {
            'total_items': len(self.items),
            'total_sales': self.total_sales,
            'total_revenue': self.total_revenue,
            'most_popular_item': self.most_popular_item,
            'items_on_sale': len(self.get_sale_items()),
            'featured_items_count': len(self.featured_items),
            'items_by_category': {
                category.value: len(self.get_items_by_category(category))
                for category in ItemCategory
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'items': {
                item_id: item.to_dict()
                for item_id, item in self.items.items()
            },
            'featured_items': self.featured_items,
            'shop_level': self.shop_level,
            'daily_refresh_enabled': self.daily_refresh_enabled,
            'last_refresh_date': self.last_refresh_date,
            'total_sales': self.total_sales,
            'total_revenue': self.total_revenue,
            'most_popular_item': self.most_popular_item
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShopSystem':
        """Deserialize from dictionary."""
        system = cls()

        # Don't create default items, restore from data
        system.items = {}
        items_data = data.get('items', {})
        for item_id, item_data in items_data.items():
            system.items[item_id] = ShopItem.from_dict(item_data)

        system.featured_items = data.get('featured_items', [])
        system.shop_level = data.get('shop_level', 1)
        system.daily_refresh_enabled = data.get('daily_refresh_enabled', True)
        system.last_refresh_date = data.get('last_refresh_date')
        system.total_sales = data.get('total_sales', 0)
        system.total_revenue = data.get('total_revenue', 0)
        system.most_popular_item = data.get('most_popular_item')

        return system
