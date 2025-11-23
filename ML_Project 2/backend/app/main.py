from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models.generate_request import GenerateRequest
from .services.diffusion_engine import DiffusionEngine
from .services.orchestrator import ArtDirectorOrchestrator

app = FastAPI(title="Agentic AI Art Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = DiffusionEngine()
orchestrator = ArtDirectorOrchestrator(engine)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate")
def generate(req: GenerateRequest):
    image_path = orchestrator.handle_simple_request(req)
    return {
        "image_path": image_path,
        "prompt": req.prompt,
    }
