"""
Google Gemini provider implementation.
Supports chat and image generation (Nano Banana / Nano Banana Pro).
"""
import aiohttp
from typing import Any
import torch

from .base import BaseProvider, ChatResponse
from ..image_utils import tensor_to_base64, base64_to_tensor


class GeminiProvider(BaseProvider):
    """Google Gemini API provider with image generation support."""

    @property
    def default_base_url(self) -> str:
        return "https://generativelanguage.googleapis.com/v1beta"

    def _build_contents(
        self,
        messages: list[dict[str, Any]],
        images: list[torch.Tensor] | None = None,
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """
        Build Gemini-format contents.

        Returns:
            Tuple of (system_instruction, contents)
        """
        system = None
        contents = []

        for i, msg in enumerate(messages):
            role = msg["role"]
            content = msg["content"]

            # Extract system message
            if role == "system":
                system = content
                continue

            # Map roles
            gemini_role = "user" if role == "user" else "model"

            # Build parts
            parts = []

            # Add images to last user message
            if role == "user" and images and i == len(messages) - 1:
                for img in images:
                    b64 = tensor_to_base64(img)
                    parts.append({
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": b64,
                        }
                    })

            parts.append({"text": content})
            contents.append({"role": gemini_role, "parts": parts})

        return system, contents

    async def chat(
        self,
        messages: list[dict[str, Any]],
        model: str,
        temperature: float = 1.0,
        max_tokens: int = 2048,
        images: list[torch.Tensor] | None = None,
        enable_image_generation: bool = False,
        **kwargs,
    ) -> ChatResponse:
        """Send chat request to Gemini API."""

        url = f"{self.base_url}/models/{model}:generateContent"

        # Add API key as query parameter
        if "?" in url:
            url += f"&key={self.api_key}"
        else:
            url += f"?key={self.api_key}"

        headers = {"Content-Type": "application/json"}

        system, contents = self._build_contents(messages, images)

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        # Enable image generation if requested
        if enable_image_generation:
            payload["generationConfig"]["responseModalities"] = ["TEXT", "IMAGE"]

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"Gemini API error {resp.status}: {error_text}")

                data = await resp.json()

        # Extract text and images from response
        text = ""
        result_image = None

        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                if "text" in part:
                    text += part["text"]
                elif "inlineData" in part:
                    inline = part["inlineData"]
                    if inline.get("mimeType", "").startswith("image/"):
                        result_image = base64_to_tensor(inline["data"])

        return ChatResponse(text=text, image=result_image, raw_response=data)

    async def generate_image(
        self,
        prompt: str,
        model: str,
        reference_image: torch.Tensor | None = None,
        aspect_ratio: str = "1:1",
        size: str = "1K",
        **kwargs,
    ) -> ChatResponse:
        """Generate or edit image using Gemini."""

        url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        # Build parts
        parts = []

        # Add reference image if provided
        if reference_image is not None:
            b64 = tensor_to_base64(reference_image)
            parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": b64,
                }
            })

        parts.append({"text": prompt})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
            }
        }

        # Add image config if supported
        if aspect_ratio or size:
            payload["generationConfig"]["imageConfig"] = {}
            if aspect_ratio:
                payload["generationConfig"]["imageConfig"]["aspectRatio"] = aspect_ratio
            if size:
                payload["generationConfig"]["imageConfig"]["imageSize"] = size

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"Gemini API error {resp.status}: {error_text}")

                data = await resp.json()

        # Extract text and image
        text = ""
        result_image = None

        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                if "text" in part:
                    text += part["text"]
                elif "inlineData" in part:
                    inline = part["inlineData"]
                    if inline.get("mimeType", "").startswith("image/"):
                        result_image = base64_to_tensor(inline["data"])

        if result_image is None:
            raise RuntimeError("Gemini did not return an image. Try a different prompt or model.")

        return ChatResponse(text=text, image=result_image, raw_response=data)
