"""
Simulation Manager for the Boids Interactive Demo.

Wraps FlockOptimized (2D) or Flock3D (3D), handles parameter updates, 
and produces frame data for WebSocket streaming.
"""

import time
from typing import Dict, Any, Optional, List, Union

import numpy as np

from boids import FlockOptimized, SimulationParams as FlockSimParams
from boids.flock3d import Flock3D, SimulationParams3D
from boids.metrics import (
    compute_avg_distance_to_predator,
    compute_min_distance_to_predator,
    compute_flock_cohesion,
)
from config import (
    SIMULATION_WIDTH, SIMULATION_HEIGHT, SIMULATION_DEPTH, 
    TARGET_FPS, DEFAULT_PARAMS, SimulationMode
)
from models import SimulationParams, FrameData, FrameMetrics


class SimulationManager:
    """
    Manages simulation state for a single client.
    
    Handles:
    - Flock initialization and updates (2D or 3D)
    - Parameter changes (with flock recreation when needed)
    - Frame data serialization
    - Pause/resume functionality
    - FPS tracking
    - Mode switching (2D <-> 3D)
    """

    def __init__(
        self,
        params: Optional[SimulationParams] = None,
        seed: Optional[int] = None
    ):
        """
        Initialize simulation manager.
        
        Args:
            params: Initial simulation parameters (uses defaults if None)
            seed: Random seed for reproducibility (random if None)
        """
        self._params = params or SimulationParams()
        self._seed = seed
        self._flock: Optional[Union[FlockOptimized, Flock3D]] = None
        self._frame_id: int = 0
        self._paused: bool = False
        self._running: bool = False
        
        # FPS tracking
        self._last_frame_time: float = time.time()
        self._fps: float = TARGET_FPS
        self._fps_samples: List[float] = []
        
        # Initialize flock
        self._init_flock()

    @property
    def is_3d(self) -> bool:
        """Whether simulation is in 3D mode."""
        return self._params.simulation_mode == SimulationMode.MODE_3D

    def _init_flock(self) -> None:
        """Create flock from current parameters."""
        if self._seed is not None:
            np.random.seed(self._seed)
        
        if self.is_3d:
            self._init_flock_3d()
        else:
            self._init_flock_2d()

    def _init_flock_2d(self) -> None:
        """Create 2D flock from current parameters."""
        flock_params = FlockSimParams(
            width=SIMULATION_WIDTH,
            height=SIMULATION_HEIGHT,
            visual_range=self._params.visual_range,
            protected_range=self._params.protected_range,
            max_speed=self._params.max_speed,
            min_speed=self._params.min_speed,
            cohesion_factor=self._params.cohesion_factor,
            alignment_factor=self._params.alignment_factor,
            separation_strength=self._params.separation_strength,
            margin=self._params.margin,
            turn_factor=self._params.turn_factor,
            predator_speed=self._params.predator_speed,
            predator_avoidance_strength=self._params.predator_avoidance_strength,
            predator_detection_range=self._params.predator_detection_range,
            predator_hunting_strength=self._params.predator_hunting_strength,
        )
        
        self._flock = FlockOptimized(
            num_boids=self._params.num_boids,
            params=flock_params,
            enable_predator=self._params.predator_enabled,
            num_predators=self._params.num_predators
        )

    def _init_flock_3d(self) -> None:
        """Create 3D flock from current parameters."""
        flock_params = SimulationParams3D(
            width=SIMULATION_WIDTH,
            height=SIMULATION_HEIGHT,
            depth=self._params.depth,
            num_boids=self._params.num_boids,
            visual_range=self._params.visual_range,
            protected_range=self._params.protected_range,
            max_speed=self._params.max_speed,
            min_speed=self._params.min_speed,
            cohesion_factor=self._params.cohesion_factor,
            alignment_factor=self._params.alignment_factor,
            separation_strength=self._params.separation_strength,
            margin=self._params.margin,
            turn_factor=self._params.turn_factor,
            predator_speed=self._params.predator_speed,
            predator_avoidance_strength=self._params.predator_avoidance_strength,
            predator_detection_range=self._params.predator_detection_range,
            predator_hunting_strength=self._params.predator_hunting_strength,
            enable_predator=self._params.predator_enabled,
            num_predators=self._params.num_predators,
        )
        
        self._flock = Flock3D(
            num_boids=self._params.num_boids,
            params=flock_params,
            enable_predator=self._params.predator_enabled,
            num_predators=self._params.num_predators
        )

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def start(self) -> None:
        """Start the simulation."""
        self._running = True
        self._last_frame_time = time.time()

    def stop(self) -> None:
        """Stop the simulation."""
        self._running = False

    def pause(self) -> None:
        """Pause the simulation (frames still sent, but no updates)."""
        self._paused = True

    def resume(self) -> None:
        """Resume the simulation."""
        self._paused = False

    @property
    def is_running(self) -> bool:
        """Whether simulation is running."""
        return self._running

    @property
    def is_paused(self) -> bool:
        """Whether simulation is paused."""
        return self._paused

    # =========================================================================
    # Simulation Update
    # =========================================================================

    def update(self) -> None:
        """Advance simulation by one frame (if not paused)."""
        if self._paused:
            return
        
        self._flock.update()
        self._frame_id += 1
        
        # Update FPS tracking
        now = time.time()
        delta = now - self._last_frame_time
        if delta > 0:
            instant_fps = 1.0 / delta
            self._fps_samples.append(instant_fps)
            # Keep last 30 samples for averaging
            if len(self._fps_samples) > 30:
                self._fps_samples.pop(0)
            self._fps = sum(self._fps_samples) / len(self._fps_samples)
        self._last_frame_time = now

    def reset(self) -> None:
        """Reset simulation with current parameters."""
        self._frame_id = 0
        self._fps_samples = []
        self._init_flock()

    # =========================================================================
    # Parameter Management
    # =========================================================================

    def update_params(self, updates: Dict[str, Any]) -> None:
        """
        Update simulation parameters.
        
        Args:
            updates: Dictionary of parameter updates (partial)
        """
        # Check if mode changed (requires full recreation)
        mode_changed = (
            'simulation_mode' in updates and 
            updates['simulation_mode'] != self._params.simulation_mode
        )
        
        # Check if num_boids changed (requires flock recreation)
        needs_recreation = (
            'num_boids' in updates and updates['num_boids'] != self._params.num_boids
        )
        predator_toggled = (
            'predator_enabled' in updates and 
            updates['predator_enabled'] != self._params.predator_enabled
        )
        num_predators_changed = (
            'num_predators' in updates and
            updates['num_predators'] != self._params.num_predators
        )
        depth_changed = (
            'depth' in updates and
            updates['depth'] != self._params.depth
        )
        
        # Apply updates to params
        current_dict = self._params.to_dict()
        current_dict.update(updates)
        
        # Validate and create new params
        try:
            self._params = SimulationParams(**current_dict)
        except Exception:
            # If validation fails, keep old params
            return
        
        # Mode change requires full recreation
        if mode_changed or (depth_changed and self.is_3d):
            self._init_flock()
        elif needs_recreation:
            # Full recreation needed for num_boids change
            self._init_flock()
        elif predator_toggled:
            # Toggle predator without full recreation
            if self._params.predator_enabled:
                self._set_num_predators(self._params.num_predators)
            else:
                self._set_num_predators(0)
        elif num_predators_changed and self._params.predator_enabled:
            # Update number of predators
            self._set_num_predators(self._params.num_predators)
        else:
            # Update flock params in place
            self._update_flock_params()

    def _set_num_predators(self, count: int) -> None:
        """Set number of predators (works for both 2D and 3D)."""
        if self.is_3d:
            # For 3D, we need to recreate for now
            # TODO: Add set_num_predators to Flock3D
            self._init_flock()
        else:
            self._flock.set_num_predators(count)

    def _update_flock_params(self) -> None:
        """Update flock parameters without recreation."""
        if self.is_3d:
            self._update_flock_params_3d()
        else:
            self._update_flock_params_2d()

    def _update_flock_params_2d(self) -> None:
        """Update 2D flock parameters without recreation."""
        self._flock.params.visual_range = self._params.visual_range
        self._flock.params.protected_range = self._params.protected_range
        self._flock.params.max_speed = self._params.max_speed
        self._flock.params.min_speed = self._params.min_speed
        self._flock.params.cohesion_factor = self._params.cohesion_factor
        self._flock.params.alignment_factor = self._params.alignment_factor
        self._flock.params.separation_strength = self._params.separation_strength
        self._flock.params.margin = self._params.margin
        self._flock.params.turn_factor = self._params.turn_factor
        self._flock.params.predator_speed = self._params.predator_speed
        self._flock.params.predator_avoidance_strength = self._params.predator_avoidance_strength
        self._flock.params.predator_detection_range = self._params.predator_detection_range
        self._flock.params.predator_hunting_strength = self._params.predator_hunting_strength

    def _update_flock_params_3d(self) -> None:
        """Update 3D flock parameters without recreation."""
        self._flock.params.visual_range = self._params.visual_range
        self._flock.params.protected_range = self._params.protected_range
        self._flock.params.max_speed = self._params.max_speed
        self._flock.params.min_speed = self._params.min_speed
        self._flock.params.cohesion_factor = self._params.cohesion_factor
        self._flock.params.alignment_factor = self._params.alignment_factor
        self._flock.params.separation_strength = self._params.separation_strength
        self._flock.params.margin = self._params.margin
        self._flock.params.turn_factor = self._params.turn_factor
        self._flock.params.predator_speed = self._params.predator_speed
        self._flock.params.predator_avoidance_strength = self._params.predator_avoidance_strength
        self._flock.params.predator_detection_range = self._params.predator_detection_range
        self._flock.params.predator_hunting_strength = self._params.predator_hunting_strength

    def set_mode(self, mode: str) -> None:
        """
        Switch simulation mode (2D <-> 3D).
        
        Args:
            mode: '2d' or '3d'
        """
        if mode not in [SimulationMode.MODE_2D, SimulationMode.MODE_3D]:
            raise ValueError(f"Invalid mode: {mode}")
        
        if mode != self._params.simulation_mode:
            self._params = SimulationParams(
                **{**self._params.to_dict(), 'simulation_mode': mode}
            )
            self._frame_id = 0
            self._fps_samples = []
            self._init_flock()

    def get_params(self) -> SimulationParams:
        """Get current parameters."""
        return self._params

    def get_params_dict(self) -> Dict[str, Any]:
        """Get current parameters as dictionary."""
        return self._params.to_dict()

    # =========================================================================
    # Frame Data
    # =========================================================================

    def get_frame_data(self) -> FrameData:
        """
        Get current frame data for sending to client.
        
        Returns:
            FrameData with boids, predators, obstacles, and metrics
        """
        if self.is_3d:
            return self._get_frame_data_3d()
        else:
            return self._get_frame_data_2d()

    def _get_frame_data_2d(self) -> FrameData:
        """Get 2D frame data."""
        # Serialize boids: [[x, y, vx, vy], ...]
        boids_data = [
            [b.x, b.y, b.vx, b.vy]
            for b in self._flock.boids
        ]
        
        # Serialize all predators with strategy info
        predators_data = [
            {
                "x": p.x,
                "y": p.y,
                "vx": p.vx,
                "vy": p.vy,
                "strategy": p.strategy.value,
                "strategy_name": p.strategy_name
            }
            for p in self._flock.predators
        ]
        
        # First predator for backward compatibility
        predator_data = None
        if self._flock.predators:
            p = self._flock.predators[0]
            predator_data = [p.x, p.y, p.vx, p.vy]
        
        # Serialize obstacles
        obstacles_data = [
            [obs.x, obs.y, obs.radius]
            for obs in self._flock.obstacles
        ]
        
        # Compute metrics if predator is active (uses first predator)
        metrics = None
        if self._flock.predator is not None:
            metrics = FrameMetrics(
                fps=round(self._fps, 1),
                avg_distance_to_predator=round(
                    compute_avg_distance_to_predator(
                        self._flock.boids, self._flock.predator
                    ), 1
                ),
                min_distance_to_predator=round(
                    compute_min_distance_to_predator(
                        self._flock.boids, self._flock.predator
                    ), 1
                ),
                flock_cohesion=round(
                    compute_flock_cohesion(self._flock.boids), 1
                )
            )
        else:
            metrics = FrameMetrics(fps=round(self._fps, 1))
        
        return FrameData(
            frame_id=self._frame_id,
            mode=SimulationMode.MODE_2D,
            boids=boids_data,
            predator=predator_data,
            predators=predators_data,
            obstacles=obstacles_data,
            metrics=metrics
        )

    def _get_frame_data_3d(self) -> FrameData:
        """Get 3D frame data."""
        # Serialize boids: [[x, y, z, vx, vy, vz], ...]
        boids_data = [
            [b.x, b.y, b.z, b.vx, b.vy, b.vz]
            for b in self._flock.boids
        ]
        
        # Serialize all predators with strategy info and z coordinates
        predators_data = [
            {
                "x": p.x,
                "y": p.y,
                "z": p.z,
                "vx": p.vx,
                "vy": p.vy,
                "vz": p.vz,
                "strategy": p.strategy.value,
                "strategy_name": p.strategy_name
            }
            for p in self._flock.predators
        ]
        
        # Serialize obstacles (spheres in 3D)
        obstacles_data = [
            [obs.x, obs.y, obs.z, obs.radius]
            for obs in self._flock.obstacles
        ]
        
        # Basic metrics for 3D (predator metrics would need 3D distance functions)
        metrics = FrameMetrics(fps=round(self._fps, 1))
        
        return FrameData(
            frame_id=self._frame_id,
            mode=SimulationMode.MODE_3D,
            boids=boids_data,
            predator=None,  # No backward compat for 3D
            predators=predators_data,
            obstacles=obstacles_data,
            metrics=metrics,
            bounds={
                "width": SIMULATION_WIDTH,
                "height": SIMULATION_HEIGHT,
                "depth": self._params.depth
            }
        )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def frame_id(self) -> int:
        """Current frame number."""
        return self._frame_id

    @property
    def num_boids(self) -> int:
        """Current number of boids."""
        return len(self._flock.boids)

    @property
    def has_predator(self) -> bool:
        """Whether predator is active."""
        if self.is_3d:
            return len(self._flock.predators) > 0
        return self._flock.predator is not None

    @property
    def mode(self) -> str:
        """Current simulation mode."""
        return self._params.simulation_mode

    @property
    def fps(self) -> float:
        """Current frames per second."""
        return self._fps

    # =========================================================================
    # Obstacle Management
    # =========================================================================

    def add_obstacle(self, x: float, y: float, radius: float = 30.0, z: float = None) -> Dict[str, Any]:
        """
        Add an obstacle to the simulation.
        
        Args:
            x: X position (center)
            y: Y position (center)
            radius: Obstacle radius
            z: Z position (center) - only used in 3D mode
            
        Returns:
            Dictionary with obstacle data and index
        """
        if self.is_3d:
            from boids.obstacle3d import Obstacle3D
            # Default z to center of depth if not provided
            if z is None:
                z = self._params.depth / 2
            obstacle = Obstacle3D(x, y, z, radius)
            self._flock.add_obstacle(obstacle)
            index = len(self._flock.obstacles) - 1
            return {
                'index': index,
                'x': obstacle.x,
                'y': obstacle.y,
                'z': obstacle.z,
                'radius': obstacle.radius
            }
        else:
            obstacle = self._flock.add_obstacle(x, y, radius)
            index = len(self._flock.obstacles) - 1
            return {
                'index': index,
                'x': obstacle.x,
                'y': obstacle.y,
                'radius': obstacle.radius
            }

    def remove_obstacle(self, index: int) -> bool:
        """
        Remove an obstacle by index.
        
        Args:
            index: Index of obstacle to remove
            
        Returns:
            True if removed, False if invalid index
        """
        if self.is_3d:
            self._flock.remove_obstacle(index)
            return True
        return self._flock.remove_obstacle(index)

    def clear_obstacles(self) -> int:
        """
        Remove all obstacles.
        
        Returns:
            Number of obstacles removed
        """
        if self.is_3d:
            count = len(self._flock.obstacles)
            self._flock.clear_obstacles()
            return count
        return self._flock.clear_obstacles()

    def get_obstacles(self) -> List[Dict[str, Any]]:
        """
        Get all obstacles.
        
        Returns:
            List of obstacle dictionaries
        """
        if self.is_3d:
            return [
                {'x': obs.x, 'y': obs.y, 'z': obs.z, 'radius': obs.radius}
                for obs in self._flock.obstacles
            ]
        return [
            {'x': obs.x, 'y': obs.y, 'radius': obs.radius}
            for obs in self._flock.obstacles
        ]

    @property
    def num_obstacles(self) -> int:
        """Current number of obstacles."""
        return len(self._flock.obstacles)