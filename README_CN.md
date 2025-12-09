# ComfyUI-SimpleChat

ComfyUI 的极简 LLM 聊天节点。轻松连接 OpenAI, Claude, Gemini 以及本地 LLM。

[English](README.md) | [中文](README_CN.md)

![工作流示例](assets/example-workflow.webp)

[查看示例工作流 JSON](assets/SimpleChatExample.json)

## 特性 (Features)

- **一站式配置**: 一个强大的配置节点即可搞定所有提供商。
- **动态获取模型**: 点击按钮即可获取您的 API Key 实际可用的**实时模型列表**。告别写死的列表！
- **通用兼容性**: 支持官方 API 以及任何兼容 OpenAI 格式的代理/本地接口 (如 LM Studio, Ollama)。
- **多模态支持**: 使用具备视觉能力的模型与图片进行对话。
- **NoASS 角色扮演模式 (实验性)**: 专为硬核角色扮演设计的节点，支持 Assistant Prefill (预填) 技术。
- **Gemini 原生功能**: 专为 Gemini 设计的文生图和图片编辑节点。

## 安装 (Installation)

1. 进入您的 `ComfyUI/custom_nodes` 文件夹并克隆本仓库：
```bash
git clone https://github.com/yourname/ComfyUI-SimpleChat.git
```
2. 重启 ComfyUI。

## 使用指南 (Usage Guide)

### 1. API 配置 (核心步骤)

一切从 **API Config** 节点开始。

1.  **添加节点**: 右键 -> `SimpleChat` -> `API Config`。
2.  **选择提供商 (Provider)**: 选择 `openai`, `claude`, 或 `gemini`。
3.  **输入 API Key**: 粘贴您的密钥。
    *   *OpenAI*: `sk-...`
    *   *Claude*: `sk-ant-...`
    *   *Gemini*: 您的 Google AI Studio key。
4.  **Base URL (可选)**:
    *   使用官方 API 时请留空。
    *   如果您使用代理、中转或本地 LLM，请在此输入 URL。
    *   *例如*: `https://api.deepseek.com/v1` 或 `http://localhost:1234/v1`。
5.  **选择模型 (Select Model)**:
    *   **点击 "Refresh Models" 按钮**。
    *   节点会连接 API 并获取您当前可用的**实时模型列表**。
    *   从下拉菜单中选择您想用的模型。

### 2. 基础对话 (Basic Chat)
用于标准的文本生成或问答。

*   **节点**: `Chat`
*   **连接**: 将 **API Config** 的 `config` 输出连接到 **Chat** 的 `config` 输入。
*   **输入**: 在 `text` 中输入您的提示词。
*   **输出**: 返回 AI 的回复字符串。

### 3. 图片对话 (Chat with Images)
让 AI 分析或描述图片。

*   **节点**: `Chat with Image`
*   **连接**:
    *   连接 **API Config** 的 `config`。
    *   连接一张图片 (来自 `Load Image` 节点) 到 `image` 输入。
*   **输入**: 输入提示词 (例如："描述这张图片")。

### 4. NoASS 角色扮演 (Chat NoASS - Experimental)
"No Assistant" (NoASS) 节点专为**硬核角色扮演和创意写作**设计。它利用 Assistant Prefill 技术，强行规定 AI 回复的开头，从而打破角色的废话限制。

*   **节点**: `Chat NoASS (Exp)`
*   **输入**:
    *   **Scenario Instructions (场景指令)**: (对应 User 消息) 定义世界观、角色设定和规则。这是舞台背景。
    *   **User Action (用户动作)**: 您当前轮次的动作或对话。
    *   **Prefill Start (预填开头 - 可选)**: 强行写下 AI 回复的前几个字。AI **必须**接着这几个字往下写。这是控制语气和破除限制的神器。
    *   **History (历史)**: 将输出的 `history` 连接到下一个节点的 `history` 输入，以保持对话连续性。

### 5. Gemini 文生图 (Gemini Image Generation)
使用 Google Gemini 模型生成图片。

*   **节点**: `Gemini Image Gen`
*   **要求**: **API Config** 中必须选择 `gemini` 提供商。
*   **输出**: 生成标准的 ComfyUI IMAGE。

### 6. Gemini 图片编辑 (Gemini Image Edit)
通过文字指令修改现有图片。

*   **节点**: `Gemini Image Edit`
*   **输入**: 原图 (Source image) + 遮罩 (Mask image) + 提示词 (Prompt)。

## 常见问题 (FAQ)

**Q: 列表里找不到我要的模型。**
A: 请确保 API Key 和 Base URL 输入正确，然后点击 **Refresh Models**。只要 API 支持列出模型，它们就会显示出来。如果不支持，您可以尝试直接在下拉框中手动输入模型名称（如果 UI 允许）或检查服务商文档。

**Q: 我可以用本地模型吗？**
A: 可以！提供商选择 `openai`，将 **Base URL** 设置为您本地服务的地址 (例如 `http://127.0.0.1:1234/v1`)，然后点击 Refresh。

**Q: 下拉框是空的。**
A: 请检查网络连接和 API Key。如果 API Key 无效或网络不通，列表将无法填充。

## 许可证 (License)

MIT
