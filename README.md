# Boids Interactive Demo

An interactive web-based demonstration of the Boids flocking simulation with real-time parameter manipulation.

## Overview

This project provides a browser-based interface to explore Reynolds' Boids algorithm, allowing users to:

- **Observe** emergent flocking behavior from simple rules
- **Manipulate** parameters in real-time and see immediate effects
- **Experiment** with predator-prey dynamics
- **Learn** how separation, alignment, and cohesion create complex patterns

## Architecture

```
┌──────────────────┐         WebSocket          ┌──────────────────┐
│  React Frontend  │ ◄──────────────────────────► │  FastAPI Backend │
│                  │     JSON @ 60fps            │                  │
│  - Canvas render │                             │  - Simulation    │
│  - Parameter UI  │                             │  - KDTree optim  │
│  - Presets       │                             │  - Metrics       │
└──────────────────┘                             └──────────────────┘
```

## Features

### Core Simulation
- Separation, alignment, and cohesion rules
- KDTree-optimized neighbor finding (handles 200+ boids at 60fps)
- Soft boundary handling

### Predator System
- Toggle predator on/off
- Predator tracks flock center
- Boids flee from predator
- Configurable speed and avoidance strength

### Interactive Controls

**Primary Parameters:**
- Number of boids (1-200)
- Visual range (how far boids see)
- Separation strength

**Predator Parameters:**
- Enable/disable toggle
- Predator speed
- Avoidance strength

**Advanced Parameters:**
- Protected range, cohesion, alignment
- Speed limits, boundary margin
- Detection range, hunting strength

### Presets
| Preset | Description |
|--------|-------------|
| Default | Balanced flocking |
| Tight Swarm | Dense ball formation |
| Loose Cloud | Spread out, drifting |
| High Speed | Fast, chaotic |
| Slow Dance | Graceful, synchronized |
| Predator Chase | Dramatic chase scene |
| Swarm Defense | Tight flock under threat |

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Using Docker
```bash
docker-compose up
```

Then open http://localhost:3000

## Project Structure

```
boids-interactive/
├── SPECIFICATION.md      # Detailed technical spec
├── IMPLEMENTATION_PLAN.md # Step-by-step build guide
├── README.md             # This file
│
├── backend/
│   ├── main.py           # FastAPI WebSocket server
│   ├── simulation_manager.py
│   ├── models.py         # Pydantic validation
│   ├── presets.py
│   └── boids/            # Simulation engine
│
└── frontend/
    ├── src/
    │   ├── components/   # React components
    │   ├── hooks/        # Custom hooks
    │   └── types/        # TypeScript types
    └── public/
```

## API

### WebSocket Endpoint
`ws://localhost:8000/ws/simulation`

### Client → Server Messages

**Update Parameters:**
```json
{"type": "update_params", "params": {"num_boids": 75}}
```

**Reset Simulation:**
```json
{"type": "reset"}
```

**Apply Preset:**
```json
{"type": "preset", "name": "tight_swarm"}
```

**Pause/Resume:**
```json
{"type": "pause"}
{"type": "resume"}
```

### Server → Client Messages

**Frame (60fps):**
```json
{
  "type": "frame",
  "frame_id": 12345,
  "boids": [[x, y, vx, vy], ...],
  "predator": [x, y, vx, vy],
  "metrics": {"fps": 60, "avg_distance": 234.5}
}
```

## Development Status

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ⏳ Next | Backend Core |
| Phase 2 | ⏸️ | Backend Polish |
| Phase 3 | ⏸️ | Frontend Core |
| Phase 4 | ⏸️ | Frontend Polish |
| Phase 5 | ⏸️ | Integration |

## Related

This project builds on the core Boids simulation implemented in `/boids/`:
- 144 unit tests
- KDTree optimization (12x speedup)
- Predator avoidance
- Quantitative analysis tools

## License

MIT

## Credits

- Original Boids algorithm: Craig Reynolds (1986)
- Implementation: Built with Claude AI assistance