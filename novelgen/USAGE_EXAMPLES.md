# 小说生成器使用示例

本文档提供了更新后的小说生成器系统的详细使用示例。

## 功能概览

### 核心功能
- ✅ **智能导入设定**: 从任意目录导入世界观、角色、环境等设定
- ✅ **显示设定和记忆**: 支持多种格式显示设定内容和记忆片段
- ✅ **智能章节编辑**: 支持本地和AI辅助的章节内容编辑
- ✅ **上下文感知更新**: 维护章节间的一致性和连贯性
- ✅ **AI能力集成**: 预留AI接口，支持内容分析和智能编辑

### AI交互设计
系统采用本地处理+AI客户端的架构：
- **本地处理**: 文件操作、数据管理、流程控制
- **AI客户端**: 内容分析、智能编辑、语义理解

## 使用示例

### 1. 导入设定功能

#### 1.1 扫描目录内容
```bash
# 使用ImportManager直接扫描
python3 scripts/import_manager.py --action scan-directory --target-directory ./source_materials

# 使用统一API
python3 scripts/unified_api.py --request-json '{
  "action": "import.scan_directory",
  "target_directory": "./source_materials"
}'
```

#### 1.2 从目录导入设定（需要AI分析）
```bash
# 导入所有类型的设定
python3 scripts/unified_api.py --request-json '{
  "action": "import.from_directory",
  "target_directory": "./source_materials"
}'

# 只导入角色设定
python3 scripts/unified_api.py --request-json '{
  "action": "import.from_directory",
  "target_directory": "./source_materials",
  "specific_setting": "character"
}'
```

#### 1.3 处理AI分析结果
当系统返回 `ai_task_required` 状态时，客户端需要：
1. 获取AI任务请求
2. 调用AI进行分析
3. 将结果返回给系统

```python
# Python示例
import requests
import json

# 1. 获取AI任务请求
result = api.process_request({
    "action": "import.from_directory",
    "target_directory": "./source_materials"
})

if result["status"] == "ai_task_required":
    # 2. 调用AI分析（示例）
    ai_result = call_your_ai_service(result["ai_task"])

    # 3. 处理AI分析结果
    final_result = api.process_request({
        "action": "import.process_ai_result",
        "ai_result": ai_result
    })
```

### 2. 显示设定功能

#### 2.1 显示世界观设定
```bash
# 可读格式
python3 scripts/settings_display_manager.py --type worldview --format readable

# JSON格式
python3 scripts/unified_api.py --request-json '{
  "action": "display.setting",
  "setting_type": "worldview",
  "format_type": "json"
}'

# 摘要格式（需要AI）
python3 scripts/unified_api.py --request-json '{
  "action": "display.setting",
  "setting_type": "worldview",
  "format_type": "summary"
}'
```

#### 2.2 显示角色设定
```bash
# 显示所有角色
python3 scripts/settings_display_manager.py --type character --format readable

# 显示特定角色
python3 scripts/unified_api.py --request-json '{
  "action": "display.setting",
  "setting_type": "character",
  "setting_name": "张三",
  "format_type": "readable"
}'
```

#### 2.3 显示记忆内容
```bash
# 显示角色所有记忆
python3 scripts/memory_display_manager.py --identifier "张三" --type character_all

# 显示记忆时间线
python3 scripts/unified_api.py --request-json '{
  "action": "display.memory",
  "identifier": "张三",
  "segment_type": "timeline",
  "display_format": "timeline"
}'

# 显示特定记忆（通过记忆ID）
python3 scripts/unified_api.py --request-json '{
  "action": "display.memory",
  "identifier": "abc12345",
  "segment_type": "single",
  "display_format": "readable"
}'
```

### 3. 章节编辑功能

#### 3.1 创建章节
```bash
# 基本创建
python3 scripts/unified_api.py --request-json '{
  "action": "chapter.create",
  "chapter_number": 1,
  "title": "第一章：初遇",
  "context_summary": "主角初次遇到重要角色的场景"
}'
```

#### 3.2 本地智能编辑
```bash
# 追加内容
python3 scripts/unified_api.py --request-json '{
  "action": "chapter.intelligent_edit",
  "chapter_number": 1,
  "edit_request": {
    "content": "这是要追加的新内容...",
    "edit_mode": "append",
    "requires_ai": false
  }
}'

# 插入内容到指定位置
python3 scripts/unified_api.py --request-json '{
  "action": "chapter.intelligent_edit",
  "chapter_number": 1,
  "edit_request": {
    "content": "要插入的内容...",
    "edit_mode": "insert",
    "position": 100,
    "requires_ai": false
  }
}'
```

#### 3.3 AI辅助编辑
```bash
# AI改进内容
python3 scripts/unified_api.py --request-json '{
  "action": "chapter.intelligent_edit",
  "chapter_number": 1,
  "edit_request": {
    "edit_instructions": "请让这段文字更加生动有趣，增加对话",
    "edit_mode": "improve",
    "requires_ai": true
  }
}'
```

#### 3.4 上下文更新
```bash
# 更新章节上下文
python3 scripts/unified_api.py --request-json '{
  "action": "chapter.context_update",
  "chapter_number": 1,
  "context_update": {
    "previous_chapter_summary": "前一章主要讲述了主角的成长背景",
    "current_chapter_focus": "本章重点是主角面临的第一个挑战",
    "next_chapter_preview": "下一章将介绍新的重要角色"
  }
}'
```

### 4. 系统状态查看
```bash
# 查看系统整体状态
python3 scripts/unified_api.py --request-json '{
  "action": "system.status"
}'

# 查看可用设定
python3 scripts/unified_api.py --request-json '{
  "action": "display.available_settings"
}'
```

## AI集成示例

### 客户端AI处理流程

```python
class AIClient:
    def process_ai_task(self, ai_task):
        """处理AI任务"""
        task_type = ai_task["task_type"]

        if task_type == "content_analysis":
            return self.analyze_content(ai_task)
        elif task_type == "content_edit":
            return self.edit_content(ai_task)
        elif task_type == "generate_summary":
            return self.generate_summary(ai_task)
        else:
            return {"status": "error", "message": f"不支持的任务类型: {task_type}"}

    def analyze_content(self, task):
        """分析内容并提取设定"""
        files = task["files"]

        # 调用你的AI服务分析文件内容
        # 示例返回结果
        return {
            "status": "success",
            "analysis_summary": "成功提取了世界观和角色设定",
            "extracted_settings": {
                "worldview": [{
                    "world_name": "魔法世界",
                    "era": "中世纪",
                    "technology_level": "魔法科技",
                    "geography": "分为北境和南境的大陆"
                }],
                "character": [{
                    "name": "张三",
                    "personality": "勇敢善良",
                    "background": "普通家庭出身",
                    "type": "main"
                }]
            }
        }

    def edit_content(self, task):
        """编辑内容"""
        existing_content = task["existing_content"]
        edit_instructions = task["edit_instructions"]

        # 调用你的AI服务编辑内容
        # 示例返回结果
        return {
            "status": "success",
            "edited_content": "这是经过AI改进的内容...",
            "edit_summary": "改进了语言表达，增加了生动描述"
        }
```

### 完整工作流示例

```python
from unified_api import UnifiedAPI
from your_ai_client import AIClient

def complete_import_workflow():
    """完整的导入工作流"""
    api = UnifiedAPI("./my_novel_project")
    ai_client = AIClient()

    # 1. 扫描源文件
    scan_result = api.process_request({
        "action": "import.scan_directory",
        "target_directory": "./source_materials"
    })

    if scan_result["status"] != "success":
        print(f"扫描失败: {scan_result['message']}")
        return

    # 2. 请求AI分析
    import_result = api.process_request({
        "action": "import.from_directory",
        "target_directory": "./source_materials"
    })

    # 3. 处理AI任务
    if import_result["status"] == "ai_task_required":
        ai_result = ai_client.process_ai_task(import_result["ai_task"])

        # 4. 应用AI分析结果
        final_result = api.process_request({
            "action": "import.process_ai_result",
            "ai_result": ai_result
        })

        print(f"导入完成: {final_result['message']}")
        print(f"更新了 {final_result['total_updated']} 个设定")
    else:
        print(f"导入失败: {import_result['message']}")

def complete_chapter_edit_workflow():
    """完整的章节编辑工作流"""
    api = UnifiedAPI("./my_novel_project")
    ai_client = AIClient()

    # 1. 请求AI编辑
    edit_result = api.process_request({
        "action": "chapter.intelligent_edit",
        "chapter_number": 1,
        "edit_request": {
            "edit_instructions": "请让这段文字更加生动有趣",
            "requires_ai": True
        }
    })

    # 2. 处理AI任务
    if edit_result["status"] == "ai_task_required":
        ai_result = ai_client.process_ai_task(edit_result["ai_task"])

        # 3. 应用AI编辑结果
        final_result = api.process_request({
            "action": "chapter.process_ai_edit",
            "chapter_number": 1,
            "ai_result": ai_result
        })

        print(f"编辑完成: {final_result['message']}")
        print(f"AI编辑摘要: {final_result.get('ai_edit_summary', '无')}")
    else:
        print(f"编辑失败: {edit_result['message']}")
```

## 注意事项

### 1. AI能力集成
- 系统设计了标准的AI任务请求格式
- 客户端需要实现具体的AI服务调用
- 支持多种AI服务提供商

### 2. 数据格式
- 所有交互使用JSON格式
- 统一的错误处理和状态返回
- 支持中文内容（UTF-8编码）

### 3. 文件管理
- 自动创建必要的目录结构
- 同时维护JSON和Markdown格式的文件
- 支持版本控制和备份

### 4. 扩展性
- 模块化设计，易于添加新功能
- 统一的API接口，便于集成
- 支持自定义数据管理器

这个更新后的系统为您提供了强大的小说创作工具，支持智能导入、灵活编辑和AI辅助创作。您可以根据具体需求选择合适的功能组合。