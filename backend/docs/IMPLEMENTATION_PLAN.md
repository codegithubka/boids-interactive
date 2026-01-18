# Boids Interactive Demo — Implementation Plan

## Project Structure

```
boids-interactive/
├── SPECIFICATION.md          # Technical specification (this doc's companion)
├── IMPLEMENTATION_PLAN.md    # This document
├── README.md                 # Project overview and setup instructions
│
├── backend/
│   ├── main.py               # FastAPI application entry point
│   ├── config.py             # Configuration constants and limits
│   ├── models.py             # Pydantic models for validation
│   ├── simulation_manager.py # Per-client simulation controller
│   ├── presets.py            # Preset parameter definitions
│   ├── requirements.txt      # Python dependencies
│   │
│   ├── boids/                # Symlink or copy of existing simulation code
│   │   ├── __init__.py
│   │   ├── boid.py
│   │   ├── predator.py
│   │   ├── flock.py
│   │   ├── flock_optimized.py
│   │   ├── rules.py
│   │   ├── rules_optimized.py
│   │   └── metrics.py
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py       # Pytest fixtures
│       ├── test_models.py    # Parameter validation tests
│       ├── test_simulation.py # SimulationManager tests
│       └── test_websocket.py # WebSocket integration tests
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   │
│   ├── src/
│   │   ├── main.tsx          # Entry point
│   │   ├── App.tsx           # Main application component
│   │   ├── App.css           # Global styles
│   │   │
│   │   ├── components/
│   │   │   ├── Canvas.tsx           # Boid rendering canvas
│   │   │   ├── ControlPanel.tsx     # Parameter control container
│   │   │   ├── SliderControl.tsx    # Reusable slider component
│   │   │   ├── ToggleSwitch.tsx     # Boolean toggle component
│   │   │   ├── PresetButtons.tsx    # Preset selection buttons
│   │   │   ├── MetricsBar.tsx       # FPS and metrics display
│   │   │   └── ConnectionStatus.tsx # WebSocket status indicator
│   │   │
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts      # WebSocket connection management
│   │   │   └── useSimulation.ts     # Simulation state management
│   │   │
│   │   ├── types/
│   │   │   └── index.ts             # TypeScript type definitions
│   │   │
│   │   └── constants/
│   │       ├── parameters.ts        # Parameter definitions and limits
│   │       └── presets.ts           # Preset configurations
│   │
│   └── public/
│       └── favicon.ico
│
└── docker/
    ├── Dockerfile.backend
    ├── Dockerfile.frontend
    └── docker-compose.yml
```

---

## Implementation Phases

### Phase 1: Backend Core

**Goal**: Working WebSocket endpoint that streams boid positions

**Duration**: ~4 hours

#### Step 1.1: Project Setup

**Tasks**:
- [ ] Create directory structure
- [ ] Copy/symlink existing boids code
- [ ] Create requirements.txt
- [ ] Verify imports work

**Files**:
```
backend/
├── requirements.txt
└── boids/
    ├── __init__.py
    └── [existing files]
```

**Verification**:
```bash
cd backend
pip install -r requirements.txt
python -c "from boids.flock_optimized import FlockOptimized; print('OK')"
```

---

#### Step 1.2: Configuration Module

**Tasks**:
- [ ] Define parameter limits and defaults
- [ ] Create simulation constants
- [ ] Define message type enums

**File**: `backend/config.py`

**Key Contents**:
```python
# Parameter limits
PARAM_LIMITS = {
    "num_boids": (1, 200),
    "visual_range": (10.0, 150.0),
    # ... etc
}

# Default values
DEFAULT_PARAMS = {
    "num_boids": 50,
    "visual_range": 50.0,
    # ... etc
}

# Simulation constants
SIMULATION_WIDTH = 800
SIMULATION_HEIGHT = 600
TARGET_FPS = 60
```

**Verification**:
```python
from config import DEFAULT_PARAMS, PARAM_LIMITS
assert all(k in PARAM_LIMITS for k in DEFAULT_PARAMS)
```

---

#### Step 1.3: Pydantic Models

**Tasks**:
- [ ] Create SimulationParams model with validation
- [ ] Create message models for WebSocket communication
- [ ] Add custom validators for cross-field constraints

**File**: `backend/models.py`

**Key Contents**:
```python
class SimulationParams(BaseModel):
    num_boids: int = Field(ge=1, le=200, default=50)
    visual_range: float = Field(ge=10, le=150, default=50)
    # ... all parameters
    
    @model_validator(mode='after')
    def validate_ranges(self):
        if self.min_speed > self.max_speed:
            raise ValueError("min_speed must be <= max_speed")
        return self

class FrameData(BaseModel):
    type: Literal["frame"] = "frame"
    frame_id: int
    boids: List[List[float]]  # [[x, y, vx, vy], ...]
    predator: Optional[List[float]]
    metrics: Optional[dict]
```

**Tests**: `test_models.py`
- Valid parameters accepted
- Invalid parameters rejected with clear errors
- Cross-field validation works

---

#### Step 1.4: Simulation Manager

**Tasks**:
- [ ] Create SimulationManager class
- [ ] Implement flock initialization
- [ ] Implement frame data serialization
- [ ] Implement parameter updates
- [ ] Implement reset functionality

**File**: `backend/simulation_manager.py`

**Key Contents**:
```python
class SimulationManager:
    def __init__(self, params: SimulationParams = None):
        self.params = params or SimulationParams()
        self.flock = None
        self.frame_id = 0
        self.paused = False
        self.running = False
        self._init_flock()
    
    def _init_flock(self):
        """Create flock from current parameters."""
        
    def update(self):
        """Advance simulation one frame."""
        
    def get_frame_data(self) -> dict:
        """Serialize current state for WebSocket."""
        
    def update_params(self, updates: dict):
        """Apply partial parameter updates."""
        
    def reset(self):
        """Reset simulation with current parameters."""
```

**Tests**: `test_simulation.py`
- Manager initializes correctly
- Frame data has correct structure
- Parameter updates apply correctly
- Reset creates new boids
- num_boids change recreates flock

---

#### Step 1.5: WebSocket Endpoint

**Tasks**:
- [ ] Create FastAPI app
- [ ] Implement WebSocket endpoint
- [ ] Implement simulation loop
- [ ] Handle client messages
- [ ] Handle disconnection cleanup

**File**: `backend/main.py`

**Key Contents**:
```python
app = FastAPI()

@app.websocket("/ws/simulation")
async def simulation_websocket(websocket: WebSocket):
    await websocket.accept()
    manager = SimulationManager()
    
    try:
        # Start simulation loop task
        loop_task = asyncio.create_task(
            simulation_loop(manager, websocket)
        )
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_json()
            handle_message(manager, data)
            
    except WebSocketDisconnect:
        manager.stop()
```

**Verification**:
```bash
# Terminal 1
uvicorn main:app --reload

# Terminal 2 (using wscat or similar)
wscat -c ws://localhost:8000/ws/simulation
# Should see frame messages streaming
```

---

#### Step 1.6: Integration Testing

**Tasks**:
- [ ] Write WebSocket connection tests
- [ ] Test message handling
- [ ] Test parameter updates via WebSocket
- [ ] Verify frame rate

**File**: `backend/tests/test_websocket.py`

**Tests**:
- Connection established successfully
- Frames received at ~60fps
- Parameter update message changes simulation
- Reset message creates new boids
- Invalid messages don't crash server

---

### Phase 2: Backend Polish

**Goal**: Complete backend with presets, metrics, and robustness

**Duration**: ~3 hours

#### Step 2.1: Presets System

**Tasks**:
- [ ] Define all preset configurations
- [ ] Implement preset application in SimulationManager
- [ ] Handle preset WebSocket message
- [ ] Send params_sync after preset application

**File**: `backend/presets.py`

---

#### Step 2.2: Metrics Integration

**Tasks**:
- [ ] Add metrics collection to SimulationManager
- [ ] Compute metrics only when predator enabled
- [ ] Include metrics in frame data

---

#### Step 2.3: Pause/Resume

**Tasks**:
- [ ] Implement pause flag in SimulationManager
- [ ] Continue sending frames when paused (same data)
- [ ] Handle pause/resume messages

---

#### Step 2.4: Error Handling

**Tasks**:
- [ ] Graceful handling of invalid JSON
- [ ] Graceful handling of unknown message types
- [ ] Error message responses to client
- [ ] Logging for debugging

---

#### Step 2.5: Performance Optimization

**Tasks**:
- [ ] Profile frame generation time
- [ ] Optimize serialization if needed
- [ ] Test with 200 boids
- [ ] Test with 10 concurrent clients

---

### Phase 3: Frontend Core

**Goal**: Working React app with canvas and basic controls

**Duration**: ~4 hours

#### Step 3.1: Project Setup

**Tasks**:
- [ ] Initialize Vite + React + TypeScript project
- [ ] Configure build settings
- [ ] Set up basic project structure

**Commands**:
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
```

---

#### Step 3.2: Type Definitions

**Tasks**:
- [ ] Define TypeScript interfaces matching backend models
- [ ] Define parameter metadata (limits, steps, labels)

**File**: `frontend/src/types/index.ts`

---

#### Step 3.3: WebSocket Hook

**Tasks**:
- [ ] Implement connection management
- [ ] Handle reconnection on disconnect
- [ ] Parse incoming messages
- [ ] Expose send function for outgoing messages

**File**: `frontend/src/hooks/useWebSocket.ts`

---

#### Step 3.4: Simulation State Hook

**Tasks**:
- [ ] Manage simulation state (boids, predator, metrics)
- [ ] Manage parameter state
- [ ] Provide update functions

**File**: `frontend/src/hooks/useSimulation.ts`

---

#### Step 3.5: Canvas Component

**Tasks**:
- [ ] Set up canvas element
- [ ] Implement boid rendering (triangles)
- [ ] Implement predator rendering
- [ ] Use requestAnimationFrame for smooth rendering
- [ ] Optimize for 200 boids

**File**: `frontend/src/components/Canvas.tsx`

---

#### Step 3.6: Basic Controls

**Tasks**:
- [ ] Create SliderControl component
- [ ] Add num_boids slider
- [ ] Add visual_range slider
- [ ] Add separation_strength slider
- [ ] Wire up to WebSocket

**Files**: 
- `frontend/src/components/SliderControl.tsx`
- `frontend/src/components/ControlPanel.tsx`

---

### Phase 4: Frontend Polish

**Goal**: Complete UI with all controls and presets

**Duration**: ~4 hours

#### Step 4.1: All Parameter Controls

**Tasks**:
- [ ] Add predator toggle
- [ ] Add predator parameter sliders
- [ ] Create collapsible advanced section
- [ ] Add all advanced parameter sliders

---

#### Step 4.2: Preset Buttons

**Tasks**:
- [ ] Create PresetButtons component
- [ ] Style active preset indication
- [ ] Wire up to WebSocket

---

#### Step 4.3: Metrics Display

**Tasks**:
- [ ] Create MetricsBar component
- [ ] Show FPS
- [ ] Show boid count
- [ ] Show predator metrics when active

---

#### Step 4.4: Connection Status

**Tasks**:
- [ ] Show connected/disconnected status
- [ ] Show reconnecting state
- [ ] Error display

---

#### Step 4.5: Visual Polish

**Tasks**:
- [ ] Style sliders
- [ ] Add parameter tooltips
- [ ] Responsive layout
- [ ] Dark theme (optional)

---

### Phase 5: Integration & Deployment

**Goal**: Containerized, deployable application

**Duration**: ~2 hours

#### Step 5.1: Docker Setup

**Tasks**:
- [ ] Create backend Dockerfile
- [ ] Create frontend Dockerfile
- [ ] Create docker-compose.yml
- [ ] Test local deployment

---

#### Step 5.2: Documentation

**Tasks**:
- [ ] Write README with setup instructions
- [ ] Document API
- [ ] Add screenshots

---

## Acceptance Criteria Checklist

### Backend (Phases 1-2)

- [ ] WebSocket endpoint accepts connections
- [ ] Frames sent at 60fps
- [ ] Frame data contains boid positions and velocities
- [ ] Parameter updates change simulation behavior
- [ ] num_boids change recreates flock
- [ ] Presets apply correctly
- [ ] Pause/resume works
- [ ] Metrics included when predator enabled
- [ ] Graceful error handling
- [ ] 200 boids at 60fps
- [ ] 10 concurrent clients supported

### Frontend (Phases 3-4)

- [ ] Canvas renders boids smoothly
- [ ] Predator renders distinctly
- [ ] Sliders update parameters
- [ ] Debounced parameter updates
- [ ] Preset buttons work
- [ ] Advanced panel expands/collapses
- [ ] Metrics display updates
- [ ] Connection status shown
- [ ] Responsive layout
- [ ] Performance: 200 boids at 60fps

### Integration (Phase 5)

- [ ] Docker containers build
- [ ] docker-compose up works
- [ ] Frontend connects to backend
- [ ] Full flow works end-to-end

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| WebSocket latency | Medium | High | Client-side interpolation, reduce message size |
| Canvas performance | Low | Medium | Use WebGL if needed, batch operations |
| State sync issues | Medium | Medium | Server as source of truth, sync on connect |
| Browser compatibility | Low | Low | Test in Chrome, Firefox, Safari |
| Network bandwidth | Low | Medium | Compress messages if needed |

---

## Testing Commands

### Backend

```bash
cd backend

# Run all tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_simulation.py -v

# Run server for manual testing
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend

# Run dev server
npm run dev

# Build for production
npm run build

# Run tests (if configured)
npm test
```

### Integration

```bash
# Start everything
docker-compose up

# Rebuild after changes
docker-compose up --build
```

---

## Notes

1. **Backend first**: Complete backend before starting frontend to have stable API
2. **Test early**: Write tests as you implement, not after
3. **Simple first**: Get basic flow working before adding features
4. **Performance later**: Optimize only after functionality works

---

*Document Version: 1.0*
*Created: January 2026*
*Status: Ready to Begin Phase 1*