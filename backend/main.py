"""
FastAPI application for the Boids Interactive Demo.

Provides WebSocket endpoint for real-time simulation streaming
and parameter control.
"""

import asyncio
import time
import json
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.config import TARGET_FPS, MessageType
from models import (
    SimulationParams,
    parse_client_message,
    apply_param_updates,
    FrameMessage,
    ParamsSyncMessage,
    ErrorMessage,
    UpdateParamsMessage,
    ResetMessage,
    PresetMessage,
    PauseMessage,
    ResumeMessage,
)
from simulation_manager import SimulationManager
from presets import get_preset, is_valid_preset


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="Boids Interactive Demo",
    description="Real-time Boids flocking simulation with WebSocket streaming",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to frontend origin
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
# WebSocket Handler
# =============================================================================

async def handle_client_message(
    manager: SimulationManager,
    websocket: WebSocket,
    data: dict
) -> None:
    """
    Handle an incoming message from the client.
    
    Args:
        manager: The simulation manager for this client
        websocket: The WebSocket connection
        data: Parsed JSON message data
    """
    message = parse_client_message(data)
    
    if message is None:
        error = ErrorMessage(message=f"Unknown message type: {data.get('type')}")
        await websocket.send_json(error.model_dump())
        return
    
    if isinstance(message, UpdateParamsMessage):
        # Apply parameter updates
        new_params, errors = apply_param_updates(manager.params, message.params)
        
        if errors:
            for err in errors:
                error = ErrorMessage(message=err)
                await websocket.send_json(error.model_dump())
        
        manager.update_params(new_params)
        
    elif isinstance(message, ResetMessage):
        # Reset simulation
        manager.reset()
        
    elif isinstance(message, PresetMessage):
        # Apply preset
        if not is_valid_preset(message.name):
            error = ErrorMessage(message=f"Unknown preset: {message.name}")
            await websocket.send_json(error.model_dump())
            return
        
        preset_params = get_preset(message.name)
        if preset_params:
            manager.update_params(preset_params)
            
            # Send params sync after preset
            sync = ParamsSyncMessage(params=manager.get_params_dict())
            await websocket.send_json(sync.model_dump())
        
    elif isinstance(message, PauseMessage):
        manager.pause()
        
    elif isinstance(message, ResumeMessage):
        manager.resume()


async def simulation_loop(
    manager: SimulationManager,
    websocket: WebSocket
) -> None:
    """
    Main simulation loop - sends frames at TARGET_FPS.
    
    Args:
        manager: The simulation manager
        websocket: The WebSocket connection
    """
    target_frame_time = 1.0 / TARGET_FPS
    
    while manager.running:
        frame_start = time.perf_counter()
        
        # Update simulation
        manager.update()
        
        # Send frame data
        frame = manager.get_frame_data()
        await websocket.send_json(frame.model_dump())
        
        # Rate limiting
        elapsed = time.perf_counter() - frame_start
        sleep_time = target_frame_time - elapsed
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)


@app.websocket("/ws/simulation")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for simulation streaming.
    
    Protocol:
    - On connect: Creates new SimulationManager, sends params_sync, starts streaming
    - During connection: Handles update_params, reset, preset, pause, resume messages
    - On disconnect: Cleans up simulation
    """
    await websocket.accept()
    
    # Create simulation manager for this client
    manager = SimulationManager()
    manager.start()
    
    # Send initial params sync
    sync = ParamsSyncMessage(params=manager.get_params_dict())
    await websocket.send_json(sync.model_dump())
    
    # Create simulation loop task
    loop_task = asyncio.create_task(simulation_loop(manager, websocket))
    
    try:
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                await handle_client_message(manager, websocket, data)
            except json.JSONDecodeError:
                error = ErrorMessage(message="Invalid JSON")
                await websocket.send_json(error.model_dump())
                
    except WebSocketDisconnect:
        pass
    finally:
        # Clean up
        manager.stop()
        loop_task.cancel()
        try:
            await loop_task
        except asyncio.CancelledError:
            pass


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)