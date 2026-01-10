"""
Tests for preset configurations.
"""

import pytest

from presets import (
    PRESETS,
    get_preset,
    get_preset_params,
    is_valid_preset,
    list_presets,
)
from config import PresetName, DEFAULT_PARAMS, PARAM_DEFINITIONS


class TestPresetDefinitions:
    """Tests for preset definitions."""

    def test_all_presets_defined(self):
        """All 7 presets are defined."""
        assert len(PRESETS) == 7

    def test_default_preset_exists(self):
        """Default preset exists."""
        assert PresetName.DEFAULT in PRESETS

    def test_all_preset_names_exist(self):
        """All preset names have definitions."""
        expected = [
            PresetName.DEFAULT,
            PresetName.TIGHT_SWARM,
            PresetName.LOOSE_CLOUD,
            PresetName.HIGH_SPEED,
            PresetName.SLOW_DANCE,
            PresetName.PREDATOR_CHASE,
            PresetName.SWARM_DEFENSE,
        ]
        for name in expected:
            assert name in PRESETS, f"Missing preset: {name}"

    def test_presets_have_all_params(self):
        """Each preset has all 15 parameters."""
        for name, preset in PRESETS.items():
            for param in DEFAULT_PARAMS:
                assert param in preset, f"{name} missing param: {param}"

    def test_preset_values_within_limits(self):
        """All preset values are within valid limits."""
        for name, preset in PRESETS.items():
            for param, value in preset.items():
                if param == "predator_enabled":
                    continue  # Boolean, skip limit check
                defn = PARAM_DEFINITIONS[param]
                assert defn.min <= value <= defn.max, \
                    f"{name}.{param}={value} not in [{defn.min}, {defn.max}]"


class TestPresetCharacteristics:
    """Tests for specific preset characteristics."""

    def test_default_matches_defaults(self):
        """Default preset matches DEFAULT_PARAMS."""
        default = PRESETS[PresetName.DEFAULT]
        for param, value in DEFAULT_PARAMS.items():
            assert default[param] == value

    def test_tight_swarm_high_cohesion(self):
        """Tight swarm has high cohesion."""
        tight = PRESETS[PresetName.TIGHT_SWARM]
        default = PRESETS[PresetName.DEFAULT]
        assert tight["cohesion_factor"] > default["cohesion_factor"]

    def test_loose_cloud_low_cohesion(self):
        """Loose cloud has low cohesion."""
        loose = PRESETS[PresetName.LOOSE_CLOUD]
        default = PRESETS[PresetName.DEFAULT]
        assert loose["cohesion_factor"] < default["cohesion_factor"]

    def test_high_speed_fast(self):
        """High speed preset has higher speeds."""
        fast = PRESETS[PresetName.HIGH_SPEED]
        default = PRESETS[PresetName.DEFAULT]
        assert fast["max_speed"] > default["max_speed"]
        assert fast["min_speed"] > default["min_speed"]

    def test_slow_dance_slow(self):
        """Slow dance preset has lower speeds."""
        slow = PRESETS[PresetName.SLOW_DANCE]
        default = PRESETS[PresetName.DEFAULT]
        assert slow["max_speed"] < default["max_speed"]
        assert slow["min_speed"] < default["min_speed"]

    def test_predator_chase_has_predator(self):
        """Predator chase has predator enabled."""
        chase = PRESETS[PresetName.PREDATOR_CHASE]
        assert chase["predator_enabled"] is True

    def test_swarm_defense_has_predator(self):
        """Swarm defense has predator enabled."""
        defense = PRESETS[PresetName.SWARM_DEFENSE]
        assert defense["predator_enabled"] is True

    def test_default_no_predator(self):
        """Default preset has no predator."""
        default = PRESETS[PresetName.DEFAULT]
        assert default["predator_enabled"] is False


class TestGetPreset:
    """Tests for get_preset function."""

    def test_get_valid_preset(self):
        """Get valid preset returns dict."""
        preset = get_preset(PresetName.TIGHT_SWARM)
        assert preset is not None
        assert isinstance(preset, dict)

    def test_get_invalid_preset(self):
        """Get invalid preset returns None."""
        preset = get_preset("nonexistent")
        assert preset is None

    def test_get_preset_has_params(self):
        """Retrieved preset has all params."""
        preset = get_preset(PresetName.HIGH_SPEED)
        assert "num_boids" in preset
        assert "max_speed" in preset


class TestGetPresetParams:
    """Tests for get_preset_params function."""

    def test_valid_preset(self):
        """Valid preset returns its params."""
        params = get_preset_params(PresetName.LOOSE_CLOUD)
        assert params["cohesion_factor"] == PRESETS[PresetName.LOOSE_CLOUD]["cohesion_factor"]

    def test_invalid_preset_returns_default(self):
        """Invalid preset returns default params."""
        params = get_preset_params("nonexistent")
        assert params == PRESETS[PresetName.DEFAULT]


class TestIsValidPreset:
    """Tests for is_valid_preset function."""

    def test_valid_preset(self):
        """Valid preset name returns True."""
        assert is_valid_preset(PresetName.DEFAULT) is True
        assert is_valid_preset(PresetName.TIGHT_SWARM) is True

    def test_invalid_preset(self):
        """Invalid preset name returns False."""
        assert is_valid_preset("nonexistent") is False
        assert is_valid_preset("") is False


class TestListPresets:
    """Tests for list_presets function."""

    def test_returns_list(self):
        """Returns a list."""
        presets = list_presets()
        assert isinstance(presets, list)

    def test_contains_all_presets(self):
        """List contains all preset names."""
        presets = list_presets()
        assert len(presets) == 7
        assert PresetName.DEFAULT in presets
        assert PresetName.PREDATOR_CHASE in presets


if __name__ == "__main__":
    pytest.main([__file__, "-v"])