"""
Boids simulation package.

Core simulation code for the Boids flocking algorithm.
"""

from .boid import Boid
from .predator import Predator
from .flock import Flock, SimulationParams
from .flock_optimized import FlockOptimized
from .metrics import (
    compute_avg_distance_to_predator,
    compute_min_distance_to_predator,
    compute_flock_cohesion,
    MetricsCollector,
)

__all__ = [
    "Boid",
    "Predator",
    "Flock",
    "FlockOptimized",
    "SimulationParams",
    "compute_avg_distance_to_predator",
    "compute_min_distance_to_predator",
    "compute_flock_cohesion",
    "MetricsCollector",
]