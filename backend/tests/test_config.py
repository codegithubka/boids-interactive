"""
Tests for configuration module.
"""

import pytest
from config import (
    SIMULATION_WIDTH,
    SIMULATION_HEIGHT,
    TARGET_FPS,
    PARAM_DEFINITIONS,
    DEFAULT_PARAMS,
    PRIMARY_PARAMS,
    PREDATOR_PARAMS,
    ADVANCED_PARAMS,
    get_params_by_category,
    validate_param,
    clamp_param,
    get_default,
    MessageType,
    PresetName,
    VALID_PRESETS,
)


class TestSimulationConstants:
    """Tests for simulation constants."""

    def test_simulation_dimensions(self):
        """Simulation has valid dimensions."""
        assert SIMULATION_WIDTH == 800
        assert SIMULATION_HEIGHT == 600

    def test_target_fps(self):
        """Target FPS is 60."""
        assert TARGET_FPS == 60


class TestParamDefinitions:
    """Tests for parameter definitions."""

    def test_all_params_have_required_fields(self):
        """All parameters have required fields."""
        for name, defn in PARAM_DEFINITIONS.items():
            assert hasattr(defn, 'min'), f"{name} missing min"
            assert hasattr(defn, 'max'), f"{name} missing max"
            assert hasattr(defn, 'default'), f"{name} missing default"
            assert hasattr(defn, 'step'), f"{name} missing step"
            assert hasattr(defn, 'category'), f"{name} missing category"
            assert hasattr(defn, 'label'), f"{name} missing label"
            assert hasattr(defn, 'description'), f"{name} missing description"

    def test_defaults_within_limits(self):
        """All defaults are within min/max limits."""
        for name, defn in PARAM_DEFINITIONS.items():
            assert defn.min <= defn.default <= defn.max, \
                f"{name}: default {defn.default} not in [{defn.min}, {defn.max}]"

    def test_min_less_than_max(self):
        """Min is always less than max."""
        for name, defn in PARAM_DEFINITIONS.items():
            assert defn.min < defn.max, f"{name}: min >= max"

    def test_step_positive(self):
        """Step values are positive."""
        for name, defn in PARAM_DEFINITIONS.items():
            assert defn.step > 0, f"{name}: step <= 0"

    def test_valid_categories(self):
        """All categories are valid."""
        valid_categories = {'primary', 'predator', 'advanced'}
        for name, defn in PARAM_DEFINITIONS.items():
            assert defn.category in valid_categories, \
                f"{name}: invalid category '{defn.category}'"

    def test_expected_params_exist(self):
        """Expected parameters are defined."""
        expected = [
            'num_boids', 'visual_range', 'separation_strength',
            'predator_enabled', 'predator_speed', 'predator_avoidance_strength',
            'protected_range', 'cohesion_factor', 'alignment_factor',
            'max_speed', 'min_speed', 'margin', 'turn_factor',
            'predator_detection_range', 'predator_hunting_strength'
        ]
        for param in expected:
            assert param in PARAM_DEFINITIONS, f"Missing parameter: {param}"

    def test_param_count(self):
        """Correct number of parameters defined."""
        assert len(PARAM_DEFINITIONS) == 15


class TestDefaultParams:
    """Tests for default parameters."""

    def test_all_params_have_defaults(self):
        """All parameters have a default value."""
        for name in PARAM_DEFINITIONS:
            assert name in DEFAULT_PARAMS, f"Missing default for {name}"

    def test_predator_enabled_is_boolean(self):
        """predator_enabled default is a boolean."""
        assert isinstance(DEFAULT_PARAMS['predator_enabled'], bool)
        assert DEFAULT_PARAMS['predator_enabled'] is False

    def test_num_boids_default(self):
        """num_boids has expected default."""
        assert DEFAULT_PARAMS['num_boids'] == 50

    def test_visual_range_default(self):
        """visual_range has expected default."""
        assert DEFAULT_PARAMS['visual_range'] == 50


class TestParamCategories:
    """Tests for parameter categories."""

    def test_primary_params(self):
        """Primary parameters are correct."""
        assert 'num_boids' in PRIMARY_PARAMS
        assert 'visual_range' in PRIMARY_PARAMS
        assert 'separation_strength' in PRIMARY_PARAMS
        assert len(PRIMARY_PARAMS) == 3

    def test_predator_params(self):
        """Predator parameters are correct."""
        assert 'predator_enabled' in PREDATOR_PARAMS
        assert 'predator_speed' in PREDATOR_PARAMS
        assert 'predator_avoidance_strength' in PREDATOR_PARAMS
        assert len(PREDATOR_PARAMS) == 3

    def test_advanced_params(self):
        """Advanced parameters are correct."""
        assert 'protected_range' in ADVANCED_PARAMS
        assert 'cohesion_factor' in ADVANCED_PARAMS
        assert 'max_speed' in ADVANCED_PARAMS
        assert len(ADVANCED_PARAMS) == 9

    def test_all_params_categorized(self):
        """Every parameter is in exactly one category."""
        all_categorized = set(PRIMARY_PARAMS) | set(PREDATOR_PARAMS) | set(ADVANCED_PARAMS)
        all_defined = set(PARAM_DEFINITIONS)
        assert all_categorized == all_defined

    def test_get_params_by_category(self):
        """get_params_by_category works correctly."""
        primary = get_params_by_category('primary')
        assert 'num_boids' in primary
        assert 'predator_enabled' not in primary


class TestValidation:
    """Tests for validate_param function."""

    def test_valid_param(self):
        """Valid parameter passes validation."""
        is_valid, msg = validate_param('num_boids', 50)
        assert is_valid is True
        assert msg == ""

    def test_at_min(self):
        """Parameter at minimum is valid."""
        is_valid, msg = validate_param('num_boids', 1)
        assert is_valid is True

    def test_at_max(self):
        """Parameter at maximum is valid."""
        is_valid, msg = validate_param('num_boids', 200)
        assert is_valid is True

    def test_below_min(self):
        """Parameter below minimum fails."""
        is_valid, msg = validate_param('num_boids', 0)
        assert is_valid is False
        assert 'must be >=' in msg

    def test_above_max(self):
        """Parameter above maximum fails."""
        is_valid, msg = validate_param('num_boids', 300)
        assert is_valid is False
        assert 'must be <=' in msg

    def test_unknown_param(self):
        """Unknown parameter fails."""
        is_valid, msg = validate_param('unknown_param', 50)
        assert is_valid is False
        assert 'Unknown parameter' in msg


class TestClamp:
    """Tests for clamp_param function."""

    def test_within_range(self):
        """Value within range is unchanged."""
        assert clamp_param('num_boids', 50) == 50

    def test_below_min(self):
        """Value below min is clamped to min."""
        assert clamp_param('num_boids', -10) == 1

    def test_above_max(self):
        """Value above max is clamped to max."""
        assert clamp_param('num_boids', 500) == 200

    def test_unknown_param(self):
        """Unknown parameter returns original value."""
        assert clamp_param('unknown', 999) == 999


class TestGetDefault:
    """Tests for get_default function."""

    def test_known_param(self):
        """Get default for known parameter."""
        assert get_default('num_boids') == 50

    def test_unknown_param(self):
        """Get default for unknown parameter returns None."""
        assert get_default('unknown') is None


class TestMessageTypes:
    """Tests for message type constants."""

    def test_client_messages(self):
        """Client message types are defined."""
        assert MessageType.UPDATE_PARAMS == "update_params"
        assert MessageType.RESET == "reset"
        assert MessageType.PRESET == "preset"
        assert MessageType.PAUSE == "pause"
        assert MessageType.RESUME == "resume"

    def test_server_messages(self):
        """Server message types are defined."""
        assert MessageType.FRAME == "frame"
        assert MessageType.PARAMS_SYNC == "params_sync"
        assert MessageType.ERROR == "error"


class TestPresets:
    """Tests for preset constants."""

    def test_preset_names(self):
        """Preset names are defined."""
        assert PresetName.DEFAULT == "default"
        assert PresetName.TIGHT_SWARM == "tight_swarm"
        assert PresetName.PREDATOR_CHASE == "predator_chase"

    def test_valid_presets_list(self):
        """VALID_PRESETS contains all presets."""
        assert PresetName.DEFAULT in VALID_PRESETS
        assert PresetName.TIGHT_SWARM in VALID_PRESETS
        assert PresetName.LOOSE_CLOUD in VALID_PRESETS
        assert PresetName.HIGH_SPEED in VALID_PRESETS
        assert PresetName.SLOW_DANCE in VALID_PRESETS
        assert PresetName.PREDATOR_CHASE in VALID_PRESETS
        assert PresetName.SWARM_DEFENSE in VALID_PRESETS

    def test_preset_count(self):
        """Correct number of presets."""
        assert len(VALID_PRESETS) == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])