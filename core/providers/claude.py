"""
Claude/Anthropic provider implementation.
"""
import aiohttp
from typing import Any
import torch

from .base import BaseProvider, ChatResponse
from ..image_utils import tensor_to_base64, create_data_uri


class ClaudeProvider(BaseProvider):
    """Anthropic Claude API provider."""

    @property
    def default_base_url(self) -> str:
        return "https://api.anthropic.com/v1"

    def _build_messages(
        self,
        messages: list[dict[str, Any]],
        images: list[torch.Tensor] | None = None,
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """
        Build Claude-format messages with optional images.

        Returns:
            Tuple of (system_prompt, messages)
        """
        system = None
        result = []

        for i, msg in enumerate(messages):
            role = msg["role"]
            content = msg["content"]

            # Extract system message
            if role == "system":
                system = content
                continue

            # Handle user message with images
            if role == "user" and images and i == len(messages) - 1:
                content_parts = []
                for img in images:
                    b64 = tensor_to_base64(img)
                    content_parts.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": b64,
                        }
                    })
                content_parts.append({"type": "text", "text": content})
                result.append({"role": "user", "content": content_parts})
            else:
                result.append({"role": role, "content": content})

        return system, result

    async def chat(
        self,
        messages: list[dict[str, Any]],
        model: str,
        temperature: float = 1.0,
        max_tokens: int = 2048,
        images: list[torch.Tensor] | None = None,
        **kwargs,
    ) -> ChatResponse:
        """Send chat request to Claude API."""

        url = f"{self.base_url}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        system, claude_messages = self._build_messages(messages, images)

        payload = {
            "model": model,
            "messages": claude_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system:
            payload["system"] = system

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"Claude API error {resp.status}: {error_text}")

                data = await resp.json()

        # Extract text from response
        text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                text += block.get("text", "")

        return ChatResponse(text=text, raw_response=data)

    async def generate_image(
        self,
        prompt: str,
        model: str,
        reference_image: torch.Tensor | None = None,
        aspect_ratio: str = "1:1",
        size: str = "1K",
        **kwargs,
    ) -> ChatResponse:
        """Claude doesn't support image generation."""
        raise NotImplementedError(
            "Claude does not support image generation. "
            "Use Gemini provider for image generation."
        )
