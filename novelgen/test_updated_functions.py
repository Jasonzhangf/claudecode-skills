#!/usr/bin/env python3
"""
测试更新后的功能
验证所有新增和修改的功能是否正常工作
"""

import json
import sys
from pathlib import Path

# 添加脚本目录到路径
sys.path.append(str(Path(__file__).parent / "scripts"))

from unified_api import UnifiedAPI

def test_import_functionality():
    """测试导入功能"""
    print("=" * 50)
    print("测试导入功能")
    print("=" * 50)

    api = UnifiedAPI()

    # 测试系统状态
    print("1. 获取系统状态...")
    status_request = {"action": "system.status"}
    status_result = api.process_request(status_request)
    print(f"系统状态: {status_result['status']}")
    if status_result['status'] == 'success':
        print(f"项目路径: {status_result['project_path']}")
        print(f"可用功能: {', '.join(status_result['features_available'])}")

    # 测试目录扫描（创建测试目录）
    print("\n2. 测试目录扫描...")
    test_dir = Path("test_import_data")
    test_dir.mkdir(exist_ok=True)

    # 创建测试文件
    test_file = test_dir / "test_worldview.md"
    test_file.write_text("""# 测试世界观

## 基本信息
- **世界名称**: 测试世界
- **时代背景**: 魔法时代
- **技术水平**: 中等魔法

## 地理环境
这是一个充满魔法的大陆，分为北境和南境。

## 魔法系统
元素魔法是这个世界的主要力量来源。
""", encoding='utf-8')

    # 测试扫描
    scan_request = {
        "action": "import.scan_directory",
        "target_directory": str(test_dir)
    }
    scan_result = api.process_request(scan_request)
    print(f"目录扫描: {scan_result['status']}")
    if scan_result['status'] == 'success':
        print(f"找到文件数: {scan_result['total_files']}")
        print(f"文件列表: {[f['name'] for f in scan_result['found_files']]}")

    # 测试导入（这会返回AI任务请求）
    print("\n3. 测试导入请求...")
    import_request = {
        "action": "import.from_directory",
        "target_directory": str(test_dir)
    }
    import_result = api.process_request(import_request)
    print(f"导入请求: {import_result['status']}")
    if import_result['status'] == 'ai_task_required':
        print("需要AI处理 - 正确返回了AI任务请求")
        print(f"AI任务类型: {import_result['ai_task']['task_type']}")
        print(f"文件数量: {import_result['local_data']['files_found']}")

def test_display_functionality():
    """测试显示功能"""
    print("\n" + "=" * 50)
    print("测试显示功能")
    print("=" * 50)

    api = UnifiedAPI()

    # 测试显示可用设定
    print("1. 显示可用设定...")
    display_request = {
        "action": "display.available_settings"
    }
    display_result = api.process_request(display_request)
    print(f"显示可用设定: {display_result['status']}")

    # 测试显示世界观
    print("\n2. 显示世界观设定...")
    worldview_request = {
        "action": "display.setting",
        "setting_type": "worldview",
        "format_type": "readable"
    }
    worldview_result = api.process_request(worldview_request)
    print(f"世界观显示: {worldview_result['status']}")
    if worldview_result['status'] == 'success':
        print(f"显示标题: {worldview_result.get('display_title', '无')}")
        print(f"内容长度: {len(worldview_result.get('content', ''))}")
    elif worldview_result['status'] == 'error':
        print(f"错误信息: {worldview_result['message']}")

def test_chapter_functionality():
    """测试章节功能"""
    print("\n" + "=" * 50)
    print("测试章节功能")
    print("=" * 50)

    api = UnifiedAPI()

    # 测试创建章节
    print("1. 创建章节...")
    create_request = {
        "action": "chapter.create",
        "chapter_number": 1,
        "title": "测试章节",
        "context_summary": "这是一个测试章节"
    }
    create_result = api.process_request(create_request)
    print(f"创建章节: {create_result['status']}")
    if create_result['status'] == 'success':
        print(f"章节号: {create_result['chapter']}")
        print(f"标题: {create_result['title']}")

    # 测试获取章节内容
    print("\n2. 获取章节内容...")
    content_request = {
        "action": "chapter.get_content",
        "chapter_number": 1
    }
    content_result = api.process_request(content_request)
    print(f"获取内容: {content_result['status']}")
    if content_result['status'] == 'success':
        print(f"JSON文件存在: {content_result['json_file']}")
        print(f"MD文件存在: {content_result['md_exists']}")

    # 测试智能编辑（本地模式）
    print("\n3. 测试智能编辑（本地模式）...")
    edit_request = {
        "action": "chapter.intelligent_edit",
        "chapter_number": 1,
        "edit_request": {
            "content": "这是新增的章节内容。\n\n章节内容正在更新中...",
            "edit_mode": "append",
            "requires_ai": False
        }
    }
    edit_result = api.process_request(edit_request)
    print(f"智能编辑: {edit_result['status']}")
    if edit_result['status'] == 'success':
        print(f"更新字数: {edit_result['word_count']}")

    # 测试智能编辑（AI模式）
    print("\n4. 测试智能编辑（AI模式）...")
    ai_edit_request = {
        "action": "chapter.intelligent_edit",
        "chapter_number": 1,
        "edit_request": {
            "edit_instructions": "请改进这段文字的表达",
            "edit_mode": "improve",
            "requires_ai": True
        }
    }
    ai_edit_result = api.process_request(ai_edit_request)
    print(f"AI编辑请求: {ai_edit_result['status']}")
    if ai_edit_result['status'] == 'ai_task_required':
        print("需要AI处理 - 正确返回了AI任务请求")
        print(f"AI任务类型: {ai_edit_result['ai_task']['task_type']}")

    # 测试上下文更新
    print("\n5. 测试上下文更新...")
    context_request = {
        "action": "chapter.context_update",
        "chapter_number": 1,
        "context_update": {
            "current_chapter_focus": "主要角色的成长历程",
            "previous_chapter_summary": "主角初次接触魔法世界",
            "next_chapter_preview": "主角将面临第一个挑战"
        }
    }
    context_result = api.process_request(context_request)
    print(f"上下文更新: {context_result['status']}")
    if context_result['status'] == 'success':
        print(f"更新的上下文: {context_result['updated_context']}")

def test_memory_functionality():
    """测试记忆功能"""
    print("\n" + "=" * 50)
    print("测试记忆功能")
    print("=" * 50)

    api = UnifiedAPI()

    # 测试记忆统计
    print("1. 获取记忆统计...")
    stats_request = {
        "action": "display.memory_stats"
    }
    stats_result = api.process_request(stats_request)
    print(f"记忆统计: {stats_result['status']}")
    if stats_result['status'] == 'success':
        print(f"总角色数: {stats_result.get('total_characters', 0)}")
        print(f"总记忆数: {stats_result.get('total_memories', 0)}")

    # 测试显示角色记忆
    print("\n2. 显示角色记忆...")
    memory_request = {
        "action": "display.memory",
        "identifier": "测试角色",
        "segment_type": "character_all",
        "display_format": "readable"
    }
    memory_result = api.process_request(memory_request)
    print(f"显示记忆: {memory_result['status']}")
    if memory_result['status'] == 'success':
        print(f"角色名: {memory_result['character']}")
        print(f"记忆数量: {memory_result['total_count']}")
    elif memory_result['status'] == 'error':
        print(f"错误信息: {memory_result['message']}")

def test_ai_integration():
    """测试AI集成"""
    print("\n" + "=" * 50)
    print("测试AI集成")
    print("=" * 50)

    api = UnifiedAPI()

    # 测试内容分析请求
    print("1. 测试内容分析请求...")
    analysis_request = {
        "action": "ai.analyze_content",
        "files": [
            {
                "name": "test.txt",
                "content": "这是一个测试文件，包含一些角色和世界观信息。"
            }
        ],
        "analysis_type": "setting_extraction"
    }
    analysis_result = api.process_request(analysis_request)
    print(f"内容分析请求: {analysis_result['status']}")
    if analysis_result['status'] == 'ai_task_required':
        print("需要AI处理 - 正确返回了AI任务请求")
        print(f"AI任务类型: {analysis_result['ai_task']['task_type']}")

    # 测试内容编辑请求
    print("\n2. 测试内容编辑请求...")
    edit_request = {
        "action": "ai.edit_content",
        "existing_content": "这是一段需要改进的文字。",
        "edit_instructions": "请让这段文字更加生动有趣",
        "edit_mode": "improve"
    }
    edit_result = api.process_request(edit_request)
    print(f"内容编辑请求: {edit_result['status']}")
    if edit_result['status'] == 'ai_task_required':
        print("需要AI处理 - 正确返回了AI任务请求")
        print(f"AI任务类型: {edit_result['ai_task']['task_type']}")

def cleanup():
    """清理测试数据"""
    print("\n" + "=" * 50)
    print("清理测试数据")
    print("=" * 50)

    # 删除测试目录
    import shutil
    test_dir = Path("test_import_data")
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("已删除测试目录")

    # 删除测试章节（如果存在）
    draft_dir = Path("draft/chapters")
    if draft_dir.exists():
        chapter_1_dir = draft_dir / "chapter_01"
        if chapter_1_dir.exists():
            shutil.rmtree(chapter_1_dir)
            print("已删除测试章节")

def main():
    """主测试函数"""
    print("开始测试更新后的功能...")
    print("注意：某些功能会返回AI任务请求，这是正常的行为")

    try:
        # 运行各项测试
        test_import_functionality()
        test_display_functionality()
        test_chapter_functionality()
        test_memory_functionality()
        test_ai_integration()

        print("\n" + "=" * 50)
        print("所有测试完成!")
        print("=" * 50)

    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理测试数据
        cleanup()

if __name__ == "__main__":
    main()