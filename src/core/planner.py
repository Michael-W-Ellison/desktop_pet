"""
Strategic planner for ADVANCED/EXPERT pets: multi-step strategies over the coming day.

The planner combines:
- A world model learned from the pet's own experience: for each goal, how hunger,
  energy and happiness change while the player is away, what a player interaction
  under that goal does (for example, whether asking for food gets the pet fed), and
  how the goal changes the chance of an interaction.
- A forecast of when the player will be around, from the social network (time of
  day, day of week and memory of previous days).

It plans over PLANNER_HORIZON_HOURS in PLANNER_STEP_MINUTES steps with dynamic
programming on a grid of (hunger, energy, happiness), scoring each step with the
same reward terms the RL agent learns from. The result is the goal that does best
over the whole horizon, such as asking for food while the player is still around
because the next chance to eat is hours away.
"""
import time
from typing import Callable, Dict, Any, List

import numpy as np

from .config import (
    PLANNER_STEP_MINUTES, PLANNER_HORIZON_HOURS, PLANNER_DISCOUNT, PLANNER_MIN_EXPERIENCE,
    PLANNER_REPLAN_SECONDS, PLANNER_MARGIN, SOCIAL_PREDICTION_HORIZON
)

# Forecast at or above which the player counts as "around" for learning goal effects
PLAYER_AROUND_FORECAST = 0.3

PLANNER_GOALS = ['seek_food', 'rest', 'seek_interaction', 'play', 'explore']
NEEDS = ('hunger', 'energy', 'happiness')

# Grid the plan is computed on (values in between are interpolated)
HUNGER_GRID = np.linspace(0, 100, 21)
ENERGY_GRID = np.linspace(0, 100, 6)
HAPPINESS_GRID = np.linspace(0, 100, 11)


class WorldModel:
    """Need dynamics and player responses per goal, learned from observed decision steps."""

    def __init__(self):
        # Per goal: totals over steps without a player interaction (to learn drift per hour)
        self.drift = {g: {'seconds': 0.0, **{n: 0.0 for n in NEEDS}} for g in PLANNER_GOALS}
        # Per goal: totals over steps with an interaction (to learn its effect)
        self.events = {g: {'count': 0, 'positive': 0, **{n: 0.0 for n in NEEDS}} for g in PLANNER_GOALS}
        # Per goal: steps observed and steps with an interaction
        self.steps = {g: 0 for g in PLANNER_GOALS}
        self.interacting_steps = {g: 0 for g in PLANNER_GOALS}
        # The same, counted only while the player was forecast to be around, so a goal
        # is not credited for interactions that only happen at times the player is there
        self.around_steps = {g: 0 for g in PLANNER_GOALS}
        self.around_interacting_steps = {g: 0 for g in PLANNER_GOALS}

    @property
    def experience(self) -> int:
        return sum(self.steps.values())

    def observe(self, goal: str, seconds: float, before: Dict[str, float], after: Dict[str, float],
                interacted: bool, positive: bool, player_forecast: float = 0.0):
        """
        Record one decision step: the goal pursued, its duration and what changed.

        Args:
            player_forecast: Forecast chance the player would interact, when the step began
        """
        if goal not in self.steps or seconds <= 0:
            return
        self.steps[goal] += 1
        if player_forecast >= PLAYER_AROUND_FORECAST:
            self.around_steps[goal] += 1
            self.around_interacting_steps[goal] += interacted
        deltas = {n: after[n] - before[n] for n in NEEDS}
        if interacted:
            self.interacting_steps[goal] += 1
            event = self.events[goal]
            event['count'] += 1
            event['positive'] += positive
            for n in NEEDS:
                event[n] += deltas[n]
        else:
            drift = self.drift[goal]
            drift['seconds'] += seconds
            for n in NEEDS:
                drift[n] += deltas[n]

    def _pooled(self, table: Dict[str, Dict[str, float]], key: str, goal: str, minimum: float):
        """A goal's own totals, or all goals pooled if it has too little data."""
        entry = table[goal]
        if entry[key] >= minimum:
            return entry
        pooled = {k: sum(table[g][k] for g in PLANNER_GOALS) for k in entry}
        return pooled if pooled[key] > 0 else None

    def drift_per_step(self, goal: str, step_seconds: float) -> np.ndarray:
        """Expected change in (hunger, energy, happiness) over a step without the player."""
        entry = self._pooled(self.drift, 'seconds', goal, 600.0)
        if entry is None:
            return np.zeros(3)
        return np.array([entry[n] / entry['seconds'] * step_seconds for n in NEEDS])

    def interaction_effect(self, goal: str) -> np.ndarray:
        """Expected change in (hunger, energy, happiness) from a player interaction."""
        entry = self._pooled(self.events, 'count', goal, 5)
        if entry is None:
            return np.zeros(3)
        return np.array([entry[n] / entry['count'] for n in NEEDS])

    def positive_share(self, goal: str) -> float:
        entry = self._pooled(self.events, 'count', goal, 5)
        return entry['positive'] / entry['count'] if entry else 1.0

    def interaction_ratio(self, goal: str) -> float:
        """How much more (or less) often the player interacts, while around, when the pet pursues this goal."""
        total_steps = sum(self.around_steps.values())
        total_interacting = sum(self.around_interacting_steps.values())
        if self.around_steps[goal] < 50 or total_interacting == 0:
            return 1.0
        goal_rate = self.around_interacting_steps[goal] / self.around_steps[goal]
        return float(np.clip(goal_rate / (total_interacting / total_steps), 0.2, 5.0))

    def to_dict(self) -> Dict[str, Any]:
        return {'drift': self.drift, 'events': self.events, 'steps': self.steps,
                'interacting_steps': self.interacting_steps, 'around_steps': self.around_steps,
                'around_interacting_steps': self.around_interacting_steps}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldModel':
        model = cls()
        for name in ('drift', 'events', 'steps', 'interacting_steps', 'around_steps', 'around_interacting_steps'):
            for goal, value in data.get(name, {}).items():
                if goal in model.steps:
                    getattr(model, name)[goal] = value
        return model


def _interpolation_weights(hunger: np.ndarray, energy: np.ndarray, happiness: np.ndarray):
    """
    Corner indices (into the flattened grid) and weights for trilinear interpolation.

    Returns:
        (indices, weights): two lists of 8 arrays shaped like the inputs
    """
    def axis(grid, x):
        x = np.clip(x, grid[0], grid[-1])
        i = np.clip(np.searchsorted(grid, x) - 1, 0, len(grid) - 2)
        w = (x - grid[i]) / (grid[i + 1] - grid[i])
        return i, w

    (hi, hw), (ei, ew), (pi, pw) = axis(HUNGER_GRID, hunger), axis(ENERGY_GRID, energy), axis(HAPPINESS_GRID, happiness)
    shape = (len(HUNGER_GRID), len(ENERGY_GRID), len(HAPPINESS_GRID))
    indices, weights = [], []
    for dh, wh in ((0, 1 - hw), (1, hw)):
        for de, we in ((0, 1 - ew), (1, ew)):
            for dp, wp in ((0, 1 - pw), (1, pw)):
                indices.append(np.ravel_multi_index((hi + dh, ei + de, pi + dp), shape))
                weights.append(wh * we * wp)
    return indices, weights


def _interpolate(values: np.ndarray, hunger: np.ndarray, energy: np.ndarray,
                 happiness: np.ndarray) -> np.ndarray:
    """Trilinear interpolation of a value grid at continuous need levels."""
    return _gather(values, *_interpolation_weights(hunger, energy, happiness))


def _gather(values: np.ndarray, indices, weights) -> np.ndarray:
    """Interpolate with precomputed corner indices and weights."""
    flat = values.ravel()
    return sum(w * flat[i] for i, w in zip(indices, weights))


def step_reward(goal: str, before: np.ndarray, after: np.ndarray, interacted: bool,
                positive_share: float) -> np.ndarray:
    """
    Reward for one plan step, using the RL agent's reward terms
    (ReinforcementLearningAgent.calculate_reward) on whole grids of states.

    Args:
        before, after: Arrays shaped (3, ...) of hunger, energy, happiness
    """
    hunger_b, hunger_a = before[0], after[0]
    energy_a, happiness_b, happiness_a = after[1], before[2], after[2]
    reward = 0.1 * (happiness_a - happiness_b)
    reward = reward - np.where(hunger_a > 80, 2.0, np.where(hunger_a > 60, 0.5, 0.0))
    reward = reward - np.where(energy_a < 20, 1.0, 0.0)
    if goal == 'rest':
        reward = reward + np.where((energy_a >= 20) & (energy_a < 50), 1.0, 0.0)
    alive = hunger_a < 100
    reward = reward + np.where(alive, 0.5, -50.0)
    if interacted:
        reward = reward + 2.0 + 1.0 * positive_share
    if goal == 'seek_food':
        reward = reward + np.where(hunger_a < hunger_b, 1.5, 0.0)
    return reward


class Planner:
    """Plans which goal to pursue over the coming day."""

    def __init__(self):
        self.model = WorldModel()
        self.last_plan_time = None
        self.plan: List[Dict[str, Any]] = []
        self.goal_values: Dict[str, float] = {}

    @property
    def ready(self) -> bool:
        """Whether the world model has enough experience to plan with."""
        return self.model.experience >= PLANNER_MIN_EXPERIENCE

    def needs_replan(self, now: float) -> bool:
        return self.last_plan_time is None or now - self.last_plan_time >= PLANNER_REPLAN_SECONDS

    def make_plan(self, needs: Dict[str, float], now: float,
                  interaction_probability: Callable[[float], float]) -> List[Dict[str, Any]]:
        """
        Plan the coming horizon.

        Args:
            needs: Current hunger, energy and happiness
            now: Current time
            interaction_probability: P(player interacts within SOCIAL_PREDICTION_HORIZON)
                at a given timestamp

        Returns:
            List of plan steps: {'time', 'goal', 'hunger', 'energy', 'happiness', 'p_player'}
        """
        step_seconds = PLANNER_STEP_MINUTES * 60
        steps = int(PLANNER_HORIZON_HOURS * 60 / PLANNER_STEP_MINUTES)
        times = [now + k * step_seconds for k in range(steps)]

        # Chance the player interacts during each step, from the 30-minute forecast
        share = min(1.0, step_seconds / SOCIAL_PREDICTION_HORIZON)
        p_player = [1.0 - (1.0 - float(np.clip(interaction_probability(t), 0, 1))) ** share for t in times]

        grid = np.stack(np.meshgrid(HUNGER_GRID, ENERGY_GRID, HAPPINESS_GRID, indexing='ij'))
        drift = {g: self.model.drift_per_step(g, step_seconds) for g in PLANNER_GOALS}
        effect = {g: self.model.interaction_effect(g) for g in PLANNER_GOALS}
        positive = {g: self.model.positive_share(g) for g in PLANNER_GOALS}
        ratio = {g: self.model.interaction_ratio(g) for g in PLANNER_GOALS}

        def outcome(goal, interacted):
            """Needs after one step, and its reward, for every grid state."""
            change = drift[goal] + (effect[goal] if interacted else 0.0)
            after = np.clip(grid + change.reshape(3, 1, 1, 1), 0, 100)
            return after, step_reward(goal, grid, after, interacted, positive[goal])

        # Outcomes for every goal, without and with a player interaction, stacked
        # so each step interpolates them all at once
        afters, rewards = [], []
        for goal in PLANNER_GOALS:
            for interacted in (False, True):
                after, reward = outcome(goal, interacted)
                afters.append(after)
                rewards.append(reward)
        afters = np.stack(afters)                    # (goals * 2, 3, *grid)
        rewards = np.stack(rewards)                  # (goals * 2, *grid)
        dead = afters[:, 0] >= 100
        # The same next states are looked up at every step, so find their grid corners once
        corners = _interpolation_weights(afters[:, 0], afters[:, 1], afters[:, 2])
        ratios = np.repeat([ratio[g] for g in PLANNER_GOALS], 2)
        with_player = np.tile([0.0, 1.0], len(PLANNER_GOALS))

        # Backward dynamic programming over the horizon
        value = np.zeros(grid.shape[1:])
        policies = [None] * steps
        for k in reversed(range(steps)):
            p = np.minimum(1.0, p_player[k] * ratios)
            weights = np.where(with_player == 1.0, p, 1.0 - p).reshape(-1, 1, 1, 1)
            future = np.where(dead, 0.0, _gather(value, *corners))
            branch_q = weights * (rewards + PLANNER_DISCOUNT * future)
            q_values = branch_q.reshape(len(PLANNER_GOALS), 2, *grid.shape[1:]).sum(axis=1)
            policies[k] = q_values
            value = q_values.max(axis=0)

        # Value of each goal now, over the whole horizon
        current = [np.array([needs[n]], dtype=float) for n in NEEDS]
        self.goal_values = {g: float(_interpolate(policies[0][i], *current)[0])
                            for i, g in enumerate(PLANNER_GOALS)}

        # Follow the plan forward from the current needs (expected outcomes)
        state = np.array([needs['hunger'], needs['energy'], needs['happiness']], dtype=float)
        plan = []
        for k in range(steps):
            q_here = [_interpolate(policies[k][i], *[np.array([v]) for v in state])[0]
                      for i in range(len(PLANNER_GOALS))]
            goal = PLANNER_GOALS[int(np.argmax(q_here))]
            # Steps where no goal is clearly better are left to the goal rules
            label = goal if max(q_here) - min(q_here) > PLANNER_MARGIN else 'no preference'
            plan.append({'time': times[k], 'goal': label, 'hunger': state[0], 'energy': state[1],
                         'happiness': state[2], 'p_player': p_player[k]})
            p = min(1.0, p_player[k] * ratio[goal])
            state = np.clip(state + drift[goal] + p * effect[goal], 0, 100)

        self.plan = plan
        self.last_plan_time = now
        return plan

    def choose_goal(self, rule_goal: str) -> str:
        """
        The planned goal if it does clearly better over the horizon than the goal the
        fixed rules would pick; otherwise the rules' goal.
        """
        if not self.plan:
            return rule_goal
        planned = max(self.goal_values, key=self.goal_values.get)
        if self.goal_values[planned] - self.goal_values.get(rule_goal, float('-inf')) > PLANNER_MARGIN:
            return planned
        return rule_goal

    def describe(self, count: int = 8) -> List[str]:
        """Upcoming plan steps as text, merging consecutive steps with the same goal."""
        lines, previous = [], None
        for step in self.plan:
            if step['goal'] != previous:
                when = time.strftime('%a %H:%M', time.localtime(step['time']))
                lines.append(f"{when}  {step['goal']:<17} (hunger {step['hunger']:.0f}, "
                             f"player {step['p_player']:.0%})")
                previous = step['goal']
            if len(lines) >= count:
                break
        return lines

    def to_dict(self) -> Dict[str, Any]:
        return {'model': self.model.to_dict()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Planner':
        planner = cls()
        planner.model = WorldModel.from_dict(data.get('model', {}))
        return planner

