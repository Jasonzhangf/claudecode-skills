#!/bin/bash

# 小说生成器技能自动安装脚本

set -e

echo "🚀 开始安装小说生成器技能..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 设置默认安装路径
DEFAULT_PATH="$HOME/.claude/skills"
INSTALL_PATH="${1:-$DEFAULT_PATH}"

echo "📁 安装路径: $INSTALL_PATH"

# 创建安装目录
mkdir -p "$INSTALL_PATH"

# 创建技能目录
SKILL_DIR="$INSTALL_PATH/novel-generator"
mkdir -p "$SKILL_DIR"

echo "📦 解压技能文件..."

# 查找zip文件，优先使用最新版本
ZIP_FILES=("novelgen-v2.0.0.zip" "novelgen-v*.zip" "novel-generator-v2.zip")

for ZIP_FILE in "${ZIP_FILES[@]}"; do
    if [ -f "$ZIP_FILE" ]; then
        unzip -q "$ZIP_FILE" -d "$SKILL_DIR"
        echo "✅ 从 $ZIP_FILE 安装完成"
        ZIP_FOUND=true
        break
    fi
done

if [ "$ZIP_FOUND" != true ]; then
    echo "❌ 错误: 未找到可用的zip文件"
    echo "请确保以下文件之一在当前目录中："
    for ZIP_FILE in "${ZIP_FILES[@]}"; do
        echo "  - $ZIP_FILE"
    done
    exit 1
fi

# 验证安装
echo "🔍 验证安装..."

if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "❌ 错误: SKILL.md 文件不存在，安装可能失败"
    exit 1
fi

if [ ! -d "$SKILL_DIR/scripts" ]; then
    echo "❌ 错误: scripts 目录不存在，安装可能失败"
    exit 1
fi

# 设置执行权限
chmod +x "$SKILL_DIR/scripts"/*.py
chmod +x "$SKILL_DIR/scripts/data_managers"/*.py

echo "🧪 测试安装..."

# 测试Python脚本
cd "$SKILL_DIR"

# 测试基本功能
python3 scripts/session_manager.py --action info > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 基本脚本测试通过"
else
    echo "⚠️  警告: 基本脚本测试失败，但安装可能仍然成功"
fi

# 测试新功能 - 统一API
python3 scripts/unified_api.py --request-json '{"action": "system.status"}' > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 统一API测试通过"
else
    echo "⚠️  警告: 统一API测试失败"
fi

# 创建示例项目
echo "📝 创建示例项目..."
EXAMPLE_PROJECT="$HOME/novel-example-project"
mkdir -p "$EXAMPLE_PROJECT"

# 复制示例配置
if [ -f "assets/examples/sample_project.md" ]; then
    cp assets/examples/sample_project.md "$EXAMPLE_PROJECT/project_info.md"
fi

# 创建使用示例
cat > "$EXAMPLE_PROJECT/usage_examples.md" << 'EOF'
# 小说生成器使用示例

## 基本使用
```bash
# 使用统一API查看系统状态
python3 ~/.claude/skills/novel-generator/scripts/unified_api.py --request-json '{"action": "system.status"}'

# 显示世界观设定
python3 ~/.claude/skills/novel-generator/scripts/settings_display_manager.py --type worldview

# 显示角色记忆
python3 ~/.claude/skills/novel-generator/scripts/memory_display_manager.py --identifier "角色名"
```

## 新功能使用
```bash
# 分析章节内容生成记忆
python3 ~/.claude/skills/novel-generator/scripts/chapter_memory_analyzer.py --action analyze --chapter 1

# 应用生成的记忆
python3 ~/.claude/skills/novel-generator/scripts/chapter_memory_analyzer.py --action apply --chapter 1

# 智能编辑章节
python3 ~/.claude/skills/novel-generator/scripts/unified_api.py --request-json '{
  "action": "chapter.intelligent_edit",
  "chapter_number": 1,
  "edit_request": {
    "content": "新内容...",
    "edit_mode": "append",
    "requires_ai": false
  }
}'
```
EOF

echo "🎉 安装完成！"
echo ""
echo "📋 安装信息:"
echo "  - 技能路径: $SKILL_DIR"
echo "  - 示例项目: $EXAMPLE_PROJECT"
echo ""
echo "🚀 使用方法:"
echo "  1. 启动Claude Code"
echo "  2. 输入: /skill novel-generator"
echo "  3. 开始创作你的小说！"
echo ""
echo "📖 更多帮助:"
echo "  - 使用指南: $SKILL_DIR/USAGE_EXAMPLES.md"
echo "  - 功能介绍: $SKILL_DIR/SKILL.md"
echo "  - 示例项目: $EXAMPLE_PROJECT/usage_examples.md"
echo ""
echo "🆕 v2.0 新功能:"
echo "  - ✅ 智能导入设定：从外部目录自动导入设定"
echo "  - ✅ 统一API接口：所有功能通过统一API访问"
echo "  - ✅ 章节记忆分析：自动解析章节生成人物记忆"
echo "  - ✅ 智能编辑功能：支持AI辅助和上下文感知编辑"
echo "  - ✅ 记忆管理系统：多维度记忆展示和管理"
echo ""
echo "💡 提示: 你可以在任何目录下创建小说项目，技能会自动识别和管理。"