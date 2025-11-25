"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from api.routes import router
from services.unified_image_service import unified_image_service
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("Starting up application...")
    try:
        unified_image_service.load_model()
        logger.info(f"Models loaded successfully (backend: {settings.image_backend})")

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

    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        logger.warning("Application starting without models loaded")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="Agentic AI Art Generator & Storybook Editor",
    description="Generate images and storybooks using Stable Diffusion and LLM agents",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(router, prefix="/api", tags=["AI Generation"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Agentic AI Art Generator & Storybook Editor API",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
