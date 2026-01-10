"""
FastAPI WebSocket server for the Boids Interactive Demo.

Provides real-time simulation streaming and parameter control.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from config import TARGET_FPS, MessageType
from models import (
    parse_client_message,
    UpdateParamsMessage,
    ResetMessage,
    PauseMessage,
    ResumeMessage,
    ParamsSyncMessage,
    ErrorMessage,
)
from simulation_manager import SimulationManager
from presets import get_preset_params, is_valid_preset


# =============================================================================
# Application Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    print("Boids Interactive Demo starting...")
    yield
    print("Boids Interactive Demo shutting down...")


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="Boids Interactive Demo",
    description="Real-time boids simulation with WebSocket streaming",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# REST Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "boids-interactive"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# =============================================================================
# WebSocket Connection Manager
# =============================================================================

class ConnectionManager:
    """Manages WebSocket connections and their simulations."""

    def __init__(self):
        self.active_connections: Dict[WebSocket, SimulationManager] = {}

    async def connect(self, websocket: WebSocket) -> SimulationManager:
        """Accept connection and create simulation."""
        await websocket.accept()
        manager = SimulationManager()
        manager.start()
        self.active_connections[websocket] = manager
        return manager

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove connection and stop simulation."""
        if websocket in self.active_connections:
            manager = self.active_connections[websocket]
            manager.stop()
            del self.active_connections[websocket]

    def get_manager(self, websocket: WebSocket) -> SimulationManager:
        """Get simulation manager for connection."""
        return self.active_connections.get(websocket)


connection_manager = ConnectionManager()


# =============================================================================
# Message Handlers
# =============================================================================

async def handle_message(
    websocket: WebSocket,
    manager: SimulationManager,
    data: dict
) -> None:
    """Handle incoming WebSocket message."""
    msg_type = data.get("type")
    
    # Handle preset separately to give better error messages
    if msg_type == MessageType.PRESET:
        preset_name = data.get("name", "")
        if is_valid_preset(preset_name):
            preset_params = get_preset_params(preset_name)
            manager.update_params(preset_params)
            sync = ParamsSyncMessage(params=manager.get_params_dict())
            await websocket.send_json(sync.model_dump())
        else:
            error = ErrorMessage(message=f"Invalid preset: {preset_name}")
            await websocket.send_json(error.model_dump())
        return
    
    message = parse_client_message(data)

    if message is None:
        # Unknown or invalid message
        error = ErrorMessage(message=f"Unknown message type: {msg_type}")
        await websocket.send_json(error.model_dump())
        return

    if isinstance(message, UpdateParamsMessage):
        manager.update_params(message.params)
        # Send params sync back
        sync = ParamsSyncMessage(params=manager.get_params_dict())
        await websocket.send_json(sync.model_dump())

    elif isinstance(message, ResetMessage):
        manager.reset()
        # Send params sync back
        sync = ParamsSyncMessage(params=manager.get_params_dict())
        await websocket.send_json(sync.model_dump())

    elif isinstance(message, PauseMessage):
        manager.pause()

    elif isinstance(message, ResumeMessage):
        manager.resume()


# =============================================================================
# WebSocket Endpoint
# =============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for simulation streaming.
    
    Protocol:
    - On connect: sends params_sync with current parameters
    - Continuously: sends frame data at TARGET_FPS
    - Receives: update_params, reset, preset, pause, resume messages
    """
    manager = await connection_manager.connect(websocket)
    frame_interval = 1.0 / TARGET_FPS

    try:
        # Send initial params sync
        sync = ParamsSyncMessage(params=manager.get_params_dict())
        await websocket.send_json(sync.model_dump())

        # Start frame loop
        while True:
            frame_start = asyncio.get_event_loop().time()

            # Check for incoming messages (non-blocking)
            try:
                # Wait for message with short timeout
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=0.001  # 1ms timeout
                )
                await handle_message(websocket, manager, data)
            except asyncio.TimeoutError:
                # No message, continue with frame
                pass

            # Update simulation
            manager.update()

            # Send frame data
            frame_data = manager.get_frame_data()
            await websocket.send_json(frame_data.model_dump())

            # Maintain frame rate
            frame_end = asyncio.get_event_loop().time()
            elapsed = frame_end - frame_start
            sleep_time = frame_interval - elapsed
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        connection_manager.disconnect(websocket)


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)