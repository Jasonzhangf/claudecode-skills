#!/usr/bin/env python3
"""
项目扫描器 - 扫描项目结构并收集文件信息
用于system-chain技能的项目架构分析
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any

class ProjectScanner:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.project_structure = {}

    def scan_project(self) -> Dict[str, Any]:
        """扫描整个项目结构"""
        print(f"扫描项目根目录: {self.root_path}")

        self.project_structure = {
            "root_path": str(self.root_path),
            "modules": {},
            "files": [],
            "readme_files": {},
            "claude_md": None
        }

        # 遍历项目目录
        for root, dirs, files in os.walk(self.root_path):
            root_path = Path(root)
            relative_path = root_path.relative_to(self.root_path)

            # 跳过隐藏目录和常见的忽略目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                'node_modules', '__pycache__', 'target', 'build', 'dist', '.git'
            ]]

            # 检查是否为模块目录（包含readme文件）
            readme_files = [f for f in files if f.lower().startswith('readme')]
            if readme_files:
                module_info = {
                    "path": str(relative_path),
                    "readme_file": readme_files[0],
                    "files": [f for f in files if not f.lower().startswith('readme')],
                    "subdirectories": dirs
                }
                self.project_structure["modules"][str(relative_path)] = module_info

                # 读取readme文件内容
                readme_path = root_path / readme_files[0]
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        self.project_structure["readme_files"][str(relative_path)] = f.read()
                except Exception as e:
                    print(f"读取readme文件失败 {readme_path}: {e}")

            # 检查CLAUDE.md文件
            if 'CLAUDE.md' in files:
                claude_md_path = root_path / 'CLAUDE.md'
                try:
                    with open(claude_md_path, 'r', encoding='utf-8') as f:
                        self.project_structure["claude_md"] = f.read()
                except Exception as e:
                    print(f"读取CLAUDE.md失败 {claude_md_path}: {e}")

            # 记录所有文件
            for file in files:
                if not file.startswith('.'):
                    file_path = root_path / file
                    relative_file_path = file_path.relative_to(self.root_path)
                    self.project_structure["files"].append({
                        "path": str(relative_file_path),
                        "module": str(relative_path) if relative_path != Path('.') else "root"
                    })

        return self.project_structure

    def get_module_function_summary(self, module_path: str) -> str:
        """从模块readme中提取功能摘要"""
        readme_content = self.project_structure["readme_files"].get(module_path, "")
        lines = readme_content.split('\n')

        # 查找第一行结构化描述
        for line in lines[:10]:  # 只检查前10行
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('---'):
                return line

        return "未找到功能描述"

    def find_untracked_files(self) -> List[Dict[str, str]]:
        """查找未在readme中记录的文件"""
        untracked_files = []

        for file_info in self.project_structure["files"]:
            file_path = file_info["path"]
            module_path = file_info["module"]

            # 检查文件是否在对应模块的readme中被记录
            if module_path in self.project_structure["readme_files"]:
                readme_content = self.project_structure["readme_files"][module_path]
                file_name = Path(file_path).name

                if file_name not in readme_content and not file_name.startswith('readme'):
                    untracked_files.append({
                        "file": file_path,
                        "module": module_path,
                        "status": "新文件"
                    })

        return untracked_files

    def export_structure(self, output_file: str = None) -> str:
        """导出项目结构为JSON到.claude/skill/sysmem/目录"""
        if not output_file:
            output_file = "project_structure.json"

        # 创建.claude/skill/sysmem/目录
        claude_skill_dir = self.root_path / ".claude" / "skill" / "sysmem"
        claude_skill_dir.mkdir(parents=True, exist_ok=True)

        output_path = claude_skill_dir / output_file

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.project_structure, f, ensure_ascii=False, indent=2)

        return str(output_path)

if __name__ == "__main__":
    import sys

    # 确定目标目录：如果提供了参数就使用参数目录，否则使用当前工作目录
    target_directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    print(f"🎯 目标项目目录: {target_directory}")
    print(f"📍 脚本执行目录: {os.getcwd()}")

    # 检查目标目录是否存在
    if not os.path.exists(target_directory):
        print(f"❌ 错误: 目标目录 '{target_directory}' 不存在")
        sys.exit(1)

    scanner = ProjectScanner(target_directory)
    structure = scanner.scan_project()

    print(f"发现 {len(structure['modules'])} 个模块")
    print(f"发现 {len(structure['files'])} 个文件")

    # 导出结构到.claude/skill/sysmem/目录
    output_file = scanner.export_structure()
    print(f"项目结构已导出到: {output_file}")

    # 显示未跟踪文件
    untracked = scanner.find_untracked_files()
    if untracked:
        print(f"\n发现 {len(untracked)} 个未记录的文件:")
        for file_info in untracked[:10]:  # 只显示前10个
            print(f"  - {file_info['file']} ({file_info['module']})")

    print(f"✅ 结构文件已创建在目标项目的 .claude/skill/sysmem/ 目录中")