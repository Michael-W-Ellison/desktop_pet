"""
Phase 8: Breeding and Genetics System

Manages pet breeding, pregnancy, and genetic inheritance.
"""
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class GeneticTrait(Enum):
    """Genetic traits that can be inherited."""
    # Physical
    SIZE = "size"
    COLOR = "color"
    PATTERN = "pattern"
    EYE_COLOR = "eye_color"

    # Personality
    ENERGY_LEVEL = "energy_level"
    FRIENDLINESS = "friendliness"
    INTELLIGENCE = "intelligence"
    PLAYFULNESS = "playfulness"

    # Special
    LIFESPAN = "lifespan"
    HEALTH = "health"
    LEARNING_SPEED = "learning_speed"


class PregnancyStage(Enum):
    """Stages of pregnancy."""
    NOT_PREGNANT = "not_pregnant"
    EARLY = "early"        # 0-33%
    MID = "mid"            # 33-66%
    LATE = "late"          # 66-100%
    READY_TO_GIVE_BIRTH = "ready"


class BreedingSystem:
    """
    Manages breeding, pregnancy, and genetics.

    Features:
    - Mating compatibility
    - Pregnancy progression
    - Offspring generation
    - Genetic inheritance
    - Recessive/dominant traits
    """

    def __init__(self, creature_id: str, gender: str = None):
        """
        Initialize breeding system.

        Args:
            creature_id: Unique ID for this creature
            gender: 'male' or 'female' (random if not specified)
        """
        self.creature_id = creature_id
        self.gender = gender or random.choice(['male', 'female'])

        # Breeding readiness
        self.can_breed = False  # Becomes true at adult stage
        self.times_bred = 0
        self.offspring_count = 0

        # Pregnancy (for females)
        self.is_pregnant = False
        self.pregnancy_progress = 0.0  # 0-1
        self.pregnancy_duration_days = 7.0  # ~1 week
        self.pregnancy_start_time = None
        self.mate_id = None  # ID of mate
        self.mate_genetics = None  # Genetics from mate

        # Genetics
        self.genetics = self._initialize_genetics()

        # Breeding history
        self.breeding_history = []
        self.offspring_ids = []

    def _initialize_genetics(self) -> Dict[str, Any]:
        """
        Initialize random genetics.

        Returns:
            Dictionary of genetic traits
        """
        return {
            # Physical traits (dominant/recessive pairs)
            'size': {
                'dominant': random.choice(['small', 'medium', 'large']),
                'recessive': random.choice(['small', 'medium', 'large'])
            },
            'color': {
                'dominant': random.choice(['red', 'blue', 'green', 'yellow', 'purple', 'orange']),
                'recessive': random.choice(['red', 'blue', 'green', 'yellow', 'purple', 'orange'])
            },
            'pattern': {
                'dominant': random.choice(['solid', 'striped', 'spotted', 'mixed']),
                'recessive': random.choice(['solid', 'striped', 'spotted', 'mixed'])
            },
            'eye_color': {
                'dominant': random.choice(['brown', 'blue', 'green', 'amber']),
                'recessive': random.choice(['brown', 'blue', 'green', 'amber'])
            },

            # Personality traits (numerical values 0-100)
            'energy_level': random.uniform(40, 90),
            'friendliness': random.uniform(40, 90),
            'intelligence': random.uniform(40, 90),
            'playfulness': random.uniform(40, 90),

            # Special traits
            'lifespan_modifier': random.uniform(0.8, 1.2),  # Multiplier
            'health_bonus': random.uniform(-10, 10),
            'learning_speed_modifier': random.uniform(0.8, 1.2)
        }

    def attempt_breeding(self, partner: 'BreedingSystem', compatibility: float = 1.0) -> Dict[str, Any]:
        """
        Attempt to breed with another creature.

        Args:
            partner: Partner's breeding system
            compatibility: Compatibility factor (0-1)

        Returns:
            Breeding result dictionary
        """
        # Check if breeding is possible
        if not self.can_breed:
            return {'success': False, 'reason': 'not_ready_self'}

        if not partner.can_breed:
            return {'success': False, 'reason': 'not_ready_partner'}

        # Check gender compatibility
        if self.gender == partner.gender:
            return {'success': False, 'reason': 'same_gender'}

        # Female must not be pregnant
        female = self if self.gender == 'female' else partner
        male = partner if self.gender == 'female' else self

        if female.is_pregnant:
            return {'success': False, 'reason': 'already_pregnant'}

        # Calculate breeding success chance
        base_chance = 0.7  # 70% base chance
        success_chance = base_chance * compatibility

        if random.random() < success_chance:
            # Successful breeding
            female.become_pregnant(male.creature_id, male.genetics)
            male.times_bred += 1
            female.times_bred += 1

            # Record breeding
            breeding_event = {
                'timestamp': time.time(),
                'datetime': datetime.now().isoformat(),
                'partner_id': partner.creature_id,
                'success': True
            }
            self.breeding_history.append(breeding_event)
            partner.breeding_history.append(breeding_event.copy())

            return {
                'success': True,
                'pregnant_id': female.creature_id,
                'father_id': male.creature_id,
                'expected_birth_days': female.pregnancy_duration_days
            }
        else:
            return {'success': False, 'reason': 'breeding_failed'}

    def become_pregnant(self, mate_id: str, mate_genetics: Dict[str, Any]):
        """
        Become pregnant.

        Args:
            mate_id: ID of the mate
            mate_genetics: Genetic information from mate
        """
        if self.gender != 'female':
            return

        self.is_pregnant = True
        self.pregnancy_progress = 0.0
        self.pregnancy_start_time = time.time()
        self.mate_id = mate_id
        self.mate_genetics = mate_genetics

    def update_pregnancy(self, hours_elapsed: float):
        """
        Update pregnancy progress.

        Args:
            hours_elapsed: Hours since last update
        """
        if not self.is_pregnant:
            return

        # Progress pregnancy
        days_elapsed = hours_elapsed / 24.0
        progress_gain = days_elapsed / self.pregnancy_duration_days

        self.pregnancy_progress = min(1.0, self.pregnancy_progress + progress_gain)

    def get_pregnancy_stage(self) -> PregnancyStage:
        """Get current pregnancy stage."""
        if not self.is_pregnant:
            return PregnancyStage.NOT_PREGNANT

        if self.pregnancy_progress >= 1.0:
            return PregnancyStage.READY_TO_GIVE_BIRTH
        elif self.pregnancy_progress >= 0.66:
            return PregnancyStage.LATE
        elif self.pregnancy_progress >= 0.33:
            return PregnancyStage.MID
        else:
            return PregnancyStage.EARLY

    def give_birth(self, litter_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Give birth to offspring.

        Args:
            litter_size: Number of offspring (random if not specified)

        Returns:
            List of offspring genetic profiles
        """
        if not self.is_pregnant or self.pregnancy_progress < 1.0:
            return []

        # Determine litter size
        if litter_size is None:
            litter_size = random.randint(1, 3)  # 1-3 offspring

        # Generate offspring
        offspring = []
        for i in range(litter_size):
            offspring_genetics = self._combine_genetics(self.genetics, self.mate_genetics)
            offspring_id = f"{self.creature_id}_offspring_{self.offspring_count + i}"

            offspring.append({
                'id': offspring_id,
                'genetics': offspring_genetics,
                'mother_id': self.creature_id,
                'father_id': self.mate_id,
                'birth_time': time.time(),
                'birth_order': i + 1,
                'litter_size': litter_size
            })

            self.offspring_ids.append(offspring_id)

        # Update stats
        self.offspring_count += litter_size
        self.is_pregnant = False
        self.pregnancy_progress = 0.0
        self.mate_id = None
        self.mate_genetics = None

        return offspring

    def _combine_genetics(self, parent1_genetics: Dict[str, Any],
                         parent2_genetics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine genetics from two parents using Mendelian inheritance.

        Args:
            parent1_genetics: Genetics from parent 1
            parent2_genetics: Genetics from parent 2

        Returns:
            Offspring genetics
        """
        offspring = {}

        # Physical traits (dominant/recessive)
        for trait in ['size', 'color', 'pattern', 'eye_color']:
            if trait in parent1_genetics and trait in parent2_genetics:
                # Randomly inherit from each parent
                allele1 = random.choice([
                    parent1_genetics[trait]['dominant'],
                    parent1_genetics[trait]['recessive']
                ])
                allele2 = random.choice([
                    parent2_genetics[trait]['dominant'],
                    parent2_genetics[trait]['recessive']
                ])

                # Determine which is dominant (for display)
                # In real genetics this would be more complex
                if allele1 == allele2:
                    dominant = allele1
                    recessive = allele1
                else:
                    dominant = random.choice([allele1, allele2])
                    recessive = allele1 if dominant == allele2 else allele2

                offspring[trait] = {
                    'dominant': dominant,
                    'recessive': recessive
                }

        # Numerical traits (blend with variation)
        for trait in ['energy_level', 'friendliness', 'intelligence', 'playfulness']:
            if trait in parent1_genetics and trait in parent2_genetics:
                # Average of parents with some random variation
                average = (parent1_genetics[trait] + parent2_genetics[trait]) / 2.0
                variation = random.uniform(-10, 10)
                offspring[trait] = max(0, min(100, average + variation))

        # Special traits
        if 'lifespan_modifier' in parent1_genetics and 'lifespan_modifier' in parent2_genetics:
            offspring['lifespan_modifier'] = (
                parent1_genetics['lifespan_modifier'] +
                parent2_genetics['lifespan_modifier']
            ) / 2.0

        if 'health_bonus' in parent1_genetics and 'health_bonus' in parent2_genetics:
            offspring['health_bonus'] = (
                parent1_genetics['health_bonus'] +
                parent2_genetics['health_bonus']
            ) / 2.0

        if 'learning_speed_modifier' in parent1_genetics and 'learning_speed_modifier' in parent2_genetics:
            offspring['learning_speed_modifier'] = (
                parent1_genetics['learning_speed_modifier'] +
                parent2_genetics['learning_speed_modifier']
            ) / 2.0

        # Small chance of random mutation
        if random.random() < 0.1:  # 10% mutation chance
            offspring = self._apply_mutation(offspring)

        return offspring

    def _apply_mutation(self, genetics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a random mutation to genetics.

        Args:
            genetics: Genetics to mutate

        Returns:
            Mutated genetics
        """
        # Random mutation type
        mutation_types = ['color', 'pattern', 'trait_boost', 'trait_penalty']
        mutation = random.choice(mutation_types)

        if mutation == 'color':
            # New color mutation
            new_color = random.choice(['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'silver', 'gold'])
            genetics['color'] = {'dominant': new_color, 'recessive': new_color}

        elif mutation == 'pattern':
            # New pattern mutation
            new_pattern = random.choice(['solid', 'striped', 'spotted', 'mixed', 'swirled'])
            genetics['pattern'] = {'dominant': new_pattern, 'recessive': new_pattern}

        elif mutation == 'trait_boost':
            # Boost a random numerical trait
            trait = random.choice(['energy_level', 'friendliness', 'intelligence', 'playfulness'])
            if trait in genetics:
                genetics[trait] = min(100, genetics[trait] + random.uniform(5, 15))

        elif mutation == 'trait_penalty':
            # Penalty to a random numerical trait
            trait = random.choice(['energy_level', 'friendliness', 'intelligence', 'playfulness'])
            if trait in genetics:
                genetics[trait] = max(0, genetics[trait] - random.uniform(5, 15))

        return genetics

    def get_displayed_genetics(self) -> Dict[str, Any]:
        """
        Get genetics as they would be displayed (dominant traits shown).

        Returns:
            Dictionary of displayed traits
        """
        displayed = {}

        # Show dominant alleles for physical traits
        for trait in ['size', 'color', 'pattern', 'eye_color']:
            if trait in self.genetics:
                displayed[trait] = self.genetics[trait]['dominant']

        # Show numerical traits
        for trait in ['energy_level', 'friendliness', 'intelligence', 'playfulness']:
            if trait in self.genetics:
                displayed[trait] = self.genetics[trait]

        # Show special traits
        for trait in ['lifespan_modifier', 'health_bonus', 'learning_speed_modifier']:
            if trait in self.genetics:
                displayed[trait] = self.genetics[trait]

        return displayed

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive breeding status."""
        status = {
            'creature_id': self.creature_id,
            'gender': self.gender,
            'can_breed': self.can_breed,
            'times_bred': self.times_bred,
            'offspring_count': self.offspring_count,
            'offspring_ids': self.offspring_ids.copy(),
            'genetics': self.get_displayed_genetics()
        }

        if self.gender == 'female':
            status['is_pregnant'] = self.is_pregnant
            if self.is_pregnant:
                status['pregnancy_progress'] = self.pregnancy_progress
                status['pregnancy_stage'] = self.get_pregnancy_stage().value
                status['mate_id'] = self.mate_id
                days_until_birth = (1.0 - self.pregnancy_progress) * self.pregnancy_duration_days
                status['days_until_birth'] = days_until_birth

        return status

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'creature_id': self.creature_id,
            'gender': self.gender,
            'can_breed': self.can_breed,
            'times_bred': self.times_bred,
            'offspring_count': self.offspring_count,
            'is_pregnant': self.is_pregnant,
            'pregnancy_progress': self.pregnancy_progress,
            'pregnancy_duration_days': self.pregnancy_duration_days,
            'pregnancy_start_time': self.pregnancy_start_time,
            'mate_id': self.mate_id,
            'mate_genetics': self.mate_genetics,
            'genetics': self.genetics,
            'breeding_history': self.breeding_history.copy(),
            'offspring_ids': self.offspring_ids.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BreedingSystem':
        """Deserialize from dictionary."""
        system = cls(
            creature_id=data.get('creature_id', 'unknown'),
            gender=data.get('gender', 'female')
        )
        system.can_breed = data.get('can_breed', False)
        system.times_bred = data.get('times_bred', 0)
        system.offspring_count = data.get('offspring_count', 0)
        system.is_pregnant = data.get('is_pregnant', False)
        system.pregnancy_progress = data.get('pregnancy_progress', 0.0)
        system.pregnancy_duration_days = data.get('pregnancy_duration_days', 7.0)
        system.pregnancy_start_time = data.get('pregnancy_start_time')
        system.mate_id = data.get('mate_id')
        system.mate_genetics = data.get('mate_genetics')
        system.genetics = data.get('genetics', system.genetics)
        system.breeding_history = data.get('breeding_history', [])
        system.offspring_ids = data.get('offspring_ids', [])
        return system
