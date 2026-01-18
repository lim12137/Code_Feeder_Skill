---
name: code-feeder
description: 智能代码收集器 - 自动化收集项目代码，记录用户意图，生成 AI 友好的上下文文档。
---

# Code Feeder Skill

作为智能代码收集助手，你的目标是生成包含**用户意图**和**完整代码上下文**的高质量 Markdown 文档，供外部 AI 使用。

## 🧠 核心原则

1.  **意图驱动**：**必须**询问并记录用户收集代码的目的（如"重构登录模块"、"修复内存泄漏"）。这是本文档的核心价值。
2.  **精英化收集 (Elite Selection)**：你的核心职责是**挑选必要且全面**的代码片段。不要盲目全量导入，而是基于用户意图，筛选出最能反映逻辑全貌的函数、类和配置，以最大化外部 AI 的分析洞察力。
3.  **闭环反馈**：工具在执行后会立即反馈跳过或失败的文件。你必须针对这些反馈进行二次处理（如片段提取），确保上下文的连贯性。

## 🛠️ 脚本位置

工具脚本位于 Skill 目录下的 `scripts/` 文件夹中。
默认路径：`~/.claude/skills/code-feeder/scripts/`
*注意：如果默认路径不存在，请先搜索 `code_collector.py` 的实际位置。*

## 📋 工作流程

### Step 1: 确认意图与范围 (Critical)
如果用户未明确提供，请询问：
- **目的**：为什么要收集代码？
- **范围**：关注全项目、特定文件夹还是核心逻辑？

### Step 2: 智能检测
运行检测脚本，获取项目类型和推荐配置：
```bash
python {script_dir}/detect_project.py "{project_path}"
```

### Step 3: 执行收集与实时反馈
根据文件数量和大小选择模式。执行后，工具会直接向你反馈处理状态。

#### 🟢 模式 A：批量导入 (Batch)
*适用于：小型项目、整个模块、核心文件集合*
1. 使用 `glob` 查找文件。
2. 过滤掉无需收集的文件（参考检测结果）。
3. 运行：
```bash
python {script_dir}/code_collector.py "{project_path}" \
  --mode batch \
  --files {file_path_1} {file_path_2} ... \
  --intent "{user_intent}" \
  --output "{output_filename}.md"
```

#### 🔵 模式 B：片段提取 (Snippets)
*适用于：大型单文件、仅需特定函数/类*
1. 定位目标文件和符号（函数名/类名）。
2. 运行：
```bash
python {script_dir}/code_collector.py "{project_path}" \
  --mode snippets \
  --target "{file_path}" \
  --ranges '[{{"type": "function", "name": "login"}}, {{"type": "class", "name": "User"}}]' \
  --intent "{user_intent}" \
  --output "{output_filename}.md"
```

### Step 4: 处理反馈与“填补空白” (Critical)
执行脚本后，工具会列出 **"⚠️ 跳过的文件"**（如大文件）或 **"❌ 失败的文件"**（如编码问题）。
作为专家级 Agent，你必须：
1.  **分析跳过文件的重要性**：如果 `large_module.py` 被跳过，但它包含核心业务逻辑，你**必须**立即切换到 **模式 B (Snippets)** 提取其中的关键函数。
2.  **手动补全摘要**：对于无法读取的二进制文件或持续失败的文件，使用 `Read` 尝试手动查看并为外部 AI 写一段功能摘要。
3.  **确保上下文闭环**：检查是否有被跳过的文件是其他已提取代码的关键依赖。

### Step 5: 交付反馈
- 确认文档路径。
- 提醒用户：**"文档已包含您的意图说明，可直接发送给 AI 开始任务。"**

## ⚠️ 异常处理
- **文件过大 (>200KB)**：工具会自动跳过。你**必须**检查输出，并主动提议提取其中的关键片段。
- **二进制文件**：不要尝试读取，仅在文档中记录其存在和用途。
