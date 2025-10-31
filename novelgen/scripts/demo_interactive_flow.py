#!/usr/bin/env python3
"""
交互式小说生成流程演示
展示完整的智能状态检查、进度判断和用户交互流程
"""

import sys
from pathlib import Path

# 添加技能目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from novel_generator import NovelGenerator

def demo_interactive_flow():
    """演示交互式流程"""
    print("🎨 NovelGen - 交互式小说生成器演示")
    print("=" * 60)

    # 初始化生成器
    project_path = "/Users/fanzhang/Documents/novel/进化"
    generator = NovelGenerator(project_path)

    print(f"📁 项目路径: {project_path}")
    print()

    # 步骤1: 检查项目状态
    print("📊 步骤1: 检查项目状态")
    print("-" * 30)
    project_status = generator.check_project_status()

    print(f"🏗️  项目名称: {project_status['project_name']}")
    print(f"📅 检查时间: {project_status['check_time']}")
    print(f"📋 整体状态: {project_status['overall_status']}")

    # 显示各组件状态
    for component, status in project_status['components'].items():
        status_icon = "✅" if status.get('status') == 'success' else "❌"
        message = status.get('message', '状态未知')
        print(f"   {status_icon} {component}: {message}")

    print()

    # 步骤2: 分析创作进度
    print("📈 步骤2: 分析创作进度")
    print("-" * 30)
    progress = generator.get_current_progress()

    print(f"📚 当前章节: 第{progress['current_chapter']}章")
    print(f"✅ 已完成章节: {len(progress['existing_chapters'])}章")
    print(f"📋 规划章节: {progress['total_planned']}章")
    print(f"📊 完成进度: {progress['completion_percentage']:.1f}%")
    print(f"🎯 下一步操作: {progress['next_action']}")

    if progress['existing_chapters']:
        print("\n📖 已完成章节详情:")
        for chapter in progress['existing_chapters']:
            print(f"   第{chapter['chapter']}章: {chapter['title']}")
            print(f"      📊 字数: {chapter['word_count']}字")
            print(f"      📅 更新: {chapter['updated_at']}")

    print()

    # 步骤3: 检查生成条件
    current_chapter = progress['current_chapter']
    print(f"🔍 步骤3: 检查第{current_chapter}章生成条件")
    print("-" * 30)

    if progress['next_action'] == 'create_outline':
        print(f"📝 需要创建第{current_chapter}章大纲")
        print("💡 建议操作: outline create-chapter {current_chapter} --title '章节标题'")
    else:
        prerequisites = generator.check_generation_prerequisites(current_chapter)

        if prerequisites['ready']:
            print("✅ 所有生成条件已满足")
            print("🚀 可以开始生成章节内容")
            print("💡 建议操作: generate --chapter {current_chapter}")
        else:
            print("❌ 生成条件不满足:")
            for item in prerequisites['missing_items']:
                print(f"   • {item}")

            print("\n💡 修复建议:")
            for suggestion in prerequisites['suggestions']:
                print(f"   • {suggestion}")

    print()

    # 步骤4: AI模型状态
    print("🤖 步骤4: AI模型状态")
    print("-" * 30)
    ai_info = generator.ai_adapter.get_model_info()
    print(f"🔧 模型类型: {ai_info['type']}")
    print(f"📋 模型名称: {ai_info['model']}")
    print(f"🔑 API配置: {'已配置' if ai_info['api_key_configured'] else '未配置'}")

    print()

    # 步骤5: 智能建议
    print("💡 步骤5: 智能建议")
    print("-" * 30)

    suggestions = []

    # 基于当前状态提供建议
    if project_status['overall_status'] != 'complete':
        suggestions.append("建议先完善项目设定文件，确保世界观、人物、环境等设定完整")

    if progress['completion_percentage'] == 0:
        suggestions.append("建议从第一章开始，先创建大纲，然后生成内容")
    elif progress['completion_percentage'] < 20:
        suggestions.append("建议保持稳定的创作节奏，每完成一章后及时规划下一章大纲")
    elif progress['completion_percentage'] > 80:
        suggestions.append("项目即将完成，建议开始规划结局和收尾工作")

    if progress['next_action'] == 'create_outline':
        suggestions.append(f"当前需要创建第{current_chapter}章大纲，可以使用交互式命令")
    elif prerequisites['ready']:
        suggestions.append(f"所有条件已满足，可以开始生成第{current_chapter}章内容")

    if not ai_info['api_key_configured'] and ai_info['type'] != 'Local':
        suggestions.append("建议配置AI API密钥以获得更好的生成质量，或继续使用本地模拟模式")

    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")

    print()
    print("=" * 60)
    print("🎉 演示完成！")

def demo_user_interaction_scenarios():
    """演示用户交互场景"""
    print("\n🎭 用户交互场景演示")
    print("=" * 60)

    scenarios = [
        {
            "title": "场景1: 新用户首次使用",
            "description": "用户刚刚创建项目，需要从头开始",
            "steps": [
                "系统检查项目状态 → 发现缺少设定文件",
                "提示用户完善世界观、人物等基础设定",
                "协助用户创建第一章大纲",
                "检查生成条件 → 开始生成第一章"
            ]
        },
        {
            "title": "场景2: 继续创作中断的小说",
            "description": "用户之前已经写了部分章节，现在继续创作",
            "steps": [
                "系统分析现有进度 → 识别当前应该写第几章",
                "检查前序章节的连贯性",
                "验证当前章节大纲是否存在",
                "如条件满足 → 提示用户可以开始生成"
            ]
        },
        {
            "title": "场景3: 发现问题需要修复",
            "description": "系统在检查过程中发现问题，需要用户修复",
            "steps": [
                "系统检查生成条件 → 发现缺失组件",
                "明确指出缺失的具体内容",
                "提供详细的修复建议和命令",
                "等待用户修复后重新检查"
            ]
        }
    ]

    for scenario in scenarios:
        print(f"\n📋 {scenario['title']}")
        print(f"📝 {scenario['description']}")
        print("🔄 执行流程:")
        for i, step in enumerate(scenario['steps'], 1):
            print(f"   {i}. {step}")

    print("\n" + "=" * 60)
    print("💡 核心设计理念:")
    print("   • 智能化: 自动判断当前状态和下一步操作")
    print("   • 用户友好: 提供清晰的提示和建议")
    print("   • 容错性: 优雅处理各种异常情况")
    print("   • 渐进式: 引导用户完成整个创作流程")

if __name__ == "__main__":
    demo_interactive_flow()
    demo_user_interaction_scenarios()