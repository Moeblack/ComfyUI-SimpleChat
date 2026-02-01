"""
Simple text input node.

Provides a standalone multiline text box and outputs a STRING.
"""

from __future__ import annotations


class SimpleChatTextInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "output"
    CATEGORY = "SimpleChat/Utils"
    DESCRIPTION = "Standalone multiline text input."

    def output(self, text: str):
        return (text,)

