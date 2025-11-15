"""
Phase 9: Peer Teaching System

Allows trained pets to teach tricks to untrained pets through social learning.
"""
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


class PeerTeachingSystem:
    """
    Manages peer-to-peer teaching and social learning.

    Features:
    - Trained pets can teach tricks to others
    - Teaching success based on friendship and hierarchy
    - Faster learning from peers than solo
    - Teaching builds bonds
    """

    def __init__(self, pet_id: str):
        """
        Initialize peer teaching system.

        Args:
            pet_id: This pet's ID
        """
        self.pet_id = pet_id

        # Teaching history
        self.tricks_taught = {}  # trick_name: times_taught
        self.tricks_learned_from_peers = {}  # trick_name: teacher_id
        self.total_teaching_sessions = 0
        self.successful_teachings = 0

        # Learning from peers
        self.total_learning_sessions = 0
        self.successful_learnings = 0

        # Teaching ability (improves with experience)
        self.teaching_skill = 0.0  # 0-1, improves with practice

        # Observation learning (learning by watching)
        self.observed_tricks = {}  # trick_name: observation_count

    def can_teach_trick(self, trick_name: str, proficiency: float) -> bool:
        """
        Check if can teach a trick.

        Args:
            trick_name: Name of trick
            proficiency: This pet's proficiency (0-1)

        Returns:
            True if can teach
        """
        # Must have mastered the trick (>= 0.8 proficiency)
        return proficiency >= 0.8

    def teach_trick(self, student_id: str, trick_name: str,
                    teacher_proficiency: float,
                    student_proficiency: float,
                    friendship: float = 50.0,
                    teacher_rank_higher: bool = False) -> Dict[str, Any]:
        """
        Teach a trick to another pet.

        Args:
            student_id: ID of student pet
            trick_name: Trick being taught
            teacher_proficiency: Teacher's proficiency (0-1)
            student_proficiency: Student's current proficiency (0-1)
            friendship: Friendship level between pets (0-100)
            teacher_rank_higher: Whether teacher outranks student

        Returns:
            Teaching session results
        """
        self.total_teaching_sessions += 1

        # Check if can teach
        if not self.can_teach_trick(trick_name, teacher_proficiency):
            return {
                'success': False,
                'reason': 'teacher_not_proficient',
                'proficiency_gain': 0.0
            }

        # Calculate teaching success probability
        base_success = 0.6  # 60% base chance

        # Teacher's skill matters
        base_success += self.teaching_skill * 0.2

        # Friendship helps
        friendship_bonus = (friendship / 100.0) * 0.2
        base_success += friendship_bonus

        # Hierarchy matters (students learn better from higher-ranked teachers)
        if teacher_rank_higher:
            base_success += 0.1

        # Student's current proficiency affects learning
        # Easier to learn from scratch, harder to improve when already good
        if student_proficiency < 0.3:
            base_success += 0.1  # Easier for beginners
        elif student_proficiency > 0.7:
            base_success -= 0.1  # Harder when already skilled

        # Clamp probability
        base_success = max(0.0, min(1.0, base_success))

        # Determine success
        teaching_successful = random.random() < base_success

        if teaching_successful:
            self.successful_teachings += 1

            # Calculate proficiency gain (faster than solo learning)
            base_gain = 0.15  # 15% gain (vs ~8% solo)

            # Teacher's proficiency affects how much can be learned
            gain_modifier = (teacher_proficiency - 0.8) / 0.2  # 0-1 for proficiency 0.8-1.0
            proficiency_gain = base_gain * (1.0 + gain_modifier * 0.5)

            # Friendship bonus
            proficiency_gain *= (1.0 + friendship_bonus)

            # Record teaching
            if trick_name not in self.tricks_taught:
                self.tricks_taught[trick_name] = 0
            self.tricks_taught[trick_name] += 1

            # Improve teaching skill
            self.teaching_skill = min(1.0, self.teaching_skill + 0.02)

            return {
                'success': True,
                'proficiency_gain': proficiency_gain,
                'teaching_quality': base_success,
                'friendship_bonus': friendship_bonus,
                'teacher_skill_improved': True,
                'bonding_gain': 3.0  # Teaching builds bond
            }
        else:
            return {
                'success': False,
                'reason': 'student_distracted',
                'proficiency_gain': 0.0,
                'bonding_gain': 0.5  # Still builds a little bond
            }

    def learn_from_peer(self, teacher_id: str, trick_name: str,
                       current_proficiency: float,
                       teaching_quality: float) -> Dict[str, Any]:
        """
        Learn a trick from another pet.

        Args:
            teacher_id: ID of teaching pet
            trick_name: Trick being learned
            current_proficiency: Current proficiency (0-1)
            teaching_quality: Quality of teaching (0-1)

        Returns:
            Learning results
        """
        self.total_learning_sessions += 1

        # Higher teaching quality = more likely to learn
        learns = random.random() < teaching_quality

        if learns:
            self.successful_learnings += 1

            # Record who taught this trick
            if trick_name not in self.tricks_learned_from_peers:
                self.tricks_learned_from_peers[trick_name] = teacher_id

            return {
                'learned': True,
                'teacher_id': teacher_id,
                'trick': trick_name
            }
        else:
            return {
                'learned': False,
                'reason': 'failed_to_understand'
            }

    def observe_trick(self, trick_name: str, performer_proficiency: float) -> Dict[str, Any]:
        """
        Observe another pet performing a trick (passive learning).

        Args:
            trick_name: Trick being observed
            performer_proficiency: How well they performed (0-1)

        Returns:
            Observation results
        """
        if trick_name not in self.observed_tricks:
            self.observed_tricks[trick_name] = 0

        self.observed_tricks[trick_name] += 1

        # Small chance to learn by observation (5% per observation)
        # More observations = higher chance
        observation_count = self.observed_tricks[trick_name]
        learn_chance = min(0.3, observation_count * 0.05)

        # Better performance = easier to learn from
        learn_chance *= performer_proficiency

        if random.random() < learn_chance:
            # Learned through observation!
            proficiency_gain = 0.05  # Small gain, but free
            return {
                'observed': True,
                'learned_by_observation': True,
                'proficiency_gain': proficiency_gain,
                'observations_needed': observation_count
            }
        else:
            return {
                'observed': True,
                'learned_by_observation': False,
                'total_observations': observation_count
            }

    def get_teaching_stats(self) -> Dict[str, Any]:
        """Get teaching statistics."""
        return {
            'tricks_taught_count': len(self.tricks_taught),
            'tricks_taught': list(self.tricks_taught.keys()),
            'total_teaching_sessions': self.total_teaching_sessions,
            'successful_teachings': self.successful_teachings,
            'teaching_success_rate': (
                self.successful_teachings / max(1, self.total_teaching_sessions)
            ),
            'teaching_skill': self.teaching_skill,
            'tricks_learned_from_peers_count': len(self.tricks_learned_from_peers),
            'total_learning_sessions': self.total_learning_sessions,
            'successful_learnings': self.successful_learnings,
            'learning_success_rate': (
                self.successful_learnings / max(1, self.total_learning_sessions)
            )
        }

    def get_tricks_can_teach(self, proficiencies: Dict[str, float]) -> List[str]:
        """
        Get list of tricks this pet can teach.

        Args:
            proficiencies: Dict of trick_name: proficiency

        Returns:
            List of teachable tricks
        """
        teachable = []
        for trick, prof in proficiencies.items():
            if self.can_teach_trick(trick, prof):
                teachable.append(trick)
        return teachable

    def recommend_teacher_for_trick(self, trick_name: str,
                                    available_teachers: List[Dict[str, Any]]) -> Optional[str]:
        """
        Recommend best teacher for a trick from available teachers.

        Args:
            trick_name: Trick to learn
            available_teachers: List of dicts with teacher info

        Returns:
            Best teacher's ID or None
        """
        if not available_teachers:
            return None

        # Score each teacher
        teacher_scores = []
        for teacher in available_teachers:
            score = 0.0

            # Proficiency (most important)
            proficiency = teacher.get('proficiency', 0.0)
            score += proficiency * 100

            # Teaching skill
            teaching_skill = teacher.get('teaching_skill', 0.0)
            score += teaching_skill * 30

            # Friendship
            friendship = teacher.get('friendship', 50.0)
            score += friendship * 0.2

            # Rank (higher rank = better teacher)
            if teacher.get('rank_higher', False):
                score += 20

            teacher_scores.append((teacher['pet_id'], score))

        # Return highest scoring teacher
        if teacher_scores:
            teacher_scores.sort(key=lambda x: x[1], reverse=True)
            return teacher_scores[0][0]

        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'pet_id': self.pet_id,
            'tricks_taught': self.tricks_taught.copy(),
            'tricks_learned_from_peers': self.tricks_learned_from_peers.copy(),
            'total_teaching_sessions': self.total_teaching_sessions,
            'successful_teachings': self.successful_teachings,
            'total_learning_sessions': self.total_learning_sessions,
            'successful_learnings': self.successful_learnings,
            'teaching_skill': self.teaching_skill,
            'observed_tricks': self.observed_tricks.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PeerTeachingSystem':
        """Deserialize from dictionary."""
        system = cls(pet_id=data.get('pet_id', 'unknown'))
        system.tricks_taught = data.get('tricks_taught', {})
        system.tricks_learned_from_peers = data.get('tricks_learned_from_peers', {})
        system.total_teaching_sessions = data.get('total_teaching_sessions', 0)
        system.successful_teachings = data.get('successful_teachings', 0)
        system.total_learning_sessions = data.get('total_learning_sessions', 0)
        system.successful_learnings = data.get('successful_learnings', 0)
        system.teaching_skill = data.get('teaching_skill', 0.0)
        system.observed_tricks = data.get('observed_tricks', {})
        return system
