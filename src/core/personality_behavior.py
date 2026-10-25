"""
Turns a personality's trait values (PERSONALITY_TRAITS in config) into behavior.

Traits are multipliers around 1.0; a trait a personality does not list counts as 1.0.
- Activity frequency traits scale how often each activity is chosen
- Attention traits set how often the pet sticks with what it is doing
- Unpredictability traits set how often it does something random
- Need and emotion traits change sleep, happiness decay and emotional sensitivity
"""
import math
import random
from typing import Dict, Optional

from .config import (
    ACTIVITY_CHOICE_TEMPERATURE, BASE_ACTIVITY_PERSISTENCE, BASE_RANDOM_ACTIVITY_CHANCE,
    SLEEP_ENERGY_THRESHOLD
)

# Traits that make each activity more (multiplied) or less (divided) frequent
ACTIVITY_TRAITS = {
    'ball_play': (('play_frequency', 'self_play_frequency'), ()),
    'mouse_chase': (('play_frequency', 'mouse_following_frequency', 'interaction_desire',
                     'aggression', 'territoriality'), ()),
    'hide_seek': (('hiding_frequency',), ('boldness',)),
    'hide_and_seek': (('hiding_frequency',), ('boldness',)),
    'hide': (('hiding_frequency',), ('boldness',)),
    'explore': (('exploration_frequency', 'boldness', 'icon_movement_frequency'), ()),
    'random_wander': (('exploration_frequency', 'random_behavior'), ()),
    'icon_interaction': (('icon_movement_frequency', 'exploration_frequency'), ()),
    'sleep': (('sleep_frequency',), ()),
    'idle': (('calm_behavior', 'patience'), ()),
    'stay_still': (('calm_behavior', 'patience'), ()),
    'seek_interaction': (('interaction_desire', 'owner_focus'), ('independence', 'self_focus')),
    'move_to_center': (('interaction_desire',), ()),
    'seek_food': (('resource_guarding',), ()),
    'eat': (('resource_guarding',), ()),
}


class PersonalityBehavior:
    """Behavioral parameters derived from one personality's traits."""

    def __init__(self, traits: Dict[str, float]):
        self.traits = dict(traits)

    def trait(self, name: str) -> float:
        return self.traits.get(name, 1.0)

    def activity_weight(self, activity: str) -> float:
        """How much more often than average this personality chooses an activity."""
        boosts, damps = ACTIVITY_TRAITS.get(activity, ((), ()))
        weight = 1.0
        for name in boosts:
            weight *= self.trait(name)
        for name in damps:
            weight /= self.trait(name)
        return weight

    @property
    def persistence(self) -> float:
        """Chance of sticking with the current activity at the next decision."""
        value = BASE_ACTIVITY_PERSISTENCE * self.trait('attention_span') * self.trait('persistence') * self.trait('focus')
        return min(0.8, value)

    @property
    def random_activity_chance(self) -> float:
        """Chance of choosing an activity at random."""
        value = (BASE_RANDOM_ACTIVITY_CHANCE * self.trait('random_behavior') * self.trait('unpredictability')
                 * self.trait('pattern_breaking') / (self.trait('predictability') * self.trait('routine_preference')))
        return min(0.5, value)

    def choose_activity(self, scores: Dict[str, float], previous: Optional[str] = None) -> str:
        """
        Choose an activity from learned scores, shaped by personality.

        Probability of each activity is proportional to
        activity_weight * exp(score / ACTIVITY_CHOICE_TEMPERATURE), so learned
        preferences dominate while frequency traits scale how often each happens.

        Args:
            scores: Learned score (about 0-1) for each candidate activity
            previous: Activity chosen at the previous decision

        Returns:
            Chosen activity name
        """
        activities = list(scores)
        if random.random() < self.random_activity_chance:
            return random.choice(activities)
        if previous in scores and random.random() < self.persistence:
            return previous

        top = max(scores.values())
        weights = [self.activity_weight(a) * math.exp((scores[a] - top) / ACTIVITY_CHOICE_TEMPERATURE)
                   for a in activities]
        return random.choices(activities, weights=weights)[0]

    # Needs

    @property
    def sleep_energy_threshold(self) -> float:
        """Energy below which the pet falls asleep."""
        return SLEEP_ENERGY_THRESHOLD * self.trait('sleep_frequency')

    @property
    def neglect_happiness_multiplier(self) -> float:
        """How much faster happiness falls without interaction."""
        return self.trait('happiness_decay')

    @property
    def hunger_unhappiness_multiplier(self) -> float:
        """How much more hunger lowers happiness."""
        return self.trait('irritability')

    # Relationship

    @property
    def negative_reaction_chance(self) -> float:
        """Chance an interaction is received badly."""
        return self.traits.get('negative_reaction_chance', 0.0)

    @property
    def bond_gain_multiplier(self) -> float:
        """How much faster the bond grows from interactions."""
        return self.trait('bonding_speed') * self.trait('bonding_strength')

    @property
    def interaction_desire(self) -> float:
        """How strongly the pet wants the player's company."""
        return (self.trait('interaction_desire') * self.trait('owner_focus')
                / (self.trait('independence') * self.trait('self_focus')))

    # Emotional sensitivity

    @property
    def anxiety_scale(self) -> float:
        """How strongly situations make the pet anxious."""
        return (self.trait('stress_sensitivity')
                / (self.trait('stress_resistance') * self.trait('emotional_stability')
                   * math.sqrt(self.trait('fear_threshold') * self.trait('panic_threshold'))))

    @property
    def loneliness_scale(self) -> float:
        """How quickly being alone makes the pet lonely."""
        return self.trait('separation_anxiety') / (self.trait('independence') * self.trait('wait_tolerance'))

    @property
    def joy_scale(self) -> float:
        """How much joy the pet takes from good situations."""
        return self.trait('happiness_gain')
