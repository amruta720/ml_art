/**
 * InlineEditableDialogue component - Supports both manual and AI-powered editing for dialogue lines.
 *
 * Features:
 * - Click to edit the dialogue text directly
 * - Select text for AI-powered editing
 * - Auto-save on blur
 * - Preserves speaker name
 */
import React, { useState, useRef, useEffect } from 'react';
import { apiClient } from '../../services/api';

interface InlineEditableDialogueProps {
  speaker: string;
  text: string;
  onTextChange: (newText: string) => void;
  onSpeakerChange: (newSpeaker: string) => void;
  context: string;
}

const InlineEditableDialogue: React.FC<InlineEditableDialogueProps> = ({
  speaker,
  text,
  onTextChange,
  onSpeakerChange,
  context,
}) => {
  const [localText, setLocalText] = useState(text);
  const [localSpeaker, setLocalSpeaker] = useState(speaker);
  const [isEditingManually, setIsEditingManually] = useState(false);
  const [isEditingSpeaker, setIsEditingSpeaker] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [showEditButton, setShowEditButton] = useState(false);
  const [buttonPosition, setButtonPosition] = useState({ top: 0, left: 0 });
  const [showModal, setShowModal] = useState(false);
  const [instruction, setInstruction] = useState('');
  const [isEditingWithAI, setIsEditingWithAI] = useState(false);
  const [error, setError] = useState('');
  const textRef = useRef<HTMLSpanElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const speakerInputRef = useRef<HTMLInputElement>(null);

  // Sync local state with prop changes
  useEffect(() => {
    setLocalText(text);
  }, [text]);

  useEffect(() => {
    setLocalSpeaker(speaker);
  }, [speaker]);

  // Auto-focus input when entering edit mode
  useEffect(() => {
    if (isEditingManually && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditingManually]);

  // Auto-focus speaker input when entering edit mode
  useEffect(() => {
    if (isEditingSpeaker && speakerInputRef.current) {
      speakerInputRef.current.focus();
      speakerInputRef.current.select();
    }
  }, [isEditingSpeaker]);

  // Handle manual editing - click to edit
  const handleClick = (e: React.MouseEvent) => {
    // Only activate edit mode if clicking on the text, not selecting
    if (window.getSelection()?.toString()) return;
    e.stopPropagation();
    setIsEditingManually(true);
    setShowEditButton(false);
  };

  // Handle blur - save changes
  const handleBlur = () => {
    setIsEditingManually(false);
    if (localText !== text) {
      onTextChange(localText);
    }
  };

  // Handle speaker click - edit speaker name
  const handleSpeakerClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsEditingSpeaker(true);
  };

  // Handle speaker blur - save changes
  const handleSpeakerBlur = () => {
    setIsEditingSpeaker(false);
    if (localSpeaker !== speaker && localSpeaker.trim()) {
      onSpeakerChange(localSpeaker.trim());
    } else if (!localSpeaker.trim()) {
      setLocalSpeaker(speaker); // Revert if empty
    }
  };

  // Handle text selection for AI editing
  const handleMouseUp = (e: React.MouseEvent) => {
    if (isEditingManually) return; // Don't show AI button during manual edit

    e.stopPropagation();

    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) {
      setShowEditButton(false);
      return;
    }

    const selected = selection.toString().trim();
    if (!selected) {
      setShowEditButton(false);
      return;
    }

    // Check if selection is within our text element
    const range = selection.getRangeAt(0);
    if (!textRef.current?.contains(range.commonAncestorContainer)) {
      setShowEditButton(false);
      return;
    }

    setSelectedText(selected);

    // Position the edit button near the selection
    const rect = range.getBoundingClientRect();
    setButtonPosition({
      top: rect.bottom + window.scrollY + 5,
      left: rect.left + window.scrollX + rect.width / 2,
    });

    setShowEditButton(true);
  };

  // Handle AI edit button click
  const handleAIEditClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowModal(true);
    setShowEditButton(false);
  };

  // Handle AI edit submission
  const handleSubmitAIEdit = async () => {
    if (!instruction.trim()) {
      setError('Please provide editing instructions');
      return;
    }

    setIsEditingWithAI(true);
    setError('');

    try {
      const response = await apiClient.editTextSegment({
        original_text: selectedText,
        instruction: instruction.trim(),
        context: `${context} - Dialogue by ${speaker}`,
      });

      // Replace the selected text with edited text
      const newText = localText.replace(selectedText, response.edited_text);
      setLocalText(newText);
      onTextChange(newText);

      // Close modal and reset
      setShowModal(false);
      setInstruction('');
      setSelectedText('');
    } catch (err) {
      console.error('AI edit failed:', err);
      setError('Failed to edit text. Please try again.');
    } finally {
      setIsEditingWithAI(false);
    }
  };

  // Close AI modal
  const handleCloseModal = () => {
    setShowModal(false);
    setInstruction('');
    setError('');
  };

  return (
    <>
      <div className="inline-dialogue-line">
        {isEditingSpeaker ? (
          <input
            ref={speakerInputRef}
            className="speaker-edit-input"
            type="text"
            value={localSpeaker}
            onChange={(e) => setLocalSpeaker(e.target.value)}
            onBlur={handleSpeakerBlur}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSpeakerBlur();
              } else if (e.key === 'Escape') {
                setLocalSpeaker(speaker); // Revert changes
                setIsEditingSpeaker(false);
              }
            }}
          />
        ) : (
          <span
            className="dialogue-speaker"
            onClick={handleSpeakerClick}
            title="Click to edit speaker name"
          >
            {localSpeaker}:
          </span>
        )}
        {isEditingManually ? (
          <input
            ref={inputRef}
            className="dialogue-edit-input"
            type="text"
            value={localText}
            onChange={(e) => setLocalText(e.target.value)}
            onBlur={handleBlur}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleBlur();
              } else if (e.key === 'Escape') {
                setLocalText(text); // Revert changes
                setIsEditingManually(false);
              }
            }}
          />
        ) : (
          <span
            ref={textRef}
            className="dialogue-text-editable"
            onClick={handleClick}
            onMouseUp={handleMouseUp}
            title="Click to edit, or select text for AI editing"
          >
            "{localText}"
          </span>
        )}
      </div>

      {/* Floating AI Edit Button */}
      {showEditButton && (
        <button
          className="edit-ai-button"
          style={{
            position: 'absolute',
            top: `${buttonPosition.top}px`,
            left: `${buttonPosition.left}px`,
            transform: 'translateX(-50%)',
          }}
          onClick={handleAIEditClick}
        >
          ✨ Edit with AI
        </button>
      )}

      {/* AI Edit Modal */}
      {showModal && (
        <div className="edit-modal-overlay" onClick={handleCloseModal}>
          <div className="edit-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Edit Dialogue with AI</h3>

            <div className="selected-text-preview">
              <strong>Selected text:</strong>
              <p>"{selectedText}"</p>
              <small>From {speaker}'s dialogue</small>
            </div>

            <div className="instruction-input">
              <label htmlFor="edit-instruction">How should I change this?</label>
              <input
                id="edit-instruction"
                type="text"
                placeholder="e.g., make it more emotional, funnier, more formal..."
                value={instruction}
                onChange={(e) => setInstruction(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !isEditingWithAI) {
                    handleSubmitAIEdit();
                  }
                }}
                autoFocus
              />
            </div>

            {error && <div className="edit-error">{error}</div>}

            <div className="modal-actions">
              <button
                className="btn-cancel"
                onClick={handleCloseModal}
                disabled={isEditingWithAI}
              >
                Cancel
              </button>
              <button
                className="btn-submit"
                onClick={handleSubmitAIEdit}
                disabled={isEditingWithAI || !instruction.trim()}
              >
                {isEditingWithAI ? 'Editing...' : 'Apply Edit'}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .inline-dialogue-line {
          margin-bottom: 12px;
          display: flex;
          align-items: baseline;
          gap: 8px;
        }

        .dialogue-speaker {
          font-weight: bold;
          color: #e74c3c;
          flex-shrink: 0;
          cursor: pointer;
          padding: 2px 6px;
          border: 2px solid transparent;
          border-radius: 4px;
          transition: all 0.2s ease;
        }

        .dialogue-speaker:hover {
          background: #ffe6e6;
          border-color: #ffcccc;
        }

        .speaker-edit-input {
          font-weight: bold;
          color: #e74c3c;
          padding: 2px 6px;
          font-size: inherit;
          font-family: inherit;
          border: 2px solid #e74c3c;
          border-radius: 4px;
          outline: none;
          box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
          flex-shrink: 0;
          min-width: 80px;
        }

        .speaker-edit-input:focus {
          box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.2);
        }

        .dialogue-text-editable {
          color: #444;
          font-style: italic;
          cursor: text;
          padding: 4px 8px;
          border: 2px solid transparent;
          border-radius: 4px;
          transition: all 0.2s ease;
          user-select: text;
          flex: 1;
        }

        .dialogue-text-editable:hover {
          background: #f8f9fa;
          border-color: #e0e0e0;
        }

        .dialogue-text-editable::selection {
          background-color: #ffe6f0;
        }

        .dialogue-edit-input {
          flex: 1;
          padding: 6px 12px;
          font-size: inherit;
          font-family: inherit;
          font-style: italic;
          border: 2px solid #e74c3c;
          border-radius: 4px;
          outline: none;
          box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
        }

        .dialogue-edit-input:focus {
          box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.2);
        }

        .edit-ai-button {
          z-index: 1000;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 20px;
          font-size: 0.9rem;
          font-weight: 600;
          cursor: pointer;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
          transition: all 0.2s ease;
          white-space: nowrap;
        }

        .edit-ai-button:hover {
          transform: translateX(-50%) translateY(-2px);
          box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
        }

        .edit-modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 2000;
        }

        .edit-modal {
          background: white;
          border-radius: 12px;
          padding: 30px;
          max-width: 500px;
          width: 90%;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }

        .edit-modal h3 {
          margin: 0 0 20px 0;
          font-size: 1.5rem;
          color: #2c3e50;
        }

        .selected-text-preview {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 8px;
          margin-bottom: 20px;
          border-left: 4px solid #e74c3c;
        }

        .selected-text-preview strong {
          display: block;
          margin-bottom: 8px;
          color: #555;
          font-size: 0.9rem;
        }

        .selected-text-preview p {
          margin: 0;
          color: #333;
          font-style: italic;
          line-height: 1.6;
        }

        .selected-text-preview small {
          display: block;
          margin-top: 5px;
          color: #e74c3c;
          font-weight: 600;
        }

        .instruction-input {
          margin-bottom: 20px;
        }

        .instruction-input label {
          display: block;
          margin-bottom: 8px;
          font-weight: 600;
          color: #2c3e50;
        }

        .instruction-input input {
          width: 100%;
          padding: 12px;
          border: 2px solid #e0e0e0;
          border-radius: 8px;
          font-size: 1rem;
          transition: border-color 0.2s ease;
        }

        .instruction-input input:focus {
          outline: none;
          border-color: #e74c3c;
        }

        .edit-error {
          background: #ffe6e6;
          color: #c0392b;
          padding: 10px;
          border-radius: 6px;
          margin-bottom: 15px;
          font-size: 0.9rem;
        }

        .modal-actions {
          display: flex;
          gap: 10px;
          justify-content: flex-end;
        }

        .modal-actions button {
          padding: 10px 20px;
          border: none;
          border-radius: 6px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .btn-cancel {
          background: #e0e0e0;
          color: #555;
        }

        .btn-cancel:hover:not(:disabled) {
          background: #d0d0d0;
        }

        .btn-submit {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .btn-submit:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .btn-submit:disabled,
        .btn-cancel:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </>
  );
};

export default InlineEditableDialogue;
