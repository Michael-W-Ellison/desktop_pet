"""
Phase 8: Health and Illness System

Manages pet health, illness, and recovery.
"""
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class IllnessType(Enum):
    """Types of illnesses."""
    COLD = "cold"
    FLU = "flu"
    STOMACH_BUG = "stomach_bug"
    INFECTION = "infection"
    PARASITE = "parasite"
    ALLERGY = "allergy"
    EXHAUSTION = "exhaustion"
    MALNUTRITION = "malnutrition"


class IllnessSeverity(Enum):
    """Illness severity levels."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class HealthSystem:
    """
    Manages pet health and illness.

    Features:
    - Overall health score (0-100)
    - Multiple concurrent illnesses
    - Illness progression and recovery
    - Medicine and treatment
    - Environmental risk factors
    """

    def __init__(self):
        """Initialize health system."""
        self.health = 100.0  # 0-100 overall health
        self.max_health = 100.0

        # Current illnesses
        self.active_illnesses = []  # List of active illness dicts

        # Immunity system
        self.immunity = 50.0  # 0-100, resistance to illness
        self.immunity_history = {}  # illness_type: immunity_level

        # Treatment history
        self.medications = []  # Active medications
        self.treatment_history = []  # Past treatments

        # Health statistics
        self.total_illnesses = 0
        self.total_recoveries = 0
        self.total_vet_visits = 0

        # Risk factors
        self.stress_level = 0.0  # 0-100
        self.hygiene_level = 100.0  # 0-100

    def update(self, hours_elapsed: float, environment: Dict[str, Any]):
        """
        Update health status.

        Args:
            hours_elapsed: Hours since last update
            environment: Environmental factors (cleanliness, stress, etc.)
        """
        # Update active illnesses
        for illness in self.active_illnesses[:]:  # Copy list to allow removal
            self._progress_illness(illness, hours_elapsed)

            # Check if recovered
            if illness['recovery_progress'] >= 1.0:
                self._recover_from_illness(illness)
                self.active_illnesses.remove(illness)

        # Update medications
        for med in self.medications[:]:
            med['hours_remaining'] -= hours_elapsed
            if med['hours_remaining'] <= 0:
                self.medications.remove(med)

        # Natural health regeneration (if not sick)
        if not self.active_illnesses:
            health_regen = 2.0 * hours_elapsed  # 2 points per hour
            self.health = min(self.max_health, self.health + health_regen)

        # Update immunity
        self._update_immunity(hours_elapsed, environment)

        # Update stress and hygiene from environment
        if 'stress' in environment:
            self.stress_level = environment['stress']
        if 'cleanliness' in environment:
            self.hygiene_level = environment['cleanliness']

        # Random illness checks
        if random.random() < 0.001 * hours_elapsed:  # Small chance per hour
            self._check_for_illness()

    def _progress_illness(self, illness: Dict[str, Any], hours_elapsed: float):
        """Progress an illness (worsen or recover)."""
        # Apply illness effects
        health_damage = illness['damage_per_hour'] * hours_elapsed
        self.health = max(0.0, self.health - health_damage)

        # Recovery progress
        recovery_rate = illness['natural_recovery_rate']

        # Medicine speeds recovery
        for med in self.medications:
            if illness['type'] in med['effective_against']:
                recovery_rate *= 2.0

        illness['recovery_progress'] += recovery_rate * hours_elapsed / 24.0  # Per day

        # Illness can worsen if untreated
        if illness['recovery_progress'] < 0.1 and random.random() < 0.05:
            self._worsen_illness(illness)

    def _worsen_illness(self, illness: Dict[str, Any]):
        """Make illness worse."""
        current_severity = IllnessSeverity(illness['severity'])

        if current_severity == IllnessSeverity.MILD:
            illness['severity'] = IllnessSeverity.MODERATE.value
            illness['damage_per_hour'] *= 1.5
        elif current_severity == IllnessSeverity.MODERATE:
            illness['severity'] = IllnessSeverity.SEVERE.value
            illness['damage_per_hour'] *= 1.5
        elif current_severity == IllnessSeverity.SEVERE:
            illness['severity'] = IllnessSeverity.CRITICAL.value
            illness['damage_per_hour'] *= 2.0

    def _recover_from_illness(self, illness: Dict[str, Any]):
        """Recover from an illness."""
        self.total_recoveries += 1

        # Build immunity to this illness type
        illness_type = illness['type']
        current_immunity = self.immunity_history.get(illness_type, 0.0)
        self.immunity_history[illness_type] = min(100.0, current_immunity + 20.0)

        # Overall immunity boost
        self.immunity = min(100.0, self.immunity + 5.0)

    def _update_immunity(self, hours_elapsed: float, environment: Dict[str, Any]):
        """Update immunity based on conditions."""
        # Good conditions improve immunity slowly
        happiness = environment.get('happiness', 50.0)
        nutrition = environment.get('nutrition', 50.0)
        rest = environment.get('energy', 50.0)

        immunity_change = 0.0

        # Positive factors
        if happiness > 70:
            immunity_change += 0.1 * hours_elapsed
        if nutrition > 70:
            immunity_change += 0.1 * hours_elapsed
        if rest > 70:
            immunity_change += 0.1 * hours_elapsed

        # Negative factors
        if self.stress_level > 70:
            immunity_change -= 0.2 * hours_elapsed
        if self.hygiene_level < 30:
            immunity_change -= 0.2 * hours_elapsed

        self.immunity = max(0.0, min(100.0, self.immunity + immunity_change))

    def _check_for_illness(self):
        """Check if pet gets sick (random)."""
        # Calculate illness probability
        illness_prob = (100 - self.immunity) / 100.0

        # Stress and poor hygiene increase risk
        if self.stress_level > 70:
            illness_prob *= 1.5
        if self.hygiene_level < 30:
            illness_prob *= 2.0

        # Roll for illness
        if random.random() < illness_prob:
            # Random illness type
            illness_types = list(IllnessType)
            illness_type = random.choice(illness_types)
            self.contract_illness(illness_type.value, severity="mild")

    def contract_illness(self, illness_type: str, severity: str = "mild",
                        source: str = "environmental") -> Dict[str, Any]:
        """
        Pet contracts an illness.

        Args:
            illness_type: Type of illness
            severity: Severity level
            source: How illness was contracted

        Returns:
            Dictionary with illness details
        """
        # Check immunity to this specific illness
        specific_immunity = self.immunity_history.get(illness_type, 0.0)

        # High immunity might prevent illness
        if specific_immunity > 80 and random.random() < 0.7:
            return {'contracted': False, 'reason': 'immune'}

        # Create illness
        illness = {
            'type': illness_type,
            'severity': severity,
            'contracted_time': time.time(),
            'datetime': datetime.now().isoformat(),
            'source': source,
            'recovery_progress': 0.0,
            'natural_recovery_rate': 0.05,  # 5% per day
            'damage_per_hour': self._get_illness_damage(illness_type, severity),
            'symptoms': self._get_illness_symptoms(illness_type)
        }

        self.active_illnesses.append(illness)
        self.total_illnesses += 1

        return {'contracted': True, 'illness': illness}

    def _get_illness_damage(self, illness_type: str, severity: str) -> float:
        """Get damage per hour for illness type and severity."""
        base_damage = {
            'cold': 0.5,
            'flu': 1.0,
            'stomach_bug': 1.5,
            'infection': 2.0,
            'parasite': 1.0,
            'allergy': 0.3,
            'exhaustion': 0.8,
            'malnutrition': 1.2
        }

        severity_multiplier = {
            'mild': 1.0,
            'moderate': 2.0,
            'severe': 4.0,
            'critical': 8.0
        }

        damage = base_damage.get(illness_type, 1.0)
        damage *= severity_multiplier.get(severity, 1.0)

        return damage

    def _get_illness_symptoms(self, illness_type: str) -> List[str]:
        """Get symptoms for illness type."""
        symptoms_map = {
            'cold': ['sneezing', 'runny_nose', 'lethargy'],
            'flu': ['fever', 'body_aches', 'lethargy', 'loss_of_appetite'],
            'stomach_bug': ['nausea', 'vomiting', 'diarrhea', 'loss_of_appetite'],
            'infection': ['fever', 'swelling', 'pain', 'lethargy'],
            'parasite': ['itching', 'weight_loss', 'poor_coat'],
            'allergy': ['itching', 'sneezing', 'watery_eyes'],
            'exhaustion': ['lethargy', 'weakness', 'irritability'],
            'malnutrition': ['weight_loss', 'weakness', 'poor_coat']
        }

        return symptoms_map.get(illness_type, ['discomfort'])

    def administer_medicine(self, medicine_type: str, illness_targets: List[str]) -> Dict[str, Any]:
        """
        Give medicine to pet.

        Args:
            medicine_type: Type of medicine
            illness_targets: List of illness types this medicine treats

        Returns:
            Treatment results
        """
        medication = {
            'type': medicine_type,
            'effective_against': illness_targets,
            'started_time': time.time(),
            'hours_remaining': 24.0  # 24 hour duration
        }

        self.medications.append(medication)

        # Record treatment
        self.treatment_history.append({
            'timestamp': time.time(),
            'medicine': medicine_type,
            'active_illnesses': [ill['type'] for ill in self.active_illnesses]
        })

        # Immediate slight health boost
        self.health = min(self.max_health, self.health + 5.0)

        return {
            'success': True,
            'medicine': medicine_type,
            'treating': [ill['type'] for ill in self.active_illnesses if ill['type'] in illness_targets]
        }

    def visit_vet(self) -> Dict[str, Any]:
        """
        Visit veterinarian for professional treatment.

        Returns:
            Vet visit results
        """
        self.total_vet_visits += 1

        # Diagnose all illnesses
        diagnosed = [
            {
                'type': ill['type'],
                'severity': ill['severity'],
                'recovery_progress': ill['recovery_progress']
            }
            for ill in self.active_illnesses
        ]

        # Treat all illnesses (boost recovery significantly)
        treatments = []
        for illness in self.active_illnesses:
            illness['recovery_progress'] += 0.3  # 30% recovery boost
            illness['damage_per_hour'] *= 0.5  # Reduce damage
            treatments.append(illness['type'])

        # Health boost
        health_restored = min(30.0, self.max_health - self.health)
        self.health = min(self.max_health, self.health + health_restored)

        # Stress reduction from care
        self.stress_level = max(0.0, self.stress_level - 20.0)

        return {
            'diagnosed_illnesses': diagnosed,
            'treatments_given': treatments,
            'health_restored': health_restored,
            'recovery_boost': 30.0,
            'cost': 50 + len(self.active_illnesses) * 25  # In-game currency
        }

    def is_sick(self) -> bool:
        """Check if pet is currently sick."""
        return len(self.active_illnesses) > 0

    def get_health_status(self) -> str:
        """Get overall health status."""
        if self.health >= 90:
            return "excellent"
        elif self.health >= 70:
            return "good"
        elif self.health >= 50:
            return "fair"
        elif self.health >= 30:
            return "poor"
        elif self.health >= 10:
            return "very_poor"
        else:
            return "critical"

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        return {
            'health': self.health,
            'max_health': self.max_health,
            'health_status': self.get_health_status(),
            'is_sick': self.is_sick(),
            'active_illnesses': len(self.active_illnesses),
            'illnesses': [
                {
                    'type': ill['type'],
                    'severity': ill['severity'],
                    'symptoms': ill['symptoms'],
                    'recovery_progress': ill['recovery_progress'],
                    'days_sick': (time.time() - ill['contracted_time']) / 86400.0
                }
                for ill in self.active_illnesses
            ],
            'immunity': self.immunity,
            'stress_level': self.stress_level,
            'active_medications': len(self.medications),
            'total_illnesses': self.total_illnesses,
            'total_recoveries': self.total_recoveries,
            'total_vet_visits': self.total_vet_visits
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'health': self.health,
            'max_health': self.max_health,
            'active_illnesses': self.active_illnesses.copy(),
            'immunity': self.immunity,
            'immunity_history': self.immunity_history.copy(),
            'medications': self.medications.copy(),
            'treatment_history': self.treatment_history.copy(),
            'total_illnesses': self.total_illnesses,
            'total_recoveries': self.total_recoveries,
            'total_vet_visits': self.total_vet_visits,
            'stress_level': self.stress_level,
            'hygiene_level': self.hygiene_level
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthSystem':
        """Deserialize from dictionary."""
        system = cls()
        system.health = data.get('health', 100.0)
        system.max_health = data.get('max_health', 100.0)
        system.active_illnesses = data.get('active_illnesses', [])
        system.immunity = data.get('immunity', 50.0)
        system.immunity_history = data.get('immunity_history', {})
        system.medications = data.get('medications', [])
        system.treatment_history = data.get('treatment_history', [])
        system.total_illnesses = data.get('total_illnesses', 0)
        system.total_recoveries = data.get('total_recoveries', 0)
        system.total_vet_visits = data.get('total_vet_visits', 0)
        system.stress_level = data.get('stress_level', 0.0)
        system.hygiene_level = data.get('hygiene_level', 100.0)
        return system
