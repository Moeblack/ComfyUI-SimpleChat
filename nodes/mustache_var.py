"""
Mustache variables node - define {{var}} values.
"""

from __future__ import annotations

from typing import Any


class SimpleChatMustacheVar:
    """
    Define a single Mustache variable and output a merged vars dict.

    Usage:
      - Set name/value in this node
      - Connect output to other SimpleChat nodes via optional `vars` input
      - Use {{name}} anywhere in prompts to inject the value
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "name": ("STRING", {"default": "自定义胡子变量"}),
                "value": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "vars_in": ("SIMPLECHAT_VARS",),
            },
        }

    RETURN_TYPES = ("SIMPLECHAT_VARS",)
    RETURN_NAMES = ("vars",)
    FUNCTION = "set_var"
    CATEGORY = "SimpleChat/Utils"
    DESCRIPTION = "Define a {{var}} value for prompt templating."

    def set_var(self, name: str, value: str, vars_in: Any = None):
        merged = {}
        if isinstance(vars_in, dict):
            merged.update(vars_in)

        key = (name or "").strip()
        if key:
            merged[key] = value

        return (merged,)

