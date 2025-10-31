# NovelGen Claude Skill 集成指南

## 🎯 技能概述

NovelGen是一个专为Claude设计的智能小说生成技能，提供完整的小说创作管理功能。技能专注于上下文准备、项目管理和流程控制，AI内容生成由Claude本身处理。

## 🏗️ 系统架构

### 设计理念
- **职责分离**: 技能负责准备和管理，Claude负责创作
- **智能流程**: 自动化状态检查、进度判断和缺失内容提示
- **用户友好**: 清晰的交互式引导和错误处理

### 核心组件
1. **章节生成器** (`chapter_generator.py`) - 七步生成流程，构建完整上下文
2. **大纲管理器** (`outline_manager.py`) - 独立的大纲文件管理系统
3. **Claude集成器** (`claude_integration.py`) - 处理Claude生成内容的保存
4. **交互式管理器** (`novel_generator.py`) - 智能状态检查和用户交互

## 🚀 使用流程

### 1. 智能状态检查
```bash
# 启动交互式会话（推荐）
python3 ~/.claude/skills/novelgen/scripts/novelgen_cli.py generate

# 或者直接运行
python3 ~/.claude/skills/novelgen/scripts/novel_generator.py
```

系统会自动：
- ✅ 检查项目整体状态
- ✅ 分析当前创作进度
- ✅ 识别下一步操作
- ✅ 检查生成先决条件
- ✅ 提供智能建议

### 2. 生成上下文准备
当条件满足时，系统会：
- 📚 执行完整的七步生成流程
- 🗜️ 应用三层压缩机制
- 📄 加载前序章节内容
- 📝 整合所有设定和大纲
- 🎯 生成完整的prompt上下文

### 3. Claude内容生成
系统返回`ready_for_claude`状态后：
- 🤖 Claude基于上下文生成章节内容
- 📊 目标字数：2000-3000字
- 🎭 遵循人物性格和世界观设定
- 📋 按照大纲推进情节发展

### 4. 内容保存管理
使用Claude集成器保存生成的内容：
```bash
python3 ~/.claude/skills/novelgen/scripts/claude_integration.py \
  --chapter 1 \
  --title "血色实验室" \
  --content "生成的章节内容..."
```

## 📋 完整工作流程示例

### 用户操作流程：
1. **用户要求**: "生成小说"
2. **系统检查**: 自动分析项目状态和进度
3. **智能判断**: 识别当前应该写第几章，需要什么条件
4. **条件检查**: 验证设定文件、大纲、前序章节等
5. **缺失提示**: 如有缺失，明确指出并提供修复建议
6. **上下文准备**: 条件满足后，构建完整生成上下文
7. **等待Claude**: 返回ready_for_claude状态，等待Claude生成
8. **内容保存**: Claude生成后，保存为JSON和MD双版本

### 状态输出示例：
```json
{
  "status": "ready_for_claude",
  "chapter": 3,
  "context_length": 2841,
  "context": "完整的生成上下文...",
  "message": "第3章上下文已准备完成，请Claude生成内容",
  "next_step": "请基于以上上下文生成完整的章节内容",
  "generation_instructions": {
    "word_count_target": "2000-3000字",
    "follow_outline": true,
    "maintain_consistency": true
  }
}
```

## 🎨 核心特性

### 智能状态管理
- **自动进度判断**: 基于现有章节和大纲规划，自动确定当前进度
- **完整性检查**: 验证所有必需组件（设定、大纲、前序章节）
- **智能建议**: 基于当前状态提供具体的操作建议

### 七步生成流程
1. **加载各种设定到上下文** - 世界观、人物、环境、情节、写作风格
2. **加载前序章节的压缩提示** - 三层压缩机制管理长篇小说
3. **加载上一章全文** - 确保情节连贯性
4. **生成上下文JSON** - 构建结构化上下文
5. **加载当前章节的情节简介** - 从大纲提取核心信息
6. **加载当前章节和后续章节大纲** - 确保整体方向一致
7. **准备生成请求** - 返回给Claude的完整上下文

### 三层压缩机制
- **近期章节** (2章): 完整保留，约2000 tokens
- **中期章节** (3-10章): 压缩摘要，约500 tokens
- **长期章节** (11章以上): 核心要点，约100 tokens

### 独立大纲管理
```
settings/outlines/
├── README.md           # 项目总览
├── master_outline.md   # 完整总大纲
└── chapters/           # 章节大纲
    ├── chapter_01_outline.md
    ├── chapter_02_outline.md
    └── ...
```

## 🔧 CLI工具使用

### 基本命令
```bash
# 交互式智能生成（推荐）
novelgen_cli.py generate

# 生成指定章节上下文
novelgen_cli.py generate --chapter 3

# 大纲管理
novelgen_cli.py outline status
novelgen_cli.py outline create-chapter 3 --title "新章节"

# 项目状态
novelgen_cli.py project status
```

### Claude集成
```bash
# 保存Claude生成的内容
claude_integration.py --chapter 1 --title "章节标题" --content "内容..."

# 查看章节信息
claude_integration.py --summary 1

# 列出所有章节
claude_integration.py --list
```

## 📊 文件结构

### 项目结构
```
你的小说项目/
├── settings/           # 设定文件
│   ├── outlines/      # 🆕 大纲管理
│   ├── worldview/
│   ├── characters/
│   ├── environments/
│   ├── plot/
│   └── writing_style/
├── draft/             # 草稿章节
│   └── chapters/
│       └── chapter_XX/
│           ├── chapter_XX.json  # 编辑版本
│           └── chapter_XX.md    # 阅读版本
├── manuscript/        # 最终版本
├── system/            # 系统生成文件
│   └── chapter_generation_prompt.md
└── NOVELGEN_GUIDE.md  # 使用指南
```

### 技能文件结构
```
~/.claude/skills/novelgen/
├── SKILL.md            # 技能定义
├── scripts/            # 核心脚本
│   ├── novel_generator.py        # 🆕 交互式管理器
│   ├── chapter_generator.py      # 章节生成器
│   ├── outline_manager.py        # 大纲管理器
│   ├── claude_integration.py     # 🆕 Claude集成器
│   ├── ai_adapter.py            # AI适配器（可选）
│   └── novelgen_cli.py          # CLI工具
└── data_managers/      # 数据管理器
    ├── worldbuilder.py
    ├── character_manager.py
    └── ...
```

## 🎯 最佳实践

### 1. 创作流程建议
1. **先完善设定**: 确保世界观、人物、环境等基础设定完整
2. **大纲先行**: 为每个章节创建详细大纲（300-800字）
3. **按序创作**: 严格按照章节顺序，确保连贯性
4. **及时保存**: 每次生成后立即保存到项目中

### 2. 大纲管理建议
- 每章大纲包含：开端、发展、高潮、结局、核心冲突
- 定期更新总大纲，保持整体方向一致
- 使用独立文件，便于版本控制和协作

### 3. 质量控制建议
- 生成后检查人物性格一致性
- 验证情节是否符合大纲规划
- 确保世界观设定没有冲突
- 注意章节间的衔接和过渡

## 🔍 故障排除

### 常见问题
1. **生成条件不满足**: 检查设定文件是否完整，大纲是否存在
2. **上下文过长**: 系统会自动压缩，确保在128k token限制内
3. **人物不一致**: 检查人物设定文件，确保信息准确
4. **情节断裂**: 确保前序章节存在且内容完整

### 调试命令
```bash
# 检查项目状态
python3 novel_generator.py

# 查看详细大纲状态
python3 outline_manager.py status

# 测试章节生成
python3 chapter_generator.py --chapter 1
```

## 📈 性能优化

### 上下文管理
- 自动应用三层压缩，确保处理长篇小说
- 智能筛选相关信息，避免上下文冗余
- 动态调整压缩权重，优化生成质量

### 文件管理
- 增量保存，避免重复处理
- 双版本输出，兼顾编辑和阅读需求
- 自动备份，防止数据丢失

---

## 🎉 总结

NovelGen Claude Skill通过智能化的流程管理和上下文准备，为Claude提供了完整的小说创作支持。系统专注于项目管理和内容组织，让Claude能够专注于创意生成，实现人机协作的最佳效果。

**核心理念**: 系统管流程，Claude管创作，用户管方向