# Anima（circlestone-labs/Anima）专用方案

目标：在 ComfyUI 里用 Anima 生成高质量二次元/插画向图像（非写实、非摄影）。

---

## 1) 强制 JSON 输出（推荐）

建议你在 `Chat.system` 中使用仓库提供的模板（已强制“只输出一个 JSON”）：
- `docs/anima_prompt.md`

LLM 输出 JSON schema（固定）：

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

## 2) 一键拆字段（避免“只能接 positive 不能接 json”）

把 LLM 的输出接到：
- `Prompt JSON Unpack.json_text`

你会得到强类型输出口（可直接接到 ComfyUI 节点）：
- `positive/negative`（STRING）
- `width/height/steps/seed`（INT）
- `cfg`（FLOAT）
- `sampler`（SAMPLER 对象，用于 custom-sampling 图）
- `sampler_name`（STRING，便于展示/拼接）
- `notes`（STRING）

---

## 3) 内置胡子变量（vars）

`Prompt JSON Unpack` 同时输出 `vars`（`SIMPLECHAT_VARS`），可直接用于 Mustache 模板渲染：

推荐用带前缀（防冲突）：
- `{{anima.positive}}` / `{{anima.negative}}`
- `{{anima.width}}` / `{{anima.height}}`
- `{{anima.steps}}` / `{{anima.cfg}}`
- `{{anima.sampler}}` / `{{anima.sampler_name}}`
- `{{anima.seed}}` / `{{anima.notes}}`

也支持不带前缀的简写：`{{positive}}`、`{{width}}` 等；并提供中文别名（如 `{{正面提示词}}`）。

更完整的变量清单见：
- `docs/anima_scheme.md`

---

## 4) 规则要点（给提示词工程）

- **标签顺序固定**：
  `[质量/元数据/年份/安全] [人数] [角色名] [作品名] [画师] [通用标签]`
- **画师必须 @**：例如 `@xxx`
- **混合输入**：tags + 自然语言（自然语言建议至少 2 句，复杂构图更要写清楚）
- **默认参数**：约 1MP；steps 30–50；cfg 4–5；sampler 优先 `er_sde`
- **安全标签**：safe/sensitive/nsfw/explicit 必须明确；negative 里写相反约束
- **避免写实**：不要用 photo/realistic/皮肤毛孔等措辞
- **非二次元风格**：第一行写 `ye-pop` 或 `deviantart`，换行后再给标题/描述与正常标签行

