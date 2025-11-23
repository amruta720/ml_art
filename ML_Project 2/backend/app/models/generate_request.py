from pydantic import BaseModel
from typing import Optional

class GenerateRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    steps: int = 30
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    width: int = 768
    height: int = 768
