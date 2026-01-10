"""
Tests for SimulationManager.
"""

import pytest
import numpy as np

from simulation_manager import SimulationManager
from models import SimulationParams, FrameData, FrameMetrics


class TestSimulationManagerInit:
    """Tests for SimulationManager initialization."""

    def test_default_initialization(self):
        """Default initialization works."""
        manager = SimulationManager()
        assert manager.num_boids == 50
        assert manager.has_predator is False
        assert manager.frame_id == 0

    def test_custom_params(self):
        """Custom parameters are applied."""
        params = SimulationParams(num_boids=100, visual_range=75)
        manager = SimulationManager(params=params)
        assert manager.num_boids == 100

    def test_with_seed_reproducible(self):
        """Seeded initialization is reproducible."""
        manager1 = SimulationManager(seed=42)
        manager2 = SimulationManager(seed=42)
        
        # Get first boid positions
        frame1 = manager1.get_frame_data()
        frame2 = manager2.get_frame_data()
        
        assert frame1.boids[0] == frame2.boids[0]

    def test_default_not_running(self):
        """Manager starts not running."""
        manager = SimulationManager()
        assert manager.is_running is False

    def test_default_not_paused(self):
        """Manager starts not paused."""
        manager = SimulationManager()
        assert manager.is_paused is False

    def test_with_predator_enabled(self):
        """Predator can be enabled at init."""
        params = SimulationParams(predator_enabled=True)
        manager = SimulationManager(params=params)
        assert manager.has_predator is True


class TestSimulationManagerLifecycle:
    """Tests for start/stop/pause/resume."""

    def test_start(self):
        """Start sets running flag."""
        manager = SimulationManager()
        manager.start()
        assert manager.is_running is True

    def test_stop(self):
        """Stop clears running flag."""
        manager = SimulationManager()
        manager.start()
        manager.stop()
        assert manager.is_running is False

    def test_pause(self):
        """Pause sets paused flag."""
        manager = SimulationManager()
        manager.start()
        manager.pause()
        assert manager.is_paused is True

    def test_resume(self):
        """Resume clears paused flag."""
        manager = SimulationManager()
        manager.start()
        manager.pause()
        manager.resume()
        assert manager.is_paused is False


class TestSimulationManagerUpdate:
    """Tests for simulation update."""

    def test_update_increments_frame_id(self):
        """Update increments frame ID."""
        manager = SimulationManager(seed=42)
        assert manager.frame_id == 0
        manager.update()
        assert manager.frame_id == 1
        manager.update()
        assert manager.frame_id == 2

    def test_update_changes_positions(self):
        """Update changes boid positions."""
        manager = SimulationManager(seed=42)
        frame1 = manager.get_frame_data()
        initial_pos = frame1.boids[0][:2]  # x, y
        
        manager.update()
        
        frame2 = manager.get_frame_data()
        new_pos = frame2.boids[0][:2]
        
        # At least one coordinate should change
        assert initial_pos != new_pos

    def test_paused_no_frame_increment(self):
        """Paused update does not increment frame."""
        manager = SimulationManager(seed=42)
        manager.pause()
        manager.update()
        assert manager.frame_id == 0

    def test_paused_no_position_change(self):
        """Paused update does not move boids."""
        manager = SimulationManager(seed=42)
        frame1 = manager.get_frame_data()
        initial_pos = frame1.boids[0]
        
        manager.pause()
        manager.update()
        
        frame2 = manager.get_frame_data()
        assert frame2.boids[0] == initial_pos


class TestSimulationManagerReset:
    """Tests for simulation reset."""

    def test_reset_resets_frame_id(self):
        """Reset sets frame ID to 0."""
        manager = SimulationManager(seed=42)
        manager.update()
        manager.update()
        assert manager.frame_id == 2
        
        manager.reset()
        assert manager.frame_id == 0

    def test_reset_recreates_boids(self):
        """Reset creates new boid positions."""
        manager = SimulationManager()  # No seed = random
        frame1 = manager.get_frame_data()
        initial_pos = frame1.boids[0][:2]
        
        manager.reset()
        
        frame2 = manager.get_frame_data()
        # Positions should be different (extremely unlikely to be same)
        assert frame2.boids[0][:2] != initial_pos

    def test_reset_preserves_params(self):
        """Reset preserves current parameters."""
        params = SimulationParams(num_boids=75)
        manager = SimulationManager(params=params)
        manager.reset()
        assert manager.num_boids == 75


class TestSimulationManagerParams:
    """Tests for parameter updates."""

    def test_update_params_basic(self):
        """Basic parameter update works."""
        manager = SimulationManager()
        manager.update_params({"visual_range": 80})
        
        params = manager.get_params()
        assert params.visual_range == 80

    def test_update_num_boids_recreates(self):
        """Changing num_boids recreates flock."""
        manager = SimulationManager()
        assert manager.num_boids == 50
        
        manager.update_params({"num_boids": 100})
        assert manager.num_boids == 100

    def test_enable_predator(self):
        """Enabling predator works."""
        manager = SimulationManager()
        assert manager.has_predator is False
        
        manager.update_params({"predator_enabled": True})
        assert manager.has_predator is True

    def test_disable_predator(self):
        """Disabling predator works."""
        params = SimulationParams(predator_enabled=True)
        manager = SimulationManager(params=params)
        assert manager.has_predator is True
        
        manager.update_params({"predator_enabled": False})
        assert manager.has_predator is False

    def test_get_params_dict(self):
        """get_params_dict returns all params."""
        manager = SimulationManager()
        d = manager.get_params_dict()
        
        assert isinstance(d, dict)
        assert 'num_boids' in d
        assert 'predator_enabled' in d
        assert len(d) == 15

    def test_invalid_params_ignored(self):
        """Invalid parameter updates are ignored."""
        manager = SimulationManager()
        original_boids = manager.num_boids
        
        # Try to set invalid value
        manager.update_params({"num_boids": 9999})
        
        # Should keep original value
        assert manager.num_boids == original_boids


class TestSimulationManagerFrameData:
    """Tests for frame data generation."""

    def test_frame_data_structure(self):
        """Frame data has correct structure."""
        manager = SimulationManager(seed=42)
        frame = manager.get_frame_data()
        
        assert isinstance(frame, FrameData)
        assert frame.frame_id == 0
        assert isinstance(frame.boids, list)
        assert len(frame.boids) == 50

    def test_boids_format(self):
        """Boids are [x, y, vx, vy] format."""
        manager = SimulationManager(seed=42)
        frame = manager.get_frame_data()
        
        boid = frame.boids[0]
        assert len(boid) == 4
        assert all(isinstance(v, float) for v in boid)

    def test_no_predator_when_disabled(self):
        """No predator data when disabled."""
        manager = SimulationManager()
        frame = manager.get_frame_data()
        
        assert frame.predator is None

    def test_predator_when_enabled(self):
        """Predator data present when enabled."""
        params = SimulationParams(predator_enabled=True)
        manager = SimulationManager(params=params, seed=42)
        frame = manager.get_frame_data()
        
        assert frame.predator is not None
        assert len(frame.predator) == 4

    def test_metrics_always_present(self):
        """Metrics always present."""
        manager = SimulationManager()
        frame = manager.get_frame_data()
        
        assert frame.metrics is not None
        assert frame.metrics.fps > 0

    def test_metrics_with_predator(self):
        """Metrics include predator stats when predator active."""
        params = SimulationParams(predator_enabled=True)
        manager = SimulationManager(params=params, seed=42)
        manager.update()  # Need at least one frame
        frame = manager.get_frame_data()
        
        assert frame.metrics.avg_distance_to_predator is not None
        assert frame.metrics.min_distance_to_predator is not None
        assert frame.metrics.flock_cohesion is not None

    def test_metrics_without_predator(self):
        """Metrics don't include predator stats when predator inactive."""
        manager = SimulationManager()
        frame = manager.get_frame_data()
        
        assert frame.metrics.fps > 0
        assert frame.metrics.avg_distance_to_predator is None


class TestSimulationManagerProperties:
    """Tests for manager properties."""

    def test_fps_property(self):
        """FPS property returns reasonable value."""
        manager = SimulationManager()
        assert manager.fps > 0

    def test_num_boids_property(self):
        """num_boids property matches param."""
        params = SimulationParams(num_boids=75)
        manager = SimulationManager(params=params)
        assert manager.num_boids == 75

    def test_has_predator_property(self):
        """has_predator property matches state."""
        manager = SimulationManager()
        assert manager.has_predator is False
        
        params = SimulationParams(predator_enabled=True)
        manager2 = SimulationManager(params=params)
        assert manager2.has_predator is True


class TestSimulationManagerObstacles:
    """Tests for SimulationManager obstacle methods."""

    def test_add_obstacle(self):
        """Add obstacle returns obstacle data."""
        manager = SimulationManager()
        result = manager.add_obstacle(100, 200, radius=40)
        
        assert result['index'] == 0
        assert result['x'] == 100
        assert result['y'] == 200
        assert result['radius'] == 40

    def test_add_multiple_obstacles(self):
        """Add multiple obstacles."""
        manager = SimulationManager()
        obs1 = manager.add_obstacle(100, 100)
        obs2 = manager.add_obstacle(200, 200)
        
        assert obs1['index'] == 0
        assert obs2['index'] == 1
        assert manager.num_obstacles == 2

    def test_remove_obstacle(self):
        """Remove obstacle by index."""
        manager = SimulationManager()
        manager.add_obstacle(100, 100)
        manager.add_obstacle(200, 200)
        
        result = manager.remove_obstacle(0)
        
        assert result is True
        assert manager.num_obstacles == 1

    def test_remove_invalid_index(self):
        """Remove with invalid index returns False."""
        manager = SimulationManager()
        manager.add_obstacle(100, 100)
        
        assert manager.remove_obstacle(5) is False
        assert manager.num_obstacles == 1

    def test_clear_obstacles(self):
        """Clear all obstacles."""
        manager = SimulationManager()
        manager.add_obstacle(100, 100)
        manager.add_obstacle(200, 200)
        manager.add_obstacle(300, 300)
        
        count = manager.clear_obstacles()
        
        assert count == 3
        assert manager.num_obstacles == 0

    def test_get_obstacles(self):
        """Get obstacles returns list."""
        manager = SimulationManager()
        manager.add_obstacle(100, 100, radius=30)
        manager.add_obstacle(200, 200, radius=40)
        
        obstacles = manager.get_obstacles()
        
        assert len(obstacles) == 2
        assert obstacles[0]['x'] == 100
        assert obstacles[1]['radius'] == 40

    def test_frame_data_includes_obstacles(self):
        """Frame data includes obstacles."""
        manager = SimulationManager()
        manager.add_obstacle(100, 100, radius=30)
        manager.add_obstacle(200, 200, radius=40)
        
        frame = manager.get_frame_data()
        
        assert len(frame.obstacles) == 2
        assert frame.obstacles[0] == [100, 100, 30]
        assert frame.obstacles[1] == [200, 200, 40]

    def test_frame_data_empty_obstacles(self):
        """Frame data has empty obstacles list when none."""
        manager = SimulationManager()
        frame = manager.get_frame_data()
        
        assert frame.obstacles == []

    def test_num_obstacles_property(self):
        """num_obstacles property works."""
        manager = SimulationManager()
        assert manager.num_obstacles == 0
        
        manager.add_obstacle(100, 100)
        assert manager.num_obstacles == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])