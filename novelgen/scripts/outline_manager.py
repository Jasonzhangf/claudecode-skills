#!/usr/bin/env python3
"""
小说大纲管理器
提供大纲的创建、编辑、查看等功能
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class OutlineManager:
    """大纲管理器"""

    def __init__(self, project_path: str = None):
        if project_path is None:
            self.project_path = Path.cwd()
        else:
            self.project_path = Path(project_path)

        self.outlines_dir = self.project_path / "settings" / "outlines"
        self.chapters_dir = self.outlines_dir / "chapters"

    def create_outline_structure(self) -> Dict[str, Any]:
        """创建大纲目录结构"""
        try:
            # 创建目录
            self.outlines_dir.mkdir(exist_ok=True)
            self.chapters_dir.mkdir(exist_ok=True)

            # 创建README文件
            readme_path = self.outlines_dir / "README.md"
            if not readme_path.exists():
                self._create_readme()

            # 创建总大纲文件
            master_outline_path = self.outlines_dir / "master_outline.md"
            if not master_outline_path.exists():
                self._create_master_outline()

            return {
                "status": "success",
                "message": "大纲目录结构创建成功",
                "outlines_dir": str(self.outlines_dir),
                "chapters_dir": str(self.chapters_dir)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"创建大纲目录结构失败: {str(e)}"
            }

    def create_chapter_outline(self, chapter_number: int, title: str = "", content: str = "") -> Dict[str, Any]:
        """创建章节大纲"""
        try:
            outline_file = self.chapters_dir / f"chapter_{chapter_number:02d}_outline.md"

            if outline_file.exists():
                return {
                    "status": "warning",
                    "message": f"第{chapter_number}章大纲已存在，将被覆盖"
                }

            # 生成大纲模板
            outline_content = self._generate_chapter_outline_template(chapter_number, title, content)

            # 写入文件
            outline_file.write_text(outline_content, encoding='utf-8')

            return {
                "status": "success",
                "message": f"第{chapter_number}章大纲创建成功",
                "file_path": str(outline_file),
                "word_count": len(outline_content)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"创建第{chapter_number}章大纲失败: {str(e)}"
            }

    def list_outlines(self) -> Dict[str, Any]:
        """列出所有大纲文件"""
        try:
            outlines = {}

            # 总大纲
            master_outline = self.outlines_dir / "master_outline.md"
            if master_outline.exists():
                outlines["master"] = {
                    "file": str(master_outline),
                    "size": master_outline.stat().st_size,
                    "modified": datetime.fromtimestamp(master_outline.stat().st_mtime).isoformat()
                }

            # 章节大纲
            chapters = {}
            for outline_file in sorted(self.chapters_dir.glob("chapter_*_outline.md")):
                # 提取章节号
                try:
                    chapter_num = int(outline_file.stem.split('_')[1])
                    chapters[chapter_num] = {
                        "file": str(outline_file),
                        "size": outline_file.stat().st_size,
                        "modified": datetime.fromtimestamp(outline_file.stat().st_mtime).isoformat()
                    }
                except:
                    continue

            outlines["chapters"] = chapters

            return {
                "status": "success",
                "outlines": outlines,
                "total_chapters": len(chapters)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"列出大纲失败: {str(e)}"
            }

    def get_outline_status(self) -> Dict[str, Any]:
        """获取大纲状态"""
        try:
            # 检查目录结构
            structure_exists = self.outlines_dir.exists() and self.chapters_dir.exists()

            # 列出大纲
            outlines_result = self.list_outlines()
            if outlines_result["status"] != "success":
                return outlines_result

            outlines = outlines_result["outlines"]
            total_chapters = outlines_result["total_chapters"]

            # 检查完整性
            has_master = "master" in outlines
            has_chapters = total_chapters > 0

            # 计算连续性
            chapter_numbers = sorted(outlines.get("chapters", {}).keys())
            is_continuous = len(chapter_numbers) > 0 and chapter_numbers == list(range(1, chapter_numbers[-1] + 1))

            status = {
                "structure_exists": structure_exists,
                "has_master_outline": has_master,
                "has_chapter_outlines": has_chapters,
                "total_chapters": total_chapters,
                "chapter_numbers": chapter_numbers,
                "is_continuous": is_continuous,
                "overall_status": "complete" if structure_exists and has_master and has_chapters else "incomplete"
            }

            return {
                "status": "success",
                "outline_status": status
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取大纲状态失败: {str(e)}"
            }

    def _create_readme(self):
        """创建README文件"""
        readme_content = f"""# 小说大纲总览

## 基本信息
- **创建时间**: {datetime.now().strftime('%Y-%m-%d')}
- **小说名称**: 待定
- **当前状态**: 创作中

## 目录结构说明
```
settings/outlines/
├── README.md                    # 本文件，总览信息
├── master_outline.md         # 总大纲
├── chapters/                    # 章节大纲目录
│   ├── chapter_01_outline.md   # 第1章大纲
│   ├── chapter_02_outline.md   # 第2章大纲
│   └── ...
└── versions/                    # 大纲版本历史（可选）
    └── outline_v1.md           # 初版大纲备份
```

## 更新记录
- **{datetime.now().strftime('%Y-%m-%d')}**: 创建大纲管理体系

---
*此文件由novelgen系统自动维护，手动修改请谨慎*
"""
        readme_path = self.outlines_dir / "README.md"
        readme_path.write_text(readme_content, encoding='utf-8')

    def _create_master_outline(self):
        """创建总大纲文件"""
        master_content = f"""# 小说总大纲

## 基本设定
- **书名**: 待定
- **类型**: 待定
- **主题**: 待定
- **时代**: 待定

## 故事概述
[待填写]

## 主要人物
[待填写]

## 章节结构
[待填写]

## 核心主题
[待填写]

---
*创建时间: {datetime.now().strftime('%Y-%m-%d')}*
*版本: v1.0*
*状态: 规划中*
"""
        master_path = self.outlines_dir / "master_outline.md"
        master_path.write_text(master_content, encoding='utf-8')

    def _generate_chapter_outline_template(self, chapter_number: int, title: str = "", content: str = "") -> str:
        """生成章节大纲模板"""
        current_time = datetime.now().strftime('%Y-%m-%d')

        template = f"""# 第{chapter_number}章大纲

## 章节标题：{title or f"第{chapter_number}章"}

## 开端
[请描述本章开端的情节发展]

## 发展
- **情节1**: [具体描述]
- **情节2**: [具体描述]
- **情节3**: [具体描述]

## 高潮
[请描述本章高潮部分的情节]

## 结局
[请描述本章的结局和为下一章的铺垫]

## 核心冲突
- [冲突1]
- [冲突2]

---
*创建时间: {current_time}*
"""

        if content:
            template = content + "\n\n" + template

        return template

def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python outline_manager.py <command> [options]")
        print("命令:")
        print("  init                    - 初始化大纲结构")
        print("  status                  - 查看大纲状态")
        print("  list                    - 列出所有大纲")
        print("  create-chapter <num>    - 创建章节大纲")
        print("  help                    - 显示帮助")
        return

    command = sys.argv[1]
    project_path = None

    # 解析项目路径参数
    if "--project-path" in sys.argv:
        path_index = sys.argv.index("--project-path")
        if path_index + 1 < len(sys.argv):
            project_path = sys.argv[path_index + 1]

    manager = OutlineManager(project_path)

    if command == "init":
        result = manager.create_outline_structure()
        print(f"✅ {result['message']}" if result['status'] == 'success' else f"❌ {result['message']}")

    elif command == "status":
        result = manager.get_outline_status()
        if result['status'] == 'success':
            status = result['outline_status']
            print("📊 大纲状态:")
            print(f"   目录结构: {'✅' if status['structure_exists'] else '❌'}")
            print(f"   总大纲: {'✅' if status['has_master_outline'] else '❌'}")
            print(f"   章节大纲: {'✅' if status['has_chapter_outlines'] else '❌'}")
            print(f"   章节数量: {status['total_chapters']}")
            print(f"   连续性: {'✅' if status['is_continuous'] else '❌'}")
            print(f"   整体状态: {status['overall_status']}")
        else:
            print(f"❌ {result['message']}")

    elif command == "list":
        result = manager.list_outlines()
        if result['status'] == 'success':
            outlines = result['outlines']
            print("📚 大纲列表:")

            if 'master' in outlines:
                master = outlines['master']
                print(f"   总大纲: {master['file']} ({master['size']} bytes)")

            chapters = outlines.get('chapters', {})
            if chapters:
                print("   章节大纲:")
                for chapter_num, info in sorted(chapters.items()):
                    print(f"     第{chapter_num}章: {info['file']} ({info['size']} bytes)")
            else:
                print("   章节大纲: 无")
        else:
            print(f"❌ {result['message']}")

    elif command == "create-chapter":
        if len(sys.argv) < 3:
            print("❌ 请指定章节号")
            return

        try:
            chapter_num = int(sys.argv[2])
            title = ""
            content = ""

            # 解析标题参数
            if "--title" in sys.argv:
                title_index = sys.argv.index("--title")
                if title_index + 1 < len(sys.argv):
                    title = sys.argv[title_index + 1]

            result = manager.create_chapter_outline(chapter_num, title, content)
            print(f"✅ {result['message']}" if result['status'] == 'success' else f"❌ {result['message']}")

        except ValueError:
            print("❌ 章节号必须是数字")

    elif command == "help":
        print("大纲管理器使用说明:")
        print("")
        print("初始化大纲结构:")
        print("  python outline_manager.py init")
        print("")
        print("查看大纲状态:")
        print("  python outline_manager.py status")
        print("")
        print("列出所有大纲:")
        print("  python outline_manager.py list")
        print("")
        print("创建章节大纲:")
        print("  python outline_manager.py create-chapter 1 --title '章节标题'")
        print("")
        print("指定项目路径:")
        print("  python outline_manager.py status --project-path /path/to/project")

    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'help' 查看可用命令")

if __name__ == "__main__":
    main()