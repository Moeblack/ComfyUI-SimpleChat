"""
Provider implementations for SimpleChat.
"""
from .base import BaseProvider, ChatResponse, ChatConfig
from .openai import OpenAIProvider
from .claude import ClaudeProvider
from .gemini import GeminiProvider


PROVIDERS = {
    "openai": OpenAIProvider,
    "claude": ClaudeProvider,
    "gemini": GeminiProvider,
}


def get_provider(config: ChatConfig) -> BaseProvider:
    """Get provider instance from config."""
    provider_cls = PROVIDERS.get(config.provider)
    if not provider_cls:
        raise ValueError(f"Unknown provider: {config.provider}")
    return provider_cls(api_key=config.api_key, base_url=config.base_url or None)


__all__ = [
    "BaseProvider",
    "ChatResponse",
    "ChatConfig",
    "OpenAIProvider",
    "ClaudeProvider",
    "GeminiProvider",
    "PROVIDERS",
    "get_provider",
]
