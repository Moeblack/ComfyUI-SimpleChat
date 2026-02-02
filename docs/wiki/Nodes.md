# Nodes（节点清单）

分类路径均为 `SimpleChat` 或 `SimpleChat/Utils`（右键菜单里可搜到）。

---

## SimpleChat（主节点）

- **API Config**：统一配置 OpenAI / Claude / Gemini（支持刷新模型列表）
- **Chat**：文本对话（支持 `system`）
- **Chat with Image**：图文对话
- **Chat NoASS**：NoASS 角色扮演模式（实验性）
- **Gemini Image Gen / Edit**：Gemini 原生文生图/图片编辑

> 以上节点均支持可选输入 `vars`：用于把 `{{变量}}` 模板渲染进 prompt/system 等文本字段。

---

## SimpleChat/Utils（工具节点）

- **Text Input**：纯文本输入框（输出 STRING）
- **Text List (Batch)**：把多行文本拆成字符串列表（输出 LIST[STRING]，可驱动批次跑图）
- **Mustache Var**：定义变量（输出 `SIMPLECHAT_VARS` 字典，支持菊花链合并）
- **Mustache Render**：不经过 Chat，也能把 `{{变量}}` 渲染成纯文本（输出 STRING）
- **JSON Parse**：解析 JSON 并按 path 拆 8 路输出（支持 `a.b[0].c`、支持 ```json 代码块提取）
- **JSON Parse (16)**：同上，但固定 16 路输出端口
- **JSON -> Vars (Editable)**：任意 JSON 转胡子变量（可扁平化 `a.b.c` / `arr[0]`，支持覆盖）
- **Prompt JSON Unpack**：固定 schema 的“一键拆包”（强类型输出 + 自动生成 `vars`）
- **Anima Prompt Router (Editable)**：分段拆提示词（画师/风格/背景等）+ 支持手动覆盖 + 锁定锁存 + 输出重组后的 positive/negative 与更新后的 JSON
- **Anima XY Matrix (JSON List)**：生成 X×Y 交叉组合的 JSON 列表（用于画师/背景 XY 测试）
- **Image Grid (Batch)**：把 IMAGE batch 拼成一张网格表格图（便于画师/背景对比）
- **XY Plot (Labels)**：把 IMAGE batch 拼成带 X/Y 标签的“完整 XY 表格图”
- **Markdown Preview**：把文本以 Markdown 方式弹窗预览（已净化）

