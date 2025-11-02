#!/usr/bin/env python3
"""
Sysmem v2.0 项目安装脚本 - 支持智能交互式更新
基于项目结构自动生成的安装配置，包含最新的智能交互功能
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class ProjectInstaller:
    """Sysmem v2.0 项目安装器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.project_type = "python"
        self.project_version = "2.0.0"

        # 更新项目信息
        self.project_info = {
            'name': 'sysmem',
            'version': self.project_version,
            'root': str(self.project_root),
            'description': '项目架构链条化管理系统 - 支持智能交互式更新',
            'has_package_json': False,
            'has_requirements': False,
            'has_pyproject': True,
            'has_setup_py': True,
            'has_makefile': True,
            'features': [
                '智能交互式更新',
                'Git集成文件变更检测',
                '模块化数据收集',
                '智能数据清理',
                '静态代码分析',
                '自动化文档管理'
            ],
            'scripts_dir': True,
            'src_dir': False,
            'type': 'python'
        }

    def detect_project_type(self):
        """检测项目类型"""
        print(f"🔍 检测项目类型: {self.project_type}")
        print(f"📦 项目版本: {self.project_version}")

    def display_project_features(self):
        """显示项目特性"""
        print(f"\n✨ {self.project_info['name']} v{self.project_version} 核心特性:")
        print("=" * 60)

        for i, feature in enumerate(self.project_info['features'], 1):
            print(f"  {i}. {feature}")

        print("\n🎯 推荐使用方式:")
        print("  • 智能交互式更新: python3 scripts/collect_data.py --interactive")
        print("  • 智能数据清理:    python3 scripts/collect_data.py --clean")
        print("  • 完全清理更新:    python3 scripts/collect_data.py --full-clean")
        print("  • 忽略规则报告:    python3 scripts/collect_data.py --ignore-report")
        print("  • 列出可用模块:    python3 scripts/collect_data.py --list-modules")
        print("  • 精确模块更新:    python3 scripts/collect_data.py --module <模块名>")
        print("  • 查看完整帮助:    python3 scripts/collect_data.py --help")

    def generate_install_commands(self) -> list:
        """生成安装命令"""
        commands = []

        if self.project_type == "python":
            # Python项目安装命令
            if self.project_info["has_pyproject"]:
                commands.append({
                    "command": "python3 -m pip install -e .",
                    "description": "🎯 用户模式安装（推荐）",
                    "detail": "可编辑模式安装，便于开发调试"
                })
                commands.append({
                    "command": "sudo python3 -m pip install .",
                    "description": "🌐 全局安装",
                    "detail": "需要管理员权限，所有用户可用"
                })

            if self.project_info["has_makefile"]:
                commands.append({
                    "command": "make install",
                    "description": "🔨 使用Makefile安装",
                    "detail": "自动化安装流程"
                })
                commands.append({
                    "command": "make install-dev",
                    "description": "🛠️ 开发模式安装",
                    "detail": "包含开发依赖和工具"
                })

        elif self.project_type == "nodejs":
            # Node.js项目安装命令
            commands.append({"command": "npm install", "description": "安装依赖"})
            commands.append({"command": "npm run build", "description": "构建项目"})

        else:
            # 通用项目安装命令
            commands.append({"command": "echo '请根据项目类型手动安装'", "description": "手动安装提示"})

        return commands

    def check_project_changes(self) -> dict:
        """检查项目变更"""
        try:
            # 尝试使用git检测变更
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                changed_files = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                return {
                    "has_changes": len(changed_files) > 0,
                    "changed_files": changed_files,
                    "method": "git"
                }
            else:
                return {"has_changes": False, "method": "git_error"}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Git不可用，检查文件修改时间
            try:
                from datetime import datetime, timedelta
                import time

                recent_changes = []
                threshold = time.time() - (24 * 3600)  # 24小时前

                for file_path in self.project_root.rglob("*.py"):
                    if file_path.stat().st_mtime > threshold:
                        relative_path = file_path.relative_to(self.project_root)
                        recent_changes.append(str(relative_path))

                return {
                    "has_changes": len(recent_changes) > 0,
                    "changed_files": recent_changes,
                    "method": "mtime"
                }
            except Exception:
                return {"has_changes": False, "method": "error"}

    def suggest_reinstall(self) -> bool:
        """建议是否需要重新安装"""
        changes = self.check_project_changes()

        if changes["has_changes"]:
            print(f"\n🔄 检测到项目变更 (使用{changes['method']}检测):")
            print(f"   变更文件数: {len(changes['changed_files'])}")

            if len(changes['changed_files']) <= 5:
                print("   变更文件:")
                for file in changes['changed_files']:
                    print(f"     - {file}")
            else:
                print("   主要变更文件:")
                for file in changes['changed_files'][:3]:
                    print(f"     - {file}")
                print(f"     ... 还有 {len(changes['changed_files']) - 3} 个文件")

            print("\n💡 建议重新安装以应用最新更改")
            return True
        else:
            print("\n✅ 项目状态正常，无需重新安装")
            return False

    def check_dependencies(self) -> bool:
        """检查依赖"""
        print("🔧 检查系统依赖...")

        try:
            # 检查Python
            result = subprocess.run([sys.executable, "--version"], capture_output=True)
            if result.returncode != 0:
                print("❌ Python未安装或不可用")
                return False
            print(f"✅ Python: {result.stdout.decode().strip()}")

            # 检查pip
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True)
            if result.returncode != 0:
                print("❌ pip未安装或不可用")
                return False
            print(f"✅ pip: {result.stdout.decode().strip()}")

            return True

        except Exception as e:
            print(f"❌ 依赖检查失败: {e}")
            return False

    def run_installation(self):
        """执行安装"""
        project_name = self.project_root.name
        print(f"🚀 开始安装 {project_name} v{self.project_version} 项目...")
        print(f"📁 项目目录: {self.project_root}")

        # 显示项目特性
        self.display_project_features()

        # 检测项目类型
        self.detect_project_type()

        # 检查依赖
        if not self.check_dependencies():
            print("❌ 依赖检查失败，无法继续安装")
            return False

        # 检查项目变更
        needs_reinstall = self.suggest_reinstall()

        # 生成安装命令
        commands = self.generate_install_commands()

        if not commands:
            print("⚠️ 未找到适合的安装命令")
            return False

        print("\n📋 可用的安装命令:")
        print("=" * 60)

        for i, cmd_info in enumerate(commands, 1):
            print(f"{i}. {cmd_info['description']}")
            print(f"   命令: {cmd_info['command']}")
            if 'detail' in cmd_info:
                print(f"   说明: {cmd_info['detail']}")
            print()

        print("=" * 60)

        if needs_reinstall:
            print("🔄 检测到项目变更，建议重新安装")
        else:
            print("✅ 项目状态正常")

        print("💡 请手动执行上述命令之一来完成安装")
        print("🎯 推荐使用命令1进行用户模式安装")

        return True

    def show_quick_start(self):
        """显示快速开始指南"""
        print("\n🚀 快速开始指南:")
        print("=" * 60)

        print("1. 📊 智能交互式数据收集（推荐新方式）:")
        print("   python3 scripts/collect_data.py --interactive")
        print("   # 自动检测文件变更，询问更新范围")

        print("\n2. 🧹 智能数据清理（新功能）:")
        print("   python3 scripts/collect_data.py --clean")
        print("   python3 scripts/collect_data.py --ignore-report")
        print("   # 清理被.gitignore标记的过时数据")

        print("\n3. 📦 模块化数据收集:")
        print("   python3 scripts/collect_data.py --list-modules")
        print("   python3 scripts/collect_data.py --module scripts")

        print("\n4. 🔍 代码质量分析:")
        print("   python3 scripts/unused_code_analyzer.py")
        print("   python3 scripts/analyze_architecture.py")

        print("\n5. 📝 文档更新:")
        print("   python3 scripts/update_claude_md.py")

        print("\n💡 更多命令请查看:")
        print("   • python3 scripts/collect_data.py --help")
        print("   • cat README.md")
        print("   • cat INSTALLATION.md")

    def export_install_info(self):
        """导出安装信息到文件"""
        install_info = {
            "project_name": self.project_info['name'],
            "version": self.project_version,
            "install_date": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "features": self.project_info['features'],
            "install_commands": [
                {
                    "command": cmd["command"],
                    "description": cmd["description"]
                }
                for cmd in self.generate_install_commands()
            ],
            "quick_start_commands": [
                "python3 scripts/collect_data.py --interactive",
                "python3 scripts/collect_data.py --clean",
                "python3 scripts/collect_data.py --ignore-report",
                "python3 scripts/collect_data.py --list-modules",
                "python3 scripts/collect_data.py --help"
            ]
        }

        # 导出到.claude目录
        claude_dir = self.project_root / ".claude"
        claude_dir.mkdir(exist_ok=True)

        install_file = claude_dir / "install_info.json"
        try:
            with open(install_file, 'w', encoding='utf-8') as f:
                json.dump(install_info, f, ensure_ascii=False, indent=2)
            print(f"✅ 安装信息已保存到: {install_file}")
        except Exception as e:
            print(f"⚠️  无法保存安装信息: {e}")

def main():
    """主函数"""
    installer = ProjectInstaller()

    # 显示欢迎信息
    print("🌟 Sysmem v2.0 智能项目架构管理系统")
    print("   支持智能交互式更新和Git集成变更检测")
    print()

    # 运行安装流程
    success = installer.run_installation()

    if success:
        # 显示快速开始指南
        installer.show_quick_start()

        # 导出安装信息
        installer.export_install_info()

        print("\n🎉 安装准备完成！")
        print("💡 现在可以使用 Sysmem 的智能交互式功能了")
    else:
        print("\n❌ 安装准备失败")
        print("💡 请检查系统依赖并重试")

if __name__ == "__main__":
    main()
