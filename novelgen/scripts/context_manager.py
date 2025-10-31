#!/usr/bin/env python3
"""
小说生成器 - 上下文管理器
负责智能上下文组装、压缩数据加载和token管理
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

class ContextManager:
    """上下文管理器，处理智能上下文组装和压缩数据管理"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.token_limit = 128000  # 默认128k tokens

        # 目录路径
        self.settings_dir = self.project_path / "settings"
        self.manuscript_dir = self.project_path / "manuscript"
        self.system_dir = self.project_path / "system"

        # 上下文配置
        self.context_config = self._load_context_config()

    def _load_context_config(self) -> Dict[str, Any]:
        """加载上下文配置"""
        config_file = self.system_dir / "context_config.json"

        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 默认配置
        default_config = {
            "token_limit": 128000,
            "compression_strategy": {
                "recent_chapters": 10,      # 最新10章使用近期压缩
                "medium_chapters": 40,      # 前40章使用中期压缩
                "token_allocation": {
                    "current_chapter": 40000,    # 当前章节40k tokens
                    "recent_compression": 2000,   # 每章近期压缩2k tokens
                    "medium_compression": 500,    # 每章中期压缩500 tokens
                    "long_term_compression": 100, # 每章长期压缩100 tokens
                    "settings_data": 30000,       # 设定数据30k tokens
                    "buffer_space": 20000         # 缓冲空间20k tokens
                }
            },
            "memory_handling": "separate_agent"  # 记忆处理使用独立agent
        }

        self._save_context_config(default_config)
        return default_config

    def _save_context_config(self, config: Dict[str, Any]):
        """保存上下文配置"""
        config_file = self.system_dir / "context_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def build_context(self, chapter: int, mode: str = "writing") -> Dict[str, Any]:
        """构建指定章节的上下文"""
        try:
            context_components = []
            token_usage = 0

            # 1. 加载当前章节内容
            current_chapter_content = self._load_current_chapter(chapter)
            if current_chapter_content:
                context_components.append({
                    "type": "current_chapter",
                    "content": current_chapter_content,
                    "tokens": self._estimate_tokens(current_chapter_content)
                })
                token_usage += context_components[-1]["tokens"]

            # 2. 加载压缩的历史章节
            compression_context = self._load_compression_context(chapter)
            context_components.extend(compression_context["components"])
            token_usage += compression_context["token_usage"]

            # 3. 加载设定数据
            settings_context = self._load_settings_context()
            context_components.extend(settings_context["components"])
            token_usage += settings_context["token_usage"]

            # 4. 检查token使用情况
            if token_usage > self.token_limit:
                return self._handle_context_overflow(context_components, token_usage, chapter)

            # 5. 组装最终上下文
            final_context = self._assemble_final_context(context_components, chapter, mode)

            return {
                "status": "success",
                "chapter": chapter,
                "context": final_context,
                "token_usage": token_usage,
                "components": len(context_components),
                "compression_loaded": compression_context["summary"]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"构建上下文失败: {e}",
                "chapter": chapter
            }

    def clean_context(self, chapter: int, jump_direction: str = "forward") -> Dict[str, Any]:
        """清理上下文，用于章节跳转"""
        try:
            # 保存当前上下文快照
            self._save_context_snapshot(chapter)

            # 根据跳转方向清理不必要的数据
            if jump_direction == "forward":
                # 向前跳转，清理后续章节的临时数据
                self._clean_forward_context(chapter)
            elif jump_direction == "backward":
                # 向后跳转，清理前序章节的临时数据
                self._clean_backward_context(chapter)

            # 重建目标章节的上下文
            return self.build_context(chapter, "writing")

        except Exception as e:
            return {
                "status": "error",
                "message": f"清理上下文失败: {e}",
                "chapter": chapter
            }

    def update_token_limit(self, new_limit: int) -> bool:
        """更新token限制"""
        if new_limit < 32000:  # 最小32k tokens
            return False

        self.token_limit = new_limit
        self.context_config["token_limit"] = new_limit
        self._save_context_config(self.context_config)
        return True

    def get_context_summary(self, chapter: int) -> Dict[str, Any]:
        """获取上下文摘要信息"""
        try:
            # 统计章节数量
            chapter_count = self._count_chapters()

            # 统计压缩数据
            compression_stats = self._get_compression_stats(chapter)

            # 计算预估token使用
            estimated_usage = self._estimate_context_usage(chapter)

            return {
                "chapter": chapter,
                "total_chapters": chapter_count,
                "compression_stats": compression_stats,
                "estimated_tokens": estimated_usage,
                "token_limit": self.token_limit,
                "utilization_rate": estimated_usage / self.token_limit
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取上下文摘要失败: {e}"
            }

    def _load_current_chapter(self, chapter: int) -> Optional[str]:
        """加载当前章节内容"""
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

    def _load_compression_context(self, chapter: int) -> Dict[str, Any]:
        """加载压缩的历史章节上下文"""
        components = []
        token_usage = 0
        summary = {"recent": 0, "medium": 0, "long_term": 0}

        # 1. 加载近期压缩（最新10章的前面章节）
        recent_start = max(1, chapter - 19)  # 当前章节前19章，最多10章近期压缩
        recent_end = chapter - 1

        for ch in range(recent_start, min(recent_end + 1, chapter)):
            if ch >= chapter - 9:  # 最近10章
                compression_data = self._load_compression_data(ch, "recent")
                if compression_data:
                    components.append({
                        "type": "recent_compression",
                        "chapter": ch,
                        "content": compression_data,
                        "tokens": self.context_config["compression_strategy"]["token_allocation"]["recent_compression"]
                    })
                    token_usage += components[-1]["tokens"]
                    summary["recent"] += 1

        # 2. 加载中期压缩（前40章）
        medium_start = max(1, chapter - 59)
        medium_end = chapter - 10

        for ch in range(medium_start, min(medium_end + 1, chapter - 9)):
            compression_data = self._load_compression_data(ch, "medium")
            if compression_data:
                components.append({
                    "type": "medium_compression",
                    "chapter": ch,
                    "content": compression_data,
                    "tokens": self.context_config["compression_strategy"]["token_allocation"]["medium_compression"]
                })
                token_usage += components[-1]["tokens"]
                summary["medium"] += 1

        # 3. 加载长期压缩（更早的章节）
        long_term_end = chapter - 50

        for ch in range(1, min(long_term_end + 1, chapter - 49)):
            if ch % 5 == 0:  # 每5章取一个长期压缩点
                compression_data = self._load_compression_data(ch, "long_term")
                if compression_data:
                    components.append({
                        "type": "long_term_compression",
                        "chapter": ch,
                        "content": compression_data,
                        "tokens": self.context_config["compression_strategy"]["token_allocation"]["long_term_compression"]
                    })
                    token_usage += components[-1]["tokens"]
                    summary["long_term"] += 1

        return {
            "components": components,
            "token_usage": token_usage,
            "summary": summary
        }

    def _load_compression_data(self, chapter: int, compression_type: str) -> Optional[str]:
        """加载指定章节和类型的压缩数据"""
        compression_file = (self.manuscript_dir / "chapters" / f"chapter_{chapter:02d}" /
                           "compression" / compression_type / "plot_summary.md")

        if compression_file.exists():
            return compression_file.read_text(encoding='utf-8')

        return None

    def _load_settings_context(self) -> Dict[str, Any]:
        """加载设定数据上下文"""
        components = []
        token_usage = 0

        # 加载各个设定文件
        setting_files = [
            ("worldview", self.settings_dir / "worldview" / "world_setting.md"),
            ("characters", self.settings_dir / "characters" / "character_relations.md"),
            ("environments", self.settings_dir / "environments" / "locations.md"),
            ("plot", self.settings_dir / "plot" / "main_plot.md"),
            ("style", self.settings_dir / "writing_style" / "narrative_style.md")
        ]

        for setting_type, file_path in setting_files:
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
                components.append({
                    "type": "setting",
                    "setting_type": setting_type,
                    "content": content,
                    "tokens": self._estimate_tokens(content)
                })
                token_usage += components[-1]["tokens"]

        return {
            "components": components,
            "token_usage": token_usage
        }

    def _assemble_final_context(self, components: List[Dict[str, Any]],
                              chapter: int, mode: str) -> str:
        """组装最终的上下文字符串"""
        context_parts = [f"# 上下文信息 - 第{chapter}章\n"]

        # 按优先级排序组件
        sorted_components = sorted(components,
                                 key=lambda x: self._get_component_priority(x["type"]))

        for component in sorted_components:
            if component["type"] == "current_chapter":
                context_parts.append(f"\n## 当前章节内容\n{component['content']}")
            elif component["type"] == "setting":
                context_parts.append(f"\n## {component['setting_type']}设定\n{component['content']}")
            elif component["type"].endswith("_compression"):
                context_parts.append(f"\n## 第{component['chapter']}章{component['type'].split('_')[0]}摘要\n{component['content']}")

        # 添加模式特定的指导信息
        if mode == "writing":
            context_parts.append(f"\n## 写作指导\n请基于以上上下文信息，继续创作第{chapter}章的内容。保持与前面章节的连贯性，并遵循已设定的世界观和人物性格。")

        return "\n".join(context_parts)

    def _get_component_priority(self, component_type: str) -> int:
        """获取组件优先级（数字越小优先级越高）"""
        priority_map = {
            "current_chapter": 1,
            "setting": 2,
            "recent_compression": 3,
            "medium_compression": 4,
            "long_term_compression": 5
        }
        return priority_map.get(component_type, 10)

    def _estimate_tokens(self, text: str) -> int:
        """估算文本的token数量"""
        # 简单估算：中文字符按1.5 tokens，英文单词按1 token计算
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_words = len(text.split()) - chinese_chars  # 粗略估算

        return int(chinese_chars * 1.5 + english_words)

    def _handle_context_overflow(self, components: List[Dict[str, Any]],
                               token_usage: int, chapter: int) -> Dict[str, Any]:
        """处理上下文溢出"""
        # 按优先级移除组件直到token使用在限制内
        sorted_components = sorted(components,
                                 key=lambda x: self._get_component_priority(x["type"]), reverse=True)

        current_usage = token_usage
        removed_components = []

        for component in sorted_components:
            if current_usage <= self.token_limit * 0.9:  # 保留10%缓冲
                break

            current_usage -= component["tokens"]
            removed_components.append(component)
            components.remove(component)

        return {
            "status": "warning",
            "message": f"上下文token超限，已移除{len(removed_components)}个低优先级组件",
            "chapter": chapter,
            "context": self._assemble_final_context(components, chapter, "writing"),
            "token_usage": current_usage,
            "removed_components": [c["type"] for c in removed_components]
        }

    def _save_context_snapshot(self, chapter: int):
        """保存上下文快照"""
        snapshot_dir = self.manuscript_dir / "context_snapshots" / f"before_chapter_{chapter:02d}"
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        snapshot_data = {
            "chapter": chapter,
            "timestamp": datetime.now().isoformat(),
            "context_config": self.context_config
        }

        with open(snapshot_dir / "snapshot.json", 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, ensure_ascii=False, indent=2)

    def _clean_forward_context(self, chapter: int):
        """清理向前跳转时的上下文"""
        # 清理后续章节的临时缓存
        draft_dir = self.project_path / "draft"
        if draft_dir.exists():
            for item in draft_dir.glob("**/*"):
                if item.is_file() and "temp" in item.name:
                    try:
                        item.unlink()
                    except:
                        pass

    def _clean_backward_context(self, chapter: int):
        """清理向后跳转时的上下文"""
        # 清理当前工作空间
        working_space = self.project_path / "draft" / "working_space"
        if working_space.exists():
            for item in working_space.glob("*"):
                if item.is_file():
                    try:
                        item.unlink()
                    except:
                        pass

    def _count_chapters(self) -> int:
        """统计现有章节数量"""
        chapters_dir = self.manuscript_dir / "chapters"
        if not chapters_dir.exists():
            return 0

        return len([d for d in chapters_dir.iterdir()
                   if d.is_dir() and d.name.startswith("chapter_")])

    def _get_compression_stats(self, chapter: int) -> Dict[str, Any]:
        """获取压缩统计信息"""
        stats = {"recent": 0, "medium": 0, "long_term": 0, "missing": []}

        for ch in range(1, chapter):
            for compression_type in ["recent", "medium", "long_term"]:
                compression_file = (self.manuscript_dir / "chapters" / f"chapter_{ch:02d}" /
                                   "compression" / compression_type / "plot_summary.md")
                if compression_file.exists():
                    stats[compression_type] += 1
                else:
                    stats["missing"].append({"chapter": ch, "type": compression_type})

        return stats

    def _estimate_context_usage(self, chapter: int) -> int:
        """估算上下文使用量"""
        # 基于配置和章节数量进行估算
        config = self.context_config["compression_strategy"]
        allocation = config["token_allocation"]

        # 基础设定数据
        usage = allocation["settings_data"] + allocation["buffer_space"]

        # 当前章节
        usage += allocation["current_chapter"]

        # 压缩数据估算
        if chapter > 1:
            recent_count = min(10, chapter - 1)
            medium_count = min(40, max(0, chapter - 11))
            long_term_count = max(0, chapter - 51) // 5  # 每5章一个

            usage += recent_count * allocation["recent_compression"]
            usage += medium_count * allocation["medium_compression"]
            usage += long_term_count * allocation["long_term_compression"]

        return usage

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="小说生成器上下文管理器")
    parser.add_argument("--action", choices=["build", "clean", "summary", "update_limit"],
                       required=True, help="操作类型")
    parser.add_argument("--chapter", type=int, help="章节号")
    parser.add_argument("--token-limit", type=int, help="token限制")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    cm = ContextManager(args.project_path)

    if args.action == "build":
        if not args.chapter:
            print("错误: build操作需要指定--chapter参数")
            return
        result = cm.build_context(args.chapter)
    elif args.action == "clean":
        if not args.chapter:
            print("错误: clean操作需要指定--chapter参数")
            return
        result = cm.clean_context(args.chapter)
    elif args.action == "summary":
        if not args.chapter:
            print("错误: summary操作需要指定--chapter参数")
            return
        result = cm.get_context_summary(args.chapter)
    elif args.action == "update_limit":
        if not args.token_limit:
            print("错误: update_limit操作需要指定--token-limit参数")
            return
        success = cm.update_token_limit(args.token_limit)
        result = {"status": "success" if success else "error", "new_limit": args.token_limit}

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()