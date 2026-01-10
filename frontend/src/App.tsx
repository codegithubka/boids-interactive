/**
 * Boids Interactive Demo - Enhanced Visuals with Obstacles
 */

import { useState, useRef, useCallback } from 'react';
import './App.css';

const WS_URL = 'ws://localhost:8000/ws';

interface FrameData {
  type: string;
  frame_id: number;
  boids: number[][];
  predator: number[] | null;
  obstacles: number[][];  // [[x, y, radius], ...]
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

// Store trails for each boid
const trailsMap = new Map<number, {x: number, y: number}[]>();
const TRAIL_LENGTH = 8;

function App() {
  const [status, setStatus] = useState('disconnected');
  const [frameData, setFrameData] = useState<FrameData | null>(null);
  const [params, setParams] = useState<Params | null>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [showTrails, setShowTrails] = useState(true);
  const [obstacleRadius, setObstacleRadius] = useState(30);
  const [obstacleCount, setObstacleCount] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const sendMessage = useCallback((msg: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    }
  }, []);

  const connect = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    trailsMap.clear();

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
        setObstacleCount(data.obstacles?.length || 0);
        drawFrame(data);
      } else if (data.type === 'params_sync') {
        setParams(data.params);
      }
    };

    wsRef.current = ws;
  };

  const disconnect = () => wsRef.current?.close();

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || status !== 'connected') return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    sendMessage({
      type: 'add_obstacle',
      x: x,
      y: y,
      radius: obstacleRadius
    });
  };

  const clearObstacles = () => {
    sendMessage({ type: 'clear_obstacles' });
  };

  const drawFrame = (data: FrameData) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Sky gradient background
    const gradient = ctx.createLinearGradient(0, 0, 0, 600);
    gradient.addColorStop(0, '#0a0a1a');
    gradient.addColorStop(0.5, '#1a1a3e');
    gradient.addColorStop(1, '#2a1a2e');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 800, 600);

    // Draw obstacles first (behind everything)
    if (data.obstacles && data.obstacles.length > 0) {
      data.obstacles.forEach((obs) => {
        drawObstacle(ctx, obs);
      });
    }

    // Update trails
    data.boids.forEach((boid, i) => {
      const [x, y] = boid;
      if (!trailsMap.has(i)) {
        trailsMap.set(i, []);
      }
      const trail = trailsMap.get(i)!;
      trail.push({ x, y });
      if (trail.length > TRAIL_LENGTH) {
        trail.shift();
      }
    });

    // Draw trails
    if (showTrails) {
      data.boids.forEach((boid, i) => {
        const trail = trailsMap.get(i);
        if (trail && trail.length > 1) {
          drawTrail(ctx, trail, boid);
        }
      });
    }

    // Draw predator danger zone
    if (data.predator) {
      drawPredatorAura(ctx, data.predator);
    }

    // Draw boids
    data.boids.forEach((boid) => {
      drawBird(ctx, boid, data.predator);
    });

    // Draw predator
    if (data.predator) {
      drawPredator(ctx, data.predator);
    }

    // Draw stats
    drawStats(ctx, data);
  };

  const drawObstacle = (ctx: CanvasRenderingContext2D, obs: number[]) => {
    const [x, y, radius] = obs;
    
    // Outer glow
    const gradient = ctx.createRadialGradient(x, y, radius * 0.8, x, y, radius * 1.5);
    gradient.addColorStop(0, 'rgba(60, 60, 80, 0.8)');
    gradient.addColorStop(0.6, 'rgba(40, 40, 60, 0.4)');
    gradient.addColorStop(1, 'rgba(40, 40, 60, 0)');
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(x, y, radius * 1.5, 0, Math.PI * 2);
    ctx.fill();
    
    // Main obstacle body
    const bodyGradient = ctx.createRadialGradient(x - radius * 0.3, y - radius * 0.3, 0, x, y, radius);
    bodyGradient.addColorStop(0, '#5a5a7a');
    bodyGradient.addColorStop(0.7, '#3a3a5a');
    bodyGradient.addColorStop(1, '#2a2a4a');
    ctx.fillStyle = bodyGradient;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
    
    // Border
    ctx.strokeStyle = 'rgba(100, 100, 140, 0.5)';
    ctx.lineWidth = 2;
    ctx.stroke();
  };

  const drawTrail = (ctx: CanvasRenderingContext2D, trail: {x: number, y: number}[], boid: number[]) => {
    const [, , vx, vy] = boid;
    const speed = Math.sqrt(vx * vx + vy * vy);
    const normalizedSpeed = Math.min(speed / 4, 1);

    ctx.beginPath();
    ctx.moveTo(trail[0].x, trail[0].y);
    
    for (let i = 1; i < trail.length; i++) {
      ctx.lineTo(trail[i].x, trail[i].y);
    }

    ctx.strokeStyle = `rgba(78, 205, 196, ${0.1 + normalizedSpeed * 0.2})`;
    ctx.lineWidth = 1 + normalizedSpeed;
    ctx.lineCap = 'round';
    ctx.stroke();
  };

  const drawBird = (ctx: CanvasRenderingContext2D, boid: number[], predator: number[] | null) => {
    const [x, y, vx, vy] = boid;
    const angle = Math.atan2(vy, vx);
    const speed = Math.sqrt(vx * vx + vy * vy);
    const normalizedSpeed = Math.min(speed / 4, 1);

    // Check distance to predator for fear coloring
    let fear = 0;
    if (predator) {
      const dx = x - predator[0];
      const dy = y - predator[1];
      const dist = Math.sqrt(dx * dx + dy * dy);
      fear = Math.max(0, 1 - dist / 150);
    }

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);

    // Glow effect for fast boids
    if (normalizedSpeed > 0.5) {
      ctx.shadowColor = '#4ecdc4';
      ctx.shadowBlur = 5 + normalizedSpeed * 10;
    }

    // Bird body - teardrop shape
    ctx.beginPath();
    ctx.moveTo(10, 0);
    ctx.bezierCurveTo(6, -3, -4, -4, -6, 0);
    ctx.bezierCurveTo(-4, 4, 6, 3, 10, 0);
    ctx.closePath();

    // Color based on speed and fear
    const r = Math.floor(78 + fear * 150 + normalizedSpeed * 30);
    const g = Math.floor(205 - fear * 100);
    const b = Math.floor(196 - fear * 100);
    ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
    ctx.fill();

    // Wing hints
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(-3, -5 - normalizedSpeed * 2);
    ctx.lineTo(-5, 0);
    ctx.moveTo(0, 0);
    ctx.lineTo(-3, 5 + normalizedSpeed * 2);
    ctx.lineTo(-5, 0);
    ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, 0.6)`;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.restore();
  };

  const drawPredatorAura = (ctx: CanvasRenderingContext2D, predator: number[]) => {
    const [x, y] = predator;
    
    // Danger zone gradient
    const gradient = ctx.createRadialGradient(x, y, 0, x, y, 150);
    gradient.addColorStop(0, 'rgba(255, 80, 80, 0.15)');
    gradient.addColorStop(0.5, 'rgba(255, 80, 80, 0.05)');
    gradient.addColorStop(1, 'rgba(255, 80, 80, 0)');
    
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(x, y, 150, 0, Math.PI * 2);
    ctx.fill();
  };

  const drawPredator = (ctx: CanvasRenderingContext2D, predator: number[]) => {
    const [x, y, vx, vy] = predator;
    const angle = Math.atan2(vy, vx);

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);

    // Glow
    ctx.shadowColor = '#ff4444';
    ctx.shadowBlur = 20;

    // Hawk-like shape
    ctx.beginPath();
    // Body
    ctx.moveTo(18, 0);
    ctx.bezierCurveTo(12, -5, -8, -6, -12, 0);
    ctx.bezierCurveTo(-8, 6, 12, 5, 18, 0);
    ctx.closePath();
    ctx.fillStyle = '#ff6b6b';
    ctx.fill();

    // Wings - swept back
    ctx.beginPath();
    ctx.moveTo(2, 0);
    ctx.lineTo(-8, -14);
    ctx.lineTo(-12, -8);
    ctx.lineTo(-4, 0);
    ctx.lineTo(-12, 8);
    ctx.lineTo(-8, 14);
    ctx.lineTo(2, 0);
    ctx.closePath();
    ctx.fillStyle = '#ee5555';
    ctx.fill();

    // Eye
    ctx.beginPath();
    ctx.arc(8, -2, 2, 0, Math.PI * 2);
    ctx.fillStyle = '#ffff00';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(8, -2, 1, 0, Math.PI * 2);
    ctx.fillStyle = '#000';
    ctx.fill();

    ctx.restore();
  };

  const drawStats = (ctx: CanvasRenderingContext2D, data: FrameData) => {
    ctx.shadowBlur = 0;
    ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
    ctx.roundRect(10, 10, 140, 76, 8);
    ctx.fill();
    
    ctx.fillStyle = '#fff';
    ctx.font = '12px monospace';
    ctx.fillText(`Frame: ${data.frame_id}`, 20, 28);
    ctx.fillText(`Boids: ${data.boids.length}`, 20, 44);
    ctx.fillText(`FPS: ${data.metrics.fps.toFixed(1)}`, 20, 60);
    ctx.fillText(`Obstacles: ${data.obstacles?.length || 0}`, 20, 76);
  };

  const updateParam = (key: string, value: number | boolean) => {
    sendMessage({ type: 'update_params', params: { [key]: value } });
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🐦 Boids Interactive Demo</h1>
        <p>Flocking simulation with predator-prey dynamics • Click canvas to add obstacles</p>
      </header>

      <main className="main">
        <canvas 
          ref={canvasRef} 
          width={800} 
          height={600} 
          className="canvas"
          onClick={handleCanvasClick}
          style={{ cursor: status === 'connected' ? 'crosshair' : 'default' }}
        />

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
                  <button onClick={() => { sendMessage({ type: 'reset' }); trailsMap.clear(); }}>
                    ↻ Reset
                  </button>
                </div>
              </section>

              {/* Obstacles */}
              <section className="section">
                <h3>🪨 Obstacles ({obstacleCount})</h3>
                <p className="hint">Click on canvas to add obstacles</p>
                <Slider label="New Obstacle Radius" value={obstacleRadius} min={15} max={60} step={5}
                  onChange={(v) => setObstacleRadius(v)} />
                <button onClick={clearObstacles} style={{ marginTop: 8 }}>
                  Clear All Obstacles
                </button>
              </section>

              {/* Visual Options */}
              <section className="section">
                <h3>Visuals</h3>
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={showTrails}
                    onChange={(e) => setShowTrails(e.target.checked)}
                  />
                  Show Motion Trails
                </label>
              </section>

              {/* Presets */}
              <section className="section">
                <h3>Presets</h3>
                <select onChange={(e) => { sendMessage({ type: 'preset', name: e.target.value }); trailsMap.clear(); }} defaultValue="">
                  <option value="" disabled>Select preset...</option>
                  {PRESETS.map((p) => (
                    <option key={p.value} value={p.value}>{p.label}</option>
                  ))}
                </select>
              </section>

              {/* Parameters */}
              {params && (
                <section className="section">
                  <h3>Flock Behavior</h3>
                  
                  <Slider label="Boids" value={params.num_boids} min={1} max={200} step={1}
                    onChange={(v) => { updateParam('num_boids', v); trailsMap.clear(); }} />
                  
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
                  <h3>🦅 Predator</h3>
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
                      <Slider label="Hunt Speed" value={params.predator_speed} min={0.5} max={5} step={0.1}
                        onChange={(v) => updateParam('predator_speed', v)} />
                      <Slider label="Flock Fear" value={params.predator_avoidance_strength} min={0.05} max={1.5} step={0.05}
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