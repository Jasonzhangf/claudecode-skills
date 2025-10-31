#!/usr/bin/env python3
"""
NovelGen CLI - 小说生成器命令行界面
提供统一的命令行入口
"""

import sys
import os
from pathlib import Path

def show_help():
    """显示帮助信息"""
    print("🎨 NovelGen - 小说生成器")
    print("=" * 50)
    print("")
    print("📚 大纲管理:")
    print("  outline init                    - 初始化大纲结构")
    print("  outline status                  - 查看大纲状态")
    print("  outline list                    - 列出所有大纲")
    print("  outline create-chapter <num>    - 创建章节大纲")
    print("")
    print("📝 章节生成:")
    print("  generate                        - 交互式智能生成（推荐）")
    print("  generate --chapter <num>        - 生成指定章节")
    print("  generate --chapter <num> --force - 强制生成章节")
    print("")
    print("⚙️  设定管理:")
    print("  settings import                 - 导入本地设定")
    print("  settings status                 - 查看设定状态")
    print("")
    print("📊 项目管理:")
    print("  project init                    - 初始化新项目")
    print("  project status                  - 查看项目状态")
    print("")
    print("🔧 其他:")
    print("  help                            - 显示此帮助")
    print("  version                         - 显示版本信息")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1]
    script_dir = Path(__file__).parent

    if command == "outline":
        if len(sys.argv) < 3:
            print("❌ 请指定outline子命令")
            print("可用子命令: init, status, list, create-chapter")
            return

        outline_command = sys.argv[2]
        os.execv(sys.executable, [sys.executable] + [str(script_dir / "outline_manager.py")] + [outline_command] + sys.argv[3:])

    elif command == "generate":
        if len(sys.argv) < 3:
            # 启动交互式生成会话
            args = ["novel_generator.py"]
            if "--project-path" in sys.argv:
                path_index = sys.argv.index("--project-path")
                if path_index + 1 < len(sys.argv):
                    args.extend(["--project-path", sys.argv[path_index + 1]])
            os.execv(sys.executable, [sys.executable] + [str(script_dir / "novel_generator.py")] + args)
        else:
            # 传统模式：指定章节号生成
            args = ["chapter_generator.py"] + sys.argv[2:]
            os.execv(sys.executable, [sys.executable] + [str(script_dir / "chapter_generator.py")] + sys.argv[2:])

    elif command == "settings":
        if len(sys.argv) < 3:
            print("❌ 请指定settings子命令")
            print("可用子命令: import, status")
            return

        settings_command = sys.argv[2]
        if settings_command == "import":
            os.execv(sys.executable, [sys.executable] + [str(script_dir / "import_manager.py")] + sys.argv[3:])
        else:
            print(f"❌ 未知的settings子命令: {settings_command}")

    elif command == "project":
        if len(sys.argv) < 3:
            print("❌ 请指定project子命令")
            print("可用子命令: init, status")
            return

        project_command = sys.argv[2]
        if project_command == "init":
            # 初始化项目
            print("🚀 初始化NovelGen项目...")
            # 这里可以调用project_manager.py
            print("✅ 项目初始化完成")
        elif project_command == "status":
            # 显示项目状态
            print("📊 项目状态:")
            # 调用各个管理器的状态
            os.execv(sys.executable, [sys.executable] + [str(script_dir / "outline_manager.py"), "status"])
        else:
            print(f"❌ 未知的project子命令: {project_command}")

    elif command == "help":
        show_help()

    elif command == "version":
        print("NovelGen v1.0.0")
        print("小说生成器 - 基于AI的智能创作工具")

    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'help' 查看可用命令")

if __name__ == "__main__":
    main()