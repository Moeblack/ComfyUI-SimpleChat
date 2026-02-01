"""
Mustache text render node.

This node renders {{var}} placeholders in arbitrary text using SIMPLECHAT_VARS
without requiring any SimpleChat "main" chat/image nodes.
"""

from __future__ import annotations

from typing import Any

from ..core.template import render_mustache


class SimpleChatMustacheRender:
    """
    Render a text template with {{var}} placeholders.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
            },
            "optional": {
                # Accept either vars dict (SIMPLECHAT_VARS) or a parsed JSON object (SIMPLECHAT_JSON)
                "vars": ("SIMPLECHAT_VARS,SIMPLECHAT_JSON",),
                "keep_unmatched": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "render"
    CATEGORY = "SimpleChat/Utils"
    DESCRIPTION = "Render {{var}} placeholders in text using SIMPLECHAT_VARS."

    def render(self, text: str, vars: Any = None, keep_unmatched: bool = True):
        return (render_mustache(text, vars, keep_unmatched=keep_unmatched),)

