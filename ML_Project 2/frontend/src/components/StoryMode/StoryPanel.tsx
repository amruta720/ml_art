import React, { useState } from 'react';
import { StoryPanel as StoryPanelType } from '../../types';
import { apiClient } from '../../services/api';

interface StoryPanelProps {
  panel: StoryPanelType;
  loading?: boolean;
  onPanelUpdate?: (updatedPanel: StoryPanelType) => void;
}

export const StoryPanelComponent: React.FC<StoryPanelProps> = ({
  panel,
  loading = false,
  onPanelUpdate
}) => {
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editInstruction, setEditInstruction] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [downloadFormat, setDownloadFormat] = useState<'png' | 'jpg' | 'webp'>('png');

  const handleEditText = async (fieldType: 'narration' | 'dialogue', originalText: string, dialogueIndex?: number) => {
    if (!editInstruction.trim()) {
      alert('Please enter an instruction for how to edit the text.');
      return;
    }

    setIsEditing(true);
    try {
      const context = `Panel ${panel.panel_number}: ${panel.title}. ${fieldType === 'dialogue' ? 'Character dialogue in a children\'s storybook.' : 'Narration in a children\'s storybook.'}`;

      const response = await apiClient.editTextSegment({
        original_text: originalText,
        instruction: editInstruction,
        context: context,
      });

      // Update the panel with the edited text
      if (onPanelUpdate) {
        const updatedPanel = { ...panel };

        if (fieldType === 'narration') {
          updatedPanel.narration = response.edited_text;
        } else if (fieldType === 'dialogue' && dialogueIndex !== undefined) {
          updatedPanel.dialogues = [...panel.dialogues];
          updatedPanel.dialogues[dialogueIndex] = {
            ...updatedPanel.dialogues[dialogueIndex],
            text: response.edited_text,
          };
        }

        onPanelUpdate(updatedPanel);
      }

      setEditingField(null);
      setEditInstruction('');
    } catch (error) {
      console.error('Error editing text:', error);
      alert('Failed to edit text. Please try again.');
    } finally {
      setIsEditing(false);
    }
  };

  const handleDownloadImage = () => {
    if (!panel.image_url) return;

    const downloadUrl = apiClient.downloadImage(panel.image_url, downloadFormat);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `panel-${panel.panel_number}.${downloadFormat}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="story-panel">
      <div className="panel-header">
        <span className="panel-number">Panel {panel.panel_number}</span>
        {panel.title && <h3 className="panel-title">{panel.title}</h3>}
      </div>

      {loading ? (
        <div className="panel-loading">
          <div className="spinner-small"></div>
          <p>Generating...</p>
        </div>
      ) : panel.image_url ? (
        <div className="panel-image-container">
          <img src={panel.image_url} alt={`Panel ${panel.panel_number}`} className="panel-image" />
          <div className="image-download-controls">
            <select
              value={downloadFormat}
              onChange={(e) => setDownloadFormat(e.target.value as 'png' | 'jpg' | 'webp')}
              className="format-selector"
            >
              <option value="png">PNG</option>
              <option value="jpg">JPG</option>
              <option value="webp">WEBP</option>
            </select>
            <button onClick={handleDownloadImage} className="download-btn">
              ⬇ Download
            </button>
          </div>
        </div>
      ) : (
        <div className="panel-placeholder">Image will appear here</div>
      )}

      <div className="panel-details">
        {/* Narration */}
        {panel.narration && (
          <div className="panel-narration">
            <div className="text-content-header">
              <strong>Narration:</strong>
              <button
                onClick={() => setEditingField('narration')}
                className="edit-text-btn"
                title="Edit with AI"
              >
                ✏️ Edit
              </button>
            </div>
            <p className="narration-text">{panel.narration}</p>

            {editingField === 'narration' && (
              <div className="edit-modal">
                <h4>Edit Narration</h4>
                <p className="original-text">"{panel.narration}"</p>
                <input
                  type="text"
                  placeholder="What do you want to change? (e.g., 'Make it more exciting')"
                  value={editInstruction}
                  onChange={(e) => setEditInstruction(e.target.value)}
                  className="edit-instruction-input"
                />
                <div className="edit-buttons">
                  <button
                    onClick={() => handleEditText('narration', panel.narration)}
                    disabled={isEditing || !editInstruction.trim()}
                    className="apply-btn"
                  >
                    {isEditing ? 'Applying...' : 'Apply'}
                  </button>
                  <button
                    onClick={() => {
                      setEditingField(null);
                      setEditInstruction('');
                    }}
                    className="cancel-btn"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Dialogues */}
        {panel.dialogues && panel.dialogues.length > 0 && (
          <div className="panel-dialogues">
            <strong>Dialogue:</strong>
            {panel.dialogues.map((dialogue, idx) => (
              <div key={idx} className="dialogue-line">
                <div className="dialogue-header">
                  <span className="speaker-name">{dialogue.speaker}:</span>
                  <button
                    onClick={() => setEditingField(`dialogue-${idx}`)}
                    className="edit-text-btn-small"
                    title="Edit with AI"
                  >
                    ✏️
                  </button>
                </div>
                <p className="dialogue-text">"{dialogue.text}"</p>

                {editingField === `dialogue-${idx}` && (
                  <div className="edit-modal">
                    <h4>Edit Dialogue</h4>
                    <p className="original-text">"{dialogue.text}"</p>
                    <input
                      type="text"
                      placeholder="What do you want to change?"
                      value={editInstruction}
                      onChange={(e) => setEditInstruction(e.target.value)}
                      className="edit-instruction-input"
                    />
                    <div className="edit-buttons">
                      <button
                        onClick={() => handleEditText('dialogue', dialogue.text, idx)}
                        disabled={isEditing || !editInstruction.trim()}
                        className="apply-btn"
                      >
                        {isEditing ? 'Applying...' : 'Apply'}
                      </button>
                      <button
                        onClick={() => {
                          setEditingField(null);
                          setEditInstruction('');
                        }}
                        className="cancel-btn"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Collapsible details */}
        {panel.image_prompt && (
          <details className="panel-prompt">
            <summary>View Image Prompt</summary>
            <p>{panel.image_prompt}</p>
          </details>
        )}
      </div>
    </div>
  );
};
