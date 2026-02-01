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
- **Mustache Var**：定义变量（输出 `SIMPLECHAT_VARS` 字典，支持菊花链合并）
- **Mustache Render**：不经过 Chat，也能把 `{{变量}}` 渲染成纯文本（输出 STRING）
- **JSON Parse**：解析 JSON 并按 path 拆 8 路输出（支持 `a.b[0].c`、支持 ```json 代码块提取）
- **Prompt JSON Unpack**：固定 schema 的“一键拆包”（强类型输出 + 自动生成 `vars`）
- **Markdown Preview**：把文本以 Markdown 方式弹窗预览（已净化）

