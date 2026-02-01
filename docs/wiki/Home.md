# ComfyUI-SimpleChat Wiki

这份 Wiki 用于集中放置插件的使用文档与工作流方案。

> 维护方式：本仓库的 `docs/wiki/` 会通过 GitHub Actions **自动同步**到 GitHub Wiki（原生 Wiki）。

---

## 快速入口

- **节点清单与用途**：见 `Nodes.md`
- **Anima（circlestone-labs/Anima）专用方案**：见 `Anima.md`
- **Wiki 自动发布（配置/排错）**：见 `Wiki-Sync.md`

---

## 推荐工作流（Anima：LLM→JSON→拆字段→接入出图）

核心思路：
1) LLM **只输出一个固定 JSON**（包含 positive/negative/width/height/steps/cfg/sampler/seed/notes）
2) 用 `Prompt JSON Unpack` 把 JSON **拆成多个强类型端口**（STRING/INT/FLOAT/SAMPLER）
3) 把各字段直接接到 ComfyUI 的对应输入口（避免“只接收 positive 不接收 json”的问题）
4) 同时得到 `vars`（内置胡子变量）用于复用/二次加工

示例工作流文件：
- `assets/AnimaPromptScheme.json`

