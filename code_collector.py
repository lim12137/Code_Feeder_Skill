#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能代码收集工具
提供一键批量导入、智能片段提取、自动结构图生成等功能
"""

import os
import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime
import re


class CodeCollector:
    """智能代码收集器"""

    def __init__(self, project_path: str, config: Dict = None):
        """初始化收集器"""
        self.project_path = Path(project_path).resolve()
        self.config = config or {}
        self.collected_files = []
        self.structure_tree = {}

    def batch_import(self, file_paths: List[str]) -> Dict:
        """
        一键批量导入多个文件

        参数:
            file_paths: 文件路径列表（相对或绝对路径）

        返回:
            {
                "files": [{"path": "...", "content": "...", "language": "...", "lines": 100}, ...],
                "structure": "树形结构字符串",
                "stats": {"total_files": 10, "total_lines": 1000, "languages": {...}},
                "skipped_files": [{"path": "...", "reason": "..."}, ...]
            }
        """
        result = {
            "files": [],
            "structure": "",
            "stats": {"total_files": 0, "total_lines": 0, "languages": {}},
            "skipped_files": []
        }

        collected_paths = []
        max_size_kb = self.config.get('max_file_size_kb', 500)

        for file_path in file_paths:
            abs_path = self._resolve_path(file_path)
            if not abs_path.exists() or not abs_path.is_file():
                continue

            # 检查文件大小
            file_size_kb = abs_path.stat().st_size / 1024
            if file_size_kb > max_size_kb:
                result["skipped_files"].append({
                    "path": str(file_path),
                    "reason": f"文件过大 ({file_size_kb:.1f} KB > {max_size_kb} KB)",
                    "size_kb": file_size_kb,
                    "lines": self._count_lines(abs_path)
                })
                continue

            # 读取文件内容
            content, encoding = self._read_file_safely(abs_path)
            if content is None:
                result["skipped_files"].append({
                    "path": str(file_path),
                    "reason": "编码错误，无法读取"
                })
                continue

            # 获取相对路径
            try:
                rel_path = abs_path.relative_to(self.project_path)
            except ValueError:
                rel_path = abs_path

            # 语言检测
            language = self._detect_language(abs_path)
            lines = len(content.splitlines())

            result["files"].append({
                "path": str(rel_path),
                "content": content,
                "language": language,
                "lines": lines,
                "size_kb": abs_path.stat().st_size / 1024
            })

            collected_paths.append(rel_path)

            # 更新统计
            result["stats"]["total_lines"] += lines
            result["stats"]["languages"][language] = result["stats"]["languages"].get(language, 0) + 1

        result["stats"]["total_files"] = len(result["files"])

        # 生成目录结构
        result["structure"] = self._generate_tree_structure(collected_paths)

        return result

    def extract_snippets(self, file_path: str, ranges: List[Dict]) -> Dict:
        """
        智能片段提取（支持行号范围和函数名）

        参数:
            file_path: 文件路径
            ranges: 提取范围列表
                [
                    {"type": "lines", "start": 10, "end": 50},
                    {"type": "function", "name": "calculate_total"},
                    {"type": "class", "name": "UserModel"}
                ]

        返回:
            {
                "file_path": "...",
                "snippets": [
                    {"type": "lines", "range": "10-50", "content": "...", "lines": 41},
                    {"type": "function", "name": "calculate_total", "content": "...", "lines": 15}
                ],
                "total_lines": 56
            }
        """
        abs_path = self._resolve_path(file_path)
        if not abs_path.exists():
            return {"error": f"文件不存在: {file_path}"}

        content, _ = self._read_file_safely(abs_path)
        if content is None:
            return {"error": f"无法读取文件: {file_path}"}

        lines = content.splitlines()
        result = {
            "file_path": str(file_path),
            "snippets": [],
            "total_lines": 0
        }

        for range_spec in ranges:
            snippet = None

            if range_spec["type"] == "lines":
                # 按行号提取
                start = range_spec.get("start", 1) - 1  # 转换为 0-based
                end = range_spec.get("end", len(lines))
                snippet_lines = lines[start:end]

                snippet = {
                    "type": "lines",
                    "range": f"{start + 1}-{end}",
                    "content": "\n".join(snippet_lines),
                    "lines": len(snippet_lines)
                }

            elif range_spec["type"] in ["function", "class", "method"]:
                # 按函数/类名提取
                name = range_spec.get("name")
                snippet_content, snippet_lines = self._extract_by_name(
                    content,
                    name,
                    range_spec["type"],
                    abs_path.suffix
                )

                if snippet_content:
                    snippet = {
                        "type": range_spec["type"],
                        "name": name,
                        "content": snippet_content,
                        "lines": snippet_lines
                    }

            if snippet:
                result["snippets"].append(snippet)
                result["total_lines"] += snippet["lines"]

        return result

    def generate_markdown(self, data: Dict, user_intent: str = "") -> str:
        """
        生成 Markdown 文档

        参数:
            data: batch_import 或 extract_snippets 返回的数据
            user_intent: 用户意图描述

        返回:
            完整的 Markdown 字符串
        """
        md_parts = []

        # 标题
        project_name = self.project_path.name
        md_parts.append(f"# Project: {project_name}\n")

        # 元信息
        md_parts.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        if user_intent:
            md_parts.append(f"**收集目的**: {user_intent}\n")

        # 项目类型（如果有）
        if "detected_project_type" in self.config:
            md_parts.append(f"**项目类型**: {self.config.get('project_type_name', '未知')}\n")

        md_parts.append("\n---\n\n")

        # 目录结构
        if "structure" in data and data["structure"]:
            md_parts.append("## 📁 目录结构\n\n")
            md_parts.append("```text\n")
            md_parts.append(data["structure"])
            md_parts.append("\n```\n\n---\n\n")

        # 文件内容（批量导入模式）
        if "files" in data:
            # 核心文件优先
            core_files = []
            other_files = []

            for file_info in data["files"]:
                if self._is_core_file(file_info["path"]):
                    core_files.append(file_info)
                else:
                    other_files.append(file_info)

            if core_files:
                md_parts.append("## 🎯 核心文件\n\n")
                for file_info in core_files:
                    md_parts.append(self._format_file_section(file_info))

            if other_files:
                md_parts.append("## 📄 代码文件\n\n")
                for file_info in other_files:
                    md_parts.append(self._format_file_section(file_info))

        # 代码片段（片段提取模式）
        if "snippets" in data:
            md_parts.append(f"## 📄 代码片段: {data['file_path']}\n\n")
            for snippet in data["snippets"]:
                md_parts.append(self._format_snippet_section(snippet))

        # 统计信息
        if "stats" in data:
            md_parts.append("## 📊 统计信息\n\n")
            stats = data["stats"]
            md_parts.append(f"- 总文件数：{stats['total_files']}\n")
            md_parts.append(f"- 总代码行数：{stats['total_lines']}\n")

            if stats.get("languages"):
                lang_stats = []
                total = sum(stats["languages"].values())
                for lang, count in sorted(stats["languages"].items(), key=lambda x: x[1], reverse=True):
                    pct = (count / total) * 100
                    lang_stats.append(f"{lang} ({pct:.1f}%)")
                md_parts.append(f"- 主要语言：{', '.join(lang_stats)}\n")

        # 跳过的文件（如果有）
        if "skipped_files" in data and data["skipped_files"]:
            md_parts.append("\n---\n\n")
            md_parts.append("## ⚠️ 跳过的文件\n\n")
            md_parts.append("以下文件因体积过大或编码问题未能自动收集，**需要 Agent 手动处理**：\n\n")
            for skipped in data["skipped_files"]:
                md_parts.append(f"### {skipped['path']}\n\n")
                md_parts.append(f"- **原因**：{skipped['reason']}\n")
                if 'size_kb' in skipped:
                    md_parts.append(f"- **文件大小**：{skipped['size_kb']:.1f} KB\n")
                if 'lines' in skipped and skipped['lines']:
                    md_parts.append(f"- **预估行数**：约 {skipped['lines']} 行\n")
                md_parts.append(f"- **建议**：使用片段提取模式 (--mode snippets) 指定函数/类名或行号范围\n\n")

        # 用户意图总结（文末）
        if user_intent:
            md_parts.append("\n---\n\n")
            md_parts.append("## 🎯 收集目的总结\n\n")
            md_parts.append(f"{user_intent}\n\n")
            md_parts.append("**提示**：以上代码已根据此目的收集整理，可直接用于相关分析或开发任务。\n")

        return "".join(md_parts)

    def _resolve_path(self, path: str) -> Path:
        """解析路径（支持相对和绝对路径）"""
        p = Path(path)
        if p.is_absolute():
            return p
        return self.project_path / p

    def _read_file_safely(self, path: Path) -> Tuple[Optional[str], Optional[str]]:
        """安全读取文件（尝试多种编码）"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']

        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    return f.read(), encoding
            except (UnicodeDecodeError, FileNotFoundError):
                continue

        return None, None

    def _count_lines(self, path: Path) -> Optional[int]:
        """快速统计文件行数（不完整读取）"""
        try:
            with open(path, 'rb') as f:
                return sum(1 for _ in f)
        except:
            return None

    def _detect_language(self, path: Path) -> str:
        """检测编程语言"""
        ext = path.suffix.lower()
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.jsx': 'jsx', '.tsx': 'tsx', '.java': 'java',
            '.cpp': 'cpp', '.c': 'c', '.h': 'c', '.hpp': 'cpp',
            '.cs': 'csharp', '.go': 'go', '.rs': 'rust',
            '.rb': 'ruby', '.php': 'php', '.swift': 'swift',
            '.kt': 'kotlin', '.scala': 'scala', '.r': 'r',
            '.m': 'objective-c', '.sql': 'sql', '.sh': 'bash',
            '.yaml': 'yaml', '.yml': 'yaml', '.json': 'json',
            '.xml': 'xml', '.html': 'html', '.css': 'css',
            '.scss': 'scss', '.sass': 'sass', '.md': 'markdown',
            '.vue': 'vue', '.svelte': 'svelte'
        }
        return lang_map.get(ext, 'text')

    def _generate_tree_structure(self, file_paths: List[Path]) -> str:
        """生成树形目录结构"""
        if not file_paths:
            return ""

        # 构建树形结构
        tree = {}
        for path in file_paths:
            parts = path.parts
            current = tree
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]

        # 渲染树形结构
        def render_tree(node: Dict, prefix: str = "", is_last: bool = True) -> List[str]:
            lines = []
            items = sorted(node.items())

            for i, (name, children) in enumerate(items):
                is_last_item = (i == len(items) - 1)

                if prefix == "":
                    lines.append(f"{name}/")
                    lines.extend(render_tree(children, "    ", is_last_item))
                else:
                    connector = "└── " if is_last_item else "├── "
                    is_file = len(children) == 0
                    display_name = name if is_file else f"{name}/"
                    lines.append(f"{prefix}{connector}{display_name}")

                    if children:
                        extension = "    " if is_last_item else "│   "
                        lines.extend(render_tree(children, prefix + extension, is_last_item))

            return lines

        tree_lines = render_tree(tree)
        return "\n".join(tree_lines)

    def _extract_by_name(self, content: str, name: str, element_type: str, file_ext: str) -> Tuple[Optional[str], int]:
        """根据函数/类名提取代码"""
        lines = content.splitlines()

        # 根据文件类型选择正则模式
        if file_ext in ['.py']:
            if element_type == 'function':
                pattern = rf'^\s*def\s+{re.escape(name)}\s*\('
            elif element_type == 'class':
                pattern = rf'^\s*class\s+{re.escape(name)}\s*[\(:]'
            else:
                return None, 0
        elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
            if element_type == 'function':
                pattern = rf'(function\s+{re.escape(name)}\s*\(|const\s+{re.escape(name)}\s*=|\s+{re.escape(name)}\s*\()'
            elif element_type == 'class':
                pattern = rf'class\s+{re.escape(name)}\s*'
            else:
                return None, 0
        elif file_ext in ['.java', '.kt', '.cs']:
            if element_type in ['function', 'method']:
                pattern = rf'\s+{re.escape(name)}\s*\('
            elif element_type == 'class':
                pattern = rf'class\s+{re.escape(name)}\s*'
            else:
                return None, 0
        else:
            # 通用模式
            pattern = rf'\b{re.escape(name)}\b'

        # 查找定义行
        start_line = None
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                start_line = i
                break

        if start_line is None:
            return None, 0

        # 确定结束行（基于缩进）
        base_indent = len(lines[start_line]) - len(lines[start_line].lstrip())
        end_line = start_line + 1

        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip() == "":
                continue

            current_indent = len(line) - len(line.lstrip())

            # 如果缩进回到同级或更少，结束
            if current_indent <= base_indent and line.strip():
                end_line = i
                break
        else:
            end_line = len(lines)

        snippet_lines = lines[start_line:end_line]
        return "\n".join(snippet_lines), len(snippet_lines)

    def _is_core_file(self, file_path: str) -> bool:
        """判断是否为核心文件"""
        core_files = self.config.get('core_files', [])
        file_name = Path(file_path).name

        # 检查完整路径或文件名
        return any(
            file_path == core or
            file_name == core or
            file_path.endswith(core)
            for core in core_files
        )

    def _format_file_section(self, file_info: Dict) -> str:
        """格式化文件段落"""
        md = f"### File: {file_info['path']}\n\n"
        md += f"```{file_info['language']}\n"
        md += file_info['content']
        md += "\n```\n\n---\n\n"
        return md

    def _format_snippet_section(self, snippet: Dict) -> str:
        """格式化代码片段段落"""
        if snippet['type'] == 'lines':
            md = f"### 行 {snippet['range']}\n\n"
        else:
            md = f"### {snippet['type'].title()}: {snippet['name']}\n\n"

        md += "```\n"
        md += snippet['content']
        md += "\n```\n\n---\n\n"
        return md


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='智能代码收集工具')
    parser.add_argument('project_path', help='项目路径')
    parser.add_argument('--mode', choices=['batch', 'snippets'], required=True,
                        help='运行模式：batch（批量导入）或 snippets（片段提取）')
    parser.add_argument('--files', nargs='+', help='文件列表（batch 模式）')
    parser.add_argument('--target', help='目标文件（snippets 模式）')
    parser.add_argument('--ranges', help='提取范围 JSON（snippets 模式）')
    parser.add_argument('--intent', help='用户意图描述')
    parser.add_argument('--config', help='配置文件路径（JSON）')
    parser.add_argument('--output', help='输出文件路径')

    args = parser.parse_args()

    # 加载配置
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)

    # 创建收集器
    collector = CodeCollector(args.project_path, config)

    # 执行收集
    if args.mode == 'batch':
        if not args.files:
            print("错误：batch 模式需要指定 --files", file=sys.stderr)
            sys.exit(1)

        data = collector.batch_import(args.files)

    elif args.mode == 'snippets':
        if not args.target or not args.ranges:
            print("错误：snippets 模式需要指定 --target 和 --ranges", file=sys.stderr)
            sys.exit(1)

        ranges = json.loads(args.ranges)
        data = collector.extract_snippets(args.target, ranges)

    # 生成 Markdown
    markdown = collector.generate_markdown(data, args.intent or "")

    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"✅ 已保存到: {args.output}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
