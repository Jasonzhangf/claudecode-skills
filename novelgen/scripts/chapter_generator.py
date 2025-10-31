#!/usr/bin/env python3
"""
小说生成器 - 章节生成器
负责智能章节内容生成，包含完整的7步流程
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from context_manager import ContextManager
from session_manager import SessionManager
from compression_engine import CompressionEngine

class ChapterGenerator:
    """章节生成器，实现完整的小说生成流程"""

    def __init__(self, project_path: str = None):
        if project_path is None:
            self.project_path = Path.cwd()
        else:
            self.project_path = Path(project_path)

        self.draft_dir = self.project_path / "draft"
        self.settings_dir = self.project_path / "settings"
        self.system_dir = self.project_path / "system"

        # 初始化管理器
        self.context_manager = ContextManager(project_path)
        self.session_manager = SessionManager(project_path)
        self.compression_engine = CompressionEngine(project_path)

    def generate_chapter(self, chapter_number: int, force: bool = False) -> Dict[str, Any]:
        """生成章节内容 - 完整的7步流程"""
        try:
            print(f"🚀 开始生成第{chapter_number}章...")

            # 步骤1: 检查生成前提条件
            prerequisites = self._check_generation_prerequisites(chapter_number)
            if not prerequisites["ready"] and not force:
                return {
                    "status": "error",
                    "message": "生成前提条件未满足",
                    "missing_items": prerequisites["missing_items"],
                    "suggestions": prerequisites["suggestions"]
                }

            # 步骤2: 构建完整上下文
            context_result = self._build_full_context(chapter_number)
            if context_result["status"] != "success":
                return context_result

            # 步骤3: 生成章节内容
            generation_result = self._generate_chapter_content(chapter_number, context_result["context"])

            return generation_result

        except Exception as e:
            return {
                "status": "error",
                "message": f"生成章节失败: {e}"
            }

    def _check_generation_prerequisites(self, chapter_number: int) -> Dict[str, Any]:
        """检查生成前提条件"""
        missing_items = []
        suggestions = []

        # 1. 检查设定完整性
        settings_check = self._check_settings_completeness()
        if not settings_check["complete"]:
            missing_items.extend(settings_check["missing"])
            suggestions.extend(settings_check["suggestions"])

        # 2. 检查前序章节
        if chapter_number > 1:
            previous_chapter = chapter_number - 1
            prev_exists = self._chapter_exists(previous_chapter)
            if not prev_exists:
                missing_items.append(f"第{previous_chapter}章不存在")
                suggestions.append(f"请先完成第{previous_chapter}章")

        # 3. 检查当前章节情节简介
        outline_check = self._check_chapter_outline(chapter_number)
        if not outline_check["exists"]:
            missing_items.append(f"第{chapter_number}章情节简介缺失")
            suggestions.append("请提供当前章节的情节简介和大纲")

        return {
            "ready": len(missing_items) == 0,
            "missing_items": missing_items,
            "suggestions": suggestions
        }

    def _check_settings_completeness(self) -> Dict[str, Any]:
        """检查设定完整性"""
        required_settings = [
            ("worldview", self.settings_dir / "worldview" / "world_setting.md"),
            ("characters", self.settings_dir / "characters" / "character_relations.md"),
            ("environments", self.settings_dir / "environments" / "locations.md"),
            ("plot", self.settings_dir / "plot" / "main_plot.md"),
            ("style", self.settings_dir / "writing_style" / "narrative_style.md")
        ]

        missing = []
        suggestions = []

        for setting_name, file_path in required_settings:
            if not file_path.exists() or file_path.stat().st_size < 100:
                missing.append(setting_name)
                suggestions.append(f"请完善{setting_name}设定")

        return {
            "complete": len(missing) == 0,
            "missing": missing,
            "suggestions": suggestions
        }

    def _check_chapter_outline(self, chapter_number: int) -> Dict[str, Any]:
        """检查章节大纲"""
        # 优先检查新的独立大纲目录
        outlines_dir = self.settings_dir / "outlines" / "chapters"
        outline_file = outlines_dir / f"chapter_{chapter_number:02d}_outline.md"

        if outline_file.exists():
            return {
                "exists": True,
                "file_path": str(outline_file),
                "source": "dedicated_outline"
            }

        # 回退到旧的plot目录
        outline_file = self.settings_dir / "plot" / f"chapter_{chapter_number:02d}_outline.md"

        return {
            "exists": outline_file.exists(),
            "file_path": str(outline_file),
            "source": "plot_outline"
        }

    def _chapter_exists(self, chapter_number: int) -> bool:
        """检查章节是否存在"""
        chapter_file = (self.draft_dir / "chapters" /
                       f"chapter_{chapter_number:02d}" / f"chapter_{chapter_number:02d}.json")
        return chapter_file.exists()

    def _build_full_context(self, chapter_number: int) -> Dict[str, Any]:
        """构建完整上下文"""
        print(f"📚 步骤1/2: 构建上下文...")

        context_components = []

        # 1. 加载各种设定
        print("   📋 加载设定...")
        settings_context = self._load_settings_context()
        context_components.extend(settings_context["components"])

        # 2. 加载前序章节压缩提示
        if chapter_number > 1:
            print("   🗜️ 加载前序章节压缩提示...")
            compression_context = self._load_compression_context(chapter_number)
            context_components.extend(compression_context["components"])

        # 3. 加载上一章全文
        if chapter_number > 1:
            print("   📄 加载上一章全文...")
            prev_chapter_context = self._load_previous_chapter_full(chapter_number - 1)
            if prev_chapter_context:
                context_components.append(prev_chapter_context)

        # 4. 加载当前章节情节简介和大纲
        print("   📝 加载当前章节大纲...")
        chapter_outline = self._load_chapter_outline(chapter_number)
        if chapter_outline:
            context_components.append(chapter_outline)

        # 5. 组装最终上下文
        final_context = self._assemble_context(context_components, chapter_number)

        return {
            "status": "success",
            "context": final_context,
            "components_count": len(context_components)
        }

    def _load_settings_context(self) -> Dict[str, Any]:
        """加载设定数据上下文"""
        components = []

        setting_files = [
            ("worldview", self.settings_dir / "worldview" / "world_setting.md"),
            ("characters", self.settings_dir / "characters" / "character_relations.md"),
            ("environments", self.settings_dir / "environments" / "locations.md"),
            ("plot", self.settings_dir / "plot" / "main_plot.md"),
            ("style", self.settings_dir / "writing_style" / "narrative_style.md")
        ]

        for setting_type, file_path in setting_files:
            if file_path.exists() and file_path.stat().st_size > 0:
                content = file_path.read_text(encoding='utf-8')
                components.append({
                    "type": "setting",
                    "setting_type": setting_type,
                    "content": content
                })

        return {"components": components}

    def _load_compression_context(self, chapter: int) -> Dict[str, Any]:
        """加载压缩的历史章节上下文"""
        components = []

        # 加载近期压缩（最近10章）
        recent_start = max(1, chapter - 10)
        for ch in range(recent_start, chapter):
            compression_file = (self.draft_dir / "chapters" / f"chapter_{ch:02d}" /
                              "compression" / "recent" / "plot_summary.md")
            if compression_file.exists():
                content = compression_file.read_text(encoding='utf-8')
                components.append({
                    "type": "recent_compression",
                    "chapter": ch,
                    "content": content
                })

        return {"components": components}

    def _load_previous_chapter_full(self, previous_chapter: int) -> Optional[Dict[str, Any]]:
        """加载上一章全文"""
        chapter_file = (self.draft_dir / "chapters" / f"chapter_{previous_chapter:02d}" /
                       f"chapter_{previous_chapter:02d}.md")

        if chapter_file.exists():
            content = chapter_file.read_text(encoding='utf-8')

            # 提取正文内容（去掉FrontMatter）
            if content.startswith('---\n'):
                parts = content.split('---\n', 2)
                if len(parts) >= 3:
                    content = parts[2].strip()

            return {
                "type": "previous_chapter_full",
                "chapter": previous_chapter,
                "content": content
            }

        return None

    def _load_chapter_outline(self, chapter_number: int) -> Optional[Dict[str, Any]]:
        """加载章节大纲"""
        # 优先从新的独立大纲目录加载
        outlines_dir = self.settings_dir / "outlines" / "chapters"
        outline_file = outlines_dir / f"chapter_{chapter_number:02d}_outline.md"

        if outline_file.exists():
            content = outline_file.read_text(encoding='utf-8')
            return {
                "type": "chapter_outline",
                "chapter": chapter_number,
                "content": content,
                "source": "dedicated_outline"
            }

        # 回退到旧的plot目录
        outline_file = self.settings_dir / "plot" / f"chapter_{chapter_number:02d}_outline.md"

        if outline_file.exists():
            content = outline_file.read_text(encoding='utf-8')
            return {
                "type": "chapter_outline",
                "chapter": chapter_number,
                "content": content,
                "source": "plot_outline"
            }

        # 尝试从主情节文件中提取
        main_plot_file = self.settings_dir / "plot" / "main_plot.md"
        if main_plot_file.exists():
            content = main_plot_file.read_text(encoding='utf-8')
            # 简单提取：查找包含章节号的内容
            chapter_pattern = f"第{chapter_number}章"
            lines = content.split('\n')
            chapter_content = []

            for i, line in enumerate(lines):
                if chapter_pattern in line:
                    # 提取从该行开始的段落
                    chapter_content.append(line)
                    j = i + 1
                    while j < len(lines) and lines[j].strip():
                        chapter_content.append(lines[j])
                        j += 1
                    break

            if chapter_content:
                return {
                    "type": "chapter_outline",
                    "chapter": chapter_number,
                    "content": '\n'.join(chapter_content)
                }

        return None

    def _assemble_context(self, components: List[Dict[str, Any]], chapter: int) -> str:
        """组装最终上下文"""
        context_parts = [f"# 第{chapter}章生成上下文\n"]
        context_parts.append("## 设定信息\n")

        # 按优先级排序组件
        sorted_components = sorted(components, key=lambda x: self._get_component_priority(x["type"]))

        for component in sorted_components:
            if component["type"] == "setting":
                context_parts.append(f"### {component['setting_type']}设定\n{component['content']}\n")
            elif component["type"] == "previous_chapter_full":
                context_parts.append(f"## 上一章全文（第{component['chapter']}章）\n{component['content']}\n")
            elif component["type"] == "recent_compression":
                context_parts.append(f"## 第{component['chapter']}章摘要\n{component['content']}\n")
            elif component["type"] == "chapter_outline":
                context_parts.append(f"## 第{component['chapter']}章大纲\n{component['content']}\n")

        context_parts.append("\n## 生成要求\n")
        context_parts.append("基于以上上下文信息，请生成第{}章的完整内容。要求：\n".format(chapter))
        context_parts.append("1. 保持与前面章节的连贯性\n")
        context_parts.append("2. 遵循已设定的世界观和人物性格\n")
        context_parts.append("3. 按照大纲推进情节发展\n")
        context_parts.append("4. 字数控制在2000-3000字之间\n")

        return "\n".join(context_parts)

    def _get_component_priority(self, component_type: str) -> int:
        """获取组件优先级"""
        priority = {
            "previous_chapter_full": 1,
            "chapter_outline": 2,
            "setting": 3,
            "recent_compression": 4
        }
        return priority.get(component_type, 10)

    def _generate_chapter_content(self, chapter_number: int, context: str) -> Dict[str, Any]:
        """准备章节生成上下文"""
        print(f"✍️ 步骤2/2: 准备第{chapter_number}章生成上下文...")

        # 保存prompt文件
        prompt_file = self.system_dir / "chapter_generation_prompt.md"
        prompt_file.write_text(context, encoding='utf-8')

        return {
            "status": "ready_for_claude",
            "chapter": chapter_number,
            "prompt_file": str(prompt_file),
            "context_length": len(context),
            "context": context,
            "message": f"第{chapter_number}章上下文已准备完成，请Claude生成内容",
            "next_step": "请基于以上上下文生成完整的章节内容"
        }

    def _call_ai_model(self, prompt: str) -> Optional[str]:
        """调用AI模型生成章节内容"""
        try:
            # 使用AI适配器进行内容生成
            from ai_adapter import AIAdapter

            # 创建AI适配器（自动选择可用模型）
            adapter = AIAdapter(model_type="auto")

            # 获取模型信息
            model_info = adapter.get_model_info()
            print(f"🤖 使用AI模型: {model_info['type']} ({model_info['model']})")

            # 生成内容
            content = adapter.generate_content(
                prompt,
                max_tokens=4000,
                temperature=0.7
            )

            if content:
                print("✅ AI模型调用成功")
                return content
            else:
                print("❌ AI模型未返回内容")
                return None

        except Exception as e:
            print(f"❌ AI模型调用失败: {str(e)}")
            return None

    def _save_chapter_content(self, chapter_number: int, content: str) -> Dict[str, Any]:
        """保存章节内容到文件"""
        try:
            from chapter_manager import ChapterManager
            chapter_manager = ChapterManager(str(self.project_path))

            # 使用chapter_manager保存内容
            result = chapter_manager.update_chapter_content(chapter_number, content)

            return {
                "status": "success",
                "json_file": result.get("json_file"),
                "md_file": result.get("md_file"),
                "word_count": len(content)
            }

        except Exception as e:
            print(f"❌ 保存章节内容失败: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="小说生成器章节生成器")
    parser.add_argument("--chapter", type=int, required=True, help="章节号")
    parser.add_argument("--force", action="store_true", help="强制生成，跳过检查")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    generator = ChapterGenerator(args.project_path)
    result = generator.generate_chapter(args.chapter, args.force)

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()