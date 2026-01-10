/**
 * Custom hook for managing the boids simulation WebSocket connection.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import type {
  ConnectionState,
  FrameData,
  SimulationParams,
  PresetName,
  ServerMessage,
  UseSimulationReturn,
} from '../types';
import { WS_URL } from '../constants';

export function useSimulation(): UseSimulationReturn {
  // Connection state
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);

  // Simulation state
  const [frameData, setFrameData] = useState<FrameData | null>(null);
  const [params, setParams] = useState<SimulationParams | null>(null);
  const [isPaused, setIsPaused] = useState(false);

  // Handle incoming messages
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: ServerMessage = JSON.parse(event.data);

      switch (message.type) {
        case 'frame':
          setFrameData(message);
          break;
        case 'params_sync':
          setParams(message.params);
          break;
        case 'error':
          console.error('Server error:', message.message);
          break;
      }
    } catch (error) {
      console.error('Failed to parse message:', error);
    }
  }, []);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionState('connecting');

    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setConnectionState('connected');
      console.log('WebSocket connected');
    };

    ws.onclose = () => {
      setConnectionState('disconnected');
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      setConnectionState('error');
      console.error('WebSocket error:', error);
    };

    ws.onmessage = handleMessage;

    wsRef.current = ws;
  }, [handleMessage]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  // Send message helper
  const sendMessage = useCallback((message: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  // Update parameters
  const updateParams = useCallback(
    (updates: Partial<SimulationParams>) => {
      sendMessage({
        type: 'update_params',
        params: updates,
      });
    },
    [sendMessage]
  );

  // Reset simulation
  const reset = useCallback(() => {
    sendMessage({ type: 'reset' });
  }, [sendMessage]);

  // Apply preset
  const applyPreset = useCallback(
    (name: PresetName) => {
      sendMessage({
        type: 'preset',
        name,
      });
    },
    [sendMessage]
  );

  // Pause simulation
  const pause = useCallback(() => {
    sendMessage({ type: 'pause' });
    setIsPaused(true);
  }, [sendMessage]);

  // Resume simulation
  const resume = useCallback(() => {
    sendMessage({ type: 'resume' });
    setIsPaused(false);
  }, [sendMessage]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connectionState,
    connect,
    disconnect,
    frameData,
    params,
    updateParams,
    reset,
    applyPreset,
    pause,
    resume,
    isPaused,
  };
}