/**
 * Boids Interactive Demo - Main Application
 */

import { useSimulation } from './hooks/useSimulation';
import { SimulationCanvas } from './components/SimulationCanvas';
import { Controls } from './components/Controls';
import './App.css';

function App() {
  const {
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
  } = useSimulation();

  return (
    <div className="app">
      <header className="app-header">
        <h1>Boids Interactive Demo</h1>
        <p>Real-time flocking simulation with WebSocket streaming</p>
      </header>

      <main className="app-main">
        <div className="simulation-container">
          <SimulationCanvas frameData={frameData} />
        </div>

        <aside className="controls-container">
          <Controls
            params={params}
            connectionState={connectionState}
            isPaused={isPaused}
            onConnect={connect}
            onDisconnect={disconnect}
            onUpdateParams={updateParams}
            onReset={reset}
            onApplyPreset={applyPreset}
            onPause={pause}
            onResume={resume}
          />
        </aside>
      </main>

      <footer className="app-footer">
        <p>
          Built with React + FastAPI •{' '}
          <a
            href="https://en.wikipedia.org/wiki/Boids"
            target="_blank"
            rel="noopener noreferrer"
          >
            Learn about Boids
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;