# Boids Interactive Demo — Technical Specification

## Project Overview

An interactive web-based demonstration of the Boids flocking simulation, allowing users to manipulate parameters in real-time and observe emergent behavior changes.

### Goals

1. **Educational**: Help users understand how simple rules create complex emergent behavior
2. **Interactive**: Real-time parameter manipulation with immediate visual feedback
3. **Performant**: Maintain 60fps with up to 200 boids
4. **Accessible**: Works in modern browsers, no installation required

### Non-Goals

- Mobile optimization (desktop-first)
- Multi-user shared simulation
- Persistent state/save functionality
- 3D visualization

---

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Main Layout                            │   │
│  │  ┌─────────────────────┐  ┌───────────────────────────┐  │   │
│  │  │                     │  │     Control Panel          │  │   │
│  │  │                     │  │  ┌─────────────────────┐   │  │   │
│  │  │   Canvas Display    │  │  │  Preset Buttons     │   │  │   │
│  │  │   (800 x 600)       │  │  ├─────────────────────┤   │  │   │
│  │  │                     │  │  │  Primary Sliders    │   │  │   │
│  │  │   - Boids (blue)    │  │  │  - num_boids        │   │  │   │
│  │  │   - Predator (red)  │  │  │  - visual_range     │   │  │   │
│  │  │   - Trails (opt)    │  │  │  - separation       │   │  │   │
│  │  │                     │  │  ├─────────────────────┤   │  │   │
│  │  │                     │  │  │  Predator Toggle    │   │  │   │
│  │  │                     │  │  │  - enabled          │   │  │   │
│  │  │                     │  │  │  - speed            │   │  │   │
│  │  │                     │  │  ├─────────────────────┤   │  │   │
│  │  │                     │  │  │  Advanced (expand)  │   │  │   │
│  │  │                     │  │  │  - cohesion         │   │  │   │
│  │  │                     │  │  │  - alignment        │   │  │   │
│  │  │                     │  │  │  - max_speed        │   │  │   │
│  │  └─────────────────────┘  │  └─────────────────────┘   │  │   │
│  │                           │                             │  │   │
│  │  ┌─────────────────────────────────────────────────┐   │  │   │
│  │  │              Metrics Bar                         │   │  │   │
│  │  │  FPS: 60  |  Boids: 50  |  Avg Dist: 234px      │   │  │   │
│  │  └─────────────────────────────────────────────────┘   │  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              │ WebSocket                         │
│                              ▼                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               │
                    JSON Messages (bidirectional)
                               │
┌──────────────────────────────┼───────────────────────────────────┐
│                        FastAPI Backend                           │
│                              │                                   │
│  ┌───────────────────────────┴────────────────────────────────┐ │
│  │                   WebSocket Manager                         │ │
│  │  - Connection handling                                      │ │
│  │  - Message routing                                          │ │
│  │  - Client state management                                  │ │
│  └───────────────────────────┬────────────────────────────────┘ │
│                              │                                   │
│  ┌───────────────────────────┴────────────────────────────────┐ │
│  │                 Simulation Manager                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │ │
│  │  │FlockOptimized│  │   Predator   │  │   Metrics    │      │ │
│  │  │              │  │              │  │  Collector   │      │ │
│  │  │ - boids[]    │  │ - position   │  │              │      │ │
│  │  │ - params     │  │ - velocity   │  │ - fps        │      │ │
│  │  │ - update()   │  │ - update()   │  │ - distances  │      │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Existing Boids Code                      │ │
│  │  boid.py | flock.py | flock_optimized.py | predator.py     │ │
│  │  rules.py | rules_optimized.py | metrics.py                │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## API Specification

### WebSocket Endpoint

**URL**: `ws://localhost:8000/ws/simulation`

**Connection Flow**:
1. Client connects to WebSocket
2. Server creates dedicated SimulationManager for this client
3. Server starts sending frames at 60fps
4. Client sends parameter updates as needed
5. On disconnect, server cleans up simulation

### Message Types

#### Client → Server

**1. Update Parameters**
```json
{
  "type": "update_params",
  "params": {
    "num_boids": 75,
    "visual_range": 60,
    "separation_strength": 0.2,
    "predator_enabled": true,
    "predator_speed": 3.0
  }
}
```
- Only include changed parameters
- Server validates ranges before applying
- Invalid values are ignored (not rejected)

**2. Reset Simulation**
```json
{
  "type": "reset"
}
```
- Recreates flock with current parameters
- Randomizes all boid positions/velocities

**3. Apply Preset**
```json
{
  "type": "preset",
  "name": "tight_swarm"
}
```
- Server applies predefined parameter set
- Responds with full parameter state

**4. Pause/Resume**
```json
{
  "type": "pause"
}
```
```json
{
  "type": "resume"
}
```

#### Server → Client

**1. Frame Update (60fps)**
```json
{
  "type": "frame",
  "frame_id": 12345,
  "boids": [
    [123.4, 456.7, 2.1, -1.3],
    [234.5, 567.8, -1.2, 2.4]
  ],
  "predator": [400.0, 300.0, 1.5, 0.8],
  "metrics": {
    "fps": 60,
    "avg_distance_to_predator": 234.5,
    "min_distance_to_predator": 45.2,
    "flock_cohesion": 67.8
  }
}
```
- `boids`: Array of [x, y, vx, vy] for each boid
- `predator`: [x, y, vx, vy] or `null` if disabled
- `metrics`: Only included if predator enabled

**2. Parameter Sync**
```json
{
  "type": "params_sync",
  "params": {
    "num_boids": 50,
    "visual_range": 50,
    "protected_range": 12,
    "max_speed": 3.0,
    "min_speed": 2.0,
    "cohesion_factor": 0.002,
    "alignment_factor": 0.06,
    "separation_strength": 0.15,
    "margin": 75,
    "turn_factor": 0.2,
    "predator_enabled": false,
    "predator_speed": 2.5,
    "predator_avoidance_strength": 0.5,
    "predator_detection_range": 100,
    "predator_hunting_strength": 0.05
  }
}
```
- Sent on connection and after preset application
- Client syncs UI state to match

**3. Error**
```json
{
  "type": "error",
  "message": "Invalid parameter: num_boids must be between 1 and 500"
}
```

---

## Parameter Specification

### Parameter Definitions

| Parameter | Type | Min | Max | Default | Step | Category |
|-----------|------|-----|-----|---------|------|----------|
| `num_boids` | int | 1 | 200 | 50 | 1 | Primary |
| `visual_range` | float | 10 | 150 | 50 | 5 | Primary |
| `separation_strength` | float | 0.01 | 0.5 | 0.15 | 0.01 | Primary |
| `predator_enabled` | bool | — | — | false | — | Predator |
| `predator_speed` | float | 0.5 | 5.0 | 2.5 | 0.1 | Predator |
| `predator_avoidance_strength` | float | 0.05 | 1.5 | 0.5 | 0.05 | Predator |
| `protected_range` | float | 2 | 50 | 12 | 1 | Advanced |
| `cohesion_factor` | float | 0.0001 | 0.02 | 0.002 | 0.0005 | Advanced |
| `alignment_factor` | float | 0.01 | 0.2 | 0.06 | 0.01 | Advanced |
| `max_speed` | float | 1.0 | 8.0 | 3.0 | 0.5 | Advanced |
| `min_speed` | float | 0.5 | 4.0 | 2.0 | 0.5 | Advanced |
| `margin` | float | 20 | 150 | 75 | 5 | Advanced |
| `turn_factor` | float | 0.05 | 0.8 | 0.2 | 0.05 | Advanced |
| `predator_detection_range` | float | 30 | 250 | 100 | 10 | Advanced |
| `predator_hunting_strength` | float | 0.01 | 0.2 | 0.05 | 0.01 | Advanced |

### Parameter Validation Rules

1. `min_speed` must be ≤ `max_speed`
2. `protected_range` must be < `visual_range`
3. `num_boids` changes trigger flock recreation
4. All other parameters apply immediately

### Presets

| Preset Name | Description | Key Parameter Changes |
|-------------|-------------|----------------------|
| `default` | Balanced flocking | All defaults |
| `tight_swarm` | Dense ball formation | cohesion×3, separation×0.5, visual_range×0.6 |
| `loose_cloud` | Spread out drifting | cohesion×0.3, separation×2, visual_range×1.5 |
| `high_speed` | Fast chaotic movement | max_speed=6, min_speed=4, alignment×0.5 |
| `slow_dance` | Graceful synchronized | max_speed=1.5, min_speed=1, alignment×2 |
| `predator_chase` | Dramatic chase | predator_enabled, predator_speed=3.5, avoidance×1.5 |
| `swarm_defense` | Tight when threatened | predator_enabled, cohesion×2, avoidance×0.8 |

---

## Frontend Specification

### Component Hierarchy

```
App
├── Header
│   └── Title + GitHub link
├── MainContent
│   ├── SimulationCanvas
│   │   ├── BoidRenderer
│   │   ├── PredatorRenderer
│   │   └── DebugOverlay (optional)
│   └── ControlPanel
│       ├── PresetButtonGroup
│       ├── PrimaryControls
│       │   ├── SliderControl (num_boids)
│       │   ├── SliderControl (visual_range)
│       │   └── SliderControl (separation_strength)
│       ├── PredatorControls
│       │   ├── ToggleSwitch (predator_enabled)
│       │   ├── SliderControl (predator_speed)
│       │   └── SliderControl (avoidance_strength)
│       ├── AdvancedControls (collapsible)
│       │   └── SliderControl × 9
│       └── ActionButtons
│           ├── ResetButton
│           └── PauseButton
├── MetricsBar
│   ├── FPSDisplay
│   ├── BoidCountDisplay
│   └── DistanceMetrics (when predator active)
└── Footer
    └── Credits + Links
```

### State Management

```typescript
interface SimulationState {
  // Connection
  connected: boolean;
  error: string | null;
  
  // Simulation data (from server)
  frameId: number;
  boids: [number, number, number, number][];  // [x, y, vx, vy]
  predator: [number, number, number, number] | null;
  metrics: {
    fps: number;
    avgDistance: number | null;
    minDistance: number | null;
    cohesion: number | null;
  };
  
  // Parameters (synced with server)
  params: SimulationParams;
  
  // UI state
  paused: boolean;
  advancedExpanded: boolean;
  activePreset: string | null;
}

interface SimulationParams {
  num_boids: number;
  visual_range: number;
  protected_range: number;
  max_speed: number;
  min_speed: number;
  cohesion_factor: number;
  alignment_factor: number;
  separation_strength: number;
  margin: number;
  turn_factor: number;
  predator_enabled: boolean;
  predator_speed: number;
  predator_avoidance_strength: number;
  predator_detection_range: number;
  predator_hunting_strength: number;
}
```

### Canvas Rendering

**Dimensions**: 800 × 600 pixels (matching simulation bounds)

**Boid Rendering**:
- Shape: Triangle pointing in velocity direction
- Size: 8px length
- Color: Cornflower blue (#6495ED)
- Optional: Velocity trail (last 5 positions, fading)

**Predator Rendering**:
- Shape: Larger triangle (15px)
- Color: Red (#DC3C3C) with yellow outline
- Visual distinction from boids

**Performance Targets**:
- Render 200 boids at 60fps
- Use requestAnimationFrame
- Batch drawing operations
- Consider OffscreenCanvas for heavy loads

### UI/UX Guidelines

1. **Responsiveness**: Sliders update simulation within 50ms
2. **Feedback**: Visual confirmation when parameters change
3. **Accessibility**: Keyboard navigation for all controls
4. **Tooltips**: Explain each parameter on hover
5. **Mobile**: Warning that desktop is recommended

---

## Backend Specification

### Module Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── config.py               # Configuration and constants
├── models.py               # Pydantic models for validation
├── simulation_manager.py   # Per-client simulation handler
├── presets.py              # Preset parameter definitions
├── websocket_handler.py    # WebSocket message routing
└── boids/                  # Existing simulation code
    ├── __init__.py
    ├── boid.py
    ├── predator.py
    ├── flock.py
    ├── flock_optimized.py
    ├── rules.py
    ├── rules_optimized.py
    └── metrics.py
```

### Class Definitions

#### SimulationManager

```python
class SimulationManager:
    """Manages simulation state for a single WebSocket client."""
    
    def __init__(self, params: SimulationParams = None):
        """Initialize with default or provided parameters."""
        
    async def start(self, websocket: WebSocket) -> None:
        """Start the simulation loop, sending frames to client."""
        
    def stop(self) -> None:
        """Stop the simulation loop."""
        
    def update_params(self, params: dict) -> None:
        """Update simulation parameters (partial update supported)."""
        
    def apply_preset(self, preset_name: str) -> SimulationParams:
        """Apply a preset and return the new parameters."""
        
    def reset(self) -> None:
        """Reset simulation with current parameters."""
        
    def pause(self) -> None:
        """Pause simulation (stop updating, keep sending last frame)."""
        
    def resume(self) -> None:
        """Resume simulation updates."""
        
    def get_frame_data(self) -> dict:
        """Get current frame data for sending to client."""
        
    def get_params(self) -> SimulationParams:
        """Get current parameter values."""
```

#### WebSocket Message Models

```python
class UpdateParamsMessage(BaseModel):
    type: Literal["update_params"]
    params: dict  # Partial parameter update

class ResetMessage(BaseModel):
    type: Literal["reset"]

class PresetMessage(BaseModel):
    type: Literal["preset"]
    name: str

class PauseMessage(BaseModel):
    type: Literal["pause"]

class ResumeMessage(BaseModel):
    type: Literal["resume"]

# Union type for incoming messages
ClientMessage = Union[UpdateParamsMessage, ResetMessage, PresetMessage, PauseMessage, ResumeMessage]
```

### Concurrency Model

- Each WebSocket connection gets its own `SimulationManager`
- Simulation runs in asyncio task (non-blocking)
- Parameter updates are thread-safe via asyncio
- Frame sending is rate-limited to 60fps

```python
async def simulation_loop(manager: SimulationManager, websocket: WebSocket):
    """Main simulation loop for a client."""
    target_frame_time = 1.0 / 60  # 60fps
    
    while manager.running:
        frame_start = time.perf_counter()
        
        if not manager.paused:
            manager.flock.update()
        
        frame_data = manager.get_frame_data()
        await websocket.send_json(frame_data)
        
        # Rate limiting
        elapsed = time.perf_counter() - frame_start
        sleep_time = target_frame_time - elapsed
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
```

### Error Handling

| Error | Response |
|-------|----------|
| Invalid JSON | Send error message, continue |
| Unknown message type | Send error message, continue |
| Invalid parameter value | Send error message, ignore parameter |
| WebSocket disconnect | Clean up simulation |
| Server error | Log error, send error message if possible |

---

## Performance Requirements

### Backend

| Metric | Target |
|--------|--------|
| Frame computation (200 boids) | < 10ms |
| Frame serialization | < 2ms |
| WebSocket send | < 1ms |
| Total frame time | < 16.67ms (60fps) |
| Memory per client | < 50MB |
| Max concurrent clients | 10 |

### Frontend

| Metric | Target |
|--------|--------|
| Frame render (200 boids) | < 5ms |
| Parameter update latency | < 50ms |
| Initial load time | < 3s |
| Bundle size | < 500KB |

### Network

| Metric | Target |
|--------|--------|
| Frame message size (50 boids) | ~2KB |
| Frame message size (200 boids) | ~8KB |
| Bandwidth per client | ~500KB/s |

---

## Testing Strategy

### Backend Tests

| Test Category | Description |
|---------------|-------------|
| Unit: SimulationManager | Parameter updates, reset, pause/resume |
| Unit: Message parsing | Valid/invalid message handling |
| Unit: Presets | All presets apply correctly |
| Integration: WebSocket | Connection, message flow, disconnection |
| Performance: Frame rate | Maintains 60fps with 200 boids |
| Load: Multiple clients | 10 concurrent connections |

### Frontend Tests

| Test Category | Description |
|---------------|-------------|
| Unit: Components | Render correctly with props |
| Unit: Hooks | WebSocket connection management |
| Integration: Sliders | Parameter changes sent to server |
| E2E: Full flow | Connect, change params, see updates |
| Visual: Rendering | Boids render correctly |

---

## Development Phases

### Phase 1: Backend Core (Current Target)

**Deliverables**:
- FastAPI WebSocket endpoint
- SimulationManager class
- Parameter validation
- Frame serialization
- Basic tests

**Acceptance Criteria**:
- WebSocket connection works
- Frames sent at 60fps
- Parameters can be updated
- Simulation resets correctly

### Phase 2: Backend Polish

**Deliverables**:
- Preset system
- Pause/resume
- Metrics in frames
- Error handling
- Comprehensive tests

**Acceptance Criteria**:
- All presets work
- Graceful error handling
- 10 concurrent clients supported

### Phase 3: Frontend Core

**Deliverables**:
- React project setup
- Canvas rendering
- WebSocket hook
- Basic sliders
- Metrics display

**Acceptance Criteria**:
- Boids render smoothly
- Sliders update simulation
- Connection status shown

### Phase 4: Frontend Polish

**Deliverables**:
- All parameter controls
- Preset buttons
- Advanced panel
- Tooltips and help
- Responsive design
- Visual polish

**Acceptance Criteria**:
- All features work
- Good user experience
- Performance targets met

### Phase 5: Integration & Deployment

**Deliverables**:
- Docker containerization
- CI/CD pipeline
- Documentation
- Demo deployment

**Acceptance Criteria**:
- One-command startup
- Stable in production

---

## File Manifest

### Backend Files to Create

| File | Purpose | Priority |
|------|---------|----------|
| `backend/main.py` | FastAPI app, WebSocket endpoint | P1 |
| `backend/config.py` | Constants, parameter limits | P1 |
| `backend/models.py` | Pydantic validation models | P1 |
| `backend/simulation_manager.py` | Per-client simulation | P1 |
| `backend/presets.py` | Preset definitions | P2 |
| `backend/requirements.txt` | Dependencies | P1 |
| `backend/tests/test_simulation.py` | Unit tests | P1 |
| `backend/tests/test_websocket.py` | Integration tests | P2 |

### Frontend Files to Create

| File | Purpose | Priority |
|------|---------|----------|
| `frontend/src/App.tsx` | Main application | P3 |
| `frontend/src/components/Canvas.tsx` | Boid rendering | P3 |
| `frontend/src/components/ControlPanel.tsx` | Parameter controls | P3 |
| `frontend/src/components/SliderControl.tsx` | Reusable slider | P3 |
| `frontend/src/hooks/useWebSocket.ts` | Connection management | P3 |
| `frontend/src/hooks/useSimulation.ts` | State management | P3 |
| `frontend/src/types.ts` | TypeScript interfaces | P3 |
| `frontend/src/constants.ts` | Parameter definitions | P3 |
| `frontend/src/presets.ts` | Preset buttons | P4 |

---

## Dependencies

### Backend

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
websockets>=12.0
pydantic>=2.5.0
numpy>=1.26.0
scipy>=1.12.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

### Frontend

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Frame rate | Stable 60fps |
| Parameter latency | < 100ms perceived |
| Crash rate | 0 |
| User engagement | > 2 min average session |
| Educational value | Users understand flocking rules |

---

## Appendix: Preset Parameter Values

### Default
```python
DEFAULT_PARAMS = {
    "num_boids": 50,
    "visual_range": 50,
    "protected_range": 12,
    "max_speed": 3.0,
    "min_speed": 2.0,
    "cohesion_factor": 0.002,
    "alignment_factor": 0.06,
    "separation_strength": 0.15,
    "margin": 75,
    "turn_factor": 0.2,
    "predator_enabled": False,
    "predator_speed": 2.5,
    "predator_avoidance_strength": 0.5,
    "predator_detection_range": 100,
    "predator_hunting_strength": 0.05
}
```

### Tight Swarm
```python
TIGHT_SWARM = {
    **DEFAULT_PARAMS,
    "visual_range": 30,
    "cohesion_factor": 0.006,
    "separation_strength": 0.08,
}
```

### Loose Cloud
```python
LOOSE_CLOUD = {
    **DEFAULT_PARAMS,
    "visual_range": 75,
    "cohesion_factor": 0.0006,
    "separation_strength": 0.3,
}
```

### High Speed
```python
HIGH_SPEED = {
    **DEFAULT_PARAMS,
    "max_speed": 6.0,
    "min_speed": 4.0,
    "alignment_factor": 0.03,
}
```

### Slow Dance
```python
SLOW_DANCE = {
    **DEFAULT_PARAMS,
    "max_speed": 1.5,
    "min_speed": 1.0,
    "alignment_factor": 0.12,
}
```

### Predator Chase
```python
PREDATOR_CHASE = {
    **DEFAULT_PARAMS,
    "predator_enabled": True,
    "predator_speed": 3.5,
    "predator_avoidance_strength": 0.75,
}
```

### Swarm Defense
```python
SWARM_DEFENSE = {
    **DEFAULT_PARAMS,
    "predator_enabled": True,
    "cohesion_factor": 0.004,
    "predator_avoidance_strength": 0.4,
}
```

---

*Document Version: 1.0*
*Created: January 2026*
*Status: Ready for Implementation*