# Anima Prompt Scheme（JSON + 内置胡子变量）

本方案用于：**LLM 只输出一个 JSON** → ComfyUI 里用 `Prompt JSON Unpack` **一键拆字段** → 直接接入你的图像工作流（positive/negative/参数），同时自动得到一套可复用的 Mustache 变量。

---

## 1) LLM 必须输出的 JSON Schema（固定）

> 你在 `docs/anima_prompt.md` 的 System Prompt 已经强制要求输出这个结构。

```json
{
  "positive": "...",
  "negative": "...",
  "width": 1024,
  "height": 1024,
  "steps": 40,
  "cfg": 4.5,
  "sampler": "er_sde",
  "seed": -1,
  "notes": "1-3条简短技巧/提醒"
}
```

---

## 2) `Prompt JSON Unpack` 的输出（端口）

- **positive/negative**: `STRING`
- **width/height/steps/seed**: `INT`
- **cfg**: `FLOAT`
- **sampler**: `SAMPLER`（对象，适配 custom-sampling 工作流）
- **sampler_name**: `STRING`（文本形式，便于展示/拼接/日志）
- **notes**: `STRING`
- **vars**: `SIMPLECHAT_VARS`（下文“内置胡子变量”）
- **obj**: `SIMPLECHAT_JSON`（完整 dict）

---

## 3) 内置胡子变量（Mustache Vars）

把 `Prompt JSON Unpack.vars` 接到任何 SimpleChat 节点的 `vars` 输入后，就能在 `prompt/system` 里直接使用这些变量：

### 3.1 推荐使用（带前缀，避免变量冲突）

- `{{anima.positive}}`
- `{{anima.negative}}`
- `{{anima.width}}`
- `{{anima.height}}`
- `{{anima.steps}}`
- `{{anima.cfg}}`
- `{{anima.sampler}}` / `{{anima.sampler_name}}`
- `{{anima.seed}}`
- `{{anima.notes}}`

### 3.2 简写（不带前缀）

- `{{positive}}`
- `{{negative}}`
- `{{width}}`
- `{{height}}`
- `{{steps}}`
- `{{cfg}}`
- `{{sampler}}` / `{{sampler_name}}`
- `{{seed}}`
- `{{notes}}`

### 3.3 中文别名（可选）

- `{{正面提示词}}` / `{{anima.正面提示词}}`
- `{{负面提示词}}` / `{{anima.负面提示词}}`
- `{{宽}}` / `{{anima.宽}}`
- `{{高}}` / `{{anima.高}}`
- `{{步数}}` / `{{anima.步数}}`
- `{{采样器}}` / `{{anima.采样器}}`
- `{{种子}}` / `{{anima.种子}}`
- `{{备注}}` / `{{anima.备注}}`

---

## 4) 最小工作流接线（推荐）

1) `SimpleChatText`（system 用 `docs/anima_prompt.md`，prompt 写你的需求）
2) 输出接 `Prompt JSON Unpack.json_text`
3) 把 `positive/negative/width/...` 分别接到你现有出图工作流对应口
4) 如需二次加工：把 `Prompt JSON Unpack.vars` 接到下一个 `SimpleChatText.vars`，就能用上面的胡子变量复用字段

