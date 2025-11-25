/**
 * StoryBookViewer component for displaying 3-phase generated storybooks.
 *
 * Displays pages in a real children's book format:
 * - Left page: Full-page illustration
 * - Right page: Title, narration, and dialogues (with inline AI editing)
 */
import React, { useState } from 'react';
import { StoryBook, DialogueLine } from '../../types';
import InlineEditableText from '../common/InlineEditableText';
import InlineEditableDialogue from '../common/InlineEditableDialogue';

interface StoryBookViewerProps {
  storybook: StoryBook;
}

const StoryBookViewer: React.FC<StoryBookViewerProps> = ({ storybook: initialStorybook }) => {
  const [storybook, setStorybook] = useState<StoryBook>(initialStorybook);

  // Update narration for a specific page
  const handleNarrationChange = (pageNumber: number, newNarration: string) => {
    setStorybook((prev) => ({
      ...prev,
      pages: prev.pages.map((page) =>
        page.page_number === pageNumber
          ? { ...page, narration: newNarration }
          : page
      ),
    }));
  };

  // Update dialogue for a specific page and dialogue index
  const handleDialogueChange = (
    pageNumber: number,
    dialogueIndex: number,
    newText: string
  ) => {
    setStorybook((prev) => ({
      ...prev,
      pages: prev.pages.map((page) =>
        page.page_number === pageNumber
          ? {
              ...page,
              dialogues: page.dialogues.map((dialogue, idx) =>
                idx === dialogueIndex ? { ...dialogue, text: newText } : dialogue
              ),
            }
          : page
      ),
    }));
  };

  // Update speaker name for a specific page and dialogue index
  const handleSpeakerChange = (
    pageNumber: number,
    dialogueIndex: number,
    newSpeaker: string
  ) => {
    setStorybook((prev) => ({
      ...prev,
      pages: prev.pages.map((page) =>
        page.page_number === pageNumber
          ? {
              ...page,
              dialogues: page.dialogues.map((dialogue, idx) =>
                idx === dialogueIndex ? { ...dialogue, speaker: newSpeaker } : dialogue
              ),
            }
          : page
      ),
    }));
  };
  return (
    <div className="storybook-viewer">
      {/* Story Title Section */}
      <div className="story-header">
        <h1 className="story-title">{storybook.meta.title}</h1>
        <p className="story-logline">{storybook.meta.logline}</p>
        <div className="story-meta">
          <span className="age-range">Ages {storybook.meta.age_range}</span>
          {storybook.meta.characters.length > 0 && (
            <div className="characters-list">
              <strong>Characters:</strong>
              <ul>
                {storybook.meta.characters.map((char, idx) => (
                  <li key={idx}>{char}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Story Pages */}
      <div className="story-pages">
        {storybook.pages.map((page) => (
          <div key={page.page_number} className="story-spread">
            {/* Left Page - Image */}
            <div className="page-left">
              {page.image_url ? (
                <img
                  src={page.image_url}
                  alt={`${page.title} - Page ${page.page_number}`}
                  className="page-image"
                />
              ) : (
                <div className="page-image-placeholder">
                  <p>Generating image...</p>
                </div>
              )}
              <div className="page-number-left">Page {page.page_number}</div>
            </div>

            {/* Right Page - Text */}
            <div className="page-right">
              <div className="page-content">
                <h2 className="page-title">{page.title}</h2>

                {/* Editable Narration */}
                <InlineEditableText
                  text={page.narration}
                  onTextChange={(newText: string) =>
                    handleNarrationChange(page.page_number, newText)
                  }
                  context={`Narration on page ${page.page_number} of story "${storybook.meta.title}"`}
                  className="page-narration"
                  placeholder="Click to add narration..."
                />

                {/* Editable Dialogues */}
                {page.dialogues && page.dialogues.length > 0 && (
                  <div className="page-dialogues">
                    {page.dialogues.map((dialogue: DialogueLine, idx: number) => (
                      <InlineEditableDialogue
                        key={idx}
                        speaker={dialogue.speaker}
                        text={dialogue.text}
                        onTextChange={(newText: string) =>
                          handleDialogueChange(page.page_number, idx, newText)
                        }
                        onSpeakerChange={(newSpeaker: string) =>
                          handleSpeakerChange(page.page_number, idx, newSpeaker)
                        }
                        context={`Page ${page.page_number} of story "${storybook.meta.title}"`}
                      />
                    ))}
                  </div>
                )}
              </div>
              <div className="page-number-right">Page {page.page_number}</div>
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .storybook-viewer {
          max-width: 1400px;
          margin: 0 auto;
          padding: 20px;
        }

        .story-header {
          text-align: center;
          margin-bottom: 40px;
          padding: 30px;
          background: linear-gradient(to bottom, #f8f9fa, #ffffff);
          border-radius: 10px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .story-title {
          font-size: 2.5rem;
          font-weight: bold;
          color: #2c3e50;
          margin-bottom: 10px;
        }

        .story-logline {
          font-size: 1.2rem;
          color: #555;
          font-style: italic;
          margin-bottom: 15px;
        }

        .story-meta {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 10px;
        }

        .age-range {
          background: #e74c3c;
          color: white;
          padding: 5px 15px;
          border-radius: 20px;
          font-size: 0.9rem;
          font-weight: bold;
        }

        .characters-list {
          margin-top: 15px;
          text-align: left;
        }

        .characters-list ul {
          list-style: none;
          padding: 0;
          margin-top: 5px;
        }

        .characters-list li {
          padding: 5px 0;
          color: #555;
        }

        .story-pages {
          display: flex;
          flex-direction: column;
          gap: 40px;
        }

        .story-spread {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 30px;
          min-height: 600px;
          background: white;
          border-radius: 10px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          overflow: hidden;
        }

        .page-left, .page-right {
          position: relative;
          padding: 30px;
          display: flex;
          flex-direction: column;
        }

        .page-left {
          background: #f8f9fa;
          border-right: 2px dashed #ddd;
          justify-content: center;
          align-items: center;
        }

        .page-image {
          max-width: 100%;
          max-height: 100%;
          object-fit: contain;
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }

        .page-image-placeholder {
          width: 100%;
          height: 400px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #e0e0e0;
          border-radius: 8px;
          color: #666;
        }

        .page-right {
          background: #ffffff;
          justify-content: flex-start;
        }

        .page-content {
          flex: 1;
        }

        .page-title {
          font-size: 1.8rem;
          font-weight: bold;
          color: #2c3e50;
          margin-bottom: 20px;
          border-bottom: 3px solid #3498db;
          padding-bottom: 10px;
        }

        .page-narration {
          font-size: 1.1rem;
          line-height: 1.8;
          color: #333;
          margin-bottom: 20px;
        }

        .page-narration p {
          margin-bottom: 15px;
        }

        .page-dialogues {
          margin-top: 20px;
          padding: 15px;
          background: #f0f8ff;
          border-left: 4px solid #3498db;
          border-radius: 5px;
        }

        .dialogue-line {
          margin-bottom: 10px;
          display: flex;
          flex-direction: column;
        }

        .dialogue-speaker {
          font-weight: bold;
          color: #e74c3c;
          margin-bottom: 3px;
        }

        .dialogue-text {
          color: #444;
          font-style: italic;
          margin-left: 10px;
        }

        .page-number-left, .page-number-right {
          position: absolute;
          bottom: 10px;
          font-size: 0.9rem;
          color: #999;
        }

        .page-number-left {
          left: 20px;
        }

        .page-number-right {
          right: 20px;
        }

        @media (max-width: 1024px) {
          .story-spread {
            grid-template-columns: 1fr;
            gap: 0;
          }

          .page-left {
            border-right: none;
            border-bottom: 2px dashed #ddd;
          }
        }
      `}</style>
    </div>
  );
};

export default StoryBookViewer;
