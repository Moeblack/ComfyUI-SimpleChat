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
    SimpleChatTextList,
    SimpleChatJsonParse,
    SimpleChatJsonParse16,
    SimpleChatJsonToVars,
    SimpleChatMarkdownPreview,
    SimpleChatPromptJsonUnpack,
    SimpleChatAnimaPromptRouter,
    SimpleChatImageGrid,
    SimpleChatAnimaPromptXYMatrix,
    SimpleChatXYPlot,
    SimpleChatXYCellPrefix,
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
    "SimpleChatTextList": SimpleChatTextList,
    "SimpleChatJsonParse": SimpleChatJsonParse,
    "SimpleChatJsonParse16": SimpleChatJsonParse16,
    "SimpleChatJsonToVars": SimpleChatJsonToVars,
    "SimpleChatMarkdownPreview": SimpleChatMarkdownPreview,
    "SimpleChatPromptJsonUnpack": SimpleChatPromptJsonUnpack,
    "SimpleChatAnimaPromptRouter": SimpleChatAnimaPromptRouter,
    "SimpleChatImageGrid": SimpleChatImageGrid,
    "SimpleChatAnimaPromptXYMatrix": SimpleChatAnimaPromptXYMatrix,
    "SimpleChatXYPlot": SimpleChatXYPlot,
    "SimpleChatXYCellPrefix": SimpleChatXYCellPrefix,
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
    "SimpleChatTextList": "Text List (Batch)",
    "SimpleChatJsonParse": "JSON Parse",
    "SimpleChatJsonParse16": "JSON Parse (16)",
    "SimpleChatJsonToVars": "JSON -> Vars (Editable)",
    "SimpleChatMarkdownPreview": "Markdown Preview",
    "SimpleChatPromptJsonUnpack": "Prompt JSON Unpack",
    "SimpleChatAnimaPromptRouter": "Anima Prompt Router (Editable)",
    "SimpleChatImageGrid": "Image Grid (Batch)",
    "SimpleChatAnimaPromptXYMatrix": "Anima XY Matrix (JSON List)",
    "SimpleChatXYPlot": "XY Plot (Labels)",
    "SimpleChatXYCellPrefix": "XY Cell Prefix (Batch)",
}

# Expose web directory for JS extensions
WEB_DIRECTORY = "./web"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]
