#!/usr/bin/env python3
"""
章节梗概生成器
为章节创作提供梗概建议和引导
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from settings_completeness_checker import SettingsCompletenessChecker

class ChapterOutlineGenerator:
    """章节梗概生成器"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.settings_dir = self.project_path / "settings"
        self.draft_dir = self.project_path / "draft" / "chapters"
        self.manuscript_dir = self.project_path / "manuscript" / "chapters"

        # 初始化设定检查器
        self.settings_checker = SettingsCompletenessChecker(str(self.project_path))

    def prepare_chapter_creation(self, chapter_number: int) -> Dict[str, Any]:
        """准备章节创作，检查前置条件并提供引导"""
        preparation_result = {
            "chapter_number": chapter_number,
            "ready_for_creation": False,
            "settings_status": None,
            "existing_outline": None,
            "creation_guidance": {},
            "suggestions": {},
            "blocking_issues": [],
            "check_time": datetime.now().isoformat()
        }

        # 1. 检查设定完整性
        settings_status = self.settings_checker.check_all_settings_completeness()
        preparation_result["settings_status"] = settings_status

        if not settings_status["ready_for_writing"]:
            preparation_result["blocking_issues"].append("基础设定不完整，需要先完善设定")
            user_guidance = self.settings_checker.generate_user_guidance(settings_status)
            preparation_result["creation_guidance"] = user_guidance
            return preparation_result

        # 2. 检查现有章节状态
        existing_chapters = self._get_existing_chapters()
        chapter_context = self._analyze_chapter_context(chapter_number, existing_chapters)
        preparation_result["chapter_context"] = chapter_context

        # 3. 检查是否有现有梗概
        existing_outline = self._get_existing_outline(chapter_number)
        preparation_result["existing_outline"] = existing_outline

        # 4. 生成章节创作建议
        suggestions = self._generate_chapter_suggestions(chapter_number, chapter_context, settings_status)
        preparation_result["suggestions"] = suggestions

        # 5. 检查是否准备好创作
        preparation_result["ready_for_creation"] = len(preparation_result["blocking_issues"]) == 0

        # 6. 生成创作引导
        if preparation_result["ready_for_creation"]:
            creation_guidance = self._generate_creation_guidance(chapter_number, chapter_context, suggestions)
            preparation_result["creation_guidance"] = creation_guidance

        return preparation_result

    def generate_outline_suggestions(self, chapter_number: int, context_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成章节梗概建议"""
        if context_info is None:
            context_info = self._analyze_chapter_context(chapter_number, self._get_existing_chapters())

        suggestions = {
            "chapter_number": chapter_number,
            "outline_options": [],
            "key_elements": [],
            "character_focus": [],
            "plot_advancement": [],
            "scene_suggestions": [],
            "estimated_length": "2000-3000字",
            "ai_task_required": False
        }

        # 获取项目设定信息
        settings_status = self.settings_checker.check_all_settings_completeness()

        # 生成多个梗概选项
        suggestions["outline_options"] = self._generate_outline_options(chapter_number, context_info, settings_status)

        # 确定关键元素
        suggestions["key_elements"] = self._identify_key_elements(chapter_number, context_info)

        # 确定角色焦点
        suggestions["character_focus"] = self._determine_character_focus(chapter_number, context_info)

        # 确定情节推进
        suggestions["plot_advancement"] = self._identify_plot_advancement(chapter_number, context_info)

        # 生成场景建议
        suggestions["scene_suggestions"] = self._generate_scene_suggestions(chapter_number, context_info)

        # 如果需要AI生成更详细的梗概，设置AI任务
        if len(suggestions["outline_options"]) == 0 or len(suggestions["key_elements"]) < 3:
            suggestions["ai_task_required"] = True
            suggestions["ai_task"] = {
                "task_type": "generate_outline",
                "chapter_number": chapter_number,
                "context": context_info,
                "settings_summary": self._create_settings_summary(settings_status),
                "requirements": {
                    "length": "detailed outline for 2000-3000 words chapter",
                    "style": "detailed and actionable",
                    "include": ["key scenes", "character development", "plot progression", "dialogue hints"]
                }
            }

        return suggestions

    def _get_existing_chapters(self) -> List[Dict[str, Any]]:
        """获取现有章节信息"""
        existing_chapters = []

        # 检查草稿章节
        if self.draft_dir.exists():
            for chapter_dir in self.draft_dir.iterdir():
                if chapter_dir.is_dir() and chapter_dir.name.startswith("chapter_"):
                    chapter_info = self._get_chapter_info(chapter_dir)
                    if chapter_info:
                        existing_chapters.append(chapter_info)

        # 检查成品章节
        if self.manuscript_dir.exists():
            for chapter_dir in self.manuscript_dir.iterdir():
                if chapter_dir.is_dir() and chapter_dir.name.startswith("chapter_"):
                    chapter_info = self._get_chapter_info(chapter_dir)
                    if chapter_info:
                        chapter_info["is_manuscript"] = True
                        existing_chapters.append(chapter_info)

        # 按章节号排序
        existing_chapters.sort(key=lambda x: x.get("chapter_number", 0))
        return existing_chapters

    def _get_chapter_info(self, chapter_dir: Path) -> Optional[Dict[str, Any]]:
        """获取章节信息"""
        try:
            # 提取章节号
            chapter_match = re.search(r'chapter_(\d+)', chapter_dir.name)
            if not chapter_match:
                return None

            chapter_number = int(chapter_match.group(1))

            # 读取章节JSON文件
            json_file = chapter_dir / f"{chapter_dir.name}.json"
            md_file = chapter_dir / f"{chapter_dir.name}.md"

            chapter_info = {
                "chapter_number": chapter_number,
                "directory": str(chapter_dir.relative_to(self.project_path)),
                "has_json": json_file.exists(),
                "has_md": md_file.exists(),
                "word_count": 0,
                "status": "outline_only"
            }

            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    chapter_info.update({
                        "title": json_data.get("metadata", {}).get("title", ""),
                        "status": json_data.get("metadata", {}).get("status", "unknown"),
                        "created_at": json_data.get("metadata", {}).get("created_at"),
                        "updated_at": json_data.get("metadata", {}).get("updated_at")
                    })

            if md_file.exists():
                content = md_file.read_text(encoding='utf-8')
                chapter_info["word_count"] = len(content)
                if chapter_info["word_count"] > 500:
                    chapter_info["status"] = "draft"

            return chapter_info

        except Exception as e:
            return None

    def _analyze_chapter_context(self, chapter_number: int, existing_chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析章节上下文"""
        context = {
            "chapter_number": chapter_number,
            "is_first_chapter": chapter_number == 1,
            "previous_chapter": None,
            "next_chapter": None,
            "story_progress": "beginning",
            "existing_chapters_count": len(existing_chapters),
            "recent_events": [],
            "active_characters": [],
            "current_plot_phase": ""
        }

        # 找到前一章和后一章
        for chapter in existing_chapters:
            if chapter["chapter_number"] == chapter_number - 1:
                context["previous_chapter"] = chapter
            elif chapter["chapter_number"] == chapter_number + 1:
                context["next_chapter"] = chapter

        # 确定故事进度阶段
        if chapter_number <= 3:
            context["story_progress"] = "beginning"
        elif chapter_number <= 10:
            context["story_progress"] = "middle"
        else:
            context["story_progress"] = "end"

        # 分析近期事件（如果有的话）
        if context["previous_chapter"]:
            context["recent_events"] = self._extract_recent_events(context["previous_chapter"])

        return context

    def _extract_recent_events(self, previous_chapter: Dict[str, Any]) -> List[str]:
        """从上一章提取近期事件"""
        events = []

        try:
            md_file = self.project_path / previous_chapter["directory"] / f"{Path(previous_chapter['directory']).name}.md"
            if md_file.exists():
                content = md_file.read_text(encoding='utf-8')

                # 简单的事件提取（可以通过AI增强）
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 10 and not line.startswith('#'):
                        # 提取看起来像事件描述的句子
                        if any(keyword in line for keyword in ['突然', '终于', '发现', '决定', '离开', '到达', '遇到']):
                            events.append(line[:100] + "..." if len(line) > 100 else line)
                            if len(events) >= 3:
                                break

        except Exception:
            pass

        return events

    def _get_existing_outline(self, chapter_number: int) -> Optional[Dict[str, Any]]:
        """获取现有梗概"""
        chapter_dir = self.draft_dir / f"chapter_{chapter_number:02d}"
        outline_file = chapter_dir / "outline.md"

        if outline_file.exists():
            try:
                content = outline_file.read_text(encoding='utf-8')
                return {
                    "exists": True,
                    "content": content,
                    "word_count": len(content),
                    "last_modified": datetime.fromtimestamp(outline_file.stat().st_mtime).isoformat()
                }
            except Exception:
                pass

        return {"exists": False}

    def _generate_chapter_suggestions(self, chapter_number: int, chapter_context: Dict[str, Any], settings_status: Dict[str, Any]) -> Dict[str, Any]:
        """生成章节创作建议"""
        suggestions = {
            "tone": "neutral",
            "pacing": "medium",
            "focus_areas": [],
            "character_development": [],
            "plot_points": [],
            "scene_count": 3,
            "estimated_word_count": "2000-3000"
        }

        # 根据章节位置确定建议
        if chapter_context["is_first_chapter"]:
            suggestions["tone"] = "introductory"
            suggestions["pacing"] = "steady"
            suggestions["focus_areas"] = ["世界观介绍", "主角登场", "初始冲突设定"]
            suggestions["character_development"] = ["主角介绍", "主要配角引入"]
            suggestions["plot_points"] = ["故事开端", "激励事件"]
        elif chapter_context["story_progress"] == "middle":
            suggestions["tone"] = "developing"
            suggestions["pacing"] = "dynamic"
            suggestions["focus_areas"] = ["冲突发展", "角色关系", "情节推进"]
            suggestions["character_development"] = ["角色成长", "关系变化"]
            suggestions["plot_points"] = ["上升情节", "中点转折"]
        else:
            suggestions["tone"] = "concluding"
            suggestions["pacing"] = "accelerating"
            suggestions["focus_areas"] = ["冲突解决", "结局铺垫", "主题深化"]
            suggestions["character_development"] = ["角色结局", "成长完成"]
            suggestions["plot_points"] = ["高潮", "下降情节", "结局"]

        return suggestions

    def _generate_outline_options(self, chapter_number: int, chapter_context: Dict[str, Any], settings_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成梗概选项"""
        options = []

        # 基于上下文生成不同的梗概选项
        if chapter_context["is_first_chapter"]:
            options.append({
                "title": "经典开局：主角登场",
                "description": "以主角的日常生活开始，通过一个事件引出故事主线",
                "key_scenes": [
                    "主角日常生活场景",
                    "激励事件发生",
                    "主角做出决定"
                ],
                "focus": "character_introduction"
            })
            options.append({
                "title": "悬念开局：事件驱动",
                "description": "以一个重要事件或悬念开场，吸引读者注意",
                "key_scenes": [
                    "重要事件发生",
                    "主角被卷入其中",
                    "留下悬念"
                ],
                "focus": "plot_hook"
            })
        elif chapter_context["story_progress"] == "middle":
            options.append({
                "title": "情节推进：冲突升级",
                "description": "在现有冲突基础上增加新的复杂因素",
                "key_scenes": [
                    "现有冲突发展",
                    "新因素引入",
                    "角色面临新挑战"
                ],
                "focus": "conflict_development"
            })
        else:
            options.append({
                "title": "高潮准备：决战前夕",
                "description": "为最终冲突做准备，各方力量集结",
                "key_scenes": [
                    "最终准备阶段",
                    "各方力量汇集",
                    "决战前夜"
                ],
                "focus": "climax_preparation"
            })

        return options

    def _identify_key_elements(self, chapter_number: int, chapter_context: Dict[str, Any]) -> List[str]:
        """识别关键元素"""
        elements = []

        if chapter_context["is_first_chapter"]:
            elements = [
                "确立主角形象和基本特征",
                "介绍故事发生的世界背景",
                "设置初始冲突或目标",
                "引入关键配角或反派"
            ]
        elif chapter_context["story_progress"] == "middle":
            elements = [
                "发展现有情节线索",
                "展示角色成长或变化",
                "增加新的冲突或挑战",
                "推进关系发展"
            ]
        else:
            elements = [
                "解决主要冲突",
                "展示角色最终成长",
                "处理次要情节线索",
                "为结局做铺垫"

            ]

        return elements

    def _determine_character_focus(self, chapter_number: int, chapter_context: Dict[str, Any]) -> List[str]:
        """确定角色焦点"""
        # 这里可以根据项目设定中的角色信息来确定
        if chapter_context["is_first_chapter"]:
            return ["主角", "关键配角"]
        elif chapter_context["story_progress"] == "middle":
            return ["主角成长", "关系发展"]
        else:
            return ["主角结局", "配角收尾"]

    def _identify_plot_advancement(self, chapter_number: int, chapter_context: Dict[str, Any]) -> List[str]:
        """识别情节推进"""
        if chapter_context["is_first_chapter"]:
            return ["建立故事世界", "设置初始目标", "引入主要冲突"]
        elif chapter_context["story_progress"] == "middle":
            return ["发展冲突", "角色成长", "情节转折"]
        else:
            return ["解决冲突", "故事高潮", "结局铺垫"]

    def _generate_scene_suggestions(self, chapter_number: int, chapter_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成场景建议"""
        scenes = []

        if chapter_context["is_first_chapter"]:
            scenes = [
                {
                    "scene_number": 1,
                    "setting": "主角日常生活环境",
                    "purpose": "展示主角性格和现状",
                    "characters": ["主角"],
                    "estimated_length": "500-800字"
                },
                {
                    "scene_number": 2,
                    "setting": "关键事件发生地",
                    "purpose": "引入主要冲突",
                    "characters": ["主角", "关键配角"],
                    "estimated_length": "800-1200字"
                },
                {
                    "scene_number": 3,
                    "setting": "决策或行动地点",
                    "purpose": "主角做出决定，开启故事",
                    "characters": ["主角"],
                    "estimated_length": "500-1000字"
                }
            ]
        else:
            # 生成通用场景结构
            scenes = [
                {
                    "scene_number": 1,
                    "setting": "承接上一章的场景",
                    "purpose": "连接情节，展示后果",
                    "characters": ["相关角色"],
                    "estimated_length": "600-1000字"
                },
                {
                    "scene_number": 2,
                    "setting": "新的发展场景",
                    "purpose": "推进主要情节",
                    "characters": ["主要角色"],
                    "estimated_length": "800-1200字"
                },
                {
                    "scene_number": 3,
                    "setting": "转折或准备场景",
                    "purpose": "为下一章做准备",
                    "characters": ["相关角色"],
                    "estimated_length": "400-800字"
                }
            ]

        return scenes

    def _create_settings_summary(self, settings_status: Dict[str, Any]) -> Dict[str, Any]:
        """创建设定摘要"""
        summary = {
            "worldview_available": settings_status["category_results"].get("worldview", {}).get("completeness_score", 0) > 10,
            "characters_available": settings_status["category_results"].get("characters", {}).get("completeness_score", 0) > 10,
            "plot_available": settings_status["category_results"].get("plot", {}).get("completeness_score", 0) > 10,
            "main_characters": [],
            "story_conflict": "",
            "world_setting": ""
        }

        # 提取主要角色信息
        characters_result = settings_status["category_results"].get("characters", {})
        for char_info in characters_result.get("details", {}).get("main_characters", []):
            summary["main_characters"].append(char_info["file"].replace(".md", ""))

        return summary

    def _generate_creation_guidance(self, chapter_number: int, chapter_context: Dict[str, Any], suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """生成创作引导"""
        guidance = {
            "ready_to_start": True,
            "recommended_workflow": [
                {
                    "step": 1,
                    "title": "确定章节梗概",
                    "description": "从建议的梗概选项中选择一个，或结合多个创建自己的梗概",
                    "estimated_time": "15-30分钟"
                },
                {
                    "step": 2,
                    "title": "细化场景大纲",
                    "description": "根据场景建议，详细规划每个场景的具体内容",
                    "estimated_time": "20-40分钟"
                },
                {
                    "step": 3,
                    "title": "开始写作",
                    "description": "按照大纲开始创作章节内容",
                    "estimated_time": "60-120分钟"
                },
                {
                    "step": 4,
                    "title": "审阅修改",
                    "description": "完成初稿后进行审阅和修改",
                    "estimated_time": "30-60分钟"
                }
            ],
            "key_considerations": [
                "确保章节内容与整体设定保持一致",
                "注意角色性格和行为的连续性",
                "控制好章节节奏和字数",
                "为下一章留下适当的悬念或伏笔"
            ],
            "success_criteria": [
                "完成预定字数目标（2000-3000字）",
                "推进了主要情节发展",
                "展现了角色成长或变化",
                "与前后章节衔接良好"
            ]
        }

        return guidance

    def save_chapter_outline(self, chapter_number: int, outline_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存章节梗概"""
        chapter_dir = self.draft_dir / f"chapter_{chapter_number:02d}"
        chapter_dir.mkdir(parents=True, exist_ok=True)

        outline_file = chapter_dir / "outline.md"
        json_file = chapter_dir / f"chapter_{chapter_number:02d}.json"

        try:
            # 保存Markdown格式的梗概
            outline_content = self._format_outline_as_markdown(outline_data)
            outline_file.write_text(outline_content, encoding='utf-8')

            # 更新或创建章节JSON文件
            chapter_metadata = {
                "metadata": {
                    "chapter": chapter_number,
                    "title": outline_data.get("title", f"第{chapter_number}章"),
                    "word_count_target": outline_data.get("estimated_word_count", "2500"),
                    "status": "outlined",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "outline": outline_data,
                "content": {
                    "sections": [],
                    "main_content": "章节梗概已保存，请根据梗概创作具体内容",
                    "dialogues": [],
                    "descriptions": [],
                    "notes": []
                }
            }

            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(chapter_metadata, f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "message": "章节梗概保存成功",
                "outline_file": str(outline_file.relative_to(self.project_path)),
                "json_file": str(json_file.relative_to(self.project_path))
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"保存梗概失败: {e}"
            }

    def _format_outline_as_markdown(self, outline_data: Dict[str, Any]) -> str:
        """将梗概数据格式化为Markdown"""
        content = []

        # 标题
        content.append(f"# {outline_data.get('title', '章节梗概')}")
        content.append("")

        # 基本信息
        content.append("## 基本信息")
        content.append(f"- **章节号**: {outline_data.get('chapter_number', '未知')}")
        content.append(f"- **预计字数**: {outline_data.get('estimated_word_count', '2000-3000字')}")
        content.append(f"- **创作重点**: {', '.join(outline_data.get('focus_areas', []))}")
        content.append("")

        # 梗概描述
        if "description" in outline_data:
            content.append("## 梗概描述")
            content.append(outline_data["description"])
            content.append("")

        # 关键场景
        if "key_scenes" in outline_data:
            content.append("## 关键场景")
            for i, scene in enumerate(outline_data["key_scenes"], 1):
                content.append(f"### 场景 {i}: {scene.get('title', f'场景{i}')}")
                content.append(f"- **地点**: {scene.get('setting', '待定')}")
                content.append(f"- **目的**: {scene.get('purpose', '待定')}")
                content.append(f"- **角色**: {', '.join(scene.get('characters', []))}")
                content.append(f"- **预计长度**: {scene.get('estimated_length', '待定')}")
                content.append("")

        # 关键元素
        if "key_elements" in outline_data:
            content.append("## 关键元素")
            for element in outline_data["key_elements"]:
                content.append(f"- {element}")
            content.append("")

        # 创作时间
        content.append(f"---")
        content.append(f"*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        return "\n".join(content)

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="章节梗概生成器")
    parser.add_argument("--project-path", default=".", help="项目路径")
    parser.add_argument("--chapter", type=int, required=True, help="章节号")
    parser.add_argument("--action", choices=["prepare", "suggest", "save"], default="prepare", help="操作类型")
    parser.add_argument("--format", choices=["json", "readable"], default="readable", help="输出格式")

    args = parser.parse_args()

    generator = ChapterOutlineGenerator(args.project_path)

    if args.action == "prepare":
        result = generator.prepare_chapter_creation(args.chapter)
    elif args.action == "suggest":
        result = generator.generate_outline_suggestions(args.chapter)
    elif args.action == "save":
        # 这里需要从文件或其他方式获取梗概数据
        print("保存功能需要结合其他工具使用")
        return

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 可读格式输出
        print("📝 章节创作准备报告")
        print("=" * 40)
        print(f"章节号: {result.get('chapter_number', args.chapter)}")
        print(f"准备状态: {'✅ 就绪' if result.get('ready_for_creation') else '❌ 未就绪'}")
        print()

        if result.get('blocking_issues'):
            print("🚫 阻塞问题:")
            for issue in result['blocking_issues']:
                print(f"  • {issue}")
            print()

        if 'creation_guidance' in result and result['creation_guidance']:
            guidance = result['creation_guidance']
            if guidance.get('recommended_workflow'):
                print("🎯 推荐工作流程:")
                for step in guidance['recommended_workflow']:
                    print(f"  {step['step']}. {step['title']} ({step['estimated_time']})")
                print()

if __name__ == "__main__":
    main()