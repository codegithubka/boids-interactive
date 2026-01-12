"""
Boids simulation package.

Core simulation code for the Boids flocking algorithm.
Supports both 2D and 3D simulations.
"""

from .boid import Boid
from .predator import Predator, HuntingStrategy
from .flock import Flock, SimulationParams
from .flock_optimized import FlockOptimized
from .obstacle import Obstacle, compute_obstacle_avoidance
from .metrics import (
    compute_avg_distance_to_predator,
    compute_min_distance_to_predator,
    compute_flock_cohesion,
    MetricsCollector,
)

# 3D classes
from .boid3d import Boid3D, distance_3d
from .predator3d import Predator3D
from .obstacle3d import Obstacle3D, create_obstacle_field_3d

__all__ = [
    # 2D classes
    "Boid",
    "Predator",
    "HuntingStrategy",
    "Flock",
    "FlockOptimized",
    "SimulationParams",
    "Obstacle",
    "compute_obstacle_avoidance",
    "compute_avg_distance_to_predator",
    "compute_min_distance_to_predator",
    "compute_flock_cohesion",
    "MetricsCollector",
    # 3D classes
    "Boid3D",
    "distance_3d",
    "Predator3D",
    "Obstacle3D",
    "create_obstacle_field_3d",
]