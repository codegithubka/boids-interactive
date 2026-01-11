"""
Pydantic models for the Boids Interactive Demo.

Provides validation for simulation parameters, WebSocket messages,
and frame data serialization.
"""

from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, model_validator

from config import (
    PARAM_DEFINITIONS,
    DEFAULT_PARAMS,
    VALID_PRESETS,
    MessageType,
)


# =============================================================================
# Simulation Parameters
# =============================================================================

class SimulationParams(BaseModel):
    """Validated simulation parameters."""

    # Primary parameters
    num_boids: int = Field(
        default=DEFAULT_PARAMS["num_boids"],
        ge=PARAM_DEFINITIONS["num_boids"].min,
        le=PARAM_DEFINITIONS["num_boids"].max,
        description="Number of boids in simulation"
    )
    visual_range: float = Field(
        default=DEFAULT_PARAMS["visual_range"],
        ge=PARAM_DEFINITIONS["visual_range"].min,
        le=PARAM_DEFINITIONS["visual_range"].max,
        description="How far each boid can see"
    )
    separation_strength: float = Field(
        default=DEFAULT_PARAMS["separation_strength"],
        ge=PARAM_DEFINITIONS["separation_strength"].min,
        le=PARAM_DEFINITIONS["separation_strength"].max,
        description="Strength of separation behavior"
    )

    # Predator parameters
    predator_enabled: bool = Field(
        default=DEFAULT_PARAMS["predator_enabled"],
        description="Whether predator is active"
    )
    predator_speed: float = Field(
        default=DEFAULT_PARAMS["predator_speed"],
        ge=PARAM_DEFINITIONS["predator_speed"].min,
        le=PARAM_DEFINITIONS["predator_speed"].max,
        description="Predator maximum speed"
    )
    predator_avoidance_strength: float = Field(
        default=DEFAULT_PARAMS["predator_avoidance_strength"],
        ge=PARAM_DEFINITIONS["predator_avoidance_strength"].min,
        le=PARAM_DEFINITIONS["predator_avoidance_strength"].max,
        description="How strongly boids avoid predator"
    )

    # Advanced parameters
    protected_range: float = Field(
        default=DEFAULT_PARAMS["protected_range"],
        ge=PARAM_DEFINITIONS["protected_range"].min,
        le=PARAM_DEFINITIONS["protected_range"].max,
        description="Personal space for separation"
    )
    cohesion_factor: float = Field(
        default=DEFAULT_PARAMS["cohesion_factor"],
        ge=PARAM_DEFINITIONS["cohesion_factor"].min,
        le=PARAM_DEFINITIONS["cohesion_factor"].max,
        description="Strength of cohesion behavior"
    )
    alignment_factor: float = Field(
        default=DEFAULT_PARAMS["alignment_factor"],
        ge=PARAM_DEFINITIONS["alignment_factor"].min,
        le=PARAM_DEFINITIONS["alignment_factor"].max,
        description="Strength of alignment behavior"
    )
    max_speed: float = Field(
        default=DEFAULT_PARAMS["max_speed"],
        ge=PARAM_DEFINITIONS["max_speed"].min,
        le=PARAM_DEFINITIONS["max_speed"].max,
        description="Maximum boid speed"
    )
    min_speed: float = Field(
        default=DEFAULT_PARAMS["min_speed"],
        ge=PARAM_DEFINITIONS["min_speed"].min,
        le=PARAM_DEFINITIONS["min_speed"].max,
        description="Minimum boid speed"
    )
    margin: float = Field(
        default=DEFAULT_PARAMS["margin"],
        ge=PARAM_DEFINITIONS["margin"].min,
        le=PARAM_DEFINITIONS["margin"].max,
        description="Boundary margin for turning"
    )
    turn_factor: float = Field(
        default=DEFAULT_PARAMS["turn_factor"],
        ge=PARAM_DEFINITIONS["turn_factor"].min,
        le=PARAM_DEFINITIONS["turn_factor"].max,
        description="Boundary turn strength"
    )
    predator_detection_range: float = Field(
        default=DEFAULT_PARAMS["predator_detection_range"],
        ge=PARAM_DEFINITIONS["predator_detection_range"].min,
        le=PARAM_DEFINITIONS["predator_detection_range"].max,
        description="Predator detection distance"
    )
    predator_hunting_strength: float = Field(
        default=DEFAULT_PARAMS["predator_hunting_strength"],
        ge=PARAM_DEFINITIONS["predator_hunting_strength"].min,
        le=PARAM_DEFINITIONS["predator_hunting_strength"].max,
        description="Predator pursuit strength"
    )
    num_predators: int = Field(
        default=DEFAULT_PARAMS["num_predators"],
        ge=PARAM_DEFINITIONS["num_predators"].min,
        le=PARAM_DEFINITIONS["num_predators"].max,
        description="Number of predators (1-5)"
    )

    @model_validator(mode='after')
    def validate_speed_range(self):
        """Ensure min_speed <= max_speed."""
        if self.min_speed > self.max_speed:
            raise ValueError("min_speed must be <= max_speed")
        return self

    @model_validator(mode='after')
    def validate_range_hierarchy(self):
        """Ensure protected_range < visual_range."""
        if self.protected_range >= self.visual_range:
            raise ValueError("protected_range must be < visual_range")
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump()


# =============================================================================
# WebSocket Messages: Client -> Server
# =============================================================================

class UpdateParamsMessage(BaseModel):
    """Message to update simulation parameters."""
    type: Literal["update_params"] = MessageType.UPDATE_PARAMS
    params: Dict[str, Any] = Field(
        description="Partial parameter updates"
    )


class ResetMessage(BaseModel):
    """Message to reset simulation."""
    type: Literal["reset"] = MessageType.RESET


class PresetMessage(BaseModel):
    """Message to apply a preset."""
    type: Literal["preset"] = MessageType.PRESET
    name: str = Field(description="Preset name to apply")

    @model_validator(mode='after')
    def validate_preset_name(self):
        """Ensure preset name is valid."""
        if self.name not in VALID_PRESETS:
            raise ValueError(f"Invalid preset: {self.name}. Valid: {VALID_PRESETS}")
        return self


class PauseMessage(BaseModel):
    """Message to pause simulation."""
    type: Literal["pause"] = MessageType.PAUSE


class ResumeMessage(BaseModel):
    """Message to resume simulation."""
    type: Literal["resume"] = MessageType.RESUME


# =============================================================================
# WebSocket Messages: Server -> Client
# =============================================================================

class FrameMetrics(BaseModel):
    """Metrics included in frame data when predator is active."""
    fps: float = Field(description="Current frames per second")
    avg_distance_to_predator: Optional[float] = Field(
        default=None,
        description="Average boid distance to predator"
    )
    min_distance_to_predator: Optional[float] = Field(
        default=None,
        description="Minimum boid distance to predator"
    )
    flock_cohesion: Optional[float] = Field(
        default=None,
        description="Flock dispersion (std of positions)"
    )


class FrameData(BaseModel):
    """Frame data sent to client each tick."""
    type: Literal["frame"] = MessageType.FRAME
    frame_id: int = Field(description="Frame sequence number")
    boids: List[List[float]] = Field(
        description="List of [x, y, vx, vy] for each boid"
    )
    predator: Optional[List[float]] = Field(
        default=None,
        description="[x, y, vx, vy] of first predator (backward compat)"
    )
    predators: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of {x, y, vx, vy, strategy} for each predator"
    )
    obstacles: List[List[float]] = Field(
        default_factory=list,
        description="List of [x, y, radius] for each obstacle"
    )
    metrics: Optional[FrameMetrics] = Field(
        default=None,
        description="Metrics when predator is active"
    )


class ParamsSyncMessage(BaseModel):
    """Message to sync all parameters to client."""
    type: Literal["params_sync"] = MessageType.PARAMS_SYNC
    params: Dict[str, Any] = Field(
        description="All current parameter values"
    )


class ErrorMessage(BaseModel):
    """Error message sent to client."""
    type: Literal["error"] = MessageType.ERROR
    message: str = Field(description="Error description")


# =============================================================================
# Message Parsing Helper
# =============================================================================

def parse_client_message(data: Dict[str, Any]) -> Optional[BaseModel]:
    """
    Parse incoming WebSocket message from client.
    
    Returns the appropriate message model, or None if invalid.
    """
    msg_type = data.get("type")
    
    try:
        if msg_type == MessageType.UPDATE_PARAMS:
            return UpdateParamsMessage(**data)
        elif msg_type == MessageType.RESET:
            return ResetMessage(**data)
        elif msg_type == MessageType.PRESET:
            return PresetMessage(**data)
        elif msg_type == MessageType.PAUSE:
            return PauseMessage(**data)
        elif msg_type == MessageType.RESUME:
            return ResumeMessage(**data)
        else:
            return None
    except Exception:
        return None