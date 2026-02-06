"""
Content generation API clients.

Reference: specs/functional.md US-007, US-008, US-009
"""

import os
import httpx
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from chimera_factory.utils.logging import setup_logger
from chimera_factory.exceptions import ContentGenerationError, APIError

load_dotenv()
logger = setup_logger(__name__)


class IdeogramClient:
    """Ideogram API client for image generation."""
    
    def __init__(self):
        self.api_key = os.getenv("IDEOGRAM_API_KEY")
        self.base_url = os.getenv("IDEOGRAM_API_BASE_URL", "https://api.ideogram.ai/v1")
        self._client: Optional[httpx.Client] = None
    
    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.Client(base_url=self.base_url, headers=headers, timeout=60.0)
        return self._client
    
    def is_configured(self) -> bool:
        """Check if client is configured."""
        return bool(self.api_key)
    
    def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        character_reference_id: Optional[str] = None,
        dimensions: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Generate image using Ideogram API.
        
        Reference: https://ideogram.ai/api/docs
        
        Args:
            prompt: Image generation prompt
            style: Optional style guide
            character_reference_id: Optional character reference ID
            dimensions: Optional dimensions dict with width/height
            
        Returns:
            Dict with content_url and metadata
            
        Raises:
            ContentGenerationError: If generation fails
        """
        if not self.is_configured():
            logger.warning("Ideogram API not configured, returning mock response")
            return {
                "content_url": "https://ideogram.example.com/image/12345",
                "metadata": {
                    "platform": "ideogram",
                    "format": "image",
                    "dimensions": dimensions or {"width": 1024, "height": 1024},
                    "mock": True
                },
                "confidence": 0.85
            }
        
        try:
            client = self._get_client()
            payload = {
                "prompt": prompt,
                "aspect_ratio": "1:1"  # Default, can be customized
            }
            if style:
                payload["style"] = style
            if character_reference_id:
                payload["character_reference_id"] = character_reference_id
            if dimensions:
                payload["width"] = dimensions.get("width", 1024)
                payload["height"] = dimensions.get("height", 1024)
            
            # Submit generation request
            response = client.post("/images/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Ideogram API typically returns a job ID, then we poll for results
            job_id = data.get("job_id") or data.get("id")
            if job_id:
                # Poll for completion (simplified - actual implementation would poll)
                logger.info(f"Ideogram image generation job submitted: {job_id}")
                # In real implementation, poll until ready
                return {
                    "content_url": data.get("image_url") or f"https://ideogram.ai/image/{job_id}",
                    "metadata": {
                        "platform": "ideogram",
                        "format": "image",
                        "dimensions": dimensions or {"width": 1024, "height": 1024},
                        "job_id": job_id
                    },
                    "confidence": 0.85
                }
            
            raise ContentGenerationError("Invalid response from Ideogram API")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Ideogram API error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 429:
                raise APIError("Ideogram API rate limit exceeded", code="RATE_LIMIT_EXCEEDED", retryable=True)
            raise ContentGenerationError(f"Failed to generate image: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error in Ideogram image generation: {e}", exc_info=True)
            raise ContentGenerationError(f"Failed to generate image: {str(e)}")


class RunwayClient:
    """Runway API client for video generation."""
    
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_KEY")
        self.base_url = os.getenv("RUNWAY_API_BASE_URL", "https://api.runwayml.com/v1")
        self._client: Optional[httpx.Client] = None
    
    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.Client(base_url=self.base_url, headers=headers, timeout=120.0)  # Longer timeout for video
        return self._client
    
    def is_configured(self) -> bool:
        """Check if client is configured."""
        return bool(self.api_key)
    
    def generate_video(
        self,
        prompt: str,
        style: Optional[str] = None,
        character_reference_id: Optional[str] = None,
        duration: float = 30.0
    ) -> Dict[str, Any]:
        """
        Generate video using Runway API.
        
        Reference: https://docs.runwayml.com/
        
        Args:
            prompt: Video generation prompt
            style: Optional style guide
            character_reference_id: Optional character reference ID
            duration: Video duration in seconds
            
        Returns:
            Dict with content_url and metadata
            
        Raises:
            ContentGenerationError: If generation fails
        """
        if not self.is_configured():
            logger.warning("Runway API not configured, returning mock response")
            return {
                "content_url": "https://runway.example.com/video/12345",
                "metadata": {
                    "platform": "runway",
                    "format": "video",
                    "duration": duration,
                    "mock": True
                },
                "confidence": 0.80
            }
        
        try:
            client = self._get_client()
            payload = {
                "prompt": prompt,
                "duration": min(duration, 10.0)  # Runway typically limits duration
            }
            if style:
                payload["style"] = style
            if character_reference_id:
                payload["character_reference_id"] = character_reference_id
            
            # Submit generation request
            response = client.post("/videos/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Runway API typically returns a task ID, then we poll for results
            task_id = data.get("task_id") or data.get("id")
            if task_id:
                logger.info(f"Runway video generation task submitted: {task_id}")
                # In real implementation, poll until ready
                return {
                    "content_url": data.get("video_url") or f"https://runwayml.com/video/{task_id}",
                    "metadata": {
                        "platform": "runway",
                        "format": "video",
                        "duration": duration,
                        "task_id": task_id
                    },
                    "confidence": 0.80
                }
            
            raise ContentGenerationError("Invalid response from Runway API")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Runway API error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 429:
                raise APIError("Runway API rate limit exceeded", code="RATE_LIMIT_EXCEEDED", retryable=True)
            raise ContentGenerationError(f"Failed to generate video: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error in Runway video generation: {e}", exc_info=True)
            raise ContentGenerationError(f"Failed to generate video: {str(e)}")
