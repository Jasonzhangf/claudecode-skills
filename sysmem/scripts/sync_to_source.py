#!/usr/bin/env python3
"""
源代码同步脚本 - 将安装目录的更改同步回源代码
"""

import os
import sys
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any
import difflib

class SourceSynchronizer:
    """源代码同步器"""

    def __init__(self, install_dir: str = None, source_dir: str = None):
        # 默认路径
        self.install_dir = Path(install_dir) if install_dir else Path("/Users/fanzhang/.claude/skills/sysmem")
        self.source_dir = Path(source_dir) if source_dir else Path("/Users/fanzhang/Documents/github/claudecode-skills/sysmem")

        if not self.install_dir.exists():
            raise FileNotFoundError(f"安装目录不存在: {self.install_dir}")

        if not self.source_dir.exists():
            raise FileNotFoundError(f"源代码目录不存在: {self.source_dir}")

    def sync_all_changes(self, interactive: bool = True) -> bool:
        """同步所有更改"""
        print("🔄 开始同步安装目录到源代码...")
        print(f"📁 安装目录: {self.install_dir}")
        print(f"📁 源代码目录: {self.source_dir}")

        success = True

        # 同步核心文件
        core_files = [
            "setup.py",
            "pyproject.toml",
            "Makefile",
            "INSTALLATION.md"
        ]

        for file_name in core_files:
            if self._sync_file(file_name, interactive):
                print(f"✅ 已同步: {file_name}")
            else:
                print(f"❌ 同步失败: {file_name}")
                success = False

        # 同步sysmem包目录
        if self._sync_directory("sysmem", interactive):
            print("✅ 已同步: sysmem包目录")
        else:
            print("❌ 同步失败: sysmem包目录")
            success = False

        # 同步scripts目录（仅新增文件）
        if self._sync_scripts_directory(interactive):
            print("✅ 已同步: scripts目录")
        else:
            print("❌ 同步失败: scripts目录")
            success = False

        # 生成项目特定的安装配置
        if self._generate_project_config(interactive):
            print("✅ 已生成项目配置")
        else:
            print("❌ 生成项目配置失败")
            success = False

        if success:
            print("🎉 源代码同步完成！")
        else:
            print("⚠️ 部分同步失败，请检查错误信息")

        return success

    def _sync_file(self, file_name: str, interactive: bool) -> bool:
        """同步单个文件"""
        src_file = self.install_dir / file_name
        dst_file = self.source_dir / file_name

        if not src_file.exists():
            print(f"⚠️ 源文件不存在: {src_file}")
            return False

        # 检查是否需要同步
        if dst_file.exists():
            if not self._files_different(src_file, dst_file):
                print(f"⏭️ 文件无变化，跳过: {file_name}")
                return True

            if interactive:
                diff = self._get_file_diff(dst_file, src_file)
                print(f"\n📝 检测到文件变更: {file_name}")
                print("变更内容:")
                print("-" * 50)
                print(diff)
                print("-" * 50)

                choice = input(f"是否同步 {file_name}? (y/N): ").strip().lower()
                if choice != 'y':
                    print(f"⏭️ 跳过同步: {file_name}")
                    return True

        # 确保目标目录存在
        dst_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(src_file, dst_file)
            return True
        except Exception as e:
            print(f"❌ 复制文件失败 {file_name}: {e}")
            return False

    def _sync_directory(self, dir_name: str, interactive: bool) -> bool:
        """同步目录"""
        src_dir = self.install_dir / dir_name
        dst_dir = self.source_dir / dir_name

        if not src_dir.exists():
            print(f"⚠️ 源目录不存在: {src_dir}")
            return False

        # 创建目标目录
        dst_dir.mkdir(parents=True, exist_ok=True)

        success = True

        # 递归同步所有文件
        for src_file in src_dir.rglob("*"):
            if src_file.is_file():
                relative_path = src_file.relative_to(src_dir)
                dst_file = dst_dir / relative_path

                # 检查是否需要同步
                if dst_file.exists():
                    if not self._files_different(src_file, dst_file):
                        continue

                    if interactive:
                        diff = self._get_file_diff(dst_file, src_file)
                        print(f"\n📝 检测到文件变更: {relative_path}")
                        print("变更内容:")
                        print("-" * 30)
                        print(diff[:500] + "..." if len(diff) > 500 else diff)
                        print("-" * 30)

                        choice = input(f"是否同步 {relative_path}? (y/N): ").strip().lower()
                        if choice != 'y':
                            continue

                # 确保目标目录存在
                dst_file.parent.mkdir(parents=True, exist_ok=True)

                try:
                    shutil.copy2(src_file, dst_file)
                except Exception as e:
                    print(f"❌ 复制文件失败 {relative_path}: {e}")
                    success = False

        return success

    def _sync_scripts_directory(self, interactive: bool) -> bool:
        """同步scripts目录（仅新增文件）"""
        src_dir = self.install_dir / "scripts"
        dst_dir = self.source_dir / "scripts"

        if not src_dir.exists():
            return True  # 如果源目录不存在，认为不需要同步

        # 创建目标目录
        dst_dir.mkdir(parents=True, exist_ok=True)

        success = True

        # 只同步安装目录中有而源代码目录中没有的文件
        for src_file in src_dir.rglob("*.py"):
            if src_file.is_file():
                relative_path = src_file.relative_to(src_dir)
                dst_file = dst_dir / relative_path

                if not dst_file.exists():
                    if interactive:
                        print(f"\n📝 发现新脚本: {relative_path}")
                        choice = input(f"是否添加到源代码? (y/N): ").strip().lower()
                        if choice != 'y':
                            continue

                    # 确保目标目录存在
                    dst_file.parent.mkdir(parents=True, exist_ok=True)

                    try:
                        shutil.copy2(src_file, dst_file)
                        print(f"✅ 已添加新脚本: {relative_path}")
                    except Exception as e:
                        print(f"❌ 添加脚本失败 {relative_path}: {e}")
                        success = False

        return success

    def _generate_project_config(self, interactive: bool) -> bool:
        """生成项目特定的安装配置"""
        print("📝 生成项目特定配置...")

        # 分析项目结构
        project_info = self._analyze_project_structure()

        # 生成动态的安装脚本
        install_script_content = self._generate_install_script(project_info)
        install_script_path = self.source_dir / "scripts" / "install_project.py"

        try:
            with open(install_script_path, 'w', encoding='utf-8') as f:
                f.write(install_script_content)

            # 设置可执行权限
            os.chmod(install_script_path, 0o755)
            return True

        except Exception as e:
            print(f"❌ 生成安装脚本失败: {e}")
            return False

    def _analyze_project_structure(self) -> Dict[str, Any]:
        """分析项目结构"""
        project_info = {
            "name": self.source_dir.name,
            "root": str(self.source_dir),
            "has_package_json": (self.source_dir / "package.json").exists(),
            "has_requirements": (self.source_dir / "requirements.txt").exists(),
            "has_pyproject": (self.source_dir / "pyproject.toml").exists(),
            "has_setup_py": (self.source_dir / "setup.py").exists(),
            "has_makefile": (self.source_dir / "Makefile").exists(),
            "python_files": list(self.source_dir.rglob("*.py")),
            "scripts_dir": (self.source_dir / "scripts").exists(),
            "src_dir": (self.source_dir / "src").exists(),
        }

        # 检测项目类型
        if project_info["has_package_json"]:
            project_info["type"] = "nodejs"
        elif project_info["has_pyproject"] or project_info["has_setup_py"]:
            project_info["type"] = "python"
        else:
            project_info["type"] = "generic"

        return project_info

    def _generate_install_script(self, project_info: Dict[str, Any]) -> str:
        """生成动态安装脚本"""
        project_name = project_info["name"]
        project_type = project_info["type"]

        script_content = f'''#!/usr/bin/env python3
"""
{project_name} 项目安装脚本
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
        self.project_type = "{project_type}"
        self.project_info = {project_info}

    def detect_project_type(self):
        """检测项目类型"""
        print(f"🔍 检测项目类型: {{self.project_type}}")

    def generate_install_commands(self) -> list:
        """生成安装命令"""
        commands = []

        if self.project_type == "python":
            # Python项目安装命令
            if self.project_info["has_pyproject"]:
                commands.append({{"command": "python3 -m pip install -e .", "description": "用户模式安装"}})
                commands.append({{"command": "sudo python3 -m pip install .", "description": "全局安装"}})

            if self.project_info["has_makefile"]:
                commands.append({{"command": "make install", "description": "使用Makefile安装"}})
                commands.append({{"command": "make install-dev", "description": "开发模式安装"}})

        elif self.project_type == "nodejs":
            # Node.js项目安装命令
            commands.append({{"command": "npm install", "description": "安装依赖"}})
            commands.append({{"command": "npm run build", "description": "构建项目"}})

        else:
            # 通用项目安装命令
            commands.append({{"command": "echo '请根据项目类型手动安装'", "description": "手动安装提示"}})

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
            print(f"✅ Python: {{result.stdout.decode().strip()}}")

            # 检查pip
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True)
            if result.returncode != 0:
                print("❌ pip未安装或不可用")
                return False
            print(f"✅ pip: {{result.stdout.decode().strip()}}")

            return True

        except Exception as e:
            print(f"❌ 依赖检查失败: {{e}}")
            return False

    def run_installation(self):
        """执行安装"""
        print(f"🚀 开始安装 {{project_name}} 项目...")
        print(f"📁 项目目录: {{self.project_root}}")

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

        print("\\n📋 可用的安装命令:")
        print("=" * 50)

        for i, cmd_info in enumerate(commands, 1):
            print(f"{{i}}. {{cmd_info['description']}}")
            print(f"   {{cmd_info['command']}}")
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
'''

        return script_content

    def _files_different(self, file1: Path, file2: Path) -> bool:
        """检查两个文件是否不同"""
        try:
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                return f1.read() != f2.read()
        except:
            return True

    def _get_file_diff(self, file1: Path, file2: Path) -> str:
        """获取文件差异"""
        try:
            with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
                lines1 = f1.readlines()
                lines2 = f2.readlines()

            diff = difflib.unified_diff(
                lines1, lines2,
                fromfile=str(file1),
                tofile=str(file2),
                lineterm=''
            )
            return ''.join(diff)
        except Exception as e:
            return f"无法获取文件差异: {e}"


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='源代码同步工具')
    parser.add_argument('--install-dir', help='安装目录路径')
    parser.add_argument('--source-dir', help='源代码目录路径')
    parser.add_argument('--non-interactive', action='store_true', help='非交互模式')

    args = parser.parse_args()

    try:
        synchronizer = SourceSynchronizer(args.install_dir, args.source_dir)
        success = synchronizer.sync_all_changes(interactive=not args.non_interactive)
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"❌ 同步失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()