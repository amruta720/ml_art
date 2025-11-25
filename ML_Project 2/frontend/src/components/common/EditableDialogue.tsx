/**
 * EditableDialogue component - Enables inline AI editing of dialogue text.
 *
 * Similar to EditableText but optimized for dialogue lines.
 */
import React, { useState, useRef } from 'react';
import { apiClient } from '../../services/api';

interface EditableDialogueProps {
  speaker: string;
  text: string;
  onTextChange: (newText: string) => void;
  context: string;
}

const EditableDialogue: React.FC<EditableDialogueProps> = ({
  speaker,
  text,
  onTextChange,
  context,
}) => {
  const [selectedText, setSelectedText] = useState('');
  const [showEditButton, setShowEditButton] = useState(false);
  const [buttonPosition, setButtonPosition] = useState({ top: 0, left: 0 });
  const [showModal, setShowModal] = useState(false);
  const [instruction, setInstruction] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState('');
  const textRef = useRef<HTMLSpanElement>(null);

  // Handle text selection
  const handleMouseUp = () => {
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

  // Handle edit button click
  const handleEditClick = () => {
    setShowModal(true);
    setShowEditButton(false);
  };

  // Handle edit submission
  const handleSubmitEdit = async () => {
    if (!instruction.trim()) {
      setError('Please provide editing instructions');
      return;
    }

    setIsEditing(true);
    setError('');

    try {
      const response = await apiClient.editTextSegment({
        original_text: selectedText,
        instruction: instruction.trim(),
        context: `${context} - Dialogue by ${speaker}`,
      });

      // Replace the selected text with edited text
      const newText = text.replace(selectedText, response.edited_text);
      onTextChange(newText);

      // Close modal and reset
      setShowModal(false);
      setInstruction('');
      setSelectedText('');
    } catch (err) {
      console.error('Edit failed:', err);
      setError('Failed to edit text. Please try again.');
    } finally {
      setIsEditing(false);
    }
  };

  // Close modal
  const handleCloseModal = () => {
    setShowModal(false);
    setInstruction('');
    setError('');
  };

  return (
    <>
      <div className="dialogue-line">
        <span className="dialogue-speaker">{speaker}:</span>
        <span
          ref={textRef}
          className="dialogue-text editable-dialogue"
          onMouseUp={handleMouseUp}
        >
          "{text}"
        </span>
      </div>

      {/* Floating Edit Button */}
      {showEditButton && (
        <button
          className="edit-ai-button"
          style={{
            position: 'absolute',
            top: `${buttonPosition.top}px`,
            left: `${buttonPosition.left}px`,
            transform: 'translateX(-50%)',
          }}
          onClick={handleEditClick}
        >
          ✨ Edit with AI
        </button>
      )}

      {/* Edit Instruction Modal */}
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
                  if (e.key === 'Enter' && !isEditing) {
                    handleSubmitEdit();
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
                disabled={isEditing}
              >
                Cancel
              </button>
              <button
                className="btn-submit"
                onClick={handleSubmitEdit}
                disabled={isEditing || !instruction.trim()}
              >
                {isEditing ? 'Editing...' : 'Apply Edit'}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .editable-dialogue {
          cursor: text;
          user-select: text;
        }

        .editable-dialogue::selection {
          background-color: #ffe6f0;
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

export default EditableDialogue;
