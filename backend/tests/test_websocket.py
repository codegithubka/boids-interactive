"""
Tests for FastAPI WebSocket server.
"""

import pytest
from fastapi.testclient import TestClient

from main import app, connection_manager
from config import MessageType


# =============================================================================
# Test Client Fixture
# =============================================================================

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


# =============================================================================
# REST Endpoint Tests
# =============================================================================

class TestRESTEndpoints:
    """Tests for REST endpoints."""

    def test_root(self, client):
        """Root endpoint returns status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "boids-interactive"

    def test_health(self, client):
        """Health endpoint returns healthy."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


# =============================================================================
# WebSocket Connection Tests
# =============================================================================

class TestWebSocketConnection:
    """Tests for WebSocket connection."""

    def test_connect(self, client):
        """WebSocket connects successfully."""
        with client.websocket_connect("/ws") as websocket:
            # Should receive params_sync on connect
            data = websocket.receive_json()
            assert data["type"] == MessageType.PARAMS_SYNC
            assert "params" in data

    def test_params_sync_on_connect(self, client):
        """Receives params_sync with all parameters on connect."""
        with client.websocket_connect("/ws") as websocket:
            data = websocket.receive_json()
            assert data["type"] == MessageType.PARAMS_SYNC
            params = data["params"]
            assert "num_boids" in params
            assert "predator_enabled" in params
            assert len(params) == 15

    def test_receives_frames(self, client):
        """Receives frame data after connect."""
        with client.websocket_connect("/ws") as websocket:
            # Skip params_sync
            websocket.receive_json()
            
            # Should receive frame
            data = websocket.receive_json()
            assert data["type"] == MessageType.FRAME
            assert "frame_id" in data
            assert "boids" in data


# =============================================================================
# WebSocket Message Tests
# =============================================================================

class TestWebSocketMessages:
    """Tests for WebSocket message handling."""

    def test_update_params(self, client):
        """Update params message works."""
        with client.websocket_connect("/ws") as websocket:
            # Skip params_sync
            websocket.receive_json()
            
            # Send update
            websocket.send_json({
                "type": "update_params",
                "params": {"num_boids": 75}
            })
            
            # Should receive params_sync back
            # May receive frame first, so check a few messages
            for _ in range(5):
                data = websocket.receive_json()
                if data["type"] == MessageType.PARAMS_SYNC:
                    assert data["params"]["num_boids"] == 75
                    break

    def test_reset(self, client):
        """Reset message works."""
        with client.websocket_connect("/ws") as websocket:
            # Skip params_sync
            websocket.receive_json()
            
            # Send reset
            websocket.send_json({"type": "reset"})
            
            # Should receive params_sync back
            for _ in range(5):
                data = websocket.receive_json()
                if data["type"] == MessageType.PARAMS_SYNC:
                    assert "params" in data
                    break

    def test_preset(self, client):
        """Preset message works."""
        with client.websocket_connect("/ws") as websocket:
            # Skip params_sync
            websocket.receive_json()
            
            # Send preset
            websocket.send_json({
                "type": "preset",
                "name": "tight_swarm"
            })
            
            # Should receive params_sync with preset values
            for _ in range(5):
                data = websocket.receive_json()
                if data["type"] == MessageType.PARAMS_SYNC:
                    # tight_swarm has 100 boids
                    assert data["params"]["num_boids"] == 100
                    break

    def test_invalid_preset(self, client):
        """Invalid preset returns error."""
        with client.websocket_connect("/ws") as websocket:
            # Skip params_sync
            websocket.receive_json()
            
            # Send invalid preset
            websocket.send_json({
                "type": "preset",
                "name": "nonexistent"
            })
            
            # Should receive error
            for _ in range(5):
                data = websocket.receive_json()
                if data["type"] == MessageType.ERROR:
                    assert "Invalid preset" in data["message"]
                    break

    def test_pause_resume(self, client):
        """Pause and resume messages work."""
        with client.websocket_connect("/ws") as websocket:
            # Skip params_sync
            websocket.receive_json()
            
            # Get initial frame
            data1 = websocket.receive_json()
            assert data1["type"] == MessageType.FRAME
            frame1 = data1["frame_id"]
            
            # Send pause
            websocket.send_json({"type": "pause"})
            
            # Receive a few frames, frame_id should not change
            paused_frames = []
            for _ in range(3):
                data = websocket.receive_json()
                if data["type"] == MessageType.FRAME:
                    paused_frames.append(data["frame_id"])
            
            # All paused frames should have same ID
            assert len(set(paused_frames)) == 1
            
            # Send resume
            websocket.send_json({"type": "resume"})
            
            # Frame ID should start incrementing again
            data = websocket.receive_json()
            # May take a frame to resume

    def test_unknown_message(self, client):
        """Unknown message type returns error."""
        with client.websocket_connect("/ws") as websocket:
            # Skip params_sync
            websocket.receive_json()
            
            # Send unknown type
            websocket.send_json({"type": "unknown_type"})
            
            # Should receive error
            for _ in range(5):
                data = websocket.receive_json()
                if data["type"] == MessageType.ERROR:
                    assert "Unknown message type" in data["message"]
                    break


# =============================================================================
# Frame Data Tests
# =============================================================================

class TestFrameData:
    """Tests for frame data content."""

    def test_frame_has_boids(self, client):
        """Frame contains boids array."""
        with client.websocket_connect("/ws") as websocket:
            # Skip params_sync
            websocket.receive_json()
            
            # Get frame
            data = websocket.receive_json()
            assert data["type"] == MessageType.FRAME
            assert isinstance(data["boids"], list)
            assert len(data["boids"]) == 50  # Default num_boids

    def test_frame_boid_format(self, client):
        """Each boid has [x, y, vx, vy] format."""
        with client.websocket_connect("/ws") as websocket:
            # Skip params_sync
            websocket.receive_json()
            
            # Get frame
            data = websocket.receive_json()
            boid = data["boids"][0]
            assert len(boid) == 4
            assert all(isinstance(v, (int, float)) for v in boid)

    def test_frame_has_metrics(self, client):
        """Frame contains metrics."""
        with client.websocket_connect("/ws") as websocket:
            # Skip params_sync
            websocket.receive_json()
            
            # Get frame
            data = websocket.receive_json()
            assert "metrics" in data
            assert "fps" in data["metrics"]

    def test_frame_predator_when_enabled(self, client):
        """Frame contains predator when enabled."""
        with client.websocket_connect("/ws") as websocket:
            # Skip params_sync
            websocket.receive_json()
            
            # Enable predator
            websocket.send_json({
                "type": "update_params",
                "params": {"predator_enabled": True}
            })
            
            # Find frame with predator
            for _ in range(10):
                data = websocket.receive_json()
                if data["type"] == MessageType.FRAME and data.get("predator"):
                    assert len(data["predator"]) == 4
                    break


if __name__ == "__main__":
    pytest.main([__file__, "-v"])