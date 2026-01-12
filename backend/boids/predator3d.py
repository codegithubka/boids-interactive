"""
Predator3D class for 3D Boids simulation.

A predator is an antagonistic agent that hunts the flock in 3D space,
causing boids to scatter and avoid it.

Supports multiple hunting strategies for differentiated behavior.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .boid3d import Boid3D


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

# =============================================================================
# Hunting Behavior Constants
# =============================================================================

MAX_TARGET_FRAMES = 180      # ~3 seconds at 60fps
CATCH_DISTANCE = 15.0        # Consider "caught" if this close
COOLDOWN_DURATION = 60       # ~1 second at 60fps
CHASE_FAILURE_FRAMES = 90    # Give up after ~1.5 seconds no progress
EDGE_MARGIN = 100.0          # Prefer targets away from edges


@dataclass
class Predator3D:
    """
    A predator agent in 3D space.
    
    Attributes:
        x, y, z: position in 3D space (pixels)
        vx, vy, vz: velocity in 3D space (pixels/frame)
        strategy: hunting strategy determining behavior
        target_boid_index: current target boid index
        patrol_center: for PATROL_HUNTER, center of patrol sphere
        patrol_angles: for PATROL_HUNTER, current angles in patrol
        frames_since_target_switch: counter for target switching
        cooldown_frames: frames remaining in post-catch cooldown
        last_target_distance: distance to target last frame
        frames_without_progress: frames where distance hasn't decreased
    """
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    strategy: HuntingStrategy = HuntingStrategy.CENTER_HUNTER
    target_boid_index: Optional[int] = None
    patrol_center: Optional[np.ndarray] = field(default=None, repr=False)
    patrol_theta: float = 0.0  # Azimuthal angle for patrol
    patrol_phi: float = 0.0    # Polar angle for patrol
    frames_since_target_switch: int = 0
    cooldown_frames: int = 0
    last_target_distance: float = float('inf')
    frames_without_progress: int = 0
    
    @classmethod
    def create_random(
        cls,
        width: float,
        height: float,
        depth: float,
        speed: float = 2.5,
        strategy: HuntingStrategy = HuntingStrategy.CENTER_HUNTER
    ) -> "Predator3D":
        """
        Factory method to create a predator at a random position.
        
        Args:
            width: simulation width
            height: simulation height
            depth: simulation depth
            speed: initial speed magnitude
            strategy: hunting strategy
            
        Returns:
            A new Predator3D with random position and velocity
        """
        x = np.random.uniform(0, width)
        y = np.random.uniform(0, height)
        z = np.random.uniform(0, depth)
        
        # Random velocity direction (uniform on sphere)
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.arccos(np.random.uniform(-1, 1))
        
        vx = speed * np.sin(phi) * np.cos(theta)
        vy = speed * np.sin(phi) * np.sin(theta)
        vz = speed * np.cos(phi)
        
        predator = cls(x=x, y=y, z=z, vx=vx, vy=vy, vz=vz, strategy=strategy)
        
        # Initialize patrol center for patrol hunters
        if strategy == HuntingStrategy.PATROL_HUNTER:
            predator.patrol_center = np.array([x, y, z])
        
        return predator
    
    @classmethod
    def create_at_position(
        cls,
        x: float,
        y: float,
        z: float,
        speed: float = 2.5,
        strategy: HuntingStrategy = HuntingStrategy.CENTER_HUNTER
    ) -> "Predator3D":
        """
        Factory method to create a predator at a specific position.
        
        Args:
            x, y, z: position in 3D space
            speed: initial speed magnitude
            strategy: hunting strategy
            
        Returns:
            A new Predator3D at the specified position
        """
        # Random initial direction
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.arccos(np.random.uniform(-1, 1))
        
        vx = speed * np.sin(phi) * np.cos(theta)
        vy = speed * np.sin(phi) * np.sin(theta)
        vz = speed * np.cos(phi)
        
        predator = cls(x=x, y=y, z=z, vx=vx, vy=vy, vz=vz, strategy=strategy)
        
        if strategy == HuntingStrategy.PATROL_HUNTER:
            predator.patrol_center = np.array([x, y, z])
        
        return predator
    
    @classmethod
    def create_with_strategy_index(
        cls,
        index: int,
        width: float = 800,
        height: float = 600,
        depth: float = 600,
        speed: float = 2.5
    ) -> "Predator3D":
        """
        Create a predator with strategy based on index.
        
        Args:
            index: predator index (0-4), determines strategy
            width, height, depth: simulation bounds
            speed: initial speed
            
        Returns:
            Predator3D with appropriate strategy for index
        """
        strategy = STRATEGY_ORDER[index % len(STRATEGY_ORDER)]
        return cls.create_random(width, height, depth, speed, strategy)
    
    @property
    def speed(self) -> float:
        """Calculate current speed magnitude."""
        return np.sqrt(self.vx**2 + self.vy**2 + self.vz**2)
    
    @property
    def position(self) -> np.ndarray:
        """Return position as numpy array."""
        return np.array([self.x, self.y, self.z])
    
    @property
    def velocity(self) -> np.ndarray:
        """Return velocity as numpy array."""
        return np.array([self.vx, self.vy, self.vz])
    
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
    
    # =========================================================================
    # Hunting Improvement Methods
    # =========================================================================
    
    @property
    def is_in_cooldown(self) -> bool:
        """Check if predator is in post-catch cooldown."""
        return self.cooldown_frames > 0
    
    def start_cooldown(self) -> None:
        """Enter cooldown state after catching prey."""
        self.cooldown_frames = COOLDOWN_DURATION
        self.reset_target()
    
    def reset_target(self) -> None:
        """Reset target tracking state."""
        self.target_boid_index = None
        self.frames_since_target_switch = 0
        self.last_target_distance = float('inf')
        self.frames_without_progress = 0
    
    def update_cooldown(self) -> None:
        """Decrement cooldown counter if active."""
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1
    
    def check_catch(self, target_x: float, target_y: float, target_z: float) -> bool:
        """Check if predator has caught the target."""
        dx = self.x - target_x
        dy = self.y - target_y
        dz = self.z - target_z
        distance = np.sqrt(dx*dx + dy*dy + dz*dz)
        return distance < CATCH_DISTANCE
    
    def check_chase_failure(self, current_distance: float) -> bool:
        """Check if chase is failing (no progress toward target)."""
        if current_distance < self.last_target_distance - 0.5:
            self.frames_without_progress = 0
        else:
            self.frames_without_progress += 1
        
        self.last_target_distance = current_distance
        return self.frames_without_progress >= CHASE_FAILURE_FRAMES
    
    def should_switch_target(self) -> bool:
        """Check if target timeout has been reached."""
        return self.frames_since_target_switch >= MAX_TARGET_FRAMES
    
    def is_near_edge(
        self, 
        x: float, y: float, z: float,
        width: float, height: float, depth: float
    ) -> bool:
        """Check if position is near simulation edge (any of 6 faces)."""
        return (
            x < EDGE_MARGIN or x > width - EDGE_MARGIN or
            y < EDGE_MARGIN or y > height - EDGE_MARGIN or
            z < EDGE_MARGIN or z > depth - EDGE_MARGIN
        )
    
    # =========================================================================
    # Targeting Helpers
    # =========================================================================
    
    def compute_flock_center(self, boids: List["Boid3D"]) -> Optional[np.ndarray]:
        """Compute center of mass of the flock in 3D."""
        if not boids:
            return None
        
        sum_x = sum(b.x for b in boids)
        sum_y = sum(b.y for b in boids)
        sum_z = sum(b.z for b in boids)
        n = len(boids)
        
        return np.array([sum_x / n, sum_y / n, sum_z / n])
    
    def compute_nearest_boid(self, boids: List["Boid3D"]) -> Optional["Boid3D"]:
        """Find the nearest boid in 3D space."""
        if not boids:
            return None
        
        nearest = None
        min_dist_sq = float('inf')
        
        for boid in boids:
            dx = self.x - boid.x
            dy = self.y - boid.y
            dz = self.z - boid.z
            dist_sq = dx*dx + dy*dy + dz*dz
            
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = boid
        
        return nearest
    
    def compute_straggler_boid(self, boids: List["Boid3D"]) -> Optional["Boid3D"]:
        """Find the most isolated boid (furthest from flock center) in 3D."""
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
            dz = boid.z - center[2]
            dist_sq = dx*dx + dy*dy + dz*dz
            
            if dist_sq > max_dist_sq:
                max_dist_sq = dist_sq
                straggler = boid
        
        return straggler
    
    def steer_toward(
        self,
        target: np.ndarray,
        hunting_strength: float = 0.05,
        max_force: float = 1.0
    ) -> tuple:
        """
        Compute steering adjustment toward a target position in 3D.
        
        Args:
            target: numpy array [x, y, z] of target position
            hunting_strength: multiplier for steering force
            max_force: maximum magnitude of steering force
            
        Returns:
            Tuple (dvx, dvy, dvz) — velocity adjustment
        """
        dx = target[0] - self.x
        dy = target[1] - self.y
        dz = target[2] - self.z
        
        dvx = dx * hunting_strength
        dvy = dy * hunting_strength
        dvz = dz * hunting_strength
        
        # Clamp force magnitude
        magnitude = np.sqrt(dvx*dvx + dvy*dvy + dvz*dvz)
        if magnitude > max_force:
            scale = max_force / magnitude
            dvx *= scale
            dvy *= scale
            dvz *= scale
        
        return (dvx, dvy, dvz)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "vx": self.vx,
            "vy": self.vy,
            "vz": self.vz,
            "strategy": self.strategy.value,
            "strategy_name": self.strategy_name,
        }