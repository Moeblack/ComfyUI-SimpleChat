"""
JSON Parse (16 outputs).

Same as SimpleChatJsonParse but with 16 extract paths instead of 8.
Useful when you want more "ports" without adding many Mustache Var nodes.
"""

from __future__ import annotations

import json
import re
from typing import Any


_CODE_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def _strip_code_fence(text: str) -> str:
    if not isinstance(text, str):
        return text
    m = _CODE_FENCE_RE.search(text)
    return m.group(1) if m else text


def _tokenize_path(path: str) -> list[Any]:
    if not isinstance(path, str):
        return []
    s = path.strip()
    if not s:
        return []

    tokens: list[Any] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == ".":
            i += 1
            continue

        if ch == "[":
            j = s.find("]", i + 1)
            if j == -1:
                tokens.append(s[i:])
                break
            inner = s[i + 1 : j].strip()
            if (inner.startswith('"') and inner.endswith('"')) or (inner.startswith("'") and inner.endswith("'")):
                tokens.append(inner[1:-1])
            else:
                try:
                    tokens.append(int(inner))
                except Exception:
                    tokens.append(inner)
            i = j + 1
            continue

        j = i
        while j < n and s[j] not in ".[":
            j += 1
        key = s[i:j].strip()
        if key:
            tokens.append(key)
        i = j

    return tokens


_MISSING = object()


def _get_by_tokens(obj: Any, tokens: list[Any]) -> Any:
    cur = obj
    for tok in tokens:
        if isinstance(tok, int):
            if isinstance(cur, (list, tuple)) and -len(cur) <= tok < len(cur):
                cur = cur[tok]
            else:
                return _MISSING
        else:
            if isinstance(cur, dict) and tok in cur:
                cur = cur[tok]
            else:
                return _MISSING
    return cur


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)


class SimpleChatJsonParse16:
    @classmethod
    def INPUT_TYPES(cls):
        req = {
            "json_text": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
            "strip_code_fence": ("BOOLEAN", {"default": True}),
            "default": ("STRING", {"default": ""}),
        }
        for i in range(1, 17):
            req[f"path{i}"] = ("STRING", {"default": ""})
        return {"required": req}

    RETURN_TYPES = (
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "STRING",
        "SIMPLECHAT_JSON",
    )
    RETURN_NAMES = (
        "out1",
        "out2",
        "out3",
        "out4",
        "out5",
        "out6",
        "out7",
        "out8",
        "out9",
        "out10",
        "out11",
        "out12",
        "out13",
        "out14",
        "out15",
        "out16",
        "obj",
    )
    FUNCTION = "parse"
    CATEGORY = "SimpleChat/Utils"
    DESCRIPTION = "Parse JSON and extract up to 16 values by dot/bracket paths."

    def parse(self, json_text: str, strip_code_fence: bool = True, default: str = "", **kwargs):
        raw = _strip_code_fence(json_text) if strip_code_fence else json_text
        data = json.loads(raw) if isinstance(raw, str) else raw

        outs: list[str] = []
        for i in range(1, 17):
            p = (kwargs.get(f"path{i}") or "").strip()
            if not p:
                outs.append(default)
                continue
            tokens = _tokenize_path(p)
            val = _get_by_tokens(data, tokens)
            outs.append(default if val is _MISSING else _stringify(val))

        return (*outs, data)

