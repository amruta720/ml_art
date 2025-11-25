# Dialogue Generation Improvements

## Overview

Enhanced the Story Text Agent to ensure consistent, high-quality dialogue generation in children's storybooks.

---

## Changes Made

### File: `backend/agents/story_text_agent.py`

#### 1. **Improved System Instructions** (Lines 18-104)

**Added Explicit Dialogue Requirements:**
```python
7. **IMPORTANT: Include dialogue on MOST pages.**
   - At least 70% of pages should have dialogue
   - Each page should have 1-3 dialogue lines
   - Use dialogue to show character emotions and relationships
   - Only skip dialogue if the scene is purely descriptive
   - dialogues must be an array with at least one object (not empty [])
```

**Added Second Example with Multi-Character Dialogue:**
```json
{
  "page_number": 2,
  "narration": "Ellie dips her paintbrush into the blue paint and sweeps it across a large canvas. A beautiful sky appears! Her forest friends gather around to watch, their eyes wide with wonder.",
  "dialogues": [
    {
      "speaker": "Squirrel",
      "text": "Wow, Ellie! You're making magic!"
    },
    {
      "speaker": "Birdie",
      "text": "Can you paint me flying in that sky?"
    },
    {
      "speaker": "Ellie",
      "text": "Of course! Let me add some clouds for you to play in."
    }
  ]
}
```

#### 2. **Enhanced User Prompt** (Lines 156-185)

**Added CRITICAL REQUIREMENTS Section:**
```
1. Include dialogue on at least 70% of pages
2. Make characters talk to express emotions, thoughts, and reactions
3. Use dialogue to advance the story and show relationships
4. Each dialogue line should reveal something about the character
5. Keep dialogue natural and age-appropriate
```

**Added In-Prompt Example:**
Included a concrete example directly in the generation prompt to guide the LLM:
```json
{
  "page_number": 1,
  "narration": "Luna the bunny hopped through the meadow...",
  "dialogues": [
    {"speaker": "Luna", "text": "Oh wow! Where did you come from, little balloon?"},
    {"speaker": "Balloon", "text": "I escaped from the birthday party! Want to come on an adventure?"}
  ]
}
```

**Added Reinforcement Reminder:**
```
REMEMBER: Most pages need dialogue! Characters should speak their feelings and thoughts.
```

#### 3. **Added Detailed Logging** (Lines 194-215)

**Dialogue Statistics Tracking:**
```python
pages_with_dialogue = 0
total_dialogue_lines = 0

for page in text_data["pages"]:
    if page["dialogues"] and len(page["dialogues"]) > 0:
        pages_with_dialogue += 1
        total_dialogue_lines += len(page["dialogues"])
        logger.info(f"Page {page['page_number']}: {len(page['dialogues'])} dialogue lines from {[d.get('speaker', '?') for d in page['dialogues']]}")
    else:
        logger.warning(f"Page {page['page_number']}: NO DIALOGUE (narration only)")

logger.info(f"Dialogue stats: {pages_with_dialogue}/{len(text_data['pages'])} pages have dialogue ({pages_with_dialogue/len(text_data['pages'])*100:.1f}%)")
logger.info(f"Total dialogue lines: {total_dialogue_lines}")
```

**Benefits:**
- See exactly which pages have dialogue
- Track percentage of pages with dialogue
- Identify speaker names used
- Quickly spot pages missing dialogue

---

## How It Works Now

### Before Improvements:
```
LLM Prompt: "Write narration and dialogue for each page."

Result: Often generated pages with empty dialogues or no character speech
```

### After Improvements:
```
LLM Prompt:
  - "IMPORTANT: Include dialogue on MOST pages (70%+)"
  - "Make characters talk to express emotions"
  - "Here's an example: [concrete JSON example]"
  - "REMEMBER: Characters should speak their feelings!"

Result: LLM generates rich, expressive dialogue on most pages
```

---

## Expected Output

### Example Log Output:
```
INFO - Generating text for 4 pages of 'Ellie's Big Adventure'
INFO - Story text generated for 4 pages
INFO - Page 1: 1 dialogue lines from ['Ellie']
INFO - Page 2: 3 dialogue lines from ['Squirrel', 'Birdie', 'Ellie']
INFO - Page 3: 2 dialogue lines from ['Ellie', 'Rabbit']
WARNING - Page 4: NO DIALOGUE (narration only)
INFO - Dialogue stats: 3/4 pages have dialogue (75.0%)
INFO - Total dialogue lines: 6
```

### Example Generated JSON:
```json
{
  "pages": [
    {
      "page_number": 1,
      "narration": "Ellie found a magical paintbrush in the forest...",
      "dialogues": [
        {
          "speaker": "Ellie",
          "text": "What beautiful colors! I can create anything!"
        }
      ]
    },
    {
      "page_number": 2,
      "narration": "Her friends gathered to watch her paint...",
      "dialogues": [
        {
          "speaker": "Squirrel",
          "text": "Can you paint me some acorns, Ellie?"
        },
        {
          "speaker": "Ellie",
          "text": "Of course! Let me paint you a whole oak tree!"
        },
        {
          "speaker": "Birdie",
          "text": "This is amazing! You're a true artist!"
        }
      ]
    }
  ]
}
```

---

## Testing

### 1. Generate a New Storybook

```bash
cd backend
python main.py
```

Then generate a storybook through the frontend or API.

### 2. Check the Logs

Look for:
```
INFO - Page 1: X dialogue lines from [...]
INFO - Dialogue stats: X/Y pages have dialogue (Z%)
```

### 3. Verify Frontend Display

- Open the storybook in the UI
- Check that dialogue boxes show:
  - **Speaker names** in red (e.g., "Ellie:", "Squirrel:")
  - **Dialogue text** in quotes (e.g., "What beautiful colors!")
- No more empty `""` strings

### 4. Test Inline Editing

- Select any dialogue text
- Click "✨ Edit with AI"
- Enter instruction: "make it more excited"
- Verify the dialogue updates

---

## Troubleshooting

### Issue: Still seeing empty dialogues

**Possible causes:**
1. **LLM model is too small** - Try a larger model:
   ```bash
   # In backend/.env
   OLLAMA_MODEL=llama3:8b  # Instead of llama3.2:3b
   ```

2. **Temperature too low** - The agent uses `temperature=0.7` which is good for creative dialogue

3. **LLM not following instructions** - Check if Ollama is running:
   ```bash
   ollama list
   ollama ps
   ```

### Issue: Dialogue exists but shows as `""`

**Cause:** The `text` field is an empty string.

**Fix:** Check the logs to see what the LLM actually generated:
```python
# In story_text_agent.py, line 189
logger.debug(f"Raw LLM response: {response_text}")
```

### Issue: JSON parsing errors

**Cause:** LLM generating invalid JSON.

**Check:** Look for:
```
WARNING - Initial JSON parse failed: ...
```

**Fix:** The `clean_and_parse_json` utility should handle most issues automatically.

---

## Best Practices

### 1. **Character-Driven Stories**
When generating stories, specify characters upfront:
```json
{
  "story_idea": "An elephant learns to paint",
  "num_pages": 4,
  "age_range": "4-7"
}
```

The Story Draft Agent creates character descriptions, which are then used by the Story Text Agent to generate dialogue.

### 2. **Monitor Dialogue Percentage**
Aim for **70%+ of pages with dialogue**. If you see less, it might indicate:
- LLM not following instructions
- Story outline doesn't involve character interactions
- Need to adjust prompts further

### 3. **Review Generated Dialogues**
Use the inline editing feature to:
- Make dialogue more emotional: "make it more excited"
- Simplify language: "make it simpler for 4-year-olds"
- Add personality: "make it funnier"

---

## Summary

**Before:**
- ❌ Many pages had empty `dialogues: []` arrays
- ❌ No clear guidance for LLM on dialogue requirements
- ❌ No visibility into dialogue generation success

**After:**
- ✅ Explicit requirement: 70%+ pages must have dialogue
- ✅ Concrete examples in system instructions and user prompts
- ✅ Detailed logging shows dialogue statistics per page
- ✅ LLM receives multiple reminders to include dialogue
- ✅ In-prompt example guides the format

**Result:** Rich, expressive character dialogue in children's storybooks! 🎉

---

## Files Modified

1. **`backend/agents/story_text_agent.py`**
   - Enhanced system instructions (lines 18-104)
   - Improved user prompt (lines 156-185)
   - Added dialogue logging (lines 194-215)

---

**Status: ✅ Dialogue Generation Enhanced**
