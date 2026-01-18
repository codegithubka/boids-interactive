# Boids Interactive - Containerization Plan

## Overview

This document outlines the plan to containerize the Boids Interactive Demo using Docker, making it easy to deploy and run on any system.

## Status: ✅ COMPLETE

Docker containerization is fully implemented and working.

## Approach: Docker Compose

We use Docker Compose to orchestrate two containers:
1. **Backend** - Python/FastAPI WebSocket server
2. **Frontend** - Static React build served by Nginx

### Why Docker Compose?
- ✅ Works on Mac, Linux, Windows
- ✅ Single command to start everything
- ✅ Easy to distribute
- ✅ Consistent environment
- ✅ No Python/Node installation required for end users

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────────────┐ │
│  │    Frontend      │      │       Backend            │ │
│  │    (Nginx)       │      │      (FastAPI)           │ │
│  │                  │      │                          │ │
│  │  Port 8080       │ ───► │  Port 8000               │ │
│  │  Serves static   │  WS  │  WebSocket /ws           │ │
│  │  React build     │      │  Simulation engine       │ │
│  └──────────────────┘      └──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**User accesses:** `http://localhost:8080`

---

## Implementation Phases

### Phase 1: Backend Container ✅ COMPLETE
- [x] Create `backend/Dockerfile`
- [x] Test backend container standalone
- [x] Verify WebSocket functionality

### Phase 2: Frontend Container ✅ COMPLETE
- [x] Create `frontend/Dockerfile`
- [x] Configure Nginx for SPA routing
- [x] Configure WebSocket proxy to backend

### Phase 3: Docker Compose ✅ COMPLETE
- [x] Create `docker-compose.yml`
- [x] Configure networking between containers
- [x] Add health checks

### Phase 4: Documentation & Polish ✅ COMPLETE
- [x] Update README with Docker instructions
- [x] Add `.dockerignore` files
- [x] Test full stack
- [x] Document in GENAI_USAGE.md

---

## Files to Create

| File | Purpose |
|------|---------|
| `backend/Dockerfile` | Backend container definition |
| `frontend/Dockerfile` | Frontend container definition |
| `frontend/nginx.conf` | Nginx configuration with WS proxy |
| `docker-compose.yml` | Orchestrates both containers |
| `.dockerignore` | Excludes unnecessary files |
| `backend/.dockerignore` | Backend-specific exclusions |
| `frontend/.dockerignore` | Frontend-specific exclusions |

---

## Usage (End Result)

```bash
# Build and start everything
docker-compose up --build

# Or run in background
docker-compose up -d --build

# Stop
docker-compose down
```

Then open: **http://localhost:8080**

---

## Container Details

### Backend Container
- **Base image:** `python:3.12-slim`
- **Port:** 8000 (internal)
- **Command:** `uvicorn main:app --host 0.0.0.0 --port 8000`

### Frontend Container
- **Build stage:** `node:20-alpine` (builds React app)
- **Runtime stage:** `nginx:alpine` (serves static files)
- **Port:** 8080 (exposed to host)
- **WebSocket proxy:** Routes `/ws` to backend:8000

---

## Estimated Time

| Phase | Time |
|-------|------|
| Backend Dockerfile | 10 min |
| Frontend Dockerfile + Nginx | 15 min |
| Docker Compose | 10 min |
| Testing & Polish | 15 min |
| **Total** | **~50 min** |

---

## Notes

- Frontend connects to WebSocket via relative URL (`/ws`), Nginx proxies to backend
- No Three.js in containerized version (2D only)
- Tests are not included in production containers
- Health checks ensure containers are ready before accepting traffic