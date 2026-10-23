"""
Enhanced Behavior Learner integrating all sophisticated AI systems.

Provides different AI complexity levels:
- SIMPLE: Basic feedforward network
- MEDIUM: Advanced network with LSTM memory
- ADVANCED: Full system with specialized networks and RL
- EXPERT: All features plus visualization and detailed logging
"""
import copy
import itertools
import math
import time
from collections import deque
import numpy as np
from typing import Dict, Any, Optional
from .config import (
    AIComplexity, DEFAULT_AI_COMPLEXITY, DECISION_STABILITY_WINDOW, DECISION_STABILITY_SMOOTHING,
    ADVANCED_DECISION_STABILITY_SMOOTHING,
    LEARNING_RATE, SEQUENCE_LENGTH, RL_STATE_SIZE, BehaviorState
)
from .neural_network import BehaviorLearner as SimpleBehaviorLearner
from .lstm_network import LSTMNetwork
from .specialized_networks import NetworkCoordinator
from .sensory_system import CompleteSensorySystem, HidingSpotMemory
from .reinforcement_learning import GoalOrientedBehaviorSystem
from .expert_monitor import ExpertMonitor, bar

# Final activity for each RL action type
RL_ACTION_ACTIVITY = {
    'move_to_mouse': 'mouse_chase',
    'explore': 'explore',
    'seek_food': 'seek_food',
    'hide': 'hide_seek',
    'play_ball': 'ball_play',
    'sleep': 'sleep',
    'move_to_center': 'move_to_center',
    'stay_still': 'stay_still',
    'seek_interaction': 'seek_interaction',
    'random_wander': 'random_wander',
}

# Player interaction names used by the social network
SOCIAL_INTERACTION_TYPE = {'being_fed': 'feed', 'ball_play': 'play_ball', 'pet': 'pet', 'talk': 'talk'}

# Activity-network activity taught directly by a player interaction
INTERACTION_ACTIVITY = {'being_fed': 'eat', 'ball_play': 'ball_play'}

# Mouse closer than this (pixels) counts as the player being nearby
PLAYER_NEARBY_DISTANCE = 200


class EnhancedBehaviorLearner:
    """
    Enhanced behavior learner with multiple AI complexity levels.

    Adapts sophistication based on user preference and creature age.
    """

    # Fixed (hunger, energy, happiness, time) states used to probe activity decisions
    STABILITY_PROBES = list(itertools.product((0.1, 0.5, 0.9), (0.2, 0.8), (0.2, 0.8), (0.0, 1.0)))

    def __init__(self, creature, complexity: AIComplexity = DEFAULT_AI_COMPLEXITY):
        """
        Initialize enhanced behavior learner.

        Args:
            creature: The Creature instance to learn for
            complexity: AI complexity level
        """
        self.creature = creature
        self.complexity = complexity

        # Sensory system (used by all complexity levels above SIMPLE)
        self.sensory_system = None
        if complexity != AIComplexity.SIMPLE:
            self.sensory_system = CompleteSensorySystem()

        # Initialize appropriate AI system based on complexity
        if complexity == AIComplexity.SIMPLE:
            self._init_simple()
        elif complexity == AIComplexity.MEDIUM:
            self._init_medium()
        elif complexity == AIComplexity.ADVANCED:
            self._init_advanced()
        elif complexity == AIComplexity.EXPERT:
            self._init_expert()

        # Performance monitoring
        self.total_interactions = 0
        self.learning_history = []

        # ADVANCED/EXPERT: the decision being carried out and the player
        # interactions since it was made, learned from at the next decision
        self.pending_decision = None
        self.events_since_decision = []
        self.hiding_spots = HidingSpotMemory()

        # Most recent activity chosen (personalities with long attention spans stick with it)
        self.last_activity = None

        # Recent probe outputs per network for measuring stability (not saved)
        self.probe_history = {}

    def _init_simple(self):
        """Initialize simple AI (basic feedforward network)."""
        self.simple_learner = SimpleBehaviorLearner(self.creature)
        self.network_coordinator = None
        self.rl_system = None

    def _init_medium(self):
        """Initialize medium AI (advanced network with LSTM)."""
        # Use advanced network with LSTM for activity prediction
        self.activity_network = LSTMNetwork(
            input_size=len(self.get_state_vector()),  # State + sensory inputs
            hidden_size=32,
            output_size=5,  # Activity probabilities
            num_layers=2,
            learning_rate=LEARNING_RATE,
            sequence_length=SEQUENCE_LENGTH
        )

        self.network_coordinator = None
        self.rl_system = None

    def _init_advanced(self):
        """Initialize advanced AI (full specialized networks + RL)."""
        # Complete network coordinator with all specialized networks
        self.network_coordinator = NetworkCoordinator()

        # Reinforcement learning system
        self.rl_system = GoalOrientedBehaviorSystem(state_size=RL_STATE_SIZE)

        self.activity_network = None

    def _init_expert(self):
        """Initialize expert AI (advanced + visualization + logging)."""
        # Same as advanced, but with additional monitoring
        self._init_advanced()

        # Additional expert features: detailed log file, learning metrics,
        # decision tracking, and the AI Insights view (get_insights)
        self.detailed_logging = True
        self.visualization_enabled = True
        self.monitor = ExpertMonitor()

    def set_screen_size(self, screen_width: int, screen_height: int):
        """Use the actual screen size for sensing and movement targets."""
        if self.sensory_system:
            self.sensory_system.set_screen_size(screen_width, screen_height)

    def get_rl_state_vector(self) -> np.ndarray:
        """
        State for the reinforcement-learning agent: 7 creature stats + 28 sensory inputs.

        Returns:
            Vector of length RL_STATE_SIZE
        """
        creature = self.creature
        stats = [
            creature.hunger / 100.0,
            creature.energy / 100.0,
            creature.happiness / 100.0,
            min(1.0, (time.time() - creature.last_interaction_time) / 3600.0),
            creature.bonding.bond / 100.0,
            creature.trust.trust / 100.0,
            1.0 if creature.current_state == BehaviorState.SLEEPING else 0.0,
        ]
        sensory = self.sensory_system.get_complete_sensory_input(
            creature.position[0], creature.position[1]
        )
        return np.concatenate([stats, sensory])

    def update_sensory_inputs(self, mouse_x: float, mouse_y: float):
        """Update sensory system with current mouse position."""
        if self.sensory_system:
            self.sensory_system.update_mouse_position(mouse_x, mouse_y)

    def get_state_vector(self, activity_type: str = None) -> np.ndarray:
        """
        Get complete state vector for neural networks.

        Args:
            activity_type: Optional activity type for simple mode

        Returns:
            State vector appropriate for current complexity level
        """
        if self.complexity == AIComplexity.SIMPLE:
            # Simple state (from original implementation)
            state = [
                self.creature.hunger / 100.0,
                self.creature.energy / 100.0,
                self.creature.happiness / 100.0,
                min(1.0, (time.time() - self.creature.last_interaction_time) / 3600.0)
            ]

            if activity_type:
                activities = ['ball_play', 'mouse_chase', 'hide_and_seek', 'icon_interaction', 'idle']
                encoding = [0.0] * len(activities)
                if activity_type in activities:
                    encoding[activities.index(activity_type)] = 1.0
                state.extend(encoding)

            return np.array(state)

        else:
            # Enhanced state with sensory inputs
            basic_state = [
                self.creature.hunger / 100.0,
                self.creature.energy / 100.0,
                self.creature.happiness / 100.0,
                min(1.0, (time.time() - self.creature.last_interaction_time) / 3600.0),
                # Personality encoding
                *self._encode_personality()
            ]

            # Add sensory inputs
            if self.sensory_system:
                sensory_vector = self.sensory_system.get_complete_sensory_input(
                    self.creature.position[0],
                    self.creature.position[1]
                )
                basic_state = np.concatenate([basic_state, sensory_vector])

            return np.array(basic_state)

    def _encode_personality(self) -> list:
        """Encode personality as one-hot vector."""
        from .config import PersonalityType
        personalities = list(PersonalityType)
        encoding = [0.0] * len(personalities)

        try:
            idx = personalities.index(self.creature.personality)
            encoding[idx] = 1.0
        except (ValueError, AttributeError):
            pass

        return encoding

    def choose_activity(self) -> str:
        """
        Choose best activity based on AI complexity level.

        Returns:
            Activity name
        """
        if self.complexity == AIComplexity.SIMPLE:
            # Use simple learner
            scores = self.simple_learner.get_activity_scores()

        elif self.complexity == AIComplexity.MEDIUM:
            # Use LSTM network
            output = self.activity_network.predict(self.get_state_vector())[0]
            activities = ['ball_play', 'mouse_chase', 'hide_and_seek', 'explore', 'idle']
            scores = dict(zip(activities, (float(s) for s in output)))

        else:  # ADVANCED or EXPERT
            # Use full network coordinator
            behavior = self.network_coordinator.decide_behavior(
                self._get_complete_state_dict(), self._choose_by_personality
            )
            return behavior.get('activity', 'idle')

        return self._choose_by_personality(scores)

    def _choose_by_personality(self, scores: Dict[str, float]) -> str:
        """Pick an activity from learned scores, shaped by the creature's personality."""
        activity = self.creature.behavior.choose_activity(scores, self.last_activity)
        self.last_activity = activity
        return activity

    def _get_complete_state_dict(self) -> Dict[str, Any]:
        """Get complete state dictionary for advanced AI."""
        quality = self._get_recent_interaction_quality()
        state_dict = {
            'hunger': self.creature.hunger,
            'energy': self.creature.energy,
            'happiness': self.creature.happiness,
            'time_since_interaction': time.time() - self.creature.last_interaction_time,
            'personality_vector': self._encode_personality(),
            'recent_interaction_quality': quality,
            'recent_activities': self.creature.get_recent_activities(5),
            'recent_interaction_types': self.creature.get_recent_interaction_types(5),
            'player_mood_estimate': float(np.mean(quality)),
        }

        # Add sensory information and movement targets
        if self.sensory_system:
            x, y = self.creature.position[0], self.creature.position[1]
            sensory_state = self.sensory_system.get_state_dict(x, y)
            state_dict.update(sensory_state)

            mouse = (sensory_state['mouse_x'], sensory_state['mouse_y'])
            layout = self.sensory_system.layout_analyzer
            spot = self.hiding_spots.choose(layout.get_hiding_spots(x, y))
            state_dict['hiding_spot'] = spot
            state_dict['targets'] = {
                'mouse': mouse,
                'center': (layout.screen_width / 2, layout.screen_height / 2),
                'hiding_spot': ((spot['x'] + spot['width'] / 2, spot['y'] + spot['height'] / 2)
                                if spot else None),
            }
            state_dict['player_nearby'] = math.dist((x, y), mouse) < PLAYER_NEARBY_DISTANCE

        return state_dict

    def _get_recent_interaction_quality(self) -> list:
        """Get quality of recent interactions (0-1 scale)."""
        if not hasattr(self.creature, 'interaction_history'):
            return [0.5] * 10

        recent = self.creature.interaction_history[-10:]
        quality = []

        for interaction in recent:
            # Calculate quality based on positive feedback
            q = 1.0 if interaction.get('positive', False) else 0.3
            quality.append(q)

        # Pad if needed
        while len(quality) < 10:
            quality.append(0.5)

        return quality[:10]

    def learn_from_interaction(self, activity_type: str, enjoyed: bool, outcome: Dict[str, Any] = None):
        """
        Learn from an interaction.

        Args:
            activity_type: Type of activity performed
            enjoyed: Whether the creature enjoyed it
            outcome: Additional outcome information
        """
        self.total_interactions += 1

        # Elders' behavior is set: their networks no longer learn
        if self.creature.is_elder():
            return

        if self.complexity == AIComplexity.SIMPLE:
            # Simple learning
            self.simple_learner.learn_from_interaction(activity_type, enjoyed)

        elif self.complexity == AIComplexity.MEDIUM:
            # LSTM learning
            state = self.get_state_vector()
            target = np.zeros((1, 5))

            activities = ['ball_play', 'mouse_chase', 'hide_and_seek', 'explore', 'idle']
            if activity_type in activities:
                idx = activities.index(activity_type)
                target[0, idx] = 1.0 if enjoyed else 0.2

            self.activity_network.add_to_sequence(state)

            if len(self.activity_network.sequence_buffer) >= 3:
                sequence = list(self.activity_network.sequence_buffer)[-3:]
                targets = [target] * len(sequence)
                self.activity_network.train_sequence(sequence, targets)

        else:  # ADVANCED or EXPERT
            # The interaction is credited to the current decision at the next decision
            self.events_since_decision.append({'type': activity_type, 'positive': enjoyed})

            # Some interactions directly show which activity the pet enjoys
            activity = INTERACTION_ACTIVITY.get(activity_type)
            if activity:
                enjoyment = (outcome or {}).get('enjoyment', 1.0 if enjoyed else 0.3)
                self.network_coordinator.activity_net.learn_from_activity(
                    self._get_complete_state_dict(), activity, enjoyment
                )

            if self.complexity == AIComplexity.EXPERT:
                self.monitor.record_interaction(activity_type, enjoyed)

        # Record for expert mode
        if self.complexity == AIComplexity.EXPERT:
            self.learning_history.append({
                'interaction': self.total_interactions,
                'activity': activity_type,
                'enjoyed': enjoyed,
                'timestamp': time.time()
            })

        # Only player interactions advance the stage
        self._update_decision_stability()

    @staticmethod
    def _probe_lstm(network: LSTMNetwork, inputs) -> np.ndarray:
        """Outputs of an LSTM for each input on its own, leaving its recurrent state unchanged."""
        saved_states = (copy.deepcopy(network.h_states), copy.deepcopy(network.c_states))
        outputs = [network.forward_sequence([x], reset_state=True)[0][0][0] for x in inputs]
        network.h_states, network.c_states = saved_states
        return np.concatenate(outputs)

    def _probe_network_scores(self) -> Dict[str, np.ndarray]:
        """
        Outputs of each learning network for fixed probe states.

        SIMPLE and MEDIUM have one learning network; ADVANCED and EXPERT have five
        (movement, activity, emotion, social and the RL Q-network).

        Returns:
            Network name -> flat array of outputs across all probe states
        """
        probes = self.STABILITY_PROBES

        if self.complexity == AIComplexity.SIMPLE:
            learner = self.simple_learner
            activities = ['ball_play', 'mouse_chase', 'hide_and_seek', 'icon_interaction']
            inputs = np.array([[hunger, energy, happiness, hours] + learner.encode_activity(activity)
                               for hunger, energy, happiness, hours in probes
                               for activity in activities])
            return {'activity': learner.network.predict(inputs).ravel()}

        personality = self._encode_personality()

        if self.complexity == AIComplexity.MEDIUM:
            network = self.activity_network
            padding = [0.0] * (network.input_size - 4 - len(personality))
            inputs = [np.array([hunger, energy, happiness, hours] + personality + padding)
                      for hunger, energy, happiness, hours in probes]
            return {'activity': self._probe_lstm(network, inputs)}

        # ADVANCED or EXPERT: every network, each with probe inputs in its own format
        coordinator = self.network_coordinator
        movement_inputs = np.array([coordinator.movement_net.encode_state({
            'pos_x': 960, 'pos_y': 540, 'target_x': hunger * 1920, 'target_y': happiness * 1080,
            'energy': energy * 100, 'distance_to_target': hours * 500,
            'edge_top': 540, 'edge_bottom': 540, 'edge_left': 960, 'edge_right': 960,
            'personality_vector': personality,
        }) for hunger, energy, happiness, hours in probes])
        emotion_inputs = np.array([coordinator.emotion_net.encode_state({
            'hunger': hunger * 100, 'energy': energy * 100, 'happiness': happiness * 100,
            'recent_interaction_quality': [hours] * 10, 'personality_vector': personality,
        }) for hunger, energy, happiness, hours in probes])
        activity_inputs = [np.array([hunger, energy, happiness, hours] + [0.0] * 5 + [0.5] * 5)
                           for hunger, energy, happiness, hours in probes]
        social_inputs = [np.array([hunger, energy, hours] + [happiness] * 5 + [happiness])
                         for hunger, energy, happiness, hours in probes]
        rl_inputs = np.array([[hunger, energy, happiness, hours, 0.5, 0.5, 0.0] + [0.0] * (RL_STATE_SIZE - 7)
                              for hunger, energy, happiness, hours in probes])

        return {
            'movement': coordinator.movement_net.network.predict(movement_inputs).ravel(),
            'activity': self._probe_lstm(coordinator.activity_net.network, activity_inputs),
            'emotion': coordinator.emotion_net.network.predict(emotion_inputs).ravel(),
            'social': self._probe_lstm(coordinator.social_net.network, social_inputs),
            'rl': self.rl_system.rl_agent.q_network.forward(rl_inputs)[0].ravel(),
        }

    def _update_decision_stability(self):
        """
        Update how settled each network is; called once per player interaction.

        For each network, over the last DECISION_STABILITY_WINDOW interactions, compares
        how far its probe outputs moved overall with the total distance they
        travelled. A network that is still learning moves consistently in one
        direction (ratio near 1); a settled one only jitters around the same point
        (ratio near 0). The creature's decision stability is the least settled network.
        """
        stabilities = self.creature.network_stability
        smoothing = (ADVANCED_DECISION_STABILITY_SMOOTHING
                     if self.complexity in (AIComplexity.ADVANCED, AIComplexity.EXPERT)
                     else DECISION_STABILITY_SMOOTHING)
        for name, scores in self._probe_network_scores().items():
            history = self.probe_history.setdefault(name, deque(maxlen=DECISION_STABILITY_WINDOW + 1))
            history.append(scores)
            if len(history) <= DECISION_STABILITY_WINDOW:
                continue

            history = list(history)
            path = sum(np.linalg.norm(b - a) for a, b in zip(history, history[1:]))
            if path == 0:
                continue  # Network has not changed during the window
            settled = 1.0 - np.linalg.norm(history[-1] - history[0]) / path

            stability = stabilities.get(name, 0.0)
            stabilities[name] = float(stability + smoothing * (settled - stability))

        # Every network must have settled; one that has not been measured yet counts as 0
        names = self.network_names()
        self.creature.decision_stability = min(stabilities.get(name, 0.0) for name in names)

    def network_names(self):
        """Names of the networks whose stability drives evolution at this level."""
        if self.complexity in (AIComplexity.ADVANCED, AIComplexity.EXPERT):
            return ['movement', 'activity', 'emotion', 'social', 'rl']
        return ['activity']

    def get_behavioral_decision(self) -> Dict[str, Any]:
        """
        Get complete behavioral decision.

        Returns:
            Dictionary with activity, movement, emotional state, etc.
        """
        if self.complexity in [AIComplexity.SIMPLE, AIComplexity.MEDIUM]:
            # Activity only; the pet manager handles movement
            return {'activity': self.choose_activity()}

        # ADVANCED or EXPERT: full decision with all systems
        state_dict = self._get_complete_state_dict()
        rl_state = self.get_rl_state_vector()

        # Learn from how the previous decision turned out
        self._learn_from_previous_decision(state_dict, rl_state)

        # Emotion -> social -> activity -> movement networks
        decision = self.network_coordinator.decide_behavior(state_dict, self._choose_by_personality)
        modifiers = decision['emotional_modifiers']
        # Emotional desire for company, scaled by how social the personality is
        state_dict['interaction_desire'] = (modifiers['interaction_desire']
                                            * self.creature.behavior.interaction_desire)

        # The RL agent works toward the current goal; its action is carried out
        # when it serves that goal, otherwise the networks' choice stands
        rl_decision = self.rl_system.execute_goal(rl_state, state_dict)
        decision.update({
            'rl_goal': rl_decision['goal'],
            'rl_action': rl_decision['action'],
            'rl_q_value': rl_decision['q_value'],
            'decided_by': 'networks',
        })
        if rl_decision['serves_goal']:
            activity = RL_ACTION_ACTIVITY[rl_decision['action']['type']]
            if activity != decision['activity']:
                decision['activity'] = activity
                decision.update(self.network_coordinator.plan_movement(state_dict, activity, modifiers))
            decision['decided_by'] = 'rl'
            self.last_activity = activity

        decision['target'] = self.network_coordinator.get_target(state_dict, decision['activity'])

        self.pending_decision = {
            'state': state_dict,
            'rl_state': rl_state,
            'rl_action_idx': rl_decision['action_idx'],
            'decision': decision,
        }
        self.events_since_decision = []

        if self.complexity == AIComplexity.EXPERT:
            self.monitor.record_decision(decision)

        return decision

    def get_insights(self, decision: Optional[Dict[str, Any]] = None) -> str:
        """
        Text view of what the AI is doing (EXPERT mode's AI Insights).

        Args:
            decision: Most recent decision, if any

        Returns:
            Multi-line description with bars for emotions, Q-values and metrics
        """
        lines = [f"Decision stability: {bar(self.creature.decision_stability)} "
                 f"{self.creature.decision_stability:.0%} (least settled network)"]
        for name in self.network_names():
            value = self.creature.network_stability.get(name, 0.0)
            label = 'RL' if name == 'rl' else name.capitalize()
            lines.append(f"  {label:<12} {bar(value)} {value:.0%}")
        lines.append(f"Stage: {self.creature.evolution.get_stage_name()}"
                     + (" (behavior set)" if self.creature.is_elder() else ""))
        lines.append(f"Interactions learned from: {self.total_interactions}")

        if self.complexity not in (AIComplexity.ADVANCED, AIComplexity.EXPERT):
            return "\n".join(lines)

        coordinator, agent = self.network_coordinator, self.rl_system.rl_agent
        emotions = coordinator.emotion_net
        lines += ["", "Emotions:"]
        for i, name in enumerate(emotions.emotion_names):
            value = float(emotions.current_emotions[i])
            lines.append(f"  {name.capitalize():<12} {bar(value)} {value:.2f}")

        if decision:
            prediction = decision.get('player_prediction', {})
            lines += ["", f"Activity: {decision.get('activity')} (decided by {decision.get('decided_by')})",
                      f"Goal: {decision.get('rl_goal')}",
                      f"Player interaction expected: {prediction.get('interaction_probability', 0):.0%}"]

        q_values, _ = agent.q_network.forward(self.get_rl_state_vector())
        q_values = q_values[0]
        low, high = float(np.min(q_values)), float(np.max(q_values))
        lines += ["", f"Action values (exploration {agent.epsilon:.0%}):"]
        for i, q in enumerate(q_values):
            name = agent.get_action_description(i)['name']
            scaled = (q - low) / (high - low) if high > low else 0.5
            lines.append(f"  {name:<24} {bar(scaled, 12)} {q:+.2f}")

        if self.complexity == AIComplexity.EXPERT:
            lines += ["", "Learning metrics:"]
            for name, values in self.monitor.summary().items():
                if values['latest'] is None:
                    lines.append(f"  {name}: no data yet")
                else:
                    lines.append(f"  {name}: latest {values['latest']:.4g}, "
                                 f"average {values['average']:.4g} ({values['count']} samples)")
            lines += ["", "Recent decisions:"]
            for entry in self.monitor.recent_decisions(5):
                lines.append(f"  {time.strftime('%H:%M:%S', time.localtime(entry['time']))} "
                             f"{entry['activity']} via {entry['decided_by']} (goal {entry['goal']})")

        return "\n".join(lines)

    def _expected_emotions(self, state: Dict[str, Any]) -> Dict[str, float]:
        """
        Emotions the situation calls for, used to train the emotion network.

        Args:
            state: Complete state dictionary

        Returns:
            Target intensity (0-1) for each emotion
        """
        hunger = state['hunger'] / 100.0
        energy = state['energy'] / 100.0
        happiness = state['happiness'] / 100.0
        quality = float(np.mean(state['recent_interaction_quality']))
        hours_alone = min(1.0, state['time_since_interaction'] / 3600.0)
        recent_types = self.creature.interaction_history[-5:]
        play_share = (sum(1 for i in recent_types if i.get('type') == 'ball_play') / len(recent_types)
                      if recent_types else 0.0)

        def clip(value):
            return float(min(1.0, max(0.0, value)))

        # Personality sets how strongly the pet feels each of these
        behavior = self.creature.behavior
        return {
            'joy': clip(happiness * (0.5 + 0.5 * quality) * behavior.joy_scale),
            'excitement': clip(energy * (0.4 + 0.6 * play_share)),
            'contentment': clip((1.0 - hunger) * happiness),
            'anxiety': clip((max(0.0, hunger - 0.5) * 1.5 + (1.0 - quality) * 0.3) * behavior.anxiety_scale),
            'loneliness': clip(hours_alone * behavior.loneliness_scale),
        }

    def _learn_from_previous_decision(self, state_after: Dict[str, Any], rl_state_after: np.ndarray):
        """
        Learn from the outcome of the previous decision (ADVANCED/EXPERT).

        Args:
            state_after: Complete state now
            rl_state_after: RL state now
        """
        pending, events = self.pending_decision, self.events_since_decision
        self.pending_decision = None
        if pending is None or self.creature.is_elder():
            return

        state_before = pending['state']
        positive = any(e['positive'] for e in events)
        before = {key: state_before[key] for key in ('hunger', 'energy', 'happiness')}
        after = {
            'hunger': state_after['hunger'],
            'energy': state_after['energy'],
            'happiness': state_after['happiness'],
            'alive': not self.creature.is_starving(),
            'player_interacted': bool(events),
            'interaction_positive': positive,
            'ball_caught': any(e['type'] == 'ball_play' and e['positive'] for e in events),
        }

        # Reinforcement learning from the real transition
        reward = self.rl_system.learn_from_outcome(
            pending['rl_state'], pending['rl_action_idx'], rl_state_after, before, after
        )
        reward01 = 1.0 / (1.0 + math.exp(-reward / 2.0))

        # Specialized networks
        last_event = events[-1] if events else None
        self.network_coordinator.learn_from_outcome(state_before, pending['decision'], {
            'reward01': reward01,
            'expected_emotions': self._expected_emotions(state_after),
            'interaction_type': (SOCIAL_INTERACTION_TYPE.get(last_event['type'], last_event['type'])
                                 if last_event else None),
            'positive': positive,
        })

        # Hiding spots earn the reward of the time spent hiding there
        if pending['decision']['activity'] == 'hide_seek' and state_before.get('hiding_spot'):
            self.hiding_spots.record(state_before['hiding_spot'], reward01)

        # Stability (and so evolution) is only measured at player interactions, so
        # learning from decisions alone does not advance the pet's stage

        if self.complexity == AIComplexity.EXPERT:
            agent = self.rl_system.rl_agent
            self.monitor.record_learning(reward, agent.q_network.optimizer.learning_rate,
                                         agent.epsilon, self.creature.decision_stability)

    def to_dict(self) -> Dict[str, Any]:
        """Save learner state."""
        data = {
            'complexity': self.complexity.value,
            'total_interactions': self.total_interactions
        }

        if self.complexity == AIComplexity.SIMPLE:
            data['simple_learner'] = self.simple_learner.to_dict()

        elif self.complexity == AIComplexity.MEDIUM:
            data['activity_network'] = self.activity_network.to_dict()

        else:  # ADVANCED or EXPERT
            if self.network_coordinator:
                data['network_coordinator'] = self.network_coordinator.to_dict()

            if self.rl_system:
                data['rl_system'] = self.rl_system.rl_agent.to_dict()

            data['hiding_spots'] = self.hiding_spots.to_dict()

        if self.complexity == AIComplexity.EXPERT:
            data['learning_history'] = self.learning_history[-100:]  # Last 100 only

        return data

    @classmethod
    def from_dict(cls, creature, data: Dict[str, Any]) -> 'EnhancedBehaviorLearner':
        """Load learner state."""
        from .config import AIComplexity

        complexity_str = data.get('complexity', DEFAULT_AI_COMPLEXITY.value)
        complexity = AIComplexity(complexity_str)

        learner = cls(creature, complexity)
        learner.total_interactions = data.get('total_interactions', 0)

        if complexity == AIComplexity.SIMPLE and 'simple_learner' in data:
            learner.simple_learner = SimpleBehaviorLearner.from_dict(creature, data['simple_learner'])

        elif complexity == AIComplexity.MEDIUM and 'activity_network' in data:
            saved_network = LSTMNetwork.from_dict(data['activity_network'])
            # Saves from older versions used an input size that did not match
            # the state vector; keep the freshly sized network in that case
            if saved_network.input_size == learner.activity_network.input_size:
                saved_network.set_sequence_length(SEQUENCE_LENGTH)
                learner.activity_network = saved_network

        elif complexity in (AIComplexity.ADVANCED, AIComplexity.EXPERT):
            if 'hiding_spots' in data:
                learner.hiding_spots = HidingSpotMemory.from_dict(data['hiding_spots'])

            if 'network_coordinator' in data:
                learner.network_coordinator = NetworkCoordinator.from_dict(data['network_coordinator'])

            if 'rl_system' in data:
                from .reinforcement_learning import ReinforcementLearningAgent
                saved_agent = ReinforcementLearningAgent.from_dict(data['rl_system'])
                # Saves from older versions used a state size that did not match
                # the state vector; keep the freshly sized agent in that case
                if saved_agent.state_size == learner.rl_system.rl_agent.state_size:
                    learner.rl_system.rl_agent = saved_agent

        if complexity == AIComplexity.EXPERT and 'learning_history' in data:
            learner.learning_history = data['learning_history']

        return learner
