#!/usr/bin/env python3
"""
自动编译安装脚本
在项目修改后自动执行最小版本编译和全局安装
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any

class AutoInstaller:
    """自动安装管理器"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.build_dir = self.project_root / "dist"
        self.src_dir = self.project_root

    def detect_changes(self) -> bool:
        """检测项目是否有重要变更"""
        print("🔍 检测项目变更...")

        # 检查关键文件变更
        key_files = [
            "setup.py",
            "pyproject.toml",
            "Makefile",
            "sysmem/__init__.py",
            "sysmem/cli.py",
            "scripts/*.py"
        ]

        current_mtime = {}
        for pattern in key_files:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    current_mtime[str(file_path.relative_to(self.project_root))] = file_path.stat().st_mtime

        # 读取上次修改时间
        state_file = self.project_root / ".claude" / "skill" / "sysmem" / ".install_state.json"
        if not state_file.exists():
            state_file.parent.mkdir(parents=True, exist_ok=True)
            print("📋 首次检测，需要编译安装")
            return True

        try:
            import json
            with open(state_file, 'r') as f:
                last_state = json.load(f)
        except:
            print("⚠️ 无法读取安装状态，需要重新安装")
            return True

        # 比较修改时间
        for file_path, mtime in current_mtime.items():
            if file_path not in last_state or mtime > last_state[file_path]:
                print(f"📝 检测到文件变更: {file_path}")
                return True

        print("✅ 无重要变更，跳过编译安装")
        return False

    def save_install_state(self):
        """保存当前安装状态"""
        state_file = self.project_root / ".claude" / "skill" / "sysmem" / ".install_state.json"

        current_mtime = {}
        key_patterns = ["setup.py", "pyproject.toml", "Makefile", "sysmem/__init__.py", "sysmem/cli.py", "scripts/*.py"]

        for pattern in key_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    current_mtime[str(file_path.relative_to(self.project_root))] = file_path.stat().st_mtime

        try:
            import json
            with open(state_file, 'w') as f:
                json.dump(current_mtime, f, indent=2)
        except Exception as e:
            print(f"⚠️ 保存安装状态失败: {e}")

    def check_dependencies(self) -> bool:
        """检查构建依赖"""
        print("🔧 检查构建依赖...")

        required_packages = ["pip", "setuptools", "wheel", "build"]
        missing_packages = []

        for package in required_packages:
            try:
                subprocess.run([sys.executable, "-c", f"import {package}"],
                             check=True, capture_output=True)
            except subprocess.CalledProcessError:
                missing_packages.append(package)

        if missing_packages:
            print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
            print("🔄 正在安装依赖...")

            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "--upgrade"
                ] + required_packages, check=True)
                print("✅ 依赖安装完成")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ 依赖安装失败: {e}")
                return False

        print("✅ 依赖检查通过")
        return True

    def clean_build(self) -> bool:
        """清理构建文件"""
        print("🧹 清理构建文件...")

        dirs_to_clean = ["build", "dist", "*.egg-info", "__pycache__"]

        for pattern in dirs_to_clean:
            for path in self.project_root.glob(pattern):
                if path.is_dir():
                    try:
                        import shutil
                        shutil.rmtree(path)
                        print(f"  🗑️ 删除目录: {path.name}")
                    except Exception as e:
                        print(f"⚠️ 删除目录失败 {path}: {e}")

        # 清理Python缓存文件
        for pyc_file in self.project_root.rglob("*.pyc"):
            try:
                pyc_file.unlink()
            except:
                pass

        print("✅ 清理完成")
        return True

    def build_package(self) -> bool:
        """构建包"""
        print("🔨 构建Python包...")

        try:
            # 使用build模块构建
            result = subprocess.run([
                sys.executable, "-m", "build"
            ], cwd=self.project_root, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"❌ 构建失败: {result.stderr}")
                return False

            print("✅ 包构建完成")

            # 显示构建结果
            if self.build_dir.exists():
                dist_files = list(self.build_dir.glob("*"))
                print(f"📦 生成分发包: {len(dist_files)} 个文件")
                for file in dist_files:
                    print(f"  - {file.name} ({file.stat().st_size / 1024:.1f} KB)")

            return True

        except Exception as e:
            print(f"❌ 构建过程出错: {e}")
            return False

    def install_package(self, global_install: bool = False) -> bool:
        """安装包"""
        install_type = "全局安装" if global_install else "用户安装"
        print(f"📦 执行{install_type}...")

        try:
            # 查找最新的wheel文件
            wheel_files = list(self.build_dir.glob("*.whl"))
            if not wheel_files:
                print("❌ 未找到wheel文件")
                return False

            wheel_file = max(wheel_files, key=lambda x: x.stat().st_mtime)

            # 构建安装命令
            cmd = [sys.executable, "-m", "pip", "install"]

            if global_install:
                # 全局安装可能需要管理员权限
                if os.name == 'posix':  # Unix-like系统
                    if subprocess.run(["which", "sudo"], capture_output=True).returncode == 0:
                        cmd = ["sudo"] + cmd
                cmd.extend(["--upgrade", str(wheel_file)])
            else:
                cmd.extend(["--user", "--upgrade", str(wheel_file)])

            print(f"🔄 执行命令: {' '.join(cmd)}")

            result = subprocess.run(cmd, cwd=self.project_root)

            if result.returncode == 0:
                print(f"✅ {install_type}完成")
                return True
            else:
                print(f"❌ {install_type}失败")

                # 如果全局安装失败，尝试用户安装
                if global_install:
                    print("🔄 尝试用户安装...")
                    user_cmd = [sys.executable, "-m", "pip", "install", "--user", "--upgrade", str(wheel_file)]
                    result = subprocess.run(user_cmd, cwd=self.project_root)
                    if result.returncode == 0:
                        print("✅ 用户安装完成")
                        return True

                return False

        except Exception as e:
            print(f"❌ 安装过程出错: {e}")
            return False

    def verify_installation(self) -> bool:
        """验证安装"""
        print("🔍 验证安装...")

        try:
            # 尝试运行sysmem命令
            result = subprocess.run([
                sys.executable, "-c",
                "import sysmem; print(f'Sysmem {sysmem.__version__} 安装成功')"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print("✅", result.stdout.strip())
                return True
            else:
                print("❌ 模块导入失败")
                return False

        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return False

    def auto_install(self, force: bool = False, global_install: bool = False) -> bool:
        """自动安装流程"""
        print("🚀 开始自动编译安装流程...")
        print(f"📁 项目目录: {self.project_root}")

        start_time = time.time()

        try:
            # 1. 检测变更
            if not force and not self.detect_changes():
                return True

            # 2. 检查依赖
            if not self.check_dependencies():
                return False

            # 3. 清理构建
            if not self.clean_build():
                return False

            # 4. 构建包
            if not self.build_package():
                return False

            # 5. 安装包
            if not self.install_package(global_install):
                return False

            # 6. 验证安装
            if not self.verify_installation():
                return False

            # 7. 保存状态
            self.save_install_state()

            elapsed_time = time.time() - start_time
            print(f"🎉 自动安装完成！耗时: {elapsed_time:.2f} 秒")
            return True

        except Exception as e:
            print(f"❌ 自动安装失败: {e}")
            return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='Sysmem自动编译安装工具')
    parser.add_argument('directory', nargs='?', default='.', help='项目目录')
    parser.add_argument('--check', action='store_true', help='检查变更并提示')
    parser.add_argument('--force', action='store_true', help='强制重新安装')

    args = parser.parse_args()

    installer = AutoInstaller(args.directory)

    if args.check:
        changes_detected = installer.detect_changes()
        if changes_detected:
            print("\n" + "="*50)
            print("🔄 检测到项目变更，建议执行编译安装")
            print("="*50)
            print("\n可用的安装命令:")
            print("  make install       # 用户模式安装")
            print("  make global-install # 全局安装（需要sudo）")
            print("  make install-dev   # 开发模式安装")
            print("\n或者使用Python:")
            print("  python3 -m pip install -e .      # 用户模式")
            print("  sudo python3 -m pip install .    # 全局模式")
            print("="*50)
            sys.exit(1)
        else:
            print("✅ 无变更，无需重新安装")
            sys.exit(0)
    elif args.force:
        success = installer.auto_install(force=True, global_install=False)
        sys.exit(0 if success else 1)
    else:
        print("使用 --check 检查变更，或 --force 强制安装")
        sys.exit(0)


if __name__ == "__main__":
    main()