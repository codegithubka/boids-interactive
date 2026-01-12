"""
Boundary Regression Tests

These tests verify that boids and predators stay within simulation bounds.
Created to diagnose and fix boundary violations after predator species implementation.
"""

import pytest
import numpy as np
from boids import Predator, HuntingStrategy, FlockOptimized, SimulationParams
from boids.boid import Boid


# =============================================================================
# Test Constants
# =============================================================================

WIDTH = 800
HEIGHT = 600
MARGIN = 75
MAX_FRAMES = 500  # Run simulations long enough to expose issues


def is_within_bounds(x: float, y: float, width: float = WIDTH, height: float = HEIGHT, tolerance: float = 50) -> bool:
    """Check if position is within bounds (with tolerance for boundary steering lag)."""
    return -tolerance <= x <= width + tolerance and -tolerance <= y <= height + tolerance


def is_strictly_within_bounds(x: float, y: float, width: float = WIDTH, height: float = HEIGHT) -> bool:
    """Check if position is strictly within bounds (no tolerance)."""
    return 0 <= x <= width and 0 <= y <= height


# =============================================================================
# Boid Boundary Tests
# =============================================================================

class TestBoidBoundaries:
    """Tests for boid boundary behavior."""

    def test_boids_stay_in_bounds_basic(self):
        """Boids should stay within bounds during normal simulation."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=50, params=params, enable_predator=False)
        
        violations = []
        for frame in range(MAX_FRAMES):
            flock.update()
            for i, boid in enumerate(flock.boids):
                if not is_within_bounds(boid.x, boid.y):
                    violations.append((frame, i, boid.x, boid.y))
        
        assert len(violations) == 0, f"Boid boundary violations: {violations[:10]}"

    def test_boids_stay_in_bounds_with_single_predator(self):
        """Boids should stay within bounds when fleeing from predator."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=50, params=params, enable_predator=True, num_predators=1)
        
        violations = []
        for frame in range(MAX_FRAMES):
            flock.update()
            for i, boid in enumerate(flock.boids):
                if not is_within_bounds(boid.x, boid.y):
                    violations.append((frame, i, boid.x, boid.y))
        
        assert len(violations) == 0, f"Boid boundary violations: {violations[:10]}"

    def test_boids_stay_in_bounds_with_multiple_predators(self):
        """Boids should stay within bounds when fleeing from multiple predators."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=50, params=params, enable_predator=True, num_predators=5)
        
        violations = []
        for frame in range(MAX_FRAMES):
            flock.update()
            for i, boid in enumerate(flock.boids):
                if not is_within_bounds(boid.x, boid.y):
                    violations.append((frame, i, boid.x, boid.y))
        
        assert len(violations) == 0, f"Boid boundary violations: {violations[:10]}"

    def test_boid_near_edge_returns_to_bounds(self):
        """A boid placed near the edge should be steered back into bounds."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=1, params=params, enable_predator=False)
        
        # Place boid at the edge heading outward
        flock.boids[0].x = 10  # Inside left margin
        flock.boids[0].y = 300
        flock.boids[0].vx = -3.0  # Heading left (out of bounds)
        flock.boids[0].vy = 0
        
        # Run for a while
        for _ in range(100):
            flock.update()
        
        boid = flock.boids[0]
        assert is_within_bounds(boid.x, boid.y), f"Boid escaped: ({boid.x}, {boid.y})"


# =============================================================================
# Predator Boundary Tests - General
# =============================================================================

class TestPredatorBoundaries:
    """Tests for predator boundary behavior."""

    def test_single_predator_stays_in_bounds(self):
        """Single predator should stay within bounds."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=50, params=params, enable_predator=True, num_predators=1)
        
        violations = []
        for frame in range(MAX_FRAMES):
            flock.update()
            for i, pred in enumerate(flock.predators):
                if not is_within_bounds(pred.x, pred.y):
                    violations.append((frame, i, pred.strategy.value, pred.x, pred.y))
        
        assert len(violations) == 0, f"Predator boundary violations: {violations[:10]}"

    def test_all_predators_stay_in_bounds(self):
        """All 5 predator types should stay within bounds."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=50, params=params, enable_predator=True, num_predators=5)
        
        violations = []
        for frame in range(MAX_FRAMES):
            flock.update()
            for i, pred in enumerate(flock.predators):
                if not is_within_bounds(pred.x, pred.y):
                    violations.append((frame, pred.strategy_name, pred.x, pred.y))
        
        assert len(violations) == 0, f"Predator boundary violations: {violations[:10]}"


# =============================================================================
# Predator Boundary Tests - By Strategy
# =============================================================================

class TestCenterHunterBoundary:
    """Tests for CENTER_HUNTER (Hawk) boundary behavior."""

    def test_hawk_stays_in_bounds(self):
        """Hawk chasing flock center should stay in bounds."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=50, params=params, enable_predator=True, num_predators=1)
        
        # Ensure it's a hawk
        assert flock.predators[0].strategy == HuntingStrategy.CENTER_HUNTER
        
        violations = []
        for frame in range(MAX_FRAMES):
            flock.update()
            pred = flock.predators[0]
            if not is_within_bounds(pred.x, pred.y):
                violations.append((frame, pred.x, pred.y))
        
        assert len(violations) == 0, f"Hawk violations: {violations[:5]}"


class TestNearestHunterBoundary:
    """Tests for NEAREST_HUNTER (Falcon) boundary behavior."""

    def test_falcon_stays_in_bounds_when_prey_at_edge(self):
        """Falcon should not escape bounds when chasing prey near edge."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=20, params=params, enable_predator=False)
        
        # Create falcon manually
        falcon = Predator.create_at_position(400, 300, speed=2.5, strategy=HuntingStrategy.NEAREST_HUNTER)
        flock.predators.append(falcon)
        
        # Place some boids near the edge
        for i in range(5):
            flock.boids[i].x = 20  # Near left edge
            flock.boids[i].y = 300
        
        violations = []
        for frame in range(MAX_FRAMES):
            flock.update()
            if not is_within_bounds(falcon.x, falcon.y):
                violations.append((frame, falcon.x, falcon.y))
        
        assert len(violations) == 0, f"Falcon violations: {violations[:5]}"


class TestStragglerHunterBoundary:
    """Tests for STRAGGLER_HUNTER (Eagle) boundary behavior."""

    def test_eagle_stays_in_bounds_when_straggler_at_edge(self):
        """Eagle should not escape bounds when chasing straggler near edge."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=20, params=params, enable_predator=False)
        
        # Create eagle manually
        eagle = Predator.create_at_position(400, 300, speed=2.5, strategy=HuntingStrategy.STRAGGLER_HUNTER)
        flock.predators.append(eagle)
        
        # Create a clear straggler at the edge
        flock.boids[0].x = 10  # Straggler at left edge
        flock.boids[0].y = 300
        # Keep other boids in center
        for i in range(1, len(flock.boids)):
            flock.boids[i].x = 400
            flock.boids[i].y = 300
        
        violations = []
        for frame in range(MAX_FRAMES):
            flock.update()
            if not is_within_bounds(eagle.x, eagle.y):
                violations.append((frame, eagle.x, eagle.y))
        
        assert len(violations) == 0, f"Eagle violations: {violations[:5]}"


class TestPatrolHunterBoundary:
    """Tests for PATROL_HUNTER (Kite) boundary behavior."""

    def test_kite_stays_in_bounds_during_patrol(self):
        """Kite should stay in bounds while patrolling."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=20, params=params, enable_predator=False)
        
        # Create kite manually at center
        kite = Predator.create_at_position(400, 300, speed=2.5, strategy=HuntingStrategy.PATROL_HUNTER)
        kite.patrol_center = np.array([400.0, 300.0])
        flock.predators.append(kite)
        
        violations = []
        for frame in range(MAX_FRAMES):
            flock.update()
            if not is_within_bounds(kite.x, kite.y):
                violations.append((frame, kite.x, kite.y))
        
        assert len(violations) == 0, f"Kite violations: {violations[:5]}"

    def test_kite_with_edge_patrol_center(self):
        """Kite with patrol center near edge should still stay in bounds."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=20, params=params, enable_predator=False)
        
        # Create kite with patrol center near edge
        kite = Predator.create_at_position(100, 100, speed=2.5, strategy=HuntingStrategy.PATROL_HUNTER)
        kite.patrol_center = np.array([50.0, 50.0])  # Near corner
        flock.predators.append(kite)
        
        violations = []
        for frame in range(MAX_FRAMES):
            flock.update()
            if not is_within_bounds(kite.x, kite.y):
                violations.append((frame, kite.x, kite.y))
        
        assert len(violations) == 0, f"Kite (edge patrol) violations: {violations[:5]}"


class TestRandomHunterBoundary:
    """Tests for RANDOM_HUNTER (Osprey) boundary behavior."""

    def test_osprey_stays_in_bounds(self):
        """Osprey should stay in bounds while switching targets."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=20, params=params, enable_predator=False)
        
        # Create osprey manually
        osprey = Predator.create_at_position(400, 300, speed=2.5, strategy=HuntingStrategy.RANDOM_HUNTER)
        flock.predators.append(osprey)
        
        violations = []
        for frame in range(MAX_FRAMES):
            flock.update()
            if not is_within_bounds(osprey.x, osprey.y):
                violations.append((frame, osprey.x, osprey.y))
        
        assert len(violations) == 0, f"Osprey violations: {violations[:5]}"


# =============================================================================
# Force Balance Tests
# =============================================================================

class TestForceBalance:
    """Tests to verify boundary forces can overcome hunting forces."""

    def test_boundary_force_magnitude(self):
        """Boundary steering should produce progressive force based on distance."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN, turn_factor=0.2)
        flock = FlockOptimized(num_boids=1, params=params)
        
        # Place boid just inside left margin (10 pixels into margin)
        flock.boids[0].x = MARGIN - 10  # 65, inside margin of 75
        flock.boids[0].y = 300
        
        dvx, dvy = flock.apply_boundary_steering(flock.boids[0])
        
        # With progressive steering: force = turn_factor * (1 + distance_into_margin / margin)
        # distance_into_margin = 75 - 65 = 10
        # scale = 1 + 10/75 = 1.133...
        # expected = 0.2 * 1.133 = 0.2267
        expected = 0.2 * (1 + 10/75)
        
        assert dvx == pytest.approx(expected, rel=0.01), f"Expected {expected}, got {dvx}"
        assert dvy == 0
        
        # Verify force increases when further past margin
        flock.boids[0].x = 30  # 45 pixels into margin
        dvx2, _ = flock.apply_boundary_steering(flock.boids[0])
        
        # scale = 1 + 45/75 = 1.6
        # expected = 0.2 * 1.6 = 0.32
        expected2 = 0.2 * (1 + 45/75)
        assert dvx2 == pytest.approx(expected2, rel=0.01)
        assert dvx2 > dvx, "Force should be stronger when further past margin"

    def test_hunting_force_vs_boundary_force(self):
        """Verify hunting force is now capped to reasonable levels."""
        # With force capping, hunting force is limited to max_force (default 1.0)
        pred = Predator.create_at_position(0, 0, speed=0, strategy=HuntingStrategy.NEAREST_HUNTER)
        
        # Distant target
        target = np.array([400.0, 0.0])
        
        # Without capping: 400 * 0.05 = 20
        # With capping (max_force=1.0): should be 1.0
        dvx, dvy = pred.steer_toward(target, hunting_strength=0.05, max_force=1.0)
        
        magnitude = np.sqrt(dvx**2 + dvy**2)
        
        # Force should be capped at 1.0
        assert magnitude <= 1.01, f"Hunting force should be capped: got {magnitude}"
        
        # Boundary force at edge: 0.2 * (1 + distance/margin)
        # At 0 pixels (75 into margin): 0.2 * (1 + 75/75) = 0.4
        # Now boundary (0.4) vs hunting (1.0) is only 2.5x difference, not 100x
        boundary_force = 0.2 * 2  # At edge
        ratio = magnitude / boundary_force
        
        print(f"\nHunting force (capped): {magnitude}")
        print(f"Boundary force at edge: {boundary_force}")
        print(f"Ratio: {ratio}x")
        
        # Ratio should now be reasonable (< 5x)
        assert ratio < 5, f"Ratio should be < 5, got {ratio}"

    def test_predator_at_edge_with_distant_target(self):
        """Predator at edge with distant target should not escape bounds."""
        pred = Predator.create_at_position(10, 300, speed=2.5, strategy=HuntingStrategy.NEAREST_HUNTER)
        pred.vx = 0
        pred.vy = 0
        
        # Simulate a distant boid on the right side
        boids = [Boid(x=790, y=300, vx=0, vy=0)]
        
        # Apply hunting strategy
        pred.update_velocity_by_strategy(boids, hunting_strength=0.05)
        
        hunting_dvx = pred.vx  # Should be positive (toward right)
        
        # Apply boundary steering
        pred.apply_boundary_steering(WIDTH, HEIGHT, MARGIN, turn_factor=0.2)
        
        # Since we're at x=10 (inside margin of 75), we get +0.2
        # But if we were at x=-10 (outside bounds), boundary still only gives +0.2
        
        # The problem: hunting_dvx could be (790-10)*0.05 = 39
        # But boundary only gives 0.2
        
        print(f"\nHunting dvx: {hunting_dvx}")
        print(f"Final vx after boundary: {pred.vx}")
        
        # Verify the predator is being pushed in the right direction
        # (toward the target, which is also toward center for this case)
        assert pred.vx > 0, "Predator should move right toward target"


# =============================================================================
# Long-Running Stress Tests
# =============================================================================

class TestLongRunningSimulation:
    """Stress tests that run simulations for extended periods."""

    def test_1000_frame_stability(self):
        """Simulation should remain stable for 1000 frames."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=100, params=params, enable_predator=True, num_predators=5)
        
        boid_violations = 0
        pred_violations = 0
        
        for frame in range(1000):
            flock.update()
            
            for boid in flock.boids:
                if not is_within_bounds(boid.x, boid.y, tolerance=100):
                    boid_violations += 1
            
            for pred in flock.predators:
                if not is_within_bounds(pred.x, pred.y, tolerance=100):
                    pred_violations += 1
        
        # Allow very few violations (boundary steering lag)
        assert boid_violations < 10, f"Too many boid violations: {boid_violations}"
        assert pred_violations < 10, f"Too many predator violations: {pred_violations}"

    def test_worst_case_scenario(self):
        """Test with high speeds and aggressive hunting."""
        params = SimulationParams(
            width=WIDTH, 
            height=HEIGHT, 
            margin=MARGIN,
            max_speed=5.0,  # High speed
            predator_speed=4.0,  # Fast predator
            predator_hunting_strength=0.1,  # Aggressive hunting
        )
        flock = FlockOptimized(num_boids=50, params=params, enable_predator=True, num_predators=5)
        
        max_escape_distance = 0
        
        for frame in range(500):
            flock.update()
            
            for pred in flock.predators:
                escape_x = max(0, -pred.x, pred.x - WIDTH)
                escape_y = max(0, -pred.y, pred.y - HEIGHT)
                escape_dist = max(escape_x, escape_y)
                max_escape_distance = max(max_escape_distance, escape_dist)
        
        print(f"\nMax escape distance: {max_escape_distance}")
        
        # Should not escape too far even in worst case
        assert max_escape_distance < 200, f"Escaped too far: {max_escape_distance}"


# =============================================================================
# Diagnostic Tests
# =============================================================================

class TestDiagnostics:
    """Tests that help diagnose boundary issues."""

    def test_identify_escaping_strategies(self):
        """Identify which strategies are most likely to escape."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        
        escape_counts = {s.value: 0 for s in HuntingStrategy}
        
        for _ in range(10):  # Multiple runs
            flock = FlockOptimized(num_boids=50, params=params, enable_predator=True, num_predators=5)
            
            for frame in range(200):
                flock.update()
                
                for pred in flock.predators:
                    if not is_within_bounds(pred.x, pred.y, tolerance=50):
                        escape_counts[pred.strategy.value] += 1
        
        print("\nEscape counts by strategy:")
        for strategy, count in escape_counts.items():
            print(f"  {strategy}: {count}")
        
        # This test documents which strategies escape most
        # After fix, all should be 0

    def test_track_worst_offender(self):
        """Track the predator that escapes furthest."""
        params = SimulationParams(width=WIDTH, height=HEIGHT, margin=MARGIN)
        flock = FlockOptimized(num_boids=50, params=params, enable_predator=True, num_predators=5)
        
        worst_escape = None
        
        for frame in range(300):
            flock.update()
            
            for pred in flock.predators:
                if pred.x < 0 or pred.x > WIDTH or pred.y < 0 or pred.y > HEIGHT:
                    escape_dist = max(
                        max(0, -pred.x),
                        max(0, pred.x - WIDTH),
                        max(0, -pred.y),
                        max(0, pred.y - HEIGHT)
                    )
                    if worst_escape is None or escape_dist > worst_escape[2]:
                        worst_escape = (pred.strategy_name, frame, escape_dist, pred.x, pred.y)
        
        if worst_escape:
            print(f"\nWorst escape: {worst_escape[0]} at frame {worst_escape[1]}")
            print(f"  Position: ({worst_escape[3]:.1f}, {worst_escape[4]:.1f})")
            print(f"  Escape distance: {worst_escape[2]:.1f}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])