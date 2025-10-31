#!/usr/bin/env python3
"""
项目指纹系统 - 检测项目变更，支持增量数据收集
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Set, Optional
from utils import SysmemUtils

class ProjectFingerprint:
    """项目指纹管理器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.fingerprint_file = self.project_path / ".claude" / "skill" / "sysmem" / ".fingerprint.json"
        self.ensure_fingerprint_dir()

    def ensure_fingerprint_dir(self):
        """确保指纹目录存在"""
        self.fingerprint_file.parent.mkdir(parents=True, exist_ok=True)

    def generate_fingerprint(self) -> Dict[str, Any]:
        """生成项目指纹"""
        print("🔍 生成项目指纹...")

        fingerprint = {
            "scan_time": SysmemUtils.get_current_time(),
            "scan_timestamp": time.time(),
            "project_root": str(self.project_path),
            "file_hashes": self._get_file_hashes(),
            "dir_structure": self._get_dir_structure(),
            "total_files": self._count_files(),
            "total_dirs": self._count_dirs(),
            "key_files_mtime": self._get_key_files_mtime(),
            "python_files": self._get_python_files(),
            "config_files": self._get_config_files(),
            "readme_files": self._get_readme_files(),
            "claude_md_exists": (self.project_path / "CLAUDE.md").exists(),
            "claude_md_mtime": self._get_file_mtime(self.project_path / "CLAUDE.md")
        }

        print(f"✅ 指纹生成完成 - {fingerprint['total_files']} 个文件, {fingerprint['total_dirs']} 个目录")
        return fingerprint

    def has_changed(self) -> bool:
        """检查项目是否有变更"""
        if not self.fingerprint_file.exists():
            print("📋 未找到指纹文件，视为新项目")
            return True

        try:
            old_fingerprint = self._load_fingerprint()
            new_fingerprint = self.generate_fingerprint()

            # 简单比较关键指标
            if self._has_significant_changes(old_fingerprint, new_fingerprint):
                print("🔄 检测到项目变更")
                return True
            else:
                print("✅ 项目无重大变更")
                return False

        except Exception as e:
            print(f"⚠️ 指纹检查失败: {e}，视为有变更")
            return True

    def save_fingerprint(self, fingerprint: Dict[str, Any] = None):
        """保存项目指纹"""
        if fingerprint is None:
            fingerprint = self.generate_fingerprint()

        SysmemUtils.export_json_data(fingerprint, self.fingerprint_file)
        print(f"💾 指纹已保存: {self.fingerprint_file}")

    def _load_fingerprint(self) -> Dict[str, Any]:
        """加载现有指纹"""
        try:
            with open(self.fingerprint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载指纹失败: {e}")
            return {}

    def _get_file_hashes(self) -> Dict[str, str]:
        """获取文件哈希值"""
        file_hashes = {}

        # 只计算关键文件的哈希，避免全量计算
        important_files = self._get_important_files()

        for file_path in important_files:
            try:
                if file_path.exists() and file_path.is_file():
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        relative_path = str(file_path.relative_to(self.project_path))
                        file_hashes[relative_path] = file_hash
            except Exception:
                continue

        return file_hashes

    def _get_dir_structure(self) -> List[str]:
        """获取目录结构"""
        dir_structure = []

        try:
            for root, dirs, files in os.walk(self.project_path):
                # 跳过隐藏目录和常见忽略目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and
                         d not in ['node_modules', '__pycache__', 'target', 'build', 'dist', '.git']]

                root_path = Path(root)
                if root_path != self.project_path:
                    relative_path = str(root_path.relative_to(self.project_path))
                    dir_structure.append(relative_path)

        except Exception as e:
            print(f"⚠️ 获取目录结构失败: {e}")

        return sorted(dir_structure)

    def _count_files(self) -> int:
        """计算文件总数"""
        count = 0
        try:
            for root, dirs, files in os.walk(self.project_path):
                # 跳过隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                count += len(files)
        except Exception:
            pass
        return count

    def _count_dirs(self) -> int:
        """计算目录总数"""
        count = 0
        try:
            for root, dirs, files in os.walk(self.project_path):
                # 跳过隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                count += len(dirs)
        except Exception:
            pass
        return count

    def _get_key_files_mtime(self) -> Dict[str, float]:
        """获取关键文件的修改时间"""
        key_files = {}
        key_patterns = ['*.py', '*.js', '*.json', '*.yml', '*.yaml', '*.md', '*.txt']

        try:
            for pattern in key_patterns:
                for file_path in self.project_path.rglob(pattern):
                    if self._is_important_file(file_path):
                        relative_path = str(file_path.relative_to(self.project_path))
                        key_files[relative_path] = file_path.stat().st_mtime
        except Exception:
            pass

        return key_files

    def _get_python_files(self) -> List[str]:
        """获取Python文件列表"""
        python_files = []
        try:
            for file_path in self.project_path.rglob("*.py"):
                relative_path = str(file_path.relative_to(self.project_path))
                python_files.append(relative_path)
        except Exception:
            pass
        return sorted(python_files)

    def _get_config_files(self) -> List[str]:
        """获取配置文件列表"""
        config_patterns = [
            "package.json", "requirements.txt", "pyproject.toml",
            "setup.py", "Makefile", "Dockerfile", ".env", "*.yml", "*.yaml"
        ]

        config_files = []
        try:
            for pattern in config_patterns:
                for file_path in self.project_path.glob(pattern):
                    relative_path = str(file_path.relative_to(self.project_path))
                    config_files.append(relative_path)
        except Exception:
            pass
        return sorted(config_files)

    def _get_readme_files(self) -> List[str]:
        """获取README文件列表"""
        readme_files = []
        try:
            for file_path in self.project_path.rglob("README*"):
                if file_path.is_file():
                    relative_path = str(file_path.relative_to(self.project_path))
                    readme_files.append(relative_path)
        except Exception:
            pass
        return sorted(readme_files)

    def _get_important_files(self) -> List[Path]:
        """获取重要文件列表"""
        important_files = []

        # 项目根目录重要文件
        root_files = [
            "CLAUDE.md", "README.md", "package.json", "requirements.txt",
            "pyproject.toml", "setup.py", "Dockerfile", ".gitignore"
        ]

        for filename in root_files:
            file_path = self.project_path / filename
            if file_path.exists():
                important_files.append(file_path)

        # 脚本目录文件
        scripts_dir = self.project_path / "scripts"
        if scripts_dir.exists():
            for file_path in scripts_dir.glob("*.py"):
                important_files.append(file_path)

        # 源码目录的主要文件（限制数量）
        src_dirs = ["src", "lib", "app"]
        for src_dir in src_dirs:
            src_path = self.project_path / src_dir
            if src_path.exists():
                count = 0
                for file_path in src_path.rglob("*.py"):
                    if count < 50:  # 限制文件数量
                        important_files.append(file_path)
                        count += 1
                    else:
                        break

        return important_files

    def _is_important_file(self, file_path: Path) -> bool:
        """判断是否为重要文件"""
        file_name = file_path.name.lower()

        # 重要文件名
        important_names = {
            'claude.md', 'readme.md', 'package.json', 'requirements.txt',
            'pyproject.toml', 'setup.py', 'dockerfile', '.gitignore',
            'main.py', 'app.py', 'index.js', 'server.py'
        }

        # 重要扩展名
        important_extensions = {'.py', '.js', '.json', '.yml', '.yaml', '.md'}

        # 跳过的目录
        skip_dirs = {'node_modules', '__pycache__', '.git', 'dist', 'build', '.vscode', '.idea'}

        # 检查文件名
        if file_name in important_names:
            return True

        # 检查扩展名
        if file_path.suffix.lower() in important_extensions:
            # 检查路径中是否包含跳过的目录
            for part in file_path.parts:
                if part in skip_dirs:
                    return False
            return True

        return False

    def _get_file_mtime(self, file_path: Path) -> Optional[float]:
        """获取文件修改时间"""
        try:
            return file_path.stat().st_mtime if file_path.exists() else None
        except Exception:
            return None

    def _has_significant_changes(self, old_fp: Dict, new_fp: Dict) -> bool:
        """检查是否有重大变更"""
        # 检查关键指标
        checks = [
            ('total_files', lambda old, new: abs(old - new) > 10),
            ('total_dirs', lambda old, new: abs(old - new) > 5),
            ('claude_md_exists', lambda old, new: old != new),
            ('claude_md_mtime', lambda old, new: old is not None and new is not None and abs(old - new) > 1),
            ('python_files', lambda old, new: self._list_changed(old, new) > 5),
            ('readme_files', lambda old, new: self._list_changed(old, new) > 0),
            ('config_files', lambda old, new: self._list_changed(old, new) > 0)
        ]

        for key, check_func in checks:
            if key in old_fp and key in new_fp:
                if check_func(old_fp[key], new_fp[key]):
                    print(f"🔍 检测到变更: {key}")
                    return True

        # 检查关键文件哈希
        if 'file_hashes' in old_fp and 'file_hashes' in new_fp:
            old_hashes = set(old_fp['file_hashes'].items())
            new_hashes = set(new_fp['file_hashes'].items())

            if old_hashes != new_hashes:
                print("🔍 检测到文件内容变更")
                return True

        return False

    def _list_changed(self, old_list: List[str], new_list: List[str]) -> int:
        """计算列表变化数量"""
        if not isinstance(old_list, list) or not isinstance(new_list, list):
            return 1

        old_set = set(old_list)
        new_set = set(new_list)

        added = len(new_set - old_set)
        removed = len(old_set - new_set)

        return added + removed

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."

    fp = ProjectFingerprint(project_path)

    if len(sys.argv) > 2 and sys.argv[2] == "--check":
        changed = fp.has_changed()
        print(f"变更状态: {'有变更' if changed else '无变更'}")
    else:
        fingerprint = fp.generate_fingerprint()
        fp.save_fingerprint(fingerprint)
        print("✅ 指纹生成完成")