"""
Obstacle module for the Boids simulation.

Defines static obstacles that boids must navigate around.
"""

from dataclasses import dataclass
from typing import List, Tuple
import math


@dataclass
class Obstacle:
    """
    A circular static obstacle.
    
    Attributes:
        x: X position (center)
        y: Y position (center)
        radius: Obstacle radius in pixels
    """
    x: float
    y: float
    radius: float = 30.0

    def contains_point(self, px: float, py: float) -> bool:
        """Check if a point is inside the obstacle."""
        dx = px - self.x
        dy = py - self.y
        return (dx * dx + dy * dy) <= (self.radius * self.radius)

    def distance_to_point(self, px: float, py: float) -> float:
        """
        Distance from point to obstacle surface.
        
        Returns:
            Positive if outside, negative if inside
        """
        dx = px - self.x
        dy = py - self.y
        center_dist = math.sqrt(dx * dx + dy * dy)
        return center_dist - self.radius

    def avoidance_vector(self, px: float, py: float, detection_range: float = 50.0) -> Tuple[float, float]:
        """
        Compute avoidance steering vector for a point near this obstacle.
        
        Args:
            px, py: Point position
            detection_range: Distance at which avoidance starts
            
        Returns:
            (vx, vy) steering vector pointing away from obstacle.
            Magnitude is stronger when closer. (0, 0) if out of range.
        """
        dx = px - self.x
        dy = py - self.y
        center_dist = math.sqrt(dx * dx + dy * dy)
        
        # Distance to surface
        surface_dist = center_dist - self.radius
        
        # If inside obstacle, strong push out
        if surface_dist <= 0:
            if center_dist < 0.001:
                # At center, push in random direction
                return (1.0, 0.0)
            # Normalize and scale strongly
            scale = 2.0
            return (dx / center_dist * scale, dy / center_dist * scale)
        
        # If outside detection range, no avoidance
        if surface_dist > detection_range:
            return (0.0, 0.0)
        
        # Gradual avoidance: stronger when closer
        # Strength: 1.0 at surface, 0.0 at detection_range
        strength = 1.0 - (surface_dist / detection_range)
        
        # Direction: away from obstacle center
        if center_dist < 0.001:
            return (0.0, 0.0)
        
        nx = dx / center_dist
        ny = dy / center_dist
        
        return (nx * strength, ny * strength)


def compute_obstacle_avoidance(
    boid_x: float,
    boid_y: float,
    obstacles: List[Obstacle],
    detection_range: float = 50.0,
    avoidance_strength: float = 0.5
) -> Tuple[float, float]:
    """
    Compute total obstacle avoidance steering for a boid.
    
    Args:
        boid_x, boid_y: Boid position
        obstacles: List of obstacles
        detection_range: Distance at which avoidance starts
        avoidance_strength: Multiplier for avoidance force
        
    Returns:
        (vx, vy) total steering vector
    """
    total_vx = 0.0
    total_vy = 0.0
    
    for obstacle in obstacles:
        vx, vy = obstacle.avoidance_vector(boid_x, boid_y, detection_range)
        total_vx += vx
        total_vy += vy
    
    return (total_vx * avoidance_strength, total_vy * avoidance_strength)