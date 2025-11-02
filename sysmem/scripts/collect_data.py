#!/usr/bin/env python3
"""
项目数据收集器 - 仅负责收集和分析项目数据，不直接修改文件
将分析结果交给Claude进行智能处理
"""

import os
import json
import ast
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict
from utils import SysmemUtils

class ProjectDataCollector:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.gitignore_path = self.root_path / ".gitignore"
        self.ignore_patterns = self._load_ignore_patterns()
        self.initial_scan_completed = False

    def _load_ignore_patterns(self) -> Set[str]:
        """加载忽略模式，合并 .gitignore 和默认模式"""
        # 从 .gitignore 加载模式
        gitignore_patterns = SysmemUtils.parse_gitignore(self.gitignore_path)

        # 合并默认模式
        default_patterns = SysmemUtils.get_default_ignore_patterns()

        all_patterns = gitignore_patterns.union(default_patterns)

        print(f"📋 已加载 {len(gitignore_patterns)} 个 .gitignore 规则")
        print(f"📋 合并 {len(default_patterns)} 个默认规则")
        print(f"📋 总计 {len(all_patterns)} 个忽略规则")

        return all_patterns

    def reload_ignore_patterns(self) -> None:
        """重新加载忽略模式（用于 .gitignore 更新后）"""
        old_count = len(self.ignore_patterns)
        self.ignore_patterns = self._load_ignore_patterns()
        new_count = len(self.ignore_patterns)

        print(f"🔄 忽略规则已更新: {old_count} → {new_count} 条规则")

    def should_ignore_path(self, path_name: str, is_directory: bool = False) -> bool:
        """检查路径是否应该被忽略"""
        return SysmemUtils.should_ignore(path_name, self.ignore_patterns, is_directory)

    def collect_single_module_data(self, module_path: str) -> Dict[str, Any]:
        """收集单个模块的数据"""
        print(f"🎯 开始收集单个模块数据: {module_path}", flush=True)

        target_path = self.root_path / module_path
        if not target_path.exists():
            print(f"❌ 错误: 模块路径 '{module_path}' 不存在")
            return {}

        if not target_path.is_dir():
            print(f"❌ 错误: '{module_path}' 不是一个目录")
            return {}

        # 检查模块是否有 README 文件
        readme_files = []
        for item in target_path.iterdir():
            if item.is_file() and item.name.lower().startswith('readme'):
                readme_files.append(item.name)

        if not readme_files:
            print(f"⚠️  警告: 模块 '{module_path}' 中未找到 README 文件")
            return {}

        # 收集模块数据
        module_data = self._collect_single_module(module_path, readme_files[0])

        print(f"✅ 模块 '{module_path}' 数据收集完成")
        return {module_path: module_data}

    def _collect_single_module(self, module_path: str, readme_file: str) -> Dict[str, Any]:
        """收集单个模块的详细数据"""
        module_dir = self.root_path / module_path

        # 获取目录中的文件和子目录（过滤忽略项）
        files = []
        subdirs = []

        for item in module_dir.iterdir():
            if self.should_ignore_path(item.name, item.is_dir()):
                continue

            if item.is_file():
                files.append(item.name)
            elif item.is_dir():
                subdirs.append(item.name)

        # 读取 README 内容
        readme_path = module_dir / readme_file
        readme_content = self._safe_read_file(readme_path)

        # 提取信息
        function_summary = self._extract_function_summary(readme_content)
        important_definitions = self._extract_important_definitions(readme_content)
        file_descriptions = self._extract_file_descriptions(readme_content)

        return {
            "path": module_path,
            "readme_file": readme_file,
            "readme_content": readme_content,
            "files": [f for f in files if not f.lower().startswith('readme')],
            "subdirectories": subdirs,
            "function_summary": function_summary,
            "important_definitions": important_definitions,
            "file_descriptions": file_descriptions,
            "scan_time": self._get_current_time()
        }

    def collect_module_specific_data(self, module_path: str) -> Dict[str, Any]:
        """收集模块特定的数据（包含基本的扫描信息）"""
        print(f"🔍 开始模块特定数据收集: {module_path}", flush=True)

        # 基本扫描信息
        data = {
            "scan_info": self._get_scan_info(),
            "target_module": module_path,
            "scan_mode": "module_specific"
        }

        # 收集指定模块数据
        modules_data = self.collect_single_module_data(module_path)
        data["modules"] = modules_data

        # 分析 CLAUDE.md（仅检查是否需要更新）
        print("📄 检查CLAUDE.md文件...")
        data["claude_md_info"] = self._analyze_claude_md_for_module(module_path)

        # 查找模块内未记录文件
        print("🔍 查找模块内未记录的文件...")
        data["untracked_files"] = self._find_untracked_files_in_module(module_path)

        # 生成模块特定更新建议
        print("💡 生成模块更新建议...")
        data["update_suggestions"] = self._generate_module_update_suggestions(module_path)

        print(f"✅ 模块 '{module_path}' 数据收集完成！")
        return data

    def collect_multiple_modules_data(self, module_paths: List[str]) -> Dict[str, Any]:
        """收集多个模块的数据"""
        print(f"🔍 开始收集 {len(module_paths)} 个模块的数据...", flush=True)

        # 基本扫描信息
        data = {
            "scan_info": self._get_scan_info(),
            "target_modules": module_paths,
            "scan_mode": "multi_module_specific"
        }

        # 收集所有指定模块的数据
        all_modules_data = {}
        all_untracked_files = []

        for module_path in module_paths:
            print(f"\n📦 处理模块: {module_path}")
            modules_data = self.collect_single_module_data(module_path)
            all_modules_data.update(modules_data)

            # 收集该模块的未记录文件
            untracked_files = self._find_untracked_files_in_module(module_path)
            all_untracked_files.extend(untracked_files)

        data["modules"] = all_modules_data
        data["untracked_files"] = all_untracked_files

        # 分析 CLAUDE.md
        print("📄 检查CLAUDE.md文件...")
        data["claude_md_info"] = self._analyze_claude_md()

        # 生成多模块更新建议
        print("💡 生成多模块更新建议...")
        data["update_suggestions"] = self._generate_multi_module_update_suggestions(module_paths)

        print(f"✅ {len(module_paths)} 个模块数据收集完成！")
        return data

    def _generate_multi_module_update_suggestions(self, module_paths: List[str]) -> Dict[str, Any]:
        """生成多模块更新的建议"""
        return {
            "claude_md_updates": [
                f"检查模块 {', '.join(module_paths)} 在 CLAUDE.md 中的描述是否准确",
                f"更新相关模块的架构信息和功能定义"
            ],
            "readme_updates": [
                f"检查模块 {', '.join(module_paths)} 的 README.md 功能描述",
                f"验证相关模块的文件结构说明",
                f"确认相关模块的重要定义是否标记为 Ground Truth"
            ],
            "multi_module_improvements": [
                f"处理模块 {', '.join(module_paths)} 内的重复文件",
                f"完善相关模块的文档覆盖率",
                f"检查模块间的依赖关系和一致性"
            ]
        }

    def execute_smart_update(self, user_confirmation: Dict[str, Any]) -> Dict[str, Any]:
        """执行用户确认的智能更新"""
        action = user_confirmation["action"]
        selected_modules = user_confirmation["selected_modules"]

        if action == "cancelled" or not user_confirmation["confirmed"]:
            print("❌ 用户取消更新")
            return None

        if action == "full":
            print("🔄 执行全面更新...")
            return self.collect_all_data()

        elif action == "selective":
            if not selected_modules:
                print("❌ 未选择要更新的模块")
                return None

            if len(selected_modules) == 1:
                print(f"🎯 执行单模块更新: {selected_modules[0]}")
                return self.collect_module_specific_data(selected_modules[0])
            else:
                print(f"🎯 执行多模块更新: {', '.join(selected_modules)}")
                return self.collect_multiple_modules_data(selected_modules)

        elif action == "none":
            print("✅ 无需更新")
            return None

        else:
            print(f"❌ 未知的更新行动: {action}")
            return None

    def _analyze_claude_md_for_module(self, module_path: str) -> Dict[str, Any]:
        """为特定模块分析 CLAUDE.md"""
        claude_md_info = self._analyze_claude_md()

        # 添加模块特定信息
        claude_md_info["target_module"] = module_path
        claude_md_info["needs_module_update"] = self._check_if_claude_md_needs_module_update(module_path)

        return claude_md_info

    def _check_if_claude_md_needs_module_update(self, module_path: str) -> bool:
        """检查 CLAUDE.md 是否需要为特定模块更新"""
        claude_md_path = self.root_path / "CLAUDE.md"

        if not claude_md_path.exists():
            return True

        content = self._safe_read_file(claude_md_path)

        # 简单检查：如果 CLAUDE.md 中没有提到该模块路径，可能需要更新
        return module_path not in content

    def _find_untracked_files_in_module(self, module_path: str) -> List[Dict[str, Any]]:
        """查找特定模块内未记录的文件"""
        untracked = []
        module_dir = self.root_path / module_path

        if not module_dir.exists():
            return untracked

        # 查找 README 文件
        readme_files = [f for f in module_dir.iterdir()
                       if f.is_file() and f.name.lower().startswith('readme')]

        if not readme_files:
            return untracked

        readme_path = readme_files[0]
        readme_content = self._safe_read_file(readme_path)

        # 扫描模块目录
        for item in module_dir.iterdir():
            if item.is_file() and not self.should_ignore_path(item.name, False):
                if (not item.name.lower().startswith('readme') and
                    not item.name.startswith('.') and
                    item.name not in readme_content):

                    untracked.append({
                        "file": f"{module_path}/{item.name}",
                        "module": module_path,
                        "suggestion": self._suggest_file_action(item.name)
                    })

        return untracked

    def _generate_module_update_suggestions(self, module_path: str) -> Dict[str, Any]:
        """生成模块特定的更新建议"""
        return {
            "claude_md_updates": [
                f"检查模块 '{module_path}' 在 CLAUDE.md 中的描述是否准确",
                f"更新模块 '{module_path}' 的功能定义和架构信息"
            ],
            "readme_updates": [
                f"检查模块 '{module_path}' 的 README.md 功能描述",
                f"验证模块 '{module_path}' 的文件结构说明",
                f"确认模块 '{module_path}' 的重要定义是否标记为 Ground Truth"
            ],
            "module_specific_improvements": [
                f"处理模块 '{module_path}' 内的重复文件",
                f"完善模块 '{module_path}' 的文档覆盖率",
                f"检查模块 '{module_path}' 的依赖关系"
            ]
        }

    def list_available_modules(self) -> List[str]:
        """列出可用的模块（包含 README 的目录）"""
        modules = []

        for item in self.root_path.iterdir():
            if (item.is_dir() and
                not item.name.startswith('.') and
                not self.should_ignore_path(item.name, True)):

                # 检查是否有 README 文件
                has_readme = any(f.name.lower().startswith('readme')
                               for f in item.iterdir()
                               if f.is_file())

                if has_readme:
                    modules.append(item.name)

        return sorted(modules)

    def detect_file_changes(self) -> Dict[str, Any]:
        """检测文件变更（基于 git 或文件修改时间）"""
        print("🔍 检测文件变更...", flush=True)

        # 首先尝试使用 git 检测
        git_changes = SysmemUtils.get_git_changed_files(self.root_path)

        if git_changes["is_git_repo"] and not git_changes.get("error"):
            print("✅ 使用 git 检测变更")
            return {
                "detection_method": "git",
                "changed_files": git_changes["changed_files"],
                "modified_modules": list(git_changes["modified_modules"]),
                "change_summary": git_changes["change_summary"],
                "critical_changes": git_changes["change_summary"].get("critical_changes", []),
                "recommendations": git_changes["change_summary"].get("recommended_updates", [])
            }
        else:
            # 如果 git 不可用，使用文件修改时间检测
            print("⚠️  Git 不可用，使用文件修改时间检测")
            mtime_changes = SysmemUtils.get_file_changes_by_mtime(self.root_path, hours=24)

            return {
                "detection_method": "mtime",
                "changed_files": mtime_changes["changed_files"],
                "modified_modules": list(mtime_changes["modified_modules"]),
                "change_summary": mtime_changes["change_summary"],
                "critical_changes": mtime_changes["change_summary"].get("critical_changes", []),
                "recommendations": mtime_changes["change_summary"].get("recommended_updates", []),
                "error": git_changes.get("error") or mtime_changes.get("error")
            }

    def analyze_update_strategy(self, changes_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析更新策略"""
        strategy = {
            "recommended_action": "selective",  # selective, full, none
            "affected_modules": [],
            "priority_modules": [],
            "reasoning": [],
            "user_choices": []
        }

        if not changes_info["changed_files"]:
            strategy["recommended_action"] = "none"
            strategy["reasoning"].append("未检测到文件变更")
            return strategy

        # 分析关键变更
        critical_changes = changes_info["critical_changes"]
        if critical_changes:
            strategy["recommended_action"] = "full"
            strategy["reasoning"].append(f"检测到 {len(critical_changes)} 个关键文件变更")
            strategy["priority_modules"] = changes_info["modified_modules"]
        else:
            strategy["recommended_action"] = "selective"
            strategy["affected_modules"] = changes_info["modified_modules"]

        # 添加推理过程
        total_changes = len(changes_info["changed_files"])
        strategy["reasoning"].append(f"检测到 {total_changes} 个文件变更")

        if changes_info["modified_modules"]:
            strategy["reasoning"].append(f"影响 {len(changes_info['modified_modules'])} 个模块: {', '.join(changes_info['modified_modules'])}")

        return strategy

    def interactive_update_confirmation(self, update_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """交互式更新确认"""
        print("\n" + "="*60)
        print("🤖 智能更新建议")
        print("="*60)

        # 显示变更摘要
        if update_strategy["recommended_action"] == "none":
            print("📋 变更摘要: 未检测到文件变更")
            print("💡 建议: 无需更新")

            user_input = input("\n是否仍要执行更新? (y/N): ").strip().lower()
            return {
                "confirmed": user_input in ['y', 'yes'],
                "selected_modules": [],
                "action": "none" if user_input not in ['y', 'yes'] else "full"
            }

        print("📋 变更摘要:")
        for reason in update_strategy["reasoning"]:
            print(f"  • {reason}")

        if update_strategy["recommendations"]:
            print("💡 系统建议:")
            for rec in update_strategy["recommendations"]:
                print(f"  • {rec}")

        # 根据推荐行动显示不同的确认界面
        if update_strategy["recommended_action"] == "full":
            print("\n🔄 推荐行动: 全面更新")
            print("   原因: 检测到关键文件变更")

            user_input = input("\n确认执行全面更新? (Y/n): ").strip().lower()
            if user_input in ['', 'y', 'yes']:
                return {
                    "confirmed": True,
                    "selected_modules": [],
                    "action": "full"
                }
            else:
                return {
                    "confirmed": False,
                    "selected_modules": [],
                    "action": "cancelled"
                }

        elif update_strategy["recommended_action"] == "selective":
            print(f"\n🎯 推荐行动: 选择性更新")
            print(f"   受影响模块: {', '.join(update_strategy['affected_modules'])}")

            # 获取可用模块列表
            available_modules = self.list_available_modules()
            affected_available_modules = [m for m in update_strategy["affected_modules"] if m in available_modules]

            if not affected_available_modules:
                print("⚠️  受影响的模块中没有可更新的模块")
                user_input = input("\n是否执行全面更新? (y/N): ").strip().lower()
                if user_input in ['y', 'yes']:
                    return {
                        "confirmed": True,
                        "selected_modules": [],
                        "action": "full"
                    }
                else:
                    return {
                        "confirmed": False,
                        "selected_modules": [],
                        "action": "cancelled"
                    }

            print(f"\n可更新的受影响模块:")
            for i, module in enumerate(affected_available_modules, 1):
                print(f"  {i}. {module}")

            print(f"\n请选择更新方式:")
            print(f"  1. 更新所有受影响模块 ({', '.join(affected_available_modules)})")
            print(f"  2. 选择特定模块")
            print(f"  3. 全面更新所有模块")
            print(f"  4. 取消更新")

            while True:
                choice = input(f"\n请输入选择 (1-4): ").strip()

                if choice == "1":
                    return {
                        "confirmed": True,
                        "selected_modules": affected_available_modules,
                        "action": "selective"
                    }
                elif choice == "2":
                    return self._select_specific_modules(affected_available_modules)
                elif choice == "3":
                    return {
                        "confirmed": True,
                        "selected_modules": [],
                        "action": "full"
                    }
                elif choice == "4":
                    return {
                        "confirmed": False,
                        "selected_modules": [],
                        "action": "cancelled"
                    }
                else:
                    print("⚠️  无效选择，请输入 1-4")

    def _select_specific_modules(self, available_modules: List[str]) -> Dict[str, Any]:
        """选择特定模块"""
        print(f"\n可选择的模块:")
        for i, module in enumerate(available_modules, 1):
            print(f"  {i}. {module}")

        print(f"\n输入要更新的模块编号，多个编号用逗号分隔 (例如: 1,3,5)")
        print(f"或输入 'all' 选择所有模块")

        while True:
            user_input = input(f"选择: ").strip().lower()

            if user_input == "all":
                return {
                    "confirmed": True,
                    "selected_modules": available_modules,
                    "action": "selective"
                }

            try:
                selected_indices = [int(x.strip()) for x in user_input.split(',')]
                selected_modules = []

                for idx in selected_indices:
                    if 1 <= idx <= len(available_modules):
                        selected_modules.append(available_modules[idx - 1])
                    else:
                        print(f"⚠️  编号 {idx} 超出范围，忽略")

                if selected_modules:
                    print(f"✅ 已选择模块: {', '.join(selected_modules)}")
                    confirm = input(f"确认选择? (Y/n): ").strip().lower()

                    if confirm in ['', 'y', 'yes']:
                        return {
                            "confirmed": True,
                            "selected_modules": selected_modules,
                            "action": "selective"
                        }
                else:
                    print("⚠️  未选择有效模块，请重新输入")

            except ValueError:
                print("⚠️  输入格式错误，请输入数字编号")

    def detect_if_full_update_needed(self) -> Dict[str, Any]:
        """智能检测是否需要全面更新（已弃用，使用 detect_file_changes 替代）"""
        # 保留此方法以兼容现有代码
        return {
            "needs_full_update": False,
            "reasons": ["请使用新的智能更新功能"],
            "recommendations": ["建议使用基于文件变更的智能更新"],
            "confidence": "low"
        }

    def _get_current_timestamp(self) -> int:
        """获取当前时间戳"""
        import time
        return int(time.time())

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

            # 使用动态忽略规则过滤目录
            dirs[:] = [d for d in dirs if not self.should_ignore_path(d, is_directory=True)]

            # 使用动态忽略规则过滤文件
            files = [f for f in files if not self.should_ignore_path(f, is_directory=False)]

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
            # 使用动态忽略规则过滤目录
            dirs[:] = [d for d in dirs if not self.should_ignore_path(d, is_directory=True)]

            # 使用动态忽略规则过滤文件
            files = [f for f in files if not self.should_ignore_path(f, is_directory=False)]

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

    def load_existing_data(self) -> Dict[str, Any]:
        """加载现有的项目数据文件"""
        try:
            import json
            # 尝试加载主要的project_data.json文件
            data_file = SysmemUtils.ensure_claude_skill_dir(self.root_path) / "project_data.json"

            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"📖 已加载现有数据文件: {data_file}")
                return data
            else:
                print(f"📂 未找到数据文件: {data_file}")
                return None

        except Exception as e:
            print(f"⚠️  加载数据文件失败: {e}")
            return None

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

    def rescan_after_gitignore_update(self) -> Dict[str, Any]:
        """在 .gitignore 更新后重新扫描项目"""
        print("🔄 检测到 .gitignore 可能已更新，重新加载忽略规则...", flush=True)

        # 重新加载忽略规则
        self.reload_ignore_patterns()

        # 重新收集数据
        print("🔍 重新扫描项目数据...", flush=True)
        return self.collect_all_data()

    def clean_data_after_ignore_update(self) -> Dict[str, Any]:
        """清理因忽略规则更新而过时的数据"""
        print("🧹 清理过时的扫描数据...", flush=True)

        # 加载现有数据
        old_data = self.load_existing_data()
        if not old_data:
            print("⚠️  未找到现有数据文件，无法执行清理")
            return None

        # 重新加载忽略规则
        old_patterns_count = len(self.ignore_patterns)
        self.reload_ignore_patterns()
        new_patterns_count = len(self.ignore_patterns)

        print(f"📋 忽略规则已更新: {old_patterns_count} → {new_patterns_count} 条规则")

        # 使用新的忽略规则清理旧数据
        cleaned_data = SysmemUtils.clean_ignored_data(
            self.root_path,
            old_data,
            self.ignore_patterns
        )

        print("✅ 数据清理完成", flush=True)
        return cleaned_data

    def generate_ignore_report(self) -> Dict[str, Any]:
        """生成忽略规则报告"""
        print("📋 生成忽略规则报告...", flush=True)

        # 确保忽略规则已加载
        if not self.ignore_patterns:
            self.reload_ignore_patterns()

        # 获取被忽略的路径
        ignored_paths = SysmemUtils.get_ignored_paths(self.root_path, self.ignore_patterns)

        # 构建报告
        report = {
            "total_rules": len(self.ignore_patterns),
            "ignored_modules": ignored_paths["ignored_modules"],
            "ignored_files": ignored_paths["ignored_files"],
            "ignored_directories": ignored_paths["ignored_directories"],
            "generation_time": SysmemUtils.get_current_time()
        }

        return report

    def clean_and_reclean_data(self) -> Dict[str, Any]:
        """清理旧数据并重新收集（当.gitignore发生重大变更时）"""
        print("🔄 检测到 .gitignore 重大变更，执行完整的数据清理和重新收集...", flush=True)

        # 重新加载忽略规则
        old_patterns_count = len(self.ignore_patterns) if self.ignore_patterns else 0
        self.reload_ignore_patterns()
        new_patterns_count = len(self.ignore_patterns)

        # 加载现有数据
        old_data = self.load_existing_data()
        if not old_data:
            print("🔍 未找到现有数据文件，将直接收集新数据")
            return self.collect_all_data()

        print("📖 已加载现有数据文件")

        # 清理旧数据
        print("🧹 清理旧数据中的被忽略项目...")
        cleaned_data = SysmemUtils.clean_ignored_data(
            self.root_path,
            old_data,
            self.ignore_patterns
        )

        # 更新扫描信息
        if "scan_info" not in cleaned_data:
            cleaned_data["scan_info"] = {}

        cleaned_data["scan_info"]["full_reclean"] = {
            "reason": "gitignore_major_changes",
            "reclean_time": self._get_current_time(),
            "old_patterns_count": old_patterns_count,
            "new_patterns_count": new_patterns_count
        }

        # 重新收集部分数据以补充清理后的数据
        print("🔍 补充收集新数据...")
        new_data = self.collect_all_data()

        # 合并数据
        merged_data = cleaned_data.copy()
        merged_data["modules"] = new_data["modules"]
        merged_data["untracked_files"] = new_data["untracked_files"]
        merged_data["claude_md_info"] = new_data["claude_md_info"]

        # 添加清理信息
        if "update_suggestions" not in merged_data:
            merged_data["update_suggestions"] = {}

        merged_data["update_suggestions"]["data_reclean"] = [
            f"已完成数据清理和重新收集",
            f"移除了被.gitignore标记的项目",
            f"重新扫描了当前项目状态"
        ]

        print("✅ 数据清理和重新收集完成", flush=True)
        return merged_data

    def get_ignore_changes_report(self) -> Dict[str, Any]:
        """生成忽略规则变更报告"""
        # 重新加载规则
        old_count = len(self.ignore_patterns)
        self.reload_ignore_patterns()
        new_count = len(self.ignore_patterns)

        # 获取被忽略的路径列表
        ignored_paths = SysmemUtils.get_ignored_paths(self.root_path, self.ignore_patterns)

        # 分析gitignore文件
        gitignore_content = self._safe_read_file(self.gitignore_path)

        report = {
            "gitignore_file": str(self.gitignore_path),
            "gitignore_exists": self.gitignore_path.exists(),
            "gitignore_size": len(gitignore_content) if gitignore_content else 0,
            "total_ignore_rules": new_count,
            "rule_change": new_count - old_count,
            "ignored_paths_count": {
                "modules": len(ignored_paths["ignored_modules"]),
                "files": len(ignored_paths["ignored_files"]),
                "directories": len(ignored_paths["ignored_directories"])
            },
            "sample_ignored_items": {
                "modules": ignored_paths["ignored_modules"][:5],
                "files": ignored_paths["ignored_files"][:10],
                "directories": ignored_paths["ignored_directories"][:5]
            }
        }

        return report

    def should_force_full_reclean(self) -> bool:
        """判断是否需要强制完整重新收集"""
        # 检查是否有现有数据文件
        claude_skill_dir = self.root_path / ".claude" / "skill" / "sysmem"
        project_data_file = claude_skill_dir / "project_data.json"

        if not project_data_file.exists():
            return False

        try:
            # 检查数据文件的修改时间
            data_mtime = project_data_file.stat().st_mtime
            gitignore_mtime = self.gitignore_path.stat().st_mtime

            # 如果.gitignore比数据文件新，且差异较大，建议重新收集
            if gitignore_mtime > data_mtime:
                time_diff = gitignore_mtime - data_mtime
                # 如果差异超过1小时，建议重新收集
                if time_diff > 3600:  # 1小时
                    return True

            # 检查gitignore内容的重大变化
            current_rules = len(self.ignore_patterns)
            if current_rules > 50:  # 规则数量较多时建议重新收集
                return True

        except Exception:
            pass

        return False

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

    # 解析命令行参数
    target_directory = None
    target_module = None
    rescan_mode = False
    list_modules_mode = False
    full_scan_mode = False
    interactive_mode = False
    clean_mode = False
    full_clean_mode = False
    ignore_report_mode = False
    help_mode = False

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ['--rescan', '-r']:
            rescan_mode = True
        elif arg in ['--help', '-h']:
            help_mode = True
        elif arg in ['--list-modules', '-l']:
            list_modules_mode = True
        elif arg in ['--module', '-m']:
            if i + 1 < len(sys.argv):
                target_module = sys.argv[i + 1]
                i += 1
            else:
                print("❌ 错误: --module 参数需要指定模块名称")
                sys.exit(1)
        elif arg in ['--full-scan', '-f']:
            full_scan_mode = True
        elif arg in ['--interactive', '-i']:
            interactive_mode = True
        elif arg in ['--clean', '-c']:
            clean_mode = True
        elif arg == '--full-clean':
            full_clean_mode = True
        elif arg == '--ignore-report':
            ignore_report_mode = True
        elif not arg.startswith('-') and target_directory is None:
            target_directory = arg
        i += 1

    if help_mode:
        print("""
📋 Sysmem 项目数据收集器 - 支持模块化更新

用法:
    python collect_data.py [目录路径] [选项]

选项:
    -m, --module <name>    仅扫描指定模块（避免全面更新）
    -l, --list-modules     列出可用的模块
    -f, --full-scan        强制全面扫描所有模块
    -i, --interactive      智能交互式更新（基于文件变更检测）
    -r, --rescan           重新扫描模式（用于 .gitignore 更新后）
    -c, --clean            清理被.gitignore标记的数据
    --full-clean           清理并重新收集所有数据
    --ignore-report        显示.gitignore变更报告
    -h, --help             显示帮助信息

示例:
    # 智能交互式更新（推荐新方式）
    python collect_data.py --interactive              # 检测文件变更并询问更新范围
    python collect_data.py -i                         # 简写形式

    # 模块化更新（精确控制）
    python collect_data.py --module scripts          # 仅更新 scripts 模块
    python collect_data.py -m examples/basic         # 仅更新指定模块

    # 查看可用模块
    python collect_data.py --list-modules

    # 全面更新（仅在必要时使用）
    python collect_data.py --full-scan               # 强制全面扫描
    python collect_data.py                           # 默认智能模式

    # 重新扫描
    python collect_data.py --rescan                  # 重新扫描当前目录
    python collect_data.py -m scripts --rescan       # 重新扫描指定模块

    # 数据清理（新增功能）
    python collect_data.py --clean                   # 清理被.gitignore标记的数据
    python collect_data.py --full-clean              # 清理并重新收集所有数据
    python collect_data.py --ignore-report          # 显示.gitignore变更报告

功能:
    • 🤖 智能交互式更新 - 基于文件变更检测，用户确认更新范围
    • 📊 Git 集成检测 - 自动检测 git 仓库中的文件变更
    • ⏰ 文件时间检测 - 当 git 不可用时，基于文件修改时间
    • 🎯 精确模块化更新 - 避免不必要的全面扫描
    • 🧹 智能数据清理 - 自动清理被.gitignore标记的文件数据
    • 📋 读取并解析 .gitignore 文件
    • 🔍 动态过滤不需要扫描的文件和目录
    • 🔄 支持 .gitignore 更新后的重新扫描和数据清理
    • 📈 生成精确的模块数据报告
        """)
        sys.exit(0)

    # 确定目标目录：如果提供了参数就使用参数目录，否则使用当前工作目录
    if target_directory is None:
        target_directory = os.getcwd()

    print(f"🎯 目标项目目录: {target_directory}")
    print(f"📍 脚本执行目录: {os.getcwd()}")

    # 创建目标目录的收集器实例
    collector = ProjectDataCollector(target_directory)

    # 检查目标目录是否存在
    if not os.path.exists(target_directory):
        print(f"❌ 错误: 目标目录 '{target_directory}' 不存在")
        sys.exit(1)

    data = None
    scan_mode_description = ""

    # 处理不同的扫描模式
    if list_modules_mode:
        print("📋 模式: 列出可用模块")
        modules = collector.list_available_modules()
        if modules:
            print(f"\n📦 发现 {len(modules)} 个可用模块:")
            for i, module in enumerate(modules, 1):
                print(f"  {i}. {module}")
            print(f"\n💡 使用方法: python collect_data.py --module <模块名>")
        else:
            print("⚠️  未找到包含 README 文件的模块")
        sys.exit(0)

    elif clean_mode:
        print("🧹 模式: 清理被.gitignore标记的数据")
        scan_mode_description = "数据清理"

        # 执行数据清理
        data = collector.clean_data_after_ignore_update()

        if data:
            output_file = collector.export_data(data)
            print(f"✅ 数据清理完成，已更新项目数据")
        else:
            print("⚠️  未找到需要清理的数据或清理失败")
            sys.exit(1)

    elif full_clean_mode:
        print("🧹 模式: 清理并重新收集所有数据")
        scan_mode_description = "清理并重新收集"

        # 执行清理并重新收集
        data = collector.clean_and_reclean_data()

        if data:
            output_file = collector.export_data(data)
            print(f"✅ 清理并重新收集完成")
        else:
            print("⚠️  清理并重新收集失败")
            sys.exit(1)

    elif ignore_report_mode:
        print("📋 模式: 显示.gitignore变更报告")
        scan_mode_description = "忽略规则报告"

        # 生成忽略规则报告
        report = collector.generate_ignore_report()

        if report:
            print(f"\n📊 .gitignore 规则报告:")
            print(f"- 忽略规则总数: {report.get('total_rules', 0)}")
            print(f"- 被忽略的模块: {len(report.get('ignored_modules', []))}")
            print(f"- 被忽略的文件: {len(report.get('ignored_files', []))}")
            print(f"- 被忽略的目录: {len(report.get('ignored_directories', []))}")

            if report.get('ignored_modules'):
                print(f"\n🚫 被忽略的模块:")
                for module in report['ignored_modules']:
                    print(f"  - {module}")

            if report.get('ignored_files')[:10]:  # 只显示前10个
                print(f"\n🚫 被忽略的文件 (前10个):")
                for file in report['ignored_files'][:10]:
                    print(f"  - {file}")
                if len(report['ignored_files']) > 10:
                    print(f"  - ... 还有 {len(report['ignored_files']) - 10} 个文件")
        else:
            print("⚠️  生成忽略规则报告失败")

        sys.exit(0)

    elif interactive_mode:
        print("🤖 模式: 智能交互式更新")
        scan_mode_description = "智能交互式更新"

        # 1. 检测文件变更
        changes_info = collector.detect_file_changes()

        if changes_info.get("error"):
            print(f"⚠️  变更检测警告: {changes_info['error']}")

        # 2. 分析更新策略
        update_strategy = collector.analyze_update_strategy(changes_info)

        # 3. 用户交互确认
        user_confirmation = collector.interactive_update_confirmation(update_strategy)

        # 4. 执行更新
        if user_confirmation and user_confirmation["confirmed"]:
            data = collector.execute_smart_update(user_confirmation)

            if data:
                # 根据更新类型选择输出文件名
                action = user_confirmation["action"]
                if action == "selective":
                    modules = user_confirmation["selected_modules"]
                    if len(modules) == 1:
                        output_file = collector.export_data(data, f"module_{modules[0]}_data.json")
                    else:
                        module_names = "_".join(modules)
                        output_file = collector.export_data(data, f"multi_{module_names}_data.json")
                else:
                    output_file = collector.export_data(data)

                # 显示结果摘要
                print(f"\n📋 更新完成摘要:")
                print(f"- 目标目录: {target_directory}")
                print(f"- 更新模式: {scan_mode_description}")
                print(f"- 检测方法: {changes_info['detection_method']}")
                print(f"- 变更文件数: {len(changes_info['changed_files'])}")

                if action == "selective":
                    print(f"- 更新模块: {', '.join(user_confirmation['selected_modules'])}")
                else:
                    print(f"- 更新类型: 全面更新")

                print(f"- 发现模块数量: {len(data['modules'])}")
                print(f"- 未记录文件: {len(data['untracked_files'])} 个")
                print(f"✅ 数据文件已创建在目标项目的 .claude/skill/sysmem/ 目录中")

                print(f"\n💡 智能提示:")
                print(f"• 交互式更新已完成")
                print(f"• 下次可以直接使用: python collect_data.py --module <模块名> 进行精确更新")
            else:
                print("❌ 更新执行失败")
        else:
            print("❌ 用户取消更新或更新未确认")
        sys.exit(0)

    elif target_module:
        # 模块特定扫描
        print(f"🎯 模式: 模块化更新 - {target_module}")
        scan_mode_description = f"模块化更新 ({target_module})"

        # 验证模块是否存在
        available_modules = collector.list_available_modules()
        if target_module not in available_modules:
            print(f"❌ 错误: 模块 '{target_module}' 不存在或没有 README 文件")
            print(f"📦 可用模块: {', '.join(available_modules)}")
            print(f"💡 使用 --list-modules 查看所有可用模块")
            sys.exit(1)

        if rescan_mode:
            print("🔄 重新扫描模式：重新加载忽略规则")
            collector.reload_ignore_patterns()

        # 收集模块特定数据
        data = collector.collect_module_specific_data(target_module)

    elif full_scan_mode:
        # 强制全面扫描
        print("🔍 模式: 强制全面扫描")
        scan_mode_description = "全面扫描"

        # 检查 .gitignore 文件状态
        gitignore_path = Path(target_directory) / ".gitignore"
        if gitignore_path.exists():
            print(f"📄 发现 .gitignore 文件: {gitignore_path}")
            if rescan_mode:
                print("🔄 重新扫描模式：重新加载忽略规则")
                data = collector.rescan_after_gitignore_update()
            else:
                print("📖 全面扫描模式：使用当前忽略规则")
                data = collector.collect_all_data()
        else:
            print("⚠️  未找到 .gitignore 文件，使用默认忽略规则")
            data = collector.collect_all_data()

    else:
        # 默认智能模式
        print("🧠 模式: 智能扫描（自动判断扫描范围）")
        scan_mode_description = "智能扫描"

        # 执行智能检测
        detection_result = collector.detect_if_full_update_needed()

        # 根据检测结果决定扫描策略
        if detection_result["needs_full_update"] and detection_result["confidence"] == "high":
            print("🔄 智能决策: 检测到需要全面更新，执行全面扫描")
            scan_mode_description = "智能全面扫描"

            # 检查 .gitignore 文件状态
            gitignore_path = Path(target_directory) / ".gitignore"
            if gitignore_path.exists():
                print(f"📄 发现 .gitignore 文件: {gitignore_path}")
                if rescan_mode:
                    print("🔄 重新扫描模式：重新加载忽略规则")
                    data = collector.rescan_after_gitignore_update()
                else:
                    print("📖 智能全面扫描模式：使用当前忽略规则")
                    data = collector.collect_all_data()
            else:
                print("⚠️  未找到 .gitignore 文件，使用默认忽略规则")
                data = collector.collect_all_data()

        else:
            print("🎯 智能决策: 推荐模块化更新")
            available_modules = collector.list_available_modules()

            if available_modules:
                print(f"📦 发现 {len(available_modules)} 个可用模块")
                print("💡 推荐使用模块化更新以避免不必要的全面扫描")
                print(f"   使用 --list-modules 查看所有模块")
                print(f"   使用 --module <模块名> 更新特定模块")
                print(f"   使用 --full-scan 强制全面扫描")

                # 执行轻量级扫描（仅收集基本信息）
                print("🔍 执行轻量级扫描...")
                data = collector.collect_all_data()
                scan_mode_description = "智能轻量扫描"
            else:
                print("⚠️  未发现可用模块，执行全面扫描")
                data = collector.collect_all_data()
                scan_mode_description = "智能全面扫描"

    # 导出数据
    if data:
        # 根据扫描模式选择输出文件名
        if target_module:
            output_file = collector.export_data(data, f"module_{target_module}_data.json")
        else:
            output_file = collector.export_data(data)

        # 显示摘要
        print(f"\n📋 数据收集摘要:")
        print(f"- 目标目录: {target_directory}")
        print(f"- 扫描模式: {scan_mode_description}")

        if target_module:
            print(f"- 目标模块: {target_module}")
            print(f"- 模块扫描结果: {'成功' if data['modules'] else '失败'}")
            print(f"- 未记录文件: {len(data['untracked_files'])} 个")
        else:
            print(f"- 发现模块数量: {len(data['modules'])}")
            print(f"- CLAUDE.md存在: {'是' if data['claude_md_info']['exists'] else '否'}")
            print(f"- 架构问题: {len(data['architecture_analysis']['duplicate_files'])} 个重复文件, {len(data['architecture_analysis']['duplicate_functions'])} 个重复函数")
            print(f"- 未记录文件: {len(data['untracked_files'])} 个")

        print(f"✅ 数据文件已创建在目标项目的 .claude/skill/sysmem/ 目录中")

        # 智能提示
        print(f"\n💡 智能提示:")
        if target_module:
            print(f"• 模块 '{target_module}' 更新完成")
            print(f"• 如需更新其他模块，使用: python collect_data.py --module <模块名>")
            print(f"• 如需全面更新，使用: python collect_data.py --full-scan")
        elif not full_scan_mode:
            available_modules = collector.list_available_modules()
            if available_modules:
                print(f"• 发现 {len(available_modules)} 个模块，建议使用模块化更新:")
                for module in available_modules[:3]:  # 显示前3个
                    print(f"  - python collect_data.py --module {module}")
                if len(available_modules) > 3:
                    print(f"  - ... 还有 {len(available_modules) - 3} 个模块")
                print(f"• 使用 --list-modules 查看所有模块")
                print(f"• 仅在必要时使用 --full-scan 进行全面更新")
        else:
            print(f"• 全面扫描已完成，建议后续使用模块化更新")

        if rescan_mode:
            print(f"• 重新扫描已完成，数据已根据新的 .gitignore 规则更新")

        print(f"• 使用 -h 查看更多选项")