#!/usr/bin/env python3
"""
章节记忆分析功能演示
展示如何自动从章节内容生成人物记忆
"""

import sys
import json
from pathlib import Path

# 添加脚本路径
sys.path.append(str(Path(__file__).parent / "scripts"))

from unified_api import UnifiedAPI

def demo_chapter_memory_analysis():
    """演示章节记忆分析功能"""

    print("=" * 60)
    print("🧠 章节记忆分析功能演示")
    print("=" * 60)

    # 初始化API
    project_path = "/Users/fanzhang/Documents/novel/evolve"  # 您的测试项目路径
    api = UnifiedAPI(project_path)

    print(f"📁 项目路径: {project_path}")
    print()

    # 1. 查看系统状态
    print("🔍 1. 查看系统状态...")
    status_request = {"action": "system.status"}
    status_result = api.process_request(status_request)

    if status_result["status"] == "success":
        print("✅ 系统状态正常")
        print(f"   可用功能: {', '.join(status_result['features_available'])}")
    else:
        print(f"❌ 系统状态异常: {status_result['message']}")
        return

    print()

    # 2. 检查是否有章节内容
    print("📚 2. 检查章节内容...")
    chapters_found = []

    draft_dir = Path(project_path) / "draft" / "chapters"
    if draft_dir.exists():
        for chapter_dir in draft_dir.iterdir():
            if chapter_dir.is_dir() and chapter_dir.name.startswith("chapter_"):
                chapter_file = chapter_dir / f"{chapter_dir.name}.json"
                if chapter_file.exists():
                    chapters_found.append(int(chapter_dir.name.split("_")[1]))

    if not chapters_found:
        print("❌ 未找到章节内容，请先创建章节")
        return

    print(f"✅ 找到章节: {sorted(chapters_found)}")
    print()

    # 3. 分析章节内容生成记忆
    target_chapter = min(chapters_found)  # 使用第一个章节
    print(f"🧠 3. 分析第{target_chapter}章生成记忆...")

    # 先分析章节内容
    analyze_request = {
        "action": "chapter.analyze_memory",
        "chapter_number": target_chapter
    }

    analyze_result = api.process_request(analyze_request)

    if analyze_result["status"] == "success":
        print("✅ 章节分析完成")
        print(f"   章节号: {analyze_result['chapter_number']}")
        print(f"   发现角色: {analyze_result['characters_found']}")
        print(f"   分析结果:")
        print(f"     - 角色行为: {len(analyze_result['analysis_result']['character_actions'])}")
        print(f"     - 角色情感: {len(analyze_result['analysis_result']['character_emotions'])}")
        print(f"     - 角色关系: {len(analyze_result['analysis_result']['character_relationships'])}")
        print(f"     - 角色冲突: {len(analyze_result['analysis_result']['character_conflicts'])}")
        print(f"     - 角色成长: {len(analyze_result['analysis_result']['character_growth'])}")
        print(f"   将生成记忆: {analyze_result['memory_generation']['total_generated']}条")
    else:
        print(f"❌ 章节分析失败: {analyze_result['message']}")
        return

    print()

    # 4. 生成并应用记忆
    print("💾 4. 生成并应用记忆...")
    generate_request = {
        "action": "chapter.generate_memory",
        "chapter_number": target_chapter,
        "auto_confirm": True
    }

    generate_result = api.process_request(generate_request)

    if generate_result["status"] == "success":
        print("✅ 记忆生成和应用完成")
        print(f"   章节号: {generate_result['chapter_number']}")
        print(f"   总生成: {generate_result['total_generated']}条")
        print(f"   成功应用: {generate_result['total_applied']}条")
        print(f"   失败数量: {generate_result['failed_count']}条")

        if generate_result['failed_memories']:
            print("   失败详情:")
            for failed in generate_result['failed_memories']:
                print(f"     - {failed['character']}: {failed['error']}")
    else:
        print(f"❌ 记忆生成失败: {generate_result['message']}")
        return

    print()

    # 5. 验证记忆结果
    print("🔍 5. 验证记忆结果...")

    # 获取角色列表
    characters_result = api.process_request({
        "action": "display.setting",
        "setting_type": "character",
        "format_type": "readable"
    })

    if characters_result["status"] == "success":
        characters = characters_result.get("data", {}).get("characters", [])
        print(f"✅ 当前角色数量: {len(characters)}")

        for char in characters[:3]:  # 显示前3个角色的记忆
            char_name = char.get("name", "未知角色")

            memory_request = {
                "action": "display.memory",
                "identifier": char_name,
                "segment_type": "character_all",
                "display_format": "readable"
            }

            memory_result = api.process_request(memory_request)

            if memory_result["status"] == "success":
                print(f"   📖 {char_name}: {memory_result['total_count']}条记忆")

                # 显示记忆类型统计
                memory_types = set()
                for memory in memory_result.get("content", "").split("## "):
                    if memory.strip() and not memory.startswith("##"):
                        memory_types.add("其他记忆")
                    elif memory.strip().startswith("## "):
                        memory_type = memory.strip().split(":")[0].replace("## ", "")
                        memory_types.add(memory_type)

                if memory_types:
                    print(f"      类型: {', '.join(memory_types)}")
            else:
                print(f"   ❌ {char_name}: 获取记忆失败")

    print()
    print("🎉 演示完成！")
    print()
    print("💡 新功能特点:")
    print("   ✅ 自动解析章节内容")
    print("   ✅ 识别角色行为、情感、关系")
    print("   ✅ 生成多种类型记忆（情感、行动、关系、冲突、成长）")
    print("   ✅ 自动计算情感权重")
    print("   ✅ 保存到记忆系统")
    print("   ✅ 支持人物关系网络")

def create_demo_chapter_content():
    """创建演示章节内容"""

    demo_content = '''
# 第一章：初次相遇

在一个普通的咖啡馆里，林明正在安静地阅读着最新的科技期刊。突然，他听到了熟悉的声音。

"林明？真的是你吗？"

林明抬头一看，惊讶地发现是多年未见的老同学张伟。"张伟！好久不见！"林明高兴地站起来。

"是啊，我最近在AI公司工作。"张伟笑着说，"你呢？还是做研究？"

林明点点头，但心里有些复杂。他们曾经是好朋友，但因为一次研究项目的分歧，两人关系变得紧张。

"我现在在生物科技公司工作。"林明说道，"我们在做一些很有意思的基因编辑研究。"

张伟的表情变得严肃起来。"我听说你们公司在做一些有争议的研究。"

"我们只是在追求科学进步。"林明辩解道，"而且我们有很多安全措施。"

"安全措施？"张伟冷笑，"我听说你们在做一些跨物种实验。"

林明感到一阵愤怒。张伟总是这样，不理解他们的工作。"你根本不了解我们的研究！"

咖啡馆里的其他客人都看向他们。林明意识到自己太激动了，深呼吸了一下。

"对不起，我失态了。"林明坐下说，"但是我们的研究是为了人类的未来。"

张伟叹了口气。"好吧，我不太懂这些技术。但希望你们真的知道自己在做什么。"

两人陷入了沉默。林明想起了他们的大学时光，那时他们一起梦想着改变世界。现在，他们似乎在用不同的方式追求着这个目标。

"我们的AI系统遇到了瓶颈。"张伟突然说，"它无法真正理解和创造。"

"这很有趣。"林明眼前一亮，"也许我们的生物技术可以帮上忙。"

他们开始讨论合作的可能性。林明感到一种久违的兴奋，也许这是修复他们友谊的机会。

"我们需要一个能够理解复杂生物系统的AI。"张伟说，"而你们有生物数据。"

"我们有基因编辑技术，但需要更智能的分析工具。"林明回应道。

他们讨论了几个小时，咖啡馆即将关门。离开时，张伟说："也许我们可以重新开始合作。"

林明点了点头，心中充满了希望。这可能是他们友谊和事业的新起点。
'''

    project_path = "/Users/fanzhang/Documents/novel/evolve"

    # 确保目录存在
    draft_dir = Path(project_path) / "draft" / "chapters"
    draft_dir.mkdir(parents=True, exist_ok=True)

    # 创建第一章
    chapter_dir = draft_dir / "chapter_01"
    chapter_dir.mkdir(exist_ok=True)

    chapter_data = {
        "metadata": {
            "chapter": 1,
            "title": "第一章：初次相遇",
            "word_count": len(demo_content),
            "status": "completed",
            "created_at": "2025-10-28T10:30:00",
            "updated_at": "2025-10-28T10:30:00",
            "version": "1.0"
        },
        "content": {
            "sections": [],
            "main_content": demo_content.strip(),
            "dialogues": [],
            "descriptions": [],
            "notes": []
        },
        "context": {
            "previous_chapter_summary": "",
            "current_chapter_focus": "老友重逢，讨论技术合作",
            "next_chapter_preview": "开始探索AI与生物技术的结合"
        },
        "editing": {
            "last_modified_by": "system",
            "edit_history": [],
            "word_target": 2000,
            "progress_percentage": 0
        }
    }

    # 保存章节数据
    chapter_file = chapter_dir / "chapter_01.json"
    with open(chapter_file, 'w', encoding='utf-8') as f:
        json.dump(chapter_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 创建演示章节: {chapter_file}")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="章节记忆分析功能演示")
    parser.add_argument("--create-demo", action="store_true", help="创建演示章节内容")
    parser.add_argument("--project-path", default="/Users/fanzhang/Documents/novel/evolve",
                       help="项目路径")

    args = parser.parse_args()

    if args.create_demo:
        print("🔧 创建演示章节内容...")
        create_demo_chapter_content()
        print()

    demo_chapter_memory_analysis()

if __name__ == "__main__":
    main()