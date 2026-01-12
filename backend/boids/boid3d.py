"""
Boid3D class for 3D Boids simulation.

A boid is an individual agent that follows simple rules to create
emergent flocking behavior in 3D space.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Boid3D:
    """
    A boid agent in 3D space.
    
    Attributes:
        x: horizontal position (pixels)
        y: vertical position (pixels)
        z: depth position (pixels)
        vx: horizontal velocity (pixels/frame)
        vy: vertical velocity (pixels/frame)
        vz: depth velocity (pixels/frame)
    """
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    
    @property
    def position(self) -> np.ndarray:
        """Return position as numpy array [x, y, z]."""
        return np.array([self.x, self.y, self.z])
    
    @property
    def velocity(self) -> np.ndarray:
        """Return velocity as numpy array [vx, vy, vz]."""
        return np.array([self.vx, self.vy, self.vz])
    
    @property
    def speed(self) -> float:
        """Calculate current speed magnitude in 3D."""
        return np.sqrt(self.vx * self.vx + self.vy * self.vy + self.vz * self.vz)
    
    @classmethod
    def create_random(
        cls,
        width: float,
        height: float,
        depth: float,
        max_speed: float = 3.0
    ) -> "Boid3D":
        """
        Factory method to create a boid at a random position with random velocity.
        
        Args:
            width: simulation width (x bounds)
            height: simulation height (y bounds)
            depth: simulation depth (z bounds)
            max_speed: maximum initial speed
            
        Returns:
            A new Boid3D with random position and velocity
        """
        # Random position within bounds
        x = np.random.uniform(0, width)
        y = np.random.uniform(0, height)
        z = np.random.uniform(0, depth)
        
        # Random velocity direction (uniform on sphere)
        # Using spherical coordinates for uniform distribution
        theta = np.random.uniform(0, 2 * np.pi)  # Azimuthal angle
        phi = np.arccos(np.random.uniform(-1, 1))  # Polar angle (uniform in cos)
        
        # Random speed
        speed = np.random.uniform(0, max_speed)
        
        # Convert to Cartesian
        vx = speed * np.sin(phi) * np.cos(theta)
        vy = speed * np.sin(phi) * np.sin(theta)
        vz = speed * np.cos(phi)
        
        return cls(x=x, y=y, z=z, vx=vx, vy=vy, vz=vz)
    
    @classmethod
    def create_at_position(
        cls,
        x: float,
        y: float,
        z: float,
        speed: float = 3.0,
        direction: Tuple[float, float, float] = None
    ) -> "Boid3D":
        """
        Factory method to create a boid at a specific position.
        
        Args:
            x: horizontal position
            y: vertical position
            z: depth position
            speed: initial speed magnitude
            direction: (dx, dy, dz) direction vector (will be normalized)
                      If None, uses random direction
            
        Returns:
            A new Boid3D at the specified position
        """
        if direction is None:
            # Random direction
            theta = np.random.uniform(0, 2 * np.pi)
            phi = np.arccos(np.random.uniform(-1, 1))
            vx = speed * np.sin(phi) * np.cos(theta)
            vy = speed * np.sin(phi) * np.sin(theta)
            vz = speed * np.cos(phi)
        else:
            # Normalize and scale
            dx, dy, dz = direction
            magnitude = np.sqrt(dx*dx + dy*dy + dz*dz)
            if magnitude > 0:
                vx = (dx / magnitude) * speed
                vy = (dy / magnitude) * speed
                vz = (dz / magnitude) * speed
            else:
                vx, vy, vz = speed, 0, 0
        
        return cls(x=x, y=y, z=z, vx=vx, vy=vy, vz=vz)
    
    def to_list(self) -> list:
        """Convert to list for JSON serialization [x, y, z, vx, vy, vz]."""
        return [self.x, self.y, self.z, self.vx, self.vy, self.vz]
    
    def distance_to(self, other: "Boid3D") -> float:
        """Calculate Euclidean distance to another boid."""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return np.sqrt(dx*dx + dy*dy + dz*dz)
    
    def distance_to_point(self, x: float, y: float, z: float) -> float:
        """Calculate Euclidean distance to a point."""
        dx = self.x - x
        dy = self.y - y
        dz = self.z - z
        return np.sqrt(dx*dx + dy*dy + dz*dz)


def distance_3d(a: Boid3D, b: Boid3D) -> float:
    """
    Calculate Euclidean distance between two boids in 3D space.
    
    Args:
        a: First boid
        b: Second boid
        
    Returns:
        Distance in pixels
    """
    dx = a.x - b.x
    dy = a.y - b.y
    dz = a.z - b.z
    return np.sqrt(dx*dx + dy*dy + dz*dz)