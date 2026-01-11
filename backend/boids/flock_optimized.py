"""
Optimized Flock class using KDTree for spatial queries.

This module provides FlockOptimized which uses scipy.spatial.KDTree
for O(n log n) neighbor finding instead of O(n²) naive iteration.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Tuple
from .boid import Boid
from .predator import Predator
from .flock import SimulationParams
from .obstacle import Obstacle, compute_obstacle_avoidance
from .rules_optimized import (
    FlockState, 
    compute_all_rules_kdtree, 
    compute_all_rules_with_predator_kdtree,
    compute_all_rules_with_multi_predator_kdtree
)


class FlockOptimized:
    """
    Optimized flock manager using KDTree for spatial queries.
    
    Drop-in replacement for Flock class with identical behavior
    but better performance for large numbers of boids.
    
    Supports multiple predators (Optional Enhancement).
    """
    
    def __init__(self, num_boids: int, params: SimulationParams = None,
                 enable_predator: bool = False, num_predators: int = 1):
        """
        Initialize the flock with random boids.
        
        Args:
            num_boids: Number of boids to create
            params: Simulation parameters (uses defaults if None)
            enable_predator: If True, create predator(s) (Tier 2)
            num_predators: Number of predators to create (1-5)
        """
        self.params = params or SimulationParams()
        self.boids: List[Boid] = []
        self.predators: List[Predator] = []
        self.obstacles: List[Obstacle] = []
        
        for _ in range(num_boids):
            boid = Boid.create_random(
                width=self.params.width,
                height=self.params.height,
                max_speed=self.params.max_speed
            )
            self.boids.append(boid)
        
        # Initialize spatial index
        self._flock_state = FlockState(self.boids)
        
        # Initialize predators if enabled
        if enable_predator:
            num_predators = max(1, min(5, num_predators))  # Clamp to 1-5
            for i in range(num_predators):
                predator = Predator.create_with_strategy_index(
                    index=i,
                    width=self.params.width,
                    height=self.params.height,
                    speed=self.params.predator_speed
                )
                self.predators.append(predator)
    
    # =========================================================================
    # Backward Compatibility Property
    # =========================================================================
    
    @property
    def predator(self) -> Optional[Predator]:
        """Get first predator (backward compatibility)."""
        return self.predators[0] if self.predators else None
    
    @predator.setter
    def predator(self, value: Optional[Predator]) -> None:
        """Set first predator (backward compatibility)."""
        if value is None:
            self.predators.clear()
        elif self.predators:
            self.predators[0] = value
        else:
            self.predators.append(value)
    
    def apply_boundary_steering(self, boid: Boid) -> tuple:
        """
        Compute velocity adjustment to keep boid within bounds.
        
        Identical to Flock.apply_boundary_steering.
        """
        dvx = 0.0
        dvy = 0.0
        
        p = self.params
        
        if boid.x < p.margin:
            dvx += p.turn_factor
        if boid.x > p.width - p.margin:
            dvx -= p.turn_factor
        if boid.y < p.margin:
            dvy += p.turn_factor
        if boid.y > p.height - p.margin:
            dvy -= p.turn_factor
        
        return (dvx, dvy)
    
    def enforce_speed_limits(self, boid: Boid) -> None:
        """
        Clamp boid speed to within min/max bounds.
        
        Identical to Flock.enforce_speed_limits.
        """
        speed = boid.speed
        
        if speed == 0:
            angle = np.random.uniform(0, 2 * np.pi)
            boid.vx = self.params.min_speed * np.cos(angle)
            boid.vy = self.params.min_speed * np.sin(angle)
            return
        
        if speed > self.params.max_speed:
            boid.vx = (boid.vx / speed) * self.params.max_speed
            boid.vy = (boid.vy / speed) * self.params.max_speed
        elif speed < self.params.min_speed:
            boid.vx = (boid.vx / speed) * self.params.min_speed
            boid.vy = (boid.vy / speed) * self.params.min_speed
    
    def update(self) -> None:
        """
        Advance the simulation by one time step using KDTree optimization.
        
        Key difference from naive Flock:
        1. Rebuild spatial index once at start of frame
        2. Use KDTree queries for neighbor finding
        3. Compute all velocity adjustments first
        4. Apply all updates at end (parallel semantics)
        5. Update predators if present (Tier 2 + Multiple Predators)
        6. Apply obstacle avoidance (Optional Enhancement)
        """
        p = self.params
        
        # Rebuild spatial index with current positions
        self._flock_state.update()
        
        # Get all predator positions for multi-predator avoidance
        predator_positions: List[Tuple[float, float]] = [
            (pred.x, pred.y) for pred in self.predators
        ]
        
        # Compute all velocity adjustments first (parallel semantics)
        adjustments = []
        
        for i, boid in enumerate(self.boids):
            # Compute flocking rules using KDTree (including multi-predator avoidance)
            rules_dv = compute_all_rules_with_multi_predator_kdtree(
                boid_index=i,
                flock_state=self._flock_state,
                visual_range=p.visual_range,
                protected_range=p.protected_range,
                cohesion_factor=p.cohesion_factor,
                alignment_factor=p.alignment_factor,
                separation_strength=p.separation_strength,
                predator_positions=predator_positions,
                predator_detection_range=p.predator_detection_range,
                predator_avoidance_strength=p.predator_avoidance_strength
            )
            
            # Compute boundary steering
            boundary_dv = self.apply_boundary_steering(boid)
            
            # Compute obstacle avoidance
            obstacle_dv = compute_obstacle_avoidance(
                boid.x, boid.y,
                self.obstacles,
                detection_range=50.0,
                avoidance_strength=0.5
            )
            
            adjustments.append((
                rules_dv[0] + boundary_dv[0] + obstacle_dv[0],
                rules_dv[1] + boundary_dv[1] + obstacle_dv[1]
            ))
        
        # Apply all adjustments
        for i, boid in enumerate(self.boids):
            boid.vx += adjustments[i][0]
            boid.vy += adjustments[i][1]
            
            self.enforce_speed_limits(boid)
            
            boid.x += boid.vx
            boid.y += boid.vy
        
        # Update all predators
        self.update_predators()
    
    def update_predators(self) -> None:
        """
        Update all predators' states.
        
        Each predator uses its assigned hunting strategy.
        Uses same boundary handling and speed limits as boids.
        Also avoids obstacles.
        """
        if not self.predators:
            return
        
        p = self.params
        
        for predator in self.predators:
            # Predator uses its strategy to hunt
            predator.update_velocity_by_strategy(
                self.boids,
                hunting_strength=p.predator_hunting_strength
            )
            
            # Apply boundary steering
            predator.apply_boundary_steering(
                width=p.width,
                height=p.height,
                margin=p.margin,
                turn_factor=p.turn_factor
            )
            
            # Apply obstacle avoidance to predator
            if self.obstacles:
                obstacle_dv = compute_obstacle_avoidance(
                    predator.x, predator.y,
                    self.obstacles,
                    detection_range=50.0,
                    avoidance_strength=0.5
                )
                predator.vx += obstacle_dv[0]
                predator.vy += obstacle_dv[1]
            
            # Enforce speed limits (predator has own speed)
            predator.enforce_speed_limits(
                max_speed=p.predator_speed,
                min_speed=p.predator_speed * 0.5
            )
            
            # Update position
            predator.update_position()
    
    # =========================================================================
    # Obstacle Management Methods
    # =========================================================================
    
    def add_obstacle(self, x: float, y: float, radius: float = 30.0) -> Obstacle:
        """
        Add a circular obstacle to the simulation.
        
        Args:
            x: X position (center)
            y: Y position (center)
            radius: Obstacle radius
            
        Returns:
            The created Obstacle
        """
        obstacle = Obstacle(x=x, y=y, radius=radius)
        self.obstacles.append(obstacle)
        return obstacle
    
    def remove_obstacle(self, index: int) -> bool:
        """
        Remove obstacle by index.
        
        Args:
            index: Index of obstacle to remove
            
        Returns:
            True if removed, False if index invalid
        """
        if 0 <= index < len(self.obstacles):
            self.obstacles.pop(index)
            return True
        return False
    
    def clear_obstacles(self) -> int:
        """
        Remove all obstacles.
        
        Returns:
            Number of obstacles removed
        """
        count = len(self.obstacles)
        self.obstacles.clear()
        return count
    
    def get_obstacles(self) -> List[Obstacle]:
        """Get list of all obstacles."""
        return self.obstacles.copy()
    
    def toggle_predator(self) -> bool:
        """
        Toggle predator on/off (single predator for backward compatibility).
        
        Returns:
            True if predator is now enabled, False if disabled
        """
        if not self.predators:
            predator = Predator.create_with_strategy_index(
                index=0,
                width=self.params.width,
                height=self.params.height,
                speed=self.params.predator_speed
            )
            self.predators.append(predator)
            return True
        else:
            self.predators.clear()
            return False
    
    # =========================================================================
    # Multiple Predator Management
    # =========================================================================
    
    def add_predator(self) -> Optional[Predator]:
        """
        Add a new predator to the simulation.
        
        Strategy is assigned based on predator index.
        
        Returns:
            The created Predator, or None if max predators reached (5)
        """
        if len(self.predators) >= 5:
            return None
        
        index = len(self.predators)
        predator = Predator.create_with_strategy_index(
            index=index,
            width=self.params.width,
            height=self.params.height,
            speed=self.params.predator_speed
        )
        self.predators.append(predator)
        return predator
    
    def remove_predator(self, index: int = -1) -> bool:
        """
        Remove a predator by index.
        
        Args:
            index: Index of predator to remove (-1 for last)
            
        Returns:
            True if removed, False if invalid index or no predators
        """
        if not self.predators:
            return False
        
        if index == -1:
            self.predators.pop()
            return True
        
        if 0 <= index < len(self.predators):
            self.predators.pop(index)
            return True
        
        return False
    
    def set_num_predators(self, count: int) -> int:
        """
        Set the exact number of predators.
        
        Args:
            count: Desired number of predators (0-5)
            
        Returns:
            Actual number of predators after adjustment
        """
        count = max(0, min(5, count))  # Clamp to 0-5
        
        while len(self.predators) < count:
            self.add_predator()
        
        while len(self.predators) > count:
            self.predators.pop()
        
        return len(self.predators)
    
    def get_predators(self) -> List[Predator]:
        """Get list of all predators."""
        return self.predators.copy()
    
    @property
    def num_predators(self) -> int:
        """Number of active predators."""
        return len(self.predators)
    
    def get_positions(self) -> np.ndarray:
        """Get all boid positions as a numpy array."""
        return np.array([[b.x, b.y] for b in self.boids])
    
    def get_velocities(self) -> np.ndarray:
        """Get all boid velocities as a numpy array."""
        return np.array([[b.vx, b.vy] for b in self.boids])