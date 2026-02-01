"""
Markdown preview node.

Backend returns UI text; frontend JS renders markdown to HTML safely.
"""

from __future__ import annotations


class SimpleChatMarkdownPreview:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "preview"
    OUTPUT_NODE = True
    CATEGORY = "SimpleChat/Utils"
    DESCRIPTION = "Render input text as Markdown (frontend-rendered)."

    def preview(self, text: str):
        # Use the standard 'ui.text' channel (same shape as PreviewAny)
        return {"ui": {"text": (text or "",)}}

