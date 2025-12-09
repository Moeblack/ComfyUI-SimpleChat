"""
Image conversion utilities for ComfyUI tensors.
"""
import base64
from io import BytesIO
import torch
import numpy as np
from PIL import Image


def tensor_to_pil(tensor: torch.Tensor) -> Image.Image:
    """
    Convert ComfyUI tensor to PIL Image.

    Args:
        tensor: Shape (B, H, W, C) or (H, W, C), values 0-1

    Returns:
        PIL Image (first image if batched)
    """
    if tensor.dim() == 4:
        tensor = tensor[0]  # Take first image from batch

    # Convert to numpy and scale to 0-255
    arr = (tensor.cpu().numpy() * 255).astype(np.uint8)

    # Handle different channel counts
    if arr.shape[-1] == 1:
        arr = arr.squeeze(-1)
        return Image.fromarray(arr, mode='L')
    elif arr.shape[-1] == 3:
        return Image.fromarray(arr, mode='RGB')
    elif arr.shape[-1] == 4:
        return Image.fromarray(arr, mode='RGBA')
    else:
        raise ValueError(f"Unsupported channel count: {arr.shape[-1]}")


def pil_to_tensor(image: Image.Image) -> torch.Tensor:
    """
    Convert PIL Image to ComfyUI tensor.

    Args:
        image: PIL Image

    Returns:
        Tensor shape (1, H, W, C), values 0-1
    """
    # Convert to RGB if needed
    if image.mode == 'RGBA':
        pass  # Keep alpha
    elif image.mode != 'RGB':
        image = image.convert('RGB')

    # Convert to tensor
    arr = np.array(image).astype(np.float32) / 255.0
    tensor = torch.from_numpy(arr)

    # Add batch dimension
    if tensor.dim() == 2:  # Grayscale
        tensor = tensor.unsqueeze(-1)
    tensor = tensor.unsqueeze(0)

    return tensor


def tensor_to_base64(tensor: torch.Tensor, format: str = "PNG") -> str:
    """
    Convert ComfyUI tensor to base64 string.

    Args:
        tensor: ComfyUI image tensor
        format: Image format (PNG, JPEG, WEBP)

    Returns:
        Base64 encoded string
    """
    pil_image = tensor_to_pil(tensor)

    # Convert RGBA to RGB for JPEG
    if format.upper() == "JPEG" and pil_image.mode == "RGBA":
        pil_image = pil_image.convert("RGB")

    buffer = BytesIO()
    pil_image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def base64_to_tensor(b64_string: str) -> torch.Tensor:
    """
    Convert base64 string to ComfyUI tensor.

    Args:
        b64_string: Base64 encoded image

    Returns:
        ComfyUI image tensor (1, H, W, C)
    """
    image_data = base64.b64decode(b64_string)
    image = Image.open(BytesIO(image_data))
    return pil_to_tensor(image)


def create_data_uri(tensor: torch.Tensor, mime_type: str = "image/png") -> str:
    """
    Create a data URI from tensor for API requests.

    Args:
        tensor: ComfyUI image tensor
        mime_type: MIME type (image/png, image/jpeg, image/webp)

    Returns:
        Data URI string
    """
    format_map = {
        "image/png": "PNG",
        "image/jpeg": "JPEG",
        "image/webp": "WEBP",
    }
    format = format_map.get(mime_type, "PNG")
    b64 = tensor_to_base64(tensor, format)
    return f"data:{mime_type};base64,{b64}"
