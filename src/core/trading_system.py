"""
Phase 13: Trading System

Allows trading items between pets (for multi-pet scenarios).
"""
import time
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class TradeStatus(Enum):
    """Status of a trade offer."""
    PENDING = "pending"        # Waiting for response
    ACCEPTED = "accepted"      # Trade accepted and completed
    DECLINED = "declined"      # Trade declined
    CANCELLED = "cancelled"    # Cancelled by proposer
    EXPIRED = "expired"        # Offer expired


class TradeOffer:
    """Represents a trade offer between two pets."""

    def __init__(self, trade_id: str, proposer_id: str, recipient_id: str):
        """
        Initialize trade offer.

        Args:
            trade_id: Unique trade ID
            proposer_id: ID of pet proposing trade
            recipient_id: ID of pet receiving offer
        """
        self.trade_id = trade_id
        self.proposer_id = proposer_id
        self.recipient_id = recipient_id

        # Trade contents
        self.proposer_items: Dict[str, int] = {}  # item_id: quantity
        self.proposer_coins: int = 0
        self.recipient_items: Dict[str, int] = {}  # item_id: quantity
        self.recipient_coins: int = 0

        # Metadata
        self.status = TradeStatus.PENDING
        self.created_timestamp = time.time()
        self.completed_timestamp: Optional[float] = None
        self.expiry_duration = 3600.0  # 1 hour

        # Trade message
        self.message: str = ""

    def add_proposer_item(self, item_id: str, quantity: int):
        """Add item from proposer."""
        self.proposer_items[item_id] = quantity

    def add_proposer_coins(self, amount: int):
        """Add coins from proposer."""
        self.proposer_coins = amount

    def add_recipient_item(self, item_id: str, quantity: int):
        """Add item from recipient."""
        self.recipient_items[item_id] = quantity

    def add_recipient_coins(self, amount: int):
        """Add coins from recipient."""
        self.recipient_coins = amount

    def is_expired(self) -> bool:
        """Check if offer has expired."""
        if self.status != TradeStatus.PENDING:
            return False
        return (time.time() - self.created_timestamp) > self.expiry_duration

    def get_proposer_value(self) -> int:
        """Get estimated value of proposer's offer."""
        # Simple estimation: coins + (items * avg price)
        item_value = len(self.proposer_items) * 20  # Rough estimate
        return self.proposer_coins + item_value

    def get_recipient_value(self) -> int:
        """Get estimated value of recipient's offer."""
        item_value = len(self.recipient_items) * 20
        return self.recipient_coins + item_value

    def is_fair_trade(self, tolerance: float = 0.3) -> bool:
        """
        Check if trade is relatively fair.

        Args:
            tolerance: Acceptable value difference (0-1)

        Returns:
            True if trade is fair
        """
        proposer_val = self.get_proposer_value()
        recipient_val = self.get_recipient_value()

        if proposer_val == 0 and recipient_val == 0:
            return True

        max_val = max(proposer_val, recipient_val)
        min_val = min(proposer_val, recipient_val)

        if max_val == 0:
            return True

        difference_ratio = (max_val - min_val) / max_val
        return difference_ratio <= tolerance

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'trade_id': self.trade_id,
            'proposer_id': self.proposer_id,
            'recipient_id': self.recipient_id,
            'proposer_items': self.proposer_items,
            'proposer_coins': self.proposer_coins,
            'recipient_items': self.recipient_items,
            'recipient_coins': self.recipient_coins,
            'status': self.status.value,
            'created_timestamp': self.created_timestamp,
            'completed_timestamp': self.completed_timestamp,
            'expiry_duration': self.expiry_duration,
            'message': self.message
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradeOffer':
        """Deserialize from dictionary."""
        trade = cls(
            trade_id=data['trade_id'],
            proposer_id=data['proposer_id'],
            recipient_id=data['recipient_id']
        )
        trade.proposer_items = data.get('proposer_items', {})
        trade.proposer_coins = data.get('proposer_coins', 0)
        trade.recipient_items = data.get('recipient_items', {})
        trade.recipient_coins = data.get('recipient_coins', 0)
        trade.status = TradeStatus(data.get('status', 'pending'))
        trade.created_timestamp = data.get('created_timestamp', time.time())
        trade.completed_timestamp = data.get('completed_timestamp')
        trade.expiry_duration = data.get('expiry_duration', 3600.0)
        trade.message = data.get('message', '')
        return trade


class TradingSystem:
    """
    Manages trading between pets.

    Features:
    - Create trade offers
    - Accept/decline trades
    - Trade history
    - Fair trade validation
    - Automatic expiry
    - Trade statistics
    """

    def __init__(self):
        """Initialize trading system."""
        # Active trades
        self.pending_trades: Dict[str, TradeOffer] = {}
        self.trade_history: List[TradeOffer] = []

        # Settings
        self.enable_fairness_check = True
        self.fairness_tolerance = 0.3  # 30% value difference allowed
        self.require_mutual_items = False  # Both must offer something

        # Statistics
        self.total_trades_proposed = 0
        self.total_trades_completed = 0
        self.total_trades_declined = 0
        self.total_trades_cancelled = 0

        # Trade counter for unique IDs
        self._trade_counter = 0

    def create_trade(self, proposer_id: str, recipient_id: str,
                     proposer_items: Optional[Dict[str, int]] = None,
                     proposer_coins: int = 0,
                     recipient_items: Optional[Dict[str, int]] = None,
                     recipient_coins: int = 0,
                     message: str = "") -> Optional[TradeOffer]:
        """
        Create a new trade offer.

        Args:
            proposer_id: Pet proposing the trade
            recipient_id: Pet receiving the offer
            proposer_items: Items offered by proposer
            proposer_coins: Coins offered by proposer
            recipient_items: Items requested from recipient
            recipient_coins: Coins requested from recipient
            message: Optional trade message

        Returns:
            TradeOffer if successful, None otherwise
        """
        # Validate
        if proposer_id == recipient_id:
            return None

        # Generate trade ID
        self._trade_counter += 1
        trade_id = f"trade_{self._trade_counter}_{int(time.time())}"

        # Create trade offer
        trade = TradeOffer(trade_id, proposer_id, recipient_id)

        # Add items
        if proposer_items:
            for item_id, quantity in proposer_items.items():
                trade.add_proposer_item(item_id, quantity)

        if proposer_coins > 0:
            trade.add_proposer_coins(proposer_coins)

        if recipient_items:
            for item_id, quantity in recipient_items.items():
                trade.add_recipient_item(item_id, quantity)

        if recipient_coins > 0:
            trade.add_recipient_coins(recipient_coins)

        trade.message = message

        # Validate trade requirements
        if self.require_mutual_items:
            proposer_offers = len(trade.proposer_items) + (1 if trade.proposer_coins > 0 else 0)
            recipient_offers = len(trade.recipient_items) + (1 if trade.recipient_coins > 0 else 0)
            if proposer_offers == 0 or recipient_offers == 0:
                return None

        # Check fairness if enabled
        if self.enable_fairness_check:
            if not trade.is_fair_trade(self.fairness_tolerance):
                # Trade is too unfair
                return None

        # Store trade
        self.pending_trades[trade_id] = trade
        self.total_trades_proposed += 1

        return trade

    def accept_trade(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """
        Accept a trade offer.

        Args:
            trade_id: Trade to accept

        Returns:
            Trade result or None
        """
        trade = self.pending_trades.get(trade_id)
        if not trade:
            # Try to find in history
            return None

        if trade.status != TradeStatus.PENDING:
            return None

        # Check expiry
        if trade.is_expired():
            trade.status = TradeStatus.EXPIRED
            self._move_to_history(trade_id)
            return None

        # Accept trade
        trade.status = TradeStatus.ACCEPTED
        trade.completed_timestamp = time.time()

        self.total_trades_completed += 1

        # Move to history
        self._move_to_history(trade_id)

        # Return trade details for execution
        return {
            'success': True,
            'trade_id': trade_id,
            'proposer_id': trade.proposer_id,
            'recipient_id': trade.recipient_id,
            'proposer_gives': {
                'items': trade.proposer_items,
                'coins': trade.proposer_coins
            },
            'recipient_gives': {
                'items': trade.recipient_items,
                'coins': trade.recipient_coins
            },
            'proposer_receives': {
                'items': trade.recipient_items,
                'coins': trade.recipient_coins
            },
            'recipient_receives': {
                'items': trade.proposer_items,
                'coins': trade.proposer_coins
            }
        }

    def decline_trade(self, trade_id: str) -> bool:
        """
        Decline a trade offer.

        Args:
            trade_id: Trade to decline

        Returns:
            True if successful
        """
        trade = self.pending_trades.get(trade_id)
        if not trade or trade.status != TradeStatus.PENDING:
            return False

        trade.status = TradeStatus.DECLINED
        trade.completed_timestamp = time.time()

        self.total_trades_declined += 1

        # Move to history
        self._move_to_history(trade_id)

        return True

    def cancel_trade(self, trade_id: str, proposer_id: str) -> bool:
        """
        Cancel a trade (only proposer can cancel).

        Args:
            trade_id: Trade to cancel
            proposer_id: ID of proposer (for verification)

        Returns:
            True if successful
        """
        trade = self.pending_trades.get(trade_id)
        if not trade or trade.status != TradeStatus.PENDING:
            return False

        # Verify proposer
        if trade.proposer_id != proposer_id:
            return False

        trade.status = TradeStatus.CANCELLED
        trade.completed_timestamp = time.time()

        self.total_trades_cancelled += 1

        # Move to history
        self._move_to_history(trade_id)

        return True

    def _move_to_history(self, trade_id: str):
        """Move trade from pending to history."""
        trade = self.pending_trades.get(trade_id)
        if trade:
            self.trade_history.append(trade)
            del self.pending_trades[trade_id]

    def get_trade(self, trade_id: str) -> Optional[TradeOffer]:
        """Get trade by ID (pending or history)."""
        # Check pending first
        if trade_id in self.pending_trades:
            return self.pending_trades[trade_id]

        # Check history
        for trade in self.trade_history:
            if trade.trade_id == trade_id:
                return trade

        return None

    def get_pending_trades_for_pet(self, pet_id: str) -> List[TradeOffer]:
        """Get all pending trades for a pet (as proposer or recipient)."""
        trades = []
        for trade in self.pending_trades.values():
            if trade.proposer_id == pet_id or trade.recipient_id == pet_id:
                if not trade.is_expired():
                    trades.append(trade)
                else:
                    # Mark as expired
                    trade.status = TradeStatus.EXPIRED
                    self._move_to_history(trade.trade_id)

        return trades

    def get_incoming_trades(self, pet_id: str) -> List[TradeOffer]:
        """Get trades where pet is recipient."""
        return [
            trade for trade in self.get_pending_trades_for_pet(pet_id)
            if trade.recipient_id == pet_id
        ]

    def get_outgoing_trades(self, pet_id: str) -> List[TradeOffer]:
        """Get trades where pet is proposer."""
        return [
            trade for trade in self.get_pending_trades_for_pet(pet_id)
            if trade.proposer_id == pet_id
        ]

    def get_trade_history_for_pet(self, pet_id: str, limit: int = 20) -> List[TradeOffer]:
        """Get trade history for a pet."""
        trades = [
            trade for trade in self.trade_history
            if trade.proposer_id == pet_id or trade.recipient_id == pet_id
        ]
        # Most recent first
        trades.sort(key=lambda x: x.completed_timestamp or 0, reverse=True)
        return trades[:limit]

    def get_completed_trades(self) -> List[TradeOffer]:
        """Get all completed trades."""
        return [
            trade for trade in self.trade_history
            if trade.status == TradeStatus.ACCEPTED
        ]

    def cleanup_expired_trades(self):
        """Remove expired pending trades."""
        expired_ids = []
        for trade_id, trade in self.pending_trades.items():
            if trade.is_expired():
                trade.status = TradeStatus.EXPIRED
                expired_ids.append(trade_id)

        for trade_id in expired_ids:
            self._move_to_history(trade_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Get trading statistics."""
        return {
            'total_proposed': self.total_trades_proposed,
            'total_completed': self.total_trades_completed,
            'total_declined': self.total_trades_declined,
            'total_cancelled': self.total_trades_cancelled,
            'pending_trades': len(self.pending_trades),
            'trade_history_count': len(self.trade_history),
            'completion_rate': (
                (self.total_trades_completed / self.total_trades_proposed * 100)
                if self.total_trades_proposed > 0 else 0.0
            ),
            'decline_rate': (
                (self.total_trades_declined / self.total_trades_proposed * 100)
                if self.total_trades_proposed > 0 else 0.0
            )
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'pending_trades': {
                trade_id: trade.to_dict()
                for trade_id, trade in self.pending_trades.items()
            },
            'trade_history': [
                trade.to_dict() for trade in self.trade_history
            ],
            'enable_fairness_check': self.enable_fairness_check,
            'fairness_tolerance': self.fairness_tolerance,
            'require_mutual_items': self.require_mutual_items,
            'total_trades_proposed': self.total_trades_proposed,
            'total_trades_completed': self.total_trades_completed,
            'total_trades_declined': self.total_trades_declined,
            'total_trades_cancelled': self.total_trades_cancelled,
            'trade_counter': self._trade_counter
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradingSystem':
        """Deserialize from dictionary."""
        system = cls()

        # Restore pending trades
        pending_data = data.get('pending_trades', {})
        for trade_id, trade_data in pending_data.items():
            system.pending_trades[trade_id] = TradeOffer.from_dict(trade_data)

        # Restore trade history
        history_data = data.get('trade_history', [])
        for trade_data in history_data:
            system.trade_history.append(TradeOffer.from_dict(trade_data))

        system.enable_fairness_check = data.get('enable_fairness_check', True)
        system.fairness_tolerance = data.get('fairness_tolerance', 0.3)
        system.require_mutual_items = data.get('require_mutual_items', False)
        system.total_trades_proposed = data.get('total_trades_proposed', 0)
        system.total_trades_completed = data.get('total_trades_completed', 0)
        system.total_trades_declined = data.get('total_trades_declined', 0)
        system.total_trades_cancelled = data.get('total_trades_cancelled', 0)
        system._trade_counter = data.get('trade_counter', 0)

        return system
