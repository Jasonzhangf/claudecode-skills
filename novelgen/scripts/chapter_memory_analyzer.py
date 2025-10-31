#!/usr/bin/env python3
"""
章节记忆分析器
自动解析章节内容，提取人物行为、情感和关系，生成相应的记忆条目
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from data_managers.memory_manager import MemoryManager
from data_managers.character_manager import CharacterManager

class ChapterMemoryAnalyzer:
    """章节记忆分析器，自动从章节内容生成人物记忆"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.memory_manager = MemoryManager(project_path)
        self.character_manager = CharacterManager(project_path)

        # 设置路径
        self.manuscript_dir = self.project_path / "manuscript" / "chapters"

        # 记忆类型定义
        self.memory_types = {
            "情感记忆": "角色在章节中体验到的强烈情感",
            "行动记忆": "角色在章节中执行的重要行动",
            "关系记忆": "角色与其他角色的互动关系",
            "环境记忆": "角色对环境变化的感知",
            "冲突记忆": "角色经历的冲突和矛盾",
            "成长记忆": "角色性格或认知的重要变化"
        }

        # 情感关键词映射
        self.emotion_keywords = {
            "喜悦": ["高兴", "快乐", "兴奋", "满足", "欣喜", "愉快"],
            "愤怒": ["生气", "愤怒", "恼火", "烦躁", "不满", "愤怒"],
            "悲伤": ["伤心", "难过", "痛苦", "沮丧", "失落", "哀伤"],
            "恐惧": ["害怕", "恐惧", "担心", "焦虑", "不安", "惊恐"],
            "惊讶": ["惊讶", "震惊", "意外", "震惊", "不敢相信"],
            "羞愧": ["羞愧", "尴尬", "不好意思", "羞耻"],
            "爱慕": ["爱", "喜欢", "爱慕", "倾心", "暗恋"],
            "嫉妒": ["嫉妒", "羡慕", "妒忌", "不甘心"]
        }

        # 关系关键词映射
        self.relationship_keywords = {
            "朋友": ["朋友", "友谊", "伙伴", "好友"],
            "敌人": ["敌人", "仇人", "对手", "敌人"],
            "恋人": ["爱人", "恋人", "情侣", "心上人"],
            "亲人": ["父亲", "母亲", "兄弟", "姐妹", "家人"],
            "师生": ["老师", "学生", "导师", "门生"],
            "上下级": ["上级", "下级", "领导", "下属", "老板", "同事"]
        }

    def analyze_chapter_content(self, chapter_number: int,
                               chapter_content: str = None) -> Dict[str, Any]:
        """
        分析章节内容并生成人物记忆

        Args:
            chapter_number: 章节号
            chapter_content: 章节内容（如果不提供则从文件读取）
        """
        try:
            # 如果没有提供内容，则从文件读取
            if chapter_content is None:
                chapter_content = self._load_chapter_content(chapter_number)
                if not chapter_content:
                    return {
                        "status": "error",
                        "message": f"无法读取第{chapter_number}章内容"
                    }

            # 获取角色列表
            characters_result = self.character_manager.list_characters()
            if characters_result["status"] != "success":
                return {
                    "status": "error",
                    "message": "无法获取角色列表"
                }

            characters = characters_result["characters"]
            character_names = [char["name"] for char in characters]

            # 分析章节内容
            analysis_result = self._analyze_content_for_memories(
                chapter_content, character_names
            )

            # 生成记忆条目
            memory_generation_result = self._generate_memory_entries(
                chapter_number, analysis_result
            )

            return {
                "status": "success",
                "chapter_number": chapter_number,
                "characters_found": character_names,
                "analysis_result": analysis_result,
                "memory_generation": memory_generation_result,
                "total_memories_generated": memory_generation_result["total_generated"]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"分析章节内容失败: {e}"
            }

    def _load_chapter_content(self, chapter_number: int) -> Optional[str]:
        """从文件加载章节内容"""
        try:
            chapter_dir = self.project_path / "draft" / "chapters" / f"chapter_{chapter_number:02d}"
            chapter_file = chapter_dir / f"chapter_{chapter_number:02d}.json"

            if not chapter_file.exists():
                return None

            with open(chapter_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("content", {}).get("main_content", "")

        except Exception:
            return None

    def _analyze_content_for_memories(self, content: str,
                                    character_names: List[str]) -> Dict[str, Any]:
        """分析章节内容，提取记忆相关信息"""
        analysis = {
            "character_actions": {},
            "character_emotions": {},
            "character_relationships": {},
            "character_conflicts": {},
            "character_growth": {},
            "chapter_events": [],
            "locations": []
        }

        # 提取章节中的事件
        analysis["chapter_events"] = self._extract_events(content)
        analysis["locations"] = self._extract_locations(content)

        # 为每个角色分析相关内容
        for character in character_names:
            # 提取角色相关段落
            character_paragraphs = self._extract_character_paragraphs(content, character)

            # 分析角色行为
            analysis["character_actions"][character] = self._extract_actions(
                character_paragraphs, character
            )

            # 分析角色情感
            analysis["character_emotions"][character] = self._extract_emotions(
                character_paragraphs, character
            )

            # 分析角色关系
            analysis["character_relationships"][character] = self._extract_relationships(
                character_paragraphs, character, character_names
            )

            # 分析角色冲突
            analysis["character_conflicts"][character] = self._extract_conflicts(
                character_paragraphs, character, character_names
            )

            # 分析角色成长
            analysis["character_growth"][character] = self._extract_growth(
                character_paragraphs, character
            )

        return analysis

    def _extract_events(self, content: str) -> List[str]:
        """提取章节中的主要事件"""
        events = []

        # 使用正则表达式提取关键事件描述
        event_patterns = [
            r'([^。！？]*[突然|忽然|瞬间|猛地|立即][^。！？]*[。！？])',
            r'([^。！？]*[决定|选择|同意|拒绝][^。！？]*[。！？])',
            r'([^。！？]*[发现|意识到][^。！？]*[。！？])',
            r'([^。！？]*[遇到|碰到][^。！？]*[。！？])'
        ]

        for pattern in event_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match.strip()) > 10:  # 过滤太短的匹配
                    events.append(match.strip())

        return events

    def _extract_locations(self, content: str) -> List[str]:
        """提取章节中的地点信息"""
        locations = []

        # 常见地点关键词
        location_keywords = ["房间", "街道", "建筑", "城市", "乡村", "学校", "公司", "家", "办公室"]

        for keyword in location_keywords:
            pattern = rf'([^。！？]*{keyword}[^。！？]*[。！？])'
            matches = re.findall(pattern, content)
            for match in matches:
                locations.append(match.strip())

        return locations

    def _extract_character_paragraphs(self, content: str, character: str) -> List[str]:
        """提取包含特定角色的段落"""
        paragraphs = []

        # 按句分割内容
        sentences = re.split(r'[。！？]', content)

        for sentence in sentences:
            if character in sentence:
                paragraphs.append(sentence.strip())

        return paragraphs

    def _extract_actions(self, paragraphs: List[str], character: str) -> List[str]:
        """提取角色行为"""
        actions = []

        action_verbs = ["走", "跑", "说", "想", "看", "听", "做", "拿", "放", "打开", "关闭", "开始", "结束", "决定", "选择"]

        for paragraph in paragraphs:
            for verb in action_verbs:
                if f"{character}{verb}" in paragraph or f"{verb}" in paragraph:
                    actions.append(paragraph)
                    break

        return actions

    def _extract_emotions(self, paragraphs: List[str], character: str) -> List[Tuple[str, str]]:
        """提取角色情感"""
        emotions = []

        for paragraph in paragraphs:
            for emotion_type, keywords in self.emotion_keywords.items():
                for keyword in keywords:
                    if keyword in paragraph:
                        emotions.append((emotion_type, paragraph))
                        break

        return emotions

    def _extract_relationships(self, paragraphs: List[str], character: str,
                             all_characters: List[str]) -> List[Dict[str, str]]:
        """提取角色关系"""
        relationships = []

        for paragraph in paragraphs:
            for other_character in all_characters:
                if other_character == character:
                    continue

                if other_character in paragraph:
                    # 判断关系类型
                    relationship_type = self._determine_relationship_type(paragraph)

                    relationships.append({
                        "character": other_character,
                        "relationship_type": relationship_type,
                        "context": paragraph
                    })

        return relationships

    def _determine_relationship_type(self, paragraph: str) -> str:
        """判断关系类型"""
        for relationship_type, keywords in self.relationship_keywords.items():
            for keyword in keywords:
                if keyword in paragraph:
                    return relationship_type

        return "未知关系"

    def _extract_conflicts(self, paragraphs: List[str], character: str,
                          all_characters: List[str]) -> List[str]:
        """提取角色冲突"""
        conflicts = []

        conflict_keywords = ["争吵", "反对", "不同意", "冲突", "打架", "愤怒", "威胁"]

        for paragraph in paragraphs:
            for keyword in conflict_keywords:
                if keyword in paragraph:
                    conflicts.append(paragraph)
                    break

        return conflicts

    def _extract_growth(self, paragraphs: List[str], character: str) -> List[str]:
        """提取角色成长信息"""
        growth = []

        growth_keywords = ["明白", "理解", "认识到", "学会", "改变", "成长", "成熟", "醒悟"]

        for paragraph in paragraphs:
            for keyword in growth_keywords:
                if keyword in paragraph:
                    growth.append(paragraph)
                    break

        return growth

    def _generate_memory_entries(self, chapter_number: int,
                               analysis: Dict[str, Any]) -> Dict[str, Any]:
        """根据分析结果生成记忆条目"""
        generated_memories = []
        total_generated = 0

        for character in analysis["character_actions"].keys():
            # 生成行动记忆
            for action in analysis["character_actions"][character]:
                memory = {
                    "character_name": character,
                    "memory_type": "行动记忆",
                    "content": action,
                    "emotional_weight": self._calculate_emotional_weight(action),
                    "occurrence_time": f"第{chapter_number}章",
                    "emotional_context": "章节中的重要行动",
                    "related_characters": self._extract_related_characters(action, character),
                    "trigger_keywords": self._extract_trigger_keywords(action),
                    "event_summary": f"第{chapter_number}章中的行动"
                }
                generated_memories.append(memory)
                total_generated += 1

            # 生成情感记忆
            for emotion_type, emotion_content in analysis["character_emotions"][character]:
                memory = {
                    "character_name": character,
                    "memory_type": "情感记忆",
                    "content": emotion_content,
                    "emotional_weight": self._calculate_emotional_weight(emotion_content),
                    "occurrence_time": f"第{chapter_number}章",
                    "emotional_context": emotion_type,
                    "related_characters": self._extract_related_characters(emotion_content, character),
                    "trigger_keywords": [emotion_type],
                    "event_summary": f"第{chapter_number}章中的{emotion_type}"
                }
                generated_memories.append(memory)
                total_generated += 1

            # 生成关系记忆
            for relationship in analysis["character_relationships"][character]:
                memory = {
                    "character_name": character,
                    "memory_type": "关系记忆",
                    "content": f"与{relationship['character']}的{relationship['relationship_type']}：{relationship['context']}",
                    "emotional_weight": self._calculate_emotional_weight(relationship['context']),
                    "occurrence_time": f"第{chapter_number}章",
                    "emotional_context": "角色关系发展",
                    "related_characters": [relationship['character']],
                    "trigger_keywords": [relationship['relationship_type']],
                    "event_summary": f"第{chapter_number}章中的关系发展"
                }
                generated_memories.append(memory)
                total_generated += 1

            # 生成冲突记忆
            for conflict in analysis["character_conflicts"][character]:
                memory = {
                    "character_name": character,
                    "memory_type": "冲突记忆",
                    "content": conflict,
                    "emotional_weight": 8,  # 冲突通常情感权重较高
                    "occurrence_time": f"第{chapter_number}章",
                    "emotional_context": "冲突和矛盾",
                    "related_characters": self._extract_related_characters(conflict, character),
                    "trigger_keywords": ["冲突", "矛盾"],
                    "event_summary": f"第{chapter_number}章中的冲突"
                }
                generated_memories.append(memory)
                total_generated += 1

            # 生成成长记忆
            for growth in analysis["character_growth"][character]:
                memory = {
                    "character_name": character,
                    "memory_type": "成长记忆",
                    "content": growth,
                    "emotional_weight": 7,  # 成长通常比较重要
                    "occurrence_time": f"第{chapter_number}章",
                    "emotional_context": "角色成长变化",
                    "related_characters": self._extract_related_characters(growth, character),
                    "trigger_keywords": ["成长", "变化", "成熟"],
                    "event_summary": f"第{chapter_number}章中的成长"
                }
                generated_memories.append(memory)
                total_generated += 1

        return {
            "generated_memories": generated_memories,
            "total_generated": total_generated
        }

    def _calculate_emotional_weight(self, content: str) -> int:
        """计算情感权重"""
        base_weight = 5

        # 根据关键词调整权重
        if any(word in content for word in ["爱", "喜欢", "幸福", "成功"]):
            base_weight += 2
        elif any(word in content for word in ["死亡", "背叛", "失败", "痛苦"]):
            base_weight += 3
        elif any(word in content for word in ["决定", "选择", "重要"]):
            base_weight += 1

        return min(10, max(1, base_weight))

    def _extract_related_characters(self, content: str, main_character: str) -> str:
        """提取相关角色"""
        # 这里简化处理，实际需要更复杂的角色识别逻辑
        # 返回空字符串，让系统后续处理
        return ""

    def _extract_trigger_keywords(self, content: str) -> List[str]:
        """提取触发关键词"""
        keywords = []

        # 简单的关键词提取
        important_words = ["决定", "选择", "变化", "冲突", "成长", "爱情", "友情", "家庭"]

        for word in important_words:
            if word in content:
                keywords.append(word)

        return keywords

    def get_analysis_info(self, chapter_number: int) -> Dict[str, Any]:
        """获取记忆分析信息"""
        try:
            chapter_file = self.manuscript_dir / f"chapter_{chapter_number:02d}" / "analysis.json"

            if not chapter_file.exists():
                return {
                    "status": "success",
                    "chapter_number": chapter_number,
                    "analysis_exists": False,
                    "message": f"第{chapter_number}章尚未进行记忆分析"
                }

            with open(chapter_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)

            return {
                "status": "success",
                "chapter_number": chapter_number,
                "analysis_exists": True,
                "analysis_data": analysis_data,
                "analysis_summary": {
                    "characters_found": len(analysis_data.get("character_actions", {})),
                    "total_memories": sum(len(memories) for memories in analysis_data.get("generated_memories", {}).values()),
                    "events_count": len(analysis_data.get("chapter_events", [])),
                    "locations_count": len(analysis_data.get("locations", []))
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取分析信息失败: {e}"
            }

    def apply_generated_memories(self, chapter_number: int,
                               auto_confirm: bool = False) -> Dict[str, Any]:
        """应用生成的记忆到记忆系统"""
        try:
            # 分析章节内容
            analysis_result = self.analyze_chapter_content(chapter_number)
            if analysis_result["status"] != "success":
                return analysis_result

            memories = analysis_result["memory_generation"]["generated_memories"]

            if not memories:
                return {
                    "status": "success",
                    "message": f"第{chapter_number}章没有生成记忆",
                    "total_memories": 0
                }

            # 应用记忆
            applied_count = 0
            failed_memories = []

            for memory in memories:
                try:
                    result = self.memory_manager.add_character_memory(
                        memory["character_name"], memory
                    )
                    if result["status"] == "success":
                        applied_count += 1
                    else:
                        failed_memories.append({
                            "character": memory["character_name"],
                            "error": result.get("message", "未知错误")
                        })
                except Exception as e:
                    failed_memories.append({
                        "character": memory["character_name"],
                        "error": str(e)
                    })

            return {
                "status": "success",
                "chapter_number": chapter_number,
                "total_generated": len(memories),
                "total_applied": applied_count,
                "failed_count": len(failed_memories),
                "failed_memories": failed_memories,
                "message": f"第{chapter_number}章记忆处理完成：成功应用{applied_count}条，失败{len(failed_memories)}条"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"应用记忆失败: {e}"
            }

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="章节记忆分析器")
    parser.add_argument("--action", choices=["analyze", "apply"], default="analyze",
                       help="操作类型")
    parser.add_argument("--chapter", type=int, required=True, help="章节号")
    parser.add_argument("--project-path", default=".", help="项目路径")
    parser.add_argument("--auto-confirm", action="store_true", help="自动确认应用记忆")

    args = parser.parse_args()

    analyzer = ChapterMemoryAnalyzer(args.project_path)

    if args.action == "analyze":
        result = analyzer.analyze_chapter_content(args.chapter)
    elif args.action == "apply":
        result = analyzer.apply_generated_memories(args.chapter, args.auto_confirm)
    else:
        result = {"status": "error", "message": f"未知操作: {args.action}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()