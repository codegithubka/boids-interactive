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

# =============================================================================
# Hunting Behavior Constants
# =============================================================================

# Target timeout: force switch after this many frames on same target
MAX_TARGET_FRAMES = 180  # ~3 seconds at 60fps

# Catch detection: consider "caught" if this close (triggers cooldown)
CATCH_DISTANCE = 15.0

# Cooldown after catch: predator rests before hunting again
COOLDOWN_DURATION = 60  # ~1 second at 60fps

# Chase failure: give up if no progress toward target for this many frames
CHASE_FAILURE_FRAMES = 90  # ~1.5 seconds at 60fps

# Edge avoidance: prefer targets at least this far from edges
EDGE_MARGIN = 100.0


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
        target_boid_index: current target boid index (for tracking strategies)
        patrol_center: for PATROL_HUNTER, the center of patrol area
        patrol_angle: for PATROL_HUNTER, current angle in patrol circle
        frames_since_target_switch: counter for target switching
        
        # Hunting improvement attributes
        cooldown_frames: frames remaining in post-catch cooldown
        last_target_distance: distance to target last frame (for chase failure)
        frames_without_progress: frames where distance hasn't decreased
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
    
    # Hunting improvement attributes
    cooldown_frames: int = 0
    last_target_distance: float = float('inf')
    frames_without_progress: int = 0
    
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
    
    def check_catch(self, target_x: float, target_y: float) -> bool:
        """
        Check if predator has caught the target.
        
        Args:
            target_x: target x position
            target_y: target y position
            
        Returns:
            True if within catch distance
        """
        dx = self.x - target_x
        dy = self.y - target_y
        distance = np.sqrt(dx * dx + dy * dy)
        return distance < CATCH_DISTANCE
    
    def check_chase_failure(self, current_distance: float) -> bool:
        """
        Check if chase is failing (no progress toward target).
        
        Args:
            current_distance: current distance to target
            
        Returns:
            True if should give up on this target
        """
        # Check if making progress (getting closer)
        if current_distance < self.last_target_distance - 0.5:
            # Making progress, reset counter
            self.frames_without_progress = 0
        else:
            # Not making progress
            self.frames_without_progress += 1
        
        self.last_target_distance = current_distance
        
        return self.frames_without_progress >= CHASE_FAILURE_FRAMES
    
    def should_switch_target(self) -> bool:
        """Check if target timeout has been reached."""
        return self.frames_since_target_switch >= MAX_TARGET_FRAMES
    
    def is_near_edge(self, x: float, y: float, width: float, height: float) -> bool:
        """
        Check if position is near simulation edge.
        
        Args:
            x, y: position to check
            width, height: simulation bounds
            
        Returns:
            True if within EDGE_MARGIN of any edge
        """
        return (x < EDGE_MARGIN or x > width - EDGE_MARGIN or
                y < EDGE_MARGIN or y > height - EDGE_MARGIN)
    
    def select_target_avoiding_edges(
        self, 
        boids: List["Boid"], 
        width: float, 
        height: float,
        selector_func
    ) -> Optional[int]:
        """
        Select a target boid, preferring those away from edges.
        
        Args:
            boids: list of boids to choose from
            width, height: simulation bounds
            selector_func: function(boids, excluded_indices) -> boid index
                          that selects a target from non-excluded boids
            
        Returns:
            Index of selected boid, or None if no valid targets
        """
        if not boids:
            return None
        
        # First, try to find targets away from edges
        non_edge_indices = [
            i for i, b in enumerate(boids)
            if not self.is_near_edge(b.x, b.y, width, height)
        ]
        
        if non_edge_indices:
            # Select from non-edge boids
            return selector_func(boids, non_edge_indices)
        else:
            # Fall back to any boid
            return selector_func(boids, list(range(len(boids))))

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
        hunting_strength: float = 0.05,
        max_force: float = 1.0
    ) -> tuple:
        """
        Compute steering adjustment toward a target position.
        
        Force is clamped to max_force to prevent overwhelming boundary steering.
        
        Args:
            target: numpy array [x, y] of target position
            hunting_strength: multiplier for steering force
            max_force: maximum magnitude of steering force
            
        Returns:
            Tuple (dvx, dvy) — velocity adjustment
        """
        dx = target[0] - self.x
        dy = target[1] - self.y
        
        dvx = dx * hunting_strength
        dvy = dy * hunting_strength
        
        # Clamp force magnitude to prevent overwhelming boundary steering
        magnitude = np.sqrt(dvx * dvx + dvy * dvy)
        if magnitude > max_force:
            scale = max_force / magnitude
            dvx *= scale
            dvy *= scale
        
        return (dvx, dvy)
    
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
        hunting_strength: float = 0.05,
        width: float = 800,
        height: float = 600
    ) -> None:
        """
        Adjust velocity to move toward nearest boid (Falcon strategy).
        
        Includes: catch detection, chase failure, target timeout, edge avoidance.
        
        Args:
            boids: List of all boids
            hunting_strength: multiplier for steering force
            width, height: simulation bounds for edge avoidance
        """
        if not boids:
            return
        
        # Handle cooldown
        if self.is_in_cooldown:
            self.update_cooldown()
            return
        
        self.frames_since_target_switch += 1
        
        # Find nearest boid (with edge preference)
        def select_nearest(boids_list, valid_indices):
            nearest_idx = None
            min_dist_sq = float('inf')
            for i in valid_indices:
                b = boids_list[i]
                dx = self.x - b.x
                dy = self.y - b.y
                dist_sq = dx * dx + dy * dy
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    nearest_idx = i
            return nearest_idx
        
        target_idx = self.select_target_avoiding_edges(boids, width, height, select_nearest)
        
        if target_idx is None:
            return
        
        target_boid = boids[target_idx]
        target = np.array([target_boid.x, target_boid.y])
        
        # Calculate distance for catch/failure detection
        dx = self.x - target_boid.x
        dy = self.y - target_boid.y
        distance = np.sqrt(dx * dx + dy * dy)
        
        # Check for catch
        if self.check_catch(target_boid.x, target_boid.y):
            self.start_cooldown()
            return
        
        # Check for chase failure (only if we've been chasing for a bit)
        if self.frames_since_target_switch > 30:
            if self.check_chase_failure(distance):
                self.reset_target()
                return
        else:
            self.last_target_distance = distance
        
        # Check for target timeout
        if self.should_switch_target():
            self.reset_target()
            return
        
        # Steer toward target
        dvx, dvy = self.steer_toward(target, hunting_strength)
        self.vx += dvx
        self.vy += dvy
    
    def update_velocity_toward_straggler(
        self,
        boids: List["Boid"],
        hunting_strength: float = 0.05,
        width: float = 800,
        height: float = 600
    ) -> None:
        """
        Adjust velocity to move toward most isolated boid (Eagle strategy).
        
        Includes: catch detection, chase failure, target timeout, edge avoidance.
        
        Args:
            boids: List of all boids
            hunting_strength: multiplier for steering force
            width, height: simulation bounds for edge avoidance
        """
        if not boids:
            return
        
        # Handle cooldown
        if self.is_in_cooldown:
            self.update_cooldown()
            return
        
        self.frames_since_target_switch += 1
        
        # Find straggler (with edge preference)
        center = self.compute_flock_center(boids)
        if center is None:
            return
        
        def select_straggler(boids_list, valid_indices):
            straggler_idx = None
            max_dist_sq = -1
            for i in valid_indices:
                b = boids_list[i]
                dx = b.x - center[0]
                dy = b.y - center[1]
                dist_sq = dx * dx + dy * dy
                if dist_sq > max_dist_sq:
                    max_dist_sq = dist_sq
                    straggler_idx = i
            return straggler_idx
        
        # Check if we have an existing valid target
        need_new_target = (
            self.target_boid_index is None or
            self.target_boid_index >= len(boids) or
            self.should_switch_target()
        )
        
        if need_new_target:
            self.target_boid_index = self.select_target_avoiding_edges(
                boids, width, height, select_straggler
            )
            if self.target_boid_index is not None:
                self.frames_since_target_switch = 0
                self.last_target_distance = float('inf')
                self.frames_without_progress = 0
        
        if self.target_boid_index is None:
            return
        
        target_boid = boids[self.target_boid_index]
        target = np.array([target_boid.x, target_boid.y])
        
        # Calculate distance
        dx = self.x - target_boid.x
        dy = self.y - target_boid.y
        distance = np.sqrt(dx * dx + dy * dy)
        
        # Check for catch
        if self.check_catch(target_boid.x, target_boid.y):
            self.start_cooldown()
            return
        
        # Check for chase failure
        if self.frames_since_target_switch > 30:
            if self.check_chase_failure(distance):
                self.reset_target()
                return
        else:
            self.last_target_distance = distance
        
        # Steer toward target
        dvx, dvy = self.steer_toward(target, hunting_strength)
        self.vx += dvx
        self.vy += dvy
    
    def update_velocity_patrol(
        self,
        boids: List["Boid"],
        hunting_strength: float = 0.05,
        patrol_radius: float = 150.0,
        patrol_speed: float = 0.03,
        attack_range: float = 100.0,
        width: float = 800,
        height: float = 600
    ) -> None:
        """
        Patrol in circles, attack if boids come close (Kite strategy).
        
        Includes: catch detection, chase failure during attack, edge avoidance.
        
        Args:
            boids: List of all boids
            hunting_strength: multiplier for steering force
            patrol_radius: radius of patrol circle
            patrol_speed: angular velocity of patrol
            attack_range: distance at which to break patrol and attack
            width, height: simulation bounds for edge avoidance
        """
        # Initialize patrol center if not set
        if self.patrol_center is None:
            self.patrol_center = np.array([self.x, self.y])
        
        # Handle cooldown - continue patrolling during cooldown
        if self.is_in_cooldown:
            self.update_cooldown()
            # Just patrol during cooldown
            self.patrol_angle += patrol_speed
            target_x = self.patrol_center[0] + patrol_radius * np.cos(self.patrol_angle)
            target_y = self.patrol_center[1] + patrol_radius * np.sin(self.patrol_angle)
            target = np.array([target_x, target_y])
            dvx, dvy = self.steer_toward(target, hunting_strength)
            self.vx += dvx
            self.vy += dvy
            return
        
        # Find nearest boid within attack range (preferring non-edge targets)
        def select_nearest_in_range(boids_list, valid_indices):
            nearest_idx = None
            min_dist_sq = attack_range * attack_range
            for i in valid_indices:
                b = boids_list[i]
                dx = self.x - b.x
                dy = self.y - b.y
                dist_sq = dx * dx + dy * dy
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    nearest_idx = i
            return nearest_idx
        
        attack_target_idx = self.select_target_avoiding_edges(
            boids, width, height, select_nearest_in_range
        )
        
        if attack_target_idx is not None:
            # Attack mode
            self.frames_since_target_switch += 1
            target_boid = boids[attack_target_idx]
            
            # Calculate distance
            dx = self.x - target_boid.x
            dy = self.y - target_boid.y
            distance = np.sqrt(dx * dx + dy * dy)
            
            # Check for catch
            if self.check_catch(target_boid.x, target_boid.y):
                self.start_cooldown()
                return
            
            # Check for chase failure
            if self.frames_since_target_switch > 30:
                if self.check_chase_failure(distance):
                    self.reset_target()
                    # Return to patrol
                    return
            else:
                self.last_target_distance = distance
            
            # Attack: chase target
            target = np.array([target_boid.x, target_boid.y])
            dvx, dvy = self.steer_toward(target, hunting_strength * 1.5)
            self.vx += dvx
            self.vy += dvy
            return
        
        # No target in range - reset attack state and patrol
        if self.frames_since_target_switch > 0:
            self.reset_target()
        
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
        switch_interval: int = 120,
        width: float = 800,
        height: float = 600
    ) -> None:
        """
        Lock onto a random boid, periodically switch targets (Osprey strategy).
        
        Includes: catch detection, chase failure, target timeout, edge avoidance.
        
        Args:
            boids: List of all boids
            hunting_strength: multiplier for steering force
            switch_interval: frames between forced target switches
            width, height: simulation bounds for edge avoidance
        """
        if not boids:
            return
        
        # Handle cooldown
        if self.is_in_cooldown:
            self.update_cooldown()
            return
        
        self.frames_since_target_switch += 1
        
        # Check if we need a new target
        need_new_target = (
            self.target_boid_index is None or
            self.target_boid_index >= len(boids) or
            self.frames_since_target_switch >= switch_interval or
            self.should_switch_target()
        )
        
        if need_new_target:
            # Select random target with edge avoidance
            def select_random(boids_list, valid_indices):
                if not valid_indices:
                    return None
                return np.random.choice(valid_indices)
            
            self.target_boid_index = self.select_target_avoiding_edges(
                boids, width, height, select_random
            )
            if self.target_boid_index is not None:
                self.frames_since_target_switch = 0
                self.last_target_distance = float('inf')
                self.frames_without_progress = 0
        
        if self.target_boid_index is None:
            return
        
        # Chase current target
        target_boid = boids[self.target_boid_index]
        target = np.array([target_boid.x, target_boid.y])
        
        # Calculate distance
        dx = self.x - target_boid.x
        dy = self.y - target_boid.y
        distance = np.sqrt(dx * dx + dy * dy)
        
        # Check for catch
        if self.check_catch(target_boid.x, target_boid.y):
            self.start_cooldown()
            return
        
        # Check for chase failure
        if self.frames_since_target_switch > 30:
            if self.check_chase_failure(distance):
                self.reset_target()
                return
        else:
            self.last_target_distance = distance
        
        # Steer toward target
        dvx, dvy = self.steer_toward(target, hunting_strength)
        self.vx += dvx
        self.vy += dvy
    
    def update_velocity_by_strategy(
        self,
        boids: List["Boid"],
        hunting_strength: float = 0.05,
        width: float = 800,
        height: float = 600
    ) -> None:
        """
        Update velocity based on assigned hunting strategy.
        
        Args:
            boids: List of all boids
            hunting_strength: multiplier for steering force
            width, height: simulation bounds for edge avoidance
        """
        if self.strategy == HuntingStrategy.CENTER_HUNTER:
            self.update_velocity_toward_center(boids, hunting_strength)
        elif self.strategy == HuntingStrategy.NEAREST_HUNTER:
            self.update_velocity_toward_nearest(boids, hunting_strength, width, height)
        elif self.strategy == HuntingStrategy.STRAGGLER_HUNTER:
            self.update_velocity_toward_straggler(boids, hunting_strength, width, height)
        elif self.strategy == HuntingStrategy.PATROL_HUNTER:
            self.update_velocity_patrol(boids, hunting_strength, width=width, height=height)
        elif self.strategy == HuntingStrategy.RANDOM_HUNTER:
            self.update_velocity_random_target(boids, hunting_strength, width=width, height=height)
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
        
        Uses progressive steering that increases with distance past margin.
        
        Args:
            width: simulation width
            height: simulation height
            margin: distance from edge to start turning
            turn_factor: base steering strength at boundaries
        """
        # Progressive boundary steering: force increases with distance past margin
        if self.x < margin:
            distance_into_margin = margin - self.x
            scale = 1.0 + (distance_into_margin / margin)
            self.vx += turn_factor * scale
        if self.x > width - margin:
            distance_into_margin = self.x - (width - margin)
            scale = 1.0 + (distance_into_margin / margin)
            self.vx -= turn_factor * scale
        if self.y < margin:
            distance_into_margin = margin - self.y
            scale = 1.0 + (distance_into_margin / margin)
            self.vy += turn_factor * scale
        if self.y > height - margin:
            distance_into_margin = self.y - (height - margin)
            scale = 1.0 + (distance_into_margin / margin)
            self.vy -= turn_factor * scale
        
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