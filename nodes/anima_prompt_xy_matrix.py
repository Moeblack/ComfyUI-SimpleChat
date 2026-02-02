"""
Anima Prompt XY Matrix (JSON list generator).

Goal:
- Given ONE base JSON prompt (Anima-style parts),
- Provide X list (e.g. artist list) and Y list (e.g. background list),
- Generate cross-product JSON_TEXT list in row-major order:
  y0: x0, x1, x2...
  y1: x0, x1, x2...
- Also output columns (len(x)) and labels texts for plotting.

This node does NOT run sampling. It only generates the prompt JSON list.
Downstream you can connect to:
  Prompt JSON Unpack -> CLIP/KSampler -> Image Grid / XY Plot
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Tuple


_CODE_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_LINE_COMMENT_RE = re.compile(r"^\s*(//|#).*$", re.MULTILINE)


def _strip_code_fence(text: str) -> str:
    if not isinstance(text, str):
        return text
    m = _CODE_FENCE_RE.search(text)
    return m.group(1) if m else text


def _extract_first_json_object(text: str) -> str | None:
    """
    Extract the first top-level JSON object {...} from a noisy text.
    Uses brace counting and skips braces inside quoted strings.
    """
    if not isinstance(text, str):
        return None
    s = text.lstrip("\ufeff").strip()
    start = s.find("{")
    if start == -1:
        return None

    depth = 0
    in_str: str | None = None
    esc = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_str is not None:
            if esc:
                esc = False
                continue
            if ch == "\\":
                esc = True
                continue
            if ch == in_str:
                in_str = None
            continue

        if ch == '"' or ch == "'":
            in_str = ch
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return s[start : i + 1]
    return None


def _repair_missing_commas(text: str) -> str:
    """
    Best-effort repair for a common hand-edited JSON mistake:
    missing commas between top-level lines, e.g.
      "a": "x"
      "b": "y"
    """
    if not isinstance(text, str):
        return text
    s = text
    # Add comma before a new line starting with a quote when previous line looks like a value.
    s = re.sub(
        r'("|\d|\]|\}|true|false|null)\s*\n(\s*")',
        r"\1,\n\2",
        s,
        flags=re.IGNORECASE,
    )
    return s


def _try_parse_json(text: str) -> Any:
    if not isinstance(text, str):
        return text

    s = text.lstrip("\ufeff")
    # Strip full-line comments (common when users annotate JSON)
    s = _LINE_COMMENT_RE.sub("", s).strip()

    candidates: list[str] = [s]
    extracted = _extract_first_json_object(s)
    if extracted and extracted != s:
        candidates.append(extracted)

    last_err: Exception | None = None
    for cand in candidates:
        try:
            return json.loads(cand)
        except Exception as e:
            last_err = e
            # trailing commas
            cleaned = re.sub(r",\s*([}\]])", r"\1", cand)
            cleaned = _repair_missing_commas(cleaned)
            cleaned = _LINE_COMMENT_RE.sub("", cleaned).strip()
            try:
                return json.loads(cleaned)
            except Exception as e2:
                last_err = e2

    # Provide a more actionable message
    if isinstance(last_err, json.JSONDecodeError):
        msg = (
            f"JSON 解析失败：{last_err.msg} (line {last_err.lineno}, col {last_err.colno}). "
            f"常见原因：上一行结尾缺少逗号、或 JSON 里混入了说明文字。"
        )
        raise ValueError(msg) from last_err
    raise last_err if last_err is not None else ValueError("JSON 解析失败：未知错误")


def _split_list(text: str) -> List[str]:
    if not isinstance(text, str):
        return []
    raw = text.replace("\r\n", "\n").replace("\r", "\n")
    items = []
    for line in raw.split("\n"):
        s = (line or "").strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        items.append(s)
    return items


def _as_str(v: Any, default: str = "") -> str:
    if v is None:
        return default
    if isinstance(v, str):
        return v
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return str(v)


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


def _get_field_key(field: str) -> str:
    # Normalize UI field selection to JSON key
    mapping = {
        "quality": "quality_meta_year_safe",
        "count": "count",
        "character": "character",
        "series": "series",
        "artist": "artist",
        "style": "style",
        "environment": "environment",
        "tags": "tags",
        "neg": "neg",
    }
    return mapping.get(field, field)


class SimpleChatAnimaPromptXYMatrix:
    @classmethod
    def INPUT_TYPES(cls):
        fields = ["artist", "style", "environment", "character", "series", "tags", "quality", "count", "neg"]
        return {
            "required": {
                "json_text": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "strip_code_fence": ("BOOLEAN", {"default": True}),
                "x_field": (fields, {"default": "artist"}),
                "x_list": ("STRING", {"multiline": True, "default": "@artist1\n@artist2"}),
                "y_field": (fields, {"default": "environment"}),
                "y_list": ("STRING", {"multiline": True, "default": "sunset street\nnight city"}),
                "include_environment_in_positive": ("BOOLEAN", {"default": True}),
                "auto_y_from_x_when_empty": ("BOOLEAN", {"default": True, "tooltip": "If y_list is empty, reuse x_list (useful for artist x artist matrix)."}),
                "same_field_behavior": (["override", "combine"], {"default": "combine", "tooltip": "When x_field == y_field (e.g. artist), choose overwrite or combine."}),
                "pair_join": (["newline", "comma", "space", "custom"], {"default": "newline"}),
                "custom_join": ("STRING", {"default": "\\n", "tooltip": "Used when pair_join=custom. Use \\n for newline."}),
                "diagonal_single": ("BOOLEAN", {"default": True, "tooltip": "When X==Y, use single value on diagonal (recommended)."}),
            }
        }

    RETURN_TYPES = (
        "STRING",  # json_text (list)
        "INT",     # columns
        "STRING",  # x_labels (multiline)
        "STRING",  # y_labels (multiline)
    )
    RETURN_NAMES = ("json_text", "columns", "x_labels", "y_labels")
    OUTPUT_IS_LIST = (True, False, False, False)
    FUNCTION = "build"
    CATEGORY = "SimpleChat/Utils"
    DESCRIPTION = "Generate cross-product JSON list for XY testing (artist x background, etc.)."

    def build(
        self,
        json_text: str,
        strip_code_fence: bool = True,
        x_field: str = "artist",
        x_list: str = "",
        y_field: str = "environment",
        y_list: str = "",
        include_environment_in_positive: bool = True,
        auto_y_from_x_when_empty: bool = True,
        same_field_behavior: str = "combine",
        pair_join: str = "newline",
        custom_join: str = "\\n",
        diagonal_single: bool = True,
    ):
        raw = _strip_code_fence(json_text) if strip_code_fence else json_text
        base = _try_parse_json(raw) if isinstance(raw, str) else raw
        if not isinstance(base, dict):
            raise ValueError("Expected a JSON object (dict) at top-level.")

        xs = _split_list(x_list)
        ys = _split_list(y_list)
        if not xs:
            xs = [""]
        if not ys:
            ys = xs[:] if auto_y_from_x_when_empty else [""]

        x_key = _get_field_key(x_field)
        y_key = _get_field_key(y_field)

        def _join_str() -> str:
            if pair_join == "comma":
                return ", "
            if pair_join == "space":
                return " "
            if pair_join == "custom":
                return (custom_join or "").replace("\\n", "\n")
            return "\n"  # newline

        def _combine(a: str, b: str) -> str:
            a = (a or "").strip()
            b = (b or "").strip()
            if not a:
                return b
            if not b:
                return a
            if diagonal_single and a == b:
                return a
            return f"{a}{_join_str()}{b}"

        def _build_one(xv: str, yv: str) -> str:
            obj = dict(base)
            if x_key and y_key and x_key == y_key:
                if same_field_behavior == "combine":
                    obj[x_key] = _combine(xv, yv)
                else:
                    # override: y overwrites x (old behavior)
                    obj[x_key] = yv if (yv or "").strip() else xv
            else:
                if x_key:
                    obj[x_key] = xv
                if y_key:
                    obj[y_key] = yv

            # Keep alias fields in sync for neg/negative
            if x_key == "neg":
                obj["negative"] = xv
            if y_key == "neg":
                obj["negative"] = yv

            # Rebuild positive/negative from parts (compatible with our router scheme)
            q = _as_str(obj.get("quality_meta_year_safe", obj.get("quality", "")), "")
            count = _as_str(obj.get("count", ""), "")
            character = _as_str(obj.get("character", ""), "")
            series = _as_str(obj.get("series", ""), "")
            artist = _as_str(obj.get("artist", ""), "")
            style = _as_str(obj.get("style", ""), "")
            env = _as_str(obj.get("environment", obj.get("background", obj.get("scene", ""))), "")
            tags = _as_str(obj.get("tags", ""), "")
            neg = _as_str(obj.get("neg", obj.get("negative", "")), "")

            if include_environment_in_positive:
                positive = _join_pieces(q, count, character, series, artist, style, env, tags)
            else:
                positive = _join_pieces(q, count, character, series, artist, style, tags)

            obj["positive"] = positive
            obj["neg"] = neg
            obj["negative"] = neg

            return json.dumps(obj, ensure_ascii=False, indent=2)

        # Row-major (y rows)
        out_list: List[str] = []
        for yv in ys:
            for xv in xs:
                out_list.append(_build_one(xv, yv))

        columns = len(xs)
        x_labels = "\n".join(xs)
        y_labels = "\n".join(ys)

        return (out_list, columns, x_labels, y_labels)

