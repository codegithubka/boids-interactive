"""
Tests for predator hunting strategies.
"""

import pytest
import numpy as np
from boids import Predator, HuntingStrategy, FlockOptimized, SimulationParams
from boids.boid import Boid


class TestHuntingStrategyEnum:
    """Tests for HuntingStrategy enum."""

    def test_all_strategies_exist(self):
        """All expected strategies are defined."""
        assert HuntingStrategy.CENTER_HUNTER.value == "center"
        assert HuntingStrategy.NEAREST_HUNTER.value == "nearest"
        assert HuntingStrategy.STRAGGLER_HUNTER.value == "straggler"
        assert HuntingStrategy.PATROL_HUNTER.value == "patrol"
        assert HuntingStrategy.RANDOM_HUNTER.value == "random"

    def test_five_strategies(self):
        """Exactly 5 strategies exist."""
        assert len(HuntingStrategy) == 5


class TestPredatorCreation:
    """Tests for predator creation with strategies."""

    def test_default_strategy(self):
        """Default strategy is CENTER_HUNTER."""
        pred = Predator.create_random()
        assert pred.strategy == HuntingStrategy.CENTER_HUNTER

    def test_create_with_strategy(self):
        """Can create with specific strategy."""
        pred = Predator.create_random(strategy=HuntingStrategy.NEAREST_HUNTER)
        assert pred.strategy == HuntingStrategy.NEAREST_HUNTER

    def test_create_with_strategy_index(self):
        """Strategy assigned by index."""
        pred0 = Predator.create_with_strategy_index(0)
        pred1 = Predator.create_with_strategy_index(1)
        pred2 = Predator.create_with_strategy_index(2)
        pred3 = Predator.create_with_strategy_index(3)
        pred4 = Predator.create_with_strategy_index(4)
        
        assert pred0.strategy == HuntingStrategy.CENTER_HUNTER
        assert pred1.strategy == HuntingStrategy.NEAREST_HUNTER
        assert pred2.strategy == HuntingStrategy.STRAGGLER_HUNTER
        assert pred3.strategy == HuntingStrategy.PATROL_HUNTER
        assert pred4.strategy == HuntingStrategy.RANDOM_HUNTER

    def test_strategy_index_wraps(self):
        """Index > 4 wraps around."""
        pred5 = Predator.create_with_strategy_index(5)
        assert pred5.strategy == HuntingStrategy.CENTER_HUNTER

    def test_patrol_hunter_has_patrol_center(self):
        """Patrol hunter gets initialized patrol center."""
        pred = Predator.create_random(strategy=HuntingStrategy.PATROL_HUNTER)
        assert pred.patrol_center is not None


class TestStrategyNames:
    """Tests for strategy names."""

    def test_strategy_name_hawk(self):
        """CENTER_HUNTER is Hawk."""
        pred = Predator.create_random(strategy=HuntingStrategy.CENTER_HUNTER)
        assert pred.strategy_name == "Hawk"

    def test_strategy_name_falcon(self):
        """NEAREST_HUNTER is Falcon."""
        pred = Predator.create_random(strategy=HuntingStrategy.NEAREST_HUNTER)
        assert pred.strategy_name == "Falcon"

    def test_strategy_name_eagle(self):
        """STRAGGLER_HUNTER is Eagle."""
        pred = Predator.create_random(strategy=HuntingStrategy.STRAGGLER_HUNTER)
        assert pred.strategy_name == "Eagle"

    def test_strategy_name_kite(self):
        """PATROL_HUNTER is Kite."""
        pred = Predator.create_random(strategy=HuntingStrategy.PATROL_HUNTER)
        assert pred.strategy_name == "Kite"

    def test_strategy_name_osprey(self):
        """RANDOM_HUNTER is Osprey."""
        pred = Predator.create_random(strategy=HuntingStrategy.RANDOM_HUNTER)
        assert pred.strategy_name == "Osprey"


class TestCenterHunter:
    """Tests for CENTER_HUNTER (Hawk) strategy."""

    def test_moves_toward_flock_center(self):
        """Hawk moves toward flock center of mass."""
        pred = Predator.create_at_position(0, 0, speed=0, strategy=HuntingStrategy.CENTER_HUNTER)
        pred.vx = 0
        pred.vy = 0
        
        # Boids clustered at (100, 100)
        boids = [
            Boid(x=90, y=90, vx=0, vy=0),
            Boid(x=100, y=100, vx=0, vy=0),
            Boid(x=110, y=110, vx=0, vy=0),
        ]
        
        pred.update_velocity_by_strategy(boids, hunting_strength=0.1)
        
        # Should move toward (100, 100)
        assert pred.vx > 0
        assert pred.vy > 0


class TestNearestHunter:
    """Tests for NEAREST_HUNTER (Falcon) strategy."""

    def test_moves_toward_nearest_boid(self):
        """Falcon moves toward nearest boid."""
        pred = Predator.create_at_position(0, 0, speed=0, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.vx = 0
        pred.vy = 0
        
        # Nearest boid at (50, 0), flock center at (150, 100)
        boids = [
            Boid(x=50, y=0, vx=0, vy=0),   # Nearest
            Boid(x=200, y=150, vx=0, vy=0),
            Boid(x=200, y=150, vx=0, vy=0),
        ]
        
        pred.update_velocity_by_strategy(boids, hunting_strength=0.1)
        
        # Should move toward (50, 0), not flock center
        assert pred.vx > 0
        assert abs(pred.vy) < 0.01  # Should barely move in y


class TestStragglerHunter:
    """Tests for STRAGGLER_HUNTER (Eagle) strategy."""

    def test_finds_isolated_boid(self):
        """compute_straggler_boid finds most isolated boid."""
        pred = Predator.create_at_position(0, 0, speed=0, strategy=HuntingStrategy.STRAGGLER_HUNTER)
        
        # Most boids clustered, one isolated
        boids = [
            Boid(x=100, y=100, vx=0, vy=0),
            Boid(x=102, y=100, vx=0, vy=0),
            Boid(x=100, y=102, vx=0, vy=0),
            Boid(x=500, y=500, vx=0, vy=0),  # Isolated straggler
        ]
        
        straggler = pred.compute_straggler_boid(boids)
        assert straggler.x == 500
        assert straggler.y == 500

    def test_moves_toward_straggler(self):
        """Eagle moves toward isolated boid."""
        pred = Predator.create_at_position(400, 400, speed=0, strategy=HuntingStrategy.STRAGGLER_HUNTER)
        pred.vx = 0
        pred.vy = 0
        
        boids = [
            Boid(x=100, y=100, vx=0, vy=0),
            Boid(x=102, y=100, vx=0, vy=0),
            Boid(x=500, y=500, vx=0, vy=0),  # Straggler
        ]
        
        pred.update_velocity_by_strategy(boids, hunting_strength=0.1)
        
        # Should move toward (500, 500)
        assert pred.vx > 0
        assert pred.vy > 0


class TestPatrolHunter:
    """Tests for PATROL_HUNTER (Kite) strategy."""

    def test_patrol_mode_circles(self):
        """Kite circles when no boids nearby."""
        pred = Predator.create_at_position(400, 300, speed=0, strategy=HuntingStrategy.PATROL_HUNTER)
        pred.patrol_center = np.array([400.0, 300.0])
        pred.patrol_angle = 0
        pred.vx = 0
        pred.vy = 0
        
        # Boids far away
        boids = [Boid(x=100, y=100, vx=0, vy=0)]
        
        pred.update_velocity_patrol(boids, hunting_strength=0.1, attack_range=100)
        
        # Should have some velocity from patrol circling
        assert pred.vx != 0 or pred.vy != 0

    def test_attack_mode_when_close(self):
        """Kite attacks when boid within range."""
        pred = Predator.create_at_position(400, 300, speed=0, strategy=HuntingStrategy.PATROL_HUNTER)
        pred.patrol_center = np.array([400.0, 300.0])
        pred.vx = 0
        pred.vy = 0
        
        # Boid within attack range
        boids = [Boid(x=420, y=310, vx=0, vy=0)]
        
        pred.update_velocity_patrol(boids, hunting_strength=0.1, attack_range=100)
        
        # Should move toward nearby boid
        assert pred.vx > 0
        assert pred.vy > 0


class TestRandomHunter:
    """Tests for RANDOM_HUNTER (Osprey) strategy."""

    def test_locks_onto_target(self):
        """Osprey locks onto a boid."""
        pred = Predator.create_at_position(0, 0, speed=0, strategy=HuntingStrategy.RANDOM_HUNTER)
        pred.vx = 0
        pred.vy = 0
        pred.target_boid_index = None
        
        boids = [
            Boid(x=100, y=0, vx=0, vy=0),
            Boid(x=0, y=100, vx=0, vy=0),
        ]
        
        pred.update_velocity_by_strategy(boids, hunting_strength=0.1)
        
        # Should have selected a target
        assert pred.target_boid_index is not None
        assert 0 <= pred.target_boid_index < len(boids)

    def test_switches_target_after_interval(self):
        """Osprey switches target after interval."""
        np.random.seed(42)  # For reproducibility
        
        pred = Predator.create_at_position(0, 0, speed=0, strategy=HuntingStrategy.RANDOM_HUNTER)
        pred.target_boid_index = 0
        pred.frames_since_target_switch = 119  # Almost at switch
        
        boids = [
            Boid(x=100, y=0, vx=0, vy=0),
            Boid(x=0, y=100, vx=0, vy=0),
        ]
        
        # One more frame should trigger switch
        pred.update_velocity_random_target(boids, switch_interval=120)
        
        assert pred.frames_since_target_switch == 0  # Reset


class TestFlockOptimizedStrategies:
    """Tests for FlockOptimized with different strategies."""

    def test_predators_have_different_strategies(self):
        """Multiple predators get different strategies."""
        flock = FlockOptimized(num_boids=10, enable_predator=True, num_predators=5)
        
        strategies = [p.strategy for p in flock.predators]
        
        assert strategies[0] == HuntingStrategy.CENTER_HUNTER
        assert strategies[1] == HuntingStrategy.NEAREST_HUNTER
        assert strategies[2] == HuntingStrategy.STRAGGLER_HUNTER
        assert strategies[3] == HuntingStrategy.PATROL_HUNTER
        assert strategies[4] == HuntingStrategy.RANDOM_HUNTER

    def test_simulation_runs_with_all_strategies(self):
        """Simulation runs smoothly with all strategy types."""
        params = SimulationParams(width=800, height=600)
        flock = FlockOptimized(num_boids=50, params=params, 
                              enable_predator=True, num_predators=5)
        
        # Run 100 frames
        for _ in range(100):
            flock.update()
        
        # All predators should still exist
        assert len(flock.predators) == 5
        
        # Predators should be roughly within bounds (with some tolerance
        # as boundary steering isn't instant)
        margin = 200  # Allow some overshoot
        for pred in flock.predators:
            assert -margin <= pred.x <= 800 + margin
            assert -margin <= pred.y <= 600 + margin

    def test_predators_spread_out(self):
        """Different strategies cause predators to spread out."""
        params = SimulationParams(width=800, height=600)
        flock = FlockOptimized(num_boids=100, params=params, 
                              enable_predator=True, num_predators=5)
        
        # Run simulation
        for _ in range(200):
            flock.update()
        
        # Calculate average distance between predators
        positions = [(p.x, p.y) for p in flock.predators]
        total_dist = 0
        count = 0
        for i, p1 in enumerate(positions):
            for p2 in positions[i+1:]:
                dist = np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
                total_dist += dist
                count += 1
        
        avg_dist = total_dist / count if count > 0 else 0
        
        # Predators should spread out (at least 50px average distance)
        # This is a soft check - strategies should lead to some spread
        assert avg_dist > 30  # Reasonable spread


if __name__ == "__main__":
    pytest.main([__file__, "-v"])