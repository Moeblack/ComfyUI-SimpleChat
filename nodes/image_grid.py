"""
Image Grid node (minimal).

Take a batch of images (B,H,W,C) and stitch into a single grid image.
Useful for artist/background batch testing.
"""

from __future__ import annotations

import math

import torch


class SimpleChatImageGrid:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "columns": ("INT", {"default": 4, "min": 1, "max": 64}),
                "padding": ("INT", {"default": 0, "min": 0, "max": 256}),
                "pad_color": (["black", "white"], {"default": "black"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "grid"
    CATEGORY = "SimpleChat/Utils"
    DESCRIPTION = "Stitch an IMAGE batch into a grid."

    def grid(self, images: torch.Tensor, columns: int = 4, padding: int = 0, pad_color: str = "black"):
        if images is None or not isinstance(images, torch.Tensor):
            raise ValueError("images must be a torch Tensor (ComfyUI IMAGE).")
        if images.dim() != 4:
            raise ValueError(f"Expected IMAGE tensor with 4 dims (B,H,W,C), got shape={tuple(images.shape)}")

        b, h, w, c = images.shape
        columns = max(1, int(columns))
        rows = int(math.ceil(b / columns)) if b > 0 else 1
        padding = max(0, int(padding))

        out_h = rows * h + max(0, rows - 1) * padding
        out_w = columns * w + max(0, columns - 1) * padding

        fill = 1.0 if (pad_color == "white") else 0.0
        canvas = images.new_full((1, out_h, out_w, c), fill)

        for idx in range(b):
            r = idx // columns
            col = idx % columns
            y = r * (h + padding)
            x = col * (w + padding)
            canvas[0, y : y + h, x : x + w, :] = images[idx]

        return (canvas,)

