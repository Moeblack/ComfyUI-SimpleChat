"""
XY Cell Prefix (Batch)

Generate a filename_prefix list for each XY cell (row-major),
without changing the prompt itself.

Typical use:
- Connect x_labels/y_labels from `Anima XY Matrix (JSON List)`
- Connect output `filename_prefix` to `SaveImage.filename_prefix`
"""

from __future__ import annotations

import re
from typing import Any, List


_ILLEGAL_FS_CHARS_RE = re.compile(r'[<>:"/\\\\|?*]+')
_WS_RE = re.compile(r"\s+")


def _first(v: Any, default: Any = None) -> Any:
    if isinstance(v, (list, tuple)):
        return v[0] if len(v) > 0 else default
    return v


def _split_labels(text: str) -> List[str]:
    if not isinstance(text, str):
        return []
    raw = text.replace("\r\n", "\n").replace("\r", "\n")
    out: List[str] = []
    for line in raw.split("\n"):
        s = (line or "").strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        out.append(s)
    return out


def _sanitize_prefix(s: str, max_len: int = 120) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    s = _ILLEGAL_FS_CHARS_RE.sub("_", s)
    s = s.replace("\n", "_").replace("\r", "_").replace("\t", "_")
    s = _WS_RE.sub("_", s)
    s = s.strip(" .")  # Windows doesn't allow trailing dot/space
    if len(s) > max_len:
        s = s[:max_len].rstrip(" .")
    return s


class SimpleChatXYCellPrefix:
    """
    Build per-cell filename prefixes from x/y labels.

    - Row-major order (y rows, then x columns), matching `SimpleChatAnimaPromptXYMatrix`.
    - Diagonal can be single name when x==y.
    - Default joiner for display is '+' (purely for naming; doesn't affect prompts).
    """

    # In list pipelines, run ONCE with the whole list (avoid N-times expansion).
    INPUT_IS_LIST = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "x_labels": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "y_labels": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
            },
            "optional": {
                "joiner": ("STRING", {"default": "+"}),
                "diagonal_single": ("BOOLEAN", {"default": True}),
                "base_prefix": ("STRING", {"default": ""}),
                "sanitize": ("BOOLEAN", {"default": True}),
                # Keep this as the last widget for future backward compatibility.
                "matrix_mode": (["full", "upper_triangle", "diagonal_only"], {"default": "full"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename_prefix",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "build"
    CATEGORY = "SimpleChat/Utils"
    DESCRIPTION = "Build per-cell filename_prefix list from x/y labels (row-major), for SaveImage."

    def build(
        self,
        x_labels: Any,
        y_labels: Any,
        joiner: Any = "+",
        diagonal_single: Any = True,
        base_prefix: Any = "",
        sanitize: Any = True,
        matrix_mode: Any = "full",
    ):
        x_labels = _first(x_labels, "") or ""
        y_labels = _first(y_labels, "") or ""
        joiner = str(_first(joiner, "+") or "+")
        diagonal_single = bool(_first(diagonal_single, True))
        base_prefix = str(_first(base_prefix, "") or "")
        sanitize = bool(_first(sanitize, True))
        matrix_mode = str(_first(matrix_mode, "full") or "full")

        xs = _split_labels(x_labels)
        ys = _split_labels(y_labels)
        if not xs:
            xs = [""]
        if not ys:
            ys = [""]

        def _one(x: str, y: str) -> str:
            xa = (x or "").strip()
            ya = (y or "").strip()
            if diagonal_single and xa and ya and xa == ya:
                name = xa
            else:
                if xa and ya:
                    name = f"{xa}{joiner}{ya}"
                else:
                    name = xa or ya or ""

            if base_prefix:
                name = f"{base_prefix}{name}"
            if sanitize:
                name = _sanitize_prefix(name)
            return name or "cell"

        out: List[str] = []
        if matrix_mode != "full" and len(xs) == len(ys):
            n = len(xs)
            if matrix_mode == "upper_triangle":
                for r in range(n):
                    for c in range(r, n):
                        out.append(_one(xs[c], ys[r]))
            elif matrix_mode == "diagonal_only":
                for i in range(n):
                    out.append(_one(xs[i], ys[i]))
            else:
                for y in ys:
                    for x in xs:
                        out.append(_one(x, y))
        else:
            for y in ys:
                for x in xs:
                    out.append(_one(x, y))

        return (out,)

