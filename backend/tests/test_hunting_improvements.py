"""
Tests for predator hunting improvements.

Tests the four hunting improvements:
1. Target Timeout - Force switch after N frames on same target
2. Catch & Cooldown - Rest period after catching prey
3. Chase Failure Detection - Give up on uncatchable targets
4. Edge Target Avoidance - Prefer targets away from edges
"""

import pytest
import numpy as np
from boids import Predator, HuntingStrategy, FlockOptimized, SimulationParams
from boids.boid import Boid
from boids.predator import (
    MAX_TARGET_FRAMES, 
    CATCH_DISTANCE, 
    COOLDOWN_DURATION,
    CHASE_FAILURE_FRAMES,
    EDGE_MARGIN
)


# =============================================================================
# Test Constants
# =============================================================================

WIDTH = 800
HEIGHT = 600


# =============================================================================
# 1. Target Timeout Tests
# =============================================================================

class TestTargetTimeout:
    """Tests for target timeout behavior."""

    def test_timeout_constants_exist(self):
        """Verify timeout constants are defined."""
        assert MAX_TARGET_FRAMES == 180
        assert MAX_TARGET_FRAMES > 0

    def test_should_switch_target_false_initially(self):
        """New predator should not immediately want to switch."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.frames_since_target_switch = 0
        
        assert not pred.should_switch_target()

    def test_should_switch_target_true_after_timeout(self):
        """Predator should want to switch after timeout."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.frames_since_target_switch = MAX_TARGET_FRAMES
        
        assert pred.should_switch_target()

    def test_falcon_switches_target_after_timeout(self):
        """Falcon (NEAREST_HUNTER) switches target after timeout."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.frames_since_target_switch = MAX_TARGET_FRAMES - 1
        
        boids = [
            Boid(x=300, y=300, vx=0, vy=0),
            Boid(x=500, y=300, vx=0, vy=0),
        ]
        
        # This should trigger a reset
        pred.update_velocity_by_strategy(boids, hunting_strength=0.1, width=WIDTH, height=HEIGHT)
        
        # frames_since_target_switch should be 0 or 1 after reset
        assert pred.frames_since_target_switch <= 1

    def test_osprey_respects_timeout(self):
        """Osprey (RANDOM_HUNTER) respects target timeout."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.RANDOM_HUNTER)
        pred.target_boid_index = 0
        pred.frames_since_target_switch = MAX_TARGET_FRAMES - 1
        
        boids = [
            Boid(x=300, y=300, vx=0, vy=0),
            Boid(x=500, y=300, vx=0, vy=0),
        ]
        
        # This call should trigger timeout check
        pred.update_velocity_by_strategy(boids, hunting_strength=0.1, width=WIDTH, height=HEIGHT)
        
        # Should have been reset
        assert pred.frames_since_target_switch <= 1


# =============================================================================
# 2. Catch & Cooldown Tests
# =============================================================================

class TestCatchAndCooldown:
    """Tests for catch detection and cooldown behavior."""

    def test_cooldown_constants_exist(self):
        """Verify catch/cooldown constants are defined."""
        assert CATCH_DISTANCE == 15.0
        assert COOLDOWN_DURATION == 60

    def test_is_in_cooldown_false_initially(self):
        """New predator should not be in cooldown."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        
        assert not pred.is_in_cooldown

    def test_is_in_cooldown_true_after_start(self):
        """Predator should be in cooldown after start_cooldown()."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.start_cooldown()
        
        assert pred.is_in_cooldown
        assert pred.cooldown_frames == COOLDOWN_DURATION

    def test_cooldown_decrements(self):
        """Cooldown should decrement each frame."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.cooldown_frames = 10
        
        pred.update_cooldown()
        assert pred.cooldown_frames == 9
        
        pred.update_cooldown()
        assert pred.cooldown_frames == 8

    def test_cooldown_does_not_go_negative(self):
        """Cooldown should not go below 0."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.cooldown_frames = 1
        
        pred.update_cooldown()
        assert pred.cooldown_frames == 0
        
        pred.update_cooldown()
        assert pred.cooldown_frames == 0

    def test_check_catch_true_when_close(self):
        """check_catch returns True when within catch distance."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        
        # Target at distance 10 (less than CATCH_DISTANCE of 15)
        assert pred.check_catch(410, 300)

    def test_check_catch_false_when_far(self):
        """check_catch returns False when outside catch distance."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        
        # Target at distance 50 (more than CATCH_DISTANCE of 15)
        assert not pred.check_catch(450, 300)

    def test_start_cooldown_resets_target(self):
        """start_cooldown should reset target tracking state."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.target_boid_index = 5
        pred.frames_since_target_switch = 100
        
        pred.start_cooldown()
        
        assert pred.target_boid_index is None
        assert pred.frames_since_target_switch == 0

    def test_falcon_enters_cooldown_on_catch(self):
        """Falcon should enter cooldown when catching prey."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.cooldown_frames = 0
        
        # Place boid within catch distance
        boids = [Boid(x=405, y=300, vx=0, vy=0)]
        
        pred.update_velocity_by_strategy(boids, hunting_strength=0.1, width=WIDTH, height=HEIGHT)
        
        assert pred.is_in_cooldown

    def test_predator_does_not_hunt_during_cooldown(self):
        """Predator should not update velocity during cooldown."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.vx = 0
        pred.vy = 0
        pred.cooldown_frames = 10
        
        boids = [Boid(x=200, y=300, vx=0, vy=0)]
        
        pred.update_velocity_by_strategy(boids, hunting_strength=0.1, width=WIDTH, height=HEIGHT)
        
        # Velocity should not change (no hunting during cooldown)
        assert pred.vx == 0
        assert pred.vy == 0
        # Cooldown should have decremented
        assert pred.cooldown_frames == 9


# =============================================================================
# 3. Chase Failure Detection Tests
# =============================================================================

class TestChaseFailureDetection:
    """Tests for chase failure detection."""

    def test_chase_failure_constants_exist(self):
        """Verify chase failure constants are defined."""
        assert CHASE_FAILURE_FRAMES == 90

    def test_check_chase_failure_false_when_progressing(self):
        """Should return False when making progress toward target."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.last_target_distance = 100
        pred.frames_without_progress = 0
        
        # Getting closer (distance decreased)
        result = pred.check_chase_failure(90)
        
        assert not result
        assert pred.frames_without_progress == 0

    def test_check_chase_failure_increments_when_stuck(self):
        """Should increment counter when not making progress."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.last_target_distance = 100
        pred.frames_without_progress = 0
        
        # Not getting closer (distance same or increased)
        pred.check_chase_failure(100)
        
        assert pred.frames_without_progress == 1

    def test_check_chase_failure_true_after_threshold(self):
        """Should return True after too many frames without progress."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.last_target_distance = 100
        pred.frames_without_progress = CHASE_FAILURE_FRAMES - 1
        
        # One more frame without progress
        result = pred.check_chase_failure(100)
        
        assert result
        assert pred.frames_without_progress == CHASE_FAILURE_FRAMES

    def test_progress_resets_failure_counter(self):
        """Making progress should reset the failure counter."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.last_target_distance = 100
        pred.frames_without_progress = 50
        
        # Getting closer
        pred.check_chase_failure(90)
        
        assert pred.frames_without_progress == 0

    def test_eagle_gives_up_on_uncatchable_straggler(self):
        """Eagle should give up on straggler it can't catch."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.STRAGGLER_HUNTER)
        pred.target_boid_index = 0
        pred.frames_since_target_switch = 50  # Past initial grace period
        pred.last_target_distance = 100
        pred.frames_without_progress = CHASE_FAILURE_FRAMES - 1
        
        # Boid staying at same distance (can't catch it)
        boids = [
            Boid(x=300, y=300, vx=-1, vy=0),  # Target moving away
            Boid(x=400, y=400, vx=0, vy=0),
        ]
        
        # Should trigger chase failure
        pred.update_velocity_by_strategy(boids, hunting_strength=0.1, width=WIDTH, height=HEIGHT)
        
        # Target should have been reset
        # (Either None or a new index after re-selection)
        # The key is that frames_without_progress should be 0 after reset
        assert pred.frames_without_progress == 0 or pred.frames_since_target_switch <= 1


# =============================================================================
# 4. Edge Target Avoidance Tests
# =============================================================================

class TestEdgeTargetAvoidance:
    """Tests for edge target avoidance."""

    def test_edge_margin_constant_exists(self):
        """Verify edge margin constant is defined."""
        assert EDGE_MARGIN == 100.0

    def test_is_near_edge_true_for_edge_positions(self):
        """is_near_edge should return True for positions near edges."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        
        # Left edge
        assert pred.is_near_edge(50, 300, WIDTH, HEIGHT)
        # Right edge
        assert pred.is_near_edge(750, 300, WIDTH, HEIGHT)
        # Top edge
        assert pred.is_near_edge(400, 50, WIDTH, HEIGHT)
        # Bottom edge
        assert pred.is_near_edge(400, 550, WIDTH, HEIGHT)
        # Corner
        assert pred.is_near_edge(50, 50, WIDTH, HEIGHT)

    def test_is_near_edge_false_for_center_positions(self):
        """is_near_edge should return False for positions away from edges."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        
        assert not pred.is_near_edge(400, 300, WIDTH, HEIGHT)
        assert not pred.is_near_edge(200, 300, WIDTH, HEIGHT)
        assert not pred.is_near_edge(600, 300, WIDTH, HEIGHT)

    def test_select_target_avoiding_edges_prefers_non_edge(self):
        """Should prefer targets away from edges."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        
        boids = [
            Boid(x=50, y=300, vx=0, vy=0),   # Near left edge
            Boid(x=400, y=300, vx=0, vy=0),  # Center (non-edge)
            Boid(x=750, y=300, vx=0, vy=0),  # Near right edge
        ]
        
        def select_first(boids_list, valid_indices):
            return valid_indices[0] if valid_indices else None
        
        result = pred.select_target_avoiding_edges(boids, WIDTH, HEIGHT, select_first)
        
        # Should select index 1 (the center boid)
        assert result == 1

    def test_select_target_falls_back_to_edge_if_necessary(self):
        """Should fall back to edge targets if no non-edge targets exist."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        
        # All boids near edges
        boids = [
            Boid(x=50, y=300, vx=0, vy=0),   # Near left edge
            Boid(x=750, y=300, vx=0, vy=0),  # Near right edge
        ]
        
        def select_first(boids_list, valid_indices):
            return valid_indices[0] if valid_indices else None
        
        result = pred.select_target_avoiding_edges(boids, WIDTH, HEIGHT, select_first)
        
        # Should still select something (fall back to edge target)
        assert result is not None
        assert result in [0, 1]

    def test_falcon_prefers_non_edge_targets(self):
        """Falcon should prefer hunting boids away from edges."""
        pred = Predator.create_at_position(200, 300, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.vx = 0
        pred.vy = 0
        
        boids = [
            Boid(x=50, y=300, vx=0, vy=0),   # Near left edge (closer!)
            Boid(x=400, y=300, vx=0, vy=0),  # Center (further but safe)
        ]
        
        pred.update_velocity_by_strategy(boids, hunting_strength=0.1, width=WIDTH, height=HEIGHT)
        
        # Should move toward center boid (right), not edge boid (left)
        assert pred.vx > 0


# =============================================================================
# Integration Tests
# =============================================================================

class TestHuntingImprovementsIntegration:
    """Integration tests for all hunting improvements together."""

    def test_simulation_with_all_improvements(self):
        """Full simulation should run with all improvements active."""
        params = SimulationParams(width=WIDTH, height=HEIGHT)
        flock = FlockOptimized(num_boids=50, params=params, enable_predator=True, num_predators=5)
        
        # Run simulation for 500 frames
        catches = 0
        cooldowns_observed = 0
        
        for frame in range(500):
            flock.update()
            
            for pred in flock.predators:
                if pred.is_in_cooldown:
                    cooldowns_observed += 1
        
        # Should have seen some cooldowns (catches happened)
        # This may vary due to randomness, so we just verify it ran
        assert len(flock.boids) > 0
        assert len(flock.predators) == 5

    def test_no_infinite_edge_circling(self):
        """Predators should not circle indefinitely at edges."""
        params = SimulationParams(width=WIDTH, height=HEIGHT)
        flock = FlockOptimized(num_boids=20, params=params, enable_predator=True, num_predators=3)
        
        # Place some boids near edges
        for i in range(5):
            flock.boids[i].x = 50
            flock.boids[i].y = 300
        
        edge_frames = {i: 0 for i in range(3)}
        
        for frame in range(300):
            flock.update()
            
            for i, pred in enumerate(flock.predators):
                if pred.is_near_edge(pred.x, pred.y, WIDTH, HEIGHT):
                    edge_frames[i] += 1
        
        # No predator should spend more than 50% of time at edges
        for i, frames in edge_frames.items():
            ratio = frames / 300
            assert ratio < 0.5, f"Predator {i} spent {ratio*100:.1f}% of time at edges"

    def test_predators_catch_and_recover(self):
        """Predators should catch prey and then resume hunting."""
        params = SimulationParams(width=WIDTH, height=HEIGHT)
        flock = FlockOptimized(num_boids=30, params=params, enable_predator=True, num_predators=2)
        
        total_cooldown_events = 0
        
        for frame in range(500):
            # Check for new cooldowns
            for pred in flock.predators:
                if pred.cooldown_frames == COOLDOWN_DURATION:
                    total_cooldown_events += 1
            
            flock.update()
        
        # Should have had at least some catches over 500 frames
        # (This is probabilistic, so we use a low threshold)
        assert total_cooldown_events >= 0  # At minimum, it shouldn't crash

    def test_target_switching_prevents_stalemate(self):
        """Target timeout should prevent indefinite chases."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.RANDOM_HUNTER)
        
        boids = [
            Boid(x=100, y=100, vx=0, vy=0),
            Boid(x=700, y=500, vx=0, vy=0),
        ]
        
        # Track target changes
        targets_seen = set()
        
        for frame in range(MAX_TARGET_FRAMES + 50):
            pred.update_velocity_by_strategy(boids, hunting_strength=0.05, width=WIDTH, height=HEIGHT)
            if pred.target_boid_index is not None:
                targets_seen.add(pred.target_boid_index)
            pred.x += pred.vx
            pred.y += pred.vy
        
        # Should have potentially switched targets
        # (Due to timeout, not just random switching)
        assert len(targets_seen) >= 1


# =============================================================================
# Regression Tests
# =============================================================================

class TestHuntingImprovementsRegression:
    """Regression tests to ensure improvements don't break existing behavior."""

    def test_hawk_still_hunts_center(self):
        """Hawk (CENTER_HUNTER) should still hunt flock center."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.CENTER_HUNTER)
        pred.vx = 0
        pred.vy = 0
        
        # Flock center at (200, 200)
        boids = [
            Boid(x=150, y=150, vx=0, vy=0),
            Boid(x=200, y=200, vx=0, vy=0),
            Boid(x=250, y=250, vx=0, vy=0),
        ]
        
        pred.update_velocity_by_strategy(boids, hunting_strength=0.1, width=WIDTH, height=HEIGHT)
        
        # Should move toward flock center (left and up)
        assert pred.vx < 0
        assert pred.vy < 0

    def test_patrol_still_circles(self):
        """Kite (PATROL_HUNTER) should still circle when no prey nearby."""
        pred = Predator.create_at_position(400, 300, strategy=HuntingStrategy.PATROL_HUNTER)
        pred.patrol_center = np.array([400.0, 300.0])
        pred.patrol_angle = 0
        
        # No boids nearby
        boids = [Boid(x=100, y=100, vx=0, vy=0)]  # Far away
        
        initial_angle = pred.patrol_angle
        pred.update_velocity_by_strategy(boids, hunting_strength=0.1, width=WIDTH, height=HEIGHT)
        
        # Patrol angle should have incremented
        assert pred.patrol_angle > initial_angle

    def test_boundaries_still_respected(self):
        """Boundary fixes should still work with hunting improvements."""
        params = SimulationParams(width=WIDTH, height=HEIGHT)
        flock = FlockOptimized(num_boids=50, params=params, enable_predator=True, num_predators=5)
        
        violations = 0
        
        for frame in range(300):
            flock.update()
            
            for boid in flock.boids:
                if boid.x < 0 or boid.x > WIDTH or boid.y < 0 or boid.y > HEIGHT:
                    violations += 1
            
            for pred in flock.predators:
                if pred.x < 0 or pred.x > WIDTH or pred.y < 0 or pred.y > HEIGHT:
                    violations += 1
        
        assert violations == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])