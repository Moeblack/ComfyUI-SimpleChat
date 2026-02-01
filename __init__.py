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
    SimpleChatMustacheVar,
    SimpleChatMustacheRender,
    SimpleChatTextInput,
    SimpleChatJsonParse,
    SimpleChatMarkdownPreview,
    SimpleChatPromptJsonUnpack,
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
    "SimpleChatMustacheVar": SimpleChatMustacheVar,
    "SimpleChatMustacheRender": SimpleChatMustacheRender,
    "SimpleChatTextInput": SimpleChatTextInput,
    "SimpleChatJsonParse": SimpleChatJsonParse,
    "SimpleChatMarkdownPreview": SimpleChatMarkdownPreview,
    "SimpleChatPromptJsonUnpack": SimpleChatPromptJsonUnpack,
}

# Display names for the UI
NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleChatConfig": "API Config",
    "SimpleChatText": "Chat",
    "SimpleChatImage": "Chat with Image",
    "SimpleChatNoASS": "Chat NoASS",
    "GeminiImageGen": "Gemini Image Gen",
    "GeminiImageEdit": "Gemini Image Edit",
    "SimpleChatMustacheVar": "Mustache Var",
    "SimpleChatMustacheRender": "Mustache Render",
    "SimpleChatTextInput": "Text Input",
    "SimpleChatJsonParse": "JSON Parse",
    "SimpleChatMarkdownPreview": "Markdown Preview",
    "SimpleChatPromptJsonUnpack": "Prompt JSON Unpack",
}

# Expose web directory for JS extensions
WEB_DIRECTORY = "./web"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]
