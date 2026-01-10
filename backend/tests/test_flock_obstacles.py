"""
Tests for FlockOptimized obstacle integration.
"""

import pytest
from boids import FlockOptimized, SimulationParams, Obstacle


class TestFlockObstacleManagement:
    """Tests for obstacle add/remove/clear methods."""

    def test_initial_no_obstacles(self):
        """Flock starts with no obstacles."""
        flock = FlockOptimized(num_boids=10)
        assert len(flock.obstacles) == 0

    def test_add_obstacle(self):
        """Add obstacle creates and stores obstacle."""
        flock = FlockOptimized(num_boids=10)
        obs = flock.add_obstacle(100, 200, radius=30)
        
        assert len(flock.obstacles) == 1
        assert flock.obstacles[0].x == 100
        assert flock.obstacles[0].y == 200
        assert flock.obstacles[0].radius == 30
        assert obs is flock.obstacles[0]

    def test_add_multiple_obstacles(self):
        """Can add multiple obstacles."""
        flock = FlockOptimized(num_boids=10)
        flock.add_obstacle(100, 100)
        flock.add_obstacle(200, 200)
        flock.add_obstacle(300, 300)
        
        assert len(flock.obstacles) == 3

    def test_add_obstacle_default_radius(self):
        """Add obstacle uses default radius."""
        flock = FlockOptimized(num_boids=10)
        obs = flock.add_obstacle(100, 100)
        
        assert obs.radius == 30.0

    def test_remove_obstacle_valid(self):
        """Remove obstacle by valid index."""
        flock = FlockOptimized(num_boids=10)
        flock.add_obstacle(100, 100)
        flock.add_obstacle(200, 200)
        
        result = flock.remove_obstacle(0)
        
        assert result is True
        assert len(flock.obstacles) == 1
        assert flock.obstacles[0].x == 200

    def test_remove_obstacle_invalid(self):
        """Remove obstacle with invalid index returns False."""
        flock = FlockOptimized(num_boids=10)
        flock.add_obstacle(100, 100)
        
        assert flock.remove_obstacle(-1) is False
        assert flock.remove_obstacle(1) is False
        assert flock.remove_obstacle(100) is False
        assert len(flock.obstacles) == 1

    def test_clear_obstacles(self):
        """Clear removes all obstacles."""
        flock = FlockOptimized(num_boids=10)
        flock.add_obstacle(100, 100)
        flock.add_obstacle(200, 200)
        flock.add_obstacle(300, 300)
        
        count = flock.clear_obstacles()
        
        assert count == 3
        assert len(flock.obstacles) == 0

    def test_clear_empty(self):
        """Clear on empty list returns 0."""
        flock = FlockOptimized(num_boids=10)
        count = flock.clear_obstacles()
        assert count == 0

    def test_get_obstacles_returns_copy(self):
        """get_obstacles returns a copy, not the original list."""
        flock = FlockOptimized(num_boids=10)
        flock.add_obstacle(100, 100)
        
        obstacles = flock.get_obstacles()
        obstacles.append(Obstacle(x=999, y=999))
        
        assert len(flock.obstacles) == 1


class TestFlockObstacleAvoidance:
    """Tests for obstacle avoidance behavior."""

    def test_boid_avoids_obstacle(self):
        """Boid near obstacle is pushed away."""
        params = SimulationParams(width=800, height=600)
        flock = FlockOptimized(num_boids=1, params=params)
        
        # Place boid near obstacle
        boid = flock.boids[0]
        boid.x = 100
        boid.y = 100
        boid.vx = 0
        boid.vy = 0
        
        # Place obstacle to the left
        flock.add_obstacle(60, 100, radius=30)
        
        # Update
        for _ in range(10):
            flock.update()
        
        # Boid should have moved right (away from obstacle)
        assert boid.x > 100

    def test_multiple_obstacles_avoidance(self):
        """Boid avoids multiple obstacles."""
        params = SimulationParams(width=800, height=600)
        flock = FlockOptimized(num_boids=1, params=params)
        
        boid = flock.boids[0]
        boid.x = 400
        boid.y = 300
        boid.vx = 0
        boid.vy = 0
        
        # Obstacles on left and right
        flock.add_obstacle(350, 300, radius=30)  # Left
        flock.add_obstacle(450, 300, radius=30)  # Right
        
        # Update - boid should move up or down
        for _ in range(20):
            flock.update()
        
        # Y position should have changed significantly
        assert abs(boid.y - 300) > 10

    def test_simulation_runs_with_obstacles(self):
        """Full simulation runs without errors with obstacles."""
        params = SimulationParams(width=800, height=600)
        flock = FlockOptimized(num_boids=50, params=params, enable_predator=True)
        
        # Add several obstacles
        flock.add_obstacle(200, 200, radius=40)
        flock.add_obstacle(400, 300, radius=50)
        flock.add_obstacle(600, 400, radius=30)
        
        # Run 100 frames
        for _ in range(100):
            flock.update()
        
        # Should complete without error
        assert len(flock.boids) == 50


class TestPredatorObstacleAvoidance:
    """Tests for predator obstacle avoidance."""

    def test_predator_avoids_obstacle(self):
        """Predator avoids obstacles while hunting."""
        params = SimulationParams(width=800, height=600)
        flock = FlockOptimized(num_boids=10, params=params, enable_predator=True)
        
        # Place predator near obstacle
        predator = flock.predator
        predator.x = 100
        predator.y = 100
        
        # Obstacle right next to predator
        flock.add_obstacle(80, 100, radius=30)
        
        initial_x = predator.x
        
        # Update
        for _ in range(10):
            flock.update()
        
        # Predator should have moved (away from obstacle or toward prey)
        assert predator.x != initial_x or predator.y != 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])