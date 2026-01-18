# Code Feeder Skill

> 🚀 智能代码收集器 - 自动化工具收集项目代码，记录用户意图，一键生成上下文文档

## 📖 简介

**Code Feeder** 是一个 Claude Code skill，通过自动化工具智能收集项目代码，**自动记录用户意图**，生成包含完整上下文的 Markdown 文档，让你能直接"喂"给其他 AI 工具（如 ChatGPT、DeepSeek、NotebookLM 等）使用，**无需重复说明背景**。

### 核心特性

- 🎯 **用户意图记录** ✨：自动记录收集目的，外部 AI 无需重复理解背景
- 🚀 **一键批量导入**：小型项目一次性收集所有文件，Agent 工作量减少 80%
- 🔍 **智能片段提取**：大型项目按函数名/类名/行号精确提取，无需手动操作
- 🌲 **自动结构图**：智能生成项目目录树，清晰展示代码组织
- 📊 **自动统计分析**：代码行数、语言占比、核心文件识别
- ✅ **项目类型检测**：智能识别 React、Vue、Django、Rust 等 12+ 种项目类型
- ⚡ **零手动操作**：Agent 只需判断和审查，所有收集工作由工具完成

## 🚀 快速开始

### 安装

此 skill 已创建在：`~/.claude/skills/code-feeder/`

### 使用方法

在 Claude Code 中执行：

```bash
/code-feeder
```

或者：

```bash
使用 code-feeder skill 帮我收集项目代码
```

### 工作流程

1. **询问用户意图** 🎯：了解收集代码的目的（如"重构模块"、"分析性能"等）
2. **自动检测项目类型** ✨：智能识别项目技术栈（React、Django、Rust 等）
3. **Agent 判断策略**：选择批量导入（小项目）或片段提取（大项目）
4. **工具自动收集** 🚀：一键完成文件读取、结构生成、统计分析
5. **生成完整文档**：包含代码、目录树、统计信息和**用户意图说明**
6. **Agent 审查确认**：检查完整性，必要时补充说明

## ✨ v3.0 核心升级

### 🎯 用户意图自动记录（重大改进！）

**痛点解决**：
- ❌ 旧方式：收集代码后，还要向外部 AI 重复说明"我想做什么"
- ✅ 新方式：Agent 主动询问目的，自动写入文档，外部 AI 直接理解

**示例**：
```markdown
# Project: MyApp

**收集目的**: 需要重构用户认证模块，希望 AI 分析现有代码的安全性和性能瓶颈

## 📁 目录结构
...

## 🎯 收集目的总结

需要重构用户认证模块，希望 AI 分析现有代码的安全性和性能瓶颈

**提示**：以上代码已根据此目的收集整理，可直接用于相关分析或开发任务。
```

复制给 ChatGPT 后，它会直接理解："哦，你需要我分析认证模块的安全性和性能"，无需你再解释！

---

### 🚀 一键批量导入（Agent 工作量减少 80%）

**旧方式**（v2.0）：
```
Agent 需要做：
1. Glob 查找 50 个文件
2. 并行 Read 50 个文件（分 5 批）
3. 手动构建目录树字符串
4. 手动写入 Markdown
5. 手动计算统计信息

耗时：~3 分钟
```

**新方式**（v3.0）：
```
Agent 只需做：
1. Glob 查找文件（判断哪些需要）
2. 调用工具：
   python code_collector.py --mode batch --files ...

工具自动完成：
✅ 读取所有文件
✅ 生成目录树
✅ 统计分析
✅ 写入 Markdown

耗时：~30 秒
```

---

### 🔍 智能片段提取（大型项目的福音）

**场景**：项目有 500 个文件，只需要其中 3 个文件的 5 个函数

**旧方式**：
```
1. Read 整个文件（可能几千行）
2. 手动找到函数位置
3. 手动截取代码片段
4. 重复 5 次
```

**新方式**：
```bash
python code_collector.py --mode snippets \
  --target src/auth.py \
  --ranges '[
    {"type": "function", "name": "login"},
    {"type": "function", "name": "logout"},
    {"type": "class", "name": "TokenManager"}
  ]'
```

工具自动：
- ✅ 定位函数/类定义（支持 Python, JS, Java, C# 等）
- ✅ 提取完整代码块（包括缩进）
- ✅ 格式化输出

---

### 🌲 自动目录结构图

无需 Agent 手动拼接，工具自动生成：

```text
MyProject/
├── src/
│   ├── main.py
│   ├── utils.py
│   └── models/
│       ├── user.py
│       └── product.py
├── tests/
│   └── test_main.py
└── README.md
```

---

## ✨ 功能亮点

### 1. 项目类型自动检测

无需手动配置！系统会自动识别以下项目类型：

| 项目类型 | 检测标识 | 优化内容 |
|---------|---------|---------|
| **React/Next.js** | `package.json` 中包含 `react` | 优先 `.jsx/.tsx`，忽略 `.next` |
| **Vue/Nuxt** | `package.json` 中包含 `vue` | 优先 `.vue`，忽略 `.nuxt` |
| **Django** | `manage.py` 存在 | 优先 `settings.py`，忽略 `migrations` |
| **FastAPI** | `requirements.txt` 含 `fastapi` | 优先 `main.py/app.py` |
| **Rust** | `Cargo.toml` 存在 | 优先 `.rs`，忽略 `target` |
| **Go** | `go.mod` 存在 | 优先 `.go`，忽略 `vendor` |
| **Unity** | `ProjectSettings/` 存在 | 忽略 `Library/Temp`，优先 `.cs/.shader` |
| **STM32** | `.ioc` 文件存在 | 忽略 HAL 生成文件 |
| 其他 | Python, Node.js, Java, C# 等 | 智能适配 |

**优势**：
- 🎯 **零配置**：自动适配项目特征
- 📂 **智能过滤**：减少无关文件干扰
- ⚡ **性能优化**：优先处理核心文件

### 2. 智能片段提取模式

**支持的提取方式**：

| 提取类型 | 示例 | 适用场景 |
|---------|------|---------|
| **按行号** | `{"type": "lines", "start": 100, "end": 200}` | 已知代码位置 |
| **按函数名** | `{"type": "function", "name": "calculate_total"}` | 提取特定函数 |
| **按类名** | `{"type": "class", "name": "UserModel"}` | 提取类定义 |
| **混合提取** | 组合多个提取规则 | 复杂场景 |

**支持的语言**：
- Python, JavaScript, TypeScript
- Java, Kotlin, C#
- C, C++, Go, Rust
- 更多语言持续支持中...

---

## ⚙️ 配置说明

配置文件位置：`~/.claude/skills/code-feeder/config.json`

大多数情况下你**不需要手动修改配置**，系统会自动检测项目类型并优化。

### 默认包含的文件类型

```json
[".py", ".java", ".cpp", ".c", ".h", ".js", ".ts", ".jsx", ".tsx",
 ".html", ".css", ".sql", ".md", ".yaml", ".json", ".cs", ".go",
 ".rs", ".swift", ".kt", ".php", ".rb", ".sh", ".vue", ".svelte"]
```

### 默认忽略的目录

```json
[".git", ".idea", ".vscode", "__pycache__", "node_modules", "venv",
 "build", "dist", "bin", "obj", "Library", "Temp", "Drivers",
 "Middlewares", ".next", "coverage"]
```

### 自定义配置

你可以编辑 `config.json` 来：
- 添加/移除文件扩展名
- 添加/移除忽略目录
- 设置最大文件大小限制
- 自定义输出文件名格式

## 📝 输出示例

生成的 Markdown 文档结构（v3.0 新格式）：

```markdown
# Project: MyAwesomeApp

**生成时间**: 2026-01-18 15:30:00
**收集目的**: 分析这个 Django 项目的架构设计，找出可以优化的地方
**项目类型**: Django 项目

## 📁 目录结构

```text
MyAwesomeApp/
    manage.py
    myapp/
        settings.py
        urls.py
        views.py
    templates/
        index.html
```

---

## 🎯 核心文件（优先显示）

### File: manage.py

```py
#!/usr/bin/env python
import os
import sys
...
```

---

### File: myapp/settings.py

```py
INSTALLED_APPS = [
    'django.contrib.admin',
    ...
]
```

---

## 📄 代码文件

### File: myapp/views.py

```py
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
```

---

## 📊 统计信息

- 总文件数：8
- 总代码行数：约 300 行
- 主要语言：Python (85%), HTML (15%)

---

## 🎯 收集目的总结

分析这个 Django 项目的架构设计，找出可以优化的地方

**提示**：以上代码已根据此目的收集整理，可直接用于相关分析或开发任务。
```

**关键优势**：复制给外部 AI 时，它会立即理解你的意图！

## 💡 使用场景

### 1. 向 AI 寻求帮助（v3.0 增强）
将生成的文档复制给 ChatGPT/DeepSeek/Claude.ai，**无需再解释背景**：

**旧方式**：
```
你：[粘贴代码]
你：这是我的项目，我想分析性能瓶颈
AI：好的，我来帮你分析...
```

**新方式**（文档已包含意图）：
```
你：[粘贴包含意图的文档]
AI：我看到你想分析性能瓶颈，让我检查代码...（直接开始工作）
```

### 2. 代码审查
生成项目快照，方便团队审查或存档

### 3. 文档生成
作为自动文档的基础材料

### 4. 项目迁移
快速了解陌生项目的代码结构

## 🎯 高级用法

### 场景 1：小型项目全量收集

```
用户：使用 code-feeder 收集这个项目的所有代码，我想让 AI 帮我重构

Agent 执行：
1. 询问确认意图："重构整个项目"
2. 检测项目类型（如 React）
3. Glob 查找所有相关文件
4. 调用工具：
   python code_collector.py --mode batch \
     --files [所有文件列表] \
     --intent "重构整个项目，提升代码质量" \
     --output MyProject_CodeContext.md
5. 审查生成的文档
```

### 场景 2：大型项目精准提取

```
用户：我只需要用户认证相关的代码

Agent 执行：
1. 询问意图："分析认证模块的安全性"
2. Grep 搜索 "auth" "login" 等关键词
3. 判断需要提取：
   - src/auth/login.py 的 login 函数
   - src/auth/token.py 的 TokenManager 类
   - src/middleware/auth.py 的 100-150 行
4. 调用工具：
   python code_collector.py --mode snippets \
     --target src/auth/login.py \
     --ranges '[{"type":"function","name":"login"}]' \
     --intent "分析认证模块的安全性"
5. 审查并补充说明
```

### 场景 3：特定功能分析

```
用户：帮我收集支付相关的代码，我要给另一个 AI 分析是否有漏洞

Agent 执行：
1. 明确意图："安全审计支付模块"
2. 搜索支付相关文件
3. 批量导入相关文件
4. 在文档末尾补充：
   "注意：重点关注 process_payment 函数的参数验证和 SQL 注入防护"
```

## 🔧 技术细节

### 核心机制（v3.0）

1. **项目类型检测**：`detect_project.py` 扫描特征文件
2. **智能代码收集**：`code_collector.py` 提供两种模式
   - **批量导入模式**：一次性读取多个文件
   - **片段提取模式**：基于正则匹配提取函数/类
3. **自动结构生成**：树形算法构建目录结构
4. **语言检测**：基于文件扩展名识别编程语言
5. **Markdown 生成**：模板化输出，包含用户意图
6. **Agent 职责分离**：
   - Agent：判断策略、审查结果
   - 工具：执行收集、生成文档

## 📂 文件结构

```
~/.claude/skills/code-feeder/
├── skill.clj              # Skill 元数据定义
├── prompt.md              # 核心提示词和工作流程（v3.0 更新）
├── config.json            # 基础配置文件
├── project-types.json     # 项目类型检测规则（v2.0）
├── detect_project.py      # 项目类型检测脚本（v2.0）
├── code_collector.py      # 智能代码收集工具（v3.0 新增）🚀
└── README.md              # 本文档
```

**核心文件说明**：
- `code_collector.py`：主要工具，提供批量导入和片段提取功能
- `detect_project.py`：辅助工具，自动识别项目类型
- `prompt.md`：Agent 工作流程，定义如何使用上述工具


**Happy Coding!** 🎉

使用此 skill 让代码收集变得智能、高效、便捷！
