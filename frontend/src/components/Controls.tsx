/**
 * Controls component for simulation parameters.
 */

import { useState } from 'react';
import type { SimulationParams, PresetName, ConnectionState } from '../types';
import { PARAM_DEFINITIONS, PRESET_NAMES } from '../constants';
import './Controls.css';

interface ControlsProps {
  params: SimulationParams | null;
  connectionState: ConnectionState;
  isPaused: boolean;
  onConnect: () => void;
  onDisconnect: () => void;
  onUpdateParams: (updates: Partial<SimulationParams>) => void;
  onReset: () => void;
  onApplyPreset: (name: PresetName) => void;
  onPause: () => void;
  onResume: () => void;
}

export function Controls({
  params,
  connectionState,
  isPaused,
  onConnect,
  onDisconnect,
  onUpdateParams,
  onReset,
  onApplyPreset,
  onPause,
  onResume,
}: ControlsProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const isConnected = connectionState === 'connected';

  return (
    <div className="controls">
      {/* Connection Section */}
      <section className="controls-section">
        <h3>Connection</h3>
        <div className="connection-status">
          <span className={`status-dot ${connectionState}`} />
          <span>{connectionState}</span>
        </div>
        <div className="button-row">
          {!isConnected ? (
            <button onClick={onConnect} disabled={connectionState === 'connecting'}>
              Connect
            </button>
          ) : (
            <button onClick={onDisconnect}>Disconnect</button>
          )}
        </div>
      </section>

      {/* Playback Controls */}
      {isConnected && (
        <section className="controls-section">
          <h3>Playback</h3>
          <div className="button-row">
            {isPaused ? (
              <button onClick={onResume}>▶ Resume</button>
            ) : (
              <button onClick={onPause}>⏸ Pause</button>
            )}
            <button onClick={onReset}>↻ Reset</button>
          </div>
        </section>
      )}

      {/* Presets */}
      {isConnected && (
        <section className="controls-section">
          <h3>Presets</h3>
          <select
            onChange={(e) => onApplyPreset(e.target.value as PresetName)}
            defaultValue=""
          >
            <option value="" disabled>
              Select preset...
            </option>
            {PRESET_NAMES.map(({ value, label }) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </section>
      )}

      {/* Primary Parameters */}
      {isConnected && params && (
        <section className="controls-section">
          <h3>Primary Parameters</h3>
          <ParameterSlider
            name="num_boids"
            value={params.num_boids}
            onChange={(v) => onUpdateParams({ num_boids: v })}
          />
          <ParameterSlider
            name="visual_range"
            value={params.visual_range}
            onChange={(v) => onUpdateParams({ visual_range: v })}
          />
          <ParameterSlider
            name="separation_strength"
            value={params.separation_strength}
            onChange={(v) => onUpdateParams({ separation_strength: v })}
          />
        </section>
      )}

      {/* Predator Parameters */}
      {isConnected && params && (
        <section className="controls-section">
          <h3>Predator</h3>
          <div className="checkbox-row">
            <label>
              <input
                type="checkbox"
                checked={params.predator_enabled}
                onChange={(e) => onUpdateParams({ predator_enabled: e.target.checked })}
              />
              Enable Predator
            </label>
          </div>
          {params.predator_enabled && (
            <>
              <ParameterSlider
                name="predator_speed"
                value={params.predator_speed}
                onChange={(v) => onUpdateParams({ predator_speed: v })}
              />
              <ParameterSlider
                name="predator_avoidance_strength"
                value={params.predator_avoidance_strength}
                onChange={(v) => onUpdateParams({ predator_avoidance_strength: v })}
              />
            </>
          )}
        </section>
      )}

      {/* Advanced Parameters */}
      {isConnected && params && (
        <section className="controls-section">
          <button
            className="toggle-advanced"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            {showAdvanced ? '▼' : '▶'} Advanced Parameters
          </button>
          {showAdvanced && (
            <div className="advanced-params">
              <ParameterSlider
                name="protected_range"
                value={params.protected_range}
                onChange={(v) => onUpdateParams({ protected_range: v })}
              />
              <ParameterSlider
                name="cohesion_factor"
                value={params.cohesion_factor}
                onChange={(v) => onUpdateParams({ cohesion_factor: v })}
              />
              <ParameterSlider
                name="alignment_factor"
                value={params.alignment_factor}
                onChange={(v) => onUpdateParams({ alignment_factor: v })}
              />
              <ParameterSlider
                name="max_speed"
                value={params.max_speed}
                onChange={(v) => onUpdateParams({ max_speed: v })}
              />
              <ParameterSlider
                name="min_speed"
                value={params.min_speed}
                onChange={(v) => onUpdateParams({ min_speed: v })}
              />
              <ParameterSlider
                name="margin"
                value={params.margin}
                onChange={(v) => onUpdateParams({ margin: v })}
              />
              <ParameterSlider
                name="turn_factor"
                value={params.turn_factor}
                onChange={(v) => onUpdateParams({ turn_factor: v })}
              />
            </div>
          )}
        </section>
      )}
    </div>
  );
}

// =============================================================================
// Parameter Slider Component
// =============================================================================

interface ParameterSliderProps {
  name: keyof SimulationParams;
  value: number;
  onChange: (value: number) => void;
}

function ParameterSlider({ name, value, onChange }: ParameterSliderProps) {
  const def = PARAM_DEFINITIONS[name];

  return (
    <div className="param-slider">
      <div className="param-header">
        <label>{def.label}</label>
        <span className="param-value">{value.toFixed(def.step < 1 ? 2 : 0)}</span>
      </div>
      <input
        type="range"
        min={def.min}
        max={def.max}
        step={def.step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        title={def.description}
      />
    </div>
  );
}