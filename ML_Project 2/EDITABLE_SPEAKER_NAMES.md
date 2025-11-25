# Editable Speaker Names Implementation

## Overview

Extended the inline editing functionality to allow users to edit character names (speaker names) in dialogue lines, in addition to editing the dialogue text itself.

---

## What Was Added

### Feature: Click-to-Edit Speaker Names

Users can now click on any speaker name in a dialogue line to edit it directly.

**User Experience:**
1. User sees: **Ellie:** "What beautiful colors!"
2. User clicks "Ellie" → input field appears
3. User edits: "Luna"
4. User presses Enter or clicks outside → saves
5. Updated dialogue shows: **Luna:** "What beautiful colors!"

---

## Files Modified

### 1. `frontend/src/components/common/InlineEditableDialogue.tsx`

#### Added Props
```typescript
interface InlineEditableDialogueProps {
  speaker: string;
  text: string;
  onTextChange: (newText: string) => void;
  onSpeakerChange: (newSpeaker: string) => void;  // NEW
  context: string;
}
```

#### Added State
```typescript
const [localSpeaker, setLocalSpeaker] = useState(speaker);
const [isEditingSpeaker, setIsEditingSpeaker] = useState(false);
const speakerInputRef = useRef<HTMLInputElement>(null);
```

#### Added Functions
```typescript
// Sync speaker with prop changes
useEffect(() => {
  setLocalSpeaker(speaker);
}, [speaker]);

// Auto-focus speaker input when entering edit mode
useEffect(() => {
  if (isEditingSpeaker && speakerInputRef.current) {
    speakerInputRef.current.focus();
    speakerInputRef.current.select();
  }
}, [isEditingSpeaker]);

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
```

#### Updated Render
```tsx
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
```

#### Added Styles
```css
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
```

---

### 2. `frontend/src/components/StoryMode/StoryBookViewer.tsx`

#### Added Handler Function
```typescript
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
```

#### Updated Component Usage
```tsx
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
```

---

## Features

### Visual Feedback
- **Hover effect**: Speaker name highlights with pink background when hovering
- **Tooltip**: "Click to edit speaker name" appears on hover
- **Edit mode**: Input field appears with red border and focus shadow
- **Cursor**: Pointer cursor on speaker name indicates it's clickable

### Keyboard Shortcuts
- **Enter**: Save changes and exit edit mode
- **Escape**: Cancel changes and revert to original speaker name
- **Tab**: (Browser default) Move to next focusable element

### Validation
- **Empty names prevented**: If user deletes all text and saves, the original name is restored
- **Whitespace trimmed**: Leading/trailing spaces are automatically removed
- **Auto-focus**: Input field is focused and text is selected when entering edit mode

### State Management
- **Local state**: Changes are tracked locally until saved
- **Prop sync**: When parent updates the speaker prop, local state syncs automatically
- **Immutable updates**: State updates use immutable patterns for React optimization

---

## How It Works

### State Flow

```
User clicks speaker name
    ↓
isEditingSpeaker = true
    ↓
Input field renders with localSpeaker value
    ↓
User edits speaker name
    ↓
localSpeaker state updates
    ↓
User presses Enter or clicks outside (blur)
    ↓
handleSpeakerBlur() fires
    ↓
Validates and trims input
    ↓
Calls onSpeakerChange(newSpeaker)
    ↓
StoryBookViewer.handleSpeakerChange() updates storybook state
    ↓
React re-renders with new speaker name
    ↓
Component receives new speaker prop
    ↓
useEffect syncs localSpeaker with prop
```

---

## Testing

### Manual Testing Steps

1. **Start the application:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python main.py

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

2. **Generate a storybook** with dialogues

3. **Test speaker editing:**
   - Hover over a speaker name → should see pink highlight
   - Click the speaker name → input field appears
   - Type a new name
   - Press Enter → should save
   - Click the speaker name again → should show the new name

4. **Test validation:**
   - Click speaker name
   - Delete all text
   - Press Enter → should revert to original name
   - Edit again and add spaces: "  Luna  "
   - Press Enter → should trim to "Luna"

5. **Test keyboard shortcuts:**
   - Click speaker name
   - Edit text
   - Press Escape → should cancel and revert
   - Edit again
   - Press Enter → should save

6. **Test with dialogue text editing:**
   - Click speaker name → edit it
   - Click dialogue text → edit it
   - Both should save independently

---

## Integration with Existing Features

### Works Alongside:
1. **Dialogue text editing** - Edit text by clicking the dialogue quotes
2. **AI-powered editing** - Select dialogue text for AI transformation
3. **Narration editing** - Double-click narration to edit manually
4. **Auto-save behavior** - All edits save on blur

### State Management:
- Speaker changes update the same storybook state object
- Changes are tracked in React state (not persisted to backend yet)
- All dialogue editing features work together seamlessly

---

## Code Quality

### TypeScript
- ✅ Fully typed with TypeScript interfaces
- ✅ No TypeScript compilation errors
- ✅ Type-safe callbacks and props

### React Best Practices
- ✅ Proper hooks usage (`useState`, `useEffect`, `useRef`)
- ✅ Immutable state updates
- ✅ Event handler memoization (implicitly via function definitions)
- ✅ Controlled components pattern
- ✅ Clean separation of concerns

### Accessibility
- ✅ Keyboard navigation support (Enter, Escape, Tab)
- ✅ Visual feedback (hover, focus states)
- ✅ Tooltip for discoverability
- ✅ Auto-focus on edit mode entry
- ✅ Text selection on focus

---

## Comparison: Before vs After

### Before This Implementation

| Feature | Status |
|---------|--------|
| Edit dialogue text manually | ✅ |
| Edit dialogue text with AI | ✅ |
| Edit speaker name | ❌ |
| Visual feedback for speaker | ❌ |

### After This Implementation

| Feature | Status |
|---------|--------|
| Edit dialogue text manually | ✅ |
| Edit dialogue text with AI | ✅ |
| Edit speaker name | ✅ **NEW** |
| Visual feedback for speaker | ✅ **NEW** |
| Click-to-edit speaker | ✅ **NEW** |
| Keyboard shortcuts for speaker | ✅ **NEW** |
| Empty name validation | ✅ **NEW** |
| Hover tooltip for speaker | ✅ **NEW** |

---

## User Guide

### How to Edit a Speaker Name

1. **Locate the dialogue** you want to edit
2. **Click the speaker name** (the bold red text before the colon)
3. An input field will appear
4. **Type the new name** for the character
5. **Press Enter** or **click outside** to save
6. **Press Escape** to cancel without saving

### Example

**Original:**
> **Ellie:** "What beautiful colors!"

**After editing speaker name to "Luna":**
> **Luna:** "What beautiful colors!"

---

## Next Steps (Optional)

1. **Add persistence** - Save speaker name changes to backend
2. **Add undo/redo** - Track speaker name changes in history
3. **Add character validation** - Ensure speaker names match story characters
4. **Add bulk rename** - Rename all instances of a character name at once
5. **Add character suggestions** - Dropdown of existing characters when editing

---

## Summary

**Status: ✅ Editable Speaker Names Fully Implemented**

**Features Added:**
- ✅ Click-to-edit speaker names
- ✅ Visual hover feedback
- ✅ Auto-focus and text selection
- ✅ Keyboard shortcuts (Enter, Escape)
- ✅ Empty name validation
- ✅ State management integration
- ✅ TypeScript type safety
- ✅ Smooth CSS transitions

**Files Modified:**
1. `frontend/src/components/common/InlineEditableDialogue.tsx`
2. `frontend/src/components/StoryMode/StoryBookViewer.tsx`

**Ready for use!** 🎉

Users can now edit both the speaker names and dialogue text, giving them full control over the story dialogue content.
