#!/usr/bin/env python3
"""
Sysmem公共工具类 - 提供脚本间共享的工具函数
避免代码重复，提高维护性
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path


class SysmemUtils:
    """Sysmem项目公共工具类"""

    @staticmethod
    def get_current_time() -> str:
        """获取当前时间字符串"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def safe_read_file(file_path: Path) -> str:
        """安全读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"[读取失败: {e}]"

    @staticmethod
    def extract_function_summary(content: str) -> str:
        """从README中提取功能摘要"""
        lines = content.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if (line and
                not line.startswith('#') and
                not line.startswith('---') and
                len(line) > 10):
                return line
        return "功能描述待完善"

    @staticmethod
    def extract_important_definitions(content: str) -> List[str]:
        """提取重要定义"""
        definitions = []
        lines = content.split('\n')

        for line in lines:
            if any(marker in line.lower() for marker in [
                'important:', '重要:', '关键:', 'core:', '核心:',
                '**重要**', '**关键**', 'ground truth'
            ]):
                clean_line = line.replace('*', '').replace('#', '').strip()
                if clean_line and len(clean_line) > 5:
                    definitions.append(clean_line)

        return definitions

    @staticmethod
    def extract_file_descriptions(readme_content: str) -> Dict[str, str]:
        """从README中提取文件描述"""
        descriptions = {}
        lines = readme_content.split('\n')

        for line in lines:
            if '.py' in line or '.json' in line or '.js' in line:
                # 简单的文件描述提取
                if '- `' in line and '.py` -' in line:
                    parts = line.split('` -')
                    if len(parts) >= 2:
                        filename = parts[0].split('`')[1]
                        description = parts[1].strip()
                        descriptions[filename] = description

        return descriptions

    @staticmethod
    def parse_sections(content: str) -> Dict[str, str]:
        """解析文档章节"""
        sections = {}
        lines = content.split('\n')
        current_section = "概要"
        current_content = []

        for line in lines:
            if line.startswith('##'):
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.replace('#', '').strip()
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    @staticmethod
    def suggest_file_action(filename: str) -> str:
        """建议文件处理方式"""
        filename_lower = filename.lower()

        if 'temp' in filename_lower or 'tmp' in filename_lower:
            return "建议删除 - 临时文件"
        elif 'debug' in filename_lower:
            return "需要确认 - 调试文件"
        elif 'test' in filename_lower:
            return "需要记录 - 测试文件"
        elif 'readme' in filename_lower:
            return "需要记录 - 文档文件"
        else:
            return "需要人工检查"

    @staticmethod
    def ensure_claude_skill_dir(project_path: Path) -> Path:
        """确保.claude/skill/sysmem/目录存在"""
        claude_skill_dir = project_path / ".claude" / "skill" / "sysmem"
        claude_skill_dir.mkdir(parents=True, exist_ok=True)
        return claude_skill_dir

    @staticmethod
    def export_json_data(data: Dict[str, Any], output_path: Path) -> None:
        """导出JSON数据到文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)