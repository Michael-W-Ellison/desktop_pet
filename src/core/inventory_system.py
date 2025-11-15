"""
Phase 13: Inventory System

Manages the player's owned items and their usage.
"""
import time
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class ItemType(Enum):
    """Types of inventory items."""
    CONSUMABLE = "consumable"      # Can be used and depleted (food, treats)
    EQUIPMENT = "equipment"         # Can be equipped (accessories, furniture)
    TOY = "toy"                    # Can be used multiple times
    COLLECTIBLE = "collectible"    # Just for collecting
    SPECIAL = "special"            # Special items


class InventorySlot:
    """Represents an item in the inventory."""

    def __init__(self, item_id: str, item_name: str, item_type: ItemType,
                 quantity: int = 1):
        """
        Initialize inventory slot.

        Args:
            item_id: Item identifier
            item_name: Item name
            item_type: Type of item
            quantity: Quantity owned
        """
        self.item_id = item_id
        self.item_name = item_name
        self.item_type = item_type
        self.quantity = quantity

        # Metadata
        self.acquired_timestamp = time.time()
        self.times_used = 0
        self.favorite = False
        self.equipped = False

        # Effects (copied from shop item)
        self.effects: Dict[str, float] = {}

        # Durability (for equipment/toys)
        self.max_durability = 100
        self.current_durability = 100

    def use(self, amount: int = 1) -> bool:
        """
        Use item (reduce quantity for consumables).

        Args:
            amount: Amount to use

        Returns:
            True if successful
        """
        if self.item_type == ItemType.CONSUMABLE:
            if self.quantity < amount:
                return False
            self.quantity -= amount
            self.times_used += amount
            return True
        else:
            # Non-consumables don't deplete
            self.times_used += 1
            # Reduce durability for equipment/toys
            if self.item_type in [ItemType.EQUIPMENT, ItemType.TOY]:
                self.current_durability = max(0, self.current_durability - 5)
            return True

    def repair(self, amount: int):
        """Repair item durability."""
        self.current_durability = min(self.max_durability, self.current_durability + amount)

    def is_depleted(self) -> bool:
        """Check if item is fully depleted."""
        if self.item_type == ItemType.CONSUMABLE:
            return self.quantity <= 0
        return self.current_durability <= 0

    def can_stack_with(self, other: 'InventorySlot') -> bool:
        """Check if can stack with another slot."""
        return (self.item_id == other.item_id and
                self.item_type == ItemType.CONSUMABLE)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'item_id': self.item_id,
            'item_name': self.item_name,
            'item_type': self.item_type.value,
            'quantity': self.quantity,
            'acquired_timestamp': self.acquired_timestamp,
            'times_used': self.times_used,
            'favorite': self.favorite,
            'equipped': self.equipped,
            'effects': self.effects,
            'max_durability': self.max_durability,
            'current_durability': self.current_durability
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventorySlot':
        """Deserialize from dictionary."""
        slot = cls(
            item_id=data['item_id'],
            item_name=data['item_name'],
            item_type=ItemType(data['item_type']),
            quantity=data.get('quantity', 1)
        )
        slot.acquired_timestamp = data.get('acquired_timestamp', time.time())
        slot.times_used = data.get('times_used', 0)
        slot.favorite = data.get('favorite', False)
        slot.equipped = data.get('equipped', False)
        slot.effects = data.get('effects', {})
        slot.max_durability = data.get('max_durability', 100)
        slot.current_durability = data.get('current_durability', 100)
        return slot


class InventorySystem:
    """
    Manages the player's item inventory.

    Features:
    - Store and organize owned items
    - Use consumable items
    - Equip accessories and furniture
    - Track item usage
    - Manage inventory capacity
    - Sort and filter items
    """

    def __init__(self):
        """Initialize inventory system."""
        # Inventory storage
        self.slots: Dict[str, InventorySlot] = {}  # item_id: slot
        self.max_capacity = 100
        self.auto_stack = True

        # Equipment slots
        self.equipped_accessory: Optional[str] = None  # item_id
        self.equipped_bed: Optional[str] = None
        self.active_toys: List[str] = []  # Up to 3 active toys

        # Statistics
        self.total_items_acquired = 0
        self.total_items_used = 0
        self.total_items_discarded = 0
        self.unique_items_owned = 0

    def add_item(self, item_id: str, item_name: str, item_type: ItemType,
                 quantity: int = 1, effects: Optional[Dict[str, float]] = None) -> bool:
        """
        Add item to inventory.

        Args:
            item_id: Item identifier
            item_name: Item name
            item_type: Type of item
            quantity: Quantity to add
            effects: Item effects

        Returns:
            True if successful
        """
        # Check capacity
        if not self._has_capacity(item_id, quantity):
            return False

        # Try to stack with existing item
        if self.auto_stack and item_id in self.slots:
            slot = self.slots[item_id]
            if slot.can_stack_with(InventorySlot(item_id, item_name, item_type)):
                slot.quantity += quantity
                self.total_items_acquired += quantity
                return True

        # Create new slot
        if item_id in self.slots:
            # Non-stackable duplicate - can't add
            return False

        slot = InventorySlot(item_id, item_name, item_type, quantity)
        if effects:
            slot.effects = effects.copy()

        self.slots[item_id] = slot
        self.total_items_acquired += quantity
        self.unique_items_owned = len(self.slots)

        return True

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Remove item from inventory.

        Args:
            item_id: Item to remove
            quantity: Quantity to remove

        Returns:
            True if successful
        """
        slot = self.slots.get(item_id)
        if not slot:
            return False

        if slot.quantity < quantity:
            return False

        slot.quantity -= quantity

        # Remove slot if depleted
        if slot.quantity <= 0:
            # Unequip if equipped
            self._unequip_if_equipped(item_id)
            del self.slots[item_id]
            self.unique_items_owned = len(self.slots)

        return True

    def use_item(self, item_id: str, amount: int = 1) -> Optional[Dict[str, Any]]:
        """
        Use an item.

        Args:
            item_id: Item to use
            amount: Amount to use

        Returns:
            Result with effects applied
        """
        slot = self.slots.get(item_id)
        if not slot:
            return None

        # Use the item
        if not slot.use(amount):
            return {'error': 'insufficient_quantity'}

        self.total_items_used += amount

        # Remove if depleted
        if slot.is_depleted():
            self._unequip_if_equipped(item_id)
            del self.slots[item_id]
            self.unique_items_owned = len(self.slots)

        # Return effects
        return {
            'success': True,
            'item_id': item_id,
            'item_name': slot.item_name,
            'amount_used': amount,
            'effects': slot.effects,
            'remaining': slot.quantity if slot.item_type == ItemType.CONSUMABLE else None
        }

    def equip_item(self, item_id: str) -> bool:
        """
        Equip an item.

        Args:
            item_id: Item to equip

        Returns:
            True if successful
        """
        slot = self.slots.get(item_id)
        if not slot:
            return False

        if slot.item_type != ItemType.EQUIPMENT:
            return False

        # Determine equipment slot based on item_id patterns
        if any(x in item_id for x in ['collar', 'bow_tie', 'bandana']):
            # Unequip current accessory
            if self.equipped_accessory:
                old_slot = self.slots.get(self.equipped_accessory)
                if old_slot:
                    old_slot.equipped = False

            self.equipped_accessory = item_id
            slot.equipped = True

        elif any(x in item_id for x in ['bed']):
            # Unequip current bed
            if self.equipped_bed:
                old_slot = self.slots.get(self.equipped_bed)
                if old_slot:
                    old_slot.equipped = False

            self.equipped_bed = item_id
            slot.equipped = True

        return True

    def unequip_item(self, item_id: str) -> bool:
        """Unequip an item."""
        slot = self.slots.get(item_id)
        if not slot or not slot.equipped:
            return False

        slot.equipped = False

        if self.equipped_accessory == item_id:
            self.equipped_accessory = None
        elif self.equipped_bed == item_id:
            self.equipped_bed = None

        return True

    def _unequip_if_equipped(self, item_id: str):
        """Internal helper to unequip item if equipped."""
        if self.equipped_accessory == item_id:
            self.equipped_accessory = None
        elif self.equipped_bed == item_id:
            self.equipped_bed = None
        if item_id in self.active_toys:
            self.active_toys.remove(item_id)

    def set_favorite(self, item_id: str, favorite: bool) -> bool:
        """Mark item as favorite."""
        slot = self.slots.get(item_id)
        if not slot:
            return False

        slot.favorite = favorite
        return True

    def discard_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Discard item from inventory.

        Args:
            item_id: Item to discard
            quantity: Quantity to discard

        Returns:
            True if successful
        """
        if self.remove_item(item_id, quantity):
            self.total_items_discarded += quantity
            return True
        return False

    def _has_capacity(self, item_id: str, quantity: int) -> bool:
        """Check if has capacity for item."""
        # If item exists and can stack, always has capacity
        if item_id in self.slots:
            slot = self.slots[item_id]
            if slot.item_type == ItemType.CONSUMABLE:
                return True

        # Check if under max capacity
        return len(self.slots) < self.max_capacity

    def get_item(self, item_id: str) -> Optional[InventorySlot]:
        """Get inventory slot by ID."""
        return self.slots.get(item_id)

    def get_items_by_type(self, item_type: ItemType) -> List[InventorySlot]:
        """Get all items of a type."""
        return [slot for slot in self.slots.values() if slot.item_type == item_type]

    def get_consumables(self) -> List[InventorySlot]:
        """Get all consumable items."""
        return self.get_items_by_type(ItemType.CONSUMABLE)

    def get_equipment(self) -> List[InventorySlot]:
        """Get all equipment items."""
        return self.get_items_by_type(ItemType.EQUIPMENT)

    def get_toys(self) -> List[InventorySlot]:
        """Get all toy items."""
        return self.get_items_by_type(ItemType.TOY)

    def get_equipped_items(self) -> List[InventorySlot]:
        """Get all currently equipped items."""
        return [slot for slot in self.slots.values() if slot.equipped]

    def get_favorites(self) -> List[InventorySlot]:
        """Get all favorite items."""
        return [slot for slot in self.slots.values() if slot.favorite]

    def get_low_quantity_items(self, threshold: int = 3) -> List[InventorySlot]:
        """Get items with quantity below threshold."""
        return [
            slot for slot in self.slots.values()
            if slot.item_type == ItemType.CONSUMABLE and slot.quantity <= threshold
        ]

    def get_damaged_items(self, threshold: float = 0.3) -> List[InventorySlot]:
        """Get items with durability below threshold."""
        return [
            slot for slot in self.slots.values()
            if slot.current_durability / slot.max_durability <= threshold
        ]

    def sort_items(self, sort_by: str = "name") -> List[InventorySlot]:
        """
        Get sorted list of items.

        Args:
            sort_by: Sort criteria (name, type, quantity, acquired, used)

        Returns:
            Sorted list of slots
        """
        items = list(self.slots.values())

        if sort_by == "name":
            items.sort(key=lambda x: x.item_name)
        elif sort_by == "type":
            items.sort(key=lambda x: x.item_type.value)
        elif sort_by == "quantity":
            items.sort(key=lambda x: x.quantity, reverse=True)
        elif sort_by == "acquired":
            items.sort(key=lambda x: x.acquired_timestamp, reverse=True)
        elif sort_by == "used":
            items.sort(key=lambda x: x.times_used, reverse=True)

        return items

    def search_items(self, query: str) -> List[InventorySlot]:
        """Search items by name."""
        query_lower = query.lower()
        return [
            slot for slot in self.slots.values()
            if query_lower in slot.item_name.lower() or query_lower in slot.item_id.lower()
        ]

    def get_total_value(self) -> int:
        """Get total quantity of all items."""
        return sum(slot.quantity for slot in self.slots.values())

    def get_capacity_usage(self) -> float:
        """Get capacity usage percentage."""
        return (len(self.slots) / self.max_capacity) * 100

    def is_full(self) -> bool:
        """Check if inventory is full."""
        return len(self.slots) >= self.max_capacity

    def get_statistics(self) -> Dict[str, Any]:
        """Get inventory statistics."""
        return {
            'unique_items': len(self.slots),
            'total_items': self.get_total_value(),
            'max_capacity': self.max_capacity,
            'capacity_usage': self.get_capacity_usage(),
            'items_by_type': {
                'consumable': len(self.get_consumables()),
                'equipment': len(self.get_equipment()),
                'toy': len(self.get_toys()),
                'collectible': len(self.get_items_by_type(ItemType.COLLECTIBLE)),
                'special': len(self.get_items_by_type(ItemType.SPECIAL))
            },
            'equipped_items': len(self.get_equipped_items()),
            'favorite_items': len(self.get_favorites()),
            'total_acquired': self.total_items_acquired,
            'total_used': self.total_items_used,
            'total_discarded': self.total_items_discarded,
            'low_quantity_items': len(self.get_low_quantity_items()),
            'damaged_items': len(self.get_damaged_items())
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'slots': {
                item_id: slot.to_dict()
                for item_id, slot in self.slots.items()
            },
            'max_capacity': self.max_capacity,
            'auto_stack': self.auto_stack,
            'equipped_accessory': self.equipped_accessory,
            'equipped_bed': self.equipped_bed,
            'active_toys': self.active_toys,
            'total_items_acquired': self.total_items_acquired,
            'total_items_used': self.total_items_used,
            'total_items_discarded': self.total_items_discarded,
            'unique_items_owned': self.unique_items_owned
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventorySystem':
        """Deserialize from dictionary."""
        system = cls()

        # Restore slots
        slots_data = data.get('slots', {})
        for item_id, slot_data in slots_data.items():
            system.slots[item_id] = InventorySlot.from_dict(slot_data)

        system.max_capacity = data.get('max_capacity', 100)
        system.auto_stack = data.get('auto_stack', True)
        system.equipped_accessory = data.get('equipped_accessory')
        system.equipped_bed = data.get('equipped_bed')
        system.active_toys = data.get('active_toys', [])
        system.total_items_acquired = data.get('total_items_acquired', 0)
        system.total_items_used = data.get('total_items_used', 0)
        system.total_items_discarded = data.get('total_items_discarded', 0)
        system.unique_items_owned = data.get('unique_items_owned', 0)

        return system
