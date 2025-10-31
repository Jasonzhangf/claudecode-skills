#!/usr/bin/env python3
"""
交互式小说生成器
智能状态检查、进度判断和用户交互的完整小说生成管理器
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from chapter_generator import ChapterGenerator
from outline_manager import OutlineManager
from claude_integration import ClaudeIntegration

class NovelGenerator:
    """交互式小说生成器"""

    def __init__(self, project_path: str = None):
        if project_path is None:
            self.project_path = Path.cwd()
        else:
            self.project_path = Path(project_path)

        # 初始化组件
        self.chapter_generator = ChapterGenerator(str(self.project_path))
        self.outline_manager = OutlineManager(str(self.project_path))
        self.claude_integration = ClaudeIntegration(str(self.project_path))

    def check_project_status(self) -> Dict[str, Any]:
        """检查项目整体状态"""
        status = {
            "project_path": str(self.project_path),
            "project_name": self.project_path.name,
            "check_time": datetime.now().isoformat(),
            "components": {}
        }

        # 1. 检查大纲状态
        outline_status = self.outline_manager.get_outline_status()
        status["components"]["outlines"] = outline_status

        # 2. 检查章节状态
        chapter_status = self._check_chapter_status()
        status["components"]["chapters"] = chapter_status

        # 3. 检查设定状态
        settings_status = self._check_settings_status()
        status["components"]["settings"] = settings_status

        # 4. 计算整体进度
        status["overall_status"] = self._calculate_overall_status(status["components"])

        return status

    def get_current_progress(self) -> Dict[str, Any]:
        """获取当前创作进度"""
        # 检查现有章节
        draft_dir = self.project_path / "draft" / "chapters"
        existing_chapters = []

        if draft_dir.exists():
            for chapter_dir in sorted(draft_dir.glob("chapter_*")):
                try:
                    chapter_num = int(chapter_dir.name.split('_')[1])
                    json_file = chapter_dir / f"chapter_{chapter_num:02d}.json"
                    md_file = chapter_dir / f"chapter_{chapter_num:02d}.md"

                    if json_file.exists() and md_file.exists():
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        existing_chapters.append({
                            "chapter": chapter_num,
                            "title": data.get("metadata", {}).get("title", f"第{chapter_num}章"),
                            "word_count": data.get("metadata", {}).get("word_count", 0),
                            "status": data.get("metadata", {}).get("status", "unknown"),
                            "updated_at": data.get("metadata", {}).get("updated_at", "")
                        })
                except:
                    continue

        # 检查大纲规划
        outline_status = self.outline_manager.get_outline_status()
        planned_chapters = outline_status.get("outline_status", {}).get("chapter_numbers", [])

        # 计算进度
        current_chapter = len(existing_chapters) + 1 if existing_chapters else 1
        total_planned = len(planned_chapters) if planned_chapters else 0

        return {
            "current_chapter": current_chapter,
            "existing_chapters": existing_chapters,
            "total_planned": total_planned,
            "completion_percentage": (len(existing_chapters) / total_planned * 100) if total_planned > 0 else 0,
            "next_action": "create_outline" if current_chapter not in planned_chapters else "generate_chapter"
        }

    def check_generation_prerequisites(self, chapter_number: int) -> Dict[str, Any]:
        """检查章节生成的先决条件"""
        missing_items = []
        suggestions = []

        # 1. 检查设定文件
        required_settings = [
            ("worldview", self.project_path / "settings" / "worldview" / "world_setting.md"),
            ("characters", self.project_path / "settings" / "characters" / "character_relations.md"),
            ("environments", self.project_path / "settings" / "environments" / "locations.md"),
            ("plot", self.project_path / "settings" / "plot" / "main_plot.md"),
            ("style", self.project_path / "settings" / "writing_style" / "narrative_style.md")
        ]

        for setting_name, file_path in required_settings:
            if not file_path.exists() or file_path.stat().st_size == 0:
                missing_items.append(f"{setting_name}设定文件缺失或为空")
                suggestions.append(f"请完善 {setting_name} 设定")

        # 2. 检查章节大纲
        outline_file = (self.project_path / "settings" / "outlines" / "chapters" /
                       f"chapter_{chapter_number:02d}_outline.md")

        if not outline_file.exists():
            missing_items.append(f"第{chapter_number}章大纲缺失")
            suggestions.append(f"请创建第{chapter_number}章大纲：outline create-chapter {chapter_number}")
        elif outline_file.stat().st_size < 100:
            missing_items.append(f"第{chapter_number}章大纲内容过少")
            suggestions.append(f"请完善第{chapter_number}章大纲内容")

        # 3. 检查前序章节（除第一章外）
        if chapter_number > 1:
            prev_chapter_file = (self.project_path / "draft" / "chapters" /
                               f"chapter_{chapter_number-1:02d}" /
                               f"chapter_{chapter_number-1:02d}.json")
            if not prev_chapter_file.exists():
                missing_items.append(f"第{chapter_number-1}章尚未完成")
                suggestions.append(f"请先生成第{chapter_number-1}章")

        return {
            "ready": len(missing_items) == 0,
            "missing_items": missing_items,
            "suggestions": suggestions,
            "chapter": chapter_number
        }

    def interactive_generation_session(self) -> Dict[str, Any]:
        """交互式生成会话"""
        print("🎨 NovelGen - 交互式小说生成器")
        print("=" * 50)

        # 1. 检查项目状态
        print("📊 检查项目状态...")
        project_status = self.check_project_status()

        if project_status["overall_status"] != "complete":
            print("⚠️  项目状态不完整:")
            for component, status in project_status["components"].items():
                if status.get("status") != "success":
                    print(f"   ❌ {component}: {status.get('message', '状态未知')}")
        else:
            print("✅ 项目状态良好")

        # 2. 获取当前进度
        print("\n📈 分析创作进度...")
        progress = self.get_current_progress()

        print(f"   📚 当前章节: 第{progress['current_chapter']}章")
        print(f"   ✅ 已完成章节: {len(progress['existing_chapters'])}章")
        print(f"   📋 规划章节: {progress['total_planned']}章")
        print(f"   📊 完成进度: {progress['completion_percentage']:.1f}%")

        if progress['existing_chapters']:
            print("\n   📖 已完成章节列表:")
            for chapter in progress['existing_chapters'][-5:]:  # 显示最近5章
                print(f"      第{chapter['chapter']}章: {chapter['title']} ({chapter['word_count']}字)")

        # 3. 检查下一步操作
        current_chapter = progress['current_chapter']

        if progress['next_action'] == 'create_outline':
            print(f"\n📝 下一步: 需要创建第{current_chapter}章大纲")
            if self._ask_yes_no(f"是否创建第{current_chapter}章大纲？"):
                return self._create_chapter_outline_interactive(current_chapter)
            else:
                return {"status": "cancelled", "message": "用户取消创建大纲"}

        # 4. 检查生成先决条件
        print(f"\n🔍 检查第{current_chapter}章生成条件...")
        prerequisites = self.check_generation_prerequisites(current_chapter)

        if not prerequisites["ready"]:
            print("❌ 生成条件不满足:")
            for item in prerequisites["missing_items"]:
                print(f"   • {item}")

            print("\n💡 建议:")
            for suggestion in prerequisites["suggestions"]:
                print(f"   • {suggestion}")

            return {
                "status": "prerequisites_not_met",
                "missing_items": prerequisites["missing_items"],
                "suggestions": prerequisites["suggestions"]
            }

        # 5. 确认生成
        print(f"\n🚀 准备生成第{current_chapter}章")
        print(f"   📋 将使用大纲: settings/outlines/chapters/chapter_{current_chapter:02d}_outline.md")
        print(f"   🤖 生成方式: Claude Skill")

        if self._ask_yes_no("确认准备第{current_chapter}章生成上下文？"):
            return self._generate_chapter_interactive(current_chapter)
        else:
            return {"status": "cancelled", "message": "用户取消生成"}

    def _create_chapter_outline_interactive(self, chapter_number: int) -> Dict[str, Any]:
        """交互式创建章节大纲"""
        print(f"\n📝 创建第{chapter_number}章大纲")

        # 获取章节标题
        title = input("请输入章节标题 (留空使用默认): ").strip()
        if not title:
            title = f"第{chapter_number}章"

        # 创建大纲
        result = self.outline_manager.create_chapter_outline(chapter_number, title)

        if result["status"] == "success":
            print(f"✅ 第{chapter_number}章大纲创建成功")
            print(f"📁 文件位置: {result['file_path']}")

            # 询问是否现在编辑大纲
            if self._ask_yes_no("是否现在编辑大纲内容？"):
                print(f"📝 请编辑文件: {result['file_path']}")
                input("编辑完成后按回车键继续...")

            return {"status": "success", "message": "大纲创建完成", "file_path": result["file_path"]}
        else:
            print(f"❌ 大纲创建失败: {result['message']}")
            return result

    def _generate_chapter_interactive(self, chapter_number: int) -> Dict[str, Any]:
        """交互式生成章节"""
        print(f"\n✍️ 准备生成第{chapter_number}章内容...")

        # 生成上下文
        result = self.chapter_generator.generate_chapter(chapter_number)

        if result["status"] == "ready_for_claude":
            print("✅ 上下文准备完成!")
            print(f"📊 上下文长度: {result.get('context_length', 0)}字符")
            print(f"📁 上下文文件: {result.get('prompt_file', '未知')}")
            print(f"🎯 下一步: 请Claude基于上下文生成内容")

            # 显示上下文预览
            context = result.get('context', '')
            if context:
                preview_lines = context.split('\n')[:15]
                print("\n📖 上下文预览:")
                for line in preview_lines:
                    if line.strip():
                        print(f"   {line}")
                if len(context.split('\n')) > 15:
                    print("   ...")

            print(f"\n🤖 请Claude基于以上上下文生成第{chapter_number}章完整内容")
            print(f"💡 要求: 字数2000-3000字，遵循大纲，保持人物性格一致性")

            return {
                "status": "context_ready",
                "chapter": chapter_number,
                "context": result.get('context', ''),
                "prompt_file": result.get('prompt_file', ''),
                "next_step": "请Claude生成章节内容",
                "generation_instructions": {
                    "word_count_target": "2000-3000字",
                    "follow_outline": True,
                    "maintain_consistency": True,
                    "include_dialogue": True,
                    "include_descriptions": True
                }
            }
        else:
            print(f"❌ 上下文准备失败: {result.get('message', '未知错误')}")
            return result

    def _ask_yes_no(self, question: str) -> bool:
        """询问用户是/否问题"""
        while True:
            response = input(f"{question} (y/n): ").strip().lower()
            if response in ['y', 'yes', '是', '好']:
                return True
            elif response in ['n', 'no', '否', '不']:
                return False
            else:
                print("请输入 y(是) 或 n(否)")

    def _check_chapter_status(self) -> Dict[str, Any]:
        """检查章节状态"""
        draft_dir = self.project_path / "draft" / "chapters"

        if not draft_dir.exists():
            return {
                "status": "no_chapters",
                "message": "尚未创建任何章节",
                "existing_chapters": []
            }

        chapters = []
        for chapter_dir in sorted(draft_dir.glob("chapter_*")):
            try:
                chapter_num = int(chapter_dir.name.split('_')[1])
                json_file = chapter_dir / f"chapter_{chapter_num:02d}.json"

                if json_file.exists():
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    chapters.append({
                        "chapter": chapter_num,
                        "title": data.get("metadata", {}).get("title", ""),
                        "word_count": data.get("metadata", {}).get("word_count", 0),
                        "status": data.get("metadata", {}).get("status", "")
                    })
            except:
                continue

        return {
            "status": "success",
            "message": f"找到{len(chapters)}个章节",
            "existing_chapters": chapters,
            "total_chapters": len(chapters)
        }

    def _check_settings_status(self) -> Dict[str, Any]:
        """检查设定状态"""
        required_files = [
            ("worldview", "settings/worldview/world_setting.md"),
            ("characters", "settings/characters/character_relations.md"),
            ("environments", "settings/environments/locations.md"),
            ("plot", "settings/plot/main_plot.md"),
            ("style", "settings/writing_style/narrative_style.md")
        ]

        missing_files = []
        existing_files = []

        for setting_name, file_path in required_files:
            full_path = self.project_path / file_path
            if full_path.exists() and full_path.stat().st_size > 0:
                existing_files.append(setting_name)
            else:
                missing_files.append(setting_name)

        return {
            "status": "success" if not missing_files else "incomplete",
            "message": f"设定文件: {len(existing_files)}/{len(required_files)}完整",
            "existing_settings": existing_files,
            "missing_settings": missing_files
        }

    def _calculate_overall_status(self, components: Dict[str, Any]) -> str:
        """计算整体状态"""
        statuses = [comp.get("status", "unknown") for comp in components.values()]

        if all(status == "success" for status in statuses):
            return "complete"
        elif any(status == "error" for status in statuses):
            return "error"
        else:
            return "incomplete"

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="交互式小说生成器")
    parser.add_argument("--project-path", help="项目路径")
    parser.add_argument("--auto", action="store_true", help="自动模式，跳过交互")
    parser.add_argument("--chapter", type=int, help="指定章节号")

    args = parser.parse_args()

    try:
        generator = NovelGenerator(args.project_path)

        if args.auto and args.chapter:
            # 自动生成指定章节
            result = generator.chapter_generator.generate_chapter(args.chapter)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 交互式会话
            result = generator.interactive_generation_session()

            if result["status"] == "success":
                print("\n🎉 操作完成!")
            elif result["status"] == "cancelled":
                print("\n⏹️  操作已取消")
            else:
                print(f"\n❌ 操作失败: {result.get('message', '未知错误')}")

    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序错误: {str(e)}")

if __name__ == "__main__":
    main()