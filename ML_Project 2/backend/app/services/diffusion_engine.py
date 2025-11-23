import torch
from diffusers import StableDiffusionXLPipeline
from typing import Optional
from pathlib import Path
import uuid

class DiffusionEngine:
    def __init__(self, model_id: str = "stabilityai/stable-diffusion-xl-base-1.0", device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
        )
        if self.device == "cuda":
            self.pipe = self.pipe.to(self.device)

        self.output_dir = Path("generated")
        self.output_dir.mkdir(exist_ok=True)

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        width: int = 768,
        height: int = 768,
    ) -> str:
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            generator = torch.Generator(device=self.device)

        image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height,
            generator=generator,
        ).images[0]

        file_name = f"{uuid.uuid4().hex}.png"
        file_path = self.output_dir / file_name
        image.save(file_path)
        return str(file_path)
