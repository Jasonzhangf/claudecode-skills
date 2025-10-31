#!/usr/bin/env python3
"""
小说生成器功能完整性测试脚本
测试所有核心功能和修改功能
"""

import sys
import os
import json
import subprocess
from pathlib import Path

class SkillTester:
    """技能功能测试器"""

    def __init__(self, test_dir: str):
        self.test_dir = Path(test_dir)
        self.test_project = self.test_dir / "test_project"
        self.test_project.mkdir(exist_ok=True)

        # 测试结果记录
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0

    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")

        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "message": message
        })

        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    def run_command(self, cmd: list, work_dir: str = None) -> dict:
        """运行命令并返回结果"""
        try:
            if work_dir:
                result = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True, timeout=30)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timeout",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }

    def test_basic_imports(self):
        """测试基本导入功能"""
        print("\n🧪 测试基本导入功能...")

        scripts_dir = self.test_dir / "scripts"

        # 测试会话管理器
        result = self.run_command([
            "python3", "-c",
            "import sys; sys.path.append('scripts'); from session_manager import SessionManager; print('SessionManager导入成功')"
        ], str(self.test_dir))

        self.log_test("会话管理器导入", result["success"], result["stderr"])

        # 测试角色管理器
        result = self.run_command([
            "python3", "-c",
            "import sys; sys.path.append('scripts'); from data_managers.character_manager import CharacterManager; print('CharacterManager导入成功')"
        ], str(self.test_dir))

        self.log_test("角色管理器导入", result["success"], result["stderr"])

        # 测试压缩引擎
        result = self.run_command([
            "python3", "-c",
            "import sys; sys.path.append('scripts'); from compression_engine import CompressionEngine; print('CompressionEngine导入成功')"
        ], str(self.test_dir))

        self.log_test("压缩引擎导入", result["success"], result["stderr"])

    def test_worldview_functions(self):
        """测试世界观功能"""
        print("\n🧪 测试世界观功能...")

        # 创建世界观
        test_data = {
            "world_name": "测试世界",
            "era": "测试时代",
            "technology_level": "测试科技",
            "magic_system": "测试魔法系统"
        }

        result = self.run_command([
            "python3", "scripts/data_managers/worldbuilder.py",
            "--action", "create",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("创建世界观", result["success"], result["stderr"])

        # 更新世界观
        result = self.run_command([
            "python3", "scripts/data_managers/worldbuilder.py",
            "--action", "update",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("更新世界观", result["success"], result["stderr"])

    def test_character_functions(self):
        """测试角色功能"""
        print("\n🧪 测试角色功能...")

        # 创建角色
        result = self.run_command([
            "python3", "scripts/data_managers/character_manager.py",
            "--action", "create",
            "--name", "测试主角",
            "--type", "main",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("创建角色", result["success"], result["stderr"])

        # 列出角色
        result = self.run_command([
            "python3", "scripts/data_managers/character_manager.py",
            "--action", "list",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("列出角色", result["success"], result["stderr"])

        # 更新角色
        result = self.run_command([
            "python3", "scripts/data_managers/character_manager.py",
            "--action", "update",
            "--name", "测试主角",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("更新角色", result["success"], result["stderr"])

        # 添加关系
        result = self.run_command([
            "python3", "scripts/data_managers/character_manager.py",
            "--action", "relations",
            "--name", "测试主角",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("查看角色关系", result["success"], result["stderr"])

    def test_plot_functions(self):
        """测试情节功能"""
        print("\n🧪 测试情节功能...")

        # 创建情节大纲
        result = self.run_command([
            "python3", "scripts/data_managers/plot_manager.py",
            "--action", "create",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("创建情节大纲", result["success"], result["stderr"])

        # 添加情节点
        result = self.run_command([
            "python3", "scripts/data_managers/plot_manager.py",
            "--action", "add_point",
            "--title", "测试情节",
            "--chapter", "5",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("添加情节点", result["success"], result["stderr"])

        # 获取情节结构
        result = self.run_command([
            "python3", "scripts/data_managers/plot_manager.py",
            "--action", "structure",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("获取情节结构", result["success"], result["stderr"])

        # 更新情节大纲
        update_data = '{"story_type": "测试故事类型"}'
        result = self.run_command([
            "python3", "scripts/data_managers/plot_manager.py",
            "--action", "update",
            "--data", update_data,
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("更新情节大纲", result["success"], result["stderr"])

        # 检查情节一致性
        result = self.run_command([
            "python3", "scripts/data_managers/plot_manager.py",
            "--action", "check",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("检查情节一致性", result["success"], result["stderr"])

    def test_compression_functions(self):
        """测试压缩功能"""
        print("\n🧪 测试压缩功能...")

        # 创建测试章节
        result = self.run_command([
            "python3", "scripts/chapter_manager.py",
            "--action", "create",
            "--chapter", "1",
            "--title", "测试章节",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("创建测试章节", result["success"], result["stderr"])

        # 获取压缩状态
        result = self.run_command([
            "python3", "scripts/compression_engine.py",
            "--action", "status",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("获取压缩状态", result["success"], result["stderr"])

        # 执行压缩
        result = self.run_command([
            "python3", "scripts/compression_engine.py",
            "--action", "compress",
            "--chapters", "1",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("执行压缩", result["success"], result["stderr"])

    def test_session_functions(self):
        """测试会话功能"""
        print("\n🧪 测试会话功能...")

        # 创建会话
        result = self.run_command([
            "python3", "scripts/session_manager.py",
            "--action", "create",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("创建会话", result["success"], result["stderr"])

        # 加载会话
        result = self.run_command([
            "python3", "scripts/session_manager.py",
            "--action", "load",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("加载会话", result["success"], result["stderr"])

        # 获取会话信息
        result = self.run_command([
            "python3", "scripts/session_manager.py",
            "--action", "info",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("获取会话信息", result["success"], result["stderr"])

    def test_context_functions(self):
        """测试上下文功能"""
        print("\n🧪 测试上下文功能...")

        # 构建上下文
        result = self.run_command([
            "python3", "scripts/context_manager.py",
            "--action", "build",
            "--chapter", "1",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("构建上下文", result["success"], result["stderr"])

        # 获取上下文摘要
        result = self.run_command([
            "python3", "scripts/context_manager.py",
            "--action", "summary",
            "--chapter", "1",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("获取上下文摘要", result["success"], result["stderr"])

    def test_unified_settings_manager(self):
        """测试统一设置管理器"""
        print("\n🧪 测试统一设置管理器...")

        # 测试角色状态查询
        result = self.run_command([
            "python3", "scripts/settings_manager.py",
            "--category", "character",
            "--action", "status",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("统一管理器-角色状态", result["success"], result["stderr"])

        # 测试世界观状态查询
        result = self.run_command([
            "python3", "scripts/settings_manager.py",
            "--category", "worldview",
            "--action", "status",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("统一管理器-世界观状态", result["success"], result["stderr"])

        # 测试环境状态查询
        result = self.run_command([
            "python3", "scripts/settings_manager.py",
            "--category", "environment",
            "--action", "status",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("统一管理器-环境状态", result["success"], result["stderr"])

        # 测试情节状态查询
        result = self.run_command([
            "python3", "scripts/settings_manager.py",
            "--category", "plot",
            "--action", "status",
            "--project-path", str(self.test_project)
        ], str(self.test_dir))

        self.log_test("统一管理器-情节状态", result["success"], result["stderr"])

    def test_skill_integrity(self):
        """测试技能完整性"""
        print("\n🧪 测试技能完整性...")

        # 检查必要文件
        required_files = [
            "SKILL.md",
            "scripts/session_manager.py",
            "scripts/context_manager.py",
            "scripts/compression_engine.py",
            "scripts/chapter_manager.py",
            "scripts/settings_manager.py",
            "scripts/data_managers/worldbuilder.py",
            "scripts/data_managers/character_manager.py",
            "scripts/data_managers/plot_manager.py",
            "references/data_schemas.md",
            "references/usage_guide.md"
        ]

        for file_path in required_files:
            full_path = self.test_dir / file_path
            exists = full_path.exists()
            self.log_test(f"文件存在性: {file_path}", exists,
                         "缺失" if not exists else f"大小: {full_path.stat().st_size} bytes")

        # 检查技能文件格式
        skill_file = self.test_dir / "SKILL.md"
        if skill_file.exists():
            content = skill_file.read_text(encoding='utf-8')
            has_name = "name:" in content
            has_description = "description:" in content
            self.log_test("SKILL.md格式检查", has_name and has_description,
                         "缺少name或description字段" if not (has_name and has_description) else "格式正确")

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始小说生成器功能完整性测试...")
        print(f"测试目录: {self.test_dir}")
        print(f"测试项目: {self.test_project}")

        # 运行各项测试
        self.test_skill_integrity()
        self.test_basic_imports()
        self.test_worldview_functions()
        self.test_character_functions()
        self.test_plot_functions()
        self.test_compression_functions()
        self.test_session_functions()
        self.test_context_functions()
        self.test_unified_settings_manager()

        # 输出测试结果
        self.print_summary()

        return self.failed_tests == 0

    def print_summary(self):
        """打印测试摘要"""
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0

        print("\n" + "="*50)
        print("📊 测试结果摘要")
        print("="*50)
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {self.passed_tests}")
        print(f"失败测试: {self.failed_tests}")
        print(f"成功率: {success_rate:.1f}%")

        if self.failed_tests == 0:
            print("\n🎉 所有测试通过！技能功能完整可用！")
        else:
            print(f"\n⚠️  有 {self.failed_tests} 个测试失败，需要修复")
            print("\n失败的测试:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['name']}: {result['message']}")

        print("\n📁 测试文件保存在:", self.test_project)
        print("🔍 可以检查测试项目的结构来验证功能")

def main():
    """主函数"""
    # 获取当前目录作为测试目录
    current_dir = Path(__file__).parent
    tester = SkillTester(str(current_dir))

    success = tester.run_all_tests()

    if success:
        print("\n✅ 技能准备就绪，可以进行安装！")
        sys.exit(0)
    else:
        print("\n❌ 技能存在问题，需要修复后再安装")
        sys.exit(1)

if __name__ == "__main__":
    main()