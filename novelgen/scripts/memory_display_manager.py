#!/usr/bin/env python3
"""
记忆显示管理器
专门处理记忆相关的显示功能
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from data_managers.memory_manager import MemoryManager

class MemoryDisplayManager:
    """记忆显示管理器，提供记忆相关的显示接口"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.memory_manager = MemoryManager(project_path)

    def display_memory_segment(self, memory_identifier: str,
                             segment_type: str = "single",
                             display_format: str = "readable") -> Dict[str, Any]:
        """
        显示记忆片段

        Args:
            memory_identifier: 记忆标识符（角色名、记忆ID、或关键词）
            segment_type: 显示类型 ("single", "character_all", "by_type", "timeline", "connections")
            display_format: 显示格式 ("readable", "json", "summary", "timeline")
        """
        try:
            if segment_type == "single":
                return self._display_single_memory(memory_identifier, display_format)
            elif segment_type == "character_all":
                return self._display_character_all_memories(memory_identifier, display_format)
            elif segment_type == "by_type":
                return self._display_memories_by_type(memory_identifier, display_format)
            elif segment_type == "timeline":
                return self._display_memory_timeline(memory_identifier, display_format)
            elif segment_type == "connections":
                return self._display_memory_connections(memory_identifier, display_format)
            else:
                return {
                    "status": "error",
                    "message": f"不支持的显示类型: {segment_type}"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"显示记忆失败: {e}"
            }

    def _display_single_memory(self, memory_id: str, display_format: str) -> Dict[str, Any]:
        """显示单条记忆"""
        # 在所有角色记忆中搜索指定ID的记忆
        all_characters_result = self._get_all_characters_with_memories()

        if all_characters_result["status"] != "success":
            return all_characters_result

        target_memory = None
        target_character = None

        for character_name in all_characters_result["characters"]:
            memories_result = self.memory_manager.get_character_memories(character_name)
            if memories_result["status"] == "success":
                for memory in memories_result["memories"]:
                    if memory.get("memory_id") == memory_id:
                        target_memory = memory
                        target_character = character_name
                        break
                if target_memory:
                    break

        if not target_memory:
            return {
                "status": "error",
                "message": f"未找到记忆ID: {memory_id}"
            }

        if display_format == "json":
            return {
                "status": "success",
                "memory_id": memory_id,
                "character": target_character,
                "format": "json",
                "memory_data": target_memory
            }

        elif display_format == "summary":
            # 生成记忆摘要（需要AI能力）
            return {
                "status": "ai_task_required",
                "task_type": "generate_memory_summary",
                "memory_id": memory_id,
                "memory_data": target_memory,
                "character": target_character
            }

        else:  # readable
            formatted_content = self._format_single_memory(target_memory, target_character)
            return {
                "status": "success",
                "memory_id": memory_id,
                "character": target_character,
                "format": "readable",
                "content": formatted_content,
                "display_title": f"记忆详情：{memory_id}"
            }

    def _display_character_all_memories(self, character_name: str, display_format: str) -> Dict[str, Any]:
        """显示角色的所有记忆"""
        memories_result = self.memory_manager.get_character_memories(character_name)
        if memories_result["status"] != "success":
            return memories_result

        if display_format == "json":
            return {
                "status": "success",
                "character": character_name,
                "format": "json",
                "data": memories_result
            }

        elif display_format == "summary":
            # 生成角色记忆摘要（需要AI能力）
            return {
                "status": "ai_task_required",
                "task_type": "generate_character_memory_summary",
                "character": character_name,
                "memories": memories_result["memories"],
                "total_count": memories_result["total_count"]
            }

        elif display_format == "timeline":
            timeline_content = self._format_memory_timeline(memories_result["memories"])
            return {
                "status": "success",
                "character": character_name,
                "format": "timeline",
                "content": timeline_content,
                "total_count": memories_result["total_count"],
                "display_title": f"记忆时间线：{character_name}"
            }

        else:  # readable
            formatted_content = self._format_all_memories(memories_result["memories"])
            return {
                "status": "success",
                "character": character_name,
                "format": "readable",
                "content": formatted_content,
                "total_count": memories_result["total_count"],
                "memory_types": memories_result["memory_types"],
                "display_title": f"所有记忆：{character_name}"
            }

    def _display_memories_by_type(self, character_name: str, display_format: str) -> Dict[str, Any]:
        """按记忆类型显示记忆"""
        memories_result = self.memory_manager.get_character_memories(character_name)
        if memories_result["status"] != "success":
            return memories_result

        # 按类型分组
        memories_by_type = {}
        for memory in memories_result["memories"]:
            memory_type = memory.get("memory_type", "未知类型")
            if memory_type not in memories_by_type:
                memories_by_type[memory_type] = []
            memories_by_type[memory_type].append(memory)

        if display_format == "json":
            return {
                "status": "success",
                "character": character_name,
                "format": "json",
                "data": {
                    "memories_by_type": memories_by_type,
                    "total_count": memories_result["total_count"],
                    "memory_types": list(memories_by_type.keys())
                }
            }

        else:  # readable or summary
            formatted_content = self._format_memories_by_type(memories_by_type)
            return {
                "status": "success",
                "character": character_name,
                "format": display_format,
                "content": formatted_content,
                "memory_types": list(memories_by_type.keys()),
                "total_count": memories_result["total_count"],
                "display_title": f"记忆分类：{character_name}"
            }

    def _display_memory_timeline(self, character_name: str, display_format: str) -> Dict[str, Any]:
        """显示记忆时间线"""
        return self._display_character_all_memories(character_name, "timeline")

    def _display_memory_connections(self, character_name: str, display_format: str) -> Dict[str, Any]:
        """显示记忆关联"""
        # 这里需要关键词，暂时用默认关键词
        keywords = ["重要", "情感", "关键", "转折"]

        connections_result = self.memory_manager.find_memory_connections(character_name, keywords)
        if connections_result["status"] != "success":
            return connections_result

        if display_format == "json":
            return {
                "status": "success",
                "character": character_name,
                "format": "json",
                "data": connections_result
            }

        else:  # readable or summary
            formatted_content = self._format_memory_connections(connections_result["connected_memories"])
            return {
                "status": "success",
                "character": character_name,
                "format": display_format,
                "content": formatted_content,
                "keywords": keywords,
                "total_found": connections_result["total_found"],
                "display_title": f"记忆关联：{character_name}"
            }

    def get_memory_statistics(self, character_name: str = None) -> Dict[str, Any]:
        """获取记忆统计信息"""
        try:
            if character_name:
                # 单个角色的统计
                memories_result = self.memory_manager.get_character_memories(character_name)
                if memories_result["status"] != "success":
                    return memories_result

                stats = self._calculate_memory_stats(memories_result["memories"])
                stats["character"] = character_name

                return {
                    "status": "success",
                    "statistics": stats
                }
            else:
                # 所有角色的统计
                all_characters_result = self._get_all_characters_with_memories()
                if all_characters_result["status"] != "success":
                    return all_characters_result

                all_stats = {}
                total_memories = 0

                for char_name in all_characters_result["characters"]:
                    memories_result = self.memory_manager.get_character_memories(char_name)
                    if memories_result["status"] == "success":
                        char_stats = self._calculate_memory_stats(memories_result["memories"])
                        char_stats["character"] = char_name
                        all_stats[char_name] = char_stats
                        total_memories += memories_result["total_count"]

                return {
                    "status": "success",
                    "total_characters": len(all_stats),
                    "total_memories": total_memories,
                    "character_statistics": all_stats
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取记忆统计失败: {e}"
            }

    def _get_all_characters_with_memories(self) -> Dict[str, Any]:
        """获取所有有记忆记录的角色"""
        # 这里简化处理，实际应该从记忆文件中解析
        # 可以尝试读取记忆文件并提取角色名
        try:
            memory_file = self.memory_manager.character_memory_file
            if not memory_file.exists():
                return {"status": "success", "characters": []}

            content = memory_file.read_text(encoding='utf-8')
            characters = set()

            # 简单的提取角色名的逻辑
            import re
            sections = content.split("## ")
            for section in sections[1:]:  # 跳过第一个空section
                match = re.match(r'([^ -]+)', section.strip())
                if match:
                    characters.add(match.group(1))

            return {
                "status": "success",
                "characters": list(characters)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取角色列表失败: {e}"
            }

    def _calculate_memory_stats(self, memories: List[Dict]) -> Dict[str, Any]:
        """计算记忆统计信息"""
        if not memories:
            return {
                "total_memories": 0,
                "memory_types": {},
                "emotional_weights": {"min": 0, "max": 0, "avg": 0},
                "timeline_span": "无记忆"
            }

        # 记忆类型统计
        type_counts = {}
        for memory in memories:
            memory_type = memory.get("memory_type", "未知类型")
            type_counts[memory_type] = type_counts.get(memory_type, 0) + 1

        # 情感权重统计
        weights = [memory.get("emotional_weight", 0) for memory in memories]
        weight_stats = {
            "min": min(weights),
            "max": max(weights),
            "avg": sum(weights) / len(weights)
        }

        # 时间跨度统计
        timestamps = [memory.get("timestamp", "") for memory in memories if memory.get("timestamp")]
        if timestamps:
            timeline_span = f"{min(timestamps)} ~ {max(timestamps)}"
        else:
            timeline_span = "无时间信息"

        return {
            "total_memories": len(memories),
            "memory_types": type_counts,
            "emotional_weights": weight_stats,
            "timeline_span": timeline_span
        }

    def _format_single_memory(self, memory: Dict, character_name: str) -> str:
        """格式化单条记忆显示"""
        content_lines = [
            f"# {memory.get('title', '无标题')}",
            "",
            f"**角色**: {character_name}",
            f"**记忆ID**: {memory.get('memory_id', '未知')}",
            f"**记忆类型**: {memory.get('memory_type', '未知类型')}",
            f"**情感权重**: {memory.get('emotional_weight', 0)}/10",
            f"**发生时间**: {memory.get('occurrence_time', '未知')}",
            f"**记录时间**: {memory.get('timestamp', '未知')}",
            "",
            "## 记忆内容",
            memory.get('content', '无内容'),
        ]

        if memory.get('emotional_context'):
            content_lines.extend([
                "",
                "## 情感背景",
                memory['emotional_context']
            ])

        if memory.get('related_characters'):
            content_lines.extend([
                "",
                f"**相关角色**: {memory['related_characters']}"
            ])

        if memory.get('trigger_keywords'):
            content_lines.extend([
                "",
                f"**触发关键词**: {memory['trigger_keywords']}"
            ])

        return "\n".join(content_lines)

    def _format_all_memories(self, memories: List[Dict]) -> str:
        """格式化所有记忆显示"""
        if not memories:
            return "暂无记忆记录。"

        content_lines = [f"# 所有记忆记录 (共{len(memories)}条)\n"]

        # 按时间排序
        sorted_memories = sorted(memories, key=lambda x: x.get('timestamp', ''), reverse=True)

        for memory in sorted_memories:
            content_lines.append(f"## {memory.get('title', '无标题')}")
            content_lines.append(f"**记忆ID**: {memory.get('memory_id', '未知')}")
            content_lines.append(f"**类型**: {memory.get('memory_type', '未知')}")
            content_lines.append(f"**权重**: {memory.get('emotional_weight', 0)}/10")
            content_lines.append(f"**时间**: {memory.get('occurrence_time', '未知')}")
            content_lines.append(f"**内容**: {memory.get('content', '无内容')}")
            content_lines.append("")

        return "\n".join(content_lines)

    def _format_memories_by_type(self, memories_by_type: Dict[str, List[Dict]]) -> str:
        """按类型格式化记忆显示"""
        content_lines = ["# 记忆分类显示\n"]

        for memory_type, memories in memories_by_type.items():
            content_lines.append(f"## {memory_type} ({len(memories)}条)")

            for memory in memories:
                content_lines.append(f"### {memory.get('title', '无标题')}")
                content_lines.append(f"**记忆ID**: {memory.get('memory_id', '未知')}")
                content_lines.append(f"**情感权重**: {memory.get('emotional_weight', 0)}/10")
                content_lines.append(f"**时间**: {memory.get('occurrence_time', '未知')}")
                content_lines.append(f"**内容**: {memory.get('content', '无内容')}")
                content_lines.append("")

        return "\n".join(content_lines)

    def _format_memory_timeline(self, memories: List[Dict]) -> str:
        """格式化记忆时间线显示"""
        if not memories:
            return "暂无记忆记录。"

        content_lines = ["# 记忆时间线\n"]

        # 按时间排序
        sorted_memories = sorted(memories, key=lambda x: x.get('occurrence_time', ''), reverse=True)

        for memory in sorted_memories:
            occurrence_time = memory.get('occurrence_time', '未知时间')
            content_lines.append(f"## {occurrence_time}")
            content_lines.append(f"**事件**: {memory.get('title', '无标题')}")
            content_lines.append(f"**记忆ID**: {memory.get('memory_id', '未知')}")
            content_lines.append(f"**类型**: {memory.get('memory_type', '未知')}")
            content_lines.append(f"**情感冲击**: {memory.get('emotional_weight', 0)}/10")
            content_lines.append("")
            content_lines.append(f"**记忆内容**: {memory.get('content', '无内容')}")
            content_lines.append("---")
            content_lines.append("")

        return "\n".join(content_lines)

    def _format_memory_connections(self, connected_memories: List[Dict]) -> str:
        """格式化记忆关联显示"""
        if not connected_memories:
            return "未找到相关记忆。"

        content_lines = ["# 记忆关联网络\n"]

        for memory in connected_memories:
            content_lines.append(f"## {memory.get('title', '无标题')}")
            content_lines.append(f"**相关性评分**: {memory.get('relevance_score', 0):.2f}")
            content_lines.append(f"**关键词匹配**: {memory.get('keyword_matches', 0)}个")
            content_lines.append(f"**记忆类型**: {memory.get('memory_type', '未知')}")
            content_lines.append(f"**情感权重**: {memory.get('emotional_weight', 0)}/10")
            content_lines.append("")
            content_lines.append(f"**记忆内容**: {memory.get('content', '无内容')}")
            content_lines.append("---")
            content_lines.append("")

        return "\n".join(content_lines)

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="记忆显示管理器")
    parser.add_argument("--action", choices=["show", "stats"], default="show", help="操作类型")
    parser.add_argument("--identifier", required=True, help="记忆标识符（角色名、记忆ID等）")
    parser.add_argument("--type", choices=["single", "character_all", "by_type", "timeline", "connections"],
                       default="character_all", help="显示类型")
    parser.add_argument("--format", choices=["readable", "json", "summary", "timeline"],
                       default="readable", help="显示格式")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    mdm = MemoryDisplayManager(args.project_path)

    if args.action == "show":
        result = mdm.display_memory_segment(args.identifier, args.type, args.format)
    elif args.action == "stats":
        result = mdm.get_memory_statistics(args.identifier)
    else:
        result = {"status": "error", "message": f"未知操作: {args.action}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()