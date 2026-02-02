"""
Text List node.

Create a list of strings from a multiline (or comma-separated) text input.
This is useful for batch testing (e.g. artist list) by connecting to inputs
that accept STRING and letting ComfyUI's list mapping run the graph multiple times.
"""

from __future__ import annotations


def _split_items(text: str, mode: str) -> list[str]:
    if not isinstance(text, str):
        return []
    s = text.strip()
    if not s:
        return []

    if mode == "comma":
        raw = s.replace("\r\n", "\n").replace("\r", "\n")
        raw = raw.replace("\n", ",")
        parts = raw.split(",")
    elif mode == "lines_or_comma":
        # if there is any newline, split by lines; else split by comma
        raw = s.replace("\r\n", "\n").replace("\r", "\n")
        if "\n" in raw:
            parts = raw.split("\n")
        else:
            parts = raw.split(",")
    else:
        # lines
        raw = s.replace("\r\n", "\n").replace("\r", "\n")
        parts = raw.split("\n")

    out: list[str] = []
    for p in parts:
        item = (p or "").strip()
        if not item:
            continue
        # allow comments
        if item.startswith("#") or item.startswith("//"):
            continue
        out.append(item)
    return out


class SimpleChatTextList:
    """
    Produce a STRING list output from text.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "split_mode": (["lines", "comma", "lines_or_comma"], {"default": "lines"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("item",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "make_list"
    CATEGORY = "SimpleChat/Utils"
    DESCRIPTION = "Split text into a list of strings (for batch testing)."

    def make_list(self, text: str, split_mode: str = "lines"):
        return (_split_items(text, split_mode),)

