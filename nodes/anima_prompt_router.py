"""
Anima Prompt Router (editable + latchable).

Why this node exists:
- LLM outputs ONE JSON.
- You want ComfyUI to automatically split it into prompt parts (quality/count/artist/...).
- You also want to *actively edit* some fields inside the node (manual overrides).
- And you want to *lock* some fields so that even if a new JSON comes in, those locked
  outputs do not change (latch behavior).

This node:
- Parses JSON (supports ```json fences)
- Extracts common Anima parts:
  quality_meta_year_safe / count / character / series / artist / style / environment / tags / neg
- Applies manual overrides
- Applies latch locks (sticky values per field)
- Rebuilds positive/negative from final parts
- Outputs SIMPLECHAT_VARS for Mustache usage
- Outputs the updated JSON as text (so you can log it or feed downstream)
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional


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
    def _extract_obj(s: str) -> str:
        if not isinstance(s, str):
            return s
        a = s.find("{")
        b = s.rfind("}")
        if a != -1 and b != -1 and b > a:
            return s[a : b + 1]
        return s

    try:
        return json.loads(text)
    except Exception:
        # Common LLM mistake: trailing commas
        cleaned = re.sub(r",\s*([}\]])", r"\1", text)
        try:
            return json.loads(cleaned)
        except Exception:
            return json.loads(_extract_obj(cleaned))


def _as_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)


def _clean_piece(text: str) -> str:
    if not isinstance(text, str):
        return ""
    s = text.strip()
    s = s.rstrip(",，")
    return s.strip()


def _join_pieces(*pieces: str) -> str:
    cleaned = [_clean_piece(p) for p in pieces]
    cleaned = [p for p in cleaned if p]
    return ", ".join(cleaned)


def _first_nonempty(*values: Any) -> str:
    for v in values:
        s = _as_str(v, "").strip()
        if s:
            return s
    return ""


class SimpleChatAnimaPromptRouter:
    """
    Split an Anima-style prompt JSON into editable parts with lock(latch) support.
    """

    def __init__(self):
        # Sticky values per field when lock_* is enabled
        self._latched: Dict[str, str] = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_text": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "strip_code_fence": ("BOOLEAN", {"default": True}),
                "reset_latches": ("BOOLEAN", {"default": False, "tooltip": "Clear all locked(latched) values."}),
            },
            "optional": {
                # Locks: when enabled, keep previous value even if JSON changes.
                "lock_quality": ("BOOLEAN", {"default": False}),
                "lock_count": ("BOOLEAN", {"default": False}),
                "lock_character": ("BOOLEAN", {"default": False}),
                "lock_series": ("BOOLEAN", {"default": False}),
                "lock_artist": ("BOOLEAN", {"default": False}),
                "lock_style": ("BOOLEAN", {"default": False}),
                "lock_environment": ("BOOLEAN", {"default": False}),
                "lock_tags": ("BOOLEAN", {"default": False}),
                "lock_neg": ("BOOLEAN", {"default": False}),

                # Manual overrides (active editing): if non-empty, override JSON output.
                "override_quality": ("STRING", {"multiline": True, "default": ""}),
                "override_count": ("STRING", {"multiline": False, "default": ""}),
                "override_character": ("STRING", {"multiline": True, "default": ""}),
                "override_series": ("STRING", {"multiline": False, "default": ""}),
                "override_artist": ("STRING", {"multiline": False, "default": ""}),
                "override_style": ("STRING", {"multiline": True, "default": ""}),
                "override_environment": ("STRING", {"multiline": True, "default": ""}),
                "override_tags": ("STRING", {"multiline": True, "default": ""}),
                "override_neg": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = (
        "STRING",  # quality_meta_year_safe
        "STRING",  # count
        "STRING",  # character
        "STRING",  # series
        "STRING",  # artist
        "STRING",  # style
        "STRING",  # environment
        "STRING",  # tags
        "STRING",  # neg
        "STRING",  # positive
        "STRING",  # negative
        "SIMPLECHAT_VARS",  # vars
        "SIMPLECHAT_JSON",  # obj
        "STRING",  # json_text_out
    )
    RETURN_NAMES = (
        "quality_meta_year_safe",
        "count",
        "character",
        "series",
        "artist",
        "style",
        "environment",
        "tags",
        "neg",
        "positive",
        "negative",
        "vars",
        "obj",
        "json_text",
    )
    FUNCTION = "route"
    CATEGORY = "SimpleChat/Utils"
    DESCRIPTION = "Parse Anima JSON into editable parts with lock(latch) support; outputs rebuilt positive/negative + vars + updated JSON."

    def _resolve_field(
        self,
        *,
        key: str,
        json_value: str,
        lock: bool,
        override: str,
        default: str = "",
    ) -> str:
        # 1) Manual override always wins if non-empty (supports active editing)
        ov = _as_str(override, "").strip()
        if ov:
            self._latched[key] = ov
            return ov

        # 2) Latch behavior when locked
        if lock:
            if key in self._latched:
                return self._latched[key]
            # First time locking: latch current JSON value (or default)
            cur = (json_value or "").strip() or default
            self._latched[key] = cur
            return cur

        # 3) Follow JSON when not locked
        return (json_value or "").strip() or default

    def route(
        self,
        json_text: str,
        strip_code_fence: bool = True,
        reset_latches: bool = False,
        lock_quality: bool = False,
        lock_count: bool = False,
        lock_character: bool = False,
        lock_series: bool = False,
        lock_artist: bool = False,
        lock_style: bool = False,
        lock_environment: bool = False,
        lock_tags: bool = False,
        lock_neg: bool = False,
        override_quality: str = "",
        override_count: str = "",
        override_character: str = "",
        override_series: str = "",
        override_artist: str = "",
        override_style: str = "",
        override_environment: str = "",
        override_tags: str = "",
        override_neg: str = "",
    ):
        if reset_latches:
            self._latched = {}

        raw = _strip_code_fence(json_text) if strip_code_fence else json_text
        data = _try_parse_json(raw) if isinstance(raw, str) else raw
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object (dict) at top-level.")

        # Extract with friendly aliases (support multiple schema variants)
        q_json = _first_nonempty(data.get("quality_meta_year_safe"), data.get("quality"))
        count_json = _first_nonempty(data.get("count"))
        character_json = _first_nonempty(data.get("character"), data.get("subject"))
        series_json = _first_nonempty(data.get("series"))
        artist_json = _first_nonempty(data.get("artist"))
        style_json = _first_nonempty(data.get("style"))
        env_json = _first_nonempty(data.get("environment"), data.get("env"), data.get("background"), data.get("scene"))
        tags_json = _first_nonempty(data.get("tags"))
        neg_json = _first_nonempty(data.get("neg"), data.get("negative"))

        # Resolve final values (override + lock/latch)
        q = self._resolve_field(key="quality_meta_year_safe", json_value=q_json, lock=lock_quality, override=override_quality)
        count = self._resolve_field(key="count", json_value=count_json, lock=lock_count, override=override_count)
        character = self._resolve_field(key="character", json_value=character_json, lock=lock_character, override=override_character)
        series = self._resolve_field(key="series", json_value=series_json, lock=lock_series, override=override_series)
        artist = self._resolve_field(key="artist", json_value=artist_json, lock=lock_artist, override=override_artist)
        style = self._resolve_field(key="style", json_value=style_json, lock=lock_style, override=override_style)
        environment = self._resolve_field(key="environment", json_value=env_json, lock=lock_environment, override=override_environment)
        tags = self._resolve_field(key="tags", json_value=tags_json, lock=lock_tags, override=override_tags)
        neg = self._resolve_field(key="neg", json_value=neg_json, lock=lock_neg, override=override_neg)

        # Always rebuild positive/negative from final parts (keeps consistency after edits)
        positive = _join_pieces(q, count, character, series, artist, style, environment, tags)
        # In Anima-parted schema, negative is expected to mirror `neg`.
        negative = neg

        # Build vars for Mustache usage (both plain + prefixed "anima.")
        vars_dict: Dict[str, Any] = {
            "quality_meta_year_safe": q,
            "count": count,
            "character": character,
            "series": series,
            "artist": artist,
            "style": style,
            "environment": environment,
            "tags": tags,
            "neg": neg,
            "positive": positive,
            "negative": negative,
            "anima.quality_meta_year_safe": q,
            "anima.count": count,
            "anima.character": character,
            "anima.series": series,
            "anima.artist": artist,
            "anima.style": style,
            "anima.environment": environment,
            "anima.tags": tags,
            "anima.neg": neg,
            "anima.positive": positive,
            "anima.negative": negative,
            # Chinese aliases (optional convenience)
            "正面提示词": positive,
            "负面提示词": negative,
            "背景": environment,
            "画师": artist,
            "角色": character,
            "风格": style,
            "通用标签": tags,
            "质量": q,
            "人数": count,
            "作品": series,
            "anima.正面提示词": positive,
            "anima.负面提示词": negative,
            "anima.背景": environment,
            "anima.画师": artist,
            "anima.角色": character,
            "anima.风格": style,
            "anima.通用标签": tags,
            "anima.质量": q,
            "anima.人数": count,
            "anima.作品": series,
        }

        # Produce updated JSON object (keep original keys, but ensure these fields are consistent)
        out_obj = dict(data)
        out_obj["quality_meta_year_safe"] = q
        out_obj["count"] = count
        out_obj["character"] = character
        out_obj["series"] = series
        out_obj["artist"] = artist
        out_obj["style"] = style
        out_obj["environment"] = environment
        out_obj["tags"] = tags
        out_obj["neg"] = neg
        out_obj["positive"] = positive
        out_obj["negative"] = negative

        json_text_out = json.dumps(out_obj, ensure_ascii=False, indent=2)

        return (
            q,
            count,
            character,
            series,
            artist,
            style,
            environment,
            tags,
            neg,
            positive,
            negative,
            vars_dict,
            out_obj,
            json_text_out,
        )

