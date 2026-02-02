"""
XY Plot (with labels) for IMAGE batch.

Takes an IMAGE batch (B,H,W,C) and stitches into a grid with X/Y labels.
This is meant for fast artist/background testing.
"""

from __future__ import annotations

import math
from typing import List, Tuple

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont


def _split_labels(text: str) -> List[str]:
    if not isinstance(text, str):
        return []
    raw = text.replace("\r\n", "\n").replace("\r", "\n")
    out = []
    for line in raw.split("\n"):
        s = (line or "").strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("//"):
            continue
        out.append(s)
    return out


def _to_pil(img: torch.Tensor) -> Image.Image:
    # img: (H,W,C) float 0..1
    arr = (img.detach().cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
    return Image.fromarray(arr, mode="RGB")


def _to_tensor(img: Image.Image) -> torch.Tensor:
    arr = np.array(img).astype(np.float32) / 255.0
    t = torch.from_numpy(arr)[None, ...]
    return t


class SimpleChatXYPlot:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "columns": ("INT", {"default": 4, "min": 1, "max": 64}),
                "x_labels": ("STRING", {"multiline": True, "default": ""}),
                "y_labels": ("STRING", {"multiline": True, "default": ""}),
                "padding": ("INT", {"default": 8, "min": 0, "max": 256}),
                "label_padding": ("INT", {"default": 8, "min": 0, "max": 256}),
                "bg_color": (["black", "white"], {"default": "black"}),
                "text_color": (["white", "black"], {"default": "white"}),
                "title": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "plot"
    CATEGORY = "SimpleChat/Utils"
    DESCRIPTION = "Create an XY Plot image (grid + axis labels) from an IMAGE batch."

    def plot(
        self,
        images: torch.Tensor,
        columns: int = 4,
        x_labels: str = "",
        y_labels: str = "",
        padding: int = 8,
        label_padding: int = 8,
        bg_color: str = "black",
        text_color: str = "white",
        title: str = "",
    ):
        if images is None or not isinstance(images, torch.Tensor):
            raise ValueError("images must be a torch Tensor (ComfyUI IMAGE).")
        if images.dim() != 4:
            raise ValueError(f"Expected IMAGE tensor with 4 dims (B,H,W,C), got shape={tuple(images.shape)}")

        b, h, w, c = images.shape
        columns = max(1, int(columns))
        rows = int(math.ceil(b / columns)) if b > 0 else 1
        padding = max(0, int(padding))
        label_padding = max(0, int(label_padding))

        xs = _split_labels(x_labels)
        ys = _split_labels(y_labels)

        # Try to align labels length with grid
        if len(xs) < columns:
            xs = xs + [""] * (columns - len(xs))
        if len(ys) < rows:
            ys = ys + [""] * (rows - len(ys))

        # Font
        font = ImageFont.load_default()

        # Measure label sizes
        tmp = Image.new("RGB", (10, 10), color=bg_color)
        draw_tmp = ImageDraw.Draw(tmp)

        def _text_size(s: str) -> Tuple[int, int]:
            if not s:
                return (0, 0)
            bbox = draw_tmp.textbbox((0, 0), s, font=font)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])

        title_w, title_h = _text_size(title.strip())
        x_h = max([_text_size(t)[1] for t in xs] + [0])
        y_w = max([_text_size(t)[0] for t in ys] + [0])

        # Layout margins
        top_margin = (title_h + label_padding) if title.strip() else 0
        top_margin += (x_h + label_padding) if (x_h > 0) else 0
        left_margin = (y_w + label_padding) if (y_w > 0) else 0

        grid_h = rows * h + max(0, rows - 1) * padding
        grid_w = columns * w + max(0, columns - 1) * padding

        out_w = left_margin + grid_w
        out_h = top_margin + grid_h

        bg = (0, 0, 0) if bg_color == "black" else (255, 255, 255)
        fg = (255, 255, 255) if text_color == "white" else (0, 0, 0)

        canvas = Image.new("RGB", (out_w, out_h), color=bg)
        draw = ImageDraw.Draw(canvas)

        # Title
        y_cursor = 0
        if title.strip():
            draw.text((left_margin, 0), title.strip(), fill=fg, font=font)
            y_cursor += title_h + label_padding

        # X labels row
        if x_h > 0:
            for col in range(columns):
                label = xs[col] if col < len(xs) else ""
                tw, th = _text_size(label)
                x0 = left_margin + col * (w + padding) + max(0, (w - tw) // 2)
                draw.text((x0, y_cursor), label, fill=fg, font=font)
            y_cursor += x_h + label_padding

        # Paste images + Y labels
        for idx in range(b):
            r = idx // columns
            col = idx % columns
            x = left_margin + col * (w + padding)
            y = y_cursor + r * (h + padding)
            canvas.paste(_to_pil(images[idx]), (x, y))

        if y_w > 0:
            for r in range(rows):
                label = ys[r] if r < len(ys) else ""
                tw, th = _text_size(label)
                lx = max(0, left_margin - label_padding - tw)
                ly = y_cursor + r * (h + padding) + max(0, (h - th) // 2)
                draw.text((lx, ly), label, fill=fg, font=font)

        return (_to_tensor(canvas),)

