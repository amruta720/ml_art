"""Asset management service for uploaded files."""
import logging
import uuid
from pathlib import Path
from typing import List, Optional, Dict
from models.schemas import StoryAsset, AssetUsage

logger = logging.getLogger(__name__)


class AssetManager:
    """Manages uploaded assets and their metadata."""

    def __init__(self, storage_dir: str = "static/assets"):
        """Initialize the asset manager.

        Args:
            storage_dir: Directory to store uploaded assets
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # In-memory asset registry (in production, use a database)
        self._assets: Dict[str, StoryAsset] = {}

        logger.info(f"AssetManager initialized with storage: {self.storage_dir}")

    def register_asset(
        self,
        file_path: Path,
        filename: str,
        mime_type: str,
        usage: AssetUsage = AssetUsage.STYLE,
        description: Optional[str] = None
    ) -> StoryAsset:
        """Register a new asset.

        Args:
            file_path: Path to the uploaded file
            filename: Original filename
            mime_type: MIME type of the file
            usage: How the asset should be used
            description: Optional user description

        Returns:
            StoryAsset: Registered asset metadata
        """
        asset_id = str(uuid.uuid4())

        # Create relative URL for the asset
        relative_path = file_path.relative_to(Path.cwd())
        url = f"/{relative_path}"

        asset = StoryAsset(
            id=asset_id,
            url=url,
            filename=filename,
            mime_type=mime_type,
            usage=usage,
            description=description
        )

        self._assets[asset_id] = asset
        logger.info(f"Asset registered: {asset_id} ({filename})")

        return asset

    def get_asset(self, asset_id: str) -> Optional[StoryAsset]:
        """Get an asset by ID.

        Args:
            asset_id: Asset identifier

        Returns:
            StoryAsset or None if not found
        """
        return self._assets.get(asset_id)

    def get_assets(self, asset_ids: List[str]) -> List[StoryAsset]:
        """Get multiple assets by IDs.

        Args:
            asset_ids: List of asset identifiers

        Returns:
            List of StoryAsset objects (skips missing IDs)
        """
        assets = []
        for asset_id in asset_ids:
            asset = self.get_asset(asset_id)
            if asset:
                assets.append(asset)
            else:
                logger.warning(f"Asset not found: {asset_id}")
        return assets

    def get_assets_by_usage(
        self,
        asset_ids: List[str],
        usage: AssetUsage
    ) -> List[StoryAsset]:
        """Get assets filtered by usage type.

        Args:
            asset_ids: List of asset identifiers
            usage: Filter by this usage type

        Returns:
            List of matching assets
        """
        assets = self.get_assets(asset_ids)
        return [asset for asset in assets if asset.usage == usage]

    def build_asset_context(self, asset_ids: List[str]) -> str:
        """Build a text context description from assets for LLM prompts.

        Args:
            asset_ids: List of asset identifiers

        Returns:
            Formatted text describing the assets
        """
        if not asset_ids:
            return ""

        assets = self.get_assets(asset_ids)
        if not assets:
            return ""

        context_parts = []

        # Group by usage type
        style_assets = [a for a in assets if a.usage == AssetUsage.STYLE]
        character_assets = [a for a in assets if a.usage == AssetUsage.CHARACTER]
        story_assets = [a for a in assets if a.usage == AssetUsage.STORY_SOURCE]

        if style_assets:
            context_parts.append("VISUAL STYLE REFERENCES:")
            for asset in style_assets:
                desc = asset.description or f"Image: {asset.filename}"
                context_parts.append(f"- {desc}")

        if character_assets:
            context_parts.append("\nCHARACTER REFERENCES:")
            for asset in character_assets:
                desc = asset.description or f"Character image: {asset.filename}"
                context_parts.append(f"- {desc}")

        if story_assets:
            context_parts.append("\nSTORY INSPIRATION:")
            for asset in story_assets:
                desc = asset.description or f"Source: {asset.filename}"
                context_parts.append(f"- {desc}")

        return "\n".join(context_parts)

    def get_image_asset_paths(self, asset_ids: List[str]) -> List[Path]:
        """Get file paths for image assets (for image-to-image generation).

        Args:
            asset_ids: List of asset identifiers

        Returns:
            List of file paths for image assets
        """
        assets = self.get_assets(asset_ids)
        paths = []

        for asset in assets:
            if asset.mime_type.startswith("image/"):
                # Convert URL back to file path
                file_path = Path.cwd() / asset.url.lstrip("/")
                if file_path.exists():
                    paths.append(file_path)
                else:
                    logger.warning(f"Asset file not found: {file_path}")

        return paths

    def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset (removes from registry, optionally deletes file).

        Args:
            asset_id: Asset identifier

        Returns:
            True if deleted, False if not found
        """
        if asset_id in self._assets:
            del self._assets[asset_id]
            logger.info(f"Asset deleted: {asset_id}")
            return True
        return False

    def list_all_assets(self) -> List[StoryAsset]:
        """List all registered assets.

        Returns:
            List of all assets
        """
        return list(self._assets.values())


# Singleton instance
asset_manager = AssetManager()
