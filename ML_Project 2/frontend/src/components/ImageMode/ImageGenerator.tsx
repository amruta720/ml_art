import React, { useState } from 'react';
import { apiClient } from '../../services/api';
import { ImageStyle, ImageModeResponse } from '../../types';
import { StyleSelector } from '../common/StyleSelector';
import { LoadingSpinner } from '../common/LoadingSpinner';

export const ImageGenerator: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState<ImageStyle | undefined>(undefined);
  const [enhancePrompt, setEnhancePrompt] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImageModeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState('');
  const [revising, setRevising] = useState(false);
  const [downloadFormat, setDownloadFormat] = useState<'png' | 'jpg' | 'webp'>('png');

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiClient.generateImage({
        prompt,
        style,
        enhance_prompt: enhancePrompt,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate image');
    } finally {
      setLoading(false);
    }
  };

  const handleRevise = async () => {
    if (!result || !feedback.trim()) {
      setError('Please enter feedback for revision');
      return;
    }

    setRevising(true);
    setError(null);

    try {
      const response = await apiClient.reviseImage({
        original_prompt: result.original_prompt,
        feedback,
        style,
      });
      setResult(response);
      setFeedback('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to revise image');
    } finally {
      setRevising(false);
    }
  };

  const handleDownloadImage = () => {
    if (!result?.image_url) return;

    const downloadUrl = apiClient.downloadImage(result.image_url, downloadFormat);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `generated-image.${downloadFormat}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="image-generator">
      <div className="input-section">
        <h2>Image Mode</h2>
        <p className="subtitle">Generate a single image with AI assistance</p>

        <div className="form-group">
          <label htmlFor="prompt">Describe your image:</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., a serene mountain lake at sunset"
            rows={4}
            disabled={loading}
          />
        </div>

        <StyleSelector value={style} onChange={setStyle} />

        <div className="checkbox-group">
          <label>
            <input
              type="checkbox"
              checked={enhancePrompt}
              onChange={(e) => setEnhancePrompt(e.target.checked)}
              disabled={loading}
            />
            <span>Use AI Prompt Stylist (Recommended)</span>
          </label>
        </div>

        <button onClick={handleGenerate} disabled={loading} className="btn-primary">
          {loading ? 'Generating...' : 'Generate Image'}
        </button>

        {error && <div className="error-message">{error}</div>}
      </div>

      {loading && <LoadingSpinner message="Creating your masterpiece..." />}

      {result && !loading && (
        <div className="result-section">
          <h3>Generated Image</h3>
          <img src={result.image_url} alt="Generated" className="generated-image" />

          <div className="download-controls">
            <label htmlFor="download-format">Download as:</label>
            <select
              id="download-format"
              value={downloadFormat}
              onChange={(e) => setDownloadFormat(e.target.value as 'png' | 'jpg' | 'webp')}
              className="format-selector"
            >
              <option value="png">PNG</option>
              <option value="jpg">JPG</option>
              <option value="webp">WEBP</option>
            </select>
            <button onClick={handleDownloadImage} className="btn-primary">
              ⬇ Download Image
            </button>
          </div>

          <div className="metadata">
            <p>
              <strong>Original Prompt:</strong> {result.original_prompt}
            </p>
            <p>
              <strong>Enhanced Prompt:</strong> {result.enhanced_prompt}
            </p>
            {result.style_applied && (
              <p>
                <strong>Style:</strong> {result.style_applied}
              </p>
            )}
            <p>
              <strong>Generation Time:</strong> {result.generation_time.toFixed(2)}s
            </p>
          </div>

          <div className="revision-section">
            <h4>Not quite right? Revise it!</h4>
            <div className="form-group">
              <label htmlFor="feedback">What would you like to change?</label>
              <textarea
                id="feedback"
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="e.g., make it more dramatic with stormy clouds"
                rows={3}
                disabled={revising}
              />
            </div>
            <button onClick={handleRevise} disabled={revising} className="btn-secondary">
              {revising ? 'Revising...' : 'Revise Image'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
