#!/usr/bin/env python3
"""
sysmem 项目安装脚本
根据项目结构自动生成的安装配置
"""

import os
import sys
import subprocess
from pathlib import Path

class ProjectInstaller:
    """项目安装器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.project_type = "python"
        self.project_info = {'name': 'sysmem', 'root': '/Users/fanzhang/Documents/github/claudecode-skills/sysmem', 'has_package_json': False, 'has_requirements': False, 'has_pyproject': True, 'has_setup_py': True, 'has_makefile': True, 'python_files': ['/Users/fanzhang/Documents/github/claudecode-skills/sysmem/setup.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/sysmem/__init__.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/sysmem/cli.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/install_project.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/system_monitor.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/interactive_analyzer.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/fingerprint.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/problem_analyzer.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/update_claude_md.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/interactive_problem_solver.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/utils.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/unused_code_analyzer.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/auto_install.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/collect_data.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/change_detector.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/scan_project.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/incremental_collector.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/sync_to_source.py', '/Users/fanzhang/Documents/github/claudecode-skills/sysmem/scripts/analyze_architecture.py'], 'scripts_dir': True, 'src_dir': False, 'type': 'python'}

    def detect_project_type(self):
        """检测项目类型"""
        print(f"🔍 检测项目类型: {self.project_type}")

    def generate_install_commands(self) -> list:
        """生成安装命令"""
        commands = []

        if self.project_type == "python":
            # Python项目安装命令
            if self.project_info["has_pyproject"]:
                commands.append({"command": "python3 -m pip install -e .", "description": "用户模式安装"})
                commands.append({"command": "sudo python3 -m pip install .", "description": "全局安装"})

            if self.project_info["has_makefile"]:
                commands.append({"command": "make install", "description": "使用Makefile安装"})
                commands.append({"command": "make install-dev", "description": "开发模式安装"})

        elif self.project_type == "nodejs":
            # Node.js项目安装命令
            commands.append({"command": "npm install", "description": "安装依赖"})
            commands.append({"command": "npm run build", "description": "构建项目"})

        else:
            # 通用项目安装命令
            commands.append({"command": "echo '请根据项目类型手动安装'", "description": "手动安装提示"})

        return commands

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
        print(f"🚀 开始安装 {project_name} 项目...")
        print(f"📁 项目目录: {self.project_root}")

        # 检测项目类型
        self.detect_project_type()

        # 检查依赖
        if not self.check_dependencies():
            print("❌ 依赖检查失败，无法继续安装")
            return False

        # 生成安装命令
        commands = self.generate_install_commands()

        if not commands:
            print("⚠️ 未找到适合的安装命令")
            return False

        print("\n📋 可用的安装命令:")
        print("=" * 50)

        for i, cmd_info in enumerate(commands, 1):
            print(f"{i}. {cmd_info['description']}")
            print(f"   {cmd_info['command']}")
            print()

        print("=" * 50)
        print("请手动执行上述命令之一来完成安装")

        return True

def main():
    """主函数"""
    installer = ProjectInstaller()
    installer.run_installation()

if __name__ == "__main__":
    main()
