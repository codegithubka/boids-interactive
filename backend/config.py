"""
Configuration constants for the Boids Interactive Demo.

Defines parameter limits, defaults, validation helpers, and constants.
Single source of truth for both backend and frontend.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Any


# =============================================================================
# Simulation Constants
# =============================================================================

SIMULATION_WIDTH: int = 800
SIMULATION_HEIGHT: int = 600
TARGET_FPS: int = 60


# =============================================================================
# Parameter Definitions
# =============================================================================

@dataclass(frozen=True)
class ParamLimit:
    """Defines limits and metadata for a simulation parameter."""
    min: float
    max: float
    default: float
    step: float
    category: str  # 'primary', 'predator', 'advanced'
    label: str
    description: str


PARAM_DEFINITIONS: Dict[str, ParamLimit] = {
    # Primary parameters (always visible in UI)
    "num_boids": ParamLimit(
        min=1, max=200, default=50, step=1,
        category="primary",
        label="Number of Boids",
        description="Total number of boids in the simulation"
    ),
    "visual_range": ParamLimit(
        min=10, max=150, default=50, step=5,
        category="primary",
        label="Visual Range",
        description="How far each boid can see (pixels)"
    ),
    "separation_strength": ParamLimit(
        min=0.01, max=0.5, default=0.15, step=0.01,
        category="primary",
        label="Separation Strength",
        description="How strongly boids avoid each other"
    ),

    # Predator parameters
    "predator_enabled": ParamLimit(
        min=0, max=1, default=0, step=1,
        category="predator",
        label="Predator Enabled",
        description="Toggle predator on/off"
    ),
    "predator_speed": ParamLimit(
        min=0.5, max=5.0, default=2.5, step=0.1,
        category="predator",
        label="Predator Speed",
        description="Maximum speed of the predator"
    ),
    "predator_avoidance_strength": ParamLimit(
        min=0.05, max=1.5, default=0.5, step=0.05,
        category="predator",
        label="Avoidance Strength",
        description="How strongly boids flee from predator"
    ),

    # Advanced parameters (hidden by default in UI)
    "protected_range": ParamLimit(
        min=2, max=50, default=12, step=1,
        category="advanced",
        label="Protected Range",
        description="Personal space radius for separation (pixels)"
    ),
    "cohesion_factor": ParamLimit(
        min=0.0001, max=0.02, default=0.002, step=0.0005,
        category="advanced",
        label="Cohesion Factor",
        description="How strongly boids are attracted to flock center"
    ),
    "alignment_factor": ParamLimit(
        min=0.01, max=0.2, default=0.06, step=0.01,
        category="advanced",
        label="Alignment Factor",
        description="How strongly boids match neighbor velocities"
    ),
    "max_speed": ParamLimit(
        min=1.0, max=8.0, default=3.0, step=0.5,
        category="advanced",
        label="Max Speed",
        description="Maximum boid speed (pixels/frame)"
    ),
    "min_speed": ParamLimit(
        min=0.5, max=4.0, default=2.0, step=0.5,
        category="advanced",
        label="Min Speed",
        description="Minimum boid speed (pixels/frame)"
    ),
    "margin": ParamLimit(
        min=20, max=150, default=75, step=5,
        category="advanced",
        label="Boundary Margin",
        description="Distance from edge where boids start turning (pixels)"
    ),
    "turn_factor": ParamLimit(
        min=0.05, max=0.8, default=0.2, step=0.05,
        category="advanced",
        label="Turn Factor",
        description="Strength of boundary avoidance steering"
    ),
    "predator_detection_range": ParamLimit(
        min=30, max=250, default=100, step=10,
        category="advanced",
        label="Detection Range",
        description="Distance at which boids detect predator (pixels)"
    ),
    "predator_hunting_strength": ParamLimit(
        min=0.01, max=0.2, default=0.05, step=0.01,
        category="advanced",
        label="Hunting Strength",
        description="How aggressively predator pursues flock"
    ),
}


# =============================================================================
# Default Parameters
# =============================================================================

DEFAULT_PARAMS: Dict[str, Any] = {
    name: defn.default for name, defn in PARAM_DEFINITIONS.items()
}

# Convert predator_enabled to boolean
DEFAULT_PARAMS["predator_enabled"] = bool(DEFAULT_PARAMS["predator_enabled"])


# =============================================================================
# Parameter Categories
# =============================================================================

def get_params_by_category(category: str) -> Dict[str, ParamLimit]:
    """Get all parameters in a given category."""
    return {
        name: defn for name, defn in PARAM_DEFINITIONS.items()
        if defn.category == category
    }


PRIMARY_PARAMS = get_params_by_category("primary")
PREDATOR_PARAMS = get_params_by_category("predator")
ADVANCED_PARAMS = get_params_by_category("advanced")


# =============================================================================
# Validation Helpers
# =============================================================================

def validate_param(name: str, value: float) -> Tuple[bool, str]:
    """
    Validate a parameter value against its limits.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if name not in PARAM_DEFINITIONS:
        return False, f"Unknown parameter: {name}"

    defn = PARAM_DEFINITIONS[name]

    if value < defn.min:
        return False, f"{name} must be >= {defn.min}"

    if value > defn.max:
        return False, f"{name} must be <= {defn.max}"

    return True, ""


def clamp_param(name: str, value: float) -> float:
    """Clamp a parameter value to its valid range."""
    if name not in PARAM_DEFINITIONS:
        return value

    defn = PARAM_DEFINITIONS[name]
    return max(defn.min, min(defn.max, value))


def get_default(name: str) -> Any:
    """Get default value for a parameter."""
    return DEFAULT_PARAMS.get(name)


# =============================================================================
# WebSocket Message Types
# =============================================================================

class MessageType:
    """Constants for WebSocket message types."""

    # Client -> Server
    UPDATE_PARAMS = "update_params"
    RESET = "reset"
    PRESET = "preset"
    PAUSE = "pause"
    RESUME = "resume"
    ADD_OBSTACLE = "add_obstacle"
    REMOVE_OBSTACLE = "remove_obstacle"
    CLEAR_OBSTACLES = "clear_obstacles"

    # Server -> Client
    FRAME = "frame"
    PARAMS_SYNC = "params_sync"
    OBSTACLE_ADDED = "obstacle_added"
    OBSTACLE_REMOVED = "obstacle_removed"
    OBSTACLES_CLEARED = "obstacles_cleared"
    ERROR = "error"


# =============================================================================
# Preset Names
# =============================================================================

class PresetName:
    """Constants for preset names."""
    DEFAULT = "default"
    TIGHT_SWARM = "tight_swarm"
    LOOSE_CLOUD = "loose_cloud"
    HIGH_SPEED = "high_speed"
    SLOW_DANCE = "slow_dance"
    PREDATOR_CHASE = "predator_chase"
    SWARM_DEFENSE = "swarm_defense"


VALID_PRESETS = [
    PresetName.DEFAULT,
    PresetName.TIGHT_SWARM,
    PresetName.LOOSE_CLOUD,
    PresetName.HIGH_SPEED,
    PresetName.SLOW_DANCE,
    PresetName.PREDATOR_CHASE,
    PresetName.SWARM_DEFENSE,
]