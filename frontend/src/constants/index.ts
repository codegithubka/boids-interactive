/**
 * Constants for the Boids Interactive Demo.
 */

import type { ParamDefinition, PresetName, SimulationParams } from '../types';

// =============================================================================
// Simulation Constants
// =============================================================================

export const SIMULATION_WIDTH = 800;
export const SIMULATION_HEIGHT = 600;
export const TARGET_FPS = 60;

// =============================================================================
// WebSocket Configuration
// =============================================================================

export const WS_URL = 'ws://localhost:8000/ws';

// =============================================================================
// Parameter Definitions
// =============================================================================

export const PARAM_DEFINITIONS: Record<keyof SimulationParams, ParamDefinition> = {
  num_boids: {
    min: 1,
    max: 200,
    default: 50,
    step: 1,
    category: 'primary',
    label: 'Number of Boids',
    description: 'Total number of boids in the simulation',
  },
  visual_range: {
    min: 10,
    max: 150,
    default: 50,
    step: 5,
    category: 'primary',
    label: 'Visual Range',
    description: 'How far each boid can see (pixels)',
  },
  separation_strength: {
    min: 0.01,
    max: 0.5,
    default: 0.15,
    step: 0.01,
    category: 'primary',
    label: 'Separation Strength',
    description: 'How strongly boids avoid each other',
  },
  predator_enabled: {
    min: 0,
    max: 1,
    default: 0,
    step: 1,
    category: 'predator',
    label: 'Predator Enabled',
    description: 'Toggle predator on/off',
  },
  predator_speed: {
    min: 0.5,
    max: 5.0,
    default: 2.5,
    step: 0.1,
    category: 'predator',
    label: 'Predator Speed',
    description: 'Maximum speed of the predator',
  },
  predator_avoidance_strength: {
    min: 0.05,
    max: 1.5,
    default: 0.5,
    step: 0.05,
    category: 'predator',
    label: 'Avoidance Strength',
    description: 'How strongly boids flee from predator',
  },
  protected_range: {
    min: 2,
    max: 50,
    default: 12,
    step: 1,
    category: 'advanced',
    label: 'Protected Range',
    description: 'Personal space radius for separation (pixels)',
  },
  cohesion_factor: {
    min: 0.0001,
    max: 0.02,
    default: 0.002,
    step: 0.0005,
    category: 'advanced',
    label: 'Cohesion Factor',
    description: 'How strongly boids are attracted to flock center',
  },
  alignment_factor: {
    min: 0.01,
    max: 0.2,
    default: 0.06,
    step: 0.01,
    category: 'advanced',
    label: 'Alignment Factor',
    description: 'How strongly boids match neighbor velocities',
  },
  max_speed: {
    min: 1.0,
    max: 8.0,
    default: 3.0,
    step: 0.5,
    category: 'advanced',
    label: 'Max Speed',
    description: 'Maximum boid speed (pixels/frame)',
  },
  min_speed: {
    min: 0.5,
    max: 4.0,
    default: 2.0,
    step: 0.5,
    category: 'advanced',
    label: 'Min Speed',
    description: 'Minimum boid speed (pixels/frame)',
  },
  margin: {
    min: 20,
    max: 150,
    default: 75,
    step: 5,
    category: 'advanced',
    label: 'Boundary Margin',
    description: 'Distance from edge where boids start turning (pixels)',
  },
  turn_factor: {
    min: 0.05,
    max: 0.8,
    default: 0.2,
    step: 0.05,
    category: 'advanced',
    label: 'Turn Factor',
    description: 'Strength of boundary avoidance steering',
  },
  predator_detection_range: {
    min: 30,
    max: 250,
    default: 100,
    step: 10,
    category: 'advanced',
    label: 'Detection Range',
    description: 'Distance at which boids detect predator (pixels)',
  },
  predator_hunting_strength: {
    min: 0.01,
    max: 0.2,
    default: 0.05,
    step: 0.01,
    category: 'advanced',
    label: 'Hunting Strength',
    description: 'How aggressively predator pursues flock',
  },
};

// =============================================================================
// Preset Names
// =============================================================================

export const PRESET_NAMES: { value: PresetName; label: string }[] = [
  { value: 'default', label: 'Default' },
  { value: 'tight_swarm', label: 'Tight Swarm' },
  { value: 'loose_cloud', label: 'Loose Cloud' },
  { value: 'high_speed', label: 'High Speed' },
  { value: 'slow_dance', label: 'Slow Dance' },
  { value: 'predator_chase', label: 'Predator Chase' },
  { value: 'swarm_defense', label: 'Swarm Defense' },
];

// =============================================================================
// Rendering Constants
// =============================================================================

export const COLORS = {
  background: '#1a1a2e',
  boid: '#4ecdc4',
  boidStroke: '#45b7aa',
  predator: '#ff6b6b',
  predatorStroke: '#ee5a5a',
  text: '#ffffff',
  textMuted: '#888888',
};

export const BOID_SIZE = 8;
export const PREDATOR_SIZE = 14;