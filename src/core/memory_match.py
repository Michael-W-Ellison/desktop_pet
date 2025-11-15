"""
Phase 12: Memory Match Game

A memory matching game played with your pet.
"""
import random
import time
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from .game_base import MiniGame, GameDifficulty, GameState


class CardSymbol(Enum):
    """Symbols on cards."""
    HEART = "heart"
    STAR = "star"
    BONE = "bone"
    PAW = "paw"
    FISH = "fish"
    BALL = "ball"
    FLOWER = "flower"
    MOON = "moon"
    SUN = "sun"
    LEAF = "leaf"


class MemoryCard:
    """Represents a memory card."""

    def __init__(self, card_id: int, symbol: CardSymbol):
        """
        Initialize memory card.

        Args:
            card_id: Unique card ID
            symbol: Card symbol
        """
        self.card_id = card_id
        self.symbol = symbol
        self.revealed = False
        self.matched = False


class MemoryMatch(MiniGame):
    """
    Memory matching mini-game.

    Player and pet take turns flipping cards to find matching pairs.
    """

    def __init__(self):
        """Initialize memory match game."""
        super().__init__(
            game_name="Memory Match",
            description="Find matching pairs with your pet!"
        )

        # Game settings
        self.grid_size = 4  # 4x4 grid = 16 cards
        self.time_limit = 120.0  # 2 minutes

        # Game state
        self.cards: List[MemoryCard] = []
        self.revealed_cards: List[MemoryCard] = []
        self.matches_found = 0
        self.target_matches = 8  # 16 cards = 8 pairs
        self.moves_made = 0
        self.mistakes = 0

        # Pet help
        self.pet_intelligence: float = 0.5
        self.pet_hints_given = 0
        self.max_hints = 3

    def start_game(self, difficulty: GameDifficulty = GameDifficulty.MEDIUM,
                   pet_intelligence: float = 0.5):
        """
        Start the memory match game.

        Args:
            difficulty: Game difficulty
            pet_intelligence: Pet's intelligence stat (0-1)
        """
        super().start_game(difficulty)

        # Set difficulty parameters
        difficulty_settings = {
            GameDifficulty.EASY: {'size': 3, 'time': 180.0, 'hints': 5},
            GameDifficulty.MEDIUM: {'size': 4, 'time': 120.0, 'hints': 3},
            GameDifficulty.HARD: {'size': 5, 'time': 90.0, 'hints': 2},
            GameDifficulty.EXPERT: {'size': 6, 'time': 60.0, 'hints': 1}
        }

        settings = difficulty_settings.get(difficulty, difficulty_settings[GameDifficulty.MEDIUM])
        self.grid_size = settings['size']
        self.time_limit = settings['time']
        self.max_hints = settings['hints']

        # Reset game state
        self.matches_found = 0
        self.moves_made = 0
        self.mistakes = 0
        self.pet_hints_given = 0
        self.revealed_cards = []

        # Set pet stats
        self.pet_intelligence = pet_intelligence

        # Create cards
        self._create_cards()

    def _create_cards(self):
        """Create and shuffle cards."""
        total_cards = self.grid_size * self.grid_size
        num_pairs = total_cards // 2
        self.target_matches = num_pairs

        # Select symbols
        all_symbols = list(CardSymbol)
        selected_symbols = random.sample(all_symbols, num_pairs)

        # Create pairs
        cards = []
        card_id = 0

        for symbol in selected_symbols:
            # Create two cards for each symbol
            cards.append(MemoryCard(card_id, symbol))
            card_id += 1
            cards.append(MemoryCard(card_id, symbol))
            card_id += 1

        # Shuffle
        random.shuffle(cards)

        self.cards = cards

    def flip_card(self, card_id: int) -> Dict[str, Any]:
        """
        Flip a card.

        Args:
            card_id: ID of card to flip

        Returns:
            Result of flip
        """
        if self.state != GameState.PLAYING:
            return {'error': 'game_not_active'}

        # Find card
        card = next((c for c in self.cards if c.card_id == card_id), None)
        if not card:
            return {'error': 'invalid_card'}

        if card.matched or card.revealed:
            return {'error': 'card_already_revealed'}

        # Flip card
        card.revealed = True
        self.revealed_cards.append(card)

        # Check if two cards are revealed
        if len(self.revealed_cards) == 2:
            match_result = self._check_match()
            self.moves_made += 1

            # Hide cards after checking
            for c in self.revealed_cards:
                if not c.matched:
                    c.revealed = False
            self.revealed_cards = []

            # Check for win
            if self.matches_found >= self.target_matches:
                self.end_game(success=True, reason="all_matched")

            return match_result

        return {
            'flipped': True,
            'card_id': card_id,
            'symbol': card.symbol.value,
            'waiting_for_second': True
        }

    def _check_match(self) -> Dict[str, Any]:
        """Check if revealed cards match."""
        card1, card2 = self.revealed_cards

        if card1.symbol == card2.symbol:
            # Match!
            card1.matched = True
            card2.matched = True
            self.matches_found += 1

            # Points for match
            points = 20

            # Speed bonus (fewer moves = more points)
            if self.moves_made < self.target_matches:
                points += 10

            self.add_score(points)

            return {
                'match': True,
                'symbol': card1.symbol.value,
                'points': points,
                'matches_found': self.matches_found,
                'target': self.target_matches
            }
        else:
            # No match
            self.mistakes += 1
            return {
                'match': False,
                'card1_symbol': card1.symbol.value,
                'card2_symbol': card2.symbol.value
            }

    def get_hint(self) -> Optional[Dict[str, Any]]:
        """
        Get a hint from the pet.

        Returns:
            Hint information or None
        """
        if self.pet_hints_given >= self.max_hints:
            return None

        # Pet finds a matching pair that hasn't been found
        unmatched_cards = [c for c in self.cards if not c.matched]

        # Find a pair
        for i, card1 in enumerate(unmatched_cards):
            for card2 in unmatched_cards[i+1:]:
                if card1.symbol == card2.symbol:
                    self.pet_hints_given += 1

                    # Hint quality depends on intelligence
                    if random.random() < self.pet_intelligence:
                        # Good hint - show both cards
                        return {
                            'hint_type': 'full',
                            'card1_id': card1.card_id,
                            'card2_id': card2.card_id,
                            'symbol': card1.symbol.value
                        }
                    else:
                        # Partial hint - show one card
                        return {
                            'hint_type': 'partial',
                            'card_id': card1.card_id,
                            'symbol': card1.symbol.value
                        }

        return None

    def get_progress(self) -> Dict[str, Any]:
        """Get current game progress."""
        return {
            'matches_found': self.matches_found,
            'target_matches': self.target_matches,
            'moves_made': self.moves_made,
            'mistakes': self.mistakes,
            'hints_used': self.pet_hints_given,
            'hints_remaining': self.max_hints - self.pet_hints_given,
            'time_remaining': max(0.0, self.time_limit - self.elapsed_time),
            'score': self.score,
            'accuracy': (
                ((self.matches_found * 2) / self.moves_made * 100)
                if self.moves_made > 0 else 100.0
            )
        }

    def end_game(self, success: bool, reason: str = "completed"):
        """End the memory match game."""
        result = super().end_game(success, reason)

        # Perfect game (no mistakes)
        if success and self.mistakes == 0:
            result.perfect_score = True
            self.perfect_games += 1
            result.experience_earned += 15

        # Efficiency bonus (low moves)
        if success and self.moves_made <= self.target_matches:
            result.experience_earned += 10

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryMatch':
        """Deserialize from dictionary."""
        game = cls()
        game.difficulty = GameDifficulty(data.get('difficulty', 'medium'))
        game.high_score = data.get('high_score', 0)
        game.total_plays = data.get('total_plays', 0)
        game.total_wins = data.get('total_wins', 0)
        game.total_losses = data.get('total_losses', 0)
        game.perfect_games = data.get('perfect_games', 0)
        game.total_score_earned = data.get('total_score_earned', 0)
        return game
