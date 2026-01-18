# GenAI Usage Documentation — Boids Interactive Demo

## Project Overview

This document tracks the development of an interactive web-based Boids simulation demo using GenAI assistance. The project consists of a FastAPI backend serving simulation frames via WebSocket and a React frontend for visualization and parameter control.

**Related Project**: This builds on the core Boids simulation in `/boids/`.

---

## Project Status

| Step | Component | Status | Tests |
|------|-----------|--------|-------|
| 1 | Project structure | ✅ Complete | — |
| 2 | requirements.txt | ✅ Complete | — |
| 3 | config.py | ✅ Complete | 35 |
| 4 | models.py | ✅ Complete | 36 |
| 5 | simulation_manager.py | ✅ Complete | 33 |
| 6 | presets.py | ✅ Complete | 22 |
| 7 | main.py (WebSocket) | ✅ Complete | 15 |
| 8 | Frontend setup (initial) | ⚠️ Issue | — |
| 9 | WebSocket debugging | ✅ Resolved | — |
| 10 | Enhanced visuals | ✅ Complete | — |
| **Optional Enhancements** | | | |
| 11 | Static Obstacles | ✅ Complete | 34 |
| 12 | Multiple Predators | ✅ Complete | 23 |
| 12.7 | Predator Species | ✅ Complete | 23 |
| 12.8 | Boundary Regression Fix | ✅ Complete | 19 |
| 12.9 | Hunting Improvements | ✅ Complete | 34 |
| 12.10 | Min Speed Slider | ✅ Complete | — |
| 13 | Performance Optimization | ⏳ Planned | — |
| 14 | 3D Implementation | 🔄 Reverted | — |
| 15 | Docker Containerization | ✅ Complete | — |

**Total Backend Tests**: 357 passing
**Backend Status**: ✅ Complete
**Frontend Status**: ✅ Complete (2D)
**Docker Status**: ✅ Working (~48 FPS)
**Project Status**: ✅ Production Ready

---

## Development Log

### Step 1: Project Structure Setup

**Date**: January 2026

**Prompt**: "Create the project directory structure for an interactive boids demo with FastAPI backend and React frontend. Include GENAI_USAGE.md to track development."

**Actions taken**:
- Created directory structure
- Copied existing boids simulation code to `backend/boids/`
- Created `backend/boids/__init__.py`
- Created this documentation file

**Directory structure created**:
```
boids-interactive/
├── GENAI_USAGE.md           # This file
├── backend/
│   ├── boids/               # Copied from existing project
│   │   ├── __init__.py
│   │   ├── boid.py
│   │   ├── predator.py
│   │   ├── flock.py
│   │   ├── flock_optimized.py
│   │   ├── rules.py
│   │   ├── rules_optimized.py
│   │   └── metrics.py
│   └── tests/
└── frontend/
    ├── public/
    └── src/
        ├── components/
        ├── hooks/
        └── types/
```

**Files created**:
| File | Lines | Description |
|------|-------|-------------|
| `backend/boids/__init__.py` | 28 | Package exports |
| `GENAI_USAGE.md` | — | This documentation |

**Status**: ✅ Complete

---

### Step 2: Requirements

**Prompt**: "Create requirements.txt with dependencies for FastAPI, WebSocket support, Pydantic validation, and testing."

**Actions taken**:
- Created `requirements.txt` with all dependencies
- Fixed relative imports in boids package (changed `from boid import` to `from .boid import`)
- Verified all imports work
- Verified simulation runs correctly

**Files created/modified**:
| File | Description |
|------|-------------|
| `requirements.txt` | 15 lines, 8 dependencies |
| `boids/*.py` | Fixed relative imports for package structure |

**Dependencies**:
| Package | Purpose |
|---------|---------|
| fastapi | Web framework with WebSocket support |
| uvicorn[standard] | ASGI server |
| websockets | WebSocket protocol |
| pydantic | Data validation |
| numpy | Numerical computing |
| scipy | KDTree for optimization |
| pytest | Testing framework |
| pytest-asyncio | Async test support |
| httpx | HTTP client for testing |

**Verification**:
```bash
# All imports successful
# Boids simulation runs correctly
```

**Status**: ✅ Complete

---

### Step 3: Configuration

**Prompt**: "Create config.py with parameter definitions, limits, defaults, and validation helpers."

**Actions taken**:
- Created `config.py` with all parameter definitions
- Created `conftest.py` for pytest path configuration
- Created `test_config.py` with comprehensive tests
- Ran tests: 35/35 passing

**Files created**:
| File | Lines | Description |
|------|-------|-------------|
| `config.py` | 198 | Parameter definitions, validation, constants |
| `tests/conftest.py` | 10 | Pytest configuration |
| `tests/test_config.py` | 208 | 35 unit tests |

**Key components**:
| Component | Description |
|-----------|-------------|
| `ParamLimit` | Dataclass with min, max, default, step, category, label, description |
| `PARAM_DEFINITIONS` | Dict of 15 parameters with full metadata |
| `DEFAULT_PARAMS` | Quick access to default values |
| `PRIMARY_PARAMS` | 3 always-visible parameters |
| `PREDATOR_PARAMS` | 3 predator-related parameters |
| `ADVANCED_PARAMS` | 9 advanced parameters |
| `validate_param()` | Returns (is_valid, error_message) |
| `clamp_param()` | Clamps value to valid range |
| `get_default()` | Get default for parameter |
| `MessageType` | WebSocket message type constants |
| `PresetName` | 7 preset name constants |

**Tests**: 35/35 passing
| Test Class | Tests |
|------------|-------|
| TestSimulationConstants | 2 |
| TestParamDefinitions | 7 |
| TestDefaultParams | 4 |
| TestParamCategories | 5 |
| TestValidation | 6 |
| TestClamp | 4 |
| TestGetDefault | 2 |
| TestMessageTypes | 2 |
| TestPresets | 3 |

**Status**: ✅ Complete

---

### Step 4: Pydantic Models

**Prompt**: "Create models.py with Pydantic models for SimulationParams, WebSocket messages, and FrameData."

**Actions taken**:
- Created `models.py` with all Pydantic models
- Created `test_models.py` with comprehensive tests
- Ran tests: 36/36 passing (71 total)

**Files created**:
| File | Lines | Description |
|------|-------|-------------|
| `models.py` | 224 | Pydantic validation models |
| `tests/test_models.py` | 233 | 36 unit tests |

**Key components**:
| Model | Purpose |
|-------|---------|
| `SimulationParams` | Validated parameters with cross-field validation |
| `UpdateParamsMessage` | Client message: update parameters |
| `ResetMessage` | Client message: reset simulation |
| `PresetMessage` | Client message: apply preset |
| `PauseMessage` | Client message: pause |
| `ResumeMessage` | Client message: resume |
| `FrameMetrics` | Server: metrics in frame |
| `FrameData` | Server: frame data with boids, predator, metrics |
| `ParamsSyncMessage` | Server: sync all params |
| `ErrorMessage` | Server: error response |
| `parse_client_message()` | Helper to parse incoming messages |

**Validation features**:
- Field-level validation (min, max, types)
- Cross-field validation (min_speed <= max_speed)
- Cross-field validation (protected_range < visual_range)
- Preset name validation

**Tests**: 36/36 passing
| Test Class | Tests |
|------------|-------|
| TestSimulationParams | 12 |
| TestUpdateParamsMessage | 3 |
| TestResetMessage | 1 |
| TestPresetMessage | 3 |
| TestPauseResumeMessages | 2 |
| TestFrameMetrics | 2 |
| TestFrameData | 3 |
| TestParamsSyncMessage | 1 |
| TestErrorMessage | 1 |
| TestParseClientMessage | 8 |

**Status**: ✅ Complete

---

### Step 5: Simulation Manager

**Prompt**: "Create simulation_manager.py that wraps FlockOptimized, handles parameter updates, and produces frame data."

**Actions taken**:
- Created `simulation_manager.py` with SimulationManager class
- Created `test_simulation.py` with comprehensive tests
- Ran tests: 33/33 passing (104 total)

**Files created**:
| File | Lines | Description |
|------|-------|-------------|
| `simulation_manager.py` | 250 | Simulation controller class |
| `tests/test_simulation.py` | 250 | 33 unit tests |

**Key components**:
| Method | Purpose |
|--------|---------|
| `__init__()` | Initialize with params, seed, create flock |
| `start()` / `stop()` | Lifecycle control |
| `pause()` / `resume()` | Pause/resume simulation |
| `update()` | Advance simulation by one frame |
| `reset()` | Reset to initial state |
| `update_params()` | Update parameters (recreates flock if needed) |
| `get_frame_data()` | Serialize current state for WebSocket |
| `get_params_dict()` | Get all current parameters |

**Properties**:
| Property | Description |
|----------|-------------|
| `is_running` | Whether simulation is running |
| `is_paused` | Whether simulation is paused |
| `frame_id` | Current frame number |
| `num_boids` | Current boid count |
| `has_predator` | Whether predator is active |
| `fps` | Current frames per second |

**Tests**: 33/33 passing
| Test Class | Tests |
|------------|-------|
| TestSimulationManagerInit | 6 |
| TestSimulationManagerLifecycle | 4 |
| TestSimulationManagerUpdate | 4 |
| TestSimulationManagerReset | 3 |
| TestSimulationManagerParams | 6 |
| TestSimulationManagerFrameData | 7 |
| TestSimulationManagerProperties | 3 |

**Status**: ✅ Complete

---

### Step 6: Presets

**Prompt**: "Create presets.py with predefined parameter configurations for different behaviors."

**Actions taken**:
- Created `presets.py` with 7 preset configurations
- Created `test_presets.py` with comprehensive tests
- Ran tests: 22/22 passing (126 total)

**Files created**:
| File | Lines | Description |
|------|-------|-------------|
| `presets.py` | 115 | Preset definitions and helpers |
| `tests/test_presets.py` | 155 | 22 unit tests |

**Presets defined**:
| Preset | Description |
|--------|-------------|
| `default` | Standard parameters |
| `tight_swarm` | High cohesion, tight formations |
| `loose_cloud` | Low cohesion, dispersed flock |
| `high_speed` | Fast boids, quick turns |
| `slow_dance` | Slow, graceful movement |
| `predator_chase` | Active predator, fast evasion |
| `swarm_defense` | Strong predator avoidance, tight grouping |

**Helper functions**:
| Function | Purpose |
|----------|---------|
| `get_preset(name)` | Get preset dict or None |
| `get_preset_params(name)` | Get preset dict, default fallback |
| `is_valid_preset(name)` | Check if preset name valid |
| `list_presets()` | Get all preset names |

**Tests**: 22/22 passing
| Test Class | Tests |
|------------|-------|
| TestPresetDefinitions | 5 |
| TestPresetCharacteristics | 8 |
| TestGetPreset | 3 |
| TestGetPresetParams | 2 |
| TestIsValidPreset | 2 |
| TestListPresets | 2 |

**Status**: ✅ Complete

---

### Step 7: FastAPI WebSocket Server

**Prompt**: "Create main.py with FastAPI app, WebSocket endpoint, and frame streaming."

**Actions taken**:
- Created `main.py` with FastAPI application
- Created `test_websocket.py` with WebSocket tests
- Ran tests: 15/15 passing (141 total)

**Files created**:
| File | Lines | Description |
|------|-------|-------------|
| `main.py` | 175 | FastAPI WebSocket server |
| `tests/test_websocket.py` | 200 | 15 WebSocket tests |

**Key components**:
| Component | Purpose |
|-----------|---------|
| `app` | FastAPI application with CORS |
| `ConnectionManager` | Manages WebSocket connections and simulations |
| `handle_message()` | Dispatches incoming messages |
| `/` | Root health check |
| `/health` | Health endpoint |
| `/ws` | WebSocket endpoint |

**WebSocket Protocol**:
| Direction | Message | Description |
|-----------|---------|-------------|
| Server → Client | `params_sync` | Sent on connect and after param changes |
| Server → Client | `frame` | Sent at 60 FPS with boids, predator, metrics |
| Server → Client | `error` | Sent on invalid messages |
| Client → Server | `update_params` | Update simulation parameters |
| Client → Server | `reset` | Reset simulation |
| Client → Server | `preset` | Apply preset configuration |
| Client → Server | `pause` | Pause simulation |
| Client → Server | `resume` | Resume simulation |

**Tests**: 15/15 passing
| Test Class | Tests |
|------------|-------|
| TestRESTEndpoints | 2 |
| TestWebSocketConnection | 3 |
| TestWebSocketMessages | 6 |
| TestFrameData | 4 |

**Status**: ✅ Complete

---

## Backend Complete! 🎉

**Total Backend Tests**: 141 passing

### Running the Server

```bash
cd backend
source venv/bin/activate
python main.py
```

Server starts at `http://localhost:8000`

---

### Step 8: Frontend Setup (Initial Attempt)

**Prompt**: "Create React frontend with Vite and TypeScript for the boids interactive demo."

**Actions taken**:
- Initialized Vite + React + TypeScript project
- Created TypeScript types, constants, hooks, and components
- Build successful

**Initial Architecture**:
```
src/
├── types/index.ts          # TypeScript definitions
├── constants/index.ts      # Parameter definitions
├── hooks/useSimulation.ts  # WebSocket hook with useEffect cleanup
├── components/
│   ├── SimulationCanvas.tsx
│   ├── Controls.tsx
│   └── Controls.css
├── App.tsx
└── App.css
```

**Status**: ⚠️ Build successful, but runtime issue encountered

---

### Step 9: WebSocket Connection Issue — Debugging & Resolution

**Issue Encountered**: WebSocket connection opened but immediately closed

**Symptoms**:
- Frontend showed "Connecting..." then immediately "disconnected"
- Backend logs showed:
  ```
  DEBUG: WebSocket accepted
  DEBUG: SimulationManager created and started
  DEBUG: Initial params sync sent
  INFO:  connection closed
  DEBUG: Client disconnected
  ```
- Connection opened, params_sync sent, then instant disconnect

**Debugging Process**:

1. **Added debug logging to backend** (`main.py`)
   - Confirmed server was working correctly
   - Params sync was being sent successfully

2. **Added debug logging to frontend hook** (`useSimulation.ts`)
   - Confirmed WebSocket was being created
   - Saw `onclose` firing immediately after `onopen`

3. **Tested with standalone HTML file** (bypassing React entirely)
   ```html
   <!-- test-websocket.html -->
   <script>
     ws = new WebSocket('ws://localhost:8000/ws');
     ws.onmessage = (e) => console.log(e.data);
   </script>
   ```
   - **Result**: Worked perfectly! Frames streaming at 60 FPS
   - **Conclusion**: Backend is fine, issue is in React frontend

4. **Identified Root Cause**:
   - The `useSimulation` hook had a `useEffect` cleanup function:
     ```typescript
     useEffect(() => {
       return () => {
         disconnect();  // <-- This was the problem
       };
     }, [disconnect]);
     ```
   - **React StrictMode** (in development) mounts, unmounts, and remounts components
   - **Vite's Hot Module Replacement (HMR)** also triggers remounts
   - Combined effect: WebSocket connected, then cleanup ran, disconnecting immediately

**Resolution**: Simplified Architecture

Instead of separate hooks/components with useEffect cleanup, consolidated into a single `App.tsx`:

```typescript
// No useEffect cleanup that disconnects
// WebSocket ref managed directly in component
// Connect/disconnect only on explicit user action
const wsRef = useRef<WebSocket | null>(null);

const connect = () => {
  const ws = new WebSocket(WS_URL);
  ws.onmessage = (e) => { /* handle */ };
  wsRef.current = ws;
};
```

**Files Changed**:
| File | Change |
|------|--------|
| `src/main.tsx` | Removed `<StrictMode>` wrapper |
| `src/App.tsx` | Consolidated all logic, no useEffect cleanup |
| `src/App.css` | Simplified styles |
| Deleted | `src/types/`, `src/constants/`, `src/hooks/`, `src/components/` |

**Lesson Learned**: 
For WebSocket connections in React development:
- Avoid `useEffect` cleanup that disconnects during HMR
- Or use refs and explicit connect/disconnect buttons
- Test with standalone HTML first to isolate React-specific issues

**Status**: ✅ Resolved — WebSocket connection stable

---

### Step 10: Enhanced Visuals

**Prompt**: "Improve the visuals of the demo with more realistic bird shapes, trails, and effects."

**Actions taken**:
- Added motion trails for each boid
- Implemented velocity-based coloring (faster = brighter)
- Added fear-based coloring (boids near predator turn reddish)
- Created teardrop bird shape with wing hints
- Added glow effects for fast-moving boids
- Created hawk-like predator with swept wings and eye
- Added predator danger zone (red radial gradient)
- Implemented sky gradient background
- Added "Show Motion Trails" toggle
- Polished UI with glassmorphism, gradients, and shadows

**Visual Features Added**:
| Feature | Description |
|---------|-------------|
| 🌌 Sky gradient | Deep space-like gradient background |
| ✨ Motion trails | Boids leave fading trails showing path |
| 🎨 Speed coloring | Faster boids glow brighter cyan |
| 😨 Fear coloring | Boids turn red when near predator |
| 🐦 Bird shape | Teardrop body with animated wing hints |
| 💡 Glow effects | Fast boids have subtle bloom |
| 🔴 Danger zone | Red gradient showing predator range |
| 🦅 Hawk predator | Swept wings, body, yellow eye |
| 🎛️ Trails toggle | UI control to enable/disable trails |
| 💅 Polished UI | Glassmorphism, gradient buttons |

**Final Files**:
| File | Lines | Description |
|------|-------|-------------|
| `src/App.tsx` | ~350 | All-in-one component with enhanced rendering |
| `src/App.css` | ~180 | Polished styles with gradients |
| `src/main.tsx` | 6 | Minimal entry point (no StrictMode) |
| `src/index.css` | 15 | Global styles |

**Status**: ✅ Complete

---

## Project Complete! 🎉

All steps completed successfully.

---

## Issues Encountered & Resolutions

| Issue | Cause | Resolution |
|-------|-------|------------|
| TypeScript `erasableSyntaxOnly` error | Vite template used TS 5.8+ options | Removed newer options from tsconfig |
| `ModuleNotFoundError: No module named 'boid'` | Missing relative imports in boids package | Changed `from boid import` to `from .boid import` |
| WebSocket immediately disconnects | React StrictMode + useEffect cleanup | Removed StrictMode, simplified to single component |
| HMR causing reconnects | Vite hot reload triggering cleanup | Explicit connect/disconnect without useEffect |

---

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Web framework | FastAPI | Native WebSocket, async, Pydantic integration |
| Validation | Pydantic v2 | Type safety, automatic validation |
| Testing | pytest + pytest-asyncio | Standard, async support |
| Frontend | React + TypeScript | Component model, type safety |

---

## Files Manifest

### Backend (Complete ✅)

| File | Status | Tests | Description |
|------|--------|-------|-------------|
| `boids/__init__.py` | ✅ | — | Package exports |
| `boids/obstacle.py` | ✅ | 21 | Obstacle class and avoidance |
| `requirements.txt` | ✅ | — | Dependencies |
| `config.py` | ✅ | 35 | Parameter limits, constants |
| `models.py` | ✅ | 36 | Pydantic validation models |
| `simulation_manager.py` | ✅ | 33 | Simulation controller |
| `presets.py` | ✅ | 22 | Preset configurations |
| `main.py` | ✅ | 15 | FastAPI WebSocket app |
| `tests/conftest.py` | ✅ | — | Pytest configuration |
| `tests/test_config.py` | ✅ | 35 | Config tests |
| `tests/test_models.py` | ✅ | 36 | Models tests |
| `tests/test_simulation.py` | ✅ | 33 | Simulation tests |
| `tests/test_presets.py` | ✅ | 22 | Presets tests |
| `tests/test_websocket.py` | ✅ | 34 | WebSocket tests (incl. 3D) |
| `tests/test_obstacle.py` | ✅ | 21 | Obstacle tests |
| `tests/test_flock_obstacles.py` | ✅ | 13 | Flock obstacle integration tests |
| `tests/test_multi_predator.py` | ✅ | 23 | Multiple predator tests |
| `tests/test_predator_strategies.py` | ✅ | 23 | Hunting strategy tests |
| `tests/test_boundary_regression.py` | ✅ | 19 | Boundary regression tests |
| `tests/test_hunting_improvements.py` | ✅ | 34 | Hunting improvement tests |
| `tests/test_3d_scaffold.py` | ✅ | 65 | 3D simulation tests |

### Frontend (Complete ✅ — Simplified Architecture)

| File | Status | Description |
|------|--------|-------------|
| `package.json` | ✅ | Dependencies (incl. Three.js) |
| `tsconfig.json` | ✅ | TypeScript config |
| `tsconfig.app.json` | ✅ | TypeScript app config (fixed) |
| `tsconfig.node.json` | ✅ | TypeScript node config (fixed) |
| `vite.config.ts` | ✅ | Vite configuration |
| `index.html` | ✅ | Entry HTML |
| `src/main.tsx` | ✅ | React entry (no StrictMode) |
| `src/App.tsx` | ✅ | Main app with 2D/3D mode switching |
| `src/App.css` | ✅ | Polished styles |
| `src/index.css` | ✅ | Global styles |
| `src/types/index.ts` | ✅ | TypeScript types (2D + 3D) |
| `src/constants/index.ts` | ✅ | Constants and param definitions |
| `src/hooks/useSimulation.ts` | ✅ | WebSocket hook with mode support |
| `src/components/SimulationCanvas.tsx` | ✅ | 2D canvas renderer |
| `src/components/SimulationCanvas3D.tsx` | ✅ | 3D Three.js renderer |
| `src/components/Controls.tsx` | ✅ | Control panel with mode toggle |
| `src/components/Controls.css` | ✅ | Control panel styles |

### Debugging Artifacts

| File | Purpose |
|------|---------|
| `test-websocket.html` | Standalone WebSocket test (bypasses React) |

---

## Optional Enhancements

These enhancements extend the core simulation with additional features as suggested in the assignment.

### Enhancement Overview

| Enhancement | Description | Status |
|-------------|-------------|--------|
| Static Obstacles | Circular obstacles boids navigate around | ✅ Complete |
| Multiple Predators | Multiple independent predators | ✅ Complete |
| Performance Optimization | Support thousands of boids | ✅ Complete (KDTree) |
| 3D Space | Full 3D simulation | ✅ Complete |

---

### Step 11: Static Obstacles

**Prompt**: "Formulate a clear implementation plan with the testing required and what to look out for. Then we can proceed with implementing each step"

**Implementation Plan Created**:

| Sub-step | Component | Description |
|----------|-----------|-------------|
| 1.1 | `obstacle.py` | Obstacle dataclass with avoidance logic |
| 1.2 | `rules_optimized.py` | Integrate obstacle avoidance rule |
| 1.3 | `simulation_manager.py` | Add/remove obstacle methods |
| 1.4 | WebSocket messages | Add/remove/clear obstacle messages |
| 1.5 | Frontend rendering | Draw obstacles on canvas |
| 1.6 | Click-to-add UI | Interactive obstacle placement |

**Watch-outs Identified**:
- Performance: O(boids × obstacles) — limit obstacle count
- Stuck boids: Need strong enough avoidance force
- Edge cases: Obstacles at boundaries, overlapping obstacles
- Predator interaction: Predators should also avoid obstacles

---

#### Step 11.1: Obstacle Data Structure

**Prompt**: "Yes and remember to document in the GENAI md file as well"

**Actions taken**:
- Created `boids/obstacle.py` with `Obstacle` dataclass
- Implemented `contains_point()`, `distance_to_point()`, `avoidance_vector()` methods
- Created `compute_obstacle_avoidance()` function for total avoidance steering
- Created comprehensive test suite
- Updated `boids/__init__.py` to export new components

**Files created**:
| File | Lines | Description |
|------|-------|-------------|
| `boids/obstacle.py` | 105 | Obstacle class with avoidance logic |
| `tests/test_obstacle.py` | 175 | 21 unit tests |

**Key components**:
| Component | Purpose |
|-----------|---------|
| `Obstacle` | Dataclass with x, y, radius |
| `contains_point()` | Check if point inside obstacle |
| `distance_to_point()` | Distance to obstacle surface |
| `avoidance_vector()` | Steering vector away from obstacle |
| `compute_obstacle_avoidance()` | Total avoidance from all obstacles |

**Avoidance algorithm**:
```
1. For each obstacle:
   - Calculate distance from boid to obstacle surface
   - If inside obstacle: strong push outward
   - If within detection_range: gradual push (stronger when closer)
   - If outside detection_range: no effect
2. Sum all avoidance vectors
3. Multiply by avoidance_strength
```

**Tests**: 21/21 passing
| Test Class | Tests |
|------------|-------|
| TestObstacleCreation | 2 |
| TestContainsPoint | 3 |
| TestDistanceToPoint | 4 |
| TestAvoidanceVector | 5 |
| TestComputeObstacleAvoidance | 5 |
| TestEdgeCases | 2 |

**Status**: ✅ Complete

---

#### Step 11.2: Integrate Obstacle Avoidance into Flock

**Prompt**: Continued from Step 11.1

**Actions taken**:
- Modified `boids/flock_optimized.py` to include obstacle support
- Added `obstacles` list attribute to `FlockOptimized`
- Updated `update()` method to apply obstacle avoidance to all boids
- Updated `update_predator()` to apply obstacle avoidance to predator
- Added obstacle management methods: `add_obstacle()`, `remove_obstacle()`, `clear_obstacles()`, `get_obstacles()`
- Created integration tests in `tests/test_flock_obstacles.py`

**Files modified**:
| File | Changes |
|------|---------|
| `boids/flock_optimized.py` | Added obstacle import, list, avoidance in update loops, management methods |
| `tests/test_flock_obstacles.py` | 13 new integration tests |

**Key changes to FlockOptimized**:
```python
# In __init__:
self.obstacles: List[Obstacle] = []

# In update():
obstacle_dv = compute_obstacle_avoidance(
    boid.x, boid.y,
    self.obstacles,
    detection_range=50.0,
    avoidance_strength=0.5
)

# New methods:
add_obstacle(x, y, radius) -> Obstacle
remove_obstacle(index) -> bool
clear_obstacles() -> int
get_obstacles() -> List[Obstacle]
```

**Tests**: 13/13 passing
| Test Class | Tests |
|------------|-------|
| TestFlockObstacleManagement | 9 |
| TestFlockObstacleAvoidance | 3 |
| TestPredatorObstacleAvoidance | 1 |

**Status**: ✅ Complete

---

#### Step 11.3: Update SimulationManager

**Prompt**: Continued from Step 11.2

**Actions taken**:
- Added obstacle management methods to `SimulationManager`
- Updated `get_frame_data()` to include obstacles
- Updated `FrameData` model to include `obstacles` field
- Added tests for SimulationManager obstacle methods

**Files modified**:
| File | Changes |
|------|---------|
| `simulation_manager.py` | Added `add_obstacle()`, `remove_obstacle()`, `clear_obstacles()`, `get_obstacles()`, `num_obstacles` |
| `models.py` | Added `obstacles` field to `FrameData` |
| `tests/test_simulation.py` | Added 9 obstacle tests |

**New SimulationManager methods**:
```python
add_obstacle(x, y, radius=30.0) -> Dict[str, Any]
remove_obstacle(index) -> bool  
clear_obstacles() -> int
get_obstacles() -> List[Dict[str, Any]]
num_obstacles -> int  # property
```

**Updated FrameData**:
```python
class FrameData(BaseModel):
    # ... existing fields ...
    obstacles: List[List[float]] = Field(
        default_factory=list,
        description="List of [x, y, radius] for each obstacle"
    )
```

**Tests**: 9/9 passing
| Test | Description |
|------|-------------|
| test_add_obstacle | Returns obstacle data with index |
| test_add_multiple_obstacles | Multiple obstacles work |
| test_remove_obstacle | Remove by index works |
| test_remove_invalid_index | Invalid index returns False |
| test_clear_obstacles | Clear all works |
| test_get_obstacles | Returns list of dicts |
| test_frame_data_includes_obstacles | Frame has obstacles |
| test_frame_data_empty_obstacles | Empty list when none |
| test_num_obstacles_property | Property works |

**Status**: ✅ Complete

---

#### Step 11.4: WebSocket Messages for Obstacles

**Prompt**: Continued from Step 11.3

**Actions taken**:
- Added obstacle message types to `config.py`
- Created `handle_obstacle_message()` function in `main.py`
- Added WebSocket tests for obstacle messages

**Files modified**:
| File | Changes |
|------|---------|
| `config.py` | Added `ADD_OBSTACLE`, `REMOVE_OBSTACLE`, `CLEAR_OBSTACLES` and response types |
| `main.py` | Added `handle_obstacle_message()` function |
| `tests/test_websocket.py` | Added 4 obstacle message tests |

**New Message Types**:
```python
# Client -> Server
ADD_OBSTACLE = "add_obstacle"      # {type, x, y, radius}
REMOVE_OBSTACLE = "remove_obstacle" # {type, index}
CLEAR_OBSTACLES = "clear_obstacles" # {type}

# Server -> Client
OBSTACLE_ADDED = "obstacle_added"     # {type, index, x, y, radius}
OBSTACLE_REMOVED = "obstacle_removed" # {type, index, success}
OBSTACLES_CLEARED = "obstacles_cleared" # {type, count}
```

**Tests**: 4/4 passing
| Test | Description |
|------|-------------|
| test_add_obstacle | Add returns obstacle data |
| test_remove_obstacle | Remove by index works |
| test_clear_obstacles | Clear all returns count |
| test_frame_includes_obstacles | Frame has obstacles array |

**Status**: ✅ Complete

---

#### Step 11.5 & 11.6: Frontend Obstacle Support

**Prompt**: Continued from Step 11.4

**Actions taken**:
- Added `obstacles` to FrameData interface
- Created `drawObstacle()` function with gradient styling
- Updated `drawFrame()` to render obstacles behind boids
- Added canvas click handler to add obstacles
- Added obstacle radius slider
- Added clear obstacles button
- Updated stats overlay to show obstacle count

**Files modified**:
| File | Changes |
|------|---------|
| `src/App.tsx` | Full obstacle support: rendering, click-to-add, clear |
| `src/App.css` | Added hint text styling |

**New Features**:
| Feature | Description |
|---------|-------------|
| Click to add | Click anywhere on canvas to add obstacle |
| Radius slider | Control size of new obstacles (15-60px) |
| Clear button | Remove all obstacles |
| Visual styling | Gradient-shaded rock-like obstacles |
| Stats update | Obstacle count shown in overlay |

**Obstacle Rendering**:
```typescript
const drawObstacle = (ctx, obs) => {
  // Outer glow
  // Main body with gradient
  // Border stroke
};
```

**Status**: ✅ Complete

---

### Step 12: Multiple Predators

**Prompt**: "Proceed with the next step and document"

**Implementation Plan**:
| Sub-step | Component | Description |
|----------|-----------|-------------|
| 12.1 | `rules_optimized.py` | Multi-predator avoidance functions |
| 12.2 | `flock_optimized.py` | Predators list, management methods |
| 12.3 | `config.py` | num_predators parameter definition |
| 12.4 | `models.py` | num_predators field, predators array in FrameData |
| 12.5 | `simulation_manager.py` | Support for num_predators |
| 12.6 | Frontend | Multi-predator rendering with unique colors |

---

#### Step 12.1: Multi-Predator Avoidance Rules

**Actions taken**:
- Added `compute_multi_predator_avoidance_kdtree()` function
- Added `compute_all_rules_with_multi_predator_kdtree()` function
- Boids flee from nearest predator within detection range

**Key algorithm**:
```python
def compute_multi_predator_avoidance_kdtree(boid_index, flock_state, predator_positions, ...):
    # Find nearest predator within detection range
    nearest_dist_sq = inf
    for pred_x, pred_y in predator_positions:
        dist_sq = (boid.x - pred_x)² + (boid.y - pred_y)²
        if dist_sq < nearest_dist_sq:
            nearest_dist_sq = dist_sq
    # Apply avoidance from nearest predator
```

---

#### Step 12.2: FlockOptimized Multiple Predators

**Actions taken**:
- Changed `self.predator` to `self.predators: List[Predator]`
- Added backward-compatible `predator` property
- Updated `update()` to use multi-predator avoidance
- Renamed `update_predator()` to `update_predators()`
- Added predator management methods

**New methods**:
```python
add_predator() -> Optional[Predator]  # Max 5
remove_predator(index=-1) -> bool
set_num_predators(count) -> int  # Clamps to 0-5
get_predators() -> List[Predator]
num_predators -> int  # property
```

**Tests**: 23/23 passing (test_multi_predator.py)

---

#### Step 12.3-12.5: Backend Parameter Support

**Files modified**:
| File | Changes |
|------|---------|
| `config.py` | Added `num_predators` to PARAM_DEFINITIONS (1-5, default 1) |
| `models.py` | Added `num_predators` field, `predators` array in FrameData |
| `simulation_manager.py` | Pass `num_predators` to flock, handle in `update_params()` |

**New parameter**:
```python
"num_predators": ParamLimit(
    min=1, max=5, default=1, step=1,
    category="predator",
    label="Number of Predators"
)
```

---

#### Step 12.6: Frontend Multiple Predators

**Actions taken**:
- Added `predators` array support to FrameData interface
- Created `PREDATOR_COLORS` array for visual distinction (5 colors)
- Updated `drawBird()` to check fear from all predators
- Updated `drawPredator()` to accept color index
- Added "Number of Predators" slider (1-5)

**Predator colors**:
| Index | Body | Description |
|-------|------|-------------|
| 0 | #ff6b6b | Red (original) |
| 1 | #ffa726 | Orange |
| 2 | #ab47bc | Purple |
| 3 | #26c6da | Cyan |
| 4 | #66bb6a | Green |

**Status**: ✅ Complete

---

### Step 12.7: Predator Species & Hunting Strategies

**Prompt**: "I think these predators should have different characteristics like a different species otherwise they all move together and it doesn't look good at all. What do you think?"

**Problem**: All predators were using CENTER_HUNTER strategy, causing them to clump together chasing the flock center.

**Solution**: Implemented 5 distinct hunting strategies, each assigned to predators by index.

---

#### Hunting Strategies

| Species | Strategy | Color | Behavior |
|---------|----------|-------|----------|
| **Hawk** | CENTER_HUNTER | Red | Hunts flock center of mass |
| **Falcon** | NEAREST_HUNTER | Orange | Chases nearest boid |
| **Eagle** | STRAGGLER_HUNTER | Purple | Targets isolated boids |
| **Kite** | PATROL_HUNTER | Cyan | Circles area, ambushes nearby boids |
| **Osprey** | RANDOM_HUNTER | Green | Locks onto random boid, switches periodically |

---

#### Implementation Details

**Files modified**:
- `boids/predator.py` - Added `HuntingStrategy` enum and strategy methods
- `boids/flock_optimized.py` - Use `create_with_strategy_index()`
- `models.py` - Include `strategy` and `strategy_name` in predator data
- `simulation_manager.py` - Serialize strategy info to frontend
- `frontend/src/App.tsx` - Species legend, colored danger zones, labels

**New Predator Methods**:
```python
update_velocity_toward_straggler()  # Find most isolated boid
update_velocity_patrol()             # Circle and ambush
update_velocity_random_target()      # Lock and switch
update_velocity_by_strategy()        # Dispatch to correct method
```

**Tests**: 23/23 passing (test_predator_strategies.py)

**Visual Enhancements**:
- Species-colored danger zones
- Name labels above each predator
- Species legend in control panel

**Status**: ✅ Complete

---

### Step 12.8: Boundary Regression Fix

**Problem**: After implementing predator species, boids and predators were escaping the simulation bounds.

**Root Cause Analysis**:
1. **Hunting force scaled with distance**: `steer_toward()` used `distance * hunting_strength`, creating forces up to 20.0 for distant targets
2. **Constant boundary force too weak**: `turn_factor=0.2` was constant, creating a 100x force imbalance
3. **No safety net**: No hard limits on positions

**Diagnostic Tests Created** (19 tests in `test_boundary_regression.py`):
- Boid boundary tests (4 tests)
- Predator boundary tests by strategy (8 tests)
- Force balance analysis (3 tests)
- Long-running stress tests (2 tests)
- Diagnostic tests (2 tests)

**Fixes Implemented**:

1. **Progressive boundary steering** — Force scales with distance past margin:
   ```python
   scale = 1.0 + (distance_into_margin / margin)
   dvx += turn_factor * scale
   ```

2. **Hunting force capping** — `steer_toward()` now limits max force:
   ```python
   if magnitude > max_force:
       scale = max_force / magnitude
       dvx *= scale; dvy *= scale
   ```

3. **Hard position clamping** — Safety net after position updates:
   ```python
   boid.x = max(0, min(width, boid.x))
   ```

**Results**:
- Force ratio: 100x → 2.5x
- Escape counts: 1000+ → 0
- Max escape distance: 320px → 0px

**Status**: ✅ Complete

---

### Step 12.9: Predator Hunting Improvements

**Problem**: Predators would trap boids at screen edges and circle indefinitely — unnatural and boring.

**Four Improvements Implemented**:

| Improvement | Constant | Description |
|-------------|----------|-------------|
| **Target Timeout** | `MAX_TARGET_FRAMES=180` | Force switch after 3 seconds on same target |
| **Catch & Cooldown** | `CATCH_DISTANCE=15`, `COOLDOWN_DURATION=60` | 1 second rest after "catching" prey |
| **Chase Failure** | `CHASE_FAILURE_FRAMES=90` | Give up if no progress for 1.5 seconds |
| **Edge Avoidance** | `EDGE_MARGIN=100` | Prefer targets away from screen edges |

---

#### Implementation Details

**New Predator Attributes**:
```python
cooldown_frames: int = 0              # Post-catch rest timer
last_target_distance: float = inf     # For chase progress tracking
frames_without_progress: int = 0      # Chase failure counter
```

**New Helper Methods**:
```python
is_in_cooldown -> bool                # Check cooldown state
start_cooldown() -> None              # Enter rest state
reset_target() -> None                # Clear target tracking
check_catch(x, y) -> bool             # Within catch distance?
check_chase_failure(dist) -> bool     # No progress?
should_switch_target() -> bool        # Timeout reached?
is_near_edge(x, y, w, h) -> bool      # Near screen edge?
select_target_avoiding_edges(...)     # Smart target selection
```

**Updated Strategies**: NEAREST_HUNTER, STRAGGLER_HUNTER, PATROL_HUNTER, RANDOM_HUNTER now use all improvements.

**Tests**: 34/34 passing (test_hunting_improvements.py)

**Behavioral Changes**:
- Predators now "catch" prey and rest briefly
- Long chases are abandoned
- Edge-trapped boids are deprioritized
- More dynamic, natural hunting patterns

**Status**: ✅ Complete

---

### Step 12.10: Min Speed Slider & Natural Deceleration

**Problem**: Movement felt "jerky" compared to simpler boid implementations. The forced minimum speed prevented natural coasting and deceleration.

**Solution**: 
- Changed `min_speed` default from 2.0 to **0.0**
- Added UI slider for `min_speed` (0.0 - 4.0)
- Updated `enforce_speed_limits()` to skip min enforcement when `min_speed=0`

**Comparison with Simple Demo**:
| Parameter | Simple Demo | Our Default (New) |
|-----------|-------------|-------------------|
| Min Speed | None (0) | **0** (was 2.0) |
| Max Speed | 15 | 3.0 |

**Code Changes**:
```python
# enforce_speed_limits now allows natural deceleration
if speed == 0:
    if self.params.min_speed > 0:
        # Give random direction at minimum speed
        ...
    # If min_speed=0, allow boid to stay still
    return

elif speed < self.params.min_speed and self.params.min_speed > 0:
    # Only enforce if min_speed > 0
    ...
```

**Result**: Smoother, more natural flocking movement. Boids can coast, glide through turns, and accelerate organically.

**Status**: ✅ Complete

---

### Step 14: 3D Implementation (In Progress)

**Goal**: Transform 2D boids simulation into full 3D experience with Three.js.

#### Phase 1: Backend 3D Core ✅ COMPLETE

**New Files Created**:
| File | Description | Tests |
|------|-------------|-------|
| `boids/boid3d.py` | 3D boid class with x,y,z position and velocity | 12 |
| `boids/predator3d.py` | 3D predator with all hunting strategies | 13 |
| `boids/obstacle3d.py` | Spherical obstacles in 3D space | 8 |
| `tests/test_3d_scaffold.py` | Comprehensive 3D test suite | 65 pass |

**Key Features Implemented**:
- `Boid3D`: Full 3D position/velocity, uniform spherical random direction
- `Predator3D`: All 5 hunting strategies ready for 3D, cooldown/catch mechanics
- `Obstacle3D`: Spherical obstacles with collision detection
- `distance_3d()`: 3D Euclidean distance function
- `create_obstacle_field_3d()`: Non-overlapping obstacle placement

#### Phase 2: 3D Physics Rules ✅ COMPLETE

**New File**: `boids/rules3d.py`

**Implemented Functions**:
- `compute_separation_3d()`: Flee from nearby boids in 3D
- `compute_alignment_3d()`: Match velocity with neighbors in 3D
- `compute_cohesion_3d()`: Move toward flock center in 3D
- `apply_boundary_steering_3d()`: Stay within 6-face bounding box
- `compute_predator_avoidance_3d()`: Flee from predators in 3D
- `compute_obstacle_avoidance_3d()`: Avoid spherical obstacles

#### Phase 3: Flock3D Manager ✅ COMPLETE

**New Files**:
| File | Description |
|------|-------------|
| `boids/flock3d.py` | Full 3D flock simulation manager |

**Key Features**:
- `Flock3D`: Complete 3D simulation with KDTree spatial queries
- `SimulationParams3D`: 3D-specific parameters including depth
- All 5 hunting strategies working in 3D (Hawk, Falcon, Eagle, Kite, Osprey)
- Full boundary enforcement on all 6 faces
- Obstacle avoidance for spherical obstacles
- Integration with all hunting improvements (timeout, catch, cooldown, edge avoidance)

**Tests**: 65/65 3D tests passing

#### Remaining Phases

| Phase | Task | Status |
|-------|------|--------|
| 4 | API & WebSocket Updates | ✅ COMPLETE |
| 5 | Frontend Three.js Setup | ✅ COMPLETE |
| 6 | Frontend Boid Rendering | ✅ COMPLETE (merged with Phase 5) |
| 7 | Frontend Polish | ⏳ Pending |
| 8 | Testing & Documentation | ⏳ Pending |

#### Phase 4: API & WebSocket Updates ✅ COMPLETE

**Updated Files**:
- `config.py`: Added `SIMULATION_DEPTH`, `SimulationMode`, `VALID_MODES`, `simulation_mode` and `depth` parameters
- `models.py`: Added `simulation_mode`, `depth` to `SimulationParams`, updated `FrameData` for 3D format
- `simulation_manager.py`: Full 3D support with mode switching, 3D frame serialization
- `main.py`: Added `set_mode` message handler

**New Features**:
- `set_mode` WebSocket message to switch between 2D and 3D
- `mode_changed` response message
- 3D frame format: `[x, y, z, vx, vy, vz]` for boids
- 3D predator format with z coordinates
- 3D obstacle format: `[x, y, z, radius]`
- `bounds` field in 3D frames with `{width, height, depth}`
- Backward-compatible 2D format preserved

**New Tests**: 5 tests for 3D API
- `test_set_mode_to_3d`
- `test_3d_frame_format`
- `test_switch_back_to_2d`
- `test_params_include_mode`
- `test_params_include_depth`

#### Phase 5 & 6: Frontend Three.js + Boid Rendering ✅ COMPLETE

**New Files**:
- `SimulationCanvas3D.tsx`: Full 3D rendering with Three.js
  - InstancedMesh for efficient boid rendering (up to 200 boids)
  - OrbitControls for camera manipulation
  - Predator meshes with strategy-specific colors
  - Spherical obstacle rendering
  - Wireframe boundary box
  - Real-time metrics overlay

**Updated Files**:
- `types/index.ts`: Added 3D types (`BoidData3D`, `SimulationMode`, `PredatorInfo`, etc.)
- `constants/index.ts`: Added 3D constants, predator colors
- `useSimulation.ts`: Added `setMode` action and `mode` state
- `SimulationCanvas.tsx`: Updated for new types, obstacle rendering, predator colors
- `Controls.tsx`: Added 2D/3D mode toggle with styling
- `Controls.css`: Added mode toggle button styles
- `App.tsx`: Conditional rendering of 2D or 3D canvas

**Dependencies Added**:
- `three` - Three.js for 3D rendering
- `@types/three` - TypeScript definitions

**Documentation**: See `docs/3D_IMPLEMENTATION_PLAN.md` for full details.

**Status**: ✅ 3D Frontend Functional, Polish Pending

---

## Quick Start

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
# Server runs at http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### Usage
1. Open http://localhost:5173
2. Click **Connect**
3. Watch boids flock in real-time
4. Try different **Presets** (Predator Chase is fun!)
5. Toggle **Enable Predator**
6. Adjust sliders to modify behavior
7. Toggle **Show Motion Trails**

---

### Step 15: Docker Containerization

**Date**: January 2026

**Prompt**: "Containerize the project with Docker for easy deployment"

**Actions taken**:
- Created `backend/Dockerfile` (Python 3.12-slim base)
- Created `frontend/Dockerfile` (multi-stage: Node build → Nginx serve)
- Created `frontend/nginx.conf` (WebSocket proxy configuration)
- Created `docker-compose.yml` (orchestrates both services)
- Created `.dockerignore` files for optimized builds
- Updated frontend WebSocket URL to support both dev and Docker modes

**Files created**:
| File | Description |
|------|-------------|
| `docker-compose.yml` | Orchestrates backend and frontend containers |
| `backend/Dockerfile` | Python FastAPI container |
| `backend/.dockerignore` | Excludes tests, cache, etc. |
| `frontend/Dockerfile` | Multi-stage build (Node → Nginx) |
| `frontend/nginx.conf` | Nginx config with WebSocket proxy |
| `frontend/.dockerignore` | Excludes node_modules, dist |
| `README.md` | Comprehensive project documentation |

**Architecture**:
```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────────────┐ │
│  │    Frontend      │      │       Backend            │ │
│  │    (Nginx)       │      │      (FastAPI)           │ │
│  │                  │      │                          │ │
│  │  Port 8080 ──────│─────►│  Port 8000               │ │
│  │  Static files    │  /ws │  WebSocket server        │ │
│  │  WS proxy        │      │  Simulation engine       │ │
│  └──────────────────┘      └──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Docker Usage**:
```bash
# Build and run
docker compose up --build

# Run in background
docker compose up -d --build

# Stop
docker compose down

# View logs
docker compose logs -f
```

**Performance**:
- Local development: ~60 FPS
- Docker deployment: ~48 FPS (slight container overhead)

**Status**: ✅ Complete

---

## Quick Reference

### Docker Deployment (Recommended)
```bash
docker compose up --build
# Open http://localhost:8080
```

### Local Development
```bash
# Terminal 1: Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && python main.py

# Terminal 2: Frontend
cd frontend && npm install && npm run dev
# Open http://localhost:5173
```

### Run Tests
```bash
cd backend
pytest tests/ -v
```

---

*Document Version: 11.0*
*Last Updated: January 2026*
*Status: Production Ready with Docker Containerization*
*Total Tests: 357 passing*