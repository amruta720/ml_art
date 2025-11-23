/**
 * AssetUploader component for uploading reference images/files
 */
import React, { useState } from 'react';
import { apiClient } from '../../services/api';
import { StoryAsset, AssetUsage } from '../../types';

interface AssetUploaderProps {
  onAssetUploaded: (asset: StoryAsset) => void;
  onAssetsChanged: (assets: StoryAsset[]) => void;
  selectedAssets: StoryAsset[];
}

export const AssetUploader: React.FC<AssetUploaderProps> = ({
  onAssetUploaded,
  onAssetsChanged,
  selectedAssets,
}) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const response = await apiClient.uploadAsset(
        file,
        AssetUsage.STYLE,
        `Reference image: ${file.name}`
      );

      onAssetUploaded(response.asset);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
      // Reset the input
      event.target.value = '';
    }
  };

  const handleRemoveAsset = async (assetId: string) => {
    try {
      await apiClient.deleteAsset(assetId);
      onAssetsChanged(selectedAssets.filter(a => a.id !== assetId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed');
    }
  };

  return (
    <div className="asset-uploader">
      <div className="upload-section">
        <label htmlFor="asset-upload" className="upload-label">
          📎 Upload Reference Images (optional)
        </label>
        <p className="help-text">
          Upload images to influence the story's visual style, characters, or themes
        </p>
        <input
          type="file"
          id="asset-upload"
          accept="image/*"
          onChange={handleFileUpload}
          disabled={uploading}
          className="file-input"
        />
        {uploading && <span className="uploading-text">Uploading...</span>}
        {error && <div className="error-text">{error}</div>}
      </div>

      {selectedAssets.length > 0 && (
        <div className="assets-list">
          <h4>Reference Images:</h4>
          <div className="assets-grid">
            {selectedAssets.map((asset) => (
              <div key={asset.id} className="asset-card">
                <img src={asset.url} alt={asset.filename} className="asset-preview" />
                <div className="asset-info">
                  <span className="asset-filename">{asset.filename}</span>
                  <span className="asset-usage">{asset.usage}</span>
                </div>
                <button
                  onClick={() => handleRemoveAsset(asset.id)}
                  className="remove-btn"
                  title="Remove asset"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <style>{`
        .asset-uploader {
          margin: 20px 0;
        }

        .upload-section {
          margin-bottom: 15px;
        }

        .upload-label {
          display: block;
          font-weight: 600;
          margin-bottom: 5px;
          color: #2c3e50;
        }

        .help-text {
          font-size: 0.9rem;
          color: #666;
          margin: 5px 0;
        }

        .file-input {
          display: block;
          margin-top: 10px;
          padding: 8px;
          border: 2px dashed #3498db;
          border-radius: 5px;
          background: #f8f9fa;
          cursor: pointer;
          width: 100%;
        }

        .file-input:hover {
          background: #e9ecef;
        }

        .uploading-text {
          display: inline-block;
          margin-left: 10px;
          color: #3498db;
          font-style: italic;
        }

        .error-text {
          color: #e74c3c;
          margin-top: 5px;
          font-size: 0.9rem;
        }

        .assets-list {
          margin-top: 20px;
          padding: 15px;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .assets-list h4 {
          margin: 0 0 10px 0;
          color: #2c3e50;
        }

        .assets-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
          gap: 15px;
        }

        .asset-card {
          position: relative;
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 8px;
          background: white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .asset-preview {
          width: 100%;
          height: 120px;
          object-fit: cover;
          border-radius: 5px;
          margin-bottom: 8px;
        }

        .asset-info {
          display: flex;
          flex-direction: column;
          gap: 3px;
        }

        .asset-filename {
          font-size: 0.85rem;
          font-weight: 600;
          color: #2c3e50;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .asset-usage {
          font-size: 0.75rem;
          color: #7f8c8d;
          text-transform: capitalize;
        }

        .remove-btn {
          position: absolute;
          top: 5px;
          right: 5px;
          background: #e74c3c;
          color: white;
          border: none;
          border-radius: 50%;
          width: 24px;
          height: 24px;
          cursor: pointer;
          font-size: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          opacity: 0.9;
        }

        .remove-btn:hover {
          opacity: 1;
          background: #c0392b;
        }
      `}</style>
    </div>
  );
};
