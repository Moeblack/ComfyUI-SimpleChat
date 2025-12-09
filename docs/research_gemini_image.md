# Gemini Image Generation Research Notes

## Available Models

| Model | Use Case | Features |
|-------|----------|----------|
| `gemini-2.5-flash-image` | Fast, general image generation | Lower cost, faster |
| `gemini-3-pro-image-preview` | Professional asset production | Higher quality, 1K/2K/4K output |

## API Endpoint

```
POST https://generativelanguage.googleapis.com/v1beta/models/{model-id}:generateContent
```

## Request Format

### 关键：启用图像生成

必须在 `generationConfig` 中指定 `responseModalities`:

```json
{
  "contents": [{
    "parts": [
      {"text": "Generate an image of a cat"}
    ]
  }],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"]
  }
}
```

### 带图片输入的请求（图片编辑/参考）

```json
{
  "contents": [{
    "parts": [
      {"text": "Edit this image to add a hat"},
      {
        "inline_data": {
          "mime_type": "image/png",
          "data": "base64_encoded_image_data"
        }
      }
    ]
  }],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"]
  }
}
```

### Image Configuration

```json
{
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": {
      "aspectRatio": "16:9",
      "imageSize": "2K"
    }
  }
}
```

支持的 aspectRatio: "1:1", "16:9", "9:16", "5:4", "4:5", "3:4", "4:3"
支持的 imageSize: "1K", "2K", "4K"

## Response Format

```json
{
  "candidates": [{
    "content": {
      "parts": [
        {"text": "Here is your generated image:"},
        {
          "inlineData": {
            "mimeType": "image/png",
            "data": "base64_encoded_image_data"
          }
        }
      ]
    }
  }]
}
```

## Input Modalities

1. **Text-to-Image**: 纯文本提示词
2. **Text-and-Image-to-Image**: 文本 + 参考图片
3. **Multi-Reference Images**: 最多 14 张参考图片

## Authentication

使用 API Key:
```
x-goog-api-key: YOUR_API_KEY
```

或 Bearer Token:
```
Authorization: Bearer YOUR_TOKEN
```

## Special Features

- **Thought Signatures**: 多轮对话保持推理上下文
- **SynthID**: 自动添加 AI 生成图片水印
- **Grounding with Google Search**: 可使用搜索验证事实

## Implementation Notes for ComfyUI-SimpleChat

1. 需要支持自定义 base_url（用户可能使用代理）
2. 需要处理 base64 图片编解码
3. 需要支持图片输入作为参考
4. 返回的图片需要转换为 ComfyUI tensor 格式

## Reference

- https://ai.google.dev/gemini-api/docs/image-generation
- https://ai.google.dev/gemini-api/docs/imagen
