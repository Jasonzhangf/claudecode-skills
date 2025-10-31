#!/usr/bin/env python3
"""
交互式问题解决器 - 简化的用户交互入口
提供友好的命令行界面来使用问题分析功能
"""

import sys
import os
from pathlib import Path
from problem_analyzer import ProblemAnalyzer, ProblemType

def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("🔍 Sysmem 交互式问题解决器")
    print("=" * 60)
    print("基于项目架构定义的智能问题分析和解决系统")
    print()

def get_user_query() -> str:
    """获取用户查询"""
    print("请描述您遇到的问题:")
    print("示例:")
    print("- 系统性能很慢，需要优化")
    print("- 某个功能出现错误，需要修复")
    print("- 配置问题导致服务无法启动")
    print("- 架构设计需要调整")
    print()

    while True:
        query = input("问题描述: ").strip()
        if query:
            return query
        print("⚠️ 请输入有效的问题描述")

def confirm_analysis(query: str) -> bool:
    """确认分析"""
    print(f"\n📋 问题摘要:")
    print(f"问题描述: {query}")

    # 自动分类问题
    query_lower = query.lower()
    if any(word in query_lower for word in ['慢', '性能', '卡', '延迟']):
        problem_type = "性能问题"
    elif any(word in query_lower for word in ['错误', '异常', '崩溃', '失败', 'bug']):
        problem_type = "功能问题"
    elif any(word in query_lower for word in ['架构', '设计', '结构']):
        problem_type = "架构问题"
    elif any(word in query_lower for word in ['配置', '设置', '环境']):
        problem_type = "配置问题"
    else:
        problem_type = "其他问题"

    print(f"问题类型: {problem_type}")
    print()

    while True:
        choice = input("是否开始分析? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False
        print("请输入 y 或 n")

def show_progress(step: int, total: int, description: str):
    """显示进度"""
    progress = f"[{step}/{total}]"
    print(f"{progress} {description}")

def main():
    """主函数"""
    print_banner()

    # 获取目标目录
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = "."

    target_path = Path(target_dir).resolve()
    if not target_path.exists():
        print(f"❌ 错误: 目录 '{target_dir}' 不存在")
        sys.exit(1)

    print(f"🎯 目标项目: {target_path}")
    print()

    # 交互式获取用户查询
    query = get_user_query()

    # 确认分析
    if not confirm_analysis(query):
        print("❌ 用户取消分析")
        sys.exit(0)

    # 执行分析
    print("\n🚀 开始问题分析...")
    print("-" * 40)

    try:
        analyzer = ProblemAnalyzer(str(target_path))
        result = analyzer.analyze_problem(query)

        # 显示结果
        print("\n" + "=" * 40)
        print("📊 分析结果")
        print("=" * 40)

        if result["status"] == "cancelled":
            print("❌ 分析被用户取消")
        elif result["final_status"] == "success":
            print("✅ 问题解决成功!")
            if "test_results" in result:
                for test in result["test_results"]:
                    if test.get("success"):
                        print("✅ 测试通过")
        elif result["final_status"] == "success_after_retry":
            print("✅ 问题解决成功 (经过修复)")
            if "fixes_applied" in result:
                print(f"应用的修复: {', '.join(result['fixes_applied'])}")
        else:
            print("❌ 问题解决失败")
            if "error" in result:
                print(f"错误信息: {result['error']}")

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断分析")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 分析过程中出现错误: {e}")
        sys.exit(1)

    print("\n🏁 分析完成")

if __name__ == "__main__":
    main()