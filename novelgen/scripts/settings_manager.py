#!/usr/bin/env python3
"""
设置管理器 - 统一的设定修改和管理接口
提供所有设定的修改、更新、验证功能
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# 导入各个数据管理器
from data_managers.worldbuilder import WorldBuilder
from data_managers.character_manager import CharacterManager
from data_managers.environment_manager import EnvironmentManager
from data_managers.plot_manager import PlotManager
from data_managers.style_manager import StyleManager
from data_managers.memory_manager import MemoryManager

class SettingsManager:
    """统一设置管理器，提供所有设定的CRUD操作"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)

        # 初始化各个管理器
        self.world_builder = WorldBuilder(project_path)
        self.character_manager = CharacterManager(project_path)
        self.environment_manager = EnvironmentManager(project_path)
        self.plot_manager = PlotManager(project_path)
        self.style_manager = StyleManager(project_path)
        self.memory_manager = MemoryManager(project_path)

        # 设置操作日志
        self.operations_log_file = self.project_path / "system" / "settings_operations.log"

    def modify_setting(self, category: str, action: str, target: str = None,
                      data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """统一的设定修改接口"""
        try:
            # 记录操作
            self._log_operation(category, action, target, data)

            # 根据类别调用相应的管理器
            if category == "worldview":
                return self._modify_worldview(action, data)
            elif category == "character":
                return self._modify_character(action, target, data, **kwargs)
            elif category == "environment":
                return self._modify_environment(action, target, data, **kwargs)
            elif category == "plot":
                return self._modify_plot(action, target, data, **kwargs)
            elif category == "style":
                return self._modify_style(action, target, data, **kwargs)
            elif category == "memory":
                return self._modify_memory(action, target, data, **kwargs)
            else:
                return {
                    "status": "error",
                    "message": f"未知的设定类别: {category}"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"修改设定失败: {e}"
            }

    def get_setting_status(self, category: str = None, target: str = None) -> Dict[str, Any]:
        """获取设定状态"""
        try:
            if category == "worldview":
                return self.world_builder.validate_worldview()
            elif category == "character":
                if target:
                    return self.character_manager.load_character(target)
                else:
                    return self.character_manager.list_characters()
            elif category == "environment":
                locations = self.environment_manager.get_locations()
                scenes = self.environment_manager.get_scene_templates()
                return {
                    "status": "success",
                    "locations": locations.get("locations", []),
                    "scenes": scenes.get("scenes", [])
                }
            elif category == "plot":
                return self.plot_manager.get_plot_structure()
            elif category == "style":
                return self.style_manager.get_writing_style_guide()
            elif category == "memory":
                if target:
                    return self.memory_manager.get_character_memories(target)
                else:
                    return {"status": "success", "message": "记忆系统需要指定角色"}
            else:
                # 获取所有设定的状态
                return self._get_all_settings_status()

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取设定状态失败: {e}"
            }

    def validate_settings_consistency(self) -> Dict[str, Any]:
        """验证所有设定的一致性"""
        try:
            issues = []
            warnings = []

            # 验证世界观一致性
            worldview_validation = self.world_builder.validate_worldview()
            if worldview_validation.get("status") == "error":
                issues.extend(worldview_validation.get("issues", []))

            # 验证情节一致性
            plot_consistency = self.plot_manager.check_plot_consistency()
            if plot_consistency.get("status") == "error":
                issues.extend(plot_consistency.get("issues", []))
            elif not plot_consistency.get("is_consistent", True):
                warnings.extend(plot_consistency.get("warnings", []))

            # 验证角色关系一致性
            character_consistency = self._validate_character_consistency()
            issues.extend(character_consistency["issues"])
            warnings.extend(character_consistency["warnings"])

            return {
                "status": "success",
                "is_consistent": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "total_issues": len(issues),
                "total_warnings": len(warnings)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"验证设定一致性失败: {e}"
            }

    def backup_settings(self, backup_name: str = None) -> Dict[str, Any]:
        """备份所有设定"""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            backup_dir = self.project_path / "settings" / "backups" / backup_name
            backup_dir.mkdir(parents=True, exist_ok=True)

            # 备份各个设定目录
            import shutil

            settings_dirs = ["worldview", "characters", "environments", "plot", "writing_style", "memory"]
            for dir_name in settings_dirs:
                src_dir = self.project_path / "settings" / dir_name
                if src_dir.exists():
                    dst_dir = backup_dir / dir_name
                    shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

            return {
                "status": "success",
                "backup_name": backup_name,
                "backup_path": str(backup_dir),
                "message": f"设定备份成功: {backup_name}"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"备份设定失败: {e}"
            }

    def restore_settings(self, backup_name: str) -> Dict[str, Any]:
        """恢复设定备份"""
        try:
            backup_dir = self.project_path / "settings" / "backups" / backup_name

            if not backup_dir.exists():
                return {
                    "status": "error",
                    "message": f"备份不存在: {backup_name}"
                }

            # 创建当前备份
            current_backup = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_result = self.backup_settings(current_backup)

            if backup_result["status"] != "success":
                return backup_result

            # 恢复备份
            import shutil
            settings_dir = self.project_path / "settings"

            # 删除现有设定（除了备份目录）
            for item in settings_dir.iterdir():
                if item.is_dir() and item.name != "backups":
                    shutil.rmtree(item)

            # 复制备份内容
            for item in backup_dir.iterdir():
                if item.is_dir():
                    dst_dir = settings_dir / item.name
                    shutil.copytree(item, dst_dir)

            return {
                "status": "success",
                "message": f"成功恢复备份: {backup_name}",
                "previous_backup": current_backup
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"恢复备份失败: {e}"
            }

    def _modify_worldview(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """修改世界观设定"""
        if action == "update":
            return self.world_builder.update_worldview(data)
        else:
            return {
                "status": "error",
                "message": f"不支持的世界观操作: {action}"
            }

    def _modify_character(self, action: str, target: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """修改角色设定"""
        if action == "update":
            return self.character_manager.update_character(target, data)
        elif action == "add_relationship":
            character2 = kwargs.get("character2")
            relationship_type = kwargs.get("relationship_type")
            description = kwargs.get("description", "")
            if not character2 or not relationship_type:
                return {
                    "status": "error",
                    "message": "添加关系需要指定character2和relationship_type参数"
                }
            return self.character_manager.add_relationship(target, character2, relationship_type, description)
        elif action == "add_memory":
            return self.character_manager.add_character_memory(target, data)
        elif action == "delete":
            confirm = kwargs.get("confirm", False)
            return self.character_manager.delete_character(target, confirm)
        else:
            return {
                "status": "error",
                "message": f"不支持的角色操作: {action}"
            }

    def _modify_environment(self, action: str, target: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """修改环境设定"""
        if action == "add_location":
            return self.environment_manager.add_location(data)
        elif action == "add_scene":
            return self.environment_manager.add_scene_template(data)
        elif action == "update_atmosphere":
            # 更新氛围设定
            updates = kwargs.get("updates", {})
            return self.environment_manager.update_style_component("atmosphere", updates)
        else:
            return {
                "status": "error",
                "message": f"不支持的环境操作: {action}"
            }

    def _modify_plot(self, action: str, target: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """修改情节设定"""
        if action == "add_point":
            plot_type = kwargs.get("plot_type", "main")
            return self.plot_manager.add_plot_point(data, plot_type)
        elif action == "add_event":
            return self.plot_manager.add_timeline_event(data)
        elif action == "update_structure":
            # 更新故事结构
            updates = kwargs.get("updates", {})
            return self.plot_manager.update_style_component("structure", updates)
        else:
            return {
                "status": "error",
                "message": f"不支持的情节操作: {action}"
            }

    def _modify_style(self, action: str, target: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """修改写作风格设定"""
        if action == "update_component":
            component = kwargs.get("component", target)
            return self.style_manager.update_style_component(component, data)
        elif action == "add_vocabulary":
            category = kwargs.get("category")
            words = kwargs.get("words", [])
            return self.style_manager.add_vocabulary_category(category, words)
        else:
            return {
                "status": "error",
                "message": f"不支持的写作风格操作: {action}"
            }

    def _modify_memory(self, action: str, target: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """修改记忆设定"""
        if action == "add_memory":
            return self.memory_manager.add_character_memory(target, data)
        elif action == "compress":
            compression_level = kwargs.get("compression_level", "medium")
            return self.memory_manager.compress_memories(target, compression_level)
        elif action == "update_weight":
            memory_id = kwargs.get("memory_id")
            new_weight = kwargs.get("new_weight")
            return self.memory_manager.update_memory_emotional_weight(target, memory_id, new_weight)
        else:
            return {
                "status": "error",
                "message": f"不支持的记忆操作: {action}"
            }

    def _get_all_settings_status(self) -> Dict[str, Any]:
        """获取所有设定的状态"""
        status = {
            "worldview": self.world_builder.validate_worldview(),
            "characters": self.character_manager.list_characters(),
            "environments": self.environment_manager.get_locations(),
            "plot": self.plot_manager.get_plot_structure(),
            "style": self.style_manager.get_writing_style_guide(),
            "memory": {"status": "success", "message": "记忆系统正常"}
        }

        # 统计完成度
        completed_sections = 0
        total_sections = 6

        for key, value in status.items():
            if value.get("status") == "success":
                if key == "characters" and value.get("total", 0) > 0:
                    completed_sections += 1
                elif key != "characters":
                    completed_sections += 1

        status["overall_progress"] = completed_sections / total_sections
        status["completed_sections"] = completed_sections
        status["total_sections"] = total_sections

        return {
            "status": "success",
            "settings_status": status
        }

    def _validate_character_consistency(self) -> Dict[str, Any]:
        """验证角色一致性"""
        issues = []
        warnings = []

        # 获取所有角色
        characters_result = self.character_manager.list_characters()
        if characters_result.get("status") != "success":
            return {"issues": ["无法获取角色列表"], "warnings": []}

        characters = characters_result.get("characters", [])

        # 检查角色关系的一致性
        for char in characters:
            relationships = self.character_manager.get_character_relationships(char["name"])
            if relationships.get("status") == "success":
                rels = relationships.get("relationships", [])
                # 检查是否存在矛盾的关系描述
                relationship_types = [rel.get("type", "") for rel in rels]
                if len(relationship_types) != len(set(relationship_types)):
                    warnings.append(f"角色 {char['name']} 可能存在重复的关系类型")

        return {"issues": issues, "warnings": warnings}

    def _log_operation(self, category: str, action: str, target: str, data: Dict[str, Any]):
        """记录操作日志"""
        try:
            log_file = self.project_path / "system" / "settings_operations.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "category": category,
                "action": action,
                "target": target,
                "data_keys": list(data.keys()) if data else [],
                "operation": f"{category}.{action}" + (f".{target}" if target else "")
            }

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

        except Exception:
            pass  # 日志记录失败不影响主流程

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="统一设置管理器")
    parser.add_argument("--category", required=True,
                       choices=["worldview", "character", "environment", "plot", "style", "memory"],
                       help="设定类别")
    parser.add_argument("--action", required=True,
                       help="操作类型 (update, add, delete等)")
    parser.add_argument("--target", help="操作目标 (角色名称、地点名称等)")
    parser.add_argument("--project-path", default=".", help="项目路径")

    # 角色操作参数
    parser.add_argument("--character2", help="第二个角色 (用于关系操作)")
    parser.add_argument("--relationship-type", help="关系类型")
    parser.add_argument("--description", help="描述信息")

    # 其他操作参数
    parser.add_argument("--component", help="组件名称")
    parser.add_argument("--plot-type", choices=["main", "supporting"], help="情节类型")
    parser.add_argument("--compression-level", choices=["light", "medium", "heavy"], help="压缩级别")
    parser.add_argument("--memory-id", help="记忆ID")
    parser.add_argument("--new-weight", type=int, help="新的情感权重")
    parser.add_argument("--confirm", action="store_true", help="确认删除操作")

    # 数据参数 (JSON格式)
    parser.add_argument("--data", help="操作数据 (JSON格式)")

    args = parser.parse_args()

    # 解析数据
    data = {}
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            print("错误: data参数必须是有效的JSON格式")
            return

    sm = SettingsManager(args.project_path)

    # 构建操作参数
    kwargs = {}
    if args.character2:
        kwargs["character2"] = args.character2
    if args.relationship_type:
        kwargs["relationship_type"] = args.relationship_type
    if args.description:
        kwargs["description"] = args.description
    if args.component:
        kwargs["component"] = args.component
    if args.plot_type:
        kwargs["plot_type"] = args.plot_type
    if args.compression_level:
        kwargs["compression_level"] = args.compression_level
    if args.memory_id:
        kwargs["memory_id"] = args.memory_id
    if args.new_weight:
        kwargs["new_weight"] = args.new_weight
    if args.confirm:
        kwargs["confirm"] = args.confirm

    result = sm.modify_setting(args.category, args.action, args.target, data, **kwargs)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()