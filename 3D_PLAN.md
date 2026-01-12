# 3D Boids Implementation Plan

## Overview

This document outlines the implementation of 3D space for the Boids simulation using Three.js for rendering and extended backend physics.

**Target**: Transform the 2D boids simulation into a full 3D experience with camera controls, 3D models, and volumetric boundaries.

---

## Table of Contents

1. [Architecture Changes](#architecture-changes)
2. [Backend Implementation](#backend-implementation)
3. [Frontend Implementation](#frontend-implementation)
4. [Potential Issues & Mitigations](#potential-issues--mitigations)
5. [Testing Strategy](#testing-strategy)
6. [Implementation Phases](#implementation-phases)
7. [Performance Considerations](#performance-considerations)

---

## Architecture Changes

### Current (2D) vs Target (3D)

| Component | Current (2D) | Target (3D) |
|-----------|--------------|-------------|
| Boid position | `(x, y)` | `(x, y, z)` |
| Boid velocity | `(vx, vy)` | `(vx, vy, vz)` |
| Boundaries | Rectangle `(width, height)` | Box `(width, height, depth)` |
| Obstacles | Circles `(x, y, radius)` | Spheres `(x, y, z, radius)` |
| Neighbor search | 2D KDTree | 3D KDTree |
| Rendering | Canvas 2D | Three.js WebGL |
| Camera | Fixed top-down | Orbit controls |

### Data Flow (unchanged)

```
Backend (Python)          WebSocket          Frontend (Three.js)
     │                        │                      │
     │  SimulationParams      │                      │
     │  (now with depth)      │                      │
     ├───────────────────────>│                      │
     │                        │                      │
     │  FrameData             │                      │
     │  (x,y,z,vx,vy,vz)      │                      │
     ├───────────────────────>│                      │
     │                        │    Render 3D Scene   │
     │                        │─────────────────────>│
```

---

## Backend Implementation

### Phase 1: Core 3D Classes

#### 1.1 Boid3D Class

**File**: `backend/boids/boid3d.py`

```python
@dataclass
class Boid3D:
    """A boid agent in 3D space."""
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    
    @property
    def position(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])
    
    @property
    def velocity(self) -> np.ndarray:
        return np.array([self.vx, self.vy, self.vz])
    
    @property
    def speed(self) -> float:
        return np.sqrt(self.vx**2 + self.vy**2 + self.vz**2)
    
    @classmethod
    def create_random(cls, width, height, depth, max_speed) -> "Boid3D":
        ...
```

**Key differences from 2D**:
- Added `z` position and `vz` velocity
- `speed` calculation includes `vz`
- Factory methods accept `depth` parameter

#### 1.2 Predator3D Class

**File**: `backend/boids/predator3d.py`

```python
@dataclass
class Predator3D:
    """A predator agent in 3D space."""
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    strategy: HuntingStrategy
    # ... hunting improvement fields
```

#### 1.3 Obstacle3D Class

**File**: `backend/boids/obstacle3d.py`

```python
@dataclass
class Obstacle3D:
    """A spherical obstacle in 3D space."""
    x: float
    y: float
    z: float
    radius: float
```

#### 1.4 SimulationParams3D

**File**: `backend/boids/flock.py` (extended)

```python
@dataclass
class SimulationParams3D(SimulationParams):
    """3D simulation parameters."""
    depth: float = 600  # Z-axis bounds
    
    # Boundary margins (may differ per axis)
    margin_z: float = 75
```

### Phase 2: 3D Physics Rules

#### 2.1 Distance Calculation

```python
def distance_3d(a: Boid3D, b: Boid3D) -> float:
    """Euclidean distance in 3D."""
    return np.sqrt(
        (a.x - b.x)**2 + 
        (a.y - b.y)**2 + 
        (a.z - b.z)**2
    )
```

#### 2.2 Separation (3D)

```python
def compute_separation_3d(
    boid: Boid3D,
    neighbors: List[Boid3D],
    protected_range: float,
    separation_strength: float
) -> Tuple[float, float, float]:
    """Compute separation force in 3D."""
    dvx, dvy, dvz = 0.0, 0.0, 0.0
    
    for other in neighbors:
        dx = boid.x - other.x
        dy = boid.y - other.y
        dz = boid.z - other.z
        dist = np.sqrt(dx*dx + dy*dy + dz*dz)
        
        if 0 < dist < protected_range:
            dvx += dx * separation_strength
            dvy += dy * separation_strength
            dvz += dz * separation_strength
    
    return (dvx, dvy, dvz)
```

#### 2.3 Alignment (3D)

```python
def compute_alignment_3d(
    boid: Boid3D,
    neighbors: List[Boid3D],
    alignment_factor: float
) -> Tuple[float, float, float]:
    """Compute alignment force in 3D."""
    if not neighbors:
        return (0.0, 0.0, 0.0)
    
    avg_vx = sum(n.vx for n in neighbors) / len(neighbors)
    avg_vy = sum(n.vy for n in neighbors) / len(neighbors)
    avg_vz = sum(n.vz for n in neighbors) / len(neighbors)
    
    return (
        (avg_vx - boid.vx) * alignment_factor,
        (avg_vy - boid.vy) * alignment_factor,
        (avg_vz - boid.vz) * alignment_factor
    )
```

#### 2.4 Cohesion (3D)

```python
def compute_cohesion_3d(
    boid: Boid3D,
    neighbors: List[Boid3D],
    cohesion_factor: float
) -> Tuple[float, float, float]:
    """Compute cohesion force in 3D."""
    if not neighbors:
        return (0.0, 0.0, 0.0)
    
    center_x = sum(n.x for n in neighbors) / len(neighbors)
    center_y = sum(n.y for n in neighbors) / len(neighbors)
    center_z = sum(n.z for n in neighbors) / len(neighbors)
    
    return (
        (center_x - boid.x) * cohesion_factor,
        (center_y - boid.y) * cohesion_factor,
        (center_z - boid.z) * cohesion_factor
    )
```

#### 2.5 Boundary Steering (3D)

```python
def apply_boundary_steering_3d(
    boid: Boid3D,
    width: float, height: float, depth: float,
    margin: float, turn_factor: float
) -> Tuple[float, float, float]:
    """
    Compute boundary steering in 3D (6 faces instead of 4 edges).
    Uses progressive steering like 2D implementation.
    """
    dvx, dvy, dvz = 0.0, 0.0, 0.0
    
    # X boundaries
    if boid.x < margin:
        dist = margin - boid.x
        scale = 1.0 + (dist / margin)
        dvx += turn_factor * scale
    elif boid.x > width - margin:
        dist = boid.x - (width - margin)
        scale = 1.0 + (dist / margin)
        dvx -= turn_factor * scale
    
    # Y boundaries
    if boid.y < margin:
        dist = margin - boid.y
        scale = 1.0 + (dist / margin)
        dvy += turn_factor * scale
    elif boid.y > height - margin:
        dist = boid.y - (height - margin)
        scale = 1.0 + (dist / margin)
        dvy -= turn_factor * scale
    
    # Z boundaries (NEW)
    if boid.z < margin:
        dist = margin - boid.z
        scale = 1.0 + (dist / margin)
        dvz += turn_factor * scale
    elif boid.z > depth - margin:
        dist = boid.z - (depth - margin)
        scale = 1.0 + (dist / margin)
        dvz -= turn_factor * scale
    
    return (dvx, dvy, dvz)
```

#### 2.6 Predator Avoidance (3D)

```python
def compute_predator_avoidance_3d(
    boid: Boid3D,
    predator_positions: List[Tuple[float, float, float]],
    detection_range: float,
    avoidance_strength: float
) -> Tuple[float, float, float]:
    """Flee from predators in 3D space."""
    dvx, dvy, dvz = 0.0, 0.0, 0.0
    
    for px, py, pz in predator_positions:
        dx = boid.x - px
        dy = boid.y - py
        dz = boid.z - pz
        dist = np.sqrt(dx*dx + dy*dy + dz*dz)
        
        if dist < detection_range and dist > 0:
            strength = avoidance_strength * (1 - dist / detection_range)
            dvx += (dx / dist) * strength
            dvy += (dy / dist) * strength
            dvz += (dz / dist) * strength
    
    return (dvx, dvy, dvz)
```

#### 2.7 Obstacle Avoidance (3D)

```python
def compute_obstacle_avoidance_3d(
    x: float, y: float, z: float,
    obstacles: List[Obstacle3D],
    detection_range: float,
    avoidance_strength: float
) -> Tuple[float, float, float]:
    """Avoid spherical obstacles in 3D."""
    dvx, dvy, dvz = 0.0, 0.0, 0.0
    
    for obs in obstacles:
        dx = x - obs.x
        dy = y - obs.y
        dz = z - obs.z
        dist = np.sqrt(dx*dx + dy*dy + dz*dz)
        
        effective_range = detection_range + obs.radius
        
        if dist < effective_range and dist > 0:
            strength = avoidance_strength * (1 - dist / effective_range)
            dvx += (dx / dist) * strength
            dvy += (dy / dist) * strength
            dvz += (dz / dist) * strength
    
    return (dvx, dvy, dvz)
```

### Phase 3: Flock3D Manager

**File**: `backend/boids/flock3d.py`

```python
class Flock3D:
    """
    3D Flock manager using KDTree for spatial queries.
    """
    
    def __init__(
        self, 
        num_boids: int, 
        params: SimulationParams3D,
        enable_predator: bool = False,
        num_predators: int = 1
    ):
        self.params = params
        self.boids: List[Boid3D] = []
        self.predators: List[Predator3D] = []
        self.obstacles: List[Obstacle3D] = []
        
        # Initialize boids in 3D space
        for _ in range(num_boids):
            boid = Boid3D.create_random(
                width=params.width,
                height=params.height,
                depth=params.depth,
                max_speed=params.max_speed
            )
            self.boids.append(boid)
        
        # Initialize predators if enabled
        if enable_predator:
            for i in range(num_predators):
                predator = Predator3D.create_with_strategy_index(
                    index=i,
                    width=params.width,
                    height=params.height,
                    depth=params.depth,
                    speed=params.predator_speed
                )
                self.predators.append(predator)
        
        # Build 3D KDTree
        self._rebuild_kdtree()
    
    def _rebuild_kdtree(self):
        """Rebuild spatial index with 3D positions."""
        positions = np.array([
            [b.x, b.y, b.z] for b in self.boids
        ])
        self._kdtree = KDTree(positions)
    
    def update(self):
        """Advance simulation by one frame."""
        self._rebuild_kdtree()
        
        # Compute all adjustments (parallel semantics)
        adjustments = []
        for i, boid in enumerate(self.boids):
            dv = self._compute_boid_forces(i, boid)
            adjustments.append(dv)
        
        # Apply adjustments
        for i, boid in enumerate(self.boids):
            dvx, dvy, dvz = adjustments[i]
            boid.vx += dvx
            boid.vy += dvy
            boid.vz += dvz
            
            self._enforce_speed_limits(boid)
            
            boid.x += boid.vx
            boid.y += boid.vy
            boid.z += boid.vz
            
            # Hard clamp positions
            boid.x = max(0, min(self.params.width, boid.x))
            boid.y = max(0, min(self.params.height, boid.y))
            boid.z = max(0, min(self.params.depth, boid.z))
        
        # Update predators
        self._update_predators()
```

### Phase 4: API & WebSocket Updates

#### 4.1 Updated FrameData

```python
class FrameData3D(BaseModel):
    """Frame data for 3D simulation."""
    type: Literal["frame"] = "frame"
    frame_id: int
    boids: List[List[float]]  # [x, y, z, vx, vy, vz]
    predators: List[Dict[str, Any]]  # includes z, vz
    obstacles: List[List[float]]  # [x, y, z, radius]
    metrics: Optional[FrameMetrics]
```

#### 4.2 Config Updates

```python
# Add to PARAM_DEFINITIONS
"depth": ParamLimit(
    min=200, max=1200, default=600, step=50,
    category="primary",
    label="Depth",
    description="Z-axis bounds for 3D space"
),
```

---

## Frontend Implementation

### Phase 5: Three.js Setup

#### 5.1 Dependencies

```bash
cd frontend
npm install three @types/three
```

#### 5.2 Scene Setup

**File**: `frontend/src/Scene3D.tsx`

```typescript
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

interface Scene3DProps {
  width: number;
  height: number;
  depth: number;
  boids: number[][];  // [x, y, z, vx, vy, vz]
  predators: PredatorData[];
  obstacles: number[][];
}

export function Scene3D({ width, height, depth, boids, predators, obstacles }: Scene3DProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene>();
  const rendererRef = useRef<THREE.WebGLRenderer>();
  const cameraRef = useRef<THREE.PerspectiveCamera>();
  const controlsRef = useRef<OrbitControls>();
  
  // Boid instances for performance
  const boidMeshRef = useRef<THREE.InstancedMesh>();
  
  useEffect(() => {
    // Initialize Three.js scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);
    
    // Camera
    const camera = new THREE.PerspectiveCamera(
      75,  // FOV
      window.innerWidth / window.innerHeight,
      0.1,
      2000
    );
    camera.position.set(width / 2, height / 2, depth * 1.5);
    camera.lookAt(width / 2, height / 2, depth / 2);
    
    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    containerRef.current?.appendChild(renderer.domElement);
    
    // Orbit controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(width / 2, height / 2, depth / 2);
    controls.enableDamping = true;
    
    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(width, height, depth);
    scene.add(directionalLight);
    
    // Boundary box (wireframe)
    const boxGeometry = new THREE.BoxGeometry(width, height, depth);
    const boxEdges = new THREE.EdgesGeometry(boxGeometry);
    const boxLine = new THREE.LineSegments(
      boxEdges,
      new THREE.LineBasicMaterial({ color: 0x444466, transparent: true, opacity: 0.3 })
    );
    boxLine.position.set(width / 2, height / 2, depth / 2);
    scene.add(boxLine);
    
    // Store refs
    sceneRef.current = scene;
    rendererRef.current = renderer;
    cameraRef.current = camera;
    controlsRef.current = controls;
    
    // Cleanup
    return () => {
      renderer.dispose();
      containerRef.current?.removeChild(renderer.domElement);
    };
  }, [width, height, depth]);
  
  // ... render loop and boid updates
}
```

#### 5.3 Instanced Boid Rendering

```typescript
// Create instanced mesh for boids (MUCH faster than individual meshes)
function createBoidInstances(count: number): THREE.InstancedMesh {
  // Cone geometry pointing in +X direction
  const geometry = new THREE.ConeGeometry(3, 12, 8);
  geometry.rotateZ(-Math.PI / 2);  // Point along velocity
  
  const material = new THREE.MeshPhongMaterial({
    color: 0x4fc3f7,
    emissive: 0x1a237e,
    emissiveIntensity: 0.2,
    shininess: 50
  });
  
  const mesh = new THREE.InstancedMesh(geometry, material, count);
  mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  
  return mesh;
}

// Update boid positions each frame
function updateBoidInstances(
  mesh: THREE.InstancedMesh,
  boids: number[][]
): void {
  const dummy = new THREE.Object3D();
  const up = new THREE.Vector3(0, 1, 0);
  
  for (let i = 0; i < boids.length; i++) {
    const [x, y, z, vx, vy, vz] = boids[i];
    
    dummy.position.set(x, y, z);
    
    // Orient along velocity
    const velocity = new THREE.Vector3(vx, vy, vz);
    if (velocity.length() > 0.001) {
      dummy.quaternion.setFromUnitVectors(
        new THREE.Vector3(1, 0, 0),
        velocity.normalize()
      );
    }
    
    dummy.updateMatrix();
    mesh.setMatrixAt(i, dummy.matrix);
  }
  
  mesh.instanceMatrix.needsUpdate = true;
}
```

#### 5.4 Predator Rendering

```typescript
function createPredatorMesh(species: PredatorSpecies): THREE.Mesh {
  // Larger, more menacing geometry
  const geometry = new THREE.ConeGeometry(8, 24, 8);
  geometry.rotateZ(-Math.PI / 2);
  
  const material = new THREE.MeshPhongMaterial({
    color: new THREE.Color(species.body),
    emissive: new THREE.Color(species.glow),
    emissiveIntensity: 0.4,
    shininess: 80
  });
  
  return new THREE.Mesh(geometry, material);
}
```

#### 5.5 Obstacle Rendering

```typescript
function createObstacleMesh(radius: number): THREE.Mesh {
  const geometry = new THREE.SphereGeometry(radius, 32, 32);
  const material = new THREE.MeshPhongMaterial({
    color: 0xff4444,
    transparent: true,
    opacity: 0.6,
    emissive: 0x440000,
    emissiveIntensity: 0.3
  });
  
  return new THREE.Mesh(geometry, material);
}
```

---

## Potential Issues & Mitigations

### Issue 1: Performance with Many Boids

**Problem**: Rendering 100+ individual meshes is slow.

**Mitigation**: 
- Use `THREE.InstancedMesh` for boids (single draw call)
- Use `DynamicDrawUsage` for frequently updated matrices
- Consider LOD (Level of Detail) for distant boids

**Test**: Benchmark with 50, 100, 200, 500 boids

### Issue 2: 3D KDTree Neighbor Finding

**Problem**: scipy.spatial.KDTree needs to work with 3D data.

**Mitigation**: 
- KDTree already supports N-dimensional data
- Just pass `[[x, y, z], ...]` instead of `[[x, y], ...]`
- Verify with unit tests

**Test**: `test_kdtree_3d_neighbor_finding`

### Issue 3: Camera/View Complexity

**Problem**: Users may get disoriented in 3D space.

**Mitigation**:
- Default camera position shows whole scene
- OrbitControls with sensible limits
- Optional: preset camera angles (top, side, perspective)
- Optional: "reset camera" button

**Test**: Manual UX testing

### Issue 4: Depth Perception

**Problem**: Hard to judge distances in 3D.

**Mitigation**:
- Use fog effect (`scene.fog`)
- Boid size varies with distance (perspective)
- Optional: depth-based color gradient
- Boundary box wireframe provides reference

### Issue 5: WebSocket Bandwidth

**Problem**: 50% more data per frame (z, vz added).

**Current**: `[x, y, vx, vy]` = 4 floats × 4 bytes = 16 bytes/boid
**3D**: `[x, y, z, vx, vy, vz]` = 6 floats × 4 bytes = 24 bytes/boid

**With 100 boids at 60 FPS**:
- 2D: 96 KB/s
- 3D: 144 KB/s

**Mitigation**: 
- Still well within WebSocket capacity
- Could compress with MessagePack if needed
- Could reduce precision (Float16)

### Issue 6: Boundary Visualization

**Problem**: How to show 3D boundaries without obscuring view.

**Mitigation**:
- Wireframe box (EdgesGeometry)
- Semi-transparent faces (only show back faces)
- Grid on floor plane
- Optional: toggle boundary visibility

### Issue 7: Obstacle Placement in 3D

**Problem**: Clicking to place obstacles is 2D; 3D placement is tricky.

**Mitigation**:
- Place on a plane at current camera depth
- Use raycasting to existing geometry
- Or: place at center Z, allow drag to adjust

### Issue 8: Predator Strategy in 3D

**Problem**: Patrol hunter circles in 2D; what about 3D?

**Mitigation**:
- Patrol in 3D sphere or helix pattern
- Or: patrol in XY plane at fixed Z
- Test that all strategies work in 3D

---

## Testing Strategy

### Backend Tests

#### Unit Tests: 3D Math

```python
class Test3DDistance:
    def test_same_point(self):
        b1 = Boid3D(0, 0, 0, 0, 0, 0)
        b2 = Boid3D(0, 0, 0, 0, 0, 0)
        assert distance_3d(b1, b2) == 0
    
    def test_unit_distance_x(self):
        b1 = Boid3D(0, 0, 0, 0, 0, 0)
        b2 = Boid3D(1, 0, 0, 0, 0, 0)
        assert distance_3d(b1, b2) == 1
    
    def test_unit_distance_z(self):
        b1 = Boid3D(0, 0, 0, 0, 0, 0)
        b2 = Boid3D(0, 0, 1, 0, 0, 0)
        assert distance_3d(b1, b2) == 1
    
    def test_diagonal_3d(self):
        b1 = Boid3D(0, 0, 0, 0, 0, 0)
        b2 = Boid3D(1, 1, 1, 0, 0, 0)
        assert distance_3d(b1, b2) == pytest.approx(np.sqrt(3))
```

#### Unit Tests: 3D Rules

```python
class TestSeparation3D:
    def test_no_neighbors(self):
        boid = Boid3D(0, 0, 0, 0, 0, 0)
        dv = compute_separation_3d(boid, [], 20, 0.1)
        assert dv == (0, 0, 0)
    
    def test_neighbor_in_z(self):
        boid = Boid3D(0, 0, 0, 0, 0, 0)
        neighbor = Boid3D(0, 0, 10, 0, 0, 0)  # 10 units in +Z
        dv = compute_separation_3d(boid, [neighbor], 20, 0.1)
        assert dv[2] < 0  # Should flee in -Z direction

class TestBoundary3D:
    def test_near_z_min(self):
        boid = Boid3D(400, 300, 10, 0, 0, 0)  # Near z=0
        dv = apply_boundary_steering_3d(boid, 800, 600, 600, 75, 0.2)
        assert dv[2] > 0  # Should steer toward +Z
    
    def test_near_z_max(self):
        boid = Boid3D(400, 300, 590, 0, 0, 0)  # Near z=600
        dv = apply_boundary_steering_3d(boid, 800, 600, 600, 75, 0.2)
        assert dv[2] < 0  # Should steer toward -Z
```

#### Integration Tests: Flock3D

```python
class TestFlock3D:
    def test_boids_stay_in_bounds(self):
        """All boids should stay within 3D bounds."""
        params = SimulationParams3D(width=800, height=600, depth=600)
        flock = Flock3D(num_boids=50, params=params)
        
        for _ in range(500):
            flock.update()
            for boid in flock.boids:
                assert 0 <= boid.x <= 800
                assert 0 <= boid.y <= 600
                assert 0 <= boid.z <= 600
    
    def test_predators_hunt_in_3d(self):
        """Predators should chase boids in Z dimension."""
        params = SimulationParams3D(width=800, height=600, depth=600)
        flock = Flock3D(num_boids=20, params=params, 
                        enable_predator=True, num_predators=1)
        
        # Place predator at z=0, boids at z=500
        flock.predators[0].z = 0
        for boid in flock.boids:
            boid.z = 500
        
        initial_z = flock.predators[0].z
        for _ in range(100):
            flock.update()
        
        # Predator should have moved toward boids in Z
        assert flock.predators[0].z > initial_z
    
    def test_kdtree_finds_3d_neighbors(self):
        """KDTree should find neighbors in 3D space."""
        params = SimulationParams3D(width=800, height=600, depth=600)
        flock = Flock3D(num_boids=10, params=params)
        
        # Place boids: one at origin, one nearby in Z
        flock.boids[0].x, flock.boids[0].y, flock.boids[0].z = 400, 300, 300
        flock.boids[1].x, flock.boids[1].y, flock.boids[1].z = 400, 300, 310
        
        # Other boids far away
        for i in range(2, 10):
            flock.boids[i].x, flock.boids[i].y, flock.boids[i].z = 100, 100, 100
        
        flock._rebuild_kdtree()
        
        # Query neighbors of boid[0] within range 20
        indices = flock._kdtree.query_ball_point([400, 300, 300], r=20)
        
        assert 0 in indices  # Self
        assert 1 in indices  # Nearby boid in Z
        assert len(indices) == 2
```

#### Regression Tests

```python
class TestRegression3D:
    def test_2d_behavior_preserved_at_z_midpoint(self):
        """
        With all boids at z=depth/2 and vz=0,
        behavior should match 2D simulation.
        """
        # This ensures we didn't break 2D flocking logic
        pass
    
    def test_predator_strategies_work_in_3d(self):
        """All 5 hunting strategies should function in 3D."""
        for strategy in HuntingStrategy:
            # Test each strategy hunts correctly in Z dimension
            pass
```

### Frontend Tests

#### Visual Verification Checklist

- [ ] Boids render as 3D cones
- [ ] Boids orient along velocity vector
- [ ] Boundary box visible
- [ ] Camera orbit works smoothly
- [ ] Predators render with correct colors
- [ ] Obstacles render as spheres
- [ ] Performance acceptable at 100 boids
- [ ] No visual glitches at boundaries

#### Performance Benchmarks

| Boid Count | Target FPS | Actual FPS |
|------------|------------|------------|
| 50 | 60 | ? |
| 100 | 60 | ? |
| 200 | 30+ | ? |
| 500 | 15+ | ? |

---

## Implementation Phases

### Phase 1: Backend 3D Core (Est: 2-3 hours)
- [ ] Create `Boid3D` class
- [ ] Create `Predator3D` class  
- [ ] Create `Obstacle3D` class
- [ ] Implement 3D distance function
- [ ] Write unit tests for 3D classes

### Phase 2: Backend 3D Physics (Est: 3-4 hours)
- [ ] Implement `compute_separation_3d`
- [ ] Implement `compute_alignment_3d`
- [ ] Implement `compute_cohesion_3d`
- [ ] Implement `apply_boundary_steering_3d`
- [ ] Implement `compute_predator_avoidance_3d`
- [ ] Implement `compute_obstacle_avoidance_3d`
- [ ] Write unit tests for each rule

### Phase 3: Backend Flock3D (Est: 2-3 hours)
- [ ] Create `Flock3D` class
- [ ] Integrate 3D KDTree
- [ ] Update predator hunting strategies for 3D
- [ ] Write integration tests
- [ ] Verify boundary enforcement

### Phase 4: API Updates (Est: 1-2 hours)
- [ ] Update `SimulationParams` with depth
- [ ] Update `FrameData` for 3D coordinates
- [ ] Update config with 3D parameters
- [ ] Update WebSocket serialization
- [ ] Test API changes

### Phase 5: Frontend Three.js Setup (Est: 2-3 hours)
- [ ] Install Three.js dependencies
- [ ] Create basic scene (camera, lighting, renderer)
- [ ] Add OrbitControls
- [ ] Render boundary wireframe
- [ ] Test basic rendering

### Phase 6: Frontend Boid Rendering (Est: 2-3 hours)
- [ ] Create InstancedMesh for boids
- [ ] Implement position/rotation updates
- [ ] Verify orientation along velocity
- [ ] Performance test with many boids

### Phase 7: Frontend Polish (Est: 2-3 hours)
- [ ] Predator rendering with species colors
- [ ] Obstacle sphere rendering
- [ ] UI updates for depth parameter
- [ ] Camera reset button
- [ ] Optional: fog effect, trails

### Phase 8: Testing & Documentation (Est: 2 hours)
- [ ] Full integration test
- [ ] Performance benchmarking
- [ ] Update GENAI_USAGE.md
- [ ] Browser compatibility check

**Total Estimated Time: 16-23 hours**

---

## Performance Considerations

### Backend Optimization

1. **NumPy Vectorization**: Use array operations instead of loops where possible
2. **KDTree Efficiency**: Rebuild only when needed
3. **Parallel Update**: Compute all forces before applying (already doing this)

### Frontend Optimization

1. **InstancedMesh**: Critical for boid rendering (single draw call)
2. **DynamicDrawUsage**: Tell Three.js matrices update frequently
3. **Frustum Culling**: Automatic in Three.js
4. **LOD**: Could reduce detail for distant boids
5. **Object Pooling**: Reuse geometries and materials

### Memory Management

```typescript
// Reuse objects to avoid GC pressure
const tempMatrix = new THREE.Matrix4();
const tempPosition = new THREE.Vector3();
const tempQuaternion = new THREE.Quaternion();

function updateBoids(mesh: InstancedMesh, boids: number[][]) {
  for (let i = 0; i < boids.length; i++) {
    tempPosition.set(boids[i][0], boids[i][1], boids[i][2]);
    // ... reuse temp objects
  }
}
```

---

## File Structure After Implementation

```
backend/
├── boids/
│   ├── __init__.py          # Export 3D classes
│   ├── boid.py              # 2D (keep for compatibility)
│   ├── boid3d.py            # NEW: 3D boid
│   ├── predator.py          # 2D (keep)
│   ├── predator3d.py        # NEW: 3D predator
│   ├── obstacle.py          # 2D (keep)
│   ├── obstacle3d.py        # NEW: 3D obstacle
│   ├── flock.py             # 2D params
│   ├── flock_optimized.py   # 2D flock
│   ├── flock3d.py           # NEW: 3D flock
│   ├── rules_optimized.py   # 2D rules
│   └── rules3d.py           # NEW: 3D rules
├── tests/
│   ├── test_boid3d.py       # NEW
│   ├── test_rules3d.py      # NEW
│   ├── test_flock3d.py      # NEW
│   └── ...existing tests...
└── ...

frontend/
├── src/
│   ├── App.tsx              # Main app (mode toggle)
│   ├── Scene2D.tsx          # Extracted 2D canvas
│   ├── Scene3D.tsx          # NEW: Three.js scene
│   ├── BoidRenderer3D.ts    # NEW: Instanced boid mesh
│   ├── PredatorRenderer3D.ts # NEW
│   └── ...
└── ...
```

---

## Success Criteria

1. ✅ Boids flock naturally in 3D space
2. ✅ All 5 predator strategies work in 3D
3. ✅ Boundaries enforced on all 6 faces
4. ✅ Camera controls intuitive
5. ✅ Performance ≥30 FPS with 100 boids
6. ✅ All existing tests pass
7. ✅ New 3D tests comprehensive
8. ✅ Documentation complete

---

*Document created: January 2026*
*Status: Planning Complete*