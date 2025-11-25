# ChatGPT-Style Inline Text Editing

## Overview

The storybook viewer now supports **ChatGPT-style inline editing** powered by AI. Users can select any text in the storybook and edit it with natural language instructions.

---

## Features

### 1. **Text Selection Editing**
- Select any word, phrase, sentence, or paragraph in the narration
- A floating "✨ Edit with AI" button appears near the selection
- Click it to open the edit modal
- Enter natural language instructions like:
  - "make it simpler"
  - "make it more exciting"
  - "use shorter sentences"
  - "add more emotion"

### 2. **Dialogue Editing**
- Select any part of a dialogue line
- Same floating button appears
- Edit dialogue with instructions like:
  - "make it funnier"
  - "make it more formal"
  - "shorten it"
  - "add surprise"

### 3. **Real-time Updates**
- Edited text replaces the original text immediately
- Changes are preserved in the storybook state
- No page reload required

---

## Implementation

### Frontend Components

#### 1. **EditableText Component**
Location: `frontend/src/components/common/EditableText.tsx`

**Props:**
- `text: string` - The text to display and edit
- `onTextChange: (newText: string) => void` - Callback when text is edited
- `context: string` - Context for the AI (e.g., "Narration on page 2 of story 'Elephant's Brushstrokes'")
- `className?: string` - Optional CSS class

**Usage:**
```tsx
<EditableText
  text={page.narration}
  onTextChange={(newText) => handleNarrationChange(page.page_number, newText)}
  context={`Narration on page ${page.page_number} of story "${storybook.meta.title}"`}
  className="page-narration"
/>
```

#### 2. **EditableDialogue Component**
Location: `frontend/src/components/common/EditableDialogue.tsx`

**Props:**
- `speaker: string` - Character name
- `text: string` - Dialogue text
- `onTextChange: (newText: string) => void` - Callback when text is edited
- `context: string` - Page context

**Usage:**
```tsx
<EditableDialogue
  speaker={dialogue.speaker}
  text={dialogue.text}
  onTextChange={(newText) => handleDialogueChange(page.page_number, idx, newText)}
  context={`Page ${page.page_number} of story "${storybook.meta.title}"`}
/>
```

#### 3. **Updated StoryBookViewer**
Location: `frontend/src/components/StoryMode/StoryBookViewer.tsx`

**Changes:**
- Now uses `useState` to manage editable storybook state
- Replaced static text with `EditableText` and `EditableDialogue` components
- Added `handleNarrationChange` and `handleDialogueChange` handlers

---

## Backend API

### Endpoint: `POST /api/edit_text_segment`

**Request:**
```json
{
  "original_text": "the text the user selected",
  "instruction": "make it simpler / happier / shorter",
  "context": "narration on page 2, story 'Elephant's Brushstrokes'"
}
```

**Response:**
```json
{
  "edited_text": "the AI-edited version of the text"
}
```

**Implementation:**
- Uses the Text Editor Agent (`text_editor_agent.edit_text()`)
- Accepts context to maintain story consistency
- Returns edited text that replaces the original selection

---

## User Experience Flow

1. **User reads storybook** → Sees generated narration and dialogues

2. **User selects text** → Highlights a word, phrase, or sentence

3. **Edit button appears** → Floating "✨ Edit with AI" button shows near selection

4. **User clicks button** → Modal opens showing:
   - Selected text preview
   - "How should I change this?" input field
   - Cancel and Apply buttons

5. **User enters instruction** → e.g., "make it more exciting"

6. **AI processes request** → Calls `/api/edit_text_segment` with:
   - Original selected text
   - User instruction
   - Page and story context

7. **Text updates in place** → Selected text is replaced with edited version

8. **User continues editing** → Can select and edit other text segments

---

## Visual Design

### Edit Button Styling
- **Gradient background**: Purple-blue gradient (`#667eea` to `#764ba2`)
- **Floating effect**: Positioned absolutely near selection
- **Hover animation**: Slight lift and shadow increase
- **Icon**: ✨ sparkle emoji for AI association

### Modal Styling
- **Centered overlay**: Dark semi-transparent background
- **White card**: Rounded corners, drop shadow
- **Selected text preview**: Light gray background with colored left border
- **Input field**: Clean, modern design with focus state
- **Action buttons**: Gradient submit button, gray cancel button

### Selection Highlighting
- **Narration**: Blue highlight (`#b3d9ff`)
- **Dialogue**: Pink highlight (`#ffe6f0`)

---

## Technical Details

### Text Selection Detection
```typescript
const handleMouseUp = () => {
  const selection = window.getSelection();
  if (!selection || selection.isCollapsed) return;

  const selected = selection.toString().trim();
  // Position button near selection
  const range = selection.getRangeAt(0);
  const rect = range.getBoundingClientRect();
  // Show floating button
};
```

### Text Replacement
```typescript
const handleSubmitEdit = async () => {
  const response = await apiClient.editTextSegment({
    original_text: selectedText,
    instruction: instruction.trim(),
    context,
  });

  // Replace selected text with edited text
  const newText = text.replace(selectedText, response.edited_text);
  onTextChange(newText);
};
```

---

## Error Handling

1. **Empty instruction**: Shows error message "Please provide editing instructions"
2. **API failure**: Shows error message "Failed to edit text. Please try again."
3. **Invalid selection**: Button doesn't appear if selection is outside editable area

---

## Future Enhancements

### Potential Additions:
1. **Undo/Redo**: Track edit history for reverting changes
2. **Suggested edits**: Show common editing options (simplify, expand, shorten)
3. **Batch editing**: Edit multiple selections at once
4. **Export edited version**: Download the edited storybook
5. **Highlight changes**: Show what was edited with diff highlighting
6. **Edit page title**: Make page titles editable too
7. **Character consistency**: Ensure character names remain consistent across edits

---

## Testing Checklist

- [ ] Select narration text → Edit button appears
- [ ] Select dialogue text → Edit button appears
- [ ] Click edit button → Modal opens
- [ ] Enter instruction and submit → Text updates correctly
- [ ] Cancel modal → No changes made
- [ ] Empty instruction → Error shown
- [ ] API failure → Error shown gracefully
- [ ] Multiple edits on same page → All work correctly
- [ ] Edit on different pages → Each page maintains its state
- [ ] Long selections → Button positioned correctly
- [ ] Short selections (single word) → Works correctly

---

## Files Modified/Created

### Created:
1. `frontend/src/components/common/EditableText.tsx` - Editable narration component
2. `frontend/src/components/common/EditableDialogue.tsx` - Editable dialogue component
3. `INLINE_EDITING.md` - This documentation

### Modified:
1. `frontend/src/components/StoryMode/StoryBookViewer.tsx` - Integrated editable components

### Already Existed (Reused):
1. `backend/api/routes.py` - `POST /edit_text_segment` endpoint
2. `backend/agents/text_editor_agent.py` - Text editing logic
3. `frontend/src/services/api.ts` - API client method
4. `frontend/src/types/index.ts` - Request/response types

---

## Summary

The inline editing feature brings **ChatGPT-style editing** to the storybook viewer, allowing users to:
- 📝 Select any text (narration or dialogue)
- ✨ Click "Edit with AI" button
- 💬 Provide natural language instructions
- 🎯 See instant updates

This makes storybook refinement intuitive and interactive, without requiring full regeneration.

**Implementation Status: ✅ Complete**
