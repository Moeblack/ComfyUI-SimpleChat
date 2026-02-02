"""
JSON to Mustache Vars.

Convert an arbitrary JSON object into SIMPLECHAT_VARS for Mustache rendering.
Supports:
- ```json code fences extraction
- minimal JSON cleanup (trailing commas)
- optional flattening (a.b.c keys)
- manual overrides (key=value lines)
- vars_in merge (vars_in overrides JSON by default)
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict


_CODE_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def _strip_code_fence(text: str) -> str:
    if not isinstance(text, str):
        return text
    m = _CODE_FENCE_RE.search(text)
    return m.group(1) if m else text


def _try_parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        cleaned = re.sub(r",\s*([}\]])", r"\1", text)
        try:
            return json.loads(cleaned)
        except Exception:
            # last resort: try extracting first {...} block
            a = cleaned.find("{")
            b = cleaned.rfind("}")
            if a != -1 and b != -1 and b > a:
                return json.loads(cleaned[a : b + 1])
            raise


def _as_scalar_or_str(v: Any):
    if v is None:
        return ""
    if isinstance(v, (str, int, float, bool)):
        return v
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v)


def _flatten(prefix: str, obj: Any, out: Dict[str, Any]):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str) or not k:
                continue
            key = f"{prefix}.{k}" if prefix else k
            _flatten(key, v, out)
        return
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            key = f"{prefix}[{i}]"
            _flatten(key, v, out)
        return
    out[prefix] = _as_scalar_or_str(obj)


def _parse_overrides(text: str) -> Dict[str, str]:
    """
    Parse overrides from lines like:
      key=value
      key: value
    Ignores empty lines and #// comments.
    """
    if not isinstance(text, str):
        return {}
    raw = text.replace("\r\n", "\n").replace("\r", "\n")
    out: Dict[str, str] = {}
    for line in raw.split("\n"):
        s = (line or "").strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        if "=" in s:
            k, v = s.split("=", 1)
        elif ":" in s:
            k, v = s.split(":", 1)
        else:
            # allow "key" alone => set to empty
            k, v = s, ""
        k = (k or "").strip()
        if not k:
            continue
        out[k] = (v or "").strip()
    return out


class SimpleChatJsonToVars:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_text": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "strip_code_fence": ("BOOLEAN", {"default": True}),
                "flatten_keys": ("BOOLEAN", {"default": True, "tooltip": "Flatten nested keys into a.b.c and arr[0] style keys."}),
                "prefix": ("STRING", {"default": "", "tooltip": "Optional prefix, e.g. anima. (will become prefix.key)"}),
                "override_mode": (["vars_in_overrides_json", "json_overrides_vars_in"], {"default": "vars_in_overrides_json"}),
                "overrides": ("STRING", {"multiline": True, "default": "", "placeholder": "key=value\\nkey2=value2"}),
            },
            "optional": {
                "vars_in": ("SIMPLECHAT_VARS",),
            },
        }

    RETURN_TYPES = ("SIMPLECHAT_VARS", "SIMPLECHAT_JSON")
    RETURN_NAMES = ("vars", "obj")
    FUNCTION = "to_vars"
    CATEGORY = "SimpleChat/Utils"
    DESCRIPTION = "Convert JSON to SIMPLECHAT_VARS (Mustache vars), with optional flatten + overrides."

    def to_vars(
        self,
        json_text: str,
        strip_code_fence: bool = True,
        flatten_keys: bool = True,
        prefix: str = "",
        override_mode: str = "vars_in_overrides_json",
        overrides: str = "",
        vars_in: Any = None,
    ):
        raw = _strip_code_fence(json_text) if strip_code_fence else json_text
        data = _try_parse_json(raw) if isinstance(raw, str) else raw
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object (dict) at top-level.")

        pfx = (prefix or "").strip()
        if pfx.endswith("."):
            pfx = pfx[:-1]

        base: Dict[str, Any] = {}
        if flatten_keys:
            _flatten("", data, base)
        else:
            for k, v in data.items():
                if not isinstance(k, str) or not k:
                    continue
                base[k] = _as_scalar_or_str(v)

        # Apply prefix
        if pfx:
            prefixed = {}
            for k, v in base.items():
                if not k:
                    continue
                prefixed[f"{pfx}.{k}"] = v
            base.update(prefixed)

        # Apply manual overrides (always last)
        manual = _parse_overrides(overrides)
        if pfx and manual:
            # also set prefixed versions when prefix is set and key is not already prefixed
            for k, v in list(manual.items()):
                if "." not in k and not k.startswith(f"{pfx}."):
                    manual[f"{pfx}.{k}"] = v

        merged: Dict[str, Any] = {}
        if override_mode == "json_overrides_vars_in":
            if isinstance(vars_in, dict):
                merged.update(vars_in)
            merged.update(base)
        else:
            merged.update(base)
            if isinstance(vars_in, dict):
                merged.update(vars_in)

        merged.update(manual)

        return (merged, data)

