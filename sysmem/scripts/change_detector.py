#!/usr/bin/env python3
"""
变更检测器 - 智能检测项目变更并触发数据收集
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from enum import Enum
from fingerprint import ProjectFingerprint
from utils import SysmemUtils

class ChangeLevel(Enum):
    """变更级别"""
    LOW = "LOW"      # 轻微变更，建议用户决定
    MEDIUM = "MEDIUM"  # 中等变更，建议更新
    HIGH = "HIGH"      # 重大变更，必须更新

class TriggerCondition:
    """触发条件基类"""
    def __init__(self, name: str, description: str, level: ChangeLevel):
        self.name = name
        self.description = description
        self.level = level

    def check(self, project_path: str, old_fp: Dict, new_fp: Dict) -> bool:
        """检查是否满足触发条件"""
        raise NotImplementedError

class NewFilesCondition(TriggerCondition):
    """新增文件检测"""
    def __init__(self):
        super().__init__(
            "new_files",
            "检测到新增文件",
            ChangeLevel.MEDIUM
        )

    def check(self, project_path: str, old_fp: Dict, new_fp: Dict) -> bool:
        old_files = set(old_fp.get('file_hashes', {}).keys())
        new_files = set(new_fp.get('file_hashes', {}).keys())

        added_files = new_files - old_files
        if added_files:
            print(f"📁 新增文件: {len(added_files)} 个")
            return True
        return False

class DeletedFilesCondition(TriggerCondition):
    """删除文件检测"""
    def __init__(self):
        super().__init__(
            "deleted_files",
            "检测到删除文件",
            ChangeLevel.MEDIUM
        )

    def check(self, project_path: str, old_fp: Dict, new_fp: Dict) -> bool:
        old_files = set(old_fp.get('file_hashes', {}).keys())
        new_files = set(new_fp.get('file_hashes', {}).keys())

        deleted_files = old_files - new_files
        if deleted_files:
            print(f"🗑️ 删除文件: {len(deleted_files)} 个")
            return True
        return False

class ModifiedFilesCondition(TriggerCondition):
    """修改文件检测"""
    def __init__(self):
        super().__init__(
            "modified_files",
            "检测到文件修改",
            ChangeLevel.MEDIUM
        )

    def check(self, project_path: str, old_fp: Dict, new_fp: Dict) -> bool:
        old_hashes = old_fp.get('file_hashes', {})
        new_hashes = new_fp.get('file_hashes', {})

        modified_count = 0
        for file_path, new_hash in new_hashes.items():
            if file_path in old_hashes and old_hashes[file_path] != new_hash:
                modified_count += 1

        if modified_count > 0:
            print(f"✏️ 修改文件: {modified_count} 个")
            return True
        return False

class ClaudeMdCondition(TriggerCondition):
    """CLAUDE.md文件变更检测"""
    def __init__(self):
        super().__init__(
            "claude_md_changed",
            "CLAUDE.md文件变更",
            ChangeLevel.HIGH
        )

    def check(self, project_path: str, old_fp: Dict, new_fp: Dict) -> bool:
        old_exists = old_fp.get('claude_md_exists', False)
        new_exists = new_fp.get('claude_md_exists', False)

        if old_exists != new_exists:
            print("📄 CLAUDE.md文件状态变更")
            return True

        if old_exists and new_exists:
            old_mtime = old_fp.get('claude_md_mtime', 0)
            new_mtime = new_fp.get('claude_md_mtime', 0)

            if abs(old_mtime - new_mtime) > 1:
                print("📄 CLAUDE.md文件内容变更")
                return True

        return False

class ConfigFilesCondition(TriggerCondition):
    """配置文件变更检测"""
    def __init__(self):
        super().__init__(
            "config_files_changed",
            "配置文件变更",
            ChangeLevel.HIGH
        )

    def check(self, project_path: str, old_fp: Dict, new_fp: Dict) -> bool:
        old_configs = set(old_fp.get('config_files', []))
        new_configs = set(new_fp.get('config_files', []))

        if old_configs != new_configs:
            print("⚙️ 配置文件列表变更")
            return True

        # 检查配置文件修改
        old_hashes = old_fp.get('file_hashes', {})
        new_hashes = new_fp.get('file_hashes', {})

        for config_file in new_configs:
            if config_file in old_hashes and config_file in new_hashes:
                if old_hashes[config_file] != new_hashes[config_file]:
                    print(f"⚙️ 配置文件变更: {config_file}")
                    return True

        return False

class StructureChangeCondition(TriggerCondition):
    """项目结构变更检测"""
    def __init__(self):
        super().__init__(
            "structure_changed",
            "项目结构变更",
            ChangeLevel.HIGH
        )

    def check(self, project_path: str, old_fp: Dict, new_fp: Dict) -> bool:
        old_structure = set(old_fp.get('dir_structure', []))
        new_structure = set(new_fp.get('dir_structure', []))

        if old_structure != new_structure:
            print("🏗️ 项目结构变更")
            return True

        # 检查文件数量大幅变化
        old_count = old_fp.get('total_files', 0)
        new_count = new_fp.get('total_files', 0)

        if abs(old_count - new_count) > 50:
            print(f"📊 文件数量大幅变化: {old_count} -> {new_count}")
            return True

        return False

class PythonFilesCondition(TriggerCondition):
    """Python文件变更检测"""
    def __init__(self):
        super().__init__(
            "python_files_changed",
            "Python文件变更",
            ChangeLevel.MEDIUM
        )

    def check(self, project_path: str, old_fp: Dict, new_fp: Dict) -> bool:
        old_py_files = set(old_fp.get('python_files', []))
        new_py_files = set(new_fp.get('python_files', []))

        if old_py_files != new_py_files:
            print("🐍 Python文件变更")
            return True

        return False

class ChangeDetector:
    """智能变更检测器"""

    def __init__(self):
        self.conditions = [
            ClaudeMdCondition(),
            ConfigFilesCondition(),
            StructureChangeCondition(),
            ModifiedFilesCondition(),
            NewFilesCondition(),
            DeletedFilesCondition(),
            PythonFilesCondition()
        ]

    def should_collect(self, project_path: str) -> Tuple[bool, List[str], ChangeLevel]:
        """判断是否应该触发数据收集"""
        print("🔍 检查项目变更...")

        fingerprinter = ProjectFingerprint(project_path)

        # 如果没有旧指纹，强制收集
        if not fingerprinter.fingerprint_file.exists():
            print("📋 首次扫描，需要收集数据")
            return True, ["first_scan"], ChangeLevel.HIGH

        try:
            old_fingerprint = fingerprinter._load_fingerprint()
            new_fingerprint = fingerprinter.generate_fingerprint()

            triggered_conditions = []
            max_level = ChangeLevel.LOW

            # 检查所有触发条件
            for condition in self.conditions:
                if condition.check(project_path, old_fingerprint, new_fingerprint):
                    triggered_conditions.append(condition.name)
                    if condition.level.value > max_level.value:
                        max_level = condition.level

            if triggered_conditions:
                print(f"🎯 检测到 {len(triggered_conditions)} 个变更条件")
                return True, triggered_conditions, max_level
            else:
                print("✅ 无重大变更")
                return False, [], ChangeLevel.LOW

        except Exception as e:
            print(f"⚠️ 变更检测失败: {e}")
            return True, ["detection_error"], ChangeLevel.HIGH

    def assess_change_level(self, conditions: List[str]) -> ChangeLevel:
        """评估变更级别"""
        max_level = ChangeLevel.LOW

        condition_levels = {
            'claude_md_changed': ChangeLevel.HIGH,
            'config_files_changed': ChangeLevel.HIGH,
            'structure_changed': ChangeLevel.HIGH,
            'modified_files': ChangeLevel.MEDIUM,
            'new_files': ChangeLevel.MEDIUM,
            'deleted_files': ChangeLevel.MEDIUM,
            'python_files_changed': ChangeLevel.MEDIUM,
            'first_scan': ChangeLevel.HIGH,
            'detection_error': ChangeLevel.HIGH
        }

        for condition in conditions:
            level = condition_levels.get(condition, ChangeLevel.LOW)
            if level.value > max_level.value:
                max_level = level

        return max_level

    def get_action_recommendation(self, level: ChangeLevel) -> str:
        """获取行动建议"""
        recommendations = {
            ChangeLevel.LOW: "建议暂时跳过数据收集",
            ChangeLevel.MEDIUM: "建议进行增量数据收集",
            ChangeLevel.HIGH: "强烈建议进行数据收集"
        }
        return recommendations.get(level, "需要进一步评估")

    def format_change_report(self, should_collect: bool, conditions: List[str], level: ChangeLevel) -> str:
        """格式化变更报告"""
        if not should_collect:
            return "✅ 项目状态稳定，无需数据收集"

        report = [
            "🔍 变更检测报告",
            "=" * 30,
            f"变更级别: {level.value}",
            f"触发条件: {', '.join(conditions)}",
            f"建议行动: {self.get_action_recommendation(level)}",
            ""
        ]

        if level == ChangeLevel.HIGH:
            report.extend([
                "⚠️ 检测到重大变更，建议立即进行数据收集",
                "可能影响的方面：",
                "• 项目架构定义",
                "• 模块功能边界",
                "• 依赖关系",
                ""
            ])
        elif level == ChangeLevel.MEDIUM:
            report.extend([
                "📊 检测到中等变更，建议进行增量数据收集",
                "可能影响的方面：",
                "• 文件功能定义",
                "• 代码结构",
                ""
            ])
        else:
            report.extend([
                "💡 检测到轻微变更，可以根据需要决定是否收集",
                ""
            ])

        return "\n".join(report)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."

    detector = ChangeDetector()
    should_collect, conditions, level = detector.should_collect(project_path)

    print("\n" + "=" * 50)
    print(detector.format_change_report(should_collect, conditions, level))
    print("=" * 50)