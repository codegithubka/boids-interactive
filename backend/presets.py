"""
Preset configurations for the Boids Interactive Demo.

Defines parameter presets for interesting flock behaviors.
"""

from typing import Dict, Any, Optional

from config import DEFAULT_PARAMS, PresetName, VALID_PRESETS


# =============================================================================
# Preset Definitions
# =============================================================================

PRESETS: Dict[str, Dict[str, Any]] = {
    PresetName.DEFAULT: {
        **DEFAULT_PARAMS,
    },

    PresetName.TIGHT_SWARM: {
        **DEFAULT_PARAMS,
        "num_boids": 100,
        "visual_range": 80,
        "protected_range": 8,
        "cohesion_factor": 0.008,
        "alignment_factor": 0.1,
        "separation_strength": 0.2,
    },

    PresetName.LOOSE_CLOUD: {
        **DEFAULT_PARAMS,
        "num_boids": 75,
        "visual_range": 120,
        "protected_range": 25,
        "cohesion_factor": 0.0005,
        "alignment_factor": 0.03,
        "separation_strength": 0.08,
    },

    PresetName.HIGH_SPEED: {
        **DEFAULT_PARAMS,
        "num_boids": 60,
        "max_speed": 6.0,
        "min_speed": 4.0,
        "visual_range": 60,
        "turn_factor": 0.4,
        "alignment_factor": 0.12,
    },

    PresetName.SLOW_DANCE: {
        **DEFAULT_PARAMS,
        "num_boids": 40,
        "max_speed": 1.5,
        "min_speed": 0.8,
        "visual_range": 70,
        "cohesion_factor": 0.004,
        "alignment_factor": 0.08,
        "separation_strength": 0.1,
    },

    PresetName.PREDATOR_CHASE: {
        **DEFAULT_PARAMS,
        "num_boids": 80,
        "predator_enabled": True,
        "predator_speed": 3.0,
        "predator_avoidance_strength": 0.8,
        "predator_detection_range": 120,
        "predator_hunting_strength": 0.08,
        "max_speed": 4.0,
        "min_speed": 2.5,
    },

    PresetName.SWARM_DEFENSE: {
        **DEFAULT_PARAMS,
        "num_boids": 120,
        "predator_enabled": True,
        "predator_speed": 2.0,
        "predator_avoidance_strength": 1.2,
        "predator_detection_range": 150,
        "predator_hunting_strength": 0.03,
        "cohesion_factor": 0.006,
        "visual_range": 70,
        "separation_strength": 0.12,
    },
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_preset(name: str) -> Optional[Dict[str, Any]]:
    """
    Get a preset configuration by name.
    
    Args:
        name: Preset name (use PresetName constants)
        
    Returns:
        Dictionary of parameters, or None if not found
    """
    return PRESETS.get(name)


def get_preset_params(name: str) -> Dict[str, Any]:
    """
    Get a preset configuration, falling back to default.
    
    Args:
        name: Preset name
        
    Returns:
        Dictionary of parameters (default if name not found)
    """
    return PRESETS.get(name, PRESETS[PresetName.DEFAULT])


def is_valid_preset(name: str) -> bool:
    """Check if a preset name is valid."""
    return name in VALID_PRESETS


def list_presets() -> list:
    """Get list of all preset names."""
    return list(PRESETS.keys())