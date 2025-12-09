"""
OpenAI provider implementation.
Also works with OpenAI-compatible APIs (e.g., local LLMs, other providers).
"""
import aiohttp
from typing import Any
import torch

from .base import BaseProvider, ChatResponse
from ..image_utils import tensor_to_base64, base64_to_tensor, create_data_uri


class OpenAIProvider(BaseProvider):
    """OpenAI API provider (and compatible APIs)."""

    @property
    def default_base_url(self) -> str:
        return "https://api.openai.com/v1"

    def _build_messages(
        self,
        messages: list[dict[str, Any]],
        images: list[torch.Tensor] | None = None,
    ) -> list[dict[str, Any]]:
        """Build OpenAI-format messages with optional images."""
        if not images:
            return messages

        # Find the last user message and add images to it
        result = []
        for i, msg in enumerate(messages):
            if msg["role"] == "user" and i == len(messages) - 1:
                # Convert content to multimodal format
                content = [{"type": "text", "text": msg["content"]}]
                for img in images:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": create_data_uri(img)}
                    })
                result.append({"role": "user", "content": content})
            else:
                result.append(msg)

        return result

    async def chat(
        self,
        messages: list[dict[str, Any]],
        model: str,
        temperature: float = 1.0,
        max_tokens: int = 2048,
        images: list[torch.Tensor] | None = None,
        **kwargs,
    ) -> ChatResponse:
        """Send chat request to OpenAI API."""

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": self._build_messages(messages, images),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"OpenAI API error {resp.status}: {error_text}")

                data = await resp.json()

        text = data["choices"][0]["message"]["content"]
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
        """OpenAI doesn't support native image generation in chat. Use DALL-E nodes instead."""
        raise NotImplementedError(
            "OpenAI image generation is not supported in SimpleChat. "
            "Use dedicated DALL-E nodes or Gemini provider for image generation."
        )
