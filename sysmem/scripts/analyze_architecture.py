#!/usr/bin/env python3
"""
架构分析器 - 分析项目架构风险和重复代码
用于system-chain技能的架构分析功能
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict

class ArchitectureAnalyzer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.analysis_results = {
            "duplicate_files": [],
            "duplicate_functions": [],
            "inconsistent_implementations": [],
            "architecture_risks": [],
            "suggestions": []
        }

    def analyze_module(self, module_path: str, project_structure: Dict[str, Any]) -> Dict[str, Any]:
        """分析指定模块的架构风险"""
        print(f"分析模块: {module_path}")

        module_info = project_structure["modules"].get(module_path, {})
        module_full_path = self.root_path / module_path

        # 分析文件重复
        self._analyze_file_duplicates(module_full_path, module_path)

        # 分析代码重复
        self._analyze_code_duplicates(module_full_path, module_path)

        # 分析实现一致性
        self._analyze_implementation_consistency(module_full_path, module_path)

        # 生成架构风险建议
        self._generate_architecture_suggestions(module_path, project_structure)

        return self.analysis_results

    def _analyze_file_duplicates(self, module_path: Path, module_name: str):
        """分析文件重复"""
        files_by_extension = defaultdict(list)

        for file_path in module_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                ext = file_path.suffix.lower()
                files_by_extension[ext].append(file_path)

        # 检查同名文件
        for ext, files in files_by_extension.items():
            name_groups = defaultdict(list)
            for file_path in files:
                base_name = file_path.stem.lower()
                name_groups[base_name].append(file_path)

            for base_name, duplicate_files in name_groups.items():
                if len(duplicate_files) > 1:
                    self.analysis_results["duplicate_files"].append({
                        "module": module_name,
                        "files": [str(f.relative_to(self.root_path)) for f in duplicate_files],
                        "issue": f"发现同名文件重复: {base_name}{ext}"
                    })

    def _analyze_code_duplicates(self, module_path: Path, module_name: str):
        """分析代码重复（Python文件）"""
        python_files = list(module_path.glob("*.py"))
        function_signatures = defaultdict(list)

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 解析AST提取函数
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            func_name = node.name
                            # 提取函数签名（参数数量）
                            arg_count = len(node.args.args)
                            signature = f"{func_name}({arg_count} args)"

                            function_signatures[signature].append({
                                "file": str(py_file.relative_to(self.root_path)),
                                "line": node.lineno,
                                "function": func_name
                            })
                except SyntaxError:
                    continue

            except Exception as e:
                print(f"解析文件失败 {py_file}: {e}")

        # 检查重复函数
        for signature, functions in function_signatures.items():
            if len(functions) > 1:
                self.analysis_results["duplicate_functions"].append({
                    "module": module_name,
                    "signature": signature,
                    "functions": functions,
                    "issue": f"发现重复函数签名: {signature}"
                })

    def _analyze_implementation_consistency(self, module_path: Path, module_name: str):
        """分析实现一致性"""
        # 检查配置文件一致性
        config_files = list(module_path.glob("*.json")) + list(module_path.glob("*.yaml")) + list(module_path.glob("*.yml"))

        if len(config_files) > 1:
            # 检查配置结构一致性
            config_structures = []
            for config_file in config_files:
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        if config_file.suffix == '.json':
                            import json
                            config = json.load(f)
                        else:
                            import yaml
                            config = yaml.safe_load(f)

                        # 提取配置键结构
                        keys = self._extract_dict_keys(config)
                        config_structures.append({
                            "file": str(config_file.relative_to(self.root_path)),
                            "keys": keys
                        })
                except Exception as e:
                    print(f"解析配置文件失败 {config_file}: {e}")

            # 比较配置结构差异
            if len(config_structures) > 1:
                for i in range(len(config_structures)):
                    for j in range(i + 1, len(config_structures)):
                        diff = self._compare_key_structures(
                            config_structures[i]["keys"],
                            config_structures[j]["keys"]
                        )
                        if diff:
                            self.analysis_results["inconsistent_implementations"].append({
                                "module": module_name,
                                "files": [
                                    config_structures[i]["file"],
                                    config_structures[j]["file"]
                                ],
                                "issue": f"配置结构不一致: {diff}"
                            })

    def _generate_architecture_suggestions(self, module_path: str, project_structure: Dict[str, Any]):
        """生成架构建议"""
        suggestions = []

        # 检查模块复杂度
        module_info = project_structure["modules"].get(module_path, {})
        file_count = len(module_info.get("files", []))

        if file_count > 20:
            suggestions.append({
                "type": "complexity",
                "message": f"模块 {module_path} 包含 {file_count} 个文件，建议拆分为子模块",
                "priority": "medium"
            })

        # 检查readme完整性
        readme_content = project_structure["readme_files"].get(module_path, "")
        if len(readme_content) < 100:
            suggestions.append({
                "type": "documentation",
                "message": f"模块 {module_path} 的readme文档过于简单，建议完善功能描述",
                "priority": "high"
            })

        # 检查文件组织
        if module_info:
            has_subdirs = len(module_info.get("subdirectories", [])) > 0
            if file_count > 10 and not has_subdirs:
                suggestions.append({
                    "type": "organization",
                    "message": f"模块 {module_path} 文件较多但无子目录，建议按功能分类组织",
                    "priority": "low"
                })

        self.analysis_results["suggestions"].extend(suggestions)

    def _extract_dict_keys(self, d: Dict, prefix: str = "") -> List[str]:
        """递归提取字典键结构"""
        keys = []
        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.append(full_key)
            if isinstance(value, dict):
                keys.extend(self._extract_dict_keys(value, full_key))
        return sorted(keys)

    def _compare_key_structures(self, keys1: List[str], keys2: List[str]) -> str:
        """比较两个键结构的差异"""
        set1, set2 = set(keys1), set(keys2)

        only_in_1 = set1 - set2
        only_in_2 = set2 - set1

        differences = []
        if only_in_1:
            differences.append(f"仅在第一个配置中: {sorted(only_in_1)}")
        if only_in_2:
            differences.append(f"仅在第二个配置中: {sorted(only_in_2)}")

        return "; ".join(differences) if differences else ""

    def generate_report(self, output_file: str = None) -> str:
        """生成分析报告到.claude/skill/sysmem/目录"""
        if not output_file:
            output_file = "architecture_analysis_report.md"

        # 创建.claude/skill/sysmem/目录
        claude_skill_dir = self.root_path / ".claude" / "skill" / "sysmem"
        claude_skill_dir.mkdir(parents=True, exist_ok=True)

        output_path = claude_skill_dir / output_file

        report_lines = [
            "# 架构分析报告\n",
            f"分析时间: {self._get_current_time()}",
            f"项目路径: {self.root_path}\n",
            "## 分析结果\n"
        ]

        # 重复文件
        if self.analysis_results["duplicate_files"]:
            report_lines.append("### 🚨 重复文件\n")
            for item in self.analysis_results["duplicate_files"]:
                report_lines.append(f"**模块**: {item['module']}")
                report_lines.append(f"**问题**: {item['issue']}")
                report_lines.append(f"**文件**: {', '.join(item['files'])}\n")

        # 重复函数
        if self.analysis_results["duplicate_functions"]:
            report_lines.append("### 🚨 重复函数\n")
            for item in self.analysis_results["duplicate_functions"]:
                report_lines.append(f"**模块**: {item['module']}")
                report_lines.append(f"**签名**: {item['signature']}")
                report_lines.append("**位置**:")
                for func in item['functions']:
                    report_lines.append(f"  - {func['file']}:{func['line']}")
                report_lines.append("")

        # 实现不一致
        if self.analysis_results["inconsistent_implementations"]:
            report_lines.append("### ⚠️ 实现不一致\n")
            for item in self.analysis_results["inconsistent_implementations"]:
                report_lines.append(f"**模块**: {item['module']}")
                report_lines.append(f"**问题**: {item['issue']}")
                report_lines.append(f"**文件**: {', '.join(item['files'])}\n")

        # 架构建议
        if self.analysis_results["suggestions"]:
            report_lines.append("### 💡 架构建议\n")
            # 按优先级分组
            by_priority = defaultdict(list)
            for suggestion in self.analysis_results["suggestions"]:
                by_priority[suggestion["priority"]].append(suggestion)

            for priority in ["high", "medium", "low"]:
                if by_priority[priority]:
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    report_lines.append(f"#### {priority_emoji[priority]} {priority.upper()} 优先级\n")
                    for suggestion in by_priority[priority]:
                        report_lines.append(f"- {suggestion['message']}")
                    report_lines.append("")

        # 写入报告文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        return str(output_path)

    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    import sys
    import json

    # 确定目标目录：如果提供了参数就使用参数目录，否则使用当前工作目录
    target_directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    print(f"🎯 目标项目目录: {target_directory}")
    print(f"📍 脚本执行目录: {os.getcwd()}")

    # 检查目标目录是否存在
    if not os.path.exists(target_directory):
        print(f"❌ 错误: 目标目录 '{target_directory}' 不存在")
        sys.exit(1)

    # 查找项目结构文件
    structure_file_path = Path(target_directory) / ".claude" / "skill" / "sysmem" / "project_structure.json"

    try:
        with open(structure_file_path, 'r', encoding='utf-8') as f:
            project_structure = json.load(f)
    except FileNotFoundError:
        print(f"❌ 请先在目标目录中运行 scan_project.py 生成项目结构文件")
        print(f"   期望文件位置: {structure_file_path}")
        sys.exit(1)

    analyzer = ArchitectureAnalyzer(target_directory)

    # 分析所有模块
    for module_path in project_structure["modules"].keys():
        results = analyzer.analyze_module(module_path, project_structure)

    # 生成报告到.claude/skill/sysmem/目录
    report_file = analyzer.generate_report()
    print(f"架构分析报告已生成: {report_file}")
    print(f"✅ 分析报告已创建在目标项目的 .claude/skill/sysmem/ 目录中")