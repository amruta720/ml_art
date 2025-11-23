from .diffusion_engine import DiffusionEngine
from ..models.generate_request import GenerateRequest

class ArtDirectorOrchestrator:
    def __init__(self, engine: DiffusionEngine):
        self.engine = engine

    def handle_simple_request(self, req: GenerateRequest) -> str:
        prompt = req.prompt.strip()

        steps = req.steps
        guidance = req.guidance_scale
        if "cinematic" in prompt.lower():
            steps = max(steps, 35)
            guidance = max(guidance, 8.0)

        return self.engine.generate_image(
            prompt=prompt,
            negative_prompt=req.negative_prompt,
            num_inference_steps=steps,
            guidance_scale=guidance,
            seed=req.seed,
            width=req.width,
            height=req.height,
        )
