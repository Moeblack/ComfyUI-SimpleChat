"""
Base provider class for LLM API integrations.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import torch


@dataclass
class ChatResponse:
    """Unified response from any LLM provider."""
    text: str
    image: torch.Tensor | None = None
    raw_response: dict | None = None


@dataclass
class ChatConfig:
    """Configuration for API connection."""
    provider: str
    api_key: str
    base_url: str
    model: str

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "model": self.model,
        }


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, base_url: str | None = None):
        self.api_key = api_key
        self.base_url = base_url or self.default_base_url

    @property
    @abstractmethod
    def default_base_url(self) -> str:
        """Default API endpoint for this provider."""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, Any]],
        model: str,
        temperature: float = 1.0,
        max_tokens: int = 2048,
        images: list[torch.Tensor] | None = None,
        **kwargs,
    ) -> ChatResponse:
        """Send a chat request to the API."""
        pass

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        model: str,
        reference_image: torch.Tensor | None = None,
        aspect_ratio: str = "1:1",
        size: str = "1K",
        **kwargs,
    ) -> ChatResponse:
        """Generate or edit an image. Only supported by some providers."""
        pass
