"""
3D Physics Rules for Boids Simulation.

Implements the core flocking behaviors in 3D space:
- Separation: Avoid crowding neighbors
- Alignment: Steer toward average heading of neighbors
- Cohesion: Steer toward center of mass of neighbors
- Boundary steering: Stay within simulation bounds
- Predator avoidance: Flee from predators
- Obstacle avoidance: Avoid spherical obstacles
"""

import numpy as np
from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .boid3d import Boid3D
    from .predator3d import Predator3D
    from .obstacle3d import Obstacle3D


# =============================================================================
# Separation Rule
# =============================================================================

def compute_separation_3d(
    boid: "Boid3D",
    neighbors: List["Boid3D"],
    protected_range: float,
    separation_strength: float
) -> Tuple[float, float, float]:
    """
    Compute separation force to avoid crowding neighbors in 3D.
    
    Boids steer away from neighbors that are too close.
    
    Args:
        boid: The boid to compute force for
        neighbors: List of neighboring boids (already filtered by visual range)
        protected_range: Distance at which separation activates
        separation_strength: Multiplier for separation force
        
    Returns:
        Tuple (dvx, dvy, dvz) velocity adjustment
    """
    dvx, dvy, dvz = 0.0, 0.0, 0.0
    
    for other in neighbors:
        if other is boid:
            continue
            
        dx = boid.x - other.x
        dy = boid.y - other.y
        dz = boid.z - other.z
        dist_sq = dx*dx + dy*dy + dz*dz
        
        if dist_sq > 0 and dist_sq < protected_range * protected_range:
            # Weight by inverse distance (closer = stronger)
            dvx += dx * separation_strength
            dvy += dy * separation_strength
            dvz += dz * separation_strength
    
    return (dvx, dvy, dvz)


# =============================================================================
# Alignment Rule
# =============================================================================

def compute_alignment_3d(
    boid: "Boid3D",
    neighbors: List["Boid3D"],
    alignment_factor: float
) -> Tuple[float, float, float]:
    """
    Compute alignment force to match velocity with neighbors in 3D.
    
    Boids steer toward the average heading of nearby flockmates.
    
    Args:
        boid: The boid to compute force for
        neighbors: List of neighboring boids
        alignment_factor: Multiplier for alignment force
        
    Returns:
        Tuple (dvx, dvy, dvz) velocity adjustment
    """
    if not neighbors:
        return (0.0, 0.0, 0.0)
    
    # Compute average velocity of neighbors
    avg_vx = 0.0
    avg_vy = 0.0
    avg_vz = 0.0
    count = 0
    
    for other in neighbors:
        if other is not boid:
            avg_vx += other.vx
            avg_vy += other.vy
            avg_vz += other.vz
            count += 1
    
    if count == 0:
        return (0.0, 0.0, 0.0)
    
    avg_vx /= count
    avg_vy /= count
    avg_vz /= count
    
    # Steer toward average velocity
    dvx = (avg_vx - boid.vx) * alignment_factor
    dvy = (avg_vy - boid.vy) * alignment_factor
    dvz = (avg_vz - boid.vz) * alignment_factor
    
    return (dvx, dvy, dvz)


# =============================================================================
# Cohesion Rule
# =============================================================================

def compute_cohesion_3d(
    boid: "Boid3D",
    neighbors: List["Boid3D"],
    cohesion_factor: float
) -> Tuple[float, float, float]:
    """
    Compute cohesion force to move toward center of mass of neighbors in 3D.
    
    Boids steer toward the average position of nearby flockmates.
    
    Args:
        boid: The boid to compute force for
        neighbors: List of neighboring boids
        cohesion_factor: Multiplier for cohesion force
        
    Returns:
        Tuple (dvx, dvy, dvz) velocity adjustment
    """
    if not neighbors:
        return (0.0, 0.0, 0.0)
    
    # Compute center of mass
    center_x = 0.0
    center_y = 0.0
    center_z = 0.0
    count = 0
    
    for other in neighbors:
        if other is not boid:
            center_x += other.x
            center_y += other.y
            center_z += other.z
            count += 1
    
    if count == 0:
        return (0.0, 0.0, 0.0)
    
    center_x /= count
    center_y /= count
    center_z /= count
    
    # Steer toward center of mass
    dvx = (center_x - boid.x) * cohesion_factor
    dvy = (center_y - boid.y) * cohesion_factor
    dvz = (center_z - boid.z) * cohesion_factor
    
    return (dvx, dvy, dvz)


# =============================================================================
# Boundary Steering
# =============================================================================

def apply_boundary_steering_3d(
    boid: "Boid3D",
    width: float,
    height: float,
    depth: float,
    margin: float,
    turn_factor: float
) -> Tuple[float, float, float]:
    """
    Compute boundary steering to keep boid within 3D bounds.
    
    Uses progressive steering that increases with distance past margin.
    Applies to all 6 faces of the bounding box.
    
    Args:
        boid: The boid to compute force for
        width: Simulation width (X bounds: 0 to width)
        height: Simulation height (Y bounds: 0 to height)
        depth: Simulation depth (Z bounds: 0 to depth)
        margin: Distance from edge to start turning
        turn_factor: Base steering strength at boundaries
        
    Returns:
        Tuple (dvx, dvy, dvz) velocity adjustment
    """
    dvx, dvy, dvz = 0.0, 0.0, 0.0
    
    # X boundaries (left/right)
    if boid.x < margin:
        distance_into_margin = margin - boid.x
        scale = 1.0 + (distance_into_margin / margin)
        dvx += turn_factor * scale
    elif boid.x > width - margin:
        distance_into_margin = boid.x - (width - margin)
        scale = 1.0 + (distance_into_margin / margin)
        dvx -= turn_factor * scale
    
    # Y boundaries (top/bottom)
    if boid.y < margin:
        distance_into_margin = margin - boid.y
        scale = 1.0 + (distance_into_margin / margin)
        dvy += turn_factor * scale
    elif boid.y > height - margin:
        distance_into_margin = boid.y - (height - margin)
        scale = 1.0 + (distance_into_margin / margin)
        dvy -= turn_factor * scale
    
    # Z boundaries (front/back) - NEW for 3D
    if boid.z < margin:
        distance_into_margin = margin - boid.z
        scale = 1.0 + (distance_into_margin / margin)
        dvz += turn_factor * scale
    elif boid.z > depth - margin:
        distance_into_margin = boid.z - (depth - margin)
        scale = 1.0 + (distance_into_margin / margin)
        dvz -= turn_factor * scale
    
    return (dvx, dvy, dvz)


def apply_boundary_steering_3d_point(
    x: float, y: float, z: float,
    width: float,
    height: float,
    depth: float,
    margin: float,
    turn_factor: float
) -> Tuple[float, float, float]:
    """
    Compute boundary steering for a point (used by predators).
    
    Same as apply_boundary_steering_3d but takes coordinates directly.
    """
    dvx, dvy, dvz = 0.0, 0.0, 0.0
    
    # X boundaries
    if x < margin:
        distance_into_margin = margin - x
        scale = 1.0 + (distance_into_margin / margin)
        dvx += turn_factor * scale
    elif x > width - margin:
        distance_into_margin = x - (width - margin)
        scale = 1.0 + (distance_into_margin / margin)
        dvx -= turn_factor * scale
    
    # Y boundaries
    if y < margin:
        distance_into_margin = margin - y
        scale = 1.0 + (distance_into_margin / margin)
        dvy += turn_factor * scale
    elif y > height - margin:
        distance_into_margin = y - (height - margin)
        scale = 1.0 + (distance_into_margin / margin)
        dvy -= turn_factor * scale
    
    # Z boundaries
    if z < margin:
        distance_into_margin = margin - z
        scale = 1.0 + (distance_into_margin / margin)
        dvz += turn_factor * scale
    elif z > depth - margin:
        distance_into_margin = z - (depth - margin)
        scale = 1.0 + (distance_into_margin / margin)
        dvz -= turn_factor * scale
    
    return (dvx, dvy, dvz)


# =============================================================================
# Predator Avoidance
# =============================================================================

def compute_predator_avoidance_3d(
    boid: "Boid3D",
    predator_positions: List[Tuple[float, float, float]],
    detection_range: float,
    avoidance_strength: float
) -> Tuple[float, float, float]:
    """
    Compute force to flee from predators in 3D space.
    
    Force is stronger when predator is closer, and directed away from predator.
    
    Args:
        boid: The boid to compute force for
        predator_positions: List of (x, y, z) predator positions
        detection_range: Distance at which boid detects predator
        avoidance_strength: Multiplier for avoidance force
        
    Returns:
        Tuple (dvx, dvy, dvz) velocity adjustment
    """
    dvx, dvy, dvz = 0.0, 0.0, 0.0
    
    for px, py, pz in predator_positions:
        dx = boid.x - px
        dy = boid.y - py
        dz = boid.z - pz
        dist = np.sqrt(dx*dx + dy*dy + dz*dz)
        
        if dist < detection_range and dist > 0:
            # Strength decreases with distance
            strength = avoidance_strength * (1 - dist / detection_range)
            
            # Normalize direction and apply strength
            dvx += (dx / dist) * strength
            dvy += (dy / dist) * strength
            dvz += (dz / dist) * strength
    
    return (dvx, dvy, dvz)


def compute_predator_avoidance_3d_from_predators(
    boid: "Boid3D",
    predators: List["Predator3D"],
    detection_range: float,
    avoidance_strength: float
) -> Tuple[float, float, float]:
    """
    Compute predator avoidance directly from Predator3D objects.
    
    Convenience wrapper that extracts positions from predators.
    """
    positions = [(p.x, p.y, p.z) for p in predators]
    return compute_predator_avoidance_3d(boid, positions, detection_range, avoidance_strength)


# =============================================================================
# Obstacle Avoidance
# =============================================================================

def compute_obstacle_avoidance_3d(
    x: float, y: float, z: float,
    obstacles: List["Obstacle3D"],
    detection_range: float,
    avoidance_strength: float
) -> Tuple[float, float, float]:
    """
    Compute force to avoid spherical obstacles in 3D space.
    
    Force is directed away from obstacle center, stronger when closer.
    
    Args:
        x, y, z: Position of agent
        obstacles: List of Obstacle3D objects
        detection_range: Base detection range (added to obstacle radius)
        avoidance_strength: Multiplier for avoidance force
        
    Returns:
        Tuple (dvx, dvy, dvz) velocity adjustment
    """
    dvx, dvy, dvz = 0.0, 0.0, 0.0
    
    for obs in obstacles:
        dx = x - obs.x
        dy = y - obs.y
        dz = z - obs.z
        dist = np.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Effective range includes obstacle radius
        effective_range = detection_range + obs.radius
        
        if dist < effective_range and dist > 0:
            # Strength increases as we get closer to obstacle surface
            # Maximum at obstacle surface, zero at effective_range
            surface_dist = dist - obs.radius
            if surface_dist < 0:
                # Inside obstacle - maximum avoidance
                strength = avoidance_strength * 2.0
            else:
                # Outside but within range
                strength = avoidance_strength * (1 - surface_dist / detection_range)
            
            # Normalize direction and apply strength
            dvx += (dx / dist) * strength
            dvy += (dy / dist) * strength
            dvz += (dz / dist) * strength
    
    return (dvx, dvy, dvz)


def compute_obstacle_avoidance_3d_for_boid(
    boid: "Boid3D",
    obstacles: List["Obstacle3D"],
    detection_range: float,
    avoidance_strength: float
) -> Tuple[float, float, float]:
    """
    Compute obstacle avoidance for a Boid3D object.
    
    Convenience wrapper that extracts position from boid.
    """
    return compute_obstacle_avoidance_3d(
        boid.x, boid.y, boid.z,
        obstacles, detection_range, avoidance_strength
    )


# =============================================================================
# Combined Forces
# =============================================================================

def compute_all_forces_3d(
    boid: "Boid3D",
    neighbors: List["Boid3D"],
    predators: List["Predator3D"],
    obstacles: List["Obstacle3D"],
    # Flocking parameters
    protected_range: float,
    separation_strength: float,
    alignment_factor: float,
    cohesion_factor: float,
    # Boundary parameters
    width: float,
    height: float,
    depth: float,
    margin: float,
    turn_factor: float,
    # Predator parameters
    predator_detection_range: float,
    predator_avoidance_strength: float,
    # Obstacle parameters
    obstacle_detection_range: float = 50.0,
    obstacle_avoidance_strength: float = 0.5,
) -> Tuple[float, float, float]:
    """
    Compute all forces acting on a boid in 3D.
    
    Combines: separation, alignment, cohesion, boundary steering,
    predator avoidance, and obstacle avoidance.
    
    Args:
        boid: The boid to compute forces for
        neighbors: Nearby boids
        predators: Active predators
        obstacles: Obstacles to avoid
        ... various parameters ...
        
    Returns:
        Tuple (dvx, dvy, dvz) total velocity adjustment
    """
    # Initialize
    dvx, dvy, dvz = 0.0, 0.0, 0.0
    
    # Separation
    sep = compute_separation_3d(boid, neighbors, protected_range, separation_strength)
    dvx += sep[0]
    dvy += sep[1]
    dvz += sep[2]
    
    # Alignment
    ali = compute_alignment_3d(boid, neighbors, alignment_factor)
    dvx += ali[0]
    dvy += ali[1]
    dvz += ali[2]
    
    # Cohesion
    coh = compute_cohesion_3d(boid, neighbors, cohesion_factor)
    dvx += coh[0]
    dvy += coh[1]
    dvz += coh[2]
    
    # Boundary steering
    bnd = apply_boundary_steering_3d(boid, width, height, depth, margin, turn_factor)
    dvx += bnd[0]
    dvy += bnd[1]
    dvz += bnd[2]
    
    # Predator avoidance
    if predators:
        pred = compute_predator_avoidance_3d_from_predators(
            boid, predators, predator_detection_range, predator_avoidance_strength
        )
        dvx += pred[0]
        dvy += pred[1]
        dvz += pred[2]
    
    # Obstacle avoidance
    if obstacles:
        obs = compute_obstacle_avoidance_3d_for_boid(
            boid, obstacles, obstacle_detection_range, obstacle_avoidance_strength
        )
        dvx += obs[0]
        dvy += obs[1]
        dvz += obs[2]
    
    return (dvx, dvy, dvz)