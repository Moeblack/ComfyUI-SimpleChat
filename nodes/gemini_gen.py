"""
Gemini Image Gen node - Text-to-image generation with Gemini.
"""
import torch
from ..core import get_provider, ChatConfig


class GeminiImageGen:
    """Generate images from text using Gemini (Nano Banana / Nano Banana Pro)."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config": ("SIMPLECHAT_CONFIG",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "aspect_ratio": (["1:1", "16:9", "9:16", "4:3", "3:4", "5:4", "4:5"], {"default": "1:1"}),
                "size": (["1K", "2K", "4K"], {"default": "1K"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("IMAGE", "text")
    FUNCTION = "generate"
    CATEGORY = "SimpleChat/Gemini"
    DESCRIPTION = "Generate image from text using Gemini image models (gemini-2.5-flash-image or gemini-3-pro-image-preview)."

    async def generate(
        self,
        config: ChatConfig,
        prompt: str,
        aspect_ratio: str = "1:1",
        size: str = "1K",
    ):
        # Validate provider
        if config.provider != "gemini":
            raise ValueError("Gemini Image Gen requires Gemini provider. Please use a Gemini config.")

        # Get provider
        provider = get_provider(config)

        # Directly await the async provider method
        response = await provider.generate_image(
            prompt=prompt,
            model=config.model,
            reference_image=None,
            aspect_ratio=aspect_ratio,
            size=size,
        )

        # Ensure we have an image
        if response.image is None:
            # Return empty image if generation failed
            empty = torch.zeros((1, 512, 512, 3))
            return (empty, response.text or "No image generated")

        return (response.image, response.text)
