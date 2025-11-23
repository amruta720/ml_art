import React, { useState } from 'react';
import { apiClient } from '../../services/api';
import { ImageStyle, StoryModeResponse, StoryPanel, ThreePhaseStoryResponse, StoryAsset } from '../../types';
import { StyleSelector } from '../common/StyleSelector';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { StoryPanelComponent } from './StoryPanel';
import StoryBookViewer from './StoryBookViewer';
import { AssetUploader } from '../common/AssetUploader';

export const StoryGenerator: React.FC = () => {
  const [storyIdea, setStoryIdea] = useState('');
  const [numPanels, setNumPanels] = useState(4);
  const [style, setStyle] = useState<ImageStyle | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<StoryModeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [downloadingPDF, setDownloadingPDF] = useState(false);
  const [use3Phase, setUse3Phase] = useState(true);
  const [ageRange, setAgeRange] = useState('4-7');
  const [threePhasedResult, setThreePhasedResult] = useState<ThreePhaseStoryResponse | null>(null);
  const [generationPhase, setGenerationPhase] = useState<string>('');
  const [selectedAssets, setSelectedAssets] = useState<StoryAsset[]>([]);

  const handleGenerate = async () => {
    if (!storyIdea.trim()) {
      setError('Please enter a story idea');
      return;
    }

    const minPages = use3Phase ? 4 : 2;
    const maxPages = use3Phase ? 16 : 12;

    if (numPanels < minPages || numPanels > maxPages) {
      setError(`Number of ${use3Phase ? 'pages' : 'panels'} must be between ${minPages} and ${maxPages}`);
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setThreePhasedResult(null);
    setGenerationPhase('');

    try {
      if (use3Phase) {
        // Use 3-phase pipeline for professional storybooks
        setGenerationPhase('Phase 1: Creating story outline...');
        const response = await apiClient.generateStorybook3Phase({
          story_idea: storyIdea,
          num_pages: numPanels,
          age_range: ageRange,
          style,
          asset_ids: selectedAssets.map(a => a.id),
        });
        setThreePhasedResult(response);
        setGenerationPhase('');
      } else {
        // Use original storyboard mode
        const response = await apiClient.generateStorybook({
          story_idea: storyIdea,
          num_panels: numPanels,
          style,
          asset_ids: selectedAssets.map(a => a.id),
        });
        setResult(response);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate storybook');
      setGenerationPhase('');
    } finally {
      setLoading(false);
    }
  };

  const handlePanelUpdate = (panelNumber: number, updatedPanel: StoryPanel) => {
    if (!result) return;

    const updatedPanels = result.panels.map(p =>
      p.panel_number === panelNumber ? updatedPanel : p
    );

    setResult({
      ...result,
      panels: updatedPanels,
    });
  };

  const handleDownloadPDF = async () => {
    if (!result) return;

    setDownloadingPDF(true);
    try {
      await apiClient.downloadStorybook({
        story_title: result.story_title,
        panels: result.panels,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download PDF');
    } finally {
      setDownloadingPDF(false);
    }
  };

  return (
    <div className="story-generator">
      <div className="input-section">
        <h2>Storybook Mode</h2>
        <p className="subtitle">Create a multi-panel visual story with AI</p>

        <div className="form-group">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={use3Phase}
              onChange={(e) => setUse3Phase(e.target.checked)}
              disabled={loading}
            />
            <span className="toggle-text">
              Use 3-Phase Pipeline (Professional Children's Book Format)
            </span>
          </label>
          <p className="help-text">
            {use3Phase
              ? '📚 Creates a complete storybook with outline, narration, dialogues, and illustrations (like real children\'s books)'
              : '🎨 Quick storyboard mode with basic panels and images'}
          </p>
        </div>

        <div className="form-group">
          <label htmlFor="story-idea">Your story idea:</label>
          <textarea
            id="story-idea"
            value={storyIdea}
            onChange={(e) => setStoryIdea(e.target.value)}
            placeholder={use3Phase ? "e.g., an elephant who loves painting rainbows" : "e.g., a robot learning to paint"}
            rows={3}
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="num-panels">
            Number of {use3Phase ? 'pages' : 'panels'} ({use3Phase ? '4-16' : '2-12'}):
          </label>
          <input
            type="number"
            id="num-panels"
            value={numPanels}
            onChange={(e) => setNumPanels(parseInt(e.target.value) || (use3Phase ? 8 : 4))}
            min={use3Phase ? 4 : 2}
            max={use3Phase ? 16 : 12}
            disabled={loading}
          />
        </div>

        {use3Phase && (
          <div className="form-group">
            <label htmlFor="age-range">Target Age Range:</label>
            <select
              id="age-range"
              value={ageRange}
              onChange={(e) => setAgeRange(e.target.value)}
              disabled={loading}
            >
              <option value="2-4">Ages 2-4 (Toddlers)</option>
              <option value="4-7">Ages 4-7 (Preschool/Early Elementary)</option>
              <option value="7-10">Ages 7-10 (Elementary)</option>
              <option value="10-13">Ages 10-13 (Middle School)</option>
            </select>
          </div>
        )}

        <StyleSelector value={style} onChange={setStyle} />

        <AssetUploader
          onAssetUploaded={(asset) => setSelectedAssets([...selectedAssets, asset])}
          onAssetsChanged={setSelectedAssets}
          selectedAssets={selectedAssets}
        />

        <button onClick={handleGenerate} disabled={loading} className="btn-primary">
          {loading ? (generationPhase || 'Creating Story...') : `Generate ${use3Phase ? 'Storybook' : 'Storyboard'}`}
        </button>

        {error && <div className="error-message">{error}</div>}
      </div>

      {loading && (
        <LoadingSpinner message={generationPhase || `Creating ${numPanels}-${use3Phase ? 'page' : 'panel'} story... This may take a few minutes.`} />
      )}

      {threePhasedResult && !loading && (
        <div className="result-section">
          <div className="story-header">
            <h3>✨ Your Storybook is Ready!</h3>
            <div className="story-metadata">
              <span>Pages: {threePhasedResult.storybook.pages.length}</span>
              <span>Total Time: {threePhasedResult.total_generation_time.toFixed(2)}s</span>
              {threePhasedResult.phase_times && (
                <>
                  <span>Phase 1: {threePhasedResult.phase_times.phase_1_outline?.toFixed(1)}s</span>
                  <span>Phase 2: {threePhasedResult.phase_times.phase_2_text?.toFixed(1)}s</span>
                  <span>Phase 3: {threePhasedResult.phase_times.phase_3_art?.toFixed(1)}s</span>
                </>
              )}
            </div>
          </div>

          <StoryBookViewer storybook={threePhasedResult.storybook} />

          <div className="story-actions">
            <button onClick={() => window.print()} className="btn-primary">
              🖨️ Print Storybook
            </button>
            <button
              onClick={() => {
                setThreePhasedResult(null);
                setStoryIdea('');
              }}
              className="btn-secondary"
            >
              ➕ Create New Story
            </button>
          </div>
        </div>
      )}

      {result && !loading && (
        <div className="result-section">
          <div className="story-header">
            <h3>{result.story_title}</h3>
            <div className="story-metadata">
              {result.style_applied && <span>Style: {result.style_applied}</span>}
              <span>Panels: {result.panels.length}</span>
              <span>Total Time: {result.total_generation_time.toFixed(2)}s</span>
            </div>
          </div>

          <div className="story-panels-grid">
            {result.panels.map((panel) => (
              <StoryPanelComponent
                key={panel.panel_number}
                panel={panel}
                onPanelUpdate={(updatedPanel) => handlePanelUpdate(panel.panel_number, updatedPanel)}
              />
            ))}
          </div>

          <div className="story-actions">
            <button
              onClick={handleDownloadPDF}
              disabled={downloadingPDF}
              className="btn-primary"
            >
              {downloadingPDF ? 'Generating PDF...' : '📥 Download Storybook (PDF)'}
            </button>
            <button onClick={() => window.print()} className="btn-secondary">
              🖨️ Print Storybook
            </button>
            <button
              onClick={() => {
                setResult(null);
                setStoryIdea('');
              }}
              className="btn-secondary"
            >
              ➕ Create New Story
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
