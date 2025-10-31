#!/usr/bin/env python3
"""
完整API接口测试脚本
测试所有统一API接口的功能
"""

import json
import subprocess
import sys
from pathlib import Path

class APITester:
    def __init__(self, project_path="."):
        self.project_path = Path(project_path)
        self.test_results = []

    def run_test(self, test_name, request_data):
        """运行单个API测试"""
        print(f"\n🧪 测试: {test_name}")
        print(f"📤 请求: {json.dumps(request_data, ensure_ascii=False, indent=2)}")

        try:
            cmd = [
                "python3", "scripts/unified_api.py",
                "--request-json", json.dumps(request_data)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_path
            )

            try:
                response = json.loads(result.stdout)
            except json.JSONDecodeError:
                response = {"raw_output": result.stdout}

            print(f"📥 响应: {json.dumps(response, ensure_ascii=False, indent=2)}")

            success = response.get("status") == "success" or "error" not in str(response).lower()
            self.test_results.append({
                "test": test_name,
                "success": success,
                "request": request_data,
                "response": response
            })

            if success:
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")

            return success

        except Exception as e:
            print(f"❌ {test_name} - 异常: {e}")
            self.test_results.append({
                "test": test_name,
                "success": False,
                "request": request_data,
                "error": str(e)
            })
            return False

    def test_system_interfaces(self):
        """测试系统相关接口"""
        print("\n" + "="*60)
        print("🔧 测试系统接口")
        print("="*60)

        # 系统状态
        self.run_test("系统状态查询", {"action": "system.status"})

    def test_import_interfaces(self):
        """测试导入相关接口"""
        print("\n" + "="*60)
        print("📥 测试导入接口")
        print("="*60)

        # 创建测试目录和文件
        test_dir = self.project_path / "test_import_data"
        test_dir.mkdir(exist_ok=True)

        # 创建测试文件
        (test_dir / "character_test.md").write_text("""
# 主角测试

## 基本信息
- 姓名: 测试主角
- 年龄: 25
- 性别: 男
- 职业: 冒险者

## 性格特点
勇敢、善良、有正义感
        """)

        (test_dir / "worldview_test.md").write_text("""
# 世界观设定

## 世界名称
艾泽拉斯世界

## 魔法体系
- 元素魔法
- 神圣魔法
- 暗影魔法
        """)

        # 扫描目录
        self.run_test("扫描目录内容", {
            "action": "import.scan_directory",
            "target_directory": str(test_dir)
        })

        # 从目录导入
        self.run_test("从目录导入设定", {
            "action": "import.from_directory",
            "target_directory": str(test_dir)
        })

        # 导入特定类型
        self.run_test("导入特定设定类型", {
            "action": "import.from_directory",
            "target_directory": str(test_dir),
            "specific_setting": "character"
        })

        # 清理测试文件
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)

    def test_display_interfaces(self):
        """测试显示相关接口"""
        print("\n" + "="*60)
        print("👁️ 测试显示接口")
        print("="*60)

        # 获取可用设定
        self.run_test("获取可用设定列表", {"action": "display.available_settings"})

        # 显示世界观
        self.run_test("显示世界观设定", {
            "action": "display.setting",
            "setting_type": "worldview"
        })

        # 显示角色
        self.run_test("显示角色设定", {
            "action": "display.setting",
            "setting_type": "character"
        })

        # 显示记忆统计
        self.run_test("显示记忆统计", {
            "action": "display.memory_stats"
        })

        # 显示特定角色记忆
        self.run_test("显示角色记忆", {
            "action": "display.memory",
            "identifier": "测试主角",
            "segment_type": "character_all",
            "display_format": "readable"
        })

    def test_chapter_interfaces(self):
        """测试章节相关接口"""
        print("\n" + "="*60)
        print("📖 测试章节接口")
        print("="*60)

        # 创建章节
        self.run_test("创建章节", {
            "action": "chapter.create",
            "chapter_number": 1,
            "title": "第一章：开始",
            "context_summary": "故事的开始"
        })

        # 获取章节内容
        self.run_test("获取章节内容", {
            "action": "chapter.get_content",
            "chapter_number": 1
        })

        # 智能编辑章节
        self.run_test("智能编辑章节", {
            "action": "chapter.intelligent_edit",
            "chapter_number": 1,
            "edit_request": {
                "content": "\n\n这是新增加的内容。",
                "edit_mode": "append",
                "requires_ai": False
            }
        })

        # 上下文更新
        self.run_test("章节上下文更新", {
            "action": "chapter.context_update",
            "chapter_number": 1,
            "context_update": {
                "summary": "更新后的章节摘要",
                "key_events": ["主角出发冒险", "遇到第一个伙伴"]
            }
        })

    def test_memory_interfaces(self):
        """测试记忆相关接口"""
        print("\n" + "="*60)
        print("🧠 测试记忆接口")
        print("="*60)

        # 创建测试章节内容
        test_chapter_file = self.project_path / "manuscript" / "chapters" / "chapter_01" / "chapter_01.md"
        test_chapter_file.parent.mkdir(parents=True, exist_ok=True)
        test_chapter_file.write_text("""
# 第一章

测试主角在艾泽拉斯世界的冒险开始了。

他遇到了美丽的女主角莉娜，两人一见钟情。

在战斗中，他表现出非凡的勇气和智慧。

这次经历让他成长了很多，对责任有了新的理解。
        """)

        # 分析章节记忆
        self.run_test("分析章节记忆", {
            "action": "chapter.analyze_memory",
            "chapter_number": 1
        })

        # 应用记忆分析
        self.run_test("应用记忆分析", {
            "action": "chapter.apply_memory",
            "chapter_number": 1
        })

        # 获取记忆分析信息
        self.run_test("获取记忆分析信息", {
            "action": "chapter.memory_info",
            "chapter_number": 1
        })

    def test_ai_interfaces(self):
        """测试AI相关接口"""
        print("\n" + "="*60)
        print("🤖 测试AI接口")
        print("="*60)

        # AI内容分析
        self.run_test("AI内容分析", {
            "action": "ai.analyze_content",
            "content": "这是一个勇敢的年轻冒险者的故事。",
            "analysis_type": "character_extraction"
        })

        # AI内容编辑
        self.run_test("AI内容编辑", {
            "action": "ai.edit_content",
            "content": "简单的描述。",
            "edit_instructions": "请让这段描述更加生动和详细。"
        })

        # 生成摘要
        self.run_test("AI生成摘要", {
            "action": "ai.generate_summary",
            "content": "长篇内容的详细描述...",
            "summary_type": "brief"
        })

    def test_error_handling(self):
        """测试错误处理"""
        print("\n" + "="*60)
        print("⚠️ 测试错误处理")
        print("="*60)

        # 无效操作
        self.run_test("无效操作", {"action": "invalid.action"})

        # 缺少参数
        self.run_test("缺少参数", {"action": "import.from_directory"})

        # 不存在的文件
        self.run_test("不存在的文件", {
            "action": "import.from_directory",
            "target_directory": "/nonexistent/path"
        })

        # 不存在的章节
        self.run_test("不存在的章节", {
            "action": "chapter.get_content",
            "chapter_number": 999
        })

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始完整API接口测试")
        print("="*60)

        # 切换到项目目录
        import os
        os.chdir(self.project_path)

        # 运行各类测试
        self.test_system_interfaces()
        self.test_import_interfaces()
        self.test_display_interfaces()
        self.test_chapter_interfaces()
        self.test_memory_interfaces()
        self.test_ai_interfaces()
        self.test_error_handling()

        # 生成测试报告
        self.generate_report()

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 测试报告")
        print("="*60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests

        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")

        if failed_tests > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}")
                    if "error" in result:
                        print(f"     错误: {result['error']}")

        # 保存详细报告
        report_file = self.project_path / "api_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": passed_tests/total_tests*100
                },
                "results": self.test_results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n详细报告已保存到: {report_file}")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="完整API接口测试")
    parser.add_argument("--project-path", default=".", help="项目路径")
    args = parser.parse_args()

    tester = APITester(args.project_path)
    tester.run_all_tests()

if __name__ == "__main__":
    main()