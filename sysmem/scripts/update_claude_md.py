#!/usr/bin/env python3
"""
CLAUDE.md更新器 - 更新项目根目录的CLAUDE.md文件
用于system-chain技能的项目文档管理
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any
from utils import SysmemUtils

class ClaudeMdUpdater:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.claude_md_path = self.root_path / "CLAUDE.md"

    def update_claude_md(self, project_structure: Dict[str, Any]) -> bool:
        """更新CLAUDE.md文件"""
        try:
            # 读取现有CLAUDE.md内容
            if self.claude_md_path.exists():
                with open(self.claude_md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = self._create_default_claude_md()

            # 更新技能包说明
            content = self._update_skill_description(content)

            # 更新项目架构树状结构
            content = self._update_architecture_tree(content, project_structure)

            # 更新模块功能定义
            content = self._update_module_definitions(content, project_structure)

            # 写入更新后的内容
            with open(self.claude_md_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"CLAUDE.md已更新: {self.claude_md_path}")
            return True

        except Exception as e:
            print(f"更新CLAUDE.md失败: {e}")
            return False

    def _create_default_claude_md(self) -> str:
        """创建默认的CLAUDE.md模板"""
        return """# CLAUDE.md

## 技能包说明

### system-chain
项目架构链条化初始化和管理技能包，负责维护项目文档结构的一致性和完整性。

## 项目架构

### 模块结构

<!-- 架构树状结构将由system-chain自动更新 -->

### 模块功能定义

<!-- 模块功能定义将由system-chain自动更新 -->

"""

    def _update_skill_description(self, content: str) -> str:
        """更新技能包说明部分"""
        skill_pattern = r'(### system-chain\n).*?(\n\n)'

        new_description = """### system-chain
项目架构链条化初始化和管理技能包，负责维护项目文档结构的一致性和完整性。提供自动化扫描、文档更新、架构分析和清理建议功能。
"""

        content = re.sub(skill_pattern, new_description, content, flags=re.DOTALL)
        return content

    def _update_architecture_tree(self, content: str, project_structure: Dict[str, Any]) -> str:
        """更新项目架构树状结构"""
        tree_section = "### 模块结构\n\n"

        if project_structure["modules"]:
            tree_lines = []
            for module_path in sorted(project_structure["modules"].keys()):
                module_info = project_structure["modules"][module_path]
                function_summary = self._extract_function_summary(
                    project_structure["readme_files"].get(module_path, "")
                )

                # 构建树状结构
                depth = module_path.count('/') if module_path != "." else 0
                indent = "  " * depth
                tree_lines.append(f"{indent}- **{module_path}**: {function_summary}")

            tree_section += "\n".join(tree_lines) + "\n\n"
        else:
            tree_section += "暂无模块结构\n\n"

        # 替换现有的架构树部分
        tree_pattern = r'(### 模块结构\n\n).*?(\n\n### 模块功能定义)'
        content = re.sub(tree_pattern, tree_section + r'\2', content, flags=re.DOTALL)

        return content

    def _update_module_definitions(self, content: str, project_structure: Dict[str, Any]) -> str:
        """更新模块功能定义（高亮重要定义）"""
        definitions_section = "### 模块功能定义\n\n"

        for module_path in sorted(project_structure["modules"].keys()):
            readme_content = project_structure["readme_files"].get(module_path, "")

            # 提取高亮定义（查找 marked as important 或特殊标记）
            important_definitions = self._extract_important_definitions(readme_content)

            if important_definitions:
                definitions_section += f"#### {module_path}\n\n"
                for definition in important_definitions:
                    definitions_section += f"- **{definition}**\n"
                definitions_section += "\n"

        # 替换现有的定义部分
        definition_pattern = r'(### 模块功能定义\n\n).*?$'
        content = re.sub(definition_pattern, definitions_section, content, flags=re.DOTALL)

        return content

    def _extract_function_summary(self, readme_content: str) -> str:
        """从readme中提取功能摘要"""
        return SysmemUtils.extract_function_summary(readme_content)

    def _extract_important_definitions(self, readme_content: str) -> List[str]:
        """提取readme中的重要定义（高亮部分）"""
        return SysmemUtils.extract_important_definitions(readme_content)

if __name__ == "__main__":
    # 示例用法
    import json

    # 假设我们有项目结构数据
    try:
        with open("project_structure.json", 'r', encoding='utf-8') as f:
            project_structure = json.load(f)
    except FileNotFoundError:
        print("请先运行 scan_project.py 生成项目结构文件")
        exit(1)

    updater = ClaudeMdUpdater()
    success = updater.update_claude_md(project_structure)

    if success:
        print("CLAUDE.md更新完成")
    else:
        print("CLAUDE.md更新失败")