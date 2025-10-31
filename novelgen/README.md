# novelgen - 智能小说生成器

## 🎉 欢迎使用 novelgen！

这是一个专业的长篇小说AI创作辅助技能，具备：
- ✅ 智能上下文管理 (128k token)
- ✅ 三层压缩机制
- ✅ 断点续传功能
- ✅ 章节跳转管理
- ✅ 完整设定修改系统

## 🚀 快速开始

### 在Claude中直接使用：
```
请使用novelgen技能帮我创建一个新的小说项目
```

### 命令行使用：
```bash
# 创建小说项目
mkdir my-novel
cd my-novel

# 创建角色
python3 ~/.claude/skills/novelgen/scripts/data_managers/character_manager.py --action create --name "主角名" --type main

# 创建会话
python3 ~/.claude/skills/novelgen/scripts/session_manager.py --action create

# 创建世界观
python3 ~/.claude/skills/novelgen/scripts/data_managers/worldbuilder.py --action create
```

## 📋 核心功能

### 角色管理
```bash
# 创建角色
python3 ~/.claude/skills/novelgen/scripts/data_managers/character_manager.py --action create --name "林辰" --type main

# 列出角色
python3 ~/.claude/skills/novelgen/scripts/data_managers/character_manager.py --action list

# 查看关系
python3 ~/.claude/skills/novelgen/scripts/data_managers/character_manager.py --action relations --name "林辰"
```

### 世界观管理
```bash
# 创建世界观
python3 ~/.claude/skills/novelgen/scripts/data_managers/worldbuilder.py --action create

# 更新世界观
python3 ~/.claude/skills/novelgen/scripts/data_managers/worldbuilder.py --action update
```

### 情节管理
```bash
# 创建情节大纲
python3 ~/.claude/skills/novelgen/scripts/data_managers/plot_manager.py --action create

# 添加情节点
python3 ~/.claude/skills/novelgen/scripts/data_managers/plot_manager.py --action add_point --title "重要事件" --chapter 5

# 查看结构
python3 ~/.claude/skills/novelgen/scripts/data_managers/plot_manager.py --action structure
```

### 章节管理
```bash
# 创建章节
python3 ~/.claude/skills/novelgen/scripts/chapter_manager.py --action create --chapter 1 --title "第一章"

# 列出章节
python3 ~/.claude/skills/novelgen/scripts/chapter_manager.py --action list

# 跳转章节
python3 ~/.claude/skills/novelgen/scripts/chapter_manager.py --action jump --chapter 5
```

### 压缩管理
```bash
# 查看状态
python3 ~/.claude/skills/novelgen/scripts/compression_engine.py --action status

# 手动压缩
python3 ~/.claude/skills/novelgen/scripts/compression_engine.py --action compress --chapters 1-10
```

### 统一设置管理
```bash
# 查看设定状态
python3 ~/.claude/skills/novelgen/scripts/settings_manager.py --category character --action status

# 修改设定
python3 ~/.claude/skills/novelgen/scripts/settings_manager.py \
  --category character \
  --action update \
  --target "林辰" \
  --data '{"age": "25岁", "personality": "勇敢善良"}'
```

## 📁 项目结构
```
my-novel/
├── settings/           # 设定数据（写作时只读）
│   ├── characters/     # 角色设定
│   ├── worldview/      # 世界观设定
│   ├── plot/          # 情节设定
│   ├── environments/  # 环境设定
│   ├── writing_style/ # 写作风格
│   └── memory/        # 记忆设定
├── draft/             # 写作工作区
├── manuscript/        # 成品区
└── system/           # 系统数据
```

## 💡 使用技巧

1. **先完善设定**：创建角色、世界观、情节等基础设定
2. **创建章节大纲**：规划故事结构
3. **开始写作**：享受断点续传的便利
4. **随时修改**：所有设定都可以动态更新
5. **定期备份**：重要设定建议备份

## 📚 更多文档

- `references/usage_guide.md` - 完整使用指南
- `references/data_schemas.md` - 数据结构说明
- `INSTALLATION.md` - 安装说明

---

**🎊 现在开始创作你的小说吧！**