#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目类型自动检测工具
用于识别项目类型并返回优化的配置
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ProjectDetector:
    """项目类型检测器"""

    def __init__(self, config_path: str = None):
        """初始化检测器"""
        if config_path is None:
            # 默认使用父目录下的 project-types.json
            script_dir = Path(__file__).parent
            project_root = script_dir.parent
            config_path = project_root / "project-types.json"

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.project_types = self.config['project_types']
        self.detection_priority = self.config['detection_priority']

    def detect(self, project_path: str) -> Tuple[Optional[str], Dict]:
        """
        检测项目类型

        返回: (项目类型名称, 配置字典)
        """
        project_path = Path(project_path).resolve()

        if not project_path.exists():
            return None, {}

        # 按优先级检测
        for type_name in self.detection_priority:
            type_config = self.project_types[type_name]

            if self._matches_project_type(project_path, type_config):
                return type_name, type_config

        # 未检测到特定类型，返回通用配置
        return "generic", self._get_generic_config()

    def _matches_project_type(self, project_path: Path, type_config: Dict) -> bool:
        """检查项目是否匹配特定类型"""
        detection_files = type_config.get('detection_files', [])
        detection_patterns = type_config.get('detection_patterns', {})

        # 检查特征文件是否存在
        matched_files = []
        for file_pattern in detection_files:
            # 支持通配符
            if '*' in file_pattern:
                # 简单的通配符匹配
                matched = list(project_path.rglob(file_pattern))
                if matched:
                    matched_files.append(matched[0])
            else:
                file_path = project_path / file_pattern
                if file_path.exists():
                    matched_files.append(file_path)

        if not matched_files:
            return False

        # 如果没有内容模式要求，直接返回 True
        if not detection_patterns:
            return True

        # 检查文件内容是否匹配模式
        for file_path in matched_files:
            file_name = file_path.name
            if file_name in detection_patterns:
                patterns = detection_patterns[file_name]
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if any(pattern in content for pattern in patterns):
                        return True
                except:
                    continue

        return True  # 文件存在即可

    def _get_generic_config(self) -> Dict:
        """返回通用配置"""
        return {
            "name": "通用项目",
            "priority_extensions": [],
            "ignore_dirs": [],
            "core_files": []
        }

    def get_optimized_config(self, project_path: str, base_config: Dict) -> Dict:
        """
        获取优化后的配置

        合并基础配置和检测到的项目类型配置
        """
        project_type, type_config = self.detect(project_path)

        # 深拷贝基础配置
        optimized = json.loads(json.dumps(base_config))

        if project_type and project_type != "generic":
            # 合并 ignore_dirs
            type_ignore_dirs = type_config.get('ignore_dirs', [])
            current_ignore = set(optimized.get('ignore_dirs', []))
            current_ignore.update(type_ignore_dirs)
            optimized['ignore_dirs'] = sorted(list(current_ignore))

            # 添加项目特定的忽略前缀
            if 'ignore_prefixes' in type_config:
                current_prefixes = set(optimized.get('ignore_prefixes', []))
                current_prefixes.update(type_config['ignore_prefixes'])
                optimized['ignore_prefixes'] = sorted(list(current_prefixes))

            # 添加优先扩展名（用于排序）
            optimized['priority_extensions'] = type_config.get('priority_extensions', [])

            # 添加核心文件列表
            optimized['core_files'] = type_config.get('core_files', [])

            # 添加项目类型元信息
            optimized['detected_project_type'] = project_type
            optimized['project_type_name'] = type_config['name']
        else:
            optimized['detected_project_type'] = 'generic'
            optimized['project_type_name'] = '通用项目'
            optimized['priority_extensions'] = []
            optimized['core_files'] = []

        return optimized


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("使用方法: python detect_project.py <项目路径> [配置文件路径]", file=sys.stderr)
        sys.exit(1)

    project_path = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else None

    detector = ProjectDetector(config_path)

    # 读取基础配置
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    base_config_path = project_root / "config.json"

    with open(base_config_path, 'r', encoding='utf-8') as f:
        base_config = json.load(f)

    # 获取优化配置
    optimized_config = detector.get_optimized_config(project_path, base_config)

    # 输出 JSON 格式
    print(json.dumps(optimized_config, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
