"""
Prompt JSON unpacker (Anima-oriented schema).

This node is designed to take an LLM output that is *one JSON object only*:
{
  "positive": "...",
  "negative": "...",
  "width": 1024,
  "height": 1024,
  "steps": 40,
  "cfg": 4.5,
  "sampler": "er_sde",
  "seed": -1,
  "notes": "..."
}

And split it into typed ComfyUI outputs, plus a SIMPLECHAT_VARS dict for
Mustache templating in other SimpleChat nodes.
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


def _try_parse_json(text: str) -> Any:
    """
    Try strict JSON first; if it fails, apply a minimal cleanup and retry.
    """
    try:
        return json.loads(text)
    except Exception:
        # Common LLM mistake: trailing commas
        cleaned = re.sub(r",\s*([}\]])", r"\1", text)
        return json.loads(cleaned)


def _as_int(value: Any, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return default
        try:
            return int(s)
        except Exception:
            try:
                return int(float(s))
            except Exception:
                return default
    return default


def _as_float(value: Any, default: float) -> float:
    if value is None:
        return default
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return default
        try:
            return float(s)
        except Exception:
            return default
    return default


def _as_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)


_SAMPLER_ALIASES = {
    # community shorthand -> ComfyUI names
    "euler_a": "euler_ancestral",
    "euler-ancestral": "euler_ancestral",
    "euler ancestral": "euler_ancestral",
}


def _normalize_sampler(name: str, default: str) -> str:
    if not isinstance(name, str):
        return default
    s = name.strip()
    if not s:
        return default
    low = s.lower()
    return _SAMPLER_ALIASES.get(low, low)


class SimpleChatPromptJsonUnpack:
    """
    Unpack a fixed-schema JSON (positive/negative/params/notes) into typed outputs.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_text": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
            },
            "optional": {
                "strip_code_fence": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = (
        "STRING",  # positive
        "STRING",  # negative
        "INT",     # width
        "INT",     # height
        "INT",     # steps
        "FLOAT",   # cfg
        "SAMPLER", # sampler
        "INT",     # seed
        "STRING",  # notes
        "SIMPLECHAT_VARS",  # vars
        "SIMPLECHAT_JSON",  # obj
        "STRING",  # sampler_name (string)
    )
    RETURN_NAMES = (
        "positive",
        "negative",
        "width",
        "height",
        "steps",
        "cfg",
        "sampler",
        "seed",
        "notes",
        "vars",
        "obj",
        "sampler_name",
    )
    FUNCTION = "unpack"
    CATEGORY = "SimpleChat/Utils"
    DESCRIPTION = "Unpack an LLM-produced JSON into ComfyUI-typed fields + Mustache vars."

    def unpack(self, json_text: str, strip_code_fence: bool = True):
        raw = _strip_code_fence(json_text) if strip_code_fence else json_text
        data = _try_parse_json(raw) if isinstance(raw, str) else raw
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object (dict) at top-level.")

        positive = _as_str(data.get("positive", ""), "")
        negative = _as_str(data.get("negative", ""), "")

        width = _as_int(data.get("width"), 1024)
        height = _as_int(data.get("height"), 1024)
        steps = _as_int(data.get("steps"), 40)
        cfg = _as_float(data.get("cfg"), 4.5)

        sampler_name = _normalize_sampler(_as_str(data.get("sampler", ""), ""), "er_sde")
        seed = _as_int(data.get("seed"), -1)
        notes = _as_str(data.get("notes", ""), "")

        vars_dict = {
            # English keys (match JSON schema)
            "positive": positive,
            "negative": negative,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg": cfg,
            "sampler": sampler_name,
            "sampler_name": sampler_name,
            "seed": seed,
            "notes": notes,
            # Prefixed scheme keys (avoid collisions)
            "anima.positive": positive,
            "anima.negative": negative,
            "anima.width": width,
            "anima.height": height,
            "anima.steps": steps,
            "anima.cfg": cfg,
            "anima.sampler": sampler_name,
            "anima.sampler_name": sampler_name,
            "anima.seed": seed,
            "anima.notes": notes,
            # Chinese aliases (optional convenience)
            "正面提示词": positive,
            "负面提示词": negative,
            "宽": width,
            "高": height,
            "步数": steps,
            "采样器": sampler_name,
            "种子": seed,
            "备注": notes,
            # Chinese aliases (prefixed)
            "anima.正面提示词": positive,
            "anima.负面提示词": negative,
            "anima.宽": width,
            "anima.高": height,
            "anima.步数": steps,
            "anima.采样器": sampler_name,
            "anima.种子": seed,
            "anima.备注": notes,
        }

        # Build an actual sampler object for SAMPLER output (for custom-sampling graphs)
        import comfy.samplers
        sampler_obj = comfy.samplers.sampler_object(sampler_name)

        return (
            positive,
            negative,
            width,
            height,
            steps,
            cfg,
            sampler_obj,
            seed,
            notes,
            vars_dict,
            data,
            sampler_name,
        )

