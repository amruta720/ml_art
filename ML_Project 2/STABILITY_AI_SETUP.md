# Stability AI Setup Guide

## What is Stability AI?

Stability AI offers **SDXL** (Stable Diffusion XL) - a powerful cloud-based image generation API that produces high-quality images quickly. It's much easier to set up than Google Vertex AI!

---

## Why Use Stability AI?

✅ **High Quality**: SDXL produces professional-grade images
✅ **Fast**: Cloud-based, faster than local generation
✅ **Easy Setup**: Just need an API key
✅ **Affordable**: Pay-as-you-go pricing
✅ **Supports Negative Prompts**: Better control over output
✅ **Multiple Aspect Ratios**: 1:1, 16:9, 9:16, 4:3, 3:4, etc.

---

## Step 1: Get Your API Key

1. Go to https://platform.stability.ai/account/keys
2. Sign up for an account (you'll get free credits to start!)
3. Click "Create API Key"
4. Copy your API key (starts with `sk-...`)

---

## Step 2: Configure Your Backend

Edit `backend/.env` and add your API key:

```bash
# Image Generation Backend
IMAGE_BACKEND=stability_ai

# Stability AI API Key
STABILITY_API_KEY=sk-your-actual-api-key-here
```

---

## Step 3: Install Dependencies

```bash
cd backend
pip install requests
```

(Requests should already be installed, but just in case!)

---

## Step 4: Restart Backend

```bash
python main.py
```

You should see:
```
INFO: Stability AI model loaded
INFO: Models loaded successfully (backend: stability_ai)
```

---

## Step 5: Test It!

Go to your frontend (http://localhost:5173) and:
1. Try Image Mode or Storybook Mode
2. Images will now be generated using Stability AI SDXL
3. Enjoy the faster, high-quality results! 🎨

---

## Pricing

- **Free Credits**: New accounts get free credits
- **Pay-as-you-go**: After free credits
- **Cost**: ~$0.002-0.01 per image (very affordable!)
- Check latest pricing: https://platform.stability.ai/pricing

---

## Features Supported

### ✅ Supported:
- Text-to-image generation
- Negative prompts (avoid unwanted elements)
- Multiple aspect ratios
- High resolution (up to 1536x1536)
- Style controls

### ❌ Not Directly Supported:
- Image-to-image (could be added if needed)
- Inpainting (could be added if needed)

---

## Switching Between Backends

You can easily switch between backends by changing `IMAGE_BACKEND` in `.env`:

### Local Stable Diffusion (Free, Offline)
```bash
IMAGE_BACKEND=local_diffusion
```

### Stability AI Cloud (Fast, High Quality)
```bash
IMAGE_BACKEND=stability_ai
STABILITY_API_KEY=sk-your-key
```

No code changes needed - just update `.env` and restart!

---

## Troubleshooting

**Problem**: "STABILITY_API_KEY not found"
- **Solution**: Make sure you added it to `backend/.env` file

**Problem**: "API error: 401 Unauthorized"
- **Solution**: Check your API key is correct and active

**Problem**: "API error: 402 Payment Required"
- **Solution**: You've used all your free credits. Add payment method at https://platform.stability.ai/account/billing

**Problem**: "API error: 400 Bad Request"
- **Solution**: Check the logs for details. Prompt might be too long or contain forbidden content

---

## Example Output

With Stability AI SDXL, you'll get:
- **Higher quality** images than local SD 1.5
- **Better details** and coherence
- **Faster generation** (no local GPU needed)
- **Consistent results** across runs

Perfect for creating professional storybooks! 📚✨

---

## API Documentation

For advanced usage:
- API Docs: https://platform.stability.ai/docs/api-reference
- Models: https://platform.stability.ai/docs/getting-started/models
- Examples: https://platform.stability.ai/docs/getting-started/text-to-image

---

**Enjoy your cloud-powered image generation!** 🚀
