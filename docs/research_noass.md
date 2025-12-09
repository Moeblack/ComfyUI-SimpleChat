# NoASS Research Notes

## What is NoASS?

NoASS (No Assistant) 是一种用于角色扮演和创意写作的提示词方法论。它将基于聊天的助手交互转换为统一的叙事格式。

## Core Concept

传统聊天是 human/assistant 轮流对话，NoASS 将整个 roleplay 合并成一个连续的故事，用户通过编辑来贡献角色动作。

## Key Motivation

1. **消除角色偏见**: 传统聊天模型对 human 角色有内在偏见，往往给予不合理的优势
2. **解决统一响应长度问题**: 标准聊天训练鼓励一致的回答长度，而动态叙事需要变化的响应规模
3. **消除闭合模式**: 传统响应以隐式呼吁用户结束（反问句），破坏沉浸感
4. **平等对待角色**: 所有角色被平等对待，因为没有角色正式"属于"任何一方

## Technical Implementation

### Context Transformation

**传统 ChatML 格式:**
```
<|im_start|>user
[Instructions]
<|im_end|>
<|im_start|>assistant
[Greeting]
<|im_end|>
<|im_start|>user
[User action]
<|im_end|>
```

**NoASS 格式:**
```
<|im_start|>user
[Instructions for story with all characters]
<|im_start|>assistant
[Greeting]
{{user}}: [user's action]
{{char}}: [character's action]
...
```

关键机制：所有 roleplay 变成单个预填充的 assistant 消息，用户输入被"拼接"到叙事中，使用角色前缀标记。

## Formatting Standards

- 一段 = 一个角色前缀 (`**char name:**`)
- 前缀下：*动作*、"对话"、'思想'，顺序任意
- 最小叙事描述；主要动作使用前缀
- 用户响应省略自己的前缀（扩展自动插入）

## Stop Token Mechanism

使用用户角色的前缀作为停止令牌，防止模型为玩家角色编写对话。这是防止模型为用户生成动作的关键。

## Implementation for ComfyUI-SimpleChat

在我们的实现中，NoASS 功能将：
1. 允许用户选择是否启用 NoASS 模式
2. 自动处理消息格式转换
3. 支持自定义角色前缀
4. 使用用户前缀作为停止字符串

## Reference

- https://rentry.org/noass_ext
