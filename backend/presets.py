"""
Preset configurations for the Boids Interactive Demo.

Each preset defines a complete set of simulation parameters
that create distinctive flock behaviors.
"""

from typing import Dict, Any, Optional

from backend.config import DEFAULT_PARAMS, PresetName, VALID_PRESETS
from models import SimulationParams


# =============================================================================
# Preset Definitions
# =============================================================================

PRESETS: Dict[str, Dict[str, Any]] = {
    PresetName.DEFAULT: {
        # All defaults - balanced flocking
        **DEFAULT_PARAMS
    },
    
    PresetName.TIGHT_SWARM: {
        # Dense ball formation
        **DEFAULT_PARAMS,
        "visual_range": 30,
        "cohesion_factor": 0.006,
        "separation_strength": 0.08,
        "protected_range": 8,  # Need to keep < visual_range
    },
    
    PresetName.LOOSE_CLOUD: {
        # Spread out, drifting
        **DEFAULT_PARAMS,
        "visual_range": 75,
        "cohesion_factor": 0.0006,
        "separation_strength": 0.3,
    },
    
    PresetName.HIGH_SPEED: {
        # Fast, chaotic movement
        **DEFAULT_PARAMS,
        "max_speed": 6.0,
        "min_speed": 4.0,
        "alignment_factor": 0.03,
    },
    
    PresetName.SLOW_DANCE: {
        # Graceful, synchronized
        **DEFAULT_PARAMS,
        "max_speed": 1.5,
        "min_speed": 1.0,
        "alignment_factor": 0.12,
    },
    
    PresetName.PREDATOR_CHASE: {
        # Dramatic chase scene
        **DEFAULT_PARAMS,
        "predator_enabled": True,
        "predator_speed": 3.5,
        "predator_avoidance_strength": 0.75,
    },
    
    PresetName.SWARM_DEFENSE: {
        # Tight flock under threat
        **DEFAULT_PARAMS,
        "predator_enabled": True,
        "cohesion_factor": 0.004,
        "predator_avoidance_strength": 0.4,
    },
}


# =============================================================================
# Preset Access Functions
# =============================================================================

def get_preset(name: str) -> Optional[SimulationParams]:
    """
    Get a preset by name.
    
    Args:
        name: Preset name (e.g., 'tight_swarm')
        
    Returns:
        SimulationParams with preset values, or None if not found
    """
    if name not in PRESETS:
        return None
    
    return SimulationParams(**PRESETS[name])


def get_preset_names() -> list[str]:
    """Get list of all available preset names."""
    return VALID_PRESETS.copy()


def get_preset_dict(name: str) -> Optional[Dict[str, Any]]:
    """
    Get raw preset dictionary by name.
    
    Args:
        name: Preset name
        
    Returns:
        Dict of parameter values, or None if not found
    """
    return PRESETS.get(name)


def is_valid_preset(name: str) -> bool:
    """Check if a preset name is valid."""
    return name in PRESETS