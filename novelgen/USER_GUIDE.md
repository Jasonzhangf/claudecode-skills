# 小说生成器技能使用指南 v2.0

## 🚀 快速开始

### 安装技能
1. 下载 `novelgen-v2.0.0.zip`
2. 解压到 `~/.claude/skills/novelgen/`
3. 运行 `./install.sh`

### 验证安装
```bash
cd ~/.claude/skills/novelgen
python3 scripts/unified_api.py --request-json '{"action": "system.status"}'
```

## 📖 基本使用流程

### 第一步：创建项目
```bash
mkdir my-novel-project
cd my-novel-project
```

### 第二步：创建设定
```bash
# 创建世界观
python3 ~/.claude/skills/novelgen/scripts/data_managers/worldbuilder.py --action create

# 创建角色
python3 ~/.claude/skills/novelgen/scripts/data_managers/character_manager.py --action create --name "主角" --type main

# 创建环境设定
python3 ~/.claude/skills/novelgen/scripts/data_managers/environment_manager.py --action create
```

### 第三步：查看设定
```bash
# 显示所有设定
python3 ~/.claude/skills/novelgen/scripts/settings_display_manager.py --action list

# 显示世界观
python3 ~/.claude/skills/novelgen/scripts/settings_display_manager.py --type worldview

# 显示角色
python3 ~/.claude/skills/novelgen/scripts/settings_display_manager.py --type character
```

## 🆕 v2.0新功能使用

### 1. 完整交互式工作流程 ⭐ 推荐
```bash
# 开始文章创作（完整流程）
python3 ~/.claude/skills/novelgen/scripts/unified_api.py --request-json '{"action": "workflow.create_article"}'

# 获取工作流程进度
python3 ~/.claude/skills/novelgen/scripts/unified_api.py --request-json '{"action": "workflow.get_progress"}'
```

### 2. 智能导入设定
```bash
# 扫描并导入所有设定
python3 ~/.claude/skills/novelgen/scripts/unified_api.py --request-json '{
  "action": "import.from_directory",
  "target_directory": "./materials"
}'

# 导入特定类型设定
python3 ~/.claude/skills/novelgen/scripts/unified_api.py --request-json '{
  "action": "import.from_directory",
  "target_directory": "./materials",
  "specific_setting": "character"
}'
```

### 3. 设定完整性检查
```bash
# 检查设定完整性
python3 ~/.claude/skills/novelgen/scripts/unified_api.py --request-json '{"action": "settings.check_completeness"}'

# 获取用户引导
python3 ~/.claude/skills/novelgen/scripts/unified_api.py --request-json '{"action": "settings.get_guidance"}'
```

### 4. 章节准备和创作
```bash
# 准备章节创作
python3 ~/.claude/skills/novelgen/scripts/unified_api.py --request-json '{
  "action": "outline.prepare_creation",
  "chapter_number": 2
}'

# 生成章节梗概建议
python3 ~/.claude/skills/novelgen/scripts/unified_api.py --request-json '{
  "action": "outline.generate_suggestions",
  "chapter_number": 2
}'

# 保存章节梗概
python3 ~/.claude/skills/novelgen/scripts/unified_api.py --request-json '{
  "action": "outline.save",
  "chapter_number": 2,
  "outline_data": {
    "title": "第二章标题",
    "description": "章节描述...",
    "key_scenes": [...]
  }
}'
```

### 5. 章节记忆分析
```bash
# 分析第1章内容
python3 ~/.claude/skills/novelgen/scripts/chapter_memory_analyzer.py --action analyze --chapter 1

# 应用生成的记忆
python3 ~/.claude/skills/novelgen/scripts/chapter_memory_analyzer.py --action apply --chapter 1

# 查看记忆分析信息
python3 ~/.claude/skills/novelgen/scripts/chapter_memory_analyzer.py --action info --chapter 1
```

### 6. 章节审阅和批准
```bash
# 审阅章节
python3 ~/.claude/skills/novelgen/scripts/unified_api.py --request-json '{
  "action": "workflow.review_chapter",
  "chapter_number": 2
}'

# 批准章节为成品
python3 ~/.claude/skills/novelgen/scripts/unified_api.py --request-json '{
  "action": "workflow.approve_chapter",
  "chapter_number": 2,
  "approval_data": {
    "approved_by": "用户名",
    "approval_notes": "章节质量很好"
  }
}'
```

### 7. 智能编辑章节
```bash
# 追加内容
python3 ~/.claude/skills/novelgen/scripts/unified_api.py --request-json '{
  "action": "chapter.intelligent_edit",
  "chapter_number": 1,
  "edit_request": {
    "content": "这是新增加的内容...",
    "edit_mode": "append",
    "requires_ai": false
  }
}'

# AI辅助编辑
python3 ~/.claude/skills/novelgen/scripts/unified_api.py --request-json '{
  "action": "chapter.intelligent_edit",
  "chapter_number": 1,
  "edit_request": {
    "edit_instructions": "请改进这段文字的表达",
    "requires_ai": true
  }
}'
```

### 8. 记忆管理
```bash
# 显示角色记忆
python3 ~/.claude/skills/novelgen/scripts/memory_display_manager.py --identifier "角色名" --type character_all

# 显示记忆时间线
python3 ~/.claude/skills/novelgen/scripts/memory_display_manager.py --identifier "角色名" --type timeline

# 获取记忆统计
python3 ~/.claude/skills/novelgen/scripts/memory_display_manager.py --action stats --identifier "角色名"
```

## 🔧 完整功能列表

### 统一API接口
```bash
# 系统状态
python3 scripts/unified_api.py --request-json '{"action": "system.status"}'

# 导入设定
python3 scripts/unified_api.py --request-json '{"action": "import.from_directory", "target_directory": "./路径"}'

# 显示设定
python3 scripts/unified_api.py --request-json '{"action": "display.setting", "setting_type": "worldview"}'

# 显示记忆
python3 scripts/unified_api.py --request-json '{"action": "display.memory", "identifier": "角色名"}'

# 章节操作
python3 scripts/unified_api.py --request-json '{"action": "chapter.create", "chapter_number": 1, "title": "第一章"}'
python3 scripts/unified_api.py --request-json '{"action": "chapter.get_content", "chapter_number": 1}'
python3 scripts/unified_api.py --request-json '{"action": "chapter.intelligent_edit", "chapter_number": 1, "edit_request": {...}}'
```

### 数据管理器
```bash
# 世界观管理
python3 scripts/data_managers/worldbuilder.py --action create
python3 scripts/data_managers/worldbuilder.py --action load
python3 scripts/data_managers/worldbuilder.py --action list

# 角色管理
python3 scripts/data_managers/character_manager.py --action create --name "角色名" --type main
python3 scripts/data_managers/character_manager.py --action load --name "角色名"
python3 scripts/data_managers/character_manager.py --action list

# 记忆管理
python3 scripts/data_managers/memory_manager.py --action add --character "角色名" --content "记忆内容"
python3 scripts/data_managers/memory_manager.py --action list --character "角色名"
```

## 📁 项目结构

技能会在当前目录创建标准项目结构：
```
项目目录/
├── settings/              # 设定文件
│   ├── worldview/         # 世界观设定
│   ├── characters/        # 角色设定
│   ├── environments/      # 环境设定
│   ├── plot/             # 情节设定
│   └── writing_style/    # 写作风格
├── draft/                 # 草稿章节
│   └── chapters/         # 章节草稿
├── manuscript/           # 完成章节
│   └── chapters/         # 最终章节
├── system/               # 系统文件
│   ├── chapter_index.json
│   └── context_config.json
└── progress/             # 进度记录
    └── chapter_status.json
```

## ⚠️ 常见问题解决

### 1. Python路径问题
```bash
# 使用python3而不是python
python3 scripts/unified_api.py ...

# 或者指定完整路径
/usr/bin/python3 ~/.claude/skills/novelgen/scripts/unified_api.py ...
```

### 2. 权限问题
```bash
# 设置执行权限
chmod +x ~/.claude/skills/novelgen/scripts/*.py
chmod +x ~/.claude/skills/novelgen/scripts/data_managers/*.py
```

### 3. 模块导入错误
```bash
# 确保在正确目录
cd ~/.claude/skills/novelgen
python3 scripts/unified_api.py --request-json '{"action": "system.status"}'
```

### 4. 章节不存在的错误
确保有对应的JSON文件：
```bash
# 检查章节文件
ls draft/chapters/chapter_01/
# 应该看到 chapter_01.json 和 chapter_01.md
```

## 🎯 AI集成说明

系统采用**本地处理 + AI客户端**架构：

### AI任务类型
- `content_analysis`: 内容分析和设定提取
- `content_edit`: 智能内容编辑
- `generate_summary`: 生成内容摘要

### AI交互流程
1. 系统返回 `ai_task_required` 状态
2. 客户端获取AI任务请求
3. 调用AI服务处理
4. 将结果返回给系统

## 📚 相关文档

- `SKILL.md` - 完整功能介绍
- `USAGE_EXAMPLES.md` - 详细使用示例
- `CHANGELOG_V2.md` - v2.0更新日志
- `INSTALLATION.md` - 安装指南

---

🎉 开始你的小说创作之旅！