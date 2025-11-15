"""
Phase 13: Currency System

Manages coins, transactions, and wallet for the pet economy.
"""
import time
from typing import Dict, Any, List, Optional
from enum import Enum


class TransactionType(Enum):
    """Types of transactions."""
    EARNED_GAME = "earned_game"          # From mini-games
    EARNED_ACTIVITY = "earned_activity"  # From activities
    EARNED_ACHIEVEMENT = "earned_achievement"  # From achievements
    EARNED_DAILY = "earned_daily"        # Daily allowance
    EARNED_GIFT = "earned_gift"          # Gift from user
    SPENT_SHOP = "spent_shop"            # Shop purchase
    SPENT_TRADE = "spent_trade"          # Trading
    SPENT_SERVICE = "spent_service"      # Services (vet, grooming)
    REFUND = "refund"                    # Refund from return


class Transaction:
    """Represents a currency transaction."""

    def __init__(self, transaction_id: str, transaction_type: TransactionType,
                 amount: int, description: str = ""):
        """
        Initialize transaction.

        Args:
            transaction_id: Unique transaction ID
            transaction_type: Type of transaction
            amount: Amount (positive for income, negative for spending)
            description: Transaction description
        """
        self.transaction_id = transaction_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description
        self.timestamp = time.time()
        self.balance_after: int = 0  # Set when transaction is processed

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'transaction_id': self.transaction_id,
            'transaction_type': self.transaction_type.value,
            'amount': self.amount,
            'description': self.description,
            'timestamp': self.timestamp,
            'balance_after': self.balance_after
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Deserialize from dictionary."""
        transaction = cls(
            transaction_id=data['transaction_id'],
            transaction_type=TransactionType(data['transaction_type']),
            amount=data['amount'],
            description=data.get('description', '')
        )
        transaction.timestamp = data['timestamp']
        transaction.balance_after = data['balance_after']
        return transaction


class CurrencySystem:
    """
    Manages currency (coins) and transactions.

    Features:
    - Track coin balance
    - Record all transactions
    - Daily allowance
    - Spending limits for kids
    - Transaction history
    """

    def __init__(self, starting_balance: int = 100):
        """
        Initialize currency system.

        Args:
            starting_balance: Starting coin balance
        """
        self.balance = starting_balance
        self.transactions: List[Transaction] = []

        # Limits and settings
        self.daily_allowance = 10
        self.daily_allowance_enabled = True
        self.last_allowance_date: Optional[str] = None
        self.max_balance = 99999
        self.spending_limit_enabled = False
        self.daily_spending_limit = 100
        self.spending_today = 0
        self.last_spending_reset_date: Optional[str] = None

        # Statistics
        self.total_earned = starting_balance
        self.total_spent = 0
        self.total_transactions = 0
        self.earnings_by_type: Dict[str, int] = {}
        self.spending_by_type: Dict[str, int] = {}

    def add_coins(self, amount: int, transaction_type: TransactionType,
                  description: str = "") -> bool:
        """
        Add coins to balance.

        Args:
            amount: Amount to add
            transaction_type: Type of transaction
            description: Transaction description

        Returns:
            True if successful
        """
        if amount <= 0:
            return False

        # Check max balance
        if self.balance + amount > self.max_balance:
            amount = self.max_balance - self.balance

        # Create transaction
        transaction_id = f"txn_{int(time.time() * 1000)}"
        transaction = Transaction(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description
        )

        # Process transaction
        self.balance += amount
        transaction.balance_after = self.balance

        # Record transaction
        self.transactions.append(transaction)
        self.total_earned += amount
        self.total_transactions += 1

        # Track by type
        type_key = transaction_type.value
        if type_key not in self.earnings_by_type:
            self.earnings_by_type[type_key] = 0
        self.earnings_by_type[type_key] += amount

        return True

    def spend_coins(self, amount: int, transaction_type: TransactionType,
                   description: str = "") -> bool:
        """
        Spend coins from balance.

        Args:
            amount: Amount to spend
            transaction_type: Type of transaction
            description: Transaction description

        Returns:
            True if successful
        """
        if amount <= 0:
            return False

        # Check balance
        if self.balance < amount:
            return False

        # Check spending limit
        if self.spending_limit_enabled:
            self._check_spending_reset()
            if self.spending_today + amount > self.daily_spending_limit:
                return False

        # Create transaction
        transaction_id = f"txn_{int(time.time() * 1000)}"
        transaction = Transaction(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            amount=-amount,  # Negative for spending
            description=description
        )

        # Process transaction
        self.balance -= amount
        transaction.balance_after = self.balance

        # Record transaction
        self.transactions.append(transaction)
        self.total_spent += amount
        self.total_transactions += 1
        self.spending_today += amount

        # Track by type
        type_key = transaction_type.value
        if type_key not in self.spending_by_type:
            self.spending_by_type[type_key] = 0
        self.spending_by_type[type_key] += amount

        return True

    def can_afford(self, amount: int) -> bool:
        """
        Check if can afford an amount.

        Args:
            amount: Amount to check

        Returns:
            True if can afford
        """
        if amount <= 0:
            return False

        # Check balance
        if self.balance < amount:
            return False

        # Check spending limit
        if self.spending_limit_enabled:
            self._check_spending_reset()
            if self.spending_today + amount > self.daily_spending_limit:
                return False

        return True

    def claim_daily_allowance(self) -> Optional[int]:
        """
        Claim daily allowance if available.

        Returns:
            Amount claimed or None
        """
        if not self.daily_allowance_enabled:
            return None

        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        # Check if already claimed today
        if self.last_allowance_date == today:
            return None

        # Claim allowance
        self.add_coins(
            self.daily_allowance,
            TransactionType.EARNED_DAILY,
            "Daily allowance"
        )

        self.last_allowance_date = today
        return self.daily_allowance

    def _check_spending_reset(self):
        """Reset daily spending counter if new day."""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        if self.last_spending_reset_date != today:
            self.spending_today = 0
            self.last_spending_reset_date = today

    def get_recent_transactions(self, count: int = 10) -> List[Transaction]:
        """Get recent transactions."""
        return self.transactions[-count:]

    def get_transactions_by_type(self, transaction_type: TransactionType) -> List[Transaction]:
        """Get all transactions of a specific type."""
        return [t for t in self.transactions if t.transaction_type == transaction_type]

    def get_earnings_summary(self) -> Dict[str, int]:
        """Get summary of earnings by type."""
        return self.earnings_by_type.copy()

    def get_spending_summary(self) -> Dict[str, int]:
        """Get summary of spending by type."""
        return self.spending_by_type.copy()

    def get_net_worth(self) -> Dict[str, Any]:
        """Get net worth statistics."""
        return {
            'current_balance': self.balance,
            'total_earned': self.total_earned,
            'total_spent': self.total_spent,
            'net_savings': self.total_earned - self.total_spent,
            'savings_rate': (
                ((self.total_earned - self.total_spent) / self.total_earned * 100)
                if self.total_earned > 0 else 0.0
            )
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get currency statistics."""
        return {
            'balance': self.balance,
            'total_earned': self.total_earned,
            'total_spent': self.total_spent,
            'total_transactions': self.total_transactions,
            'daily_allowance': self.daily_allowance,
            'spending_today': self.spending_today,
            'daily_spending_limit': self.daily_spending_limit,
            'can_claim_allowance': (
                self.last_allowance_date != time.strftime("%Y-%m-%d")
                if self.daily_allowance_enabled else False
            ),
            'earnings_by_type': self.earnings_by_type,
            'spending_by_type': self.spending_by_type
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'balance': self.balance,
            'transactions': [t.to_dict() for t in self.transactions],
            'daily_allowance': self.daily_allowance,
            'daily_allowance_enabled': self.daily_allowance_enabled,
            'last_allowance_date': self.last_allowance_date,
            'max_balance': self.max_balance,
            'spending_limit_enabled': self.spending_limit_enabled,
            'daily_spending_limit': self.daily_spending_limit,
            'spending_today': self.spending_today,
            'last_spending_reset_date': self.last_spending_reset_date,
            'total_earned': self.total_earned,
            'total_spent': self.total_spent,
            'total_transactions': self.total_transactions,
            'earnings_by_type': self.earnings_by_type,
            'spending_by_type': self.spending_by_type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CurrencySystem':
        """Deserialize from dictionary."""
        system = cls(starting_balance=0)  # Will be overwritten
        system.balance = data.get('balance', 100)

        # Restore transactions
        transactions_data = data.get('transactions', [])
        for txn_data in transactions_data:
            transaction = Transaction.from_dict(txn_data)
            system.transactions.append(transaction)

        system.daily_allowance = data.get('daily_allowance', 10)
        system.daily_allowance_enabled = data.get('daily_allowance_enabled', True)
        system.last_allowance_date = data.get('last_allowance_date')
        system.max_balance = data.get('max_balance', 99999)
        system.spending_limit_enabled = data.get('spending_limit_enabled', False)
        system.daily_spending_limit = data.get('daily_spending_limit', 100)
        system.spending_today = data.get('spending_today', 0)
        system.last_spending_reset_date = data.get('last_spending_reset_date')
        system.total_earned = data.get('total_earned', 100)
        system.total_spent = data.get('total_spent', 0)
        system.total_transactions = data.get('total_transactions', 0)
        system.earnings_by_type = data.get('earnings_by_type', {})
        system.spending_by_type = data.get('spending_by_type', {})

        return system
