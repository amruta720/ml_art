/**
 * InlineEditableText component - Supports both manual and AI-powered editing.
 *
 * Features:
 * - Click to edit manually (like Notion/Google Docs)
 * - Select text for AI-powered editing (existing feature)
 * - Auto-save on blur
 * - Smooth transitions between edit/view modes
 */
import React, { useState, useRef, useEffect } from 'react';
import { apiClient } from '../../services/api';

interface InlineEditableTextProps {
  text: string;
  onTextChange: (newText: string) => void;
  context: string;
  className?: string;
  placeholder?: string;
}

const InlineEditableText: React.FC<InlineEditableTextProps> = ({
  text,
  onTextChange,
  context,
  className = '',
  placeholder = 'Click to edit...',
}) => {
  const [localText, setLocalText] = useState(text);
  const [isEditingManually, setIsEditingManually] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [showEditButton, setShowEditButton] = useState(false);
  const [buttonPosition, setButtonPosition] = useState({ top: 0, left: 0 });
  const [showModal, setShowModal] = useState(false);
  const [instruction, setInstruction] = useState('');
  const [isEditingWithAI, setIsEditingWithAI] = useState(false);
  const [error, setError] = useState('');
  const textRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Sync local state with prop changes
  useEffect(() => {
    setLocalText(text);
  }, [text]);

  // Auto-focus textarea when entering edit mode
  useEffect(() => {
    if (isEditingManually && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.select();
    }
  }, [isEditingManually]);

  // Handle manual editing - double click to edit
  const handleDoubleClick = () => {
    setIsEditingManually(true);
    setShowEditButton(false); // Hide AI button when manually editing
  };

  // Handle blur - save changes
  const handleBlur = () => {
    setIsEditingManually(false);
    if (localText !== text) {
      onTextChange(localText);
    }
  };

  // Handle text selection for AI editing
  const handleMouseUp = () => {
    if (isEditingManually) return; // Don't show AI button during manual edit

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
        context,
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

  // Hide AI button when clicking elsewhere
  useEffect(() => {
    const handleClickOutside = () => {
      setShowEditButton(false);
    };

    if (showEditButton) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showEditButton]);

  return (
    <>
      {isEditingManually ? (
        <textarea
          ref={textareaRef}
          className={`${className} inline-edit-textarea`}
          value={localText}
          onChange={(e) => setLocalText(e.target.value)}
          onBlur={handleBlur}
          onKeyDown={(e) => {
            if (e.key === 'Escape') {
              setLocalText(text); // Revert changes
              setIsEditingManually(false);
            }
          }}
          placeholder={placeholder}
        />
      ) : (
        <div
          ref={textRef}
          className={`${className} inline-editable-text`}
          onDoubleClick={handleDoubleClick}
          onMouseUp={handleMouseUp}
          title="Double-click to edit, or select text for AI editing"
        >
          {localText.split('\n').map((paragraph, idx) => (
            <p key={idx}>{paragraph || '\u00A0'}</p>
          ))}
        </div>
      )}

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
            <h3>Edit Text with AI</h3>

            <div className="selected-text-preview">
              <strong>Selected text:</strong>
              <p>"{selectedText}"</p>
            </div>

            <div className="instruction-input">
              <label htmlFor="edit-instruction">How should I change this?</label>
              <input
                id="edit-instruction"
                type="text"
                placeholder="e.g., make it simpler, happier, shorter, more exciting..."
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
        .inline-editable-text {
          cursor: text;
          user-select: text;
          position: relative;
          min-height: 40px;
          padding: 8px;
          border: 2px solid transparent;
          border-radius: 4px;
          transition: all 0.2s ease;
        }

        .inline-editable-text:hover {
          background: #f8f9fa;
          border-color: #e0e0e0;
        }

        .inline-editable-text::after {
          content: '✏️ Double-click to edit';
          position: absolute;
          top: -25px;
          left: 0;
          font-size: 0.75rem;
          color: #999;
          opacity: 0;
          transition: opacity 0.2s ease;
          pointer-events: none;
        }

        .inline-editable-text:hover::after {
          opacity: 1;
        }

        .inline-editable-text::selection {
          background-color: #b3d9ff;
        }

        .inline-editable-text p {
          margin: 0;
          padding: 5px 0;
        }

        .inline-edit-textarea {
          width: 100%;
          min-height: 100px;
          padding: 12px;
          font-size: inherit;
          font-family: inherit;
          line-height: 1.8;
          border: 2px solid #667eea;
          border-radius: 4px;
          resize: vertical;
          outline: none;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .inline-edit-textarea:focus {
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
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
          border-left: 4px solid #667eea;
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
          border-color: #667eea;
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

export default InlineEditableText;
