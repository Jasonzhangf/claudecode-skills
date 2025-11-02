#!/usr/bin/env python3
"""
Sysmem公共工具类 - 提供脚本间共享的工具函数
避免代码重复，提高维护性
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Set
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

    @staticmethod
    def parse_gitignore(gitignore_path: Path) -> Set[str]:
        """解析 .gitignore 文件，返回忽略模式集合"""
        if not gitignore_path.exists():
            return set()

        ignore_patterns = set()

        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                    # 处理目录模式（以/结尾）
                    if line.endswith('/'):
                        ignore_patterns.add(line.rstrip('/'))
                    else:
                        ignore_patterns.add(line)
        except Exception as e:
            print(f"⚠️  警告: 无法读取 .gitignore 文件: {e}")

        return ignore_patterns

    @staticmethod
    def should_ignore_path(path_name: str, is_directory: bool = False, ignore_patterns: Set[str] = None) -> bool:
        """检查文件/目录是否应该被忽略（兼容性方法）"""
        # 如果没有提供忽略模式，使用默认的
        if ignore_patterns is None:
            ignore_patterns = SysmemUtils.get_default_ignore_patterns()

        return SysmemUtils.should_ignore(path_name, ignore_patterns, is_directory)

    @staticmethod
    def should_ignore(path_name: str, ignore_patterns: Set[str], is_directory: bool = False) -> bool:
        """检查文件/目录是否应该被忽略"""
        path_name_lower = path_name.lower()

        for pattern in ignore_patterns:
            pattern_lower = pattern.lower()

            # 直接匹配
            if path_name_lower == pattern_lower:
                return True

            # 如果是目录模式，检查目录名匹配
            if is_directory and path_name_lower == pattern_lower:
                return True

            # 通配符匹配
            if '*' in pattern_lower:
                try:
                    regex_pattern = pattern_lower.replace('*', '.*')
                    if re.match(f"^{regex_pattern}$", path_name_lower):
                        return True
                except re.error:
                    # 忽略无效的正则表达式
                    continue

            # 检查是否以模式结尾（用于扩展名匹配）
            if pattern_lower.startswith('*') and path_name_lower.endswith(pattern_lower[1:]):
                return True

        return False

    @staticmethod
    def get_default_ignore_patterns() -> Set[str]:
        """获取默认忽略模式（兼容原有逻辑）"""
        return {
            '__pycache__', 'node_modules', 'target', 'build', 'dist',
            '.git', '.svn', '.hg', '.bzr',
            '*.pyc', '*.pyo', '*.pyd', '*.so', '.Python',
            'venv', 'env', 'ENV', '.venv', '.env',
            '.vscode', '.idea', '*.swp', '*.swo', '*~',
            '.DS_Store', '.AppleDouble', '.LSOverride', 'Icon', '._*',
            'Thumbs.db', 'Thumbs.db:encryptable', 'ehthumbs.db',
            'ehthumbs_vista.db', '*.stackdump', '[Dd]esktop.ini',
            '$RECYCLE.BIN/', '*.cab', '*.msi', '*.msix', '*.msm',
            '*.msp', '*.lnk', '.claude/', '.claude-temp/', 'skill-temp/',
            '*.session', '*.log', '*.tmp', 'temp/', 'cache/',
            'test_/', '*_test*/', 'tests/output/', '.coverage',
            '.pytest_cache/', 'htmlcov/', '*.bak', '*.backup',
            '*.zip', '*.tar.gz', '*.rar', '*.7z', '.env.local',
            '.env.*.local', 'secrets.json', 'api_keys.json',
            'manuscript/', 'progress/', 'session_state.json', '*.cache'
        }

    @staticmethod
    def get_git_changed_files(project_path: Path, since_when: str = "1day") -> Dict[str, Any]:
        """获取 git 变更文件信息"""
        import subprocess

        git_info = {
            "is_git_repo": False,
            "changed_files": [],
            "modified_modules": set(),
            "change_summary": {},
            "error": None
        }

        try:
            # 检查是否为 git 仓库
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                git_info["error"] = "不是 git 仓库"
                return git_info

            git_info["is_git_repo"] = True

            # 获取变更文件列表（最近1天）
            result = subprocess.run(
                ["git", "diff", "--name-only", f"HEAD@{{{since_when}}}", "HEAD"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                changed_files = result.stdout.strip().split('\n')
                git_info["changed_files"] = [f for f in changed_files if f.strip()]
            else:
                # 如果没有1天内的变更，获取最近3次的变更
                result = subprocess.run(
                    ["git", "log", "--oneline", "-3", "--name-only"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    changed_files = []
                    for line in lines:
                        if not line.startswith('commit') and not line.strip().startswith(' ') and line.strip():
                            changed_files.append(line.strip())
                    git_info["changed_files"] = list(set(changed_files))  # 去重

            # 分析变更影响的模块
            for file_path in git_info["changed_files"]:
                parts = Path(file_path).parts
                if len(parts) > 1:
                    # 第一级目录作为模块名
                    git_info["modified_modules"].add(parts[0])

            # 生成变更摘要
            git_info["change_summary"] = SysmemUtils.analyze_changes_impact(git_info["changed_files"])

        except subprocess.TimeoutExpired:
            git_info["error"] = "git 命令超时"
        except FileNotFoundError:
            git_info["error"] = "git 命令未找到"
        except Exception as e:
            git_info["error"] = f"git 操作失败: {str(e)}"

        return git_info

    @staticmethod
    def get_file_changes_by_mtime(project_path: Path, hours: int = 24) -> Dict[str, Any]:
        """基于文件修改时间检测变更（当 git 不可用时）"""
        import time

        change_info = {
            "changed_files": [],
            "modified_modules": set(),
            "change_summary": {},
            "detection_method": "mtime"
        }

        current_time = time.time()
        time_threshold = current_time - (hours * 3600)

        try:
            for file_path in project_path.rglob("*"):
                # 跳过隐藏文件和目录
                if file_path.name.startswith('.'):
                    continue

                if file_path.is_file():
                    file_mtime = file_path.stat().st_mtime
                    if file_mtime > time_threshold:
                        relative_path = file_path.relative_to(project_path)
                        change_info["changed_files"].append(str(relative_path))

                        # 分析影响的模块
                        parts = relative_path.parts
                        if len(parts) > 1:
                            change_info["modified_modules"].add(parts[0])

            # 生成变更摘要
            change_info["change_summary"] = SysmemUtils.analyze_changes_impact(change_info["changed_files"])

        except Exception as e:
            change_info["error"] = f"文件检测失败: {str(e)}"

        return change_info

    @staticmethod
    def analyze_changes_impact(changed_files: List[str]) -> Dict[str, Any]:
        """分析文件变更的影响范围"""
        impact = {
            "total_files": len(changed_files),
            "by_type": {},
            "by_module": {},
            "critical_changes": [],
            "recommended_updates": []
        }

        for file_path in changed_files:
            # 分析文件类型
            file_ext = Path(file_path).suffix.lower()
            if file_ext:
                impact["by_type"][file_ext] = impact["by_type"].get(file_ext, 0) + 1

            # 分析影响的模块
            parts = Path(file_path).parts
            if len(parts) > 1:
                module_name = parts[0]
                impact["by_module"][module_name] = impact["by_module"].get(module_name, 0) + 1

            # 检查关键变更
            if any(keyword in file_path.lower() for keyword in [
                'claude.md', 'readme', 'package.json', 'pyproject.toml',
                'requirements.txt', 'setup.py', '.gitignore'
            ]):
                impact["critical_changes"].append(file_path)

        # 生成更新建议
        if impact["critical_changes"]:
            impact["recommended_updates"].append("建议进行全面更新（发现关键文件变更）")

        if impact["by_module"]:
            most_affected_module = max(impact["by_module"], key=impact["by_module"].get)
            impact["recommended_updates"].append(f"重点关注模块: {most_affected_module}")

        return impact

    @staticmethod
    def clean_ignored_data(project_path: Path, old_data: Dict[str, Any],
                          new_ignore_patterns: Set[str]) -> Dict[str, Any]:
        """清理被.gitignore标记的文件数据"""
        print("🧹 清理被忽略的文件数据...", flush=True)

        cleaned_data = old_data.copy()
        cleaned_files = []
        cleaned_modules = []

        # 统计清理情况
        cleanup_stats = {
            "files_removed": 0,
            "modules_removed": 0,
            "directories_removed": 0,
            "cleaned_paths": []
        }

        # 清理模块数据
        if "modules" in cleaned_data:
            original_modules = list(cleaned_data["modules"].keys())
            remaining_modules = {}

            for module_name, module_data in cleaned_data["modules"].items():
                # 检查模块是否应该被忽略
                if SysmemUtils.should_ignore_path(module_name, True, new_ignore_patterns):
                    cleanup_stats["modules_removed"] += 1
                    cleanup_stats["cleaned_paths"].append(f"模块: {module_name}")
                    print(f"   🗑️  移除模块: {module_name}")
                else:
                    # 检查模块内的文件
                    cleaned_module_data = module_data.copy()

                    # 清理文件列表
                    if "files" in cleaned_module_data:
                        original_files = cleaned_module_data["files"][:]
                        remaining_files = []

                        for file_name in original_files:
                            file_path = f"{module_name}/{file_name}"
                            if SysmemUtils.should_ignore_path(file_path, False, new_ignore_patterns):
                                cleanup_stats["files_removed"] += 1
                                cleanup_stats["cleaned_paths"].append(f"文件: {file_path}")
                                print(f"   🗑️  移除文件: {file_path}")
                            else:
                                remaining_files.append(file_name)

                        cleaned_module_data["files"] = remaining_files

                    # 清理子目录列表
                    if "subdirectories" in cleaned_module_data:
                        original_dirs = cleaned_module_data["subdirectories"][:]
                        remaining_dirs = []

                        for dir_name in original_dirs:
                            dir_path = f"{module_name}/{dir_name}"
                            if SysmemUtils.should_ignore_path(dir_path, True, new_ignore_patterns):
                                cleanup_stats["directories_removed"] += 1
                                cleanup_stats["cleaned_paths"].append(f"目录: {dir_path}")
                                print(f"   🗑️  移除目录: {dir_path}")
                            else:
                                remaining_dirs.append(dir_name)

                        cleaned_module_data["subdirectories"] = remaining_dirs

                    # 只有当模块还有内容时才保留
                    if (remaining_files or remaining_dirs or
                        "readme_content" in cleaned_module_data):
                        remaining_modules[module_name] = cleaned_module_data
                    else:
                        cleanup_stats["modules_removed"] += 1
                        cleanup_stats["cleaned_paths"].append(f"空模块: {module_name}")
                        print(f"   🗑️  移除空模块: {module_name}")

            cleaned_data["modules"] = remaining_modules

        # 清理未记录文件列表
        if "untracked_files" in cleaned_data:
            original_untracked = cleaned_data["untracked_files"][:]
            remaining_untracked = []

            for file_info in original_untracked:
                if isinstance(file_info, dict):
                    file_path = file_info.get("file", "")
                else:
                    file_path = str(file_info)

                if file_path and not SysmemUtils.should_ignore_path(file_path, False, new_ignore_patterns):
                    remaining_untracked.append(file_info)
                else:
                    cleanup_stats["files_removed"] += 1
                    cleanup_stats["cleaned_paths"].append(f"未记录文件: {file_path}")

            cleaned_data["untracked_files"] = remaining_untracked

        # 更新扫描信息
        if "scan_info" in cleaned_data:
            scan_info = cleaned_data["scan_info"].copy()
            scan_info["data_cleanup"] = {
                "cleanup_time": SysmemUtils.get_current_time(),
                "cleanup_stats": cleanup_stats,
                "gitignore_rules_count": len(new_ignore_patterns)
            }
            cleaned_data["scan_info"] = scan_info

        # 添加清理建议
        cleanup_suggestions = []
        if cleanup_stats["modules_removed"] > 0:
            cleanup_suggestions.append(f"已移除 {cleanup_stats['modules_removed']} 个被忽略的模块")
        if cleanup_stats["files_removed"] > 0:
            cleanup_suggestions.append(f"已移除 {cleanup_stats['files_removed']} 个被忽略的文件")
        if cleanup_stats["directories_removed"] > 0:
            cleanup_suggestions.append(f"已移除 {cleanup_stats['directories_removed']} 个被忽略的目录")

        if "update_suggestions" not in cleaned_data:
            cleaned_data["update_suggestions"] = {}

        cleaned_data["update_suggestions"]["data_cleanup"] = cleanup_suggestions

        # 显示清理摘要
        total_removed = (cleanup_stats["modules_removed"] +
                        cleanup_stats["files_removed"] +
                        cleanup_stats["directories_removed"])

        if total_removed > 0:
            print(f"✅ 数据清理完成: 移除了 {total_removed} 个被忽略的项目")
        else:
            print("✅ 无需清理: 未发现被忽略的项目")

        return cleaned_data

    @staticmethod
    def get_ignored_paths(project_path: Path, ignore_patterns: Set[str]) -> Dict[str, Any]:
        """获取被忽略的路径列表（用于调试和报告）"""
        ignored_paths = {
            "ignored_modules": [],
            "ignored_files": [],
            "ignored_directories": []
        }

        # 扫描项目目录
        for item in project_path.iterdir():
            if item.name.startswith('.'):
                continue

            if item.is_dir():
                if SysmemUtils.should_ignore_path(item.name, True, ignore_patterns):
                    ignored_paths["ignored_modules"].append(item.name)
                    ignored_paths["ignored_directories"].append(item.name)

                # 递归检查子目录和文件
                for sub_item in item.rglob("*"):
                    if sub_item.is_file():
                        relative_path = sub_item.relative_to(project_path)
                        if SysmemUtils.should_ignore_path(str(relative_path), False, ignore_patterns):
                            ignored_paths["ignored_files"].append(str(relative_path))
                    elif sub_item.is_dir() and sub_item.name not in ignored_paths["ignored_directories"]:
                        relative_path = sub_item.relative_to(project_path)
                        if SysmemUtils.should_ignore_path(str(relative_path), True, ignore_patterns):
                            ignored_paths["ignored_directories"].append(str(relative_path))

        return ignored_paths