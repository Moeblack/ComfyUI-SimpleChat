"""
ComfyUI-SimpleChat: Simple LLM chat nodes for ComfyUI.

Supports OpenAI, Claude, and Gemini APIs with custom base URL support.
Features NoASS mode for roleplay optimization and Gemini image generation.
"""
from .nodes import (
    SimpleChatConfig,
    SimpleChatText,
    SimpleChatImage,
    SimpleChatNoASS,
    GeminiImageGen,
    GeminiImageEdit,
)

# Register API routes
from .api import setup_routes
setup_routes()

# Node class mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "SimpleChatConfig": SimpleChatConfig,
    "SimpleChatText": SimpleChatText,
    "SimpleChatImage": SimpleChatImage,
    "SimpleChatNoASS": SimpleChatNoASS,
    "GeminiImageGen": GeminiImageGen,
    "GeminiImageEdit": GeminiImageEdit,
}

# Display names for the UI
NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleChatConfig": "API Config",
    "SimpleChatText": "Chat",
    "SimpleChatImage": "Chat with Image",
    "SimpleChatNoASS": "Chat NoASS",
    "GeminiImageGen": "Gemini Image Gen",
    "GeminiImageEdit": "Gemini Image Edit",
}

# Expose web directory for JS extensions
WEB_DIRECTORY = "./web"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]
