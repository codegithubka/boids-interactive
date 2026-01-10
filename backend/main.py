"""
FastAPI WebSocket server for the Boids Interactive Demo.

Provides real-time simulation streaming and parameter control.
"""

import asyncio
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
    allow_origins=["*"],
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
    
    # Handle obstacle messages first
    if await handle_obstacle_message(websocket, manager, data):
        return
    
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
        error = ErrorMessage(message=f"Unknown message type: {msg_type}")
        await websocket.send_json(error.model_dump())
        return

    if isinstance(message, UpdateParamsMessage):
        manager.update_params(message.params)
        sync = ParamsSyncMessage(params=manager.get_params_dict())
        await websocket.send_json(sync.model_dump())

    elif isinstance(message, ResetMessage):
        manager.reset()
        sync = ParamsSyncMessage(params=manager.get_params_dict())
        await websocket.send_json(sync.model_dump())

    elif isinstance(message, PauseMessage):
        manager.pause()

    elif isinstance(message, ResumeMessage):
        manager.resume()


async def handle_obstacle_message(
    websocket: WebSocket,
    manager: SimulationManager,
    data: dict
) -> bool:
    """
    Handle obstacle-related messages.
    
    Returns True if message was handled, False otherwise.
    """
    msg_type = data.get("type")
    
    if msg_type == MessageType.ADD_OBSTACLE:
        x = data.get("x", 400)
        y = data.get("y", 300)
        radius = data.get("radius", 30)
        result = manager.add_obstacle(x, y, radius)
        await websocket.send_json({
            "type": MessageType.OBSTACLE_ADDED,
            **result
        })
        return True
    
    elif msg_type == MessageType.REMOVE_OBSTACLE:
        index = data.get("index", -1)
        success = manager.remove_obstacle(index)
        await websocket.send_json({
            "type": MessageType.OBSTACLE_REMOVED,
            "index": index,
            "success": success
        })
        return True
    
    elif msg_type == MessageType.CLEAR_OBSTACLES:
        count = manager.clear_obstacles()
        await websocket.send_json({
            "type": MessageType.OBSTACLES_CLEARED,
            "count": count
        })
        return True
    
    return False


# =============================================================================
# WebSocket Endpoint
# =============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for simulation streaming.
    """
    manager = await connection_manager.connect(websocket)
    frame_interval = 1.0 / TARGET_FPS
    running = True

    async def send_frames():
        """Continuously send frame data."""
        nonlocal running
        try:
            while running:
                frame_start = asyncio.get_event_loop().time()
                manager.update()
                frame_data = manager.get_frame_data()
                await websocket.send_json(frame_data.model_dump())
                
                frame_end = asyncio.get_event_loop().time()
                elapsed = frame_end - frame_start
                sleep_time = frame_interval - elapsed
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
        except Exception as e:
            print(f"Send frames error: {e}")
            running = False

    async def receive_messages():
        """Receive and handle client messages."""
        nonlocal running
        try:
            while running:
                data = await websocket.receive_json()
                await handle_message(websocket, manager, data)
        except WebSocketDisconnect:
            running = False
        except Exception as e:
            print(f"Receive messages error: {e}")
            running = False

    try:
        # Send initial params sync
        sync = ParamsSyncMessage(params=manager.get_params_dict())
        await websocket.send_json(sync.model_dump())

        # Run send and receive concurrently
        send_task = asyncio.create_task(send_frames())
        receive_task = asyncio.create_task(receive_messages())
        
        done, pending = await asyncio.wait(
            [send_task, receive_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        running = False
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

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