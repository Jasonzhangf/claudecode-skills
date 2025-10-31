#!/usr/bin/env python3
"""
Claude技能集成模块
处理Claude生成的内容保存和章节管理
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class ClaudeIntegration:
    """Claude技能集成管理器"""

    def __init__(self, project_path: str = None):
        if project_path is None:
            self.project_path = Path.cwd()
        else:
            self.project_path = Path(project_path)

        self.draft_dir = self.project_path / "draft" / "chapters"

    def save_claude_generated_content(self, chapter_number: int, content: str, title: str = None) -> Dict[str, Any]:
        """保存Claude生成的章节内容"""
        try:
            # 确保章节目录存在
            chapter_dir = self.draft_dir / f"chapter_{chapter_number:02d}"
            chapter_dir.mkdir(parents=True, exist_ok=True)

            # 准备文件路径
            json_file = chapter_dir / f"chapter_{chapter_number:02d}.json"
            md_file = chapter_dir / f"chapter_{chapter_number:02d}.md"

            # 生成章节标题（如果没有提供）
            if not title:
                title = f"第{chapter_number}章"

            # 创建时间戳
            current_time = datetime.now().isoformat()

            # 准备JSON数据
            json_data = {
                "metadata": {
                    "chapter": chapter_number,
                    "title": title,
                    "word_count": len(content),
                    "status": "completed",
                    "created_at": current_time,
                    "updated_at": current_time,
                    "version": "1.0",
                    "generated_by": "claude_skill"
                },
                "content": {
                    "sections": self._parse_content_sections(content),
                    "main_content": content,
                    "dialogues": self._extract_dialogues(content),
                    "descriptions": self._extract_descriptions(content),
                    "notes": []
                },
                "context": {
                    "previous_chapter_summary": "",
                    "current_chapter_focus": title,
                    "next_chapter_preview": ""
                },
                "editing": {
                    "last_modified_by": "claude_skill",
                    "edit_history": [{
                        "timestamp": current_time,
                        "action": "initial_generation",
                        "word_count": len(content)
                    }],
                    "word_target": 2000,
                    "progress_percentage": min(100, (len(content) / 2000) * 100)
                }
            }

            # 保存JSON文件
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            # 保存MD文件
            md_content = self._create_md_content(chapter_number, title, content, current_time)
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)

            return {
                "status": "success",
                "chapter": chapter_number,
                "title": title,
                "word_count": len(content),
                "json_file": str(json_file),
                "md_file": str(md_file),
                "message": f"第{chapter_number}章内容保存成功"
            }

        except Exception as e:
            return {
                "status": "error",
                "chapter": chapter_number,
                "message": f"保存内容失败: {str(e)}"
            }

    def _parse_content_sections(self, content: str) -> list:
        """解析内容章节"""
        sections = []
        lines = content.split('\n')
        current_section = None

        for line in lines:
            if line.startswith('#'):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "type": "heading",
                    "content": line,
                    "subsections": []
                }
            elif current_section:
                if line.strip():
                    current_section["subsections"].append(line.strip())

        if current_section:
            sections.append(current_section)

        return sections

    def _extract_dialogues(self, content: str) -> list:
        """提取对话内容"""
        dialogues = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            if '"' in line and ('说' in line or '道' in line or '问' in line or '答' in line):
                dialogues.append({
                    "line_number": i + 1,
                    "content": line.strip(),
                    "type": "dialogue"
                })

        return dialogues

    def _extract_descriptions(self, content: str) -> list:
        """提取描述内容"""
        descriptions = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            if len(line) > 20 and not line.startswith('#') and '"' not in line:
                # 简单判断是否为描述性内容
                if any(word in line for word in ['的', '着', '了', '是', '有', '在', '从', '到']):
                    descriptions.append({
                        "line_number": i + 1,
                        "content": line,
                        "type": "description"
                    })

        return descriptions

    def _create_md_content(self, chapter_number: int, title: str, content: str, timestamp: str) -> str:
        """创建Markdown格式内容"""
        md_content = f"""---
chapter: {chapter_number}
title: {title}
word_count: {len(content)}
status: completed
created_at: {timestamp}
updated_at: {timestamp}
version: 1.0
generated_by: claude_skill
---

# {title}

{content}

---
*章节生成时间: {timestamp}*
*字数统计: {len(content)}*
*生成方式: Claude Skill自动生成*
"""
        return md_content

    def get_chapter_summary(self, chapter_number: int) -> Dict[str, Any]:
        """获取章节摘要信息"""
        try:
            chapter_dir = self.draft_dir / f"chapter_{chapter_number:02d}"
            json_file = chapter_dir / f"chapter_{chapter_number:02d}.json"

            if not json_file.exists():
                return {"status": "not_found", "message": f"第{chapter_number}章不存在"}

            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            metadata = data.get("metadata", {})
            content = data.get("content", {})

            return {
                "status": "success",
                "chapter": chapter_number,
                "title": metadata.get("title", f"第{chapter_number}章"),
                "word_count": metadata.get("word_count", 0),
                "status": metadata.get("status", "unknown"),
                "created_at": metadata.get("created_at", ""),
                "generated_by": metadata.get("generated_by", "unknown"),
                "sections_count": len(content.get("sections", [])),
                "dialogues_count": len(content.get("dialogues", [])),
                "descriptions_count": len(content.get("descriptions", []))
            }

        except Exception as e:
            return {"status": "error", "message": f"读取章节信息失败: {str(e)}"}

    def list_all_chapters(self) -> Dict[str, Any]:
        """列出所有章节"""
        try:
            chapters = []
            if self.draft_dir.exists():
                for chapter_dir in sorted(self.draft_dir.glob("chapter_*")):
                    try:
                        chapter_num = int(chapter_dir.name.split('_')[1])
                        summary = self.get_chapter_summary(chapter_num)
                        if summary["status"] == "success":
                            chapters.append(summary)
                    except:
                        continue

            return {
                "status": "success",
                "chapters": chapters,
                "total_chapters": len(chapters),
                "total_words": sum(ch.get("word_count", 0) for ch in chapters)
            }

        except Exception as e:
            return {"status": "error", "message": f"列出章节失败: {str(e)}"}

def main():
    """命令行接口"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Claude技能集成管理器")
    parser.add_argument("--project-path", help="项目路径")
    parser.add_argument("--chapter", type=int, help="章节号")
    parser.add_argument("--title", help="章节标题")
    parser.add_argument("--content", help="章节内容")
    parser.add_argument("--list", action="store_true", help="列出所有章节")
    parser.add_argument("--summary", type=int, help="获取章节摘要")

    args = parser.parse_args()

    integration = ClaudeIntegration(args.project_path)

    if args.list:
        result = integration.list_all_chapters()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.summary:
        result = integration.get_chapter_summary(args.summary)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.chapter and args.content:
        result = integration.save_claude_generated_content(
            args.chapter,
            args.content,
            args.title
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print("请提供具体操作参数，使用 --help 查看帮助")

if __name__ == "__main__":
    main()