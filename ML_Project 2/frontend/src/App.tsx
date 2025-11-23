import React, { useState, useEffect } from 'react';
import { ImageMode } from './components/ImageMode/ImageMode';
import { StoryMode } from './components/StoryMode/StoryMode';
import { apiClient } from './services/api';
import './App.css';

type Mode = 'image' | 'story';

function App() {
  const [mode, setMode] = useState<Mode>('image');
  const [healthStatus, setHealthStatus] = useState<string>('checking...');
  const [modelsLoaded, setModelsLoaded] = useState<boolean>(false);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const health = await apiClient.checkHealth();
      setHealthStatus(health.status);
      setModelsLoaded(health.models_loaded);
    } catch (error) {
      setHealthStatus('offline');
      console.error('Health check failed:', error);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Art Generator & Storybook Editor</h1>
        <p className="tagline">Powered by Stable Diffusion & Agentic AI</p>
        <div className="health-status">
          <span className={`status-indicator ${healthStatus === 'healthy' ? 'healthy' : 'offline'}`}></span>
          <span>{healthStatus === 'healthy' ? 'Connected' : 'Offline'}</span>
          {modelsLoaded && <span className="models-ready">Models Ready</span>}
        </div>
      </header>

      <nav className="mode-selector">
        <button
          className={mode === 'image' ? 'active' : ''}
          onClick={() => setMode('image')}
        >
          Image Mode
        </button>
        <button
          className={mode === 'story' ? 'active' : ''}
          onClick={() => setMode('story')}
        >
          Storybook Mode
        </button>
      </nav>

      <main className="app-main">
        {!modelsLoaded && healthStatus === 'healthy' && (
          <div className="warning-banner">
            Models are loading... This may take a few minutes on first startup.
          </div>
        )}

        {mode === 'image' ? <ImageMode /> : <StoryMode />}
      </main>

      <footer className="app-footer">
        <p>Built with FastAPI, React, Stable Diffusion & LLM Agents</p>
      </footer>
    </div>
  );
}

export default App;
