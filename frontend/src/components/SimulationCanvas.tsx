/**
 * Canvas component for rendering the boids simulation.
 */

import { useRef, useEffect } from 'react';
import type { FrameData, BoidData } from '../types';
import {
  SIMULATION_WIDTH,
  SIMULATION_HEIGHT,
  COLORS,
  BOID_SIZE,
  PREDATOR_SIZE,
} from '../constants';

interface SimulationCanvasProps {
  frameData: FrameData | null;
}

export function SimulationCanvas({ frameData }: SimulationCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.fillStyle = COLORS.background;
    ctx.fillRect(0, 0, SIMULATION_WIDTH, SIMULATION_HEIGHT);

    if (!frameData) {
      // Draw "Connecting..." text
      ctx.fillStyle = COLORS.textMuted;
      ctx.font = '24px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Connecting...', SIMULATION_WIDTH / 2, SIMULATION_HEIGHT / 2);
      return;
    }

    // Draw boids
    frameData.boids.forEach((boid) => {
      drawBoid(ctx, boid);
    });

    // Draw predator if present
    if (frameData.predator) {
      drawPredator(ctx, frameData.predator);
    }

    // Draw metrics overlay
    drawMetrics(ctx, frameData);
  }, [frameData]);

  return (
    <canvas
      ref={canvasRef}
      width={SIMULATION_WIDTH}
      height={SIMULATION_HEIGHT}
      style={{
        border: '2px solid #333',
        borderRadius: '8px',
      }}
    />
  );
}

/**
 * Draw a single boid as a triangle pointing in its direction.
 */
function drawBoid(ctx: CanvasRenderingContext2D, boid: BoidData) {
  const [x, y, vx, vy] = boid;
  const angle = Math.atan2(vy, vx);

  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);

  // Draw triangle
  ctx.beginPath();
  ctx.moveTo(BOID_SIZE, 0);
  ctx.lineTo(-BOID_SIZE * 0.6, BOID_SIZE * 0.5);
  ctx.lineTo(-BOID_SIZE * 0.6, -BOID_SIZE * 0.5);
  ctx.closePath();

  ctx.fillStyle = COLORS.boid;
  ctx.fill();
  ctx.strokeStyle = COLORS.boidStroke;
  ctx.lineWidth = 1;
  ctx.stroke();

  ctx.restore();
}

/**
 * Draw the predator as a larger red triangle.
 */
function drawPredator(ctx: CanvasRenderingContext2D, predator: BoidData) {
  const [x, y, vx, vy] = predator;
  const angle = Math.atan2(vy, vx);

  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);

  // Draw triangle
  ctx.beginPath();
  ctx.moveTo(PREDATOR_SIZE, 0);
  ctx.lineTo(-PREDATOR_SIZE * 0.6, PREDATOR_SIZE * 0.5);
  ctx.lineTo(-PREDATOR_SIZE * 0.6, -PREDATOR_SIZE * 0.5);
  ctx.closePath();

  ctx.fillStyle = COLORS.predator;
  ctx.fill();
  ctx.strokeStyle = COLORS.predatorStroke;
  ctx.lineWidth = 2;
  ctx.stroke();

  ctx.restore();
}

/**
 * Draw metrics overlay in the top-left corner.
 */
function drawMetrics(ctx: CanvasRenderingContext2D, frameData: FrameData) {
  const { metrics, frame_id, boids } = frameData;

  ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
  ctx.fillRect(8, 8, 150, metrics.avg_distance_to_predator ? 100 : 60);

  ctx.fillStyle = COLORS.text;
  ctx.font = '12px monospace';
  ctx.textAlign = 'left';

  let y = 24;
  ctx.fillText(`Frame: ${frame_id}`, 16, y);
  y += 16;
  ctx.fillText(`Boids: ${boids.length}`, 16, y);
  y += 16;
  ctx.fillText(`FPS: ${metrics.fps.toFixed(1)}`, 16, y);

  if (metrics.avg_distance_to_predator !== undefined) {
    y += 16;
    ctx.fillText(`Avg Dist: ${metrics.avg_distance_to_predator.toFixed(0)}`, 16, y);
    y += 16;
    ctx.fillText(`Min Dist: ${metrics.min_distance_to_predator?.toFixed(0) ?? '-'}`, 16, y);
  }
}