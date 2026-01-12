"""
3D Boids Test Suite

Comprehensive tests for 3D boids simulation including:
- 3D distance calculations
- 3D flocking rules (separation, alignment, cohesion)
- 3D boundary steering
- 3D predator avoidance
- 3D obstacle avoidance
- KDTree neighbor finding in 3D
- Integration tests for Flock3D

These tests should be implemented alongside the 3D backend code.
"""

import pytest
import numpy as np

# Phase 1 imports (now implemented)
from boids.boid3d import Boid3D, distance_3d
from boids.predator3d import Predator3D, HuntingStrategy
from boids.obstacle3d import Obstacle3D, create_obstacle_field_3d


# =============================================================================
# Test Constants
# =============================================================================

WIDTH = 800
HEIGHT = 600
DEPTH = 600
MARGIN = 75


# =============================================================================
# 3D Distance Tests
# =============================================================================

class TestDistance3D:
    """Tests for 3D Euclidean distance calculation."""

    def test_same_point_is_zero(self):
        """Distance from a point to itself is 0."""
        b = Boid3D(100, 200, 300, 0, 0, 0)
        assert distance_3d(b, b) == 0

    def test_unit_distance_x_axis(self):
        """Distance of 1 along X axis."""
        b1 = Boid3D(0, 0, 0, 0, 0, 0)
        b2 = Boid3D(1, 0, 0, 0, 0, 0)
        assert distance_3d(b1, b2) == 1

    def test_unit_distance_y_axis(self):
        """Distance of 1 along Y axis."""
        b1 = Boid3D(0, 0, 0, 0, 0, 0)
        b2 = Boid3D(0, 1, 0, 0, 0, 0)
        assert distance_3d(b1, b2) == 1

    def test_unit_distance_z_axis(self):
        """Distance of 1 along Z axis."""
        b1 = Boid3D(0, 0, 0, 0, 0, 0)
        b2 = Boid3D(0, 0, 1, 0, 0, 0)
        assert distance_3d(b1, b2) == 1

    def test_3d_diagonal(self):
        """Distance along 3D diagonal is sqrt(3)."""
        b1 = Boid3D(0, 0, 0, 0, 0, 0)
        b2 = Boid3D(1, 1, 1, 0, 0, 0)
        assert distance_3d(b1, b2) == pytest.approx(np.sqrt(3))

    def test_symmetry(self):
        """Distance is symmetric: d(a,b) == d(b,a)."""
        b1 = Boid3D(10, 20, 30, 0, 0, 0)
        b2 = Boid3D(50, 60, 70, 0, 0, 0)
        assert distance_3d(b1, b2) == distance_3d(b2, b1)

    def test_arbitrary_distance(self):
        """Distance calculation for arbitrary points."""
        b1 = Boid3D(0, 0, 0, 0, 0, 0)
        b2 = Boid3D(3, 4, 0, 0, 0, 0)  # 3-4-5 triangle in XY
        assert distance_3d(b1, b2) == pytest.approx(5.0)
        
        b3 = Boid3D(0, 0, 0, 0, 0, 0)
        b4 = Boid3D(2, 3, 6, 0, 0, 0)  # sqrt(4+9+36) = 7
        assert distance_3d(b3, b4) == pytest.approx(7.0)


# =============================================================================
# Boid3D Class Tests
# =============================================================================

class TestBoid3D:
    """Tests for Boid3D class."""

    def test_create_with_position(self):
        """Boid3D stores x, y, z position."""
        b = Boid3D(100, 200, 300, 1, 2, 3)
        assert b.x == 100
        assert b.y == 200
        assert b.z == 300

    def test_create_with_velocity(self):
        """Boid3D stores vx, vy, vz velocity."""
        b = Boid3D(0, 0, 0, 1.5, 2.5, 3.5)
        assert b.vx == 1.5
        assert b.vy == 2.5
        assert b.vz == 3.5

    def test_speed_property(self):
        """Speed is magnitude of 3D velocity."""
        b = Boid3D(0, 0, 0, 1, 2, 2)  # sqrt(1+4+4) = 3
        assert b.speed == pytest.approx(3.0)

    def test_position_property(self):
        """Position property returns numpy array."""
        b = Boid3D(10, 20, 30, 0, 0, 0)
        pos = b.position
        assert isinstance(pos, np.ndarray)
        assert list(pos) == [10, 20, 30]

    def test_velocity_property(self):
        """Velocity property returns numpy array."""
        b = Boid3D(0, 0, 0, 1, 2, 3)
        vel = b.velocity
        assert isinstance(vel, np.ndarray)
        assert list(vel) == [1, 2, 3]

    def test_create_random(self):
        """Factory creates boid within bounds."""
        for _ in range(100):
            b = Boid3D.create_random(WIDTH, HEIGHT, DEPTH, max_speed=3.0)
            assert 0 <= b.x <= WIDTH
            assert 0 <= b.y <= HEIGHT
            assert 0 <= b.z <= DEPTH
            assert b.speed <= 3.0 + 0.01  # Small tolerance

    def test_create_at_position(self):
        """Factory creates boid at specific position."""
        b = Boid3D.create_at_position(100, 200, 300, speed=2.0)
        assert b.x == 100
        assert b.y == 200
        assert b.z == 300
        assert b.speed == pytest.approx(2.0, abs=0.01)

    def test_create_at_position_with_direction(self):
        """Factory creates boid with specific direction."""
        b = Boid3D.create_at_position(100, 200, 300, speed=3.0, direction=(1, 0, 0))
        assert b.vx == pytest.approx(3.0)
        assert b.vy == pytest.approx(0.0)
        assert b.vz == pytest.approx(0.0)

    def test_to_list(self):
        """to_list returns [x, y, z, vx, vy, vz]."""
        b = Boid3D(1, 2, 3, 4, 5, 6)
        assert b.to_list() == [1, 2, 3, 4, 5, 6]

    def test_distance_to(self):
        """distance_to calculates distance to another boid."""
        b1 = Boid3D(0, 0, 0, 0, 0, 0)
        b2 = Boid3D(3, 4, 0, 0, 0, 0)
        assert b1.distance_to(b2) == pytest.approx(5.0)

    def test_distance_to_point(self):
        """distance_to_point calculates distance to coordinates."""
        b = Boid3D(0, 0, 0, 0, 0, 0)
        assert b.distance_to_point(3, 4, 0) == pytest.approx(5.0)


# =============================================================================
# Predator3D Class Tests
# =============================================================================

class TestPredator3D:
    """Tests for Predator3D class."""

    def test_create_with_position(self):
        """Predator3D stores x, y, z position."""
        p = Predator3D(100, 200, 300, 1, 2, 3)
        assert p.x == 100
        assert p.y == 200
        assert p.z == 300

    def test_speed_property(self):
        """Speed is magnitude of 3D velocity."""
        p = Predator3D(0, 0, 0, 1, 2, 2, 0, 0, 0)
        assert p.speed == pytest.approx(3.0)

    def test_create_random(self):
        """Factory creates predator within bounds."""
        for _ in range(50):
            p = Predator3D.create_random(WIDTH, HEIGHT, DEPTH, speed=2.5)
            assert 0 <= p.x <= WIDTH
            assert 0 <= p.y <= HEIGHT
            assert 0 <= p.z <= DEPTH
            assert p.speed == pytest.approx(2.5, abs=0.01)

    def test_create_with_strategy_index(self):
        """Factory assigns correct strategy by index."""
        from boids.predator3d import STRATEGY_ORDER
        
        for i, expected_strategy in enumerate(STRATEGY_ORDER):
            p = Predator3D.create_with_strategy_index(i, WIDTH, HEIGHT, DEPTH)
            assert p.strategy == expected_strategy

    def test_strategy_names(self):
        """Strategy names are correct."""
        strategies = [
            (HuntingStrategy.CENTER_HUNTER, "Hawk"),
            (HuntingStrategy.NEAREST_HUNTER, "Falcon"),
            (HuntingStrategy.STRAGGLER_HUNTER, "Eagle"),
            (HuntingStrategy.PATROL_HUNTER, "Kite"),
            (HuntingStrategy.RANDOM_HUNTER, "Osprey"),
        ]
        for strategy, expected_name in strategies:
            p = Predator3D(0, 0, 0, 0, 0, 0, strategy=strategy)
            assert p.strategy_name == expected_name

    def test_cooldown_mechanics(self):
        """Cooldown state management works."""
        p = Predator3D(0, 0, 0, 0, 0, 0)
        assert not p.is_in_cooldown
        
        p.start_cooldown()
        assert p.is_in_cooldown
        assert p.cooldown_frames == 60  # COOLDOWN_DURATION
        
        p.update_cooldown()
        assert p.cooldown_frames == 59

    def test_check_catch(self):
        """Catch detection works in 3D."""
        p = Predator3D(100, 100, 100, 0, 0, 0)
        
        # Close enough (within CATCH_DISTANCE of 15)
        assert p.check_catch(105, 100, 100)  # 5 units away
        
        # Too far
        assert not p.check_catch(150, 100, 100)  # 50 units away

    def test_steer_toward(self):
        """steer_toward calculates correct 3D force."""
        p = Predator3D(0, 0, 0, 0, 0, 0)
        target = np.array([100, 0, 0])
        
        dvx, dvy, dvz = p.steer_toward(target, hunting_strength=0.1)
        
        # Should steer toward +X
        assert dvx > 0
        assert dvy == pytest.approx(0)
        assert dvz == pytest.approx(0)

    def test_steer_toward_z_dimension(self):
        """steer_toward works in Z dimension."""
        p = Predator3D(0, 0, 0, 0, 0, 0)
        target = np.array([0, 0, 100])
        
        dvx, dvy, dvz = p.steer_toward(target, hunting_strength=0.1)
        
        assert dvx == pytest.approx(0)
        assert dvy == pytest.approx(0)
        assert dvz > 0  # Should steer toward +Z

    def test_compute_flock_center_3d(self):
        """Flock center computed correctly in 3D."""
        p = Predator3D(0, 0, 0, 0, 0, 0)
        boids = [
            Boid3D(0, 0, 0, 0, 0, 0),
            Boid3D(100, 100, 100, 0, 0, 0),
        ]
        center = p.compute_flock_center(boids)
        
        assert center[0] == pytest.approx(50)
        assert center[1] == pytest.approx(50)
        assert center[2] == pytest.approx(50)

    def test_to_dict(self):
        """to_dict returns correct structure."""
        p = Predator3D(1, 2, 3, 4, 5, 6, strategy=HuntingStrategy.CENTER_HUNTER)
        d = p.to_dict()
        
        assert d["x"] == 1
        assert d["y"] == 2
        assert d["z"] == 3
        assert d["vx"] == 4
        assert d["vy"] == 5
        assert d["vz"] == 6
        assert d["strategy"] == "center"
        assert d["strategy_name"] == "Hawk"


# =============================================================================
# Obstacle3D Class Tests
# =============================================================================

class TestObstacle3D:
    """Tests for Obstacle3D class."""

    def test_create_with_position(self):
        """Obstacle3D stores position and radius."""
        o = Obstacle3D(100, 200, 300, 50)
        assert o.x == 100
        assert o.y == 200
        assert o.z == 300
        assert o.radius == 50

    def test_position_property(self):
        """Position property returns numpy array."""
        o = Obstacle3D(10, 20, 30, 50)
        pos = o.position
        assert isinstance(pos, np.ndarray)
        assert list(pos) == [10, 20, 30]

    def test_create_random(self):
        """Factory creates obstacle within bounds."""
        for _ in range(50):
            o = Obstacle3D.create_random(WIDTH, HEIGHT, DEPTH)
            assert 0 < o.x < WIDTH
            assert 0 < o.y < HEIGHT
            assert 0 < o.z < DEPTH
            assert 20 <= o.radius <= 50

    def test_contains_point_inside(self):
        """contains_point returns True for points inside."""
        o = Obstacle3D(100, 100, 100, 50)
        assert o.contains_point(100, 100, 100)  # Center
        assert o.contains_point(120, 100, 100)  # 20 units away

    def test_contains_point_outside(self):
        """contains_point returns False for points outside."""
        o = Obstacle3D(100, 100, 100, 50)
        assert not o.contains_point(200, 100, 100)  # 100 units away

    def test_distance_to_surface(self):
        """distance_to_surface calculates correctly."""
        o = Obstacle3D(100, 100, 100, 50)
        
        # At center: -50 (inside)
        assert o.distance_to_surface(100, 100, 100) == pytest.approx(-50)
        
        # On surface: 0
        assert o.distance_to_surface(150, 100, 100) == pytest.approx(0)
        
        # Outside: positive
        assert o.distance_to_surface(200, 100, 100) == pytest.approx(50)

    def test_to_list(self):
        """to_list returns [x, y, z, radius]."""
        o = Obstacle3D(1, 2, 3, 4)
        assert o.to_list() == [1, 2, 3, 4]

    def test_create_obstacle_field(self):
        """create_obstacle_field_3d creates non-overlapping obstacles."""
        obstacles = create_obstacle_field_3d(5, WIDTH, HEIGHT, DEPTH)
        
        assert len(obstacles) <= 5  # May be fewer if couldn't place all
        
        # Check no overlaps
        for i, o1 in enumerate(obstacles):
            for o2 in obstacles[i+1:]:
                dx = o1.x - o2.x
                dy = o1.y - o2.y
                dz = o1.z - o2.z
                dist = np.sqrt(dx*dx + dy*dy + dz*dz)
                min_dist = o1.radius + o2.radius + 30  # min_spacing
                assert dist >= min_dist


# =============================================================================
# Separation 3D Tests (Phase 2)
# =============================================================================

class TestSeparation3D:
    """Tests for 3D separation rule."""

    def test_no_neighbors_no_force(self):
        """No separation force when no neighbors."""
        from boids.rules3d import compute_separation_3d
        
        boid = Boid3D(400, 300, 300, 0, 0, 0)
        dv = compute_separation_3d(boid, [], protected_range=20, separation_strength=0.1)
        assert dv == (0.0, 0.0, 0.0)

    def test_neighbor_in_positive_z(self):
        """Flee from neighbor in +Z direction."""
        from boids.rules3d import compute_separation_3d
        
        boid = Boid3D(400, 300, 300, 0, 0, 0)
        neighbor = Boid3D(400, 300, 310, 0, 0, 0)  # +10 in Z
        
        dv = compute_separation_3d(boid, [neighbor], protected_range=20, separation_strength=0.1)
        
        assert dv[0] == pytest.approx(0)  # No X force
        assert dv[1] == pytest.approx(0)  # No Y force
        assert dv[2] < 0  # Flee in -Z direction

    def test_neighbor_in_negative_z(self):
        """Flee from neighbor in -Z direction."""
        from boids.rules3d import compute_separation_3d
        
        boid = Boid3D(400, 300, 300, 0, 0, 0)
        neighbor = Boid3D(400, 300, 290, 0, 0, 0)  # -10 in Z
        
        dv = compute_separation_3d(boid, [neighbor], protected_range=20, separation_strength=0.1)
        
        assert dv[2] > 0  # Flee in +Z direction

    def test_neighbor_outside_range_no_force(self):
        """No separation force for distant neighbor."""
        from boids.rules3d import compute_separation_3d
        
        boid = Boid3D(400, 300, 300, 0, 0, 0)
        neighbor = Boid3D(400, 300, 400, 0, 0, 0)  # 100 units away
        
        dv = compute_separation_3d(boid, [neighbor], protected_range=20, separation_strength=0.1)
        
        assert dv == (0.0, 0.0, 0.0)

    def test_multiple_neighbors_3d(self):
        """Force combines from multiple 3D neighbors."""
        from boids.rules3d import compute_separation_3d
        
        boid = Boid3D(400, 300, 300, 0, 0, 0)
        neighbors = [
            Boid3D(410, 300, 300, 0, 0, 0),  # +X
            Boid3D(400, 310, 300, 0, 0, 0),  # +Y
            Boid3D(400, 300, 310, 0, 0, 0),  # +Z
        ]
        
        dv = compute_separation_3d(boid, neighbors, protected_range=20, separation_strength=0.1)
        
        assert dv[0] < 0  # Flee -X
        assert dv[1] < 0  # Flee -Y
        assert dv[2] < 0  # Flee -Z


# =============================================================================
# Alignment 3D Tests
# =============================================================================

class TestAlignment3D:
    """Tests for 3D alignment rule."""

    def test_no_neighbors_no_force(self):
        """No alignment force when no neighbors."""
        from boids.rules3d import compute_alignment_3d
        
        boid = Boid3D(400, 300, 300, 1, 0, 0)
        dv = compute_alignment_3d(boid, [], alignment_factor=0.05)
        assert dv == (0.0, 0.0, 0.0)

    def test_align_with_z_velocity(self):
        """Align velocity with neighbor moving in Z."""
        from boids.rules3d import compute_alignment_3d
        
        boid = Boid3D(400, 300, 300, 0, 0, 0)  # Stationary
        neighbor = Boid3D(410, 300, 300, 0, 0, 2)  # Moving in +Z
        
        dv = compute_alignment_3d(boid, [neighbor], alignment_factor=0.1)
        
        assert dv[0] == pytest.approx(0)
        assert dv[1] == pytest.approx(0)
        assert dv[2] > 0  # Should gain +Z velocity

    def test_already_aligned_minimal_force(self):
        """Minimal force when already aligned."""
        from boids.rules3d import compute_alignment_3d
        
        boid = Boid3D(400, 300, 300, 1, 1, 1)
        neighbor = Boid3D(410, 300, 300, 1, 1, 1)  # Same velocity
        
        dv = compute_alignment_3d(boid, [neighbor], alignment_factor=0.1)
        
        assert abs(dv[0]) < 0.01
        assert abs(dv[1]) < 0.01
        assert abs(dv[2]) < 0.01


# =============================================================================
# Cohesion 3D Tests
# =============================================================================

class TestCohesion3D:
    """Tests for 3D cohesion rule."""

    def test_no_neighbors_no_force(self):
        """No cohesion force when no neighbors."""
        from boids.rules3d import compute_cohesion_3d
        
        boid = Boid3D(400, 300, 300, 0, 0, 0)
        dv = compute_cohesion_3d(boid, [], cohesion_factor=0.005)
        assert dv == (0.0, 0.0, 0.0)

    def test_move_toward_neighbor_in_z(self):
        """Move toward neighbor center of mass in Z."""
        from boids.rules3d import compute_cohesion_3d
        
        boid = Boid3D(400, 300, 300, 0, 0, 0)
        neighbor = Boid3D(400, 300, 400, 0, 0, 0)  # +100 in Z
        
        dv = compute_cohesion_3d(boid, [neighbor], cohesion_factor=0.01)
        
        assert dv[0] == pytest.approx(0)
        assert dv[1] == pytest.approx(0)
        assert dv[2] > 0  # Move toward +Z

    def test_at_center_minimal_force(self):
        """Minimal force when at center of neighbors."""
        from boids.rules3d import compute_cohesion_3d
        
        boid = Boid3D(400, 300, 300, 0, 0, 0)
        neighbors = [
            Boid3D(350, 300, 300, 0, 0, 0),
            Boid3D(450, 300, 300, 0, 0, 0),  # Average X = 400
        ]
        
        dv = compute_cohesion_3d(boid, neighbors, cohesion_factor=0.01)
        
        assert abs(dv[0]) < 0.01


# =============================================================================
# Boundary Steering 3D Tests
# =============================================================================

class TestBoundarySteering3D:
    """Tests for 3D boundary steering."""

    def test_center_no_force(self):
        """No force when boid is in center of volume."""
        from boids.rules3d import apply_boundary_steering_3d
        
        boid = Boid3D(400, 300, 300, 0, 0, 0)  # Center
        dv = apply_boundary_steering_3d(boid, WIDTH, HEIGHT, DEPTH, MARGIN, 0.2)
        
        assert dv == (0.0, 0.0, 0.0)

    def test_near_z_min_boundary(self):
        """Steer away from Z=0 boundary."""
        from boids.rules3d import apply_boundary_steering_3d
        
        boid = Boid3D(400, 300, 10, 0, 0, 0)  # Near z=0
        dv = apply_boundary_steering_3d(boid, WIDTH, HEIGHT, DEPTH, MARGIN, 0.2)
        
        assert dv[0] == pytest.approx(0)
        assert dv[1] == pytest.approx(0)
        assert dv[2] > 0  # Push toward +Z

    def test_near_z_max_boundary(self):
        """Steer away from Z=depth boundary."""
        from boids.rules3d import apply_boundary_steering_3d
        
        boid = Boid3D(400, 300, 590, 0, 0, 0)  # Near z=600
        dv = apply_boundary_steering_3d(boid, WIDTH, HEIGHT, DEPTH, MARGIN, 0.2)
        
        assert dv[2] < 0  # Push toward -Z

    def test_corner_all_forces(self):
        """All three forces active in corner."""
        from boids.rules3d import apply_boundary_steering_3d
        
        boid = Boid3D(10, 10, 10, 0, 0, 0)  # Near (0,0,0) corner
        dv = apply_boundary_steering_3d(boid, WIDTH, HEIGHT, DEPTH, MARGIN, 0.2)
        
        assert dv[0] > 0  # Push +X
        assert dv[1] > 0  # Push +Y
        assert dv[2] > 0  # Push +Z

    def test_progressive_steering(self):
        """Force increases with distance past margin."""
        from boids.rules3d import apply_boundary_steering_3d
        
        boid1 = Boid3D(400, 300, 50, 0, 0, 0)  # 25 into margin
        boid2 = Boid3D(400, 300, 10, 0, 0, 0)  # 65 into margin
        
        dv1 = apply_boundary_steering_3d(boid1, WIDTH, HEIGHT, DEPTH, MARGIN, 0.2)
        dv2 = apply_boundary_steering_3d(boid2, WIDTH, HEIGHT, DEPTH, MARGIN, 0.2)
        
        assert dv2[2] > dv1[2]  # Deeper = stronger


# =============================================================================
# Predator Avoidance 3D Tests
# =============================================================================

class TestPredatorAvoidance3D:
    """Tests for 3D predator avoidance."""

    def test_no_predator_no_force(self):
        """No avoidance force when no predators."""
        from boids.rules3d import compute_predator_avoidance_3d
        
        boid = Boid3D(400, 300, 300, 0, 0, 0)
        dv = compute_predator_avoidance_3d(boid, [], detection_range=100, avoidance_strength=0.5)
        assert dv == (0.0, 0.0, 0.0)

    def test_flee_from_predator_in_z(self):
        """Flee from predator in Z dimension."""
        from boids.rules3d import compute_predator_avoidance_3d
        
        boid = Boid3D(400, 300, 300, 0, 0, 0)
        predator_pos = [(400, 300, 350)]  # +50 in Z
        
        dv = compute_predator_avoidance_3d(boid, predator_pos, detection_range=100, avoidance_strength=0.5)
        
        assert dv[2] < 0  # Flee in -Z direction

    def test_predator_outside_range_no_force(self):
        """No avoidance when predator outside detection range."""
        from boids.rules3d import compute_predator_avoidance_3d
        
        boid = Boid3D(400, 300, 300, 0, 0, 0)
        predator_pos = [(400, 300, 500)]  # 200 units away
        
        dv = compute_predator_avoidance_3d(boid, predator_pos, detection_range=100, avoidance_strength=0.5)
        assert dv == (0.0, 0.0, 0.0)


# =============================================================================
# Obstacle Avoidance 3D Tests
# =============================================================================

class TestObstacleAvoidance3D:
    """Tests for 3D obstacle avoidance."""

    def test_no_obstacle_no_force(self):
        """No avoidance force when no obstacles."""
        from boids.rules3d import compute_obstacle_avoidance_3d
        
        dv = compute_obstacle_avoidance_3d(400, 300, 300, [], detection_range=50, avoidance_strength=0.5)
        assert dv == (0.0, 0.0, 0.0)

    def test_avoid_sphere_in_z(self):
        """Avoid spherical obstacle in Z dimension."""
        from boids.rules3d import compute_obstacle_avoidance_3d
        
        obstacle = Obstacle3D(400, 300, 350, radius=30)  # Sphere at z=350
        
        dv = compute_obstacle_avoidance_3d(400, 300, 300, [obstacle], detection_range=50, avoidance_strength=0.5)
        
        assert dv[2] < 0  # Flee in -Z direction


# =============================================================================
# KDTree 3D Tests
# =============================================================================

class TestKDTree3D:
    """Tests for 3D KDTree neighbor finding."""

    def test_kdtree_finds_z_neighbors(self):
        """KDTree finds neighbors close in Z dimension."""
        from boids.flock3d import Flock3D, SimulationParams3D
        
        params = SimulationParams3D(width=WIDTH, height=HEIGHT, depth=DEPTH)
        flock = Flock3D(num_boids=10, params=params)
        
        # Place boids: one at center, one close in Z only
        flock.boids[0].x, flock.boids[0].y, flock.boids[0].z = 400, 300, 300
        flock.boids[1].x, flock.boids[1].y, flock.boids[1].z = 400, 300, 310  # 10 units in Z
        
        # Others far away
        for i in range(2, 10):
            flock.boids[i].x = 100
            flock.boids[i].y = 100
            flock.boids[i].z = 100
        
        flock._rebuild_kdtree()
        
        # Query neighbors within range 20
        indices = flock._kdtree.query_ball_point([400, 300, 300], r=20)
        
        assert 0 in indices
        assert 1 in indices
        assert len(indices) == 2

    def test_kdtree_excludes_far_z(self):
        """KDTree excludes boids far in Z even if close in XY."""
        from boids.flock3d import Flock3D, SimulationParams3D
        
        params = SimulationParams3D(width=WIDTH, height=HEIGHT, depth=DEPTH)
        flock = Flock3D(num_boids=3, params=params)
        
        flock.boids[0].x, flock.boids[0].y, flock.boids[0].z = 400, 300, 300
        flock.boids[1].x, flock.boids[1].y, flock.boids[1].z = 400, 300, 500  # Same XY, far Z
        flock.boids[2].x, flock.boids[2].y, flock.boids[2].z = 100, 100, 100
        
        flock._rebuild_kdtree()
        
        indices = flock._kdtree.query_ball_point([400, 300, 300], r=50)
        
        assert 0 in indices
        assert 1 not in indices  # 200 units away in Z


# =============================================================================
# Flock3D Integration Tests
# =============================================================================

class TestFlock3DIntegration:
    """Integration tests for Flock3D."""

    def test_boids_stay_in_3d_bounds(self):
        """All boids stay within 3D bounds."""
        from boids.flock3d import Flock3D, SimulationParams3D
        
        params = SimulationParams3D(width=WIDTH, height=HEIGHT, depth=DEPTH)
        flock = Flock3D(num_boids=50, params=params)
        
        for _ in range(500):
            flock.update()
            
            for boid in flock.boids:
                assert 0 <= boid.x <= WIDTH, f"X out of bounds: {boid.x}"
                assert 0 <= boid.y <= HEIGHT, f"Y out of bounds: {boid.y}"
                assert 0 <= boid.z <= DEPTH, f"Z out of bounds: {boid.z}"

    def test_predator_hunts_in_z(self):
        """Predator moves toward boids in Z dimension."""
        from boids.flock3d import Flock3D, SimulationParams3D
        
        params = SimulationParams3D(width=WIDTH, height=HEIGHT, depth=DEPTH)
        flock = Flock3D(num_boids=20, params=params, enable_predator=True, num_predators=1)
        
        # Predator at z=100, boids at z=500
        flock.predators[0].x = 400
        flock.predators[0].y = 300
        flock.predators[0].z = 100
        
        for boid in flock.boids:
            boid.x = 400
            boid.y = 300
            boid.z = 500
        
        initial_z = flock.predators[0].z
        
        for _ in range(100):
            flock.update()
        
        # Predator should have moved toward boids in Z
        assert flock.predators[0].z > initial_z + 50

    def test_flock_cohesion_in_3d(self):
        """Flock maintains cohesion in 3D space."""
        from boids.flock3d import Flock3D, SimulationParams3D
        
        params = SimulationParams3D(width=WIDTH, height=HEIGHT, depth=DEPTH)
        flock = Flock3D(num_boids=30, params=params)
        
        # Run simulation
        for _ in range(200):
            flock.update()
        
        # Calculate 3D dispersion
        positions = np.array([[b.x, b.y, b.z] for b in flock.boids])
        center = positions.mean(axis=0)
        distances = np.sqrt(((positions - center) ** 2).sum(axis=1))
        
        # Flock should have reasonable dispersion (not infinitely spread)
        assert distances.max() < 500  # Reasonable threshold for 3D space

    def test_all_predator_strategies_work_3d(self):
        """All 5 predator hunting strategies work in 3D."""
        from boids.flock3d import Flock3D, SimulationParams3D
        
        params = SimulationParams3D(width=WIDTH, height=HEIGHT, depth=DEPTH)
        flock = Flock3D(num_boids=30, params=params, enable_predator=True, num_predators=5)
        
        # Should have all 5 strategies
        strategies = [p.strategy for p in flock.predators]
        assert len(set(strategies)) == 5
        
        # Simulation should run without errors
        for _ in range(200):
            flock.update()
        
        # All predators should be within bounds
        for pred in flock.predators:
            assert 0 <= pred.z <= DEPTH


# =============================================================================
# Regression Tests
# =============================================================================

class TestRegression3D:
    """Regression tests to ensure 2D behavior is preserved."""

    def test_2d_plane_behavior(self):
        """
        When all boids are at z=depth/2 with vz=0,
        behavior should match 2D simulation.
        """
        from boids.flock3d import Flock3D, SimulationParams3D
        
        params = SimulationParams3D(width=WIDTH, height=HEIGHT, depth=DEPTH)
        flock = Flock3D(num_boids=30, params=params)
        
        # Force all boids to z=300, vz=0
        for boid in flock.boids:
            boid.z = 300
            boid.vz = 0
        
        # Run simulation
        for _ in range(100):
            flock.update()
        
        # Boids should mostly stay near z=300 (small drift allowed)
        for boid in flock.boids:
            assert 200 < boid.z < 400  # Reasonable range around z=300


if __name__ == "__main__":
    pytest.main([__file__, "-v"])