#!/usr/bin/env python3
"""
小说生成器 - 章节管理器
负责章节创建、跳转、索引和状态管理
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from session_manager import SessionManager

class ChapterManager:
    """章节管理器，处理章节相关的所有操作"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.draft_dir = self.project_path / "draft"           # 草稿目录（写作中的章节）
        self.manuscript_dir = self.project_path / "manuscript" # 最终稿目录（完成的章节）
        self.system_dir = self.project_path / "system"
        self.progress_dir = self.project_path / "progress"

        # 初始化相关管理器
        self.session_manager = SessionManager(project_path)

        # 确保目录存在
        self._ensure_directories()

        # 章节索引文件
        self.chapter_index_file = self.system_dir / "chapter_index.json"

    def _ensure_directories(self):
        """确保必要目录存在"""
        directories = [
            self.draft_dir,
            self.draft_dir / "chapters",               # 草稿章节目录
            self.draft_dir / "chapter_drafts",
            self.draft_dir / "generation_cache",
            self.draft_dir / "working_space",
            self.manuscript_dir,
            self.manuscript_dir / "completed_chapters", # 完成章节目录
            self.manuscript_dir / "context_snapshots",
            self.progress_dir
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def create_chapter(self, chapter_number: int, title: str = None,
                      context_summary: str = None) -> Dict[str, Any]:
        """创建新章节"""
        try:
            # 验证章节号
            if chapter_number <= 0:
                return {
                    "status": "error",
                    "message": "章节号必须大于0"
                }

            # 检查章节是否已存在
            if self._chapter_exists(chapter_number):
                return {
                    "status": "error",
                    "message": f"第{chapter_number}章已存在"
                }

            # 创建章节目录（在draft目录下）
            chapter_dir = self.draft_dir / "chapters" / f"chapter_{chapter_number:02d}"
            chapter_dir.mkdir(parents=True, exist_ok=True)

            # 创建章节文件（双版本在同一目录）
            json_file = chapter_dir / f"chapter_{chapter_number:02d}.json"
            md_file = chapter_dir / f"chapter_{chapter_number:02d}.md"

            # 创建压缩子目录
            compression_dir = chapter_dir / "compression"
            compression_dir.mkdir(parents=True, exist_ok=True)
            for compression_type in ["recent", "medium", "long_term"]:
                (compression_dir / compression_type).mkdir(exist_ok=True)

            # 生成章节标题
            if not title:
                title = f"第{chapter_number}章"

            # 创建章节数据
            chapter_data = self._create_chapter_data(chapter_number, title, context_summary)

            # 保存JSON版本
            json_file.write_text(json.dumps(chapter_data, ensure_ascii=False, indent=2), encoding='utf-8')

            # 创建并保存MD版本
            md_content = self._create_chapter_md_content(chapter_data)
            md_file.write_text(md_content, encoding='utf-8')

            return {
                "status": "success",
                "chapter": chapter_number,
                "title": title,
                "json_file": str(json_file),
                "md_file": str(md_file),
                "message": f"成功创建第{chapter_number}章"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"创建章节失败: {e}"
            }

    def update_chapter_content(self, chapter_number: int, content: str,
                             metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """更新章节内容（同时更新JSON和MD版本）"""
        try:
            # 章节目录（在draft目录下）
            chapter_dir = self.draft_dir / "chapters" / f"chapter_{chapter_number:02d}"

            # 两个版本的文件路径
            json_file = chapter_dir / f"chapter_{chapter_number:02d}.json"
            md_file = chapter_dir / f"chapter_{chapter_number:02d}.md"

            if not json_file.exists():
                return {
                    "status": "error",
                    "message": f"第{chapter_number}章不存在"
                }

            # 读取现有JSON数据
            existing_data = json.loads(json_file.read_text(encoding='utf-8'))

            # 更新JSON版本内容
            existing_data["content"]["main_content"] = content
            existing_data["metadata"]["updated_at"] = datetime.now().isoformat()
            existing_data["metadata"]["word_count"] = len(content)

            # 合并元数据
            if metadata:
                existing_data["metadata"].update(metadata)

            # 添加编辑历史
            edit_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "content_update",
                "word_count": len(content),
                "editor": "system"
            }
            existing_data["editing"]["edit_history"].append(edit_record)
            existing_data["editing"]["last_modified_by"] = "system"

            # 保存JSON版本
            json_file.write_text(json.dumps(existing_data, ensure_ascii=False, indent=2), encoding='utf-8')

            # 生成并保存MD版本
            md_content = self._create_chapter_md_content(existing_data)
            md_file.write_text(md_content, encoding='utf-8')

            return {
                "status": "success",
                "chapter": chapter_number,
                "word_count": len(content),
                "json_file": str(json_file),
                "md_file": str(md_file),
                "message": f"第{chapter_number}章更新成功"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"更新章节失败: {e}"
            }

    def get_chapter_content(self, chapter_number: int) -> Dict[str, Any]:
        """获取章节内容（返回JSON版本）"""
        try:
            # 章节目录（在draft目录下）
            chapter_dir = self.draft_dir / "chapters" / f"chapter_{chapter_number:02d}"

            # 两个版本的文件路径
            json_file = chapter_dir / f"chapter_{chapter_number:02d}.json"
            md_file = chapter_dir / f"chapter_{chapter_number:02d}.md"

            if not json_file.exists():
                return {
                    "status": "error",
                    "message": f"第{chapter_number}章不存在"
                }

            # 读取JSON数据
            json_data = json.loads(json_file.read_text(encoding='utf-8'))

            return {
                "status": "success",
                "chapter": chapter_number,
                "json_data": json_data,
                "json_file": str(json_file),
                "md_file": str(md_file),
                "md_exists": md_file.exists()
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"读取章节失败: {e}"
            }

    def _chapter_exists(self, chapter_number: int) -> bool:
        """检查章节是否存在"""
        json_file = (self.draft_dir / "chapters" /
                    f"chapter_{chapter_number:02d}" / f"chapter_{chapter_number:02d}.json")
        return json_file.exists()

    def _create_chapter_data(self, chapter_number: int, title: str,
                            context_summary: str = None) -> Dict[str, Any]:
        """创建章节数据"""
        now = datetime.now()

        return {
            "metadata": {
                "chapter": chapter_number,
                "title": title,
                "word_count": 0,
                "status": "created",
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "version": "1.0"
            },
            "content": {
                "sections": [],
                "main_content": context_summary or "[在此处撰写章节内容...]",
                "dialogues": [],
                "descriptions": [],
                "notes": []
            },
            "context": {
                "previous_chapter_summary": "",
                "current_chapter_focus": "",
                "next_chapter_preview": ""
            },
            "editing": {
                "last_modified_by": "system",
                "edit_history": [],
                "word_target": 2000,
                "progress_percentage": 0
            }
        }

    def intelligent_content_edit(self, chapter_number: int, edit_request: Dict[str, Any]) -> Dict[str, Any]:
        """智能章节内容编辑"""
        try:
            # 获取章节内容
            chapter_result = self.get_chapter_content(chapter_number)
            if chapter_result["status"] != "success":
                return chapter_result

            existing_data = chapter_result["json_data"]
            existing_content = existing_data["content"]["main_content"]

            # 检查是否需要AI能力
            if edit_request.get("requires_ai", False):
                return self._request_ai_content_edit(chapter_number, existing_content, edit_request)

            # 执行本地编辑
            return self._execute_local_content_edit(chapter_number, existing_data, edit_request)

        except Exception as e:
            return {
                "status": "error",
                "message": f"智能编辑失败: {e}"
            }

    def _request_ai_content_edit(self, chapter_number: int, existing_content: str,
                                 edit_request: Dict[str, Any]) -> Dict[str, Any]:
        """请求AI进行内容编辑"""
        ai_task = {
            "task_type": "content_edit",
            "chapter_number": chapter_number,
            "existing_content": existing_content,
            "edit_instructions": edit_request.get("edit_instructions", ""),
            "edit_mode": edit_request.get("edit_mode", "improve"),  # improve, expand, modify, compress
            "target_style": edit_request.get("target_style", "保持原风格"),
            "specific_requirements": edit_request.get("specific_requirements", [])
        }

        return {
            "status": "ai_task_required",
            "ai_task": ai_task,
            "chapter_number": chapter_number
        }

    def _execute_local_content_edit(self, chapter_number: int, existing_data: Dict[str, Any],
                                   edit_request: Dict[str, Any]) -> Dict[str, Any]:
        """执行本地内容编辑"""
        try:
            edit_mode = edit_request.get("edit_mode", "replace")
            new_content = edit_request.get("content", "")

            if edit_mode == "replace":
                # 完全替换
                updated_content = new_content
            elif edit_mode == "append":
                # 追加内容
                existing_content = existing_data["content"]["main_content"]
                updated_content = existing_content + "\n\n" + new_content
            elif edit_mode == "prepend":
                # 前置内容
                existing_content = existing_data["content"]["main_content"]
                updated_content = new_content + "\n\n" + existing_content
            elif edit_mode == "insert":
                # 插入到指定位置
                insert_position = edit_request.get("position", 0)
                existing_content = existing_data["content"]["main_content"]
                if insert_position <= 0:
                    updated_content = new_content + "\n\n" + existing_content
                elif insert_position >= len(existing_content):
                    updated_content = existing_content + "\n\n" + new_content
                else:
                    updated_content = (
                        existing_content[:insert_position] +
                        "\n\n" + new_content + "\n\n" +
                        existing_content[insert_position:]
                    )
            else:
                return {
                    "status": "error",
                    "message": f"不支持的编辑模式: {edit_mode}"
                }

            # 更新章节内容
            metadata = edit_request.get("metadata", {})
            return self.update_chapter_content(chapter_number, updated_content, metadata)

        except Exception as e:
            return {
                "status": "error",
                "message": f"执行本地编辑失败: {e}"
            }

    def process_ai_edit_result(self, chapter_number: int, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """处理AI编辑结果"""
        try:
            if ai_result.get("status") != "success":
                return {
                    "status": "error",
                    "message": "AI编辑失败",
                    "ai_error": ai_result.get("error", "未知错误")
                }

            edited_content = ai_result.get("edited_content", "")
            edit_summary = ai_result.get("edit_summary", "")

            # 更新章节内容
            metadata = {
                "ai_edit_applied": True,
                "ai_edit_summary": edit_summary,
                "ai_edit_timestamp": datetime.now().isoformat()
            }

            update_result = self.update_chapter_content(chapter_number, edited_content, metadata)

            if update_result["status"] == "success":
                update_result["ai_edit_summary"] = edit_summary
                update_result["ai_edit_applied"] = True

            return update_result

        except Exception as e:
            return {
                "status": "error",
                "message": f"处理AI编辑结果失败: {e}"
            }

    def context_aware_update(self, chapter_number: int, context_update: Dict[str, Any]) -> Dict[str, Any]:
        """上下文感知更新"""
        try:
            # 获取当前章节内容
            chapter_result = self.get_chapter_content(chapter_number)
            if chapter_result["status"] != "success":
                return chapter_result

            existing_data = chapter_result["json_data"]

            # 更新上下文信息
            context = existing_data.get("context", {})
            if "previous_chapter_summary" in context_update:
                context["previous_chapter_summary"] = context_update["previous_chapter_summary"]
            if "current_chapter_focus" in context_update:
                context["current_chapter_focus"] = context_update["current_chapter_focus"]
            if "next_chapter_preview" in context_update:
                context["next_chapter_preview"] = context_update["next_chapter_preview"]

            # 保存更新的上下文
            existing_data["context"] = context
            existing_data["metadata"]["updated_at"] = datetime.now().isoformat()

            # 保存更新后的数据
            chapter_dir = self.draft_dir / "chapters" / f"chapter_{chapter_number:02d}"
            json_file = chapter_dir / f"chapter_{chapter_number:02d}.json"

            json_file.write_text(json.dumps(existing_data, ensure_ascii=False, indent=2), encoding='utf-8')

            # 同时更新MD版本
            md_content = self._create_chapter_md_content(existing_data)
            md_file = chapter_dir / f"chapter_{chapter_number:02d}.md"
            md_file.write_text(md_content, encoding='utf-8')

            return {
                "status": "success",
                "message": f"第{chapter_number}章上下文更新成功",
                "updated_context": list(context_update.keys()),
                "json_file": str(json_file),
                "md_file": str(md_file)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"上下文更新失败: {e}"
            }

    def _create_chapter_md_content(self, chapter_data: Dict[str, Any]) -> str:
        """创建章节MD内容（人类阅读版）"""
        metadata = chapter_data["metadata"]
        content = chapter_data["content"]
        context = chapter_data.get("context", {})

        # 构建FrontMatter
        frontmatter_lines = ["---"]
        for key, value in metadata.items():
            frontmatter_lines.append(f"{key}: {value}")
        frontmatter_lines.append("---")
        frontmatter_lines.append("")

        # 构建正文内容
        content_lines = [
            f"# {metadata['title']}",
            "",
            content["main_content"],
            ""
        ]

        # 添加上下文信息（如果有）
        if context.get("current_chapter_focus"):
            content_lines.extend([
                "## 本章重点",
                context["current_chapter_focus"],
                ""
            ])

        if context.get("previous_chapter_summary"):
            content_lines.extend([
                "## 前章回顾",
                context["previous_chapter_summary"],
                ""
            ])

        if context.get("next_chapter_preview"):
            content_lines.extend([
                "## 下章预告",
                context["next_chapter_preview"],
                ""
            ])

        content_lines.extend([
            "---",
            f"*章节创建时间: {metadata['created_at'][:19].replace('T', ' ')}*",
            f"*最后更新: {metadata['updated_at'][:19].replace('T', ' ')}*",
            f"*字数统计: {metadata['word_count']}*"
        ])

        return "\n".join(frontmatter_lines + content_lines)

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="小说生成器章节管理器")
    parser.add_argument("--action", choices=["create", "update", "content", "intelligent-edit", "context-update", "process-ai-edit"],
                       required=True, help="操作类型")
    parser.add_argument("--chapter", type=int, help="章节号")
    parser.add_argument("--title", help="章节标题")
    parser.add_argument("--content", help="章节内容")
    parser.add_argument("--edit-mode", choices=["replace", "append", "prepend", "insert"], default="replace",
                       help="编辑模式")
    parser.add_argument("--position", type=int, help="插入位置（用于insert模式）")
    parser.add_argument("--requires-ai", action="store_true", help="需要AI处理")
    parser.add_argument("--edit-instructions", help="编辑指令（用于AI编辑）")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    cm = ChapterManager(args.project_path)

    if args.action == "create":
        if not args.chapter:
            print("错误: create操作需要指定--chapter参数")
            return
        result = cm.create_chapter(args.chapter, args.title)

    elif args.action == "update":
        if not args.chapter:
            print("错误: update操作需要指定--chapter参数")
            return
        if not args.content:
            print("错误: update操作需要指定--content参数")
            return
        metadata = {}
        if args.title:
            metadata["title"] = args.title
        result = cm.update_chapter_content(args.chapter, args.content, metadata)

    elif args.action == "content":
        if not args.chapter:
            print("错误: content操作需要指定--chapter参数")
            return
        result = cm.get_chapter_content(args.chapter)

    elif args.action == "intelligent-edit":
        if not args.chapter:
            print("错误: intelligent-edit操作需要指定--chapter参数")
            return
        if not args.content and not args.requires_ai:
            print("错误: intelligent-edit操作需要指定--content参数或--requires-ai")
            return

        edit_request = {
            "content": args.content,
            "edit_mode": args.edit_mode,
            "position": args.position or 0,
            "requires_ai": args.requires_ai,
            "edit_instructions": args.edit_instructions or ""
        }

        result = cm.intelligent_content_edit(args.chapter, edit_request)

    elif args.action == "context-update":
        if not args.chapter:
            print("错误: context-update操作需要指定--chapter参数")
            return
        # 简化的上下文更新示例
        context_update = {
            "current_chapter_focus": args.content or "更新章节重点"
        }
        result = cm.context_aware_update(args.chapter, context_update)

    elif args.action == "process-ai-edit":
        print("process-ai-edit操作需要AI处理结果，请使用API接口")
        result = {"status": "error", "message": "命令行不支持此操作"}

    else:
        result = {"status": "error", "message": f"暂不支持的操作: {args.action}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()