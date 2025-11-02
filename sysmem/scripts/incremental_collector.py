#!/usr/bin/env python3
"""
增量数据收集器 - 智能增量更新项目数据
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Set, Optional
from fingerprint import ProjectFingerprint
from change_detector import ChangeDetector, ChangeLevel
from collect_data import ProjectDataCollector
from utils import SysmemUtils

class IncrementalCollector:
    """增量数据收集器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.data_file = self.project_path / ".claude" / "skill" / "sysmem" / "project_data.json"
        self.fingerprinter = ProjectFingerprint(str(self.project_path))
        self.detector = ChangeDetector()

    def smart_collect(self, force: bool = False, interactive: bool = True) -> Dict[str, Any]:
        """智能数据收集入口"""
        print("🚀 开始智能数据收集...")
        print(f"📁 目标项目: {self.project_path}")

        # 1. 检查是否需要收集
        if not force:
            should_collect, conditions, level = self.detector.should_collect(str(self.project_path))

            if not should_collect:
                if interactive:
                    print(self.detector.format_change_report(False, conditions, level))
                    choice = input("是否强制进行数据收集？(y/N): ").strip().lower()
                    if choice != 'y':
                        return self._load_existing_data()
                else:
                    return self._load_existing_data()

            # 2. 显示变更报告
            if interactive:
                print(self.detector.format_change_report(should_collect, conditions, level))

                # 3. 询问用户确认（对于中低级别变更）
                if level in [ChangeLevel.LOW, ChangeLevel.MEDIUM] and not force:
                    choice = input("是否继续数据收集？(y/N): ").strip().lower()
                    if choice != 'y':
                        return self._load_existing_data()

        # 4. 执行数据收集
        return self._perform_collection(force)

    def _perform_collection(self, force: bool = False) -> Dict[str, Any]:
        """执行数据收集"""
        start_time = time.time()

        try:
            if force or not self.data_file.exists():
                print("🔄 执行全量数据收集...")
                return self._full_collect()
            else:
                print("🔄 执行增量数据收集...")
                return self._incremental_collect()

        except Exception as e:
            print(f"❌ 数据收集失败: {e}")
            # 回退到全量收集
            print("🔄 回退到全量数据收集...")
            return self._full_collect()

        finally:
            elapsed_time = time.time() - start_time
            print(f"⏱️ 数据收集耗时: {elapsed_time:.2f} 秒")

    def _load_existing_data(self) -> Optional[Dict[str, Any]]:
        """加载现有数据"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print("✅ 使用现有项目数据")
                return data
            else:
                print("⚠️ 未找到现有数据，执行全量收集")
                return self._full_collect()
        except Exception as e:
            print(f"⚠️ 加载现有数据失败: {e}")
            return self._full_collect()

    def _full_collect(self) -> Dict[str, Any]:
        """全量数据收集"""
        print("📊 开始全量数据收集...")

        collector = ProjectDataCollector(str(self.project_path))
        data = collector.collect_all_data()

        # 添加增量收集元数据
        data["incremental_metadata"] = {
            "collection_type": "full",
            "collection_time": SysmemUtils.get_current_time(),
            "collection_timestamp": time.time(),
            "previous_fingerprint": None
        }

        # 保存数据和指纹
        self._save_data(data)
        self.fingerprinter.save_fingerprint()

        print("✅ 全量数据收集完成")
        return data

    def _incremental_collect(self) -> Dict[str, Any]:
        """增量数据收集"""
        print("🔄 开始增量数据收集...")

        # 加载现有数据
        existing_data = self._load_existing_data()
        if not existing_data:
            print("⚠️ 无法加载现有数据，回退到全量收集")
            return self._full_collect()

        # 分析变更
        changed_modules = self._analyze_changes(existing_data)

        if not changed_modules:
            print("✅ 无模块需要更新，使用现有数据")
            return existing_data

        print(f"🔄 更新 {len(changed_modules)} 个模块...")

        # 增量更新
        updated_data = self._update_changed_modules(existing_data, changed_modules)

        # 添加增量收集元数据
        updated_data["incremental_metadata"] = {
            "collection_type": "incremental",
            "collection_time": SysmemUtils.get_current_time(),
            "collection_timestamp": time.time(),
            "previous_fingerprint": self.fingerprinter._load_fingerprint(),
            "changed_modules": changed_modules
        }

        # 保存数据和指纹
        self._save_data(updated_data)
        self.fingerprinter.save_fingerprint()

        print("✅ 增量数据收集完成")
        return updated_data

    def _analyze_changes(self, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析变更的模块"""
        old_fingerprint = self.fingerprinter._load_fingerprint()
        new_fingerprint = self.fingerprinter.generate_fingerprint()

        changed_modules = {}

        # 检查模块变化
        old_modules = set(existing_data.get('modules', {}).keys())
        new_modules = set(self._discover_modules())

        # 新增模块
        added_modules = new_modules - old_modules
        for module_name in added_modules:
            changed_modules[module_name] = {
                "action": "added",
                "reason": "新模块"
            }

        # 删除模块
        removed_modules = old_modules - new_modules
        for module_name in removed_modules:
            changed_modules[module_name] = {
                "action": "removed",
                "reason": "模块删除"
            }

        # 现有模块的内容变更
        existing_modules = old_modules & new_modules
        for module_name in existing_modules:
            if self._has_module_changed(module_name, old_fingerprint, new_fingerprint):
                changed_modules[module_name] = {
                    "action": "modified",
                    "reason": "内容变更"
                }

        return changed_modules

    def _discover_modules(self) -> List[str]:
        """发现项目中的模块"""
        modules = []

        for item in self.project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if self._is_module_directory(item):
                    modules.append(item.name)

        return modules

    def _is_module_directory(self, path: Path) -> bool:
        """判断是否为模块目录"""
        python_files = list(path.rglob("*.py"))
        js_files = list(path.rglob("*.js"))
        has_readme = any(path.rglob("README*"))

        return len(python_files) > 0 or len(js_files) > 0 or has_readme

    def _has_module_changed(self, module_name: str, old_fp: Dict, new_fp: Dict) -> bool:
        """检查模块是否有变更"""
        # 检查模块下的文件哈希变化
        module_path = self.project_path / module_name

        # 获取模块的文件列表
        module_files = self._get_module_files(module_path)

        old_hashes = old_fp.get('file_hashes', {})
        new_hashes = new_fp.get('file_hashes', {})

        # 检查模块文件变化
        for file_path in module_files:
            relative_path = str(file_path.relative_to(self.project_path))

            if relative_path in old_hashes or relative_path in new_hashes:
                old_hash = old_hashes.get(relative_path)
                new_hash = new_hashes.get(relative_path)

                if old_hash != new_hash:
                    return True

        return False

    def _get_module_files(self, module_path: str) -> List[Path]:
        """获取模块文件列表"""
        module_dir = self.project_path / module_path
        files = []

        for pattern in ["*.py", "*.js", "*.ts", "*.vue", "*.html", "*.css", "*.md", "*.json"]:
            files.extend(module_dir.rglob(pattern))

        return files

    def _update_changed_modules(self, existing_data: Dict[str, Any], changed_modules: Dict[str, Any]) -> Dict[str, Any]:
        """更新变更的模块"""
        updated_data = existing_data.copy()

        # 处理删除的模块
        for module_name in changed_modules:
            if changed_modules[module_name]["action"] == "removed":
                if module_name in updated_data["modules"]:
                    del updated_data["modules"][module_name]
                    print(f"  🗑️ 删除模块: {module_name}")

        # 重新收集数据（简化版本）
        collector = ProjectDataCollector(str(self.project_path))

        # 只收集变更的模块数据
        for module_name, change_info in changed_modules.items():
            if change_info["action"] in ["added", "modified"]:
                print(f"  🔄 更新模块: {module_name} ({change_info['reason']})")

                # 这里可以实现更精确的模块级数据收集
                # 目前使用简化版本，重新收集整个项目数据
                return collector.collect_all_data()

        return updated_data

    def _save_data(self, data: Dict[str, Any]):
        """保存数据文件"""
        SysmemUtils.export_json_data(data, self.data_file)
        print(f"💾 数据已保存: {self.data_file}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """获取收集统计信息"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                metadata = data.get('incremental_metadata', {})
                modules = data.get('modules', {})

                return {
                    "last_collection": metadata.get('collection_time'),
                    "collection_type": metadata.get('collection_type', 'unknown'),
                    "total_modules": len(modules),
                    "changed_modules": len(metadata.get('changed_modules', {})),
                    "data_file_size": self.data_file.stat().st_size if self.data_file.exists() else 0
                }
            else:
                return {"status": "no_data"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='增量数据收集器')
    parser.add_argument('directory', nargs='?', default='.', help='项目目录')
    parser.add_argument('--force', action='store_true', help='强制全量收集')
    parser.add_argument('--non-interactive', action='store_true', help='非交互模式')
    parser.add_argument('--stats', action='store_true', help='显示收集统计')
    parser.add_argument('--check', action='store_true', help='检查变更状态')

    args = parser.parse_args()

    if args.stats:
        collector = IncrementalCollector(args.directory)
        stats = collector.get_collection_stats()
        print("📊 数据收集统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    elif args.check:
        detector = ChangeDetector()
        should_collect, conditions, level = detector.should_collect(args.directory)
        print(detector.format_change_report(should_collect, conditions, level))

    else:
        collector = IncrementalCollector(args.directory)
        data = collector.smart_collect(
            force=args.force,
            interactive=not args.non_interactive
        )

        print(f"\n📋 收集结果:")
        print(f"  模块数量: {len(data.get('modules', {}))}")
        print(f"  CLAUDE.md存在: {'是' if data.get('claude_md_info', {}).get('exists') else '否'}")
        print(f"  架构问题: {len(data.get('architecture_analysis', {}).get('duplicate_files', []))} 个")
        print(f"  数据文件: {collector.data_file}")