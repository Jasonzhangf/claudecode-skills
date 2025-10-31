#!/usr/bin/env python3
"""
项目数据收集器 - 仅负责收集和分析项目数据，不直接修改文件
将分析结果交给Claude进行智能处理
"""

import os
import json
import ast
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
from utils import SysmemUtils

class ProjectDataCollector:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()

    def collect_all_data(self) -> Dict[str, Any]:
        """收集所有项目数据"""
        print("🔍 开始收集项目数据...", flush=True)
        print(f"📁 目标目录: {self.root_path}", flush=True)

        # 收集扫描信息
        print("📋 收集扫描信息...", flush=True)
        data = {
            "scan_info": self._get_scan_info(),
        }
        print("✅ 扫描信息收集完成", flush=True)

        # 收集模块数据
        print("📦 分析项目模块结构...", flush=True)
        data["modules"] = self._collect_modules_data()
        print(f"✅ 模块结构分析完成，发现 {len(data['modules'])} 个模块", flush=True)

        # 分析CLAUDE.md
        print("📄 分析CLAUDE.md文件...")
        data["claude_md_info"] = self._analyze_claude_md()
        print("✅ CLAUDE.md分析完成")

        # 分析架构问题
        print("🔍 分析架构问题...")
        data["architecture_analysis"] = self._analyze_architecture()
        duplicate_files = len(data["architecture_analysis"]["duplicate_files"])
        duplicate_functions = len(data["architecture_analysis"]["duplicate_functions"])
        print(f"✅ 架构分析完成，发现 {duplicate_files} 个潜在重复文件，{duplicate_functions} 个函数模式")

        # 查找未记录文件
        print("🔍 查找未记录的文件...")
        data["untracked_files"] = self._find_untracked_files()
        print(f"✅ 未记录文件分析完成，发现 {len(data['untracked_files'])} 个文件")

        # 生成更新建议
        print("💡 生成更新建议...")
        data["update_suggestions"] = self._generate_update_suggestions()
        print("✅ 更新建议生成完成")

        print("🎉 项目数据收集完成！")
        return data

    def _get_scan_info(self) -> Dict[str, Any]:
        """获取扫描基本信息"""
        return {
            "scan_time": self._get_current_time(),
            "project_root": str(self.root_path),
            "python_version": os.sys.version,
            "platform": os.name
        }

    def _collect_modules_data(self) -> Dict[str, Any]:
        """收集模块数据"""
        modules = {}

        for root, dirs, files in os.walk(self.root_path):
            root_path = Path(root)
            relative_path = root_path.relative_to(self.root_path)

            # 跳过隐藏目录和常见忽略目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                'node_modules', '__pycache__', 'target', 'build', 'dist', '.git'
            ]]

            # 查找README文件
            readme_files = [f for f in files if f.lower().startswith('readme')]
            if readme_files:
                readme_path = root_path / readme_files[0]

                # 读取README内容
                readme_content = self._safe_read_file(readme_path)

                # 提取功能摘要
                function_summary = self._extract_function_summary(readme_content)

                # 提取重要定义
                important_definitions = self._extract_important_definitions(readme_content)

                # 提取文件描述
                file_descriptions = self._extract_file_descriptions(readme_content)

                module_data = {
                    "path": str(relative_path),
                    "readme_file": readme_files[0],
                    "readme_content": readme_content,
                    "files": [f for f in files if not f.lower().startswith('readme')],
                    "subdirectories": dirs,
                    "function_summary": function_summary,
                    "important_definitions": important_definitions,
                    "file_descriptions": file_descriptions
                }

                modules[str(relative_path)] = module_data

        return modules

    def _analyze_claude_md(self) -> Dict[str, Any]:
        """分析现有的CLAUDE.md文件"""
        claude_md_path = self.root_path / "CLAUDE.md"

        if not claude_md_path.exists():
            return {
                "exists": False,
                "content": None,
                "sections": {},
                "suggestions": ["需要创建CLAUDE.md文件"]
            }

        content = self._safe_read_file(claude_md_path)

        return {
            "exists": True,
            "content": content,
            "sections": self._parse_sections(content),
            "has_system_chain_section": "system-chain" in content,
            "has_module_structure": "模块结构" in content,
            "has_module_definitions": "模块功能定义" in content
        }

    def _analyze_architecture(self) -> Dict[str, Any]:
        """分析架构问题"""
        issues = {
            "duplicate_files": [],
            "duplicate_functions": [],
            "inconsistent_configs": [],
            "suggestions": []
        }

        # 分析模块内相似文件名（静态分析，仅作为警告参考）
        self._analyze_similar_files_in_modules(issues)

        # 分析Python函数重复（静态分析，仅作为警告参考）
        self._analyze_function_patterns(issues)

        return issues

    def _analyze_similar_files_in_modules(self, issues: Dict[str, Any]):
        """分析同一模块内相似文件名（仅作为警告参考，需用户进一步分析）"""
        # 获取所有模块目录
        modules = {}
        for item in self.root_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
                # 检查是否有Python文件或其他项目文件
                if self._is_module_directory(item):
                    modules[item.name] = item

        # 分析每个模块内的文件
        for module_name, module_path in modules.items():
            files_in_module = self._get_module_files(module_path)
            similar_groups = self._find_similar_filenames(files_in_module)

            for group in similar_groups:
                if len(group) > 1:  # 找到相似文件名
                    issues["duplicate_files"].append({
                        "module": module_name,
                        "similar_files": group,
                        "issue_type": "similar_filenames_in_module",
                        "requires_analysis": True,
                        "description": f"模块 '{module_name}' 中发现相似文件名，需要进一步分析功能重复",
                        "suggestion": "请检查这些文件是否具有相似功能，考虑合并或明确职责分离"
                    })

    def _is_module_directory(self, path: Path) -> bool:
        """判断是否为模块目录"""
        python_files = list(path.rglob("*.py"))
        js_files = list(path.rglob("*.js"))
        has_readme = any(path.rglob("README*"))

        return len(python_files) > 0 or len(js_files) > 0 or has_readme

    def _get_module_files(self, module_path: Path) -> List[str]:
        """获取模块内的主要文件"""
        files = []
        for pattern in ["*.py", "*.js", "*.ts", "*.vue", "*.html", "*.css"]:
            files.extend([f.name for f in module_path.rglob(pattern)])
        return files

    def _find_similar_filenames(self, filenames: List[str]) -> List[List[str]]:
        """找出相似文件名"""
        from difflib import SequenceMatcher

        groups = []
        processed = set()

        for i, file1 in enumerate(filenames):
            if file1 in processed:
                continue

            similar_group = [file1]
            processed.add(file1)

            for j, file2 in enumerate(filenames[i+1:], i+1):
                if file2 in processed:
                    continue

                # 移除扩展名比较
                name1 = Path(file1).stem
                name2 = Path(file2).stem

                # 计算相似度
                similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

                # 如果相似度大于阈值，认为是相似文件
                if similarity > 0.7:
                    similar_group.append(file2)
                    processed.add(file2)

            if len(similar_group) > 1:
                groups.append(similar_group)

        return groups

    def _analyze_function_patterns(self, issues: Dict[str, Any]):
        """分析函数模式（仅作为警告参考，需用户进一步分析）"""
        python_files = list(self.root_path.rglob("*.py"))
        function_patterns = defaultdict(list)

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # 记录函数信息（但不作为重复判断，仅作为模式分析）
                        pattern_info = {
                            "name": node.name,
                            "file": str(py_file),
                            "line": node.lineno,
                            "args_count": len(node.args.args)
                        }

                        # 按函数名模式分组
                        if any(keyword in node.name.lower() for keyword in
                               ['process', 'handle', 'parse', 'convert', 'validate', 'check']):
                            function_patterns['common_patterns'].append(pattern_info)

                        # 按参数数量分组
                        function_patterns[f"args_{len(node.args.args)}"].append(pattern_info)

            except Exception as e:
                # 忽略解析错误的文件
                continue

        # 生成模式分析建议
        for pattern, functions in function_patterns.items():
            if len(functions) > 3:  # 如果同一模式函数超过3个，提示分析
                issues["duplicate_functions"].append({
                    "pattern": pattern,
                    "functions": functions[:5],  # 只显示前5个
                    "count": len(functions),
                    "issue_type": "function_pattern_analysis",
                    "requires_analysis": True,
                    "description": f"发现{len(functions)}个相似模式的函数，可能存在功能重复",
                    "suggestion": "请分析这些函数是否实现相似功能，考虑重构以减少重复"
                })

    def _find_untracked_files(self) -> List[Dict[str, Any]]:
        """查找未在README中记录的文件"""
        untracked = []

        for root, dirs, files in os.walk(self.root_path):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            readme_files = [f for f in files if f.lower().startswith('readme')]
            if readme_files:
                readme_path = Path(root) / readme_files[0]
                readme_content = self._safe_read_file(readme_path)

                for file in files:
                    if not file.lower().startswith('readme') and not file.startswith('.'):
                        if file not in readme_content:
                            file_path = Path(root) / file
                            relative_path = file_path.relative_to(self.root_path)

                            untracked.append({
                                "file": str(relative_path),
                                "module": str(Path(root).relative_to(self.root_path)),
                                "suggestion": self._suggest_file_action(file)
                            })

        return untracked

    def _generate_update_suggestions(self) -> Dict[str, Any]:
        """生成更新建议"""
        return {
            "claude_md_updates": [
                "检查system-chain技能包描述是否需要更新",
                "更新模块结构树状图",
                "同步模块重要定义"
            ],
            "readme_updates": [
                "检查第一行功能描述是否标准化",
                "验证文件结构说明是否完整",
                "确认重要定义是否标记为Ground Truth"
            ],
            "architecture_improvements": [
                "处理重复文件和函数",
                "统一配置文件格式",
                "完善文档覆盖率"
            ]
        }

    def _safe_read_file(self, file_path: Path) -> str:
        """安全读取文件内容"""
        return SysmemUtils.safe_read_file(file_path)

    def _extract_function_summary(self, content: str) -> str:
        """从README中提取功能摘要"""
        return SysmemUtils.extract_function_summary(content)

    def _extract_important_definitions(self, content: str) -> List[str]:
        """提取重要定义"""
        return SysmemUtils.extract_important_definitions(content)

    def _extract_file_descriptions(self, readme_content: str) -> Dict[str, str]:
        """从README中提取文件描述"""
        return SysmemUtils.extract_file_descriptions(readme_content)

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """解析文档章节"""
        return SysmemUtils.parse_sections(content)

    def _suggest_file_action(self, filename: str) -> str:
        """建议文件处理方式"""
        return SysmemUtils.suggest_file_action(filename)

    def _get_current_time(self) -> str:
        """获取当前时间"""
        return SysmemUtils.get_current_time()

    def export_data(self, data: Dict[str, Any], output_file: str = "project_data.json") -> str:
        """导出收集的数据到.claude/skill/sysmem/目录"""
        # 确保目录存在
        claude_skill_dir = SysmemUtils.ensure_claude_skill_dir(self.root_path)
        output_path = claude_skill_dir / output_file

        # 导出数据
        SysmemUtils.export_json_data(data, output_path)

        print(f"📊 项目数据已导出到: {output_path}")
        return str(output_path)

if __name__ == "__main__":
    import sys

    # 确定目标目录：如果提供了参数就使用参数目录，否则使用当前工作目录
    target_directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    print(f"🎯 目标项目目录: {target_directory}")
    print(f"📍 脚本执行目录: {os.getcwd()}")

    # 创建目标目录的收集器实例
    collector = ProjectDataCollector(target_directory)

    # 检查目标目录是否存在
    if not os.path.exists(target_directory):
        print(f"❌ 错误: 目标目录 '{target_directory}' 不存在")
        sys.exit(1)

    data = collector.collect_all_data()
    output_file = collector.export_data(data)

    print(f"\n📋 数据收集摘要:")
    print(f"- 目标目录: {target_directory}")
    print(f"- 发现模块数量: {len(data['modules'])}")
    print(f"- CLAUDE.md存在: {'是' if data['claude_md_info']['exists'] else '否'}")
    print(f"- 架构问题: {len(data['architecture_analysis']['duplicate_files'])} 个重复文件, {len(data['architecture_analysis']['duplicate_functions'])} 个重复函数")
    print(f"- 未记录文件: {len(data['untracked_files'])} 个")
    print(f"✅ 数据文件已创建在目标项目的 .claude/skill/sysmem/ 目录中")