"""
Obstacle3D class for 3D Boids simulation.

Spherical obstacles that boids must avoid in 3D space.
"""

import numpy as np
from dataclasses import dataclass
from typing import List


@dataclass
class Obstacle3D:
    """
    A spherical obstacle in 3D space.
    
    Attributes:
        x: center x position (pixels)
        y: center y position (pixels)
        z: center z position (pixels)
        radius: sphere radius (pixels)
    """
    x: float
    y: float
    z: float
    radius: float
    
    @property
    def position(self) -> np.ndarray:
        """Return position as numpy array [x, y, z]."""
        return np.array([self.x, self.y, self.z])
    
    @classmethod
    def create_random(
        cls,
        width: float,
        height: float,
        depth: float,
        min_radius: float = 20,
        max_radius: float = 50,
        margin: float = 50
    ) -> "Obstacle3D":
        """
        Factory method to create an obstacle at a random position.
        
        Args:
            width, height, depth: simulation bounds
            min_radius: minimum obstacle radius
            max_radius: maximum obstacle radius
            margin: distance from edges to avoid placing obstacles
            
        Returns:
            A new Obstacle3D at a random position
        """
        radius = np.random.uniform(min_radius, max_radius)
        
        # Position away from edges
        x = np.random.uniform(margin + radius, width - margin - radius)
        y = np.random.uniform(margin + radius, height - margin - radius)
        z = np.random.uniform(margin + radius, depth - margin - radius)
        
        return cls(x=x, y=y, z=z, radius=radius)
    
    @classmethod
    def create_at_position(
        cls,
        x: float,
        y: float,
        z: float,
        radius: float = 30
    ) -> "Obstacle3D":
        """
        Factory method to create an obstacle at a specific position.
        
        Args:
            x, y, z: center position
            radius: sphere radius
            
        Returns:
            A new Obstacle3D at the specified position
        """
        return cls(x=x, y=y, z=z, radius=radius)
    
    def contains_point(self, x: float, y: float, z: float) -> bool:
        """Check if a point is inside the obstacle sphere."""
        dx = x - self.x
        dy = y - self.y
        dz = z - self.z
        dist_sq = dx*dx + dy*dy + dz*dz
        return dist_sq <= self.radius * self.radius
    
    def distance_to_surface(self, x: float, y: float, z: float) -> float:
        """
        Calculate signed distance to obstacle surface.
        
        Negative values mean inside the obstacle.
        
        Args:
            x, y, z: point position
            
        Returns:
            Signed distance to surface
        """
        dx = x - self.x
        dy = y - self.y
        dz = z - self.z
        dist = np.sqrt(dx*dx + dy*dy + dz*dz)
        return dist - self.radius
    
    def to_list(self) -> list:
        """Convert to list for JSON serialization [x, y, z, radius]."""
        return [self.x, self.y, self.z, self.radius]


def create_obstacle_field_3d(
    num_obstacles: int,
    width: float,
    height: float,
    depth: float,
    min_radius: float = 20,
    max_radius: float = 50,
    min_spacing: float = 30
) -> List[Obstacle3D]:
    """
    Create multiple non-overlapping spherical obstacles.
    
    Args:
        num_obstacles: number of obstacles to create
        width, height, depth: simulation bounds
        min_radius, max_radius: obstacle size range
        min_spacing: minimum distance between obstacle surfaces
        
    Returns:
        List of Obstacle3D objects
    """
    obstacles = []
    max_attempts = 100
    
    for _ in range(num_obstacles):
        for attempt in range(max_attempts):
            candidate = Obstacle3D.create_random(
                width, height, depth, min_radius, max_radius
            )
            
            # Check for overlap with existing obstacles
            overlaps = False
            for existing in obstacles:
                dx = candidate.x - existing.x
                dy = candidate.y - existing.y
                dz = candidate.z - existing.z
                dist = np.sqrt(dx*dx + dy*dy + dz*dz)
                min_dist = candidate.radius + existing.radius + min_spacing
                
                if dist < min_dist:
                    overlaps = True
                    break
            
            if not overlaps:
                obstacles.append(candidate)
                break
    
    return obstacles