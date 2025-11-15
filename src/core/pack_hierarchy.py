"""
Phase 9: Pack Hierarchy System

Manages dominance hierarchy among multiple pets.
"""
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class Rank(Enum):
    """Pack ranks."""
    ALPHA = "alpha"        # Highest rank
    BETA = "beta"          # Second in command
    MID_RANK = "mid_rank"  # Middle of pack
    OMEGA = "omega"        # Lowest rank
    LONE = "lone"          # Not in pack


class PackHierarchy:
    """
    Manages pack hierarchy and dominance relationships.

    Features:
    - Rank assignment based on multiple factors
    - Dominance challenges
    - Submission behaviors
    - Resource priority
    - Rank changes over time
    """

    def __init__(self):
        """Initialize pack hierarchy."""
        self.members = {}  # pet_id: member_data
        self.ranks = {}    # pet_id: Rank
        self.dominance_matrix = {}  # (pet1_id, pet2_id): dominance_score

        # Pack statistics
        self.total_challenges = 0
        self.successful_challenges = 0
        self.pack_stability = 1.0  # 0-1, higher = more stable

        # History
        self.hierarchy_changes = []
        self.challenge_history = []

    def add_member(self, pet_id: str, pet_data: Dict[str, Any]):
        """
        Add a new pet to the pack.

        Args:
            pet_id: Pet's unique ID
            pet_data: Pet data (age, size, personality, etc.)
        """
        if pet_id in self.members:
            return

        member = {
            'pet_id': pet_id,
            'joined_time': time.time(),
            'age_days': pet_data.get('age_days', 100),
            'size': pet_data.get('size', 'medium'),
            'confidence': pet_data.get('confidence', 0.5),
            'dominance_score': 0.0,
            'times_challenged': 0,
            'times_submitted': 0,
            'challenges_won': 0,
            'challenges_lost': 0
        }

        self.members[pet_id] = member

        # Calculate initial dominance score
        member['dominance_score'] = self._calculate_dominance_score(pet_id)

        # Assign initial rank
        self._recalculate_ranks()

    def remove_member(self, pet_id: str):
        """Remove a pet from the pack."""
        if pet_id in self.members:
            del self.members[pet_id]
        if pet_id in self.ranks:
            del self.ranks[pet_id]

        # Remove from dominance matrix
        keys_to_remove = [k for k in self.dominance_matrix.keys() if pet_id in k]
        for key in keys_to_remove:
            del self.dominance_matrix[key]

        # Recalculate ranks
        self._recalculate_ranks()

    def _calculate_dominance_score(self, pet_id: str) -> float:
        """
        Calculate dominance score for a pet (0-100).

        Factors:
        - Age (older = more dominant)
        - Size (larger = more dominant)
        - Confidence/personality
        - Win/loss record
        - Time in pack (seniority)
        """
        if pet_id not in self.members:
            return 0.0

        member = self.members[pet_id]
        score = 0.0

        # Age factor (max 25 points)
        age = member['age_days']
        if age < 30:  # Baby
            score += 5.0
        elif age < 180:  # Young
            score += 15.0
        else:  # Adult+
            score += 25.0

        # Size factor (max 20 points)
        size_scores = {'small': 10.0, 'medium': 15.0, 'large': 20.0}
        score += size_scores.get(member['size'], 15.0)

        # Confidence factor (max 25 points)
        score += member['confidence'] * 25.0

        # Win/loss record (max 20 points)
        total_challenges = member['challenges_won'] + member['challenges_lost']
        if total_challenges > 0:
            win_rate = member['challenges_won'] / total_challenges
            score += win_rate * 20.0
        else:
            score += 10.0  # Default middle score

        # Seniority (max 10 points)
        days_in_pack = (time.time() - member['joined_time']) / 86400.0
        seniority_score = min(10.0, days_in_pack * 0.5)
        score += seniority_score

        return min(100.0, score)

    def _recalculate_ranks(self):
        """Recalculate ranks for all pack members."""
        if not self.members:
            return

        # Sort members by dominance score
        sorted_members = sorted(
            self.members.items(),
            key=lambda x: x[1]['dominance_score'],
            reverse=True
        )

        pack_size = len(sorted_members)

        for i, (pet_id, member) in enumerate(sorted_members):
            if pack_size == 1:
                new_rank = Rank.ALPHA
            elif i == 0:
                new_rank = Rank.ALPHA
            elif i == 1:
                new_rank = Rank.BETA
            elif i == pack_size - 1:
                new_rank = Rank.OMEGA
            else:
                new_rank = Rank.MID_RANK

            old_rank = self.ranks.get(pet_id)

            # Record rank change
            if old_rank != new_rank:
                self.hierarchy_changes.append({
                    'timestamp': time.time(),
                    'pet_id': pet_id,
                    'old_rank': old_rank.value if old_rank else None,
                    'new_rank': new_rank.value
                })

            self.ranks[pet_id] = new_rank

    def challenge_dominance(self, challenger_id: str, target_id: str,
                          context: str = "general") -> Dict[str, Any]:
        """
        One pet challenges another for dominance.

        Args:
            challenger_id: ID of challenging pet
            target_id: ID of target pet
            context: Context of challenge (food, toy, attention, etc.)

        Returns:
            Challenge results
        """
        if challenger_id not in self.members or target_id not in self.members:
            return {'error': 'invalid_pets'}

        challenger = self.members[challenger_id]
        target = self.members[target_id]

        # Calculate challenge success probability
        challenger_score = challenger['dominance_score']
        target_score = target['dominance_score']

        # Base probability from dominance difference
        score_diff = challenger_score - target_score
        base_prob = 0.5 + (score_diff / 200.0)  # -100 to +100 diff = 0 to 1 prob

        # Context modifiers
        if context == "food":
            # Hungrier pets fight harder for food
            base_prob *= 1.1
        elif context == "toy":
            # Playful pets more likely to challenge for toys
            base_prob *= 1.0
        elif context == "attention":
            # More emotional context
            base_prob *= 1.2

        # Random factor
        base_prob += random.uniform(-0.1, 0.1)
        base_prob = max(0.0, min(1.0, base_prob))

        # Determine outcome
        challenger_wins = random.random() < base_prob

        # Record challenge
        self.total_challenges += 1
        challenger['times_challenged'] += 1
        target['times_challenged'] += 1

        if challenger_wins:
            challenger['challenges_won'] += 1
            target['challenges_lost'] += 1
            target['times_submitted'] += 1
            self.successful_challenges += 1
            outcome = "challenger_wins"

            # Boost challenger dominance
            challenger['dominance_score'] = min(100.0, challenger['dominance_score'] + 5.0)
            target['dominance_score'] = max(0.0, target['dominance_score'] - 3.0)
        else:
            challenger['challenges_lost'] += 1
            challenger['times_submitted'] += 1
            target['challenges_won'] += 1
            outcome = "target_wins"

            # Boost target dominance
            target['dominance_score'] = min(100.0, target['dominance_score'] + 3.0)
            challenger['dominance_score'] = max(0.0, challenger['dominance_score'] - 5.0)

        # Record in history
        challenge = {
            'timestamp': time.time(),
            'challenger_id': challenger_id,
            'target_id': target_id,
            'context': context,
            'outcome': outcome,
            'challenger_score_before': challenger_score,
            'target_score_before': target_score
        }
        self.challenge_history.append(challenge)

        # Update dominance matrix
        key = (challenger_id, target_id)
        if key not in self.dominance_matrix:
            self.dominance_matrix[key] = 0.0

        if challenger_wins:
            self.dominance_matrix[key] += 1.0
        else:
            self.dominance_matrix[key] -= 1.0

        # Recalculate ranks
        old_challenger_rank = self.ranks.get(challenger_id)
        old_target_rank = self.ranks.get(target_id)

        self._recalculate_ranks()

        new_challenger_rank = self.ranks.get(challenger_id)
        new_target_rank = self.ranks.get(target_id)

        # Update pack stability
        self._update_pack_stability()

        return {
            'outcome': outcome,
            'challenger_wins': challenger_wins,
            'challenger_rank_change': old_challenger_rank != new_challenger_rank,
            'target_rank_change': old_target_rank != new_target_rank,
            'challenger_old_rank': old_challenger_rank.value if old_challenger_rank else None,
            'challenger_new_rank': new_challenger_rank.value if new_challenger_rank else None,
            'target_old_rank': old_target_rank.value if old_target_rank else None,
            'target_new_rank': new_target_rank.value if new_target_rank else None,
            'probability': base_prob
        }

    def _update_pack_stability(self):
        """Update pack stability based on recent challenges."""
        if self.total_challenges == 0:
            self.pack_stability = 1.0
            return

        # Recent challenges decrease stability
        recent_challenges = [
            c for c in self.challenge_history
            if time.time() - c['timestamp'] < 86400  # Last 24 hours
        ]

        # Stability decreases with challenge frequency
        challenges_per_day = len(recent_challenges)
        if challenges_per_day == 0:
            self.pack_stability = min(1.0, self.pack_stability + 0.1)
        else:
            stability_loss = min(0.5, challenges_per_day * 0.1)
            self.pack_stability = max(0.0, 1.0 - stability_loss)

    def get_rank(self, pet_id: str) -> Optional[Rank]:
        """Get rank of a pet."""
        return self.ranks.get(pet_id)

    def is_dominant_over(self, pet1_id: str, pet2_id: str) -> bool:
        """Check if pet1 is dominant over pet2."""
        if pet1_id not in self.members or pet2_id not in self.members:
            return False

        score1 = self.members[pet1_id]['dominance_score']
        score2 = self.members[pet2_id]['dominance_score']

        return score1 > score2

    def get_resource_priority(self) -> List[str]:
        """
        Get list of pet IDs in order of resource priority (highest first).

        Returns:
            List of pet IDs ordered by rank
        """
        if not self.members:
            return []

        # Sort by dominance score
        sorted_pets = sorted(
            self.members.items(),
            key=lambda x: x[1]['dominance_score'],
            reverse=True
        )

        return [pet_id for pet_id, _ in sorted_pets]

    def should_submit(self, submitter_id: str, dominant_id: str) -> Tuple[bool, str]:
        """
        Determine if a pet should submit to another.

        Args:
            submitter_id: Pet considering submission
            dominant_id: Potentially dominant pet

        Returns:
            Tuple of (should_submit, reason)
        """
        if submitter_id not in self.members or dominant_id not in self.members:
            return False, "unknown_pet"

        submitter_score = self.members[submitter_id]['dominance_score']
        dominant_score = self.members[dominant_id]['dominance_score']

        score_diff = dominant_score - submitter_score

        if score_diff > 30:
            return True, "much_more_dominant"
        elif score_diff > 15:
            return True, "more_dominant"
        elif score_diff > 5:
            # Check history
            key = (submitter_id, dominant_id)
            if key in self.dominance_matrix and self.dominance_matrix[key] < -2:
                return True, "lost_before"

        return False, "not_dominant"

    def get_hierarchy_summary(self) -> List[Dict[str, Any]]:
        """Get summary of pack hierarchy."""
        summary = []

        for pet_id in self.get_resource_priority():
            member = self.members[pet_id]
            rank = self.ranks.get(pet_id)

            summary.append({
                'pet_id': pet_id,
                'rank': rank.value if rank else 'unknown',
                'dominance_score': member['dominance_score'],
                'challenges_won': member['challenges_won'],
                'challenges_lost': member['challenges_lost'],
                'win_rate': (
                    member['challenges_won'] /
                    max(1, member['challenges_won'] + member['challenges_lost'])
                )
            })

        return summary

    def get_status(self) -> Dict[str, Any]:
        """Get pack hierarchy status."""
        return {
            'pack_size': len(self.members),
            'pack_stability': self.pack_stability,
            'total_challenges': self.total_challenges,
            'successful_challenges': self.successful_challenges,
            'hierarchy_changes': len(self.hierarchy_changes),
            'alpha': self._get_pet_by_rank(Rank.ALPHA),
            'omega': self._get_pet_by_rank(Rank.OMEGA)
        }

    def _get_pet_by_rank(self, rank: Rank) -> Optional[str]:
        """Get pet ID by rank."""
        for pet_id, pet_rank in self.ranks.items():
            if pet_rank == rank:
                return pet_id
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        ranks_dict = {pet_id: rank.value for pet_id, rank in self.ranks.items()}

        return {
            'members': self.members.copy(),
            'ranks': ranks_dict,
            'dominance_matrix': {f"{k[0]}__SEP__{k[1]}": v for k, v in self.dominance_matrix.items()},
            'total_challenges': self.total_challenges,
            'successful_challenges': self.successful_challenges,
            'pack_stability': self.pack_stability,
            'hierarchy_changes': self.hierarchy_changes.copy(),
            'challenge_history': self.challenge_history.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PackHierarchy':
        """Deserialize from dictionary."""
        system = cls()
        system.members = data.get('members', {})

        # Restore ranks
        ranks_data = data.get('ranks', {})
        for pet_id, rank_str in ranks_data.items():
            system.ranks[pet_id] = Rank(rank_str)

        # Restore dominance matrix
        matrix_data = data.get('dominance_matrix', {})
        for key_str, value in matrix_data.items():
            pet1, pet2 = key_str.split('__SEP__')
            system.dominance_matrix[(pet1, pet2)] = value

        system.total_challenges = data.get('total_challenges', 0)
        system.successful_challenges = data.get('successful_challenges', 0)
        system.pack_stability = data.get('pack_stability', 1.0)
        system.hierarchy_changes = data.get('hierarchy_changes', [])
        system.challenge_history = data.get('challenge_history', [])

        return system
