"""
Tests for Pydantic models.
"""

import pytest
from pydantic import ValidationError

from models import (
    SimulationParams,
    UpdateParamsMessage,
    ResetMessage,
    PresetMessage,
    PauseMessage,
    ResumeMessage,
    FrameMetrics,
    FrameData,
    ParamsSyncMessage,
    ErrorMessage,
    parse_client_message,
)
from config import DEFAULT_PARAMS, MessageType


class TestSimulationParams:
    """Tests for SimulationParams model."""

    def test_default_values(self):
        """Default values are applied correctly."""
        params = SimulationParams()
        assert params.num_boids == 50
        assert params.visual_range == 50
        assert params.predator_enabled is False

    def test_custom_values(self):
        """Custom values are accepted."""
        params = SimulationParams(num_boids=100, visual_range=75)
        assert params.num_boids == 100
        assert params.visual_range == 75

    def test_num_boids_min(self):
        """num_boids at minimum is valid."""
        params = SimulationParams(num_boids=1)
        assert params.num_boids == 1

    def test_num_boids_max(self):
        """num_boids at maximum is valid."""
        params = SimulationParams(num_boids=200)
        assert params.num_boids == 200

    def test_num_boids_below_min_rejected(self):
        """num_boids below minimum is rejected."""
        with pytest.raises(ValidationError):
            SimulationParams(num_boids=0)

    def test_num_boids_above_max_rejected(self):
        """num_boids above maximum is rejected."""
        with pytest.raises(ValidationError):
            SimulationParams(num_boids=300)

    def test_speed_range_valid(self):
        """Valid speed range is accepted."""
        params = SimulationParams(min_speed=1.5, max_speed=4.0)
        assert params.min_speed == 1.5
        assert params.max_speed == 4.0

    def test_speed_range_equal_valid(self):
        """Equal min and max speed is valid."""
        params = SimulationParams(min_speed=2.0, max_speed=2.0)
        assert params.min_speed == params.max_speed

    def test_speed_range_invalid(self):
        """min_speed > max_speed is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SimulationParams(min_speed=4.0, max_speed=2.0)
        assert "min_speed must be <= max_speed" in str(exc_info.value)

    def test_range_hierarchy_valid(self):
        """protected_range < visual_range is valid."""
        params = SimulationParams(protected_range=10, visual_range=50)
        assert params.protected_range < params.visual_range

    def test_range_hierarchy_invalid(self):
        """protected_range >= visual_range is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SimulationParams(protected_range=50, visual_range=30)
        assert "protected_range must be < visual_range" in str(exc_info.value)

    def test_to_dict(self):
        """to_dict returns all parameters."""
        params = SimulationParams()
        d = params.to_dict()
        assert isinstance(d, dict)
        assert 'num_boids' in d
        assert 'predator_enabled' in d
        assert len(d) == 15


class TestUpdateParamsMessage:
    """Tests for UpdateParamsMessage."""

    def test_valid_message(self):
        """Valid update message is accepted."""
        msg = UpdateParamsMessage(params={"num_boids": 75})
        assert msg.type == "update_params"
        assert msg.params["num_boids"] == 75

    def test_empty_params(self):
        """Empty params dict is valid."""
        msg = UpdateParamsMessage(params={})
        assert msg.params == {}

    def test_multiple_params(self):
        """Multiple params are accepted."""
        msg = UpdateParamsMessage(params={
            "num_boids": 100,
            "visual_range": 60,
            "predator_enabled": True
        })
        assert len(msg.params) == 3


class TestResetMessage:
    """Tests for ResetMessage."""

    def test_valid_message(self):
        """Valid reset message is accepted."""
        msg = ResetMessage()
        assert msg.type == "reset"


class TestPresetMessage:
    """Tests for PresetMessage."""

    def test_valid_preset(self):
        """Valid preset name is accepted."""
        msg = PresetMessage(name="tight_swarm")
        assert msg.type == "preset"
        assert msg.name == "tight_swarm"

    def test_all_presets_valid(self):
        """All defined presets are valid."""
        presets = ["default", "tight_swarm", "loose_cloud", 
                   "high_speed", "slow_dance", "predator_chase", "swarm_defense"]
        for preset in presets:
            msg = PresetMessage(name=preset)
            assert msg.name == preset

    def test_invalid_preset(self):
        """Invalid preset name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PresetMessage(name="invalid_preset")
        assert "Invalid preset" in str(exc_info.value)


class TestPauseResumeMessages:
    """Tests for PauseMessage and ResumeMessage."""

    def test_pause_message(self):
        """Pause message is valid."""
        msg = PauseMessage()
        assert msg.type == "pause"

    def test_resume_message(self):
        """Resume message is valid."""
        msg = ResumeMessage()
        assert msg.type == "resume"


class TestFrameMetrics:
    """Tests for FrameMetrics."""

    def test_basic_metrics(self):
        """Basic metrics are accepted."""
        metrics = FrameMetrics(fps=60.0)
        assert metrics.fps == 60.0
        assert metrics.avg_distance_to_predator is None

    def test_full_metrics(self):
        """Full metrics with predator data."""
        metrics = FrameMetrics(
            fps=60.0,
            avg_distance_to_predator=150.5,
            min_distance_to_predator=45.2,
            flock_cohesion=32.1
        )
        assert metrics.fps == 60.0
        assert metrics.avg_distance_to_predator == 150.5


class TestFrameData:
    """Tests for FrameData."""

    def test_minimal_frame(self):
        """Minimal frame data is valid."""
        frame = FrameData(
            frame_id=1,
            boids=[[100, 200, 1.5, -0.5]]
        )
        assert frame.type == "frame"
        assert frame.frame_id == 1
        assert len(frame.boids) == 1
        assert frame.predator is None

    def test_frame_with_predator(self):
        """Frame with predator is valid."""
        frame = FrameData(
            frame_id=100,
            boids=[[100, 200, 1.5, -0.5], [150, 250, -1.0, 2.0]],
            predator=[400, 300, 0.5, 0.5]
        )
        assert frame.predator == [400, 300, 0.5, 0.5]
        assert len(frame.boids) == 2

    def test_frame_with_metrics(self):
        """Frame with metrics is valid."""
        frame = FrameData(
            frame_id=50,
            boids=[],
            predator=[400, 300, 0.5, 0.5],
            metrics=FrameMetrics(fps=60.0, avg_distance_to_predator=120.0)
        )
        assert frame.metrics.fps == 60.0


class TestParamsSyncMessage:
    """Tests for ParamsSyncMessage."""

    def test_valid_sync(self):
        """Valid sync message is accepted."""
        msg = ParamsSyncMessage(params=DEFAULT_PARAMS)
        assert msg.type == "params_sync"
        assert "num_boids" in msg.params


class TestErrorMessage:
    """Tests for ErrorMessage."""

    def test_error_message(self):
        """Error message is valid."""
        msg = ErrorMessage(message="Something went wrong")
        assert msg.type == "error"
        assert msg.message == "Something went wrong"


class TestParseClientMessage:
    """Tests for parse_client_message helper."""

    def test_parse_update_params(self):
        """Parse update_params message."""
        data = {"type": "update_params", "params": {"num_boids": 75}}
        msg = parse_client_message(data)
        assert isinstance(msg, UpdateParamsMessage)
        assert msg.params["num_boids"] == 75

    def test_parse_reset(self):
        """Parse reset message."""
        data = {"type": "reset"}
        msg = parse_client_message(data)
        assert isinstance(msg, ResetMessage)

    def test_parse_preset(self):
        """Parse preset message."""
        data = {"type": "preset", "name": "tight_swarm"}
        msg = parse_client_message(data)
        assert isinstance(msg, PresetMessage)
        assert msg.name == "tight_swarm"

    def test_parse_pause(self):
        """Parse pause message."""
        data = {"type": "pause"}
        msg = parse_client_message(data)
        assert isinstance(msg, PauseMessage)

    def test_parse_resume(self):
        """Parse resume message."""
        data = {"type": "resume"}
        msg = parse_client_message(data)
        assert isinstance(msg, ResumeMessage)

    def test_parse_unknown_type(self):
        """Unknown message type returns None."""
        data = {"type": "unknown"}
        msg = parse_client_message(data)
        assert msg is None

    def test_parse_invalid_data(self):
        """Invalid data returns None."""
        data = {"type": "preset", "name": "invalid"}
        msg = parse_client_message(data)
        assert msg is None

    def test_parse_missing_type(self):
        """Missing type returns None."""
        data = {"params": {}}
        msg = parse_client_message(data)
        assert msg is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])