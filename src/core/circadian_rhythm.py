"""
Phase 8: Circadian Rhythm System

Manages natural sleep/wake cycles based on time of day.
"""
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum


class TimeOfDay(Enum):
    """Time of day periods."""
    NIGHT = "night"          # 0:00 - 6:00
    MORNING = "morning"      # 6:00 - 12:00
    AFTERNOON = "afternoon"  # 12:00 - 18:00
    EVENING = "evening"      # 18:00 - 24:00


class SleepState(Enum):
    """Sleep states."""
    AWAKE = "awake"
    DROWSY = "drowsy"
    LIGHT_SLEEP = "light_sleep"
    DEEP_SLEEP = "deep_sleep"
    REM_SLEEP = "rem_sleep"


class CircadianRhythm:
    """
    Manages natural sleep/wake cycles.

    Features:
    - Time-based sleep drive
    - Natural sleep/wake patterns
    - Sleep quality tracking
    - Nap scheduling
    - Sleep debt accumulation
    """

    def __init__(self, species_type: str = 'cat'):
        """
        Initialize circadian rhythm.

        Args:
            species_type: Type of species (affects sleep pattern)
        """
        self.species_type = species_type

        # Sleep state
        self.sleep_state = SleepState.AWAKE
        self.is_sleeping = False

        # Sleep drive (0-100, higher = more tired)
        self.sleep_drive = 0.0

        # Sleep debt (accumulated lack of sleep)
        self.sleep_debt_hours = 0.0

        # Sleep timing
        self.last_sleep_time = time.time()
        self.last_wake_time = time.time()
        self.current_sleep_start = None
        self.current_sleep_duration = 0.0

        # Sleep statistics
        self.total_sleep_hours = 0.0
        self.sleep_cycles_completed = 0
        self.total_naps = 0

        # Sleep preferences (species-dependent)
        self.preferred_sleep_time = self._get_preferred_sleep_time(species_type)
        self.daily_sleep_need = self._get_daily_sleep_need(species_type)

        # Sleep quality
        self.sleep_quality = 1.0  # 0-1 multiplier

    def _get_preferred_sleep_time(self, species: str) -> int:
        """
        Get preferred sleep time (hour of day, 0-23).

        Args:
            species: Species type

        Returns:
            Hour of day to prefer sleeping (0-23)
        """
        # Different species have different sleep patterns
        patterns = {
            'cat': 22,      # Cats sleep late evening
            'dog': 21,      # Dogs sleep evening
            'bird': 19,     # Birds sleep early
            'hamster': 8,   # Hamsters are nocturnal, sleep during day
            'rabbit': 20    # Rabbits sleep evening
        }
        return patterns.get(species, 22)

    def _get_daily_sleep_need(self, species: str) -> float:
        """
        Get daily sleep need in hours.

        Args:
            species: Species type

        Returns:
            Hours of sleep needed per day
        """
        needs = {
            'cat': 16.0,     # Cats sleep a lot
            'dog': 14.0,     # Dogs sleep quite a bit
            'bird': 12.0,    # Birds need moderate sleep
            'hamster': 14.0, # Hamsters sleep during day
            'rabbit': 8.0    # Rabbits sleep less
        }
        return needs.get(species, 14.0)

    def update(self, hours_elapsed: float, current_hour: int):
        """
        Update circadian rhythm.

        Args:
            hours_elapsed: Hours since last update
            current_hour: Current hour of day (0-23)
        """
        if self.is_sleeping:
            self._update_sleeping(hours_elapsed)
        else:
            self._update_awake(hours_elapsed, current_hour)

    def _update_awake(self, hours_elapsed: float, current_hour: int):
        """Update while awake."""
        # Sleep drive increases while awake
        drive_increase = hours_elapsed * 5.0  # 5 points per hour

        # Increased drive during preferred sleep time
        if self._is_preferred_sleep_time(current_hour):
            drive_increase *= 2.0

        self.sleep_drive = min(100.0, self.sleep_drive + drive_increase)

        # Accumulate sleep debt if not sleeping enough
        hours_since_sleep = (time.time() - self.last_sleep_time) / 3600.0
        if hours_since_sleep > 24.0:
            # Calculate sleep debt
            hours_awake_per_day = 24.0 - self.daily_sleep_need
            expected_sleep_in_period = (hours_since_sleep / 24.0) * self.daily_sleep_need
            actual_sleep = self.total_sleep_hours

            if actual_sleep < expected_sleep_in_period:
                self.sleep_debt_hours = expected_sleep_in_period - actual_sleep

    def _update_sleeping(self, hours_elapsed: float):
        """Update while sleeping."""
        # Sleep drive decreases while sleeping
        drive_decrease = hours_elapsed * 15.0 * self.sleep_quality  # 15 points per hour

        self.sleep_drive = max(0.0, self.sleep_drive - drive_decrease)

        # Track sleep duration
        self.current_sleep_duration += hours_elapsed
        self.total_sleep_hours += hours_elapsed

        # Pay off sleep debt
        if self.sleep_debt_hours > 0:
            debt_paid = min(self.sleep_debt_hours, hours_elapsed * self.sleep_quality)
            self.sleep_debt_hours = max(0.0, self.sleep_debt_hours - debt_paid)

        # Progress through sleep states
        self._progress_sleep_state()

    def _progress_sleep_state(self):
        """Progress through sleep states."""
        # Sleep cycle: Light -> Deep -> REM (repeats every ~90 minutes)
        sleep_minutes = self.current_sleep_duration * 60.0
        cycle_position = (sleep_minutes % 90.0) / 90.0

        if cycle_position < 0.2:
            self.sleep_state = SleepState.LIGHT_SLEEP
        elif cycle_position < 0.6:
            self.sleep_state = SleepState.DEEP_SLEEP
        else:
            self.sleep_state = SleepState.REM_SLEEP

        # Count completed cycles
        completed_cycles = int(sleep_minutes / 90.0)
        if completed_cycles > self.sleep_cycles_completed:
            self.sleep_cycles_completed = completed_cycles

    def _is_preferred_sleep_time(self, current_hour: int) -> bool:
        """Check if current time is preferred sleep time."""
        # 2-hour window around preferred time
        pref = self.preferred_sleep_time
        return (pref - 1) <= current_hour <= (pref + 1)

    def should_sleep(self, current_hour: int, energy: float) -> Tuple[bool, str]:
        """
        Determine if pet should sleep.

        Args:
            current_hour: Current hour of day (0-23)
            energy: Current energy level (0-100)

        Returns:
            Tuple of (should_sleep, reason)
        """
        # Very high sleep drive
        if self.sleep_drive > 90:
            return True, "exhausted"

        # High sleep drive during preferred sleep time
        if self.sleep_drive > 60 and self._is_preferred_sleep_time(current_hour):
            return True, "bedtime"

        # Low energy
        if energy < 20:
            return True, "tired"

        # Sleep debt
        if self.sleep_debt_hours > 8.0:
            return True, "sleep_deprived"

        # Night time and moderate tiredness
        if 0 <= current_hour < 6 and self.sleep_drive > 40:
            return True, "nighttime"

        return False, "not_tired"

    def fall_asleep(self):
        """Pet falls asleep."""
        if self.is_sleeping:
            return

        self.is_sleeping = True
        self.sleep_state = SleepState.LIGHT_SLEEP
        self.current_sleep_start = time.time()
        self.current_sleep_duration = 0.0
        self.last_sleep_time = time.time()

    def wake_up(self, natural: bool = True) -> Dict[str, Any]:
        """
        Pet wakes up.

        Args:
            natural: Whether waking naturally or forced

        Returns:
            Sleep session summary
        """
        if not self.is_sleeping:
            return {'was_sleeping': False}

        sleep_duration = self.current_sleep_duration

        # Calculate sleep quality
        quality_factors = []

        # Natural wake is better than forced
        if natural:
            quality_factors.append(1.0)
        else:
            quality_factors.append(0.6)

        # Completed sleep cycles improve quality
        if self.sleep_cycles_completed > 0:
            quality_factors.append(min(1.0, self.sleep_cycles_completed / 3.0))
        else:
            quality_factors.append(0.3)

        # Longer sleep is generally better (up to a point)
        if sleep_duration < 1.0:
            quality_factors.append(0.5)  # Too short
        elif sleep_duration < 4.0:
            quality_factors.append(0.8)
        elif sleep_duration < 10.0:
            quality_factors.append(1.0)  # Ideal
        else:
            quality_factors.append(0.7)  # Too long

        session_quality = sum(quality_factors) / len(quality_factors)

        # Determine if it was a nap or full sleep
        is_nap = sleep_duration < 2.0

        if is_nap:
            self.total_naps += 1

        # Wake up
        self.is_sleeping = False
        self.sleep_state = SleepState.AWAKE
        self.last_wake_time = time.time()
        self.current_sleep_start = None
        self.current_sleep_duration = 0.0

        return {
            'was_sleeping': True,
            'sleep_duration_hours': sleep_duration,
            'is_nap': is_nap,
            'sleep_quality': session_quality,
            'cycles_completed': self.sleep_cycles_completed,
            'natural_wake': natural,
            'energy_restored': sleep_duration * 10.0 * session_quality,  # Energy gain
            'happiness_change': 5.0 if session_quality > 0.7 else -2.0
        }

    def get_time_of_day(self, current_hour: int) -> TimeOfDay:
        """
        Get time of day category.

        Args:
            current_hour: Current hour (0-23)

        Returns:
            TimeOfDay enum
        """
        if 0 <= current_hour < 6:
            return TimeOfDay.NIGHT
        elif 6 <= current_hour < 12:
            return TimeOfDay.MORNING
        elif 12 <= current_hour < 18:
            return TimeOfDay.AFTERNOON
        else:
            return TimeOfDay.EVENING

    def get_sleepiness_level(self) -> str:
        """Get textual description of sleepiness."""
        if self.sleep_drive < 20:
            return "wide_awake"
        elif self.sleep_drive < 40:
            return "alert"
        elif self.sleep_drive < 60:
            return "getting_tired"
        elif self.sleep_drive < 80:
            return "tired"
        else:
            return "exhausted"

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive circadian rhythm status."""
        current_hour = datetime.now().hour

        status = {
            'is_sleeping': self.is_sleeping,
            'sleep_state': self.sleep_state.value,
            'sleep_drive': self.sleep_drive,
            'sleepiness_level': self.get_sleepiness_level(),
            'sleep_debt_hours': self.sleep_debt_hours,
            'sleep_quality': self.sleep_quality,
            'time_of_day': self.get_time_of_day(current_hour).value,
            'current_hour': current_hour,
            'preferred_sleep_time': self.preferred_sleep_time,
            'daily_sleep_need': self.daily_sleep_need,
            'total_sleep_hours': self.total_sleep_hours,
            'total_naps': self.total_naps,
            'sleep_cycles_completed': self.sleep_cycles_completed
        }

        if self.is_sleeping:
            status['current_sleep_duration'] = self.current_sleep_duration
        else:
            status['hours_since_sleep'] = (time.time() - self.last_sleep_time) / 3600.0
            status['hours_since_wake'] = (time.time() - self.last_wake_time) / 3600.0

        return status

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'species_type': self.species_type,
            'sleep_state': self.sleep_state.value,
            'is_sleeping': self.is_sleeping,
            'sleep_drive': self.sleep_drive,
            'sleep_debt_hours': self.sleep_debt_hours,
            'last_sleep_time': self.last_sleep_time,
            'last_wake_time': self.last_wake_time,
            'current_sleep_start': self.current_sleep_start,
            'current_sleep_duration': self.current_sleep_duration,
            'total_sleep_hours': self.total_sleep_hours,
            'sleep_cycles_completed': self.sleep_cycles_completed,
            'total_naps': self.total_naps,
            'preferred_sleep_time': self.preferred_sleep_time,
            'daily_sleep_need': self.daily_sleep_need,
            'sleep_quality': self.sleep_quality
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CircadianRhythm':
        """Deserialize from dictionary."""
        system = cls(species_type=data.get('species_type', 'cat'))
        system.sleep_state = SleepState(data.get('sleep_state', 'awake'))
        system.is_sleeping = data.get('is_sleeping', False)
        system.sleep_drive = data.get('sleep_drive', 0.0)
        system.sleep_debt_hours = data.get('sleep_debt_hours', 0.0)
        system.last_sleep_time = data.get('last_sleep_time', time.time())
        system.last_wake_time = data.get('last_wake_time', time.time())
        system.current_sleep_start = data.get('current_sleep_start')
        system.current_sleep_duration = data.get('current_sleep_duration', 0.0)
        system.total_sleep_hours = data.get('total_sleep_hours', 0.0)
        system.sleep_cycles_completed = data.get('sleep_cycles_completed', 0)
        system.total_naps = data.get('total_naps', 0)
        system.preferred_sleep_time = data.get('preferred_sleep_time', 22)
        system.daily_sleep_need = data.get('daily_sleep_need', 14.0)
        system.sleep_quality = data.get('sleep_quality', 1.0)
        return system
