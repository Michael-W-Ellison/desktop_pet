"""
EXPERT-mode monitoring: detailed logging, learning metrics and decision tracking.

Feeds the "AI Insights" view, which shows what the pet's networks are doing.
"""
import logging
import os
import time
from collections import deque
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, List

from .config import APP_DIR

LOG_FILE = os.path.join(APP_DIR, "ai_expert.log")

# Entries kept for each metric and for decision tracking
METRIC_HISTORY = 500
DECISION_HISTORY = 100


def _get_logger() -> logging.Logger:
    """Logger writing to LOG_FILE (rotated at 1 MB, 3 backups)."""
    logger = logging.getLogger("desktop_pal.expert")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.propagate = False
        try:
            handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        except OSError:
            handler = logging.NullHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        logger.addHandler(handler)
    return logger


class ExpertMonitor:
    """Records learning metrics and decisions for EXPERT mode."""

    def __init__(self):
        self.logger = _get_logger()
        self.decision_times = deque(maxlen=METRIC_HISTORY)
        self.performance_metrics = {
            'decisions_per_minute': deque(maxlen=METRIC_HISTORY),
            'learning_rate_history': deque(maxlen=METRIC_HISTORY),
            'reward_history': deque(maxlen=METRIC_HISTORY),
            'exploration_rate': deque(maxlen=METRIC_HISTORY),
        }
        self.decisions = deque(maxlen=DECISION_HISTORY)

    def record_decision(self, decision: Dict[str, Any]):
        """Track a behavioral decision and log it."""
        now = time.time()
        self.decision_times.append(now)
        recent = [t for t in self.decision_times if now - t <= 60]
        self.performance_metrics['decisions_per_minute'].append(len(recent))

        emotions = decision.get('emotions', {})
        entry = {
            'time': now,
            'activity': decision.get('activity'),
            'decided_by': decision.get('decided_by'),
            'goal': decision.get('rl_goal'),
            'rl_action': (decision.get('rl_action') or {}).get('name'),
            'q_value': decision.get('rl_q_value'),
            'emotions': {k: round(v, 2) for k, v in emotions.items()},
            'interaction_probability': decision.get('player_prediction', {}).get('interaction_probability'),
            'velocity': (round(decision.get('velocity_x', 0), 2), round(decision.get('velocity_y', 0), 2)),
        }
        self.decisions.append(entry)
        self.logger.info("DECISION %s", entry)

    def record_learning(self, reward: float, learning_rate: float, exploration_rate: float,
                        decision_stability: float):
        """Track one learning step and log it."""
        self.performance_metrics['reward_history'].append(reward)
        self.performance_metrics['learning_rate_history'].append(learning_rate)
        self.performance_metrics['exploration_rate'].append(exploration_rate)
        self.logger.info("LEARN reward=%.3f lr=%.6f epsilon=%.3f stability=%.3f",
                         reward, learning_rate, exploration_rate, decision_stability)

    def record_interaction(self, interaction_type: str, enjoyed: bool):
        """Log a player interaction."""
        self.logger.info("INTERACTION %s enjoyed=%s", interaction_type, enjoyed)

    def summary(self) -> Dict[str, Any]:
        """Latest and average values of each metric."""
        result = {}
        for name, values in self.performance_metrics.items():
            values = list(values)
            result[name] = {
                'latest': values[-1] if values else None,
                'average': sum(values) / len(values) if values else None,
                'count': len(values),
            }
        return result

    def recent_decisions(self, count: int = 10) -> List[Dict[str, Any]]:
        return list(self.decisions)[-count:]


def bar(value: float, width: int = 20) -> str:
    """Text bar for a value in 0-1."""
    value = max(0.0, min(1.0, value))
    filled = int(round(value * width))
    return "█" * filled + "░" * (width - filled)
