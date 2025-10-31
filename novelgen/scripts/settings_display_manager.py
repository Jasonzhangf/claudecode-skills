#!/usr/bin/env python3
"""
设定显示管理器
负责显示各种类型的设定内容
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from data_managers.worldbuilder import WorldBuilder
from data_managers.character_manager import CharacterManager
from data_managers.environment_manager import EnvironmentManager
from data_managers.plot_manager import PlotManager
from data_managers.style_manager import StyleManager
from data_managers.memory_manager import MemoryManager

class SettingsDisplayManager:
    """设定显示管理器，提供统一的设定显示接口"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)

        # 初始化各个管理器
        self.world_builder = WorldBuilder(project_path)
        self.character_manager = CharacterManager(project_path)
        self.environment_manager = EnvironmentManager(project_path)
        self.plot_manager = PlotManager(project_path)
        self.style_manager = StyleManager(project_path)
        self.memory_manager = MemoryManager(project_path)

    def display_setting(self, setting_type: str, setting_name: str = None,
                       format_type: str = "readable") -> Dict[str, Any]:
        """
        显示设定内容

        Args:
            setting_type: 设定类型 ("worldview", "character", "environment", "plot", "style", "memory")
            setting_name: 具体设定名称（如角色名、记忆ID等）
            format_type: 显示格式 ("readable", "json", "summary")
        """
        try:
            if setting_type == "worldview":
                return self._display_worldview(format_type)
            elif setting_type == "character":
                if not setting_name:
                    return self._display_all_characters(format_type)
                return self._display_character(setting_name, format_type)
            elif setting_type == "environment":
                return self._display_environment(format_type)
            elif setting_type == "plot":
                return self._display_plot(format_type)
            elif setting_type == "style":
                return self._display_style(format_type)
            elif setting_type == "memory":
                if not setting_name:
                    return {"status": "error", "message": "显示记忆需要指定角色名或记忆ID"}
                return self._display_memory(setting_name, format_type)
            else:
                return {
                    "status": "error",
                    "message": f"不支持的设定类型: {setting_type}"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"显示设定失败: {e}"
            }

    def _display_worldview(self, format_type: str) -> Dict[str, Any]:
        """显示世界观设定"""
        result = self.world_builder.load_worldview()
        if result["status"] != "success":
            return result

        if format_type == "json":
            return {
                "status": "success",
                "setting_type": "worldview",
                "format": "json",
                "data": result
            }

        elif format_type == "summary":
            # 生成世界观摘要（需要AI能力）
            return {
                "status": "ai_task_required",
                "task_type": "generate_summary",
                "content": result["setting_content"],
                "setting_type": "worldview"
            }

        else:  # readable
            return {
                "status": "success",
                "setting_type": "worldview",
                "format": "readable",
                "content": result["setting_content"],
                "rules_content": result.get("rules_content", ""),
                "display_title": "世界观设定"
            }

    def _display_character(self, character_name: str, format_type: str) -> Dict[str, Any]:
        """显示特定角色设定"""
        result = self.character_manager.load_character(character_name)
        if result["status"] != "success":
            return result

        # 获取角色关系
        relations_result = self.character_manager.get_character_relationships(character_name)

        if format_type == "json":
            return {
                "status": "success",
                "setting_type": "character",
                "character_name": character_name,
                "format": "json",
                "data": result,
                "relationships": relations_result.get("relationships", [])
            }

        elif format_type == "summary":
            # 生成角色摘要（需要AI能力）
            return {
                "status": "ai_task_required",
                "task_type": "generate_character_summary",
                "character_name": character_name,
                "content": result["content"],
                "relationships": relations_result.get("relationships", [])
            }

        else:  # readable
            display_content = self._format_character_display(
                result["content"],
                relations_result.get("relationships", [])
            )

            return {
                "status": "success",
                "setting_type": "character",
                "character_name": character_name,
                "format": "readable",
                "content": display_content,
                "display_title": f"角色设定：{character_name}"
            }

    def _display_all_characters(self, format_type: str) -> Dict[str, Any]:
        """显示所有角色列表"""
        result = self.character_manager.list_characters()
        if result["status"] != "success":
            return result

        if format_type == "json":
            return {
                "status": "success",
                "setting_type": "character_list",
                "format": "json",
                "data": result
            }

        else:  # readable or summary
            character_list = []
            for char in result["characters"]:
                character_list.append({
                    "name": char["name"],
                    "type": char["type"],
                    "created_at": char.get("created_at", ""),
                    "file_path": char["file_path"]
                })

            return {
                "status": "success",
                "setting_type": "character_list",
                "format": format_type,
                "characters": character_list,
                "total_count": result["total"],
                "display_title": "角色列表"
            }

    def _display_memory(self, identifier: str, format_type: str) -> Dict[str, Any]:
        """显示记忆内容"""
        # 判断是角色名还是记忆ID
        if len(identifier) == 8 and identifier.isalnum():
            # 按记忆ID查找
            return self._display_memory_by_id(identifier, format_type)
        else:
            # 按角色名查找
            return self._display_character_memories(identifier, format_type)

    def _display_memory_by_id(self, memory_id: str, format_type: str) -> Dict[str, Any]:
        """按记忆ID显示记忆"""
        # 在所有角色的记忆中搜索指定ID
        # 这里简化处理，实际应该在memory_manager中实现
        return {
            "status": "ai_task_required",
            "task_type": "find_memory_by_id",
            "memory_id": memory_id,
            "format": format_type
        }

    def _display_character_memories(self, character_name: str, format_type: str) -> Dict[str, Any]:
        """显示角色所有记忆"""
        result = self.memory_manager.get_character_memories(character_name)
        if result["status"] != "success":
            return result

        if format_type == "json":
            return {
                "status": "success",
                "setting_type": "memory",
                "character_name": character_name,
                "format": "json",
                "data": result
            }

        elif format_type == "summary":
            # 生成记忆摘要（需要AI能力）
            return {
                "status": "ai_task_required",
                "task_type": "generate_memory_summary",
                "character_name": character_name,
                "memories": result["memories"],
                "format": format_type
            }

        else:  # readable
            display_content = self._format_memory_display(result["memories"])

            return {
                "status": "success",
                "setting_type": "memory",
                "character_name": character_name,
                "format": "readable",
                "content": display_content,
                "total_count": result["total_count"],
                "memory_types": result["memory_types"],
                "display_title": f"角色记忆：{character_name}"
            }

    def _format_character_display(self, content: str, relationships: List[Dict]) -> str:
        """格式化角色显示内容"""
        display_content = content

        if relationships:
            display_content += "\n\n## 角色关系\n\n"
            for rel in relationships:
                display_content += f"### {rel['title']}\n"
                display_content += f"**关系类型**: {rel['type']}\n"
                if rel['description']:
                    display_content += f"**描述**: {rel['description']}\n"
                display_content += "\n"

        return display_content

    def _format_memory_display(self, memories: List[Dict]) -> str:
        """格式化记忆显示内容"""
        if not memories:
            return "暂无记忆记录。"

        content_lines = []

        # 按记忆类型分组
        memories_by_type = {}
        for memory in memories:
            memory_type = memory.get("memory_type", "未知类型")
            if memory_type not in memories_by_type:
                memories_by_type[memory_type] = []
            memories_by_type[memory_type].append(memory)

        for memory_type, type_memories in memories_by_type.items():
            content_lines.append(f"## {memory_type} ({len(type_memories)}条)\n")

            for memory in type_memories:
                content_lines.append(f"### {memory.get('title', '无标题')}")
                content_lines.append(f"**记忆ID**: {memory.get('memory_id', '未知')}")
                content_lines.append(f"**情感权重**: {memory.get('emotional_weight', 0)}/10")
                content_lines.append(f"**发生时间**: {memory.get('occurrence_time', '未知')}")
                content_lines.append(f"**记忆内容**: {memory.get('content', '无内容')}")
                if memory.get('emotional_context'):
                    content_lines.append(f"**情感背景**: {memory['emotional_context']}")
                content_lines.append("")

        return "\n".join(content_lines)

    def get_available_settings(self) -> Dict[str, Any]:
        """获取可用的设定列表"""
        try:
            available_settings = {}

            # 检查世界观
            worldview_result = self.world_builder.load_worldview()
            available_settings["worldview"] = worldview_result["status"] == "success"

            # 检查角色
            characters_result = self.character_manager.list_characters()
            available_settings["characters"] = {
                "available": characters_result["status"] == "success",
                "count": characters_result.get("total", 0) if characters_result["status"] == "success" else 0,
                "list": [char["name"] for char in characters_result.get("characters", [])] if characters_result["status"] == "success" else []
            }

            # 检查记忆
            # 这里简化处理，实际应该检查哪些角色有记忆记录

            return {
                "status": "success",
                "available_settings": available_settings,
                "project_path": str(self.project_path)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取可用设定失败: {e}"
            }

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="设定显示管理器")
    parser.add_argument("--action", choices=["show", "list"], default="show", help="操作类型")
    parser.add_argument("--type", choices=["worldview", "character", "environment", "plot", "style", "memory"],
                       required=True, help="设定类型")
    parser.add_argument("--name", help="设定名称（如角色名、记忆ID等）")
    parser.add_argument("--format", choices=["readable", "json", "summary"], default="readable", help="显示格式")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    sdm = SettingsDisplayManager(args.project_path)

    if args.action == "show":
        result = sdm.display_setting(args.type, args.name, args.format)
    elif args.action == "list":
        result = sdm.get_available_settings()
    else:
        result = {"status": "error", "message": f"未知操作: {args.action}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()