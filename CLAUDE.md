# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 环境配置

**Python 路径**: `D:\py311` (Windows)
- 执行 Python 命令时使用: `D:\py311\python.exe`

## Project Overview

**Code Feeder** is a Claude Code Skill that collects project code and generates AI-friendly Markdown documentation. It's designed to help users provide clean context to external AI tools (web-based AI like ChatGPT, Claude.ai, etc.) for refactoring, analysis, or bug fixing.

## Common Commands
使用mcp搜索获取网上信息
### Running the Code Collector

```bash
# Batch mode - for small files/configs
python scripts/code_collector.py "{project_path}" \
  --mode batch --files src/main.py config.json ... \
  --intent "refactor login module" --output "ctx.md"

# Snippets mode - for large files or specific functions
python scripts/code_collector.py "{project_path}" \
  --mode snippets --target "src/heavy.js" \
  --ranges '[{"type":"function","name":"login"}]' \
  --intent "check security" --output "ctx.md"

# Append mode - incremental updates
python scripts/code_collector.py "{project_path}" \
  --mode snippets --target "skipped_file.py" \
  --ranges '[{"type":"function","name":"core_logic"}]' \
  --output "ctx.md" --append
```

### Detecting Project Type

```bash
python scripts/detect_project.py "{project_path}"
```

Outputs JSON with optimized ignore rules and core files for the detected project type.

## Architecture

### Core Components

- **`scripts/code_collector.py`** - Main code collection engine
  - `CodeCollector` class with methods:
    - `batch_import(file_paths)` - Collect multiple full files
    - `extract_snippets(file_path, ranges)` - Extract functions/classes by name or line numbers
    - `parse_existing_markdown(md_path)` - Parse existing output for incremental updates
    - `merge_markdown_data(existing, new_data)` - Smart merge of old + new content
    - `generate_markdown(data, intent, append_mode)` - Generate final Markdown output

- **`scripts/detect_project.py`** - Project type detection
  - `ProjectDetector` class - Detects 12+ project types (React, Vue, Django, FastAPI, Rust, Go, Java, C#, Unity, STM32, etc.)
  - Outputs optimized config for each project type

### Two Collection Modes

| Mode | Use Case |
|------|----------|
| `batch` | Small files, configs, entire modules |
| `snippets` | Large files (>200KB), specific functions/classes |

### Output Format

Generated Markdown includes:
- Directory tree structure
- Core files section (priority files)
- Code files section
- Code snippets (functions/classes)
- Statistics (line counts, language distribution)
- Skipped files list (files too large to auto-collect)
- User intent summary

### Configuration Files

- **`config.json`** - Global defaults (allowed extensions, ignore dirs, max file size 200KB)
- **`project-types.json`** - Per-project-type detection rules and ignore patterns
