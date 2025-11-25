# Automatic Fallback: Stability AI → Local Stable Diffusion

## Overview

The image generation pipeline now includes **automatic fallback** from Stability AI to local Stable Diffusion when credits run out. Users will **never see balance errors** - the system seamlessly switches to local generation.

---

## How It Works

### Detection
When Stability AI API returns an error, the system checks for:

**Status Codes:**
- `400` - Bad Request (with balance message)
- `402` - Payment Required
- `403` - Forbidden (insufficient credits)
- `429` - Too Many Requests (rate limit due to credits)

**Error Messages containing:**
- "not have enough balance"
- "insufficient balance"
- "not enough credits"
- "grant"

### Automatic Fallback Flow

```
1. User requests image generation
   ↓
2. System tries Stability AI first
   ↓
   [If Stability AI succeeds]
   ↓
3. ✅ Return Stability AI image

   [If Stability AI returns insufficient balance error]
   ↓
4. ⚠️  Catch StabilityInsufficientBalanceError
   ↓
5. 📝 Log warning: "Stability AI credits exhausted"
   ↓
6. 🔄 Check if local SD is loaded
   ↓
7. 📥 Load local SD model if needed
   ↓
8. 🎨 Generate with local Stable Diffusion
   ↓
9. ✅ Return local SD image
   ↓
10. User gets image (never sees error!)
```

---

## Implementation Details

### 1. Custom Exception

**File:** `backend/core/exceptions.py`

```python
class StabilityInsufficientBalanceError(Exception):
    """Raised when Stability AI API returns insufficient balance/credits error."""
    pass
```

### 2. Error Detection in Stability AI Service

**File:** `backend/services/stability_ai_image.py`

**Lines 105-134:**
```python
if response.status_code != 200:
    # Try to get detailed error message
    error_msg = response.text
    try:
        error_data = response.json()
        error_msg = error_data.get('message', response.text)
    except:
        pass

    # Check for insufficient balance conditions
    balance_indicators = [
        "not have enough balance",
        "insufficient balance",
        "not enough credits",
        "grant"
    ]

    error_msg_lower = error_msg.lower()
    is_balance_error = any(indicator in error_msg_lower for indicator in balance_indicators)

    # Raise insufficient balance error for credit-related issues
    if response.status_code in [400, 402, 403, 429] and is_balance_error:
        raise StabilityInsufficientBalanceError(f"Stability AI insufficient balance: {error_msg}")

    # For 402/403/429 without clear balance message, also assume it's balance-related
    if response.status_code in [402, 403, 429]:
        raise StabilityInsufficientBalanceError(f"Stability AI credit/balance issue: {error_msg}")

    # Other errors
    raise AIGenerationError(f"Stability AI API error: {error_msg}")
```

**Applied to both methods:**
- `generate_image()` - Text-to-image generation
- `generate_image_with_reference()` - Image-to-image generation

### 3. Fallback Logic in Unified Service

**File:** `backend/services/unified_image_service.py`

**For text-to-image (lines 87-114):**
```python
if self.backend == "stability_ai":
    try:
        # Map width/height to aspect ratio for Stability AI
        aspect_ratio = self._get_aspect_ratio(width, height)
        return stability_ai_generator.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio,
            number_of_images=1
        )
    except StabilityInsufficientBalanceError as e:
        # Automatically fallback to local Stable Diffusion when credits run out
        logger.warning(f"Stability AI credits exhausted: {e}")
        logger.info("Falling back to local Stable Diffusion for image generation")

        # Ensure local SD is loaded
        if not image_generator.is_loaded():
            logger.info("Loading local Stable Diffusion model...")
            image_generator.load_model()

        # Generate with local SD
        return image_generator.generate_image(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height
        )
```

**For image-to-image (lines 167-194):**
```python
if self.backend == "stability_ai":
    try:
        # Stability AI supports image-to-image
        return stability_ai_generator.generate_image_with_reference(
            prompt=prompt,
            reference_image_path=reference_image,
            negative_prompt=negative_prompt,
            style_strength=0.6
        )
    except StabilityInsufficientBalanceError as e:
        # Automatically fallback to local Stable Diffusion when credits run out
        logger.warning(f"Stability AI credits exhausted during reference generation: {e}")
        logger.info("Falling back to local Stable Diffusion for image generation")

        # Ensure local SD is loaded
        if not image_generator.is_loaded():
            logger.info("Loading local Stable Diffusion model...")
            image_generator.load_model()

        # Fallback to regular text-to-image with local SD
        logger.info("Note: Local SD doesn't support reference images, using text-to-image")
        return image_generator.generate_image(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height
        )
```

---

## User Experience

### Before (Without Fallback)
```
User: "Generate a storybook about elephants"
System: ❌ Story generation failed: Stability AI API error: You do not have enough balance
User: 😞 (sees error, must manually switch to local SD)
```

### After (With Fallback)
```
User: "Generate a storybook about elephants"
System:
  - ⚠️  [Internal log] Stability AI credits exhausted
  - 🔄 [Internal log] Falling back to local Stable Diffusion
  - 📥 [Internal log] Loading local SD model...
  - 🎨 Generating images with local SD...
  - ✅ Returns complete storybook
User: 😊 (gets storybook, never sees error!)
```

---

## Logging

When fallback occurs, the logs show:

```
WARNING - Stability AI credits exhausted: Stability AI insufficient balance: You do not have enough balance
INFO - Falling back to local Stable Diffusion for image generation
INFO - Loading local Stable Diffusion model...
INFO - Stable Diffusion model loaded to device: cuda
INFO - Image generated with Stable Diffusion: {filename}
```

---

## Edge Cases Handled

### 1. Local SD Not Loaded
If local SD isn't loaded when fallback occurs:
```python
if not image_generator.is_loaded():
    logger.info("Loading local Stable Diffusion model...")
    image_generator.load_model()
```

### 2. Image-to-Image Fallback
Local SD doesn't support reference images, so it falls back to text-to-image:
```python
logger.info("Note: Local SD doesn't support reference images, using text-to-image")
return image_generator.generate_image(prompt, ...)
```

### 3. Other Stability AI Errors
Non-balance errors (network issues, invalid prompts, etc.) still raise `AIGenerationError` normally:
```python
# Other errors
raise AIGenerationError(f"Stability AI API error: {error_msg}")
```

---

## Testing the Fallback

### Scenario 1: Insufficient Balance
**Stability AI returns:**
```json
{
  "status": 403,
  "message": "You do not have enough balance to complete this request."
}
```

**System behavior:**
1. Catches `StabilityInsufficientBalanceError`
2. Logs warning
3. Loads local SD
4. Generates with local SD
5. ✅ Returns image successfully

### Scenario 2: Rate Limit Due to Credits
**Stability AI returns:**
```json
{
  "status": 429,
  "message": "Rate limit exceeded - insufficient credits"
}
```

**System behavior:**
1. Detects status 429 + balance error
2. Catches `StabilityInsufficientBalanceError`
3. Falls back to local SD
4. ✅ Returns image successfully

### Scenario 3: Generic 400 Error (Non-balance)
**Stability AI returns:**
```json
{
  "status": 400,
  "message": "Invalid prompt: prompt too long"
}
```

**System behavior:**
1. Checks for balance indicators
2. None found
3. Raises `AIGenerationError` (not balance-related)
4. ❌ User sees error (as intended - this is a prompt issue, not balance)

---

## Files Modified

### Created:
1. `AUTOMATIC_FALLBACK.md` - This documentation

### Modified:
1. **`backend/services/stability_ai_image.py`**
   - Added `StabilityInsufficientBalance` exception class (lines 15-17)
   - Updated `generate_image()` method (lines 105-134)
   - Updated `generate_image_with_reference()` method (lines 204-234)
   - Added error detection logic for balance issues

2. **`backend/services/unified_image_service.py`**
   - Imported `StabilityInsufficientBalance` exception (line 9)
   - Updated `generate_image()` method (lines 87-114)
   - Updated `_generate_with_reference()` method (lines 148-175)
   - Added try/catch with automatic fallback logic

3. **`backend/main.py`** ✨ NEW
   - Added automatic pre-loading of local SD on startup (lines 29-41)
   - Eliminates first-fallback delay
   - Only loads backup when `IMAGE_BACKEND=stability_ai`

---

## Configuration

No configuration changes needed! The fallback works automatically when:
- `IMAGE_BACKEND=stability_ai` is set in `.env`
- Stability AI credits run out

The system automatically uses local SD as backup.

---

## Benefits

✅ **Seamless user experience** - No balance errors visible to users

✅ **Automatic recovery** - System self-heals when credits run out

✅ **Zero downtime** - Service continues without interruption

✅ **Cost optimization** - Uses free local SD as backup

✅ **Transparent logging** - Developers can see when fallback occurs

✅ **Minimal code changes** - Only 3 files modified

---

## Production Recommendations

### 1. Monitor Logs
Watch for fallback warnings to know when to refill Stability AI credits:
```bash
grep "Stability AI credits exhausted" backend/logs/*.log
```

### 2. Pre-load Local SD ✅ IMPLEMENTED
Local SD is now **automatically pre-loaded on startup** when using Stability AI backend!

**Implementation:** [backend/main.py](backend/main.py#L29-L41)

On application startup, if `IMAGE_BACKEND=stability_ai`, the system:
1. Loads Stability AI (primary backend)
2. **Also pre-loads local Stable Diffusion** as backup
3. Fallback happens instantly with **zero delay**

**Startup logs show:**
```
INFO - Models loaded successfully (backend: stability_ai)
INFO - Pre-loading local Stable Diffusion as backup for Stability AI fallback...
INFO - Stable Diffusion model loaded to device: cuda
INFO - Local Stable Diffusion backup loaded successfully
```

### 3. Alert System (Optional)
Set up alerts when fallback occurs:
```python
# In unified_image_service.py
except StabilityInsufficientBalanceError as e:
    logger.warning(f"Stability AI credits exhausted: {e}")
    # Send alert to admin
    send_alert("Stability AI credits low - fallback active")
```

### 4. Credit Monitoring (Optional)
Add endpoint to check Stability AI balance:
```python
@app.get("/api/stability_balance")
async def get_stability_balance():
    # Check Stability AI account balance
    # Return warning if low
    pass
```

---

## Summary

The automatic fallback system provides **bulletproof image generation** by:

1. **Pre-loading** local SD on startup (when using Stability AI backend)
2. **Detecting** Stability AI balance errors (402/403/429 status or balance messages)
3. **Catching** `StabilityInsufficientBalance` exception
4. **Falling back** to local Stable Diffusion **instantly** (no loading delay)
5. **Returning** images seamlessly

Users never see "insufficient balance" errors - the system just works!

**Status: ✅ Automatic Fallback Implemented + Pre-loading Enabled**
