#!/usr/bin/env python3
"""
小说生成器 - 压缩引擎
负责三层压缩机制：近期、中期、长期压缩
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import subprocess
import tempfile

class CompressionEngine:
    """压缩引擎，实现三层智能压缩机制"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.manuscript_dir = self.project_path / "manuscript"
        self.system_dir = self.project_path / "system"

        # 压缩配置
        self.compression_config = {
            "recent": {
                "target_tokens": 2000,
                "compression_ratio": 0.1,
                "retention_policy": "detailed_events",
                "trigger_frequency": "every_chapter"
            },
            "medium": {
                "target_tokens": 500,
                "compression_ratio": 0.025,
                "retention_policy": "key_plot_points",
                "trigger_frequency": "every_10_chapters"
            },
            "long_term": {
                "target_tokens": 100,
                "compression_ratio": 0.005,
                "retention_policy": "major_story_arcs",
                "trigger_frequency": "every_50_chapters"
            }
        }

        # 压缩日志
        self.compression_log_file = self.system_dir / "compression_log.json"

    def compress_chapter(self, chapter: int, compression_types: List[str] = None) -> Dict[str, Any]:
        """压缩指定章节"""
        if compression_types is None:
            compression_types = ["recent", "medium", "long_term"]

        results = {}
        chapter_success = True

        for compression_type in compression_types:
            try:
                result = self._compress_single_chapter(chapter, compression_type)
                results[compression_type] = result

                if result["status"] != "success":
                    chapter_success = False

            except Exception as e:
                results[compression_type] = {
                    "status": "error",
                    "message": f"{compression_type}压缩失败: {e}"
                }
                chapter_success = False

        # 记录压缩日志
        self._log_compression(chapter, results)

        # 检查是否需要触发批量压缩
        if chapter_success and self._should_trigger_batch_compression(chapter):
            batch_result = self._trigger_batch_compression(chapter)
            results["batch_compression"] = batch_result

        return {
            "status": "success" if chapter_success else "partial_success",
            "chapter": chapter,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

    def recompress_chapters(self, chapter_range: Tuple[int, int],
                           compression_type: str = "all") -> Dict[str, Any]:
        """重新压缩章节范围"""
        start_chapter, end_chapter = chapter_range
        results = {}

        for chapter in range(start_chapter, end_chapter + 1):
            if compression_type == "all":
                types = ["recent", "medium", "long_term"]
            else:
                types = [compression_type]

            chapter_result = self.compress_chapter(chapter, types)
            results[f"chapter_{chapter}"] = chapter_result

        successful = sum(1 for r in results.values() if r["status"] == "success")
        total = len(results)

        return {
            "status": "success" if successful == total else "partial_success",
            "chapter_range": chapter_range,
            "compression_type": compression_type,
            "successful": successful,
            "total": total,
            "success_rate": successful / total,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

    def get_compression_status(self, chapter: int = None) -> Dict[str, Any]:
        """获取压缩状态"""
        if chapter:
            return self._get_chapter_compression_status(chapter)
        else:
            return self._get_project_compression_status()

    def _compress_single_chapter(self, chapter: int, compression_type: str) -> Dict[str, Any]:
        """压缩单个章节"""
        # 加载章节内容
        chapter_content = self._load_chapter_content(chapter)
        if not chapter_content:
            return {
                "status": "error",
                "message": f"无法加载第{chapter}章内容"
            }

        # 加载相关上下文
        context_data = self._load_chapter_context(chapter)

        # 根据压缩类型执行不同的压缩策略
        if compression_type == "recent":
            return self._compress_recent(chapter, chapter_content, context_data)
        elif compression_type == "medium":
            return self._compress_medium(chapter, chapter_content, context_data)
        elif compression_type == "long_term":
            return self._compress_long_term(chapter, chapter_content, context_data)
        else:
            return {
                "status": "error",
                "message": f"未知的压缩类型: {compression_type}"
            }

    def _compress_recent(self, chapter: int, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """近期压缩 - 保留详细事件"""
        try:
            # 近期压缩策略：保留主要事件、重要对话、关键场景
            compressed_data = {
                "plot_summary": self._extract_plot_summary(content, detail_level="high"),
                "character_actions": self._extract_character_actions(content, detail_level="high"),
                "key_dialogues": self._extract_key_dialogues(content, limit=20),
                "scene_changes": self._extract_scene_changes(content, detail_level="high"),
                "emotional_beats": self._extract_emotional_beats(content),
                "timeline_markers": self._extract_timeline_markers(content)
            }

            # 估算token数量并调整
            current_tokens = self._estimate_compressed_tokens(compressed_data)
            target_tokens = self.compression_config["recent"]["target_tokens"]

            if current_tokens > target_tokens:
                compressed_data = self._adjust_compression_level(compressed_data, target_tokens)

            # 保存压缩结果
            saved = self._save_compression_data(chapter, "recent", compressed_data)

            return {
                "status": "success" if saved else "error",
                "compression_type": "recent",
                "original_tokens": self._estimate_tokens(content),
                "compressed_tokens": self._estimate_compressed_tokens(compressed_data),
                "compression_ratio": self._estimate_compressed_tokens(compressed_data) / self._estimate_tokens(content)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"近期压缩失败: {e}"
            }

    def _compress_medium(self, chapter: int, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """中期压缩 - 保留关键情节点"""
        try:
            # 中期压缩策略：只保留关键情节转折和主要角色发展
            compressed_data = {
                "plot_summary": self._extract_plot_summary(content, detail_level="medium"),
                "major_events": self._extract_major_events(content, limit=5),
                "character_developments": self._extract_character_developments(content, limit=3),
                "plot_advancements": self._extract_plot_advancements(content, limit=3),
                "key_relationships": self._extract_key_relationships(content)
            }

            # 估算token数量并调整
            current_tokens = self._estimate_compressed_tokens(compressed_data)
            target_tokens = self.compression_config["medium"]["target_tokens"]

            if current_tokens > target_tokens:
                compressed_data = self._adjust_compression_level(compressed_data, target_tokens)

            # 保存压缩结果
            saved = self._save_compression_data(chapter, "medium", compressed_data)

            return {
                "status": "success" if saved else "error",
                "compression_type": "medium",
                "original_tokens": self._estimate_tokens(content),
                "compressed_tokens": self._estimate_compressed_tokens(compressed_data),
                "compression_ratio": self._estimate_compressed_tokens(compressed_data) / self._estimate_tokens(content)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"中期压缩失败: {e}"
            }

    def _compress_long_term(self, chapter: int, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """长期压缩 - 保留主要故事线"""
        try:
            # 长期压缩策略：只保留最核心的故事线和结局
            compressed_data = {
                "major_arc": self._extract_major_arc(content),
                "story_impact": self._extract_story_impact(content),
                "character_destinations": self._extract_character_destinations(content),
                "thematic_elements": self._extract_thematic_elements(content),
                "legacy_notes": self._extract_legacy_notes(content)
            }

            # 估算token数量并调整
            current_tokens = self._estimate_compressed_tokens(compressed_data)
            target_tokens = self.compression_config["long_term"]["target_tokens"]

            if current_tokens > target_tokens:
                compressed_data = self._adjust_compression_level(compressed_data, target_tokens)

            # 保存压缩结果
            saved = self._save_compression_data(chapter, "long_term", compressed_data)

            return {
                "status": "success" if saved else "error",
                "compression_type": "long_term",
                "original_tokens": self._estimate_tokens(content),
                "compressed_tokens": self._estimate_compressed_tokens(compressed_data),
                "compression_ratio": self._estimate_compressed_tokens(compressed_data) / self._estimate_tokens(content)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"长期压缩失败: {e}"
            }

    def _load_chapter_content(self, chapter: int) -> Optional[str]:
        """加载章节内容"""
        chapter_file = (self.manuscript_dir / "chapters" /
                       f"chapter_{chapter:02d}" / f"chapter_{chapter:02d}.md")

        if not chapter_file.exists():
            return None

        content = chapter_file.read_text(encoding='utf-8')

        # 提取正文内容（去掉FrontMatter）
        if content.startswith('---\n'):
            parts = content.split('---\n', 2)
            if len(parts) >= 3:
                return parts[2].strip()

        return content.strip()

    def _load_chapter_context(self, chapter: int) -> Dict[str, Any]:
        """加载章节上下文信息"""
        # 加载相关记忆压缩
        memory_data = self._load_memory_compression(chapter)

        # 加载角色状态变化
        character_changes = self._load_character_changes(chapter)

        return {
            "memory_data": memory_data,
            "character_changes": character_changes,
            "chapter_number": chapter
        }

    def _extract_plot_summary(self, content: str, detail_level: str = "high") -> str:
        """提取情节摘要"""
        # 使用正则表达式和关键词识别重要情节节点
        plot_indicators = [
            r'第.*章.*?\n',
            r'[情节|故事|剧情].*?[推进|发展|转折]',
            r'[突然|忽然|瞬间].*?[发生|出现]',
            r'[决定|选择|行动].*?[去做|开始]'
        ]

        sentences = self._split_into_sentences(content)
        important_sentences = []

        for sentence in sentences:
            for pattern in plot_indicators:
                if re.search(pattern, sentence):
                    important_sentences.append(sentence)
                    break

        # 根据详细程度调整摘要长度
        if detail_level == "high":
            return "\n".join(important_sentences[:50])  # 最多50句
        elif detail_level == "medium":
            return "\n".join(important_sentences[:20])  # 最多20句
        else:
            return "\n".join(important_sentences[:10])  # 最多10句

    def _extract_character_actions(self, content: str, detail_level: str = "high") -> List[str]:
        """提取角色行动"""
        # 识别角色行为模式
        action_patterns = [
            r'([A-Za-z\u4e00-\u9fff]+)[说说道道地]*[说讲道谈]:.*',
            r'([A-Za-z\u4e00-\u9fff]+)[慢慢悄悄轻轻].*[走来走去站起坐下]',
            r'([A-Za-z\u4e00-\u9fff]+)[看想回忆].*[东西事情过去]'
        ]

        actions = []
        sentences = self._split_into_sentences(content)

        for sentence in sentences:
            for pattern in action_patterns:
                match = re.search(pattern, sentence)
                if match:
                    actions.append(f"{match.group(1)}: {sentence.strip()}")
                    break

        # 根据详细程度调整数量
        if detail_level == "high":
            return actions[:30]
        elif detail_level == "medium":
            return actions[:15]
        else:
            return actions[:8]

    def _extract_key_dialogues(self, content: str, limit: int = 20) -> List[str]:
        """提取关键对话"""
        # 识别对话内容
        dialogue_pattern = r'[：:""]([^：:""]{20,})[：:""]'
        dialogues = re.findall(dialogue_pattern, content)

        # 选择较长的对话作为关键对话
        dialogues.sort(key=len, reverse=True)
        return dialogues[:limit]

    def _extract_scene_changes(self, content: str, detail_level: str = "high") -> List[str]:
        """提取场景变化"""
        scene_indicators = [
            r'[房间|街道|森林|宫殿|学校|公司][内外上下]',
            r'[天气|时间][变化|流逝|过去]',
            r'[早上|中午|下午|晚上|深夜]'
        ]

        scene_changes = []
        sentences = self._split_into_sentences(content)

        for sentence in sentences:
            for pattern in scene_indicators:
                if re.search(pattern, sentence):
                    scene_changes.append(sentence.strip())
                    break

        # 根据详细程度调整数量
        if detail_level == "high":
            return scene_changes[:20]
        elif detail_level == "medium":
            return scene_changes[:10]
        else:
            return scene_changes[:5]

    def _extract_emotional_beats(self, content: str) -> List[str]:
        """提取情感节点"""
        emotion_words = [
            '高兴', '兴奋', '满意', '得意',
            '悲伤', '难过', '失望', '沮丧',
            '愤怒', '生气', '恼火', '暴怒',
            '恐惧', '害怕', '紧张', '焦虑',
            '惊讶', '震惊', '意外', '困惑'
        ]

        emotional_beats = []
        sentences = self._split_into_sentences(content)

        for sentence in sentences:
            for emotion in emotion_words:
                if emotion in sentence:
                    emotional_beats.append(sentence.strip())
                    break

        return emotional_beats[:15]

    def _extract_major_events(self, content: str, limit: int = 5) -> List[str]:
        """提取主要事件"""
        event_indicators = [
            '战斗', '死亡', '出生', '结婚', '分离', '重逢',
            '发现', '决定', '胜利', '失败', '背叛', '拯救'
        ]

        major_events = []
        sentences = self._split_into_sentences(content)

        for sentence in sentences:
            for indicator in event_indicators:
                if indicator in sentence:
                    major_events.append(sentence.strip())
                    break

        return major_events[:limit]

    def _extract_character_developments(self, content: str, limit: int = 3) -> List[str]:
        """提取角色发展"""
        development_patterns = [
            r'[成长|变化|改变|蜕变]',
            r'[明白|领悟|醒悟|意识到]',
            r'[学会|掌握|获得|失去]'
        ]

        developments = []
        sentences = self._split_into_sentences(content)

        for sentence in sentences:
            for pattern in development_patterns:
                if re.search(pattern, sentence):
                    developments.append(sentence.strip())
                    break

        return developments[:limit]

    def _extract_plot_advancements(self, content: str, limit: int = 3) -> List[str]:
        """提取情节推进"""
        advancement_patterns = [
            r'[线索|秘密|真相][揭露|发现|揭示]',
            r'[计划|阴谋][开始|实施|失败]',
            r'[目标|愿望][实现|破灭|改变]'
        ]

        advancements = []
        sentences = self._split_into_sentences(content)

        for sentence in sentences:
            for pattern in advancement_patterns:
                if re.search(pattern, sentence):
                    advancements.append(sentence.strip())
                    break

        return advancements[:limit]

    def _extract_key_relationships(self, content: str) -> List[str]:
        """提取关键关系"""
        relationship_patterns = [
            r'[朋友|敌人|恋人|家人][关系变化]',
            r'[信任|背叛|支持][理解|误解]',
            r'[相遇|离别|重逢][场景时刻]'
        ]

        relationships = []
        sentences = self._split_into_sentences(content)

        for sentence in sentences:
            for pattern in relationship_patterns:
                if re.search(pattern, sentence):
                    relationships.append(sentence.strip())
                    break

        return relationships[:10]

    def _extract_major_arc(self, content: str) -> str:
        """提取主要故事线"""
        # 寻找章节的核心主题和主要进展
        core_elements = self._extract_major_events(content, 3)
        character_dev = self._extract_character_developments(content, 2)

        arc_summary = f"本章主要发展: {'; '.join(core_elements)}"
        if character_dev:
            arc_summary += f"\n角色成长: {'; '.join(character_dev)}"

        return arc_summary

    def _extract_story_impact(self, content: str) -> str:
        """提取故事影响"""
        # 分析本章对整体故事的影响
        impact_keywords = ['转折点', '关键', '重要', '决定性', '深远影响']

        impact_sentences = []
        sentences = self._split_into_sentences(content)

        for sentence in sentences:
            for keyword in impact_keywords:
                if keyword in sentence:
                    impact_sentences.append(sentence.strip())
                    break

        return "\n".join(impact_sentences[:5])

    def _extract_character_destinations(self, content: str) -> List[str]:
        """提取角色结局方向"""
        destination_patterns = [
            r'[未来|前景|命运][走向|方向]',
            r'[希望|目标|梦想][实现|破灭]'
        ]

        destinations = []
        sentences = self._split_into_sentences(content)

        for sentence in sentences:
            for pattern in destination_patterns:
                if re.search(pattern, sentence):
                    destinations.append(sentence.strip())
                    break

        return destinations[:5]

    def _extract_thematic_elements(self, content: str) -> List[str]:
        """提取主题元素"""
        theme_keywords = [
            '爱', '恨', '正义', '邪恶', '牺牲', '成长', '背叛', '救赎',
            '自由', '命运', '选择', '责任', '家庭', '友谊'
        ]

        themes = []
        for keyword in theme_keywords:
            if keyword in content:
                themes.append(keyword)

        return themes

    def _extract_legacy_notes(self, content: str) -> str:
        """提取传承要点"""
        # 本章对后续章节可能产生的影响
        return "本章为后续发展埋下伏笔，影响角色关系和故事走向。"

    def _extract_timeline_markers(self, content: str) -> List[str]:
        """提取时间线标记"""
        time_patterns = [
            r'[早上|上午|中午|下午|晚上|深夜]',
            r'[春天|夏天|秋天|冬天]',
            r'[昨天|今天|明天]'
        ]

        markers = []
        sentences = self._split_into_sentences(content)

        for sentence in sentences:
            for pattern in time_patterns:
                if re.search(pattern, sentence):
                    markers.append(sentence.strip())
                    break

        return markers[:10]

    def _split_into_sentences(self, content: str) -> List[str]:
        """将文本分割为句子"""
        # 简单的句子分割逻辑
        sentences = re.split(r'[。！？\n]+', content)
        return [s.strip() for s in sentences if s.strip()]

    def _estimate_tokens(self, text: str) -> int:
        """估算文本token数量"""
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_words = len(text.split()) - chinese_chars
        return int(chinese_chars * 1.5 + english_words)

    def _estimate_compressed_tokens(self, compressed_data: Dict[str, Any]) -> int:
        """估算压缩数据的token数量"""
        total_tokens = 0
        for key, value in compressed_data.items():
            if isinstance(value, str):
                total_tokens += self._estimate_tokens(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        total_tokens += self._estimate_tokens(item)
        return total_tokens

    def _adjust_compression_level(self, compressed_data: Dict[str, Any], target_tokens: int) -> Dict[str, Any]:
        """调整压缩级别以符合目标token数"""
        current_tokens = self._estimate_compressed_tokens(compressed_data)

        if current_tokens <= target_tokens:
            return compressed_data

        # 按优先级减少内容
        priority_items = [
            ('legacy_notes', 0.1),
            ('thematic_elements', 0.2),
            ('timeline_markers', 0.3),
            ('emotional_beats', 0.4),
            ('scene_changes', 0.5),
            ('key_dialogues', 0.6),
            ('character_actions', 0.7),
            ('plot_summary', 0.8)
        ]

        adjusted_data = compressed_data.copy()

        for item_name, reduction_ratio in priority_items:
            if current_tokens <= target_tokens:
                break

            if item_name in adjusted_data:
                item_value = adjusted_data[item_name]
                if isinstance(item_value, str):
                    # 缩短文本
                    sentences = self._split_into_sentences(item_value)
                    keep_count = int(len(sentences) * reduction_ratio)
                    adjusted_data[item_name] = '\n'.join(sentences[:keep_count])
                elif isinstance(item_value, list):
                    # 减少列表项
                    keep_count = int(len(item_value) * reduction_ratio)
                    adjusted_data[item_name] = item_value[:keep_count]

                current_tokens = self._estimate_compressed_tokens(adjusted_data)

        return adjusted_data

    def _save_compression_data(self, chapter: int, compression_type: str,
                             compressed_data: Dict[str, Any]) -> bool:
        """保存压缩数据"""
        try:
            # 创建压缩目录
            compression_dir = (self.manuscript_dir / "chapters" / f"chapter_{chapter:02d}" /
                              "compression" / compression_type)
            compression_dir.mkdir(parents=True, exist_ok=True)

            # 保存各个压缩组件
            for key, value in compressed_data.items():
                if isinstance(value, str):
                    file_path = compression_dir / f"{key}.md"
                    file_path.write_text(value, encoding='utf-8')
                elif isinstance(value, list):
                    file_path = compression_dir / f"{key}.md"
                    list_content = '\n'.join(f"- {item}" for item in value)
                    file_path.write_text(list_content, encoding='utf-8')

            # 保存压缩元数据
            metadata = {
                "chapter": chapter,
                "compression_type": compression_type,
                "compressed_at": datetime.now().isoformat(),
                "original_tokens": self._estimate_tokens(self._load_chapter_content(chapter) or ""),
                "compressed_tokens": self._estimate_compressed_tokens(compressed_data),
                "components": list(compressed_data.keys())
            }

            metadata_file = compression_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            return True

        except Exception:
            return False

    def _should_trigger_batch_compression(self, chapter: int) -> bool:
        """判断是否应该触发批量压缩"""
        return chapter % 10 == 0  # 每10章触发一次

    def _trigger_batch_compression(self, chapter: int) -> Dict[str, Any]:
        """触发批量压缩"""
        try:
            # 压缩前10章的中期和长期压缩
            start_chapter = max(1, chapter - 9)
            end_chapter = chapter

            result = self.recompress_chapters((start_chapter, end_chapter), "medium")

            # 如果达到50章，也触发长期压缩
            if chapter >= 50:
                long_term_result = self.recompress_chapters((1, chapter), "long_term")
                result["long_term_batch"] = long_term_result

            return result

        except Exception as e:
            return {
                "status": "error",
                "message": f"批量压缩失败: {e}"
            }

    def _log_compression(self, chapter: int, results: Dict[str, Any]):
        """记录压缩日志"""
        try:
            # 加载现有日志
            if self.compression_log_file.exists():
                with open(self.compression_log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = []

            # 添加新日志条目
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "chapter": chapter,
                "results": results
            }
            log_data.append(log_entry)

            # 保留最近1000条日志
            log_data = log_data[-1000:]

            # 保存日志
            with open(self.compression_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)

        except Exception:
            pass  # 日志失败不影响主流程

    def _get_chapter_compression_status(self, chapter: int) -> Dict[str, Any]:
        """获取单个章节的压缩状态"""
        compression_dir = self.manuscript_dir / "chapters" / f"chapter_{chapter:02d}" / "compression"

        if not compression_dir.exists():
            return {
                "chapter": chapter,
                "status": "not_found",
                "compression_types": []
            }

        compression_types = []
        for compression_type in ["recent", "medium", "long_term"]:
            type_dir = compression_dir / compression_type
            if type_dir.exists() and (type_dir / "metadata.json").exists():
                with open(type_dir / "metadata.json", 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                compression_types.append(metadata)

        return {
            "chapter": chapter,
            "status": "found" if compression_types else "not_compressed",
            "compression_types": compression_types
        }

    def _get_project_compression_status(self) -> Dict[str, Any]:
        """获取整个项目的压缩状态"""
        chapters_dir = self.manuscript_dir / "chapters"

        if not chapters_dir.exists():
            return {"status": "no_chapters", "total_chapters": 0}

        chapter_dirs = [d for d in chapters_dir.iterdir()
                       if d.is_dir() and d.name.startswith("chapter_")]
        chapter_dirs.sort(key=lambda x: int(x.name.split('_')[1]))

        total_chapters = len(chapter_dirs)
        compressed_chapters = 0
        compression_summary = {"recent": 0, "medium": 0, "long_term": 0}

        for chapter_dir in chapter_dirs:
            chapter_num = int(chapter_dir.name.split('_')[1])
            chapter_status = self._get_chapter_compression_status(chapter_num)

            if chapter_status["status"] == "found":
                compressed_chapters += 1
                for comp_type in chapter_status["compression_types"]:
                    compression_summary[comp_type["compression_type"]] += 1

        return {
            "status": "success",
            "total_chapters": total_chapters,
            "compressed_chapters": compressed_chapters,
            "compression_rate": compressed_chapters / total_chapters if total_chapters > 0 else 0,
            "compression_summary": compression_summary
        }

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="小说生成器压缩引擎")
    parser.add_argument("--action", choices=["compress", "recompress", "status"],
                       required=True, help="操作类型")
    parser.add_argument("--chapters", help="章节范围 (如: 1-10 或 5)")
    parser.add_argument("--type", choices=["recent", "medium", "long_term", "all"],
                       default="all", help="压缩类型")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    ce = CompressionEngine(args.project_path)

    if args.action == "compress":
        if not args.chapters:
            print("错误: compress操作需要指定--chapters参数")
            return

        if '-' in args.chapters:
            start, end = map(int, args.chapters.split('-'))
            chapters = list(range(start, end + 1))
        else:
            chapters = [int(args.chapters)]

        compression_types = None if args.type == "all" else [args.type]

        for chapter in chapters:
            result = ce.compress_chapter(chapter, compression_types)
            print(f"第{chapter}章压缩结果: {result['status']}")

    elif args.action == "recompress":
        if not args.chapters or '-' not in args.chapters:
            print("错误: recompress操作需要指定章节范围 (如: --chapters 1-10)")
            return

        start, end = map(int, args.chapters.split('-'))
        compression_type = None if args.type == "all" else args.type

        result = ce.recompress_chapters((start, end), compression_type)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "status":
        if args.chapters:
            result = ce.get_compression_status(int(args.chapters))
        else:
            result = ce.get_compression_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()