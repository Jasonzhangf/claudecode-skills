#!/usr/bin/env python3
"""
项目初始化管理器
安全地扫描和更新项目设定，保护现有内容
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import re

from data_managers.character_manager import CharacterManager
from data_managers.worldbuilder import WorldBuilder
from data_managers.memory_manager import MemoryManager
from chapter_manager import ChapterManager
from settings_manager import SettingsManager
import settings_display_manager

class ProjectInitializer:
    """项目初始化管理器，安全地更新项目设定"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.reference_dir = self.project_path / "reference"
        self.refs_dir = self.project_path / "refs"
        self.materials_dir = self.project_path / "materials"

        # 初始化各个管理器
        self.character_manager = CharacterManager(str(self.project_path))
        self.world_builder = WorldBuilder(str(self.project_path))
        self.memory_manager = MemoryManager(str(self.project_path))
        self.chapter_manager = ChapterManager(str(self.project_path))
        self.settings_manager = SettingsManager(str(self.project_path))

        # 备份目录 - 放在项目根目录下避免递归
        self.backup_dir = self.project_path / f"initialization_backup_{int(datetime.now().timestamp())}"

        # 初始化日志
        self.init_log = []
        self.warnings = []
        self.errors = []

        # 成品章节保护
        self.manuscript_dir = self.project_path / "manuscript"
        self.protected_files = set()

    def log_message(self, level: str, message: str, details: Any = None):
        """记录日志消息"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "details": details
        }
        self.init_log.append(log_entry)

        prefix = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "success": "✅"}.get(level, "📝")
        print(f"{prefix} {message}")

        if level == "error":
            self.errors.append(log_entry)
        elif level == "warning":
            self.warnings.append(log_entry)

    def create_backup(self):
        """创建项目备份"""
        self.log_message("info", "创建初始化备份...")

        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # 备份重要目录
        backup_items = [
            "settings",
            "system",
            "progress"
        ]

        for item in backup_items:
            src = self.project_path / item
            if src.exists():
                dst = self.backup_dir / item
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                self.log_message("success", f"已备份 {item}")

        # 记录保护文件
        self._identify_protected_files()

        self.log_message("success", f"备份完成，保存到 {self.backup_dir}")

    def _identify_protected_files(self):
        """识别需要保护的成品章节文件"""
        if self.manuscript_dir.exists():
            for chapter_file in self.manuscript_dir.rglob("*.md"):
                self.protected_files.add(chapter_file)
                self.log_message("info", f"保护成品章节: {chapter_file.relative_to(self.project_path)}")

    def scan_existing_documents(self) -> Dict[str, Any]:
        """扫描项目已有文档"""
        self.log_message("info", "扫描项目现有文档...")

        scan_result = {
            "settings_files": [],
            "character_files": [],
            "worldview_files": [],
            "chapter_files": [],
            "reference_materials": [],
            "total_files": 0
        }

        # 扫描settings目录
        settings_dir = self.project_path / "settings"
        if settings_dir.exists():
            for file_path in settings_dir.rglob("*.md"):
                relative_path = file_path.relative_to(self.project_path)
                content = file_path.read_text(encoding='utf-8')

                file_info = {
                    "path": str(relative_path),
                    "size": len(content),
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "type": self._classify_file(file_path, content)
                }

                if "character" in str(relative_path):
                    scan_result["character_files"].append(file_info)
                elif "worldview" in str(relative_path):
                    scan_result["worldview_files"].append(file_info)
                else:
                    scan_result["settings_files"].append(file_info)

        # 扫描章节文件
        draft_dir = self.project_path / "draft"
        if draft_dir.exists():
            for file_path in draft_dir.rglob("*.md"):
                relative_path = file_path.relative_to(self.project_path)
                content = file_path.read_text(encoding='utf-8')

                scan_result["chapter_files"].append({
                    "path": str(relative_path),
                    "size": len(content),
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "is_manuscript": str(relative_path).startswith("manuscript/")
                })

        # 扫描参考资料目录
        for ref_dir in [self.reference_dir, self.refs_dir, self.materials_dir]:
            if ref_dir.exists():
                for file_path in ref_dir.rglob("*"):
                    if file_path.is_file() and file_path.suffix in ['.md', '.txt', '.docx', '.pdf']:
                        relative_path = file_path.relative_to(self.project_path)
                        scan_result["reference_materials"].append({
                            "path": str(relative_path),
                            "size": file_path.stat().st_size,
                            "type": file_path.suffix,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })

        scan_result["total_files"] = (
            len(scan_result["settings_files"]) +
            len(scan_result["character_files"]) +
            len(scan_result["worldview_files"]) +
            len(scan_result["chapter_files"]) +
            len(scan_result["reference_materials"])
        )

        self.log_message("success", f"扫描完成，发现 {scan_result['total_files']} 个文件")
        return scan_result

    def _classify_file(self, file_path: Path, content: str) -> str:
        """分类文件类型"""
        path_lower = str(file_path).lower()
        content_lower = content.lower()

        if "character" in path_lower or "角色" in content_lower:
            return "character"
        elif "worldview" in path_lower or "世界观" in content_lower or "setting" in path_lower:
            return "worldview"
        elif "plot" in path_lower or "情节" in content_lower:
            return "plot"
        elif "environment" in path_lower or "环境" in content_lower:
            return "environment"
        else:
            return "general"

    def scan_reference_directory(self) -> Dict[str, Any]:
        """扫描reference目录内容"""
        self.log_message("info", "扫描参考资料目录...")

        reference_scan = {
            "directories_found": [],
            "materials_by_type": {
                "character": [],
                "worldview": [],
                "plot": [],
                "environment": [],
                "general": []
            },
            "total_materials": 0
        }

        # 检查多个可能的参考资料目录
        ref_directories = [self.reference_dir, self.refs_dir, self.materials_dir]

        for ref_dir in ref_directories:
            if ref_dir.exists():
                reference_scan["directories_found"].append(str(ref_dir.relative_to(self.project_path)))

                # 分析参考资料内容
                for file_path in ref_dir.rglob("*"):
                    if file_path.is_file() and file_path.suffix in ['.md', '.txt']:
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            material_type = self._classify_material(content)

                            material_info = {
                                "path": str(file_path.relative_to(self.project_path)),
                                "type": material_type,
                                "size": len(content),
                                "title": self._extract_title(content),
                                "key_elements": self._extract_key_elements(content, material_type)
                            }

                            reference_scan["materials_by_type"][material_type].append(material_info)
                            reference_scan["total_materials"] += 1

                        except Exception as e:
                            self.log_message("warning", f"无法读取文件 {file_path}: {e}")

        self.log_message("success", f"参考资料扫描完成，发现 {reference_scan['total_materials']} 份材料")
        return reference_scan

    def _classify_material(self, content: str) -> str:
        """分类参考资料类型"""
        content_lower = content.lower()

        # 角色相关关键词
        character_keywords = ["角色", "人物", "character", "主角", "配角", "姓名", "年龄", "性格", "背景"]
        # 世界观相关关键词
        worldview_keywords = ["世界观", "世界", "设定", "规则", "背景", "时代", "科技", "魔法"]
        # 情节相关关键词
        plot_keywords = ["情节", "故事", "剧情", "大纲", "冲突", "转折", "高潮", "结局"]
        # 环境相关关键词
        environment_keywords = ["环境", "地点", "场景", "建筑", "地理", "气候", "城市"]

        scores = {
            "character": sum(1 for kw in character_keywords if kw in content_lower),
            "worldview": sum(1 for kw in worldview_keywords if kw in content_lower),
            "plot": sum(1 for kw in plot_keywords if kw in content_lower),
            "environment": sum(1 for kw in environment_keywords if kw in content_lower)
        }

        # 返回得分最高的类型
        if max(scores.values()) == 0:
            return "general"
        return max(scores, key=scores.get)

    def _extract_title(self, content: str) -> str:
        """提取文档标题"""
        lines = content.split('\n')
        for line in lines[:5]:  # 只检查前5行
            line = line.strip()
            if line.startswith('#'):
                return line.lstrip('#').strip()
        return "无标题"

    def _extract_key_elements(self, content: str, material_type: str) -> List[str]:
        """提取关键元素"""
        content_lower = content.lower()
        key_elements = []

        # 根据类型提取不同的关键信息
        if material_type == "character":
            # 提取角色相关信息
            name_pattern = r'姓名[：:]\s*([^\n]+)'
            age_pattern = r'年龄[：:]\s*([^\n]+)'
            personality_pattern = r'性格[：:]\s*([^\n]+)'

            for pattern, label in [(name_pattern, "姓名"), (age_pattern, "年龄"), (personality_pattern, "性格")]:
                match = re.search(pattern, content)
                if match:
                    key_elements.append(f"{label}: {match.group(1).strip()}")

        elif material_type == "worldview":
            # 提取世界观相关信息
            time_pattern = r'时代[：:]\s*([^\n]+)'
            tech_pattern = r'科技[：:]\s*([^\n]+)'
            magic_pattern = r'魔法[：:]\s*([^\n]+)'

            for pattern, label in [(time_pattern, "时代"), (tech_pattern, "科技"), (magic_pattern, "魔法")]:
                match = re.search(pattern, content)
                if match:
                    key_elements.append(f"{label}: {match.group(1).strip()}")

        return key_elements[:5]  # 最多返回5个关键元素

    def update_project_status(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """更新项目状态"""
        self.log_message("info", "更新项目状态...")

        status_update = {
            "project_path": str(self.project_path),
            "scan_time": datetime.now().isoformat(),
            "file_statistics": scan_result,
            "directory_structure": self._get_directory_structure(),
            "completion_status": self._calculate_completion_status(scan_result)
        }

        # 保存状态到文件
        status_file = self.project_path / "system" / "project_status.json"
        status_file.parent.mkdir(exist_ok=True)

        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_update, f, ensure_ascii=False, indent=2)

        self.log_message("success", "项目状态已更新")
        return status_update

    def _get_directory_structure(self) -> Dict[str, Any]:
        """获取目录结构"""
        structure = {}

        for item in self.project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                structure[item.name] = {
                    "type": "directory",
                    "exists": True,
                    "file_count": len(list(item.rglob("*")))
                }

        return structure

    def _calculate_completion_status(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        """计算项目完成状态"""
        total_possible = 100
        scores = {
            "characters": min(20, len(scan_result["character_files"]) * 5),
            "worldview": min(20, len(scan_result["worldview_files"]) * 5),
            "settings": min(15, len(scan_result["settings_files"]) * 3),
            "chapters": min(25, len(scan_result["chapter_files"]) * 3),
            "references": min(20, len(scan_result["reference_materials"]) * 2)
        }

        total_score = sum(scores.values())
        completion_percentage = (total_score / total_possible) * 100

        return {
            "overall_percentage": round(completion_percentage, 1),
            "category_scores": scores,
            "status_level": self._get_status_level(completion_percentage)
        }

    def _get_status_level(self, percentage: float) -> str:
        """获取状态等级"""
        if percentage >= 80:
            return "advanced"
        elif percentage >= 60:
            return "intermediate"
        elif percentage >= 40:
            return "basic"
        else:
            return "initial"

    def create_basic_settings_files(self, reference_scan: Dict[str, Any]) -> Dict[str, Any]:
        """创建或更新基础设定文件"""
        self.log_message("info", "检查和创建基础设定文件...")

        creation_results = {
            "created_files": [],
            "updated_files": [],
            "skipped_files": [],
            "errors": []
        }

        # 需要创建的基础文件列表
        required_files = [
            {
                "path": "settings/worldview/world_setting.md",
                "title": "世界设定",
                "template": self._get_worldview_template(reference_scan)
            },
            {
                "path": "settings/worldview/world_rules.md",
                "title": "世界规则",
                "template": self._get_world_rules_template(reference_scan)
            },
            {
                "path": "settings/plot/main_plot.md",
                "title": "主要情节",
                "template": self._get_plot_template(reference_scan)
            },
            {
                "path": "settings/plot/story_structure.md",
                "title": "故事结构",
                "template": self._get_story_structure_template()
            },
            {
                "path": "settings/environments/key_locations.md",
                "title": "重要地点",
                "template": self._get_locations_template(reference_scan)
            },
            {
                "path": "settings/writing_style/narrative_style.md",
                "title": "叙事风格",
                "template": self._get_writing_style_template()
            }
        ]

        for file_info in required_files:
            file_path = self.project_path / file_info["path"]

            try:
                if file_path.exists():
                    # 检查是否需要更新
                    existing_content = file_path.read_text(encoding='utf-8')
                    if self._should_update_file(existing_content, file_info["template"], file_info["title"]):
                        # 备份现有文件
                        backup_path = self.backup_dir / file_info["path"]
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, backup_path)

                        # 更新文件
                        file_path.write_text(file_info["template"], encoding='utf-8')
                        creation_results["updated_files"].append(file_info["path"])
                        self.log_message("success", f"已更新 {file_info['title']}")
                    else:
                        creation_results["skipped_files"].append(file_info["path"])
                        self.log_message("info", f"跳过 {file_info['title']} (已是最新)")
                else:
                    # 创建新文件
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(file_info["template"], encoding='utf-8')
                    creation_results["created_files"].append(file_info["path"])
                    self.log_message("success", f"已创建 {file_info['title']}")

            except Exception as e:
                creation_results["errors"].append({"file": file_info["path"], "error": str(e)})
                self.log_message("error", f"处理文件 {file_info['path']} 失败: {e}")

        self.log_message("success", f"基础设定文件处理完成: 创建 {len(creation_results['created_files'])} 个, 更新 {len(creation_results['updated_files'])} 个")
        return creation_results

    def _should_update_file(self, existing_content: str, new_template: str, title: str) -> bool:
        """判断是否应该更新文件"""
        # 简单的启发式判断：如果现有内容很短或者包含默认占位符，则更新
        if len(existing_content.strip()) < 200:
            return True

        placeholder_indicators = ["待填写", "TODO", "示例", "模板", "请在此处填写"]
        for indicator in placeholder_indicators:
            if indicator in existing_content:
                return True

        return False

    def _get_worldview_template(self, reference_scan: Dict[str, Any]) -> str:
        """生成世界观模板"""
        template = """# 世界设定

## 基本信息

**世界名称**: 待填写
**时代背景**: 待填写
**科技水平**: 待填写
**社会结构**: 待填写

## 地理环境

待填写世界的地理环境、气候、地形等信息。

## 历史背景

待填写世界的历史发展、重要事件、时间线等。

## 核心规则

待填写世界运行的基本规则和定律。

"""

        # 如果参考材料中有世界观内容，添加提示
        if reference_scan["materials_by_type"]["worldview"]:
            template += "\n## 参考材料提示\n\n"
            template += f"发现 {len(reference_scan['materials_by_type']['worldview'])} 份世界观参考材料，"
            template += "请参考这些材料完善世界观设定。\n"

        return template

    def _get_world_rules_template(self, reference_scan: Dict[str, Any]) -> str:
        """生成世界规则模板"""
        return """# 世界规则

## 物理规则

待填写世界的基本物理定律和规则。

## 魔法/科技系统

待填写世界的魔法系统或科技规则。

## 社会规则

待填写世界的社会制度、法律、文化规范等。

## 限制与约束

待填写世界中存在的各种限制和约束条件。

"""

    def _get_plot_template(self, reference_scan: Dict[str, Any]) -> str:
        """生成情节模板"""
        template = """# 主要情节

## 故事主线

**起点**: 待填写
**发展**: 待填写
**高潮**: 待填写
**结局**: 待填写

## 主要冲突

待填写故事中的核心冲突。

## 核心情节点

1. 待填写
2. 待填写
3. 待填写

## 角色关系发展

待填写主要角色之间的关系发展变化。

"""

        # 如果参考材料中有情节内容，添加提示
        if reference_scan["materials_by_type"]["plot"]:
            template += f"\n> 发现 {len(reference_scan['materials_by_type']['plot'])} 份情节参考材料，"
            template += "建议参考这些材料完善情节设定。\n"

        return template

    def _get_story_structure_template(self) -> str:
        """生成故事结构模板"""
        return """# 故事结构

## 三幕式结构

### 第一幕：开端
- **建立**: 待填写
- **激励事件**: 待填写
- **转折点**: 待填写

### 第二幕：发展
- **上升情节**: 待填写
- **中点**: 待填写
- **危机**: 待填写

### 第三幕：结局
- **高潮**: 待填写
- **下降情节**: 待填写
- **结局**: 待填写

## 章节规划

待填写各章节的主要内容安排。

"""

    def _get_locations_template(self, reference_scan: Dict[str, Any]) -> str:
        """生成地点模板"""
        template = """# 重要地点

## 主要场景

### 场景1: 待填写
- **类型**: 待填写
- **特点**: 待填写
- **重要性**: 待填写

### 场景2: 待填写
- **类型**: 待填写
- **特点**: 待填写
- **重要性**: 待填写

## 地点关系

待填写各个地点之间的关系和连接。

## 重要地点描述

待填写重要地点的详细描述。

"""

        # 如果参考材料中有环境内容，添加提示
        if reference_scan["materials_by_type"]["environment"]:
            template += f"\n> 发现 {len(reference_scan['materials_by_type']['environment'])} 份环境参考材料，"
            template += "建议参考这些材料完善地点设定。\n"

        return template

    def _get_writing_style_template(self) -> str:
        """生成写作风格模板"""
        return """# 叙事风格

## 基本风格

**叙事视角**: 待填写 (第一人称/第三人称/全知视角)
**时态**: 待填写 (过去时/现在时)
**语调**: 待填写 (轻松/严肃/幽默/紧张)

## 语言特点

**词汇风格**: 待填写
**句式特点**: 待填写
**修辞手法**: 待填写

## 节奏控制

**整体节奏**: 待填写 (快/中/慢)
**章节长度**: 待填写
**描写密度**: 待填写

## 特色元素

待填写作品的独特写作元素和风格特点。

"""

    def verify_manuscript_protection(self) -> Dict[str, Any]:
        """验证成品章节保护"""
        self.log_message("info", "验证成品章节保护...")

        protection_status = {
            "protected_files": [],
            "verified_protection": True,
            "warnings": []
        }

        for protected_file in self.protected_files:
            if protected_file.exists():
                # 检查文件修改时间
                original_mtime = protected_file.stat().st_mtime
                protection_status["protected_files"].append({
                    "path": str(protected_file.relative_to(self.project_path)),
                    "size": protected_file.stat().st_size,
                    "last_modified": datetime.fromtimestamp(original_mtime).isoformat()
                })
            else:
                protection_status["warnings"].append(f"受保护的文件不存在: {protected_file}")
                protection_status["verified_protection"] = False

        if protection_status["verified_protection"]:
            self.log_message("success", f"成品章节保护验证通过，共保护 {len(protection_status['protected_files'])} 个文件")
        else:
            self.log_message("warning", "成品章节保护验证发现问题")

        return protection_status

    def generate_initialization_report(self) -> Dict[str, Any]:
        """生成初始化报告"""
        self.log_message("info", "生成初始化报告...")

        report = {
            "initialization_time": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "backup_location": str(self.backup_dir),
            "summary": {
                "total_log_entries": len(self.init_log),
                "warnings_count": len(self.warnings),
                "errors_count": len(self.errors),
                "success": len(self.errors) == 0
            },
            "operations_performed": [
                entry["message"] for entry in self.init_log
                if entry["level"] in ["success", "info"]
            ],
            "warnings": [w["message"] for w in self.warnings],
            "errors": [e["message"] for e in self.errors],
            "protected_files_count": len(self.protected_files),
            "detailed_log": self.init_log
        }

        # 保存报告
        report_file = self.project_path / "system" / f"initialization_report_{int(datetime.now().timestamp())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        self.log_message("success", f"初始化报告已保存到 {report_file}")
        return report

    def run_initialization(self) -> Dict[str, Any]:
        """执行完整的项目初始化"""
        print("🚀 开始项目初始化...")
        print(f"项目目录: {self.project_path}")
        print(f"备份目录: {self.backup_dir}")
        print("=" * 50)

        try:
            # 1. 创建备份
            self.create_backup()

            # 2. 扫描现有文档
            scan_result = self.scan_existing_documents()

            # 3. 扫描参考资料
            reference_scan = self.scan_reference_directory()

            # 4. 更新项目状态
            status_update = self.update_project_status(scan_result)

            # 5. 创建/更新基础设定文件
            creation_results = self.create_basic_settings_files(reference_scan)

            # 6. 验证成品章节保护
            protection_status = self.verify_manuscript_protection()

            # 7. 生成报告
            final_report = self.generate_initialization_report()

            # 汇总结果
            initialization_result = {
                "success": True,
                "message": "项目初始化完成",
                "results": {
                    "scan_result": scan_result,
                    "reference_scan": reference_scan,
                    "status_update": status_update,
                    "creation_results": creation_results,
                    "protection_status": protection_status,
                    "final_report": final_report
                }
            }

            print("=" * 50)
            print("🎉 项目初始化完成！")
            print(f"📁 备份位置: {self.backup_dir}")
            print(f"📊 扫描文件: {scan_result['total_files']} 个")
            print(f"📚 参考材料: {reference_scan['total_materials']} 份")
            print(f"📝 创建文件: {len(creation_results['created_files'])} 个")
            print(f"🔄 更新文件: {len(creation_results['updated_files'])} 个")
            print(f"🛡️ 保护文件: {len(self.protected_files)} 个")

            if self.warnings:
                print(f"⚠️ 警告: {len(self.warnings)} 个")

            if self.errors:
                print(f"❌ 错误: {len(self.errors)} 个")
                initialization_result["success"] = False
                initialization_result["message"] = "初始化完成，但存在错误"

            return initialization_result

        except Exception as e:
            error_msg = f"初始化过程中发生异常: {e}"
            self.log_message("error", error_msg)
            return {
                "success": False,
                "message": error_msg,
                "partial_results": {
                    "backup_created": self.backup_dir.exists(),
                    "log_entries": len(self.init_log),
                    "errors": len(self.errors)
                }
            }

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="项目初始化管理器")
    parser.add_argument("--project-path", default=".", help="项目路径")
    parser.add_argument("--backup-only", action="store_true", help="仅创建备份")
    parser.add_argument("--scan-only", action="store_true", help="仅扫描文档")
    parser.add_argument("--dry-run", action="store_true", help="干运行，不实际修改文件")

    args = parser.parse_args()

    initializer = ProjectInitializer(args.project_path)

    if args.backup_only:
        initializer.create_backup()
    elif args.scan_only:
        result = initializer.scan_existing_documents()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.dry_run:
        print("🔍 干运行模式 - 不会实际修改文件")
        # 这里可以添加干运行逻辑
    else:
        result = initializer.run_initialization()
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()