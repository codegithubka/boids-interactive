/**
 * TypeScript types for the Boids Interactive Demo.
 */

// =============================================================================
// Simulation Data Types
// =============================================================================

/** Boid data: [x, y, vx, vy] */
export type BoidData = [number, number, number, number];

/** Predator data: [x, y, vx, vy] or null */
export type PredatorData = [number, number, number, number] | null;

/** Frame metrics */
export interface FrameMetrics {
  fps: number;
  avg_distance_to_predator?: number;
  min_distance_to_predator?: number;
  flock_cohesion?: number;
}

/** Frame data from server */
export interface FrameData {
  type: 'frame';
  frame_id: number;
  boids: BoidData[];
  predator: PredatorData;
  metrics: FrameMetrics;
}

// =============================================================================
// Parameter Types
// =============================================================================

/** All simulation parameters */
export interface SimulationParams {
  num_boids: number;
  visual_range: number;
  separation_strength: number;
  predator_enabled: boolean;
  predator_speed: number;
  predator_avoidance_strength: number;
  protected_range: number;
  cohesion_factor: number;
  alignment_factor: number;
  max_speed: number;
  min_speed: number;
  margin: number;
  turn_factor: number;
  predator_detection_range: number;
  predator_hunting_strength: number;
}

/** Parameter metadata */
export interface ParamDefinition {
  min: number;
  max: number;
  default: number;
  step: number;
  category: 'primary' | 'predator' | 'advanced';
  label: string;
  description: string;
}

// =============================================================================
// WebSocket Message Types
// =============================================================================

/** Message types */
export type MessageType =
  | 'update_params'
  | 'reset'
  | 'preset'
  | 'pause'
  | 'resume'
  | 'frame'
  | 'params_sync'
  | 'error';

/** Params sync message from server */
export interface ParamsSyncMessage {
  type: 'params_sync';
  params: SimulationParams;
}

/** Error message from server */
export interface ErrorMessage {
  type: 'error';
  message: string;
}

/** Server message union type */
export type ServerMessage = FrameData | ParamsSyncMessage | ErrorMessage;

// =============================================================================
// Preset Types
// =============================================================================

/** Available preset names */
export type PresetName =
  | 'default'
  | 'tight_swarm'
  | 'loose_cloud'
  | 'high_speed'
  | 'slow_dance'
  | 'predator_chase'
  | 'swarm_defense';

// =============================================================================
// Connection State
// =============================================================================

/** WebSocket connection state */
export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

/** Hook return type */
export interface UseSimulationReturn {
  // Connection
  connectionState: ConnectionState;
  connect: () => void;
  disconnect: () => void;

  // Data
  frameData: FrameData | null;
  params: SimulationParams | null;

  // Actions
  updateParams: (updates: Partial<SimulationParams>) => void;
  reset: () => void;
  applyPreset: (name: PresetName) => void;
  pause: () => void;
  resume: () => void;
  isPaused: boolean;
}