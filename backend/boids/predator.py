"""
Predator class for the Boids simulation.

A predator is an antagonistic agent that hunts the flock,
causing boids to scatter and avoid it.

Supports multiple hunting strategies for differentiated behavior.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from boid import Boid


class HuntingStrategy(Enum):
    """Different predator hunting strategies."""
    CENTER_HUNTER = "center"      # Hunts flock center of mass (Hawk)
    NEAREST_HUNTER = "nearest"    # Chases nearest boid (Falcon)
    STRAGGLER_HUNTER = "straggler"  # Targets isolated boids (Eagle)
    PATROL_HUNTER = "patrol"      # Circles area, attacks approaching boids (Kite)
    RANDOM_HUNTER = "random"      # Locks onto random boid periodically (Osprey)


# Strategy assignment by predator index
STRATEGY_ORDER = [
    HuntingStrategy.CENTER_HUNTER,    # Index 0: Hawk (Red)
    HuntingStrategy.NEAREST_HUNTER,   # Index 1: Falcon (Orange)
    HuntingStrategy.STRAGGLER_HUNTER, # Index 2: Eagle (Purple)
    HuntingStrategy.PATROL_HUNTER,    # Index 3: Kite (Cyan)
    HuntingStrategy.RANDOM_HUNTER,    # Index 4: Osprey (Green)
]


@dataclass
class Predator:
    """
    A predator agent that hunts boids.
    
    Attributes:
        x: horizontal position (pixels)
        y: vertical position (pixels)
        vx: horizontal velocity (pixels/frame)
        vy: vertical velocity (pixels/frame)
        strategy: hunting strategy determining behavior
        target_boid_index: for RANDOM_HUNTER, the current target
        patrol_center: for PATROL_HUNTER, the center of patrol area
        patrol_angle: for PATROL_HUNTER, current angle in patrol circle
        frames_since_target_switch: counter for RANDOM_HUNTER target switching
    """
    x: float
    y: float
    vx: float
    vy: float
    strategy: HuntingStrategy = HuntingStrategy.CENTER_HUNTER
    target_boid_index: Optional[int] = None
    patrol_center: Optional[np.ndarray] = field(default=None, repr=False)
    patrol_angle: float = 0.0
    frames_since_target_switch: int = 0
    
    @classmethod
    def create_at_position(
        cls,
        x: float,
        y: float,
        speed: float = 2.5,
        strategy: HuntingStrategy = HuntingStrategy.CENTER_HUNTER
    ) -> "Predator":
        """
        Factory method to create a predator at a specific position.
        
        Args:
            x: horizontal position
            y: vertical position
            speed: initial speed magnitude
            strategy: hunting strategy
            
        Returns:
            A new Predator with random velocity direction.
        """
        angle = np.random.uniform(0, 2 * np.pi)
        vx = speed * np.cos(angle)
        vy = speed * np.sin(angle)
        
        return cls(x=x, y=y, vx=vx, vy=vy, strategy=strategy)
    
    @classmethod
    def create_random(
        cls,
        width: float = 800,
        height: float = 600,
        speed: float = 2.5,
        strategy: HuntingStrategy = HuntingStrategy.CENTER_HUNTER
    ) -> "Predator":
        """
        Factory method to create a predator at random position.
        
        Args:
            width: simulation width in pixels
            height: simulation height in pixels
            speed: initial speed magnitude
            strategy: hunting strategy
            
        Returns:
            A new Predator with random position and velocity.
        """
        x = np.random.uniform(0, width)
        y = np.random.uniform(0, height)
        
        predator = cls.create_at_position(x, y, speed, strategy)
        
        # Initialize patrol center for PATROL_HUNTER
        if strategy == HuntingStrategy.PATROL_HUNTER:
            predator.patrol_center = np.array([x, y])
            predator.patrol_angle = np.random.uniform(0, 2 * np.pi)
        
        return predator
    
    @classmethod
    def create_with_strategy_index(
        cls,
        index: int,
        width: float = 800,
        height: float = 600,
        speed: float = 2.5
    ) -> "Predator":
        """
        Create a predator with strategy based on index.
        
        Args:
            index: predator index (0-4), determines strategy
            width: simulation width
            height: simulation height
            speed: initial speed
            
        Returns:
            Predator with appropriate strategy for index
        """
        strategy = STRATEGY_ORDER[index % len(STRATEGY_ORDER)]
        return cls.create_random(width, height, speed, strategy)
    
    @property
    def speed(self) -> float:
        """Calculate current speed magnitude."""
        return np.sqrt(self.vx**2 + self.vy**2)
    
    @property
    def position(self) -> np.ndarray:
        """Return position as numpy array."""
        return np.array([self.x, self.y])
    
    @property
    def velocity(self) -> np.ndarray:
        """Return velocity as numpy array."""
        return np.array([self.vx, self.vy])
    
    @property
    def strategy_name(self) -> str:
        """Human-readable strategy name."""
        names = {
            HuntingStrategy.CENTER_HUNTER: "Hawk",
            HuntingStrategy.NEAREST_HUNTER: "Falcon",
            HuntingStrategy.STRAGGLER_HUNTER: "Eagle",
            HuntingStrategy.PATROL_HUNTER: "Kite",
            HuntingStrategy.RANDOM_HUNTER: "Osprey",
        }
        return names.get(self.strategy, "Unknown")
    
    def compute_flock_center(self, boids: List["Boid"]) -> Optional[np.ndarray]:
        """
        Compute center of mass of the flock.
        
        Args:
            boids: List of all boids
            
        Returns:
            numpy array [x, y] of flock center, or None if no boids
        """
        if not boids:
            return None
        
        sum_x = sum(b.x for b in boids)
        sum_y = sum(b.y for b in boids)
        n = len(boids)
        
        return np.array([sum_x / n, sum_y / n])
    
    def compute_nearest_boid(self, boids: List["Boid"]) -> Optional["Boid"]:
        """
        Find the nearest boid to the predator.
        
        Args:
            boids: List of all boids
            
        Returns:
            The nearest Boid, or None if no boids
        """
        if not boids:
            return None
        
        nearest = None
        min_dist_sq = float('inf')
        
        for boid in boids:
            dx = self.x - boid.x
            dy = self.y - boid.y
            dist_sq = dx * dx + dy * dy
            
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = boid
        
        return nearest
    
    def compute_straggler_boid(self, boids: List["Boid"]) -> Optional["Boid"]:
        """
        Find the most isolated boid (furthest from flock center).
        
        Args:
            boids: List of all boids
            
        Returns:
            The most isolated Boid, or None if no boids
        """
        if not boids:
            return None
        
        center = self.compute_flock_center(boids)
        if center is None:
            return None
        
        straggler = None
        max_dist_sq = -1
        
        for boid in boids:
            dx = boid.x - center[0]
            dy = boid.y - center[1]
            dist_sq = dx * dx + dy * dy
            
            if dist_sq > max_dist_sq:
                max_dist_sq = dist_sq
                straggler = boid
        
        return straggler
    
    def steer_toward(
        self,
        target: np.ndarray,
        hunting_strength: float = 0.05
    ) -> tuple:
        """
        Compute steering adjustment toward a target position.
        
        Args:
            target: numpy array [x, y] of target position
            hunting_strength: multiplier for steering force
            
        Returns:
            Tuple (dvx, dvy) — velocity adjustment
        """
        dx = target[0] - self.x
        dy = target[1] - self.y
        
        return (dx * hunting_strength, dy * hunting_strength)
    
    def update_velocity_toward_center(
        self,
        boids: List["Boid"],
        hunting_strength: float = 0.05
    ) -> None:
        """
        Adjust velocity to move toward flock center of mass.
        
        Args:
            boids: List of all boids
            hunting_strength: multiplier for steering force
        """
        center = self.compute_flock_center(boids)
        
        if center is None:
            return
        
        dvx, dvy = self.steer_toward(center, hunting_strength)
        self.vx += dvx
        self.vy += dvy
    
    def update_velocity_toward_nearest(
        self,
        boids: List["Boid"],
        hunting_strength: float = 0.05
    ) -> None:
        """
        Adjust velocity to move toward nearest boid.
        
        Args:
            boids: List of all boids
            hunting_strength: multiplier for steering force
        """
        nearest = self.compute_nearest_boid(boids)
        
        if nearest is None:
            return
        
        target = np.array([nearest.x, nearest.y])
        dvx, dvy = self.steer_toward(target, hunting_strength)
        self.vx += dvx
        self.vy += dvy
    
    def update_velocity_toward_straggler(
        self,
        boids: List["Boid"],
        hunting_strength: float = 0.05
    ) -> None:
        """
        Adjust velocity to move toward most isolated boid.
        
        Args:
            boids: List of all boids
            hunting_strength: multiplier for steering force
        """
        straggler = self.compute_straggler_boid(boids)
        
        if straggler is None:
            return
        
        target = np.array([straggler.x, straggler.y])
        dvx, dvy = self.steer_toward(target, hunting_strength)
        self.vx += dvx
        self.vy += dvy
    
    def update_velocity_patrol(
        self,
        boids: List["Boid"],
        hunting_strength: float = 0.05,
        patrol_radius: float = 150.0,
        patrol_speed: float = 0.03,
        attack_range: float = 100.0
    ) -> None:
        """
        Patrol in circles, attack if boids come close.
        
        Args:
            boids: List of all boids
            hunting_strength: multiplier for steering force
            patrol_radius: radius of patrol circle
            patrol_speed: angular velocity of patrol
            attack_range: distance at which to break patrol and attack
        """
        # Initialize patrol center if not set
        if self.patrol_center is None:
            self.patrol_center = np.array([self.x, self.y])
        
        # Check if any boid is within attack range
        nearest = self.compute_nearest_boid(boids)
        if nearest is not None:
            dx = self.x - nearest.x
            dy = self.y - nearest.y
            dist = np.sqrt(dx * dx + dy * dy)
            
            if dist < attack_range:
                # Attack mode: chase nearest
                target = np.array([nearest.x, nearest.y])
                dvx, dvy = self.steer_toward(target, hunting_strength * 1.5)
                self.vx += dvx
                self.vy += dvy
                return
        
        # Patrol mode: circle around patrol center
        self.patrol_angle += patrol_speed
        target_x = self.patrol_center[0] + patrol_radius * np.cos(self.patrol_angle)
        target_y = self.patrol_center[1] + patrol_radius * np.sin(self.patrol_angle)
        
        target = np.array([target_x, target_y])
        dvx, dvy = self.steer_toward(target, hunting_strength)
        self.vx += dvx
        self.vy += dvy
    
    def update_velocity_random_target(
        self,
        boids: List["Boid"],
        hunting_strength: float = 0.05,
        switch_interval: int = 120
    ) -> None:
        """
        Lock onto a random boid, periodically switch targets.
        
        Args:
            boids: List of all boids
            hunting_strength: multiplier for steering force
            switch_interval: frames between target switches
        """
        if not boids:
            return
        
        self.frames_since_target_switch += 1
        
        # Switch target if interval elapsed or target invalid
        need_new_target = (
            self.target_boid_index is None or
            self.target_boid_index >= len(boids) or
            self.frames_since_target_switch >= switch_interval
        )
        
        if need_new_target:
            self.target_boid_index = np.random.randint(0, len(boids))
            self.frames_since_target_switch = 0
        
        # Chase current target
        target_boid = boids[self.target_boid_index]
        target = np.array([target_boid.x, target_boid.y])
        dvx, dvy = self.steer_toward(target, hunting_strength)
        self.vx += dvx
        self.vy += dvy
    
    def update_velocity_by_strategy(
        self,
        boids: List["Boid"],
        hunting_strength: float = 0.05
    ) -> None:
        """
        Update velocity based on assigned hunting strategy.
        
        Args:
            boids: List of all boids
            hunting_strength: multiplier for steering force
        """
        if self.strategy == HuntingStrategy.CENTER_HUNTER:
            self.update_velocity_toward_center(boids, hunting_strength)
        elif self.strategy == HuntingStrategy.NEAREST_HUNTER:
            self.update_velocity_toward_nearest(boids, hunting_strength)
        elif self.strategy == HuntingStrategy.STRAGGLER_HUNTER:
            self.update_velocity_toward_straggler(boids, hunting_strength)
        elif self.strategy == HuntingStrategy.PATROL_HUNTER:
            self.update_velocity_patrol(boids, hunting_strength)
        elif self.strategy == HuntingStrategy.RANDOM_HUNTER:
            self.update_velocity_random_target(boids, hunting_strength)
        else:
            # Default to center hunting
            self.update_velocity_toward_center(boids, hunting_strength)
    
    def apply_boundary_steering(
        self,
        width: float,
        height: float,
        margin: float,
        turn_factor: float
    ) -> None:
        """
        Apply boundary steering to keep predator in bounds.
        
        Uses same logic as boids for consistency.
        
        Args:
            width: simulation width
            height: simulation height
            margin: distance from edge to start turning
            turn_factor: steering strength at boundaries
        """
        if self.x < margin:
            self.vx += turn_factor
        if self.x > width - margin:
            self.vx -= turn_factor
        if self.y < margin:
            self.vy += turn_factor
        if self.y > height - margin:
            self.vy -= turn_factor
        
        # Update patrol center if it would be out of bounds
        if self.strategy == HuntingStrategy.PATROL_HUNTER and self.patrol_center is not None:
            # Keep patrol center within bounds
            self.patrol_center[0] = np.clip(self.patrol_center[0], margin + 50, width - margin - 50)
            self.patrol_center[1] = np.clip(self.patrol_center[1], margin + 50, height - margin - 50)
    
    def enforce_speed_limits(
        self,
        max_speed: float,
        min_speed: float
    ) -> None:
        """
        Clamp predator speed to within bounds.
        
        Args:
            max_speed: maximum speed
            min_speed: minimum speed
        """
        speed = self.speed
        
        if speed == 0:
            angle = np.random.uniform(0, 2 * np.pi)
            self.vx = min_speed * np.cos(angle)
            self.vy = min_speed * np.sin(angle)
            return
        
        if speed > max_speed:
            self.vx = (self.vx / speed) * max_speed
            self.vy = (self.vy / speed) * max_speed
        elif speed < min_speed:
            self.vx = (self.vx / speed) * min_speed
            self.vy = (self.vy / speed) * min_speed
    
    def update_position(self) -> None:
        """Update position based on current velocity."""
        self.x += self.vx
        self.y += self.vy