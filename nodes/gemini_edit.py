"""
Gemini Image Edit node - Edit images using Gemini.
"""
import torch
from ..core import get_provider, ChatConfig


class GeminiImageEdit:
    """Edit images using Gemini (Nano Banana / Nano Banana Pro)."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "config": ("SIMPLECHAT_CONFIG",),
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "size": (["1K", "2K", "4K"], {"default": "1K"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("IMAGE", "text")
    FUNCTION = "edit"
    CATEGORY = "SimpleChat/Gemini"
    DESCRIPTION = "Edit or modify an image using Gemini image models with a text prompt."

    async def edit(
        self,
        config: ChatConfig,
        image: torch.Tensor,
        prompt: str,
        size: str = "1K",
    ):
        # Validate provider
        if config.provider != "gemini":
            raise ValueError("Gemini Image Edit requires Gemini provider. Please use a Gemini config.")

        # Get provider
        provider = get_provider(config)

        # Directly await the async provider method
        response = await provider.generate_image(
            prompt=prompt,
            model=config.model,
            reference_image=image,
            aspect_ratio=None,  # Preserve original aspect ratio for edits
            size=size,
        )

        # Ensure we have an image
        if response.image is None:
            # Return original image if edit failed
            return (image, response.text or "No image generated")

        return (response.image, response.text)
