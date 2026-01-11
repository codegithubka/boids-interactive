"""
Tests for multiple predator functionality.
"""

import pytest
from boids import FlockOptimized, SimulationParams


class TestMultiplePredatorsCreation:
    """Tests for creating multiple predators."""

    def test_default_single_predator(self):
        """Single predator created by default when enabled."""
        flock = FlockOptimized(num_boids=10, enable_predator=True)
        assert len(flock.predators) == 1
        assert flock.predator is not None

    def test_multiple_predators_on_init(self):
        """Multiple predators created on init."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=3)
        assert len(flock.predators) == 3

    def test_max_predators_clamped(self):
        """Predator count clamped to max 5."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=10)
        assert len(flock.predators) == 5

    def test_no_predators_when_disabled(self):
        """No predators when not enabled."""
        flock = FlockOptimized(num_boids=10, enable_predator=False, num_predators=3)
        assert len(flock.predators) == 0


class TestPredatorBackwardCompatibility:
    """Tests for backward compatibility with single predator."""

    def test_predator_property_returns_first(self):
        """predator property returns first predator."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=3)
        assert flock.predator is flock.predators[0]

    def test_predator_property_none_when_empty(self):
        """predator property returns None when no predators."""
        flock = FlockOptimized(num_boids=10, enable_predator=False)
        assert flock.predator is None

    def test_toggle_predator_adds_one(self):
        """toggle_predator adds single predator."""
        flock = FlockOptimized(num_boids=10, enable_predator=False)
        result = flock.toggle_predator()
        assert result is True
        assert len(flock.predators) == 1

    def test_toggle_predator_removes_all(self):
        """toggle_predator removes all predators."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=3)
        result = flock.toggle_predator()
        assert result is False
        assert len(flock.predators) == 0


class TestMultiplePredatorManagement:
    """Tests for predator management methods."""

    def test_add_predator(self):
        """add_predator adds a new predator."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=1)
        predator = flock.add_predator()
        assert predator is not None
        assert len(flock.predators) == 2

    def test_add_predator_max_limit(self):
        """add_predator returns None at max."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=5)
        predator = flock.add_predator()
        assert predator is None
        assert len(flock.predators) == 5

    def test_remove_predator_default_last(self):
        """remove_predator removes last by default."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=3)
        first_predator = flock.predators[0]
        result = flock.remove_predator()
        assert result is True
        assert len(flock.predators) == 2
        assert flock.predators[0] is first_predator

    def test_remove_predator_by_index(self):
        """remove_predator removes specific index."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=3)
        second_predator = flock.predators[1]
        result = flock.remove_predator(0)
        assert result is True
        assert len(flock.predators) == 2
        assert flock.predators[0] is second_predator

    def test_remove_predator_invalid_index(self):
        """remove_predator with invalid index returns False."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=2)
        assert flock.remove_predator(10) is False
        assert len(flock.predators) == 2

    def test_remove_predator_empty(self):
        """remove_predator on empty returns False."""
        flock = FlockOptimized(num_boids=10, enable_predator=False)
        assert flock.remove_predator() is False

    def test_set_num_predators_increase(self):
        """set_num_predators increases count."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=1)
        result = flock.set_num_predators(4)
        assert result == 4
        assert len(flock.predators) == 4

    def test_set_num_predators_decrease(self):
        """set_num_predators decreases count."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=4)
        result = flock.set_num_predators(2)
        assert result == 2
        assert len(flock.predators) == 2

    def test_set_num_predators_clamped(self):
        """set_num_predators clamps to 0-5."""
        flock = FlockOptimized(num_boids=10, enable_predator=True)
        assert flock.set_num_predators(-1) == 0
        assert flock.set_num_predators(10) == 5

    def test_get_predators_returns_copy(self):
        """get_predators returns a copy."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=2)
        predators = flock.get_predators()
        predators.clear()
        assert len(flock.predators) == 2

    def test_num_predators_property(self):
        """num_predators property works."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=3)
        assert flock.num_predators == 3


class TestMultiplePredatorSimulation:
    """Tests for simulation with multiple predators."""

    def test_simulation_runs_with_multiple_predators(self):
        """Simulation runs without errors with multiple predators."""
        params = SimulationParams(width=800, height=600)
        flock = FlockOptimized(num_boids=50, params=params, 
                              enable_predator=True, num_predators=3)
        
        # Run 50 frames
        for _ in range(50):
            flock.update()
        
        # Should complete without error
        assert len(flock.boids) == 50
        assert len(flock.predators) == 3

    def test_boids_avoid_multiple_predators(self):
        """Boids react to multiple predators."""
        params = SimulationParams(width=800, height=600)
        flock = FlockOptimized(num_boids=1, params=params, 
                              enable_predator=True, num_predators=2)
        
        # Place boid in center
        boid = flock.boids[0]
        boid.x = 400
        boid.y = 300
        boid.vx = 0
        boid.vy = 0
        
        # Place predators on either side
        flock.predators[0].x = 380
        flock.predators[0].y = 300
        flock.predators[1].x = 420
        flock.predators[1].y = 300
        
        # Update
        for _ in range(10):
            flock.update()
        
        # Boid should have moved (up or down to escape)
        assert abs(boid.y - 300) > 5

    def test_predators_move_independently(self):
        """Each predator moves independently."""
        params = SimulationParams(width=800, height=600)
        flock = FlockOptimized(num_boids=50, params=params, 
                              enable_predator=True, num_predators=2)
        
        # Record initial positions
        initial_pos1 = (flock.predators[0].x, flock.predators[0].y)
        initial_pos2 = (flock.predators[1].x, flock.predators[1].y)
        
        # Run simulation
        for _ in range(20):
            flock.update()
        
        # Both should have moved
        final_pos1 = (flock.predators[0].x, flock.predators[0].y)
        final_pos2 = (flock.predators[1].x, flock.predators[1].y)
        
        assert final_pos1 != initial_pos1
        assert final_pos2 != initial_pos2


class TestMultiplePredatorsWithObstacles:
    """Tests for multiple predators with obstacles."""

    def test_predators_avoid_obstacles(self):
        """Multiple predators avoid obstacles."""
        params = SimulationParams(width=800, height=600)
        flock = FlockOptimized(num_boids=20, params=params, 
                              enable_predator=True, num_predators=2)
        
        # Add obstacle
        flock.add_obstacle(400, 300, radius=50)
        
        # Place predators near obstacle
        flock.predators[0].x = 360
        flock.predators[0].y = 300
        flock.predators[1].x = 440
        flock.predators[1].y = 300
        
        # Run simulation
        for _ in range(50):
            flock.update()
        
        # Should complete without error
        assert len(flock.predators) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])