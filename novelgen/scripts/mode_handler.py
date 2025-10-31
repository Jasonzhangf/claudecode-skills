#!/usr/bin/env python3
"""
小说生成器 - 模式处理器
负责设定模式和写作模式之间的切换和各自的工作流程
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from session_manager import SessionManager

class ModeHandler:
    """模式处理器，管理设定模式和写作模式的工作流程"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.session_manager = SessionManager(project_path)

        # 目录路径
        self.settings_dir = self.project_path / "settings"
        self.draft_dir = self.project_path / "draft"
        self.manuscript_dir = self.project_path / "manuscript"

        # 初始化目录结构
        self._ensure_directory_structure()

    def _ensure_directory_structure(self):
        """确保项目目录结构存在"""
        directories = [
            self.settings_dir,
            self.settings_dir / "worldview",
            self.settings_dir / "characters" / "main_characters",
            self.settings_dir / "characters" / "supporting_characters",
            self.settings_dir / "environments",
            self.settings_dir / "plot",
            self.settings_dir / "writing_style",
            self.settings_dir / "memory",
            self.draft_dir / "working_space",
            self.draft_dir / "chapter_drafts",
            self.draft_dir / "generation_cache",
            self.manuscript_dir / "chapters",
            self.manuscript_dir / "compressed_summaries",
            self.manuscript_dir / "context_snapshots"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def start_setting_mode(self) -> Dict[str, Any]:
        """启动设定模式"""
        # 检查是否已有会话
        session = self.session_manager.load_session()

        if session and session["mode"] == "setting":
            return {
                "status": "continue_setting",
                "progress": self._check_setting_progress(),
                "session_id": session["session_id"]
            }

        # 创建或切换到设定模式
        if session:
            self.session_manager.switch_mode("setting")
        else:
            session = self.session_manager.create_session(mode="setting")

        return {
            "status": "setting_mode_started",
            "session_id": session["session_id"],
            "guide": self._get_setting_guide()
        }

    def start_writing_mode(self) -> Dict[str, Any]:
        """启动写作模式"""
        # 检查设定完成度
        setting_progress = self._check_setting_progress()

        if not setting_progress["all_required_complete"]:
            return {
                "status": "setting_incomplete",
                "missing_settings": setting_progress["missing_required"],
                "message": "请先完成所有必需的设定后再进入写作模式"
            }

        # 切换到写作模式
        session = self.session_manager.load_session()
        if not session:
            session = self.session_manager.create_session(mode="writing", chapter=1)
        else:
            self.session_manager.switch_mode("writing")

        # 初始化写作环境
        self._initialize_writing_environment(session)

        return {
            "status": "writing_mode_started",
            "session_id": session["session_id"],
            "current_chapter": session["current_chapter"],
            "context_summary": self._get_context_summary(session["current_chapter"])
        }

    def process_setting_input(self, category: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """处理设定模式输入"""
        setting_file_map = {
            "worldview": self.settings_dir / "worldview" / "world_setting.md",
            "characters": self.settings_dir / "characters" / "character_relations.md",
            "environments": self.settings_dir / "environments" / "locations.md",
            "plot": self.settings_dir / "plot" / "main_plot.md",
            "style": self.settings_dir / "writing_style" / "narrative_style.md",
            "memory": self.settings_dir / "memory" / "memory_structure.md"
        }

        if category not in setting_file_map:
            return {"status": "error", "message": f"未知的设定类别: {category}"}

        try:
            # 保存设定内容
            file_path = setting_file_map[category]
            self._save_setting_content(file_path, content, category)

            # 更新会话状态
            self.session_manager.update_session({
                "working_state": {
                    "last_setting_category": category,
                    "last_updated": datetime.now().isoformat()
                }
            })

            # 检查设定进度
            progress = self._check_setting_progress()

            return {
                "status": "setting_saved",
                "category": category,
                "progress": progress,
                "next_step": self._get_next_setting_step(category, progress)
            }

        except Exception as e:
            return {"status": "error", "message": f"保存设定失败: {e}"}

    def process_writing_request(self, request_type: str, **kwargs) -> Dict[str, Any]:
        """处理写作模式请求"""
        session = self.session_manager.load_session()
        if not session or session["mode"] != "writing":
            return {"status": "error", "message": "请先进入写作模式"}

        if request_type == "generate_chapter":
            return self._generate_chapter_content(session, **kwargs)
        elif request_type == "continue_chapter":
            return self._continue_chapter_content(session, **kwargs)
        elif request_type == "jump_chapter":
            return self._handle_chapter_jump(session, **kwargs)
        elif request_type == "get_context":
            return self._get_writing_context(session, **kwargs)
        else:
            return {"status": "error", "message": f"未知的请求类型: {request_type}"}

    def _check_setting_progress(self) -> Dict[str, Any]:
        """检查设定完成进度"""
        required_settings = ["worldview", "characters", "environments", "plot", "style"]
        optional_settings = ["memory"]

        completed = []
        missing_required = []

        for setting in required_settings:
            if self._is_setting_complete(setting):
                completed.append(setting)
            else:
                missing_required.append(setting)

        optional_completed = []
        for setting in optional_settings:
            if self._is_setting_complete(setting):
                optional_completed.append(setting)

        return {
            "completed": completed,
            "missing_required": missing_required,
            "optional_completed": optional_completed,
            "all_required_complete": len(missing_required) == 0,
            "total_progress": len(completed) / len(required_settings)
        }

    def _is_setting_complete(self, category: str) -> bool:
        """检查特定设定是否完整"""
        file_map = {
            "worldview": self.settings_dir / "worldview" / "world_setting.md",
            "characters": self.settings_dir / "characters" / "character_relations.md",
            "environments": self.settings_dir / "environments" / "locations.md",
            "plot": self.settings_dir / "plot" / "main_plot.md",
            "style": self.settings_dir / "writing_style" / "narrative_style.md",
            "memory": self.settings_dir / "memory" / "memory_structure.md"
        }

        file_path = file_map.get(category)
        if not file_path or not file_path.exists():
            return False

        # 简单检查文件内容长度
        content = file_path.read_text(encoding='utf-8')
        return len(content.strip()) > 100  # 至少100个字符

    def _get_setting_guide(self) -> List[Dict[str, Any]]:
        """获取设定模式引导"""
        return [
            {
                "step": 1,
                "category": "worldview",
                "title": "世界观设定",
                "description": "设定故事发生的世界背景、规则、时代背景等",
                "required": True
            },
            {
                "step": 2,
                "category": "characters",
                "title": "人物设定",
                "description": "创建主要角色和配角，定义性格、背景、关系等",
                "required": True
            },
            {
                "step": 3,
                "category": "environments",
                "title": "环境设定",
                "description": "定义故事发生的地点、场景、氛围等",
                "required": True
            },
            {
                "step": 4,
                "category": "plot",
                "title": "情节设定",
                "description": "规划主要情节线、冲突、转折点等",
                "required": True
            },
            {
                "step": 5,
                "category": "style",
                "title": "写作风格",
                "description": "定义叙事风格、对话风格、语言特色等",
                "required": True
            },
            {
                "step": 6,
                "category": "memory",
                "title": "记忆设定",
                "description": "设定角色记忆结构和关联（可选）",
                "required": False
            }
        ]

    def _save_setting_content(self, file_path: Path, content: Dict[str, Any], category: str):
        """保存设定内容到文件"""
        # 根据类别格式化内容
        if category == "worldview":
            formatted_content = self._format_worldview_content(content)
        elif category == "characters":
            formatted_content = self._format_character_content(content)
        elif category == "environments":
            formatted_content = self._format_environment_content(content)
        elif category == "plot":
            formatted_content = self._format_plot_content(content)
        elif category == "style":
            formatted_content = self._format_style_content(content)
        elif category == "memory":
            formatted_content = self._format_memory_content(content)
        else:
            formatted_content = str(content)

        file_path.write_text(formatted_content, encoding='utf-8')

    def _format_worldview_content(self, content: Dict[str, Any]) -> str:
        """格式化世界观内容"""
        return f"""# 世界观设定

## 基本信息
- **世界名称**: {content.get('world_name', '未设定')}
- **时代背景**: {content.get('era', '未设定')}
- **技术水平**: {content.get('technology_level', '未设定')}

## 世界规则
{content.get('world_rules', '待补充...')}

## 背景描述
{content.get('background_description', '待补充...')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_character_content(self, content: Dict[str, Any]) -> str:
        """格式化角色内容"""
        main_chars = content.get('main_characters', [])
        supporting_chars = content.get('supporting_characters', [])

        result = "# 人物设定\n\n"

        if main_chars:
            result += "## 主要角色\n\n"
            for i, char in enumerate(main_chars, 1):
                result += f"### 角色{i}: {char.get('name', '未命名')}\n"
                result += f"- **性格**: {char.get('personality', '待定')}\n"
                result += f"- **背景**: {char.get('background', '待定')}\n"
                result += f"- **目标**: {char.get('goal', '待定')}\n\n"

        if supporting_chars:
            result += "## 配角\n\n"
            for i, char in enumerate(supporting_chars, 1):
                result += f"### 配角{i}: {char.get('name', '未命名')}\n"
                result += f"- **作用**: {char.get('role', '待定')}\n"
                result += f"- **特点**: {char.get('traits', '待定')}\n\n"

        result += f"---\n*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        return result

    def _format_environment_content(self, content: Dict[str, Any]) -> str:
        """格式化环境内容"""
        return f"""# 环境设定

## 主要地点
{content.get('main_locations', '待补充...')}

## 环境氛围
{content.get('atmosphere', '待补充...')}

## 场景描述要点
{content.get('scene_description_points', '待补充...')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_plot_content(self, content: Dict[str, Any]) -> str:
        """格式化情节内容"""
        return f"""# 情节设定

## 主线情节
{content.get('main_plot', '待补充...')}

## 主要冲突
{content.get('main_conflicts', '待补充...')}

## 情节转折点
{content.get('plot_twists', '待补充...')}

## 结局设定
{content.get('ending_setup', '待补充...')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_style_content(self, content: Dict[str, Any]) -> str:
        """格式化写作风格内容"""
        return f"""# 写作风格设定

## 叙事风格
{content.get('narrative_style', '待补充...')}

## 对话风格
{content.get('dialogue_style', '待补充...')}

## 语言特色
{content.get('language_features', '待补充...')}

## 词汇偏好
{content.get('vocabulary_preferences', '待补充...')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_memory_content(self, content: Dict[str, Any]) -> str:
        """格式化记忆内容"""
        return f"""# 记忆设定

## 记忆结构
{content.get('memory_structure', '待补充...')}

## 角色记忆关联
{content.get('character_memory_links', '待补充...')}

## 记忆压缩规则
{content.get('memory_compression_rules', '待补充...')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _get_next_setting_step(self, current_category: str, progress: Dict[str, Any]) -> Optional[str]:
        """获取下一个设定步骤"""
        setting_order = ["worldview", "characters", "environments", "plot", "style", "memory"]

        current_index = setting_order.index(current_category)

        # 找到下一个未完成的必需设定
        for category in setting_order[current_index + 1:]:
            if category in progress["missing_required"]:
                return category

        # 如果必需设定都完成了，检查可选设定
        for category in setting_order[current_index + 1:]:
            if category == "memory" and category not in progress["optional_completed"]:
                return category

        return None

    def _initialize_writing_environment(self, session: Dict[str, Any]):
        """初始化写作环境"""
        current_chapter = session["current_chapter"]

        # 创建章节目录
        chapter_dir = self.manuscript_dir / "chapters" / f"chapter_{current_chapter:02d}"
        chapter_dir.mkdir(exist_ok=True)

        # 创建压缩子目录
        compression_dir = chapter_dir / "compression"
        (compression_dir / "recent").mkdir(exist_ok=True)
        (compression_dir / "medium").mkdir(exist_ok=True)
        (compression_dir / "long_term").mkdir(exist_ok=True)

        # 创建章节文件
        chapter_file = chapter_dir / f"chapter_{current_chapter:02d}.md"
        if not chapter_file.exists():
            chapter_file.write_text(f"""---
chapter: {current_chapter}
title: 第{current_chapter}章
word_count: 0
created_at: {datetime.now().isoformat()}
updated_at: {datetime.now().isoformat()}
---

# 第{current_chapter}章

[本章内容待生成...]
""", encoding='utf-8')

    def _get_context_summary(self, chapter: int) -> str:
        """获取当前章节上下文摘要"""
        return f"当前位于第{chapter}章，准备开始写作。已加载相关设定和历史上下文。"

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="小说生成器模式处理器")
    parser.add_argument("--mode", choices=["setting", "writing"], required=True, help="模式")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    mh = ModeHandler(args.project_path)

    if args.mode == "setting":
        result = mh.start_setting_mode()
    elif args.mode == "writing":
        result = mh.start_writing_mode()

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()