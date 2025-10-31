# 小说生成器技能安装指南

## 🚀 快速安装（推荐）

### 选项1: 使用自动安装脚本
```bash
# 1. 下载技能包到本地
# 2. 运行安装脚本
./install.sh

# 3. 或者指定安装路径
./install.sh /your/custom/skills/path
```

### 选项2: 手动安装
```bash
# 1. 创建技能目录
mkdir -p ~/.claude/skills

# 2. 解压技能包
unzip novel-generator-updated.zip -d ~/.claude/skills/novel-generator

# 3. 设置执行权限
chmod +x ~/.claude/skills/novel-generator/scripts/*.py
chmod +x ~/.claude/skills/novel-generator/scripts/data_managers/*.py
```

## 📍 安装位置选项

### 选项A: Claude默认技能目录
```bash
~/.claude/skills/novel-generator/
```
- ✅ Claude自动识别
- ✅ 标准位置
- ✅ 推荐使用

### 选项B: 自定义目录
```bash
/path/to/your/skills/novel-generator/
```
- ✅ 完全控制位置
- ⚠️ 需要手动配置Claude

### 选项C: 项目内嵌
```bash
/your/novel/project/novel-generator/
```
- ✅ 项目独立
- ✅ 便于版本控制
- ⚠️ 每个项目需要一份副本

## 🔧 详细安装步骤

### 步骤1: 准备环境
```bash
# 检查Python3是否安装
python3 --version

# 检查Claude Code是否可用
claude --version
```

### 步骤2: 下载技能包
确保你有了以下zip文件之一：
- `novel-generator-v2.zip` (最新版本，推荐)
- `novel-generator-updated.zip` (更新版本)
- `novel-generator.zip` (基础版本)

### 步骤3: 选择安装方式

#### 方式A: 自动安装（推荐）
```bash
# 1. 解压zip文件得到脚本和内容
unzip novel-generator-updated.zip
cd novelgen

# 2. 运行安装脚本
./install.sh

# 3. 按照提示完成安装
```

#### 方式B: 手动安装
```bash
# 1. 创建技能目录
mkdir -p ~/.claude/skills/novel-generator

# 2. 复制所有文件
cp -r * ~/.claude/skills/novel-generator/

# 3. 设置权限
chmod +x ~/.claude/skills/novel-generator/scripts/*.py
chmod +x ~/.claude/skills/novel-generator/scripts/data_managers/*.py

# 4. 清理临时文件（可选）
rm -rf novelgen novel-generator-updated.zip
```

#### 方式C: 直接在当前目录使用
如果你想在当前目录直接使用技能（不安装）：
```bash
# 确保当前目录包含所有技能文件
ls -la | grep -E "(SKILL\.md|scripts|references|assets)"

# 设置执行权限
chmod +x scripts/*.py
chmod +x scripts/data_managers/*.py

# 然后可以直接在当前目录使用
```

## 🧪 验证安装

### 基本验证
```bash
# 进入技能目录
cd ~/.claude/skills/novel-generator

# 检查文件结构
ls -la
# 应该看到: SKILL.md, scripts/, references/, assets/, USAGE_EXAMPLES.md

# 测试Python脚本
python3 scripts/session_manager.py --action info
# 应该返回: {"status": "no_session"}
```

### 功能验证
```bash
# 测试统一API（新功能）
python3 scripts/unified_api.py --request-json '{"action": "system.status"}'

# 测试显示管理器（新功能）
python3 scripts/settings_display_manager.py --action list

# 测试记忆分析器（新功能）
python3 scripts/chapter_memory_analyzer.py --action info

# 测试角色管理器
python3 scripts/data_managers/character_manager.py --action list

# 测试压缩引擎
python3 scripts/compression_engine.py --action status
```

## 🚀 开始使用

### 方法1: 通过Claude Code调用
```bash
# 启动Claude Code
claude

# 在Claude中调用技能
"请使用novel-generator技能帮我创建一个新的小说项目"
```

### 方法2: 直接命令行使用
```bash
# 创建新的小说项目目录
mkdir my-first-novel
cd my-first-novel

# 创建设定（示例）
python3 ~/.claude/skills/novel-generator/scripts/data_managers/worldbuilder.py --action create

# 使用统一API查看系统状态
python3 ~/.claude/skills/novel-generator/scripts/unified_api.py --request-json '{"action": "system.status"}'

# 智能导入设定（新功能）
python3 ~/.claude/skills/novel-generator/scripts/unified_api.py --request-json '{
  "action": "import.from_directory",
  "target_directory": "./source_materials"
}'

# 显示设定（新功能）
python3 ~/.claude/skills/novel-generator/scripts/settings_display_manager.py --type worldview

# 查看帮助
python3 ~/.claude/skills/novel-generator/scripts/settings_manager.py --help
```

### 方法3: 集成到工作流
```bash
# 在你的小说项目目录中创建使用脚本
cat > use-novel-generator.sh << 'EOF'
#!/bin/bash
SKILL_PATH="$HOME/.claude/skills/novel-generator"
python3 "$SKILL_PATH/scripts/settings_manager.py" "$@"
EOF

chmod +x use-novel-generator.sh

# 现在可以简化使用
./use-novel-generator.sh --category character --action list
```

## 🛠️ 配置Claude Code（如果需要）

### 如果技能不在默认位置
```bash
# 创建Claude配置目录
mkdir -p ~/.claude

# 编辑配置文件
cat >> ~/.claude/claude_settings.json << 'EOF'
{
  "skills": {
    "additional_paths": [
      "/path/to/your/skills"
    ]
  }
}
EOF
```

### 或者环境变量方式
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export CLAUDE_SKILLS_PATH="/path/to/your/skills:$HOME/.claude/skills"

# 重新加载配置
source ~/.bashrc  # 或 source ~/.zshrc
```

## 🔍 故障排除

### 常见问题1: Python权限错误
```bash
# 解决方案：给脚本添加执行权限
chmod +x ~/.claude/skills/novel-generator/scripts/*.py
chmod +x ~/.claude/skills/novel-generator/scripts/data_managers/*.py
```

### 常见问题2: Claude找不到技能
```bash
# 解决方案1：检查安装路径
ls -la ~/.claude/skills/novel-generator/

# 解决方案2：重新安装
rm -rf ~/.claude/skills/novel-generator
./install.sh
```

### 常见问题3: 模块导入错误
```bash
# 解决方案：检查Python路径
cd ~/.claude/skills/novel-generator
python3 -c "import sys; print(sys.path)"

# 确保技能目录在Python路径中
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 常见问题4: 技能文件损坏
```bash
# 解决方案：重新下载安装
# 1. 删除现有安装
rm -rf ~/.claude/skills/novel-generator

# 2. 重新下载zip文件
# 3. 重新运行安装脚本
./install.sh
```

## 📋 安装检查清单

- [ ] Python3已安装
- [ ] Claude Code已安装
- [ ] 下载了最新zip文件（novel-generator-v2.zip推荐）
- [ ] 解压到正确目录
- [ ] 设置了执行权限
- [ ] 验证基本功能正常
- [ ] 验证新功能（统一API、记忆分析等）
- [ ] 能够调用技能

## 🎯 下一步

安装完成后，你可以：

1. **查看使用指南**: `USAGE_EXAMPLES.md` (详细使用示例)
2. **查看功能介绍**: `SKILL.md` (完整功能列表)
3. **查看更新日志**: `CHANGELOG_V2.md` (v2.0新功能介绍)
4. **查看示例项目**: `assets/examples/sample_project.md`
5. **创建第一个项目**: 使用模板开始创作
6. **探索新功能**: 尝试统一API、记忆分析、智能编辑等新功能

### 🆕 v2.0新功能快速开始

```bash
# 1. 查看系统状态
python3 ~/.claude/skills/novel-generator/scripts/unified_api.py --request-json '{"action": "system.status"}'

# 2. 智能导入设定
python3 ~/.claude/skills/novel-generator/scripts/unified_api.py --request-json '{
  "action": "import.from_directory",
  "target_directory": "./my_materials"
}'

# 3. 分析章节生成记忆
python3 ~/.claude/skills/novel-generator/scripts/chapter_memory_analyzer.py --action analyze --chapter 1

# 4. 智能编辑章节
python3 ~/.claude/skills/novel-generator/scripts/unified_api.py --request-json '{
  "action": "chapter.intelligent_edit",
  "chapter_number": 1,
  "edit_request": {
    "content": "新增内容",
    "edit_mode": "append",
    "requires_ai": false
  }
}'
```

## 💡 小贴士

- **备份重要**: 定期备份你的小说项目和设定
- **版本控制**: 考虑使用git管理你的小说项目
- **渐进使用**: 先熟悉基本功能，再探索高级功能
- **寻求帮助**: 遇到问题时查看错误日志和帮助文档

---

**🎉 恭喜！你现在可以开始使用这个强大的小说生成器技能了！**