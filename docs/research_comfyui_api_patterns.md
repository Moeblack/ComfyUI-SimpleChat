# ComfyUI API Nodes Patterns Research

## 目录结构

ComfyUI 官方 API 节点位于 `/comfy_api_nodes/`:

```
comfy_api_nodes/
├── apis/              # Pydantic request/response models
├── util/              # 共享工具
│   ├── client.py      # HTTP 客户端 (sync_op, poll_op)
│   ├── _helpers.py    # 认证, base URL
│   ├── conversions.py # 图片/音频/视频转换
│   └── ...
├── nodes_openai.py    # OpenAI 节点
├── nodes_gemini.py    # Gemini 节点
└── ...
```

## 节点定义模式

### 新版 API 节点模式 (IO.ComfyNode)

```python
class MyApiNode(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="MyApiNode",
            display_name="My API Node",
            category="api node/category",
            inputs=[
                IO.String.Input("prompt", multiline=True),
                IO.Image.Input("image", optional=True),
            ],
            outputs=[
                IO.Image.Output("IMAGE"),
                IO.String.Output("TEXT"),
            ],
            hidden=[
                IO.Hidden.auth_token_comfy_org,
                IO.Hidden.api_key_comfy_org,
            ],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, prompt: str, image=None):
        # Implementation
        return IO.NodeOutput(result_image, result_text)
```

### 传统节点模式 (ComfyNodeABC)

```python
class MyNode(ComfyNodeABC):
    @classmethod
    def INPUT_TYPES(s) -> InputTypeDict:
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "text")
    FUNCTION = "execute"
    CATEGORY = "my_category"

    def execute(self, prompt, image=None):
        return (result_image, result_text)
```

## 图片处理

### Tensor 转 Base64

```python
from comfy_api_nodes.util import tensor_to_base64_string

base64_str = tensor_to_base64_string(image_tensor)
data_uri = f"data:image/png;base64,{base64_str}"
```

### Base64 转 Tensor

```python
import base64
from io import BytesIO
from comfy_api_nodes.util import bytesio_to_image_tensor

image_data = base64.b64decode(base64_string)
tensor = bytesio_to_image_tensor(BytesIO(image_data))
```

### Tensor 格式

ComfyUI 图片 tensor: `(B, H, W, C)` - Batch, Height, Width, Channels (RGBA)

## HTTP 请求

### 同步请求

```python
from comfy_api_nodes.util import sync_op

response = await sync_op(
    cls,
    ApiEndpoint(path="/api/endpoint", method="POST"),
    response_model=ResponseModel,
    data=RequestModel(...),
    timeout=3600.0,
)
```

### 轮询请求

```python
from comfy_api_nodes.util import poll_op

response = await poll_op(
    cls,
    ApiEndpoint(path="/api/status/{id}", method="GET"),
    response_model=ResponseModel,
    status_extractor=lambda r: r.status,
    completed_statuses=["completed"],
    failed_statuses=["failed"],
)
```

## 认证

官方节点使用 ComfyUI 代理认证。我们的自定义节点将支持：
1. 直接 API Key 输入
2. 自定义 base_url

## 重要发现

1. **无 Claude/Anthropic 集成** - 官方没有 Claude 节点
2. **代理模式** - 官方节点通过 ComfyUI 代理访问 API
3. **异步执行** - 所有 API 调用使用 async/await
4. **Pydantic 验证** - 请求/响应使用 Pydantic 模型

## 对我们的启示

由于我们要支持自定义 base_url 和直接 API 访问，我们将：
1. 使用传统节点模式（更简单，更灵活）
2. 直接使用 aiohttp/httpx 发请求
3. 手动处理认证
4. 复用 ComfyUI 的图片转换工具
