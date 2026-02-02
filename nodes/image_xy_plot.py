"""
XY Plot (with labels) for IMAGE batch.

Takes an IMAGE batch (B,H,W,C) and stitches into a grid with X/Y labels.
This is meant for fast artist/background testing.
"""

from __future__ import annotations

import math
from typing import Any, List, Tuple

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont


def _first(v: Any, default: Any = None) -> Any:
    if isinstance(v, (list, tuple)):
        return v[0] if len(v) > 0 else default
    return v


def _flatten_images(images: Any) -> torch.Tensor:
    """
    Accept either:
    - torch.Tensor: (B,H,W,C) or (H,W,C)
    - list/tuple of torch.Tensor batches (common when upstream is OUTPUT_IS_LIST)
    Return a single torch.Tensor (B,H,W,C).
    """
    if isinstance(images, torch.Tensor):
        t = images
        if t.dim() == 3:
            t = t.unsqueeze(0)
        return t

    if isinstance(images, (list, tuple)):
        batches: list[torch.Tensor] = []
        for item in images:
            if item is None:
                continue
            if isinstance(item, torch.Tensor):
                t = item
                if t.dim() == 3:
                    t = t.unsqueeze(0)
                if t.dim() != 4:
                    raise ValueError(f"Expected IMAGE tensor with 4 dims (B,H,W,C), got shape={tuple(t.shape)}")
                batches.append(t)
                continue
            if isinstance(item, (list, tuple)):
                batches.append(_flatten_images(item))
                continue
            raise ValueError(f"Unsupported images list element type: {type(item)}")
        if not batches:
            raise ValueError("images list is empty.")
        return torch.cat(batches, dim=0)

    raise ValueError(f"Unsupported images type: {type(images)}")


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
    # If upstream provides a list (from OUTPUT_IS_LIST), run ONCE with the whole list.
    INPUT_IS_LIST = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
            },
            "optional": {
                # These support both widget input and upstream connection (forceInput)
                "columns": ("INT", {"default": 4, "min": 1, "max": 64, "forceInput": True}),
                "x_labels": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "y_labels": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
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
        images: Any,
        columns: int = 4,
        x_labels: str = "",
        y_labels: str = "",
        padding: int = 8,
        label_padding: int = 8,
        bg_color: str = "black",
        text_color: str = "white",
        title: str = "",
    ):
        # When INPUT_IS_LIST=True, many inputs may arrive as lists; pick the first.
        columns = _first(columns, 4)
        x_labels = _first(x_labels, "") or ""
        y_labels = _first(y_labels, "") or ""
        padding = _first(padding, 8)
        label_padding = _first(label_padding, 8)
        bg_color = _first(bg_color, "black")
        text_color = _first(text_color, "white")
        title = _first(title, "") or ""

        images = _flatten_images(images)
        if images is None or not isinstance(images, torch.Tensor):
            raise ValueError("images must be a torch Tensor (ComfyUI IMAGE) or a list of IMAGE tensors.")
        if images.dim() != 4:
            raise ValueError(f"Expected IMAGE tensor with 4 dims (B,H,W,C), got shape={tuple(images.shape)}")

        b, h, w, c = images.shape
        columns = max(1, int(columns))
        padding = max(0, int(padding))
        label_padding = max(0, int(label_padding))

        xs = _split_labels(x_labels)
        ys = _split_labels(y_labels)
        has_x_labels = len(xs) > 0
        has_y_labels = len(ys) > 0

        # Prefer labels to define grid shape (scientific-style XY plots).
        if has_x_labels:
            columns = max(1, len(xs))

        rows = int(math.ceil(b / columns)) if b > 0 else 1
        if has_y_labels:
            rows = max(1, len(ys))

        # Ensure grid is large enough to hold all images.
        if b > rows * columns:
            rows = int(math.ceil(b / columns))

        # Pad labels if too short.
        if len(xs) < columns:
            xs = xs + [""] * (columns - len(xs))
        if len(ys) < rows:
            ys = ys + [""] * (rows - len(ys))

        # Detect triangular inputs for square grids:
        # - upper_triangle: N(N+1)/2 images (row-major over cells where col>=row)
        # - diagonal_only: N images (row-major over diag cells)
        triangle_mode = None  # "upper_triangle" | "diagonal_only"
        if has_x_labels and has_y_labels and rows == columns:
            n = columns
            if b == (n * (n + 1)) // 2:
                triangle_mode = "upper_triangle"
            elif b == n:
                triangle_mode = "diagonal_only"

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

        # Paste images (+ fill masked cells for triangular layouts)
        # Use a mid-gray mask for the unused half (common in scientific matrices).
        mask_color = (64, 64, 64) if bg_color == "black" else (220, 220, 220)
        mask = Image.new("RGB", (w, h), color=mask_color)

        if triangle_mode == "upper_triangle":
            idx = 0
            for r in range(rows):
                for col in range(columns):
                    x = left_margin + col * (w + padding)
                    y = y_cursor + r * (h + padding)
                    if col < r:
                        canvas.paste(mask, (x, y))
                        continue
                    if idx < b:
                        canvas.paste(_to_pil(images[idx]), (x, y))
                        idx += 1
                    else:
                        canvas.paste(mask, (x, y))
        elif triangle_mode == "diagonal_only":
            idx = 0
            for r in range(rows):
                for col in range(columns):
                    x = left_margin + col * (w + padding)
                    y = y_cursor + r * (h + padding)
                    if col == r and idx < b:
                        canvas.paste(_to_pil(images[idx]), (x, y))
                        idx += 1
                    else:
                        canvas.paste(mask, (x, y))
        else:
            # Standard row-major fill
            max_cells = rows * columns
            for idx in range(min(b, max_cells)):
                r = idx // columns
                col = idx % columns
                x = left_margin + col * (w + padding)
                y = y_cursor + r * (h + padding)
                canvas.paste(_to_pil(images[idx]), (x, y))
            # Fill remaining cells (if any) for a tidy grid.
            if b < max_cells:
                for idx in range(b, max_cells):
                    r = idx // columns
                    col = idx % columns
                    x = left_margin + col * (w + padding)
                    y = y_cursor + r * (h + padding)
                    canvas.paste(mask, (x, y))

        if y_w > 0:
            for r in range(rows):
                label = ys[r] if r < len(ys) else ""
                tw, th = _text_size(label)
                lx = max(0, left_margin - label_padding - tw)
                ly = y_cursor + r * (h + padding) + max(0, (h - th) // 2)
                draw.text((lx, ly), label, fill=fg, font=font)

        return (_to_tensor(canvas),)

