# Pre-loading Local SD as Backup

## Overview

The system now **automatically pre-loads local Stable Diffusion** on startup when using Stability AI as the primary backend. This eliminates any delay when fallback occurs.

---

## Implementation

### File: `backend/main.py`

**Lines 29-41:**

```python
# Pre-load local SD as backup when using Stability AI
if settings.image_backend == "stability_ai":
    logger.info("Pre-loading local Stable Diffusion as backup for Stability AI fallback...")
    try:
        from services.image_generator import image_generator
        if not image_generator.is_loaded():
            image_generator.load_model()
            logger.info("Local Stable Diffusion backup loaded successfully")
        else:
            logger.info("Local Stable Diffusion already loaded")
    except Exception as e:
        logger.warning(f"Failed to pre-load local SD backup: {e}")
        logger.warning("Fallback will load on-demand if needed")
```

---

## How It Works

### Startup Sequence

When `IMAGE_BACKEND=stability_ai` in `.env`:

1. **Load Stability AI** (primary backend)
   ```
   INFO - Starting up application...
   INFO - Stability AI API configured successfully
   INFO - Models loaded successfully (backend: stability_ai)
   ```

2. **Pre-load Local SD** (backup)
   ```
   INFO - Pre-loading local Stable Diffusion as backup for Stability AI fallback...
   INFO - Loading Stable Diffusion model...
   INFO - Stable Diffusion model loaded to device: cuda
   INFO - Local Stable Diffusion backup loaded successfully
   ```

3. **Ready for instant fallback**
   - Both models are now in memory
   - Fallback happens with **zero delay**
   - No model loading when credits run out

---

## Benefits

### ⚡ Zero-Delay Fallback
- No waiting when Stability AI credits run out
- Instant switch to local SD
- Seamless user experience

### 🧠 Smart Loading
- Only loads backup when using Stability AI
- Checks if already loaded (no duplicate loading)
- Graceful failure handling

### 📊 Memory Efficiency
When `IMAGE_BACKEND=local_diffusion`:
- Only local SD loads (no Stability AI, no backup)

When `IMAGE_BACKEND=stability_ai`:
- Both Stability AI and local SD load
- Worth the memory for instant fallback

---

## Memory Usage

### Before Pre-loading
- **Stability AI:** ~0 MB (API-based, no local model)
- **Local SD:** ~0 MB (loads on first fallback)
- **Total:** ~0 MB

### After Pre-loading
- **Stability AI:** ~0 MB (API-based)
- **Local SD:** ~4-6 GB VRAM (model loaded in GPU)
- **Total:** ~4-6 GB VRAM

**Worth it?** ✅ Yes!
- Instant fallback = better UX
- Modern GPUs have 8-16+ GB VRAM
- Can always disable if memory is tight

---

## Disabling Pre-loading

If you want to disable pre-loading (to save memory):

**Option 1: Comment out the code**
```python
# In backend/main.py lines 29-41
# if settings.image_backend == "stability_ai":
#     logger.info("Pre-loading local Stable Diffusion as backup...")
#     ...
```

**Option 2: Add a config flag**
```python
# In config.py
preload_sd_backup: bool = True  # Set to False to disable

# In main.py
if settings.image_backend == "stability_ai" and settings.preload_sd_backup:
    # Pre-load local SD...
```

---

## Error Handling

### If Pre-loading Fails

```
WARNING - Failed to pre-load local SD backup: Model files not found
WARNING - Fallback will load on-demand if needed
```

The app still works:
- Stability AI functions normally
- First fallback will load local SD (with delay)
- Subsequent fallbacks are instant

### If GPU Memory Is Full

Local SD will try CPU instead:
```
INFO - CUDA out of memory, falling back to CPU
INFO - Stable Diffusion model loaded to device: cpu
```

CPU generation is slower but still works.

---

## Testing

### Verify Pre-loading Works

**Step 1: Start the server**
```bash
cd backend
python main.py
```

**Step 2: Check logs**
You should see:
```
INFO - Starting up application...
INFO - Models loaded successfully (backend: stability_ai)
INFO - Pre-loading local Stable Diffusion as backup for Stability AI fallback...
INFO - Stable Diffusion model loaded to device: cuda
INFO - Local Stable Diffusion backup loaded successfully
```

**Step 3: Test fallback**
- Simulate Stability AI error (use invalid API key)
- Generate a storybook
- Should fallback instantly without loading delay

---

## Performance Impact

### Startup Time
- **Before:** ~2-5 seconds (Stability API check only)
- **After:** ~10-30 seconds (Stability + local SD loading)
- **Acceptable?** Yes - only happens once at startup

### Runtime Performance
- **No impact** - models are pre-loaded
- Fallback is instant
- No performance difference during generation

### Memory Usage
- **+4-6 GB VRAM** for local SD model
- Modern GPUs can handle it
- Can disable if memory constrained

---

## Summary

Pre-loading local SD provides:

✅ **Instant fallback** - zero delay when Stability AI fails
✅ **Better UX** - users never wait for model loading
✅ **Smart loading** - only when using Stability AI backend
✅ **Graceful degradation** - still works if pre-loading fails

**Trade-off:**
- ⬆️ Startup time: +10-30 seconds (one-time)
- ⬆️ Memory usage: +4-6 GB VRAM
- ⬇️ First-fallback delay: 0 seconds (instant)

**Verdict:** ✅ Worth it for production!

**Status: ✅ Implemented and Active**
