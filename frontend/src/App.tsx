/**
 * Boids Interactive Demo - Full Version
 */

import { useState, useRef, useCallback } from 'react';
import './App.css';

const WS_URL = 'ws://localhost:8000/ws';

interface FrameData {
  type: string;
  frame_id: number;
  boids: number[][];
  predator: number[] | null;
  metrics: {
    fps: number;
    avg_distance_to_predator?: number;
    min_distance_to_predator?: number;
  };
}

interface Params {
  num_boids: number;
  visual_range: number;
  separation_strength: number;
  predator_enabled: boolean;
  predator_speed: number;
  predator_avoidance_strength: number;
  cohesion_factor: number;
  alignment_factor: number;
  max_speed: number;
  min_speed: number;
}

const PRESETS = [
  { value: 'default', label: 'Default' },
  { value: 'tight_swarm', label: 'Tight Swarm' },
  { value: 'loose_cloud', label: 'Loose Cloud' },
  { value: 'high_speed', label: 'High Speed' },
  { value: 'slow_dance', label: 'Slow Dance' },
  { value: 'predator_chase', label: 'Predator Chase' },
  { value: 'swarm_defense', label: 'Swarm Defense' },
];

function App() {
  const [status, setStatus] = useState('disconnected');
  const [frameData, setFrameData] = useState<FrameData | null>(null);
  const [params, setParams] = useState<Params | null>(null);
  const [isPaused, setIsPaused] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const sendMessage = useCallback((msg: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    }
  }, []);

  const connect = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setStatus('connecting');
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => setStatus('connected');
    ws.onclose = () => {
      setStatus('disconnected');
      wsRef.current = null;
    };
    ws.onerror = () => setStatus('error');

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === 'frame') {
        setFrameData(data);
        drawFrame(data);
      } else if (data.type === 'params_sync') {
        setParams(data.params);
      }
    };

    wsRef.current = ws;
  };

  const disconnect = () => wsRef.current?.close();

  const drawFrame = (data: FrameData) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, 800, 600);

    // Draw boids as triangles
    ctx.fillStyle = '#4ecdc4';
    ctx.strokeStyle = '#45b7aa';
    data.boids.forEach((boid) => {
      const [x, y, vx, vy] = boid;
      const angle = Math.atan2(vy, vx);
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(angle);
      ctx.beginPath();
      ctx.moveTo(8, 0);
      ctx.lineTo(-5, 4);
      ctx.lineTo(-5, -4);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    });

    // Draw predator
    if (data.predator) {
      const [x, y, vx, vy] = data.predator;
      const angle = Math.atan2(vy, vx);
      ctx.fillStyle = '#ff6b6b';
      ctx.strokeStyle = '#ee5a5a';
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(angle);
      ctx.beginPath();
      ctx.moveTo(14, 0);
      ctx.lineTo(-8, 7);
      ctx.lineTo(-8, -7);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    }

    // Draw stats
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.fillRect(8, 8, 140, 50);
    ctx.fillStyle = '#fff';
    ctx.font = '12px monospace';
    ctx.fillText(`Frame: ${data.frame_id}`, 16, 24);
    ctx.fillText(`Boids: ${data.boids.length}`, 16, 40);
    ctx.fillText(`FPS: ${data.metrics.fps}`, 16, 56);
  };

  const updateParam = (key: string, value: number | boolean) => {
    sendMessage({ type: 'update_params', params: { [key]: value } });
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Boids Interactive Demo</h1>
      </header>

      <main className="main">
        <canvas ref={canvasRef} width={800} height={600} className="canvas" />

        <aside className="controls">
          {/* Connection */}
          <section className="section">
            <h3>Connection</h3>
            <div className="status">
              <span className={`dot ${status}`} />
              {status}
            </div>
            <div className="buttons">
              {status !== 'connected' ? (
                <button onClick={connect}>Connect</button>
              ) : (
                <button onClick={disconnect}>Disconnect</button>
              )}
            </div>
          </section>

          {status === 'connected' && (
            <>
              {/* Playback */}
              <section className="section">
                <h3>Playback</h3>
                <div className="buttons">
                  <button onClick={() => { sendMessage({ type: isPaused ? 'resume' : 'pause' }); setIsPaused(!isPaused); }}>
                    {isPaused ? '▶ Resume' : '⏸ Pause'}
                  </button>
                  <button onClick={() => sendMessage({ type: 'reset' })}>↻ Reset</button>
                </div>
              </section>

              {/* Presets */}
              <section className="section">
                <h3>Presets</h3>
                <select onChange={(e) => sendMessage({ type: 'preset', name: e.target.value })} defaultValue="">
                  <option value="" disabled>Select preset...</option>
                  {PRESETS.map((p) => (
                    <option key={p.value} value={p.value}>{p.label}</option>
                  ))}
                </select>
              </section>

              {/* Parameters */}
              {params && (
                <section className="section">
                  <h3>Parameters</h3>
                  
                  <Slider label="Boids" value={params.num_boids} min={1} max={200} step={1}
                    onChange={(v) => updateParam('num_boids', v)} />
                  
                  <Slider label="Visual Range" value={params.visual_range} min={10} max={150} step={5}
                    onChange={(v) => updateParam('visual_range', v)} />
                  
                  <Slider label="Separation" value={params.separation_strength} min={0.01} max={0.5} step={0.01}
                    onChange={(v) => updateParam('separation_strength', v)} />
                  
                  <Slider label="Cohesion" value={params.cohesion_factor} min={0.0001} max={0.02} step={0.0005}
                    onChange={(v) => updateParam('cohesion_factor', v)} />
                  
                  <Slider label="Alignment" value={params.alignment_factor} min={0.01} max={0.2} step={0.01}
                    onChange={(v) => updateParam('alignment_factor', v)} />
                  
                  <Slider label="Max Speed" value={params.max_speed} min={1} max={8} step={0.5}
                    onChange={(v) => updateParam('max_speed', v)} />
                </section>
              )}

              {/* Predator */}
              {params && (
                <section className="section">
                  <h3>Predator</h3>
                  <label className="checkbox">
                    <input
                      type="checkbox"
                      checked={params.predator_enabled}
                      onChange={(e) => updateParam('predator_enabled', e.target.checked)}
                    />
                    Enable Predator
                  </label>
                  
                  {params.predator_enabled && (
                    <>
                      <Slider label="Speed" value={params.predator_speed} min={0.5} max={5} step={0.1}
                        onChange={(v) => updateParam('predator_speed', v)} />
                      <Slider label="Avoidance" value={params.predator_avoidance_strength} min={0.05} max={1.5} step={0.05}
                        onChange={(v) => updateParam('predator_avoidance_strength', v)} />
                    </>
                  )}
                </section>
              )}
            </>
          )}
        </aside>
      </main>
    </div>
  );
}

function Slider({ label, value, min, max, step, onChange }: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="slider">
      <div className="slider-header">
        <span>{label}</span>
        <span className="slider-value">{value.toFixed(step < 1 ? 3 : 0)}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
      />
    </div>
  );
}

export default App;