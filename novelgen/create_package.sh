#!/bin/bash

# 创建小说生成器v2.0安装包脚本

set -e

echo "📦 创建小说生成器v2.0安装包..."

# 设置版本信息
VERSION="2.0.0"
PACKAGE_NAME="novelgen-v2.0.0"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🔍 版本信息:"
echo "  - 版本: $VERSION"
echo "  - 包名: $PACKAGE_NAME"
echo "  - 日期: $DATE"

# 检查必要文件
echo "📋 检查必要文件..."
REQUIRED_FILES=(
    "SKILL.md"
    "USAGE_EXAMPLES.md"
    "CHANGELOG_V2.md"
    "INSTALLATION.md"
    "scripts/unified_api.py"
    "scripts/chapter_memory_analyzer.py"
    "scripts/settings_display_manager.py"
    "scripts/memory_display_manager.py"
    "scripts/data_managers/worldbuilder.py"
    "scripts/data_managers/character_manager.py"
    "scripts/data_managers/memory_manager.py"
    "scripts/chapter_manager.py"
    "install.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 错误: 缺少必要文件: $file"
        exit 1
    fi
done

echo "✅ 所有必要文件检查通过"

# 创建临时目录
TEMP_DIR="temp_package_$DATE"
echo "📁 创建临时目录: $TEMP_DIR"
mkdir -p "$TEMP_DIR"

# 创建novelgen子目录并复制文件
echo "📦 复制文件..."
mkdir -p "$TEMP_DIR/novelgen"
rsync -av --progress \
    --exclude="temp_*" \
    --exclude="*.zip" \
    --exclude=".git" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="test_*.py" \
    --exclude="test_*.json" \
    --exclude="demo_*.py" \
    --exclude="test_install_*" \
    --exclude="test_result*.json" \
    --exclude="RELEASE_INFO_*.md" \
    --exclude="api_test_report.json" \
    . "$TEMP_DIR/novelgen/"

# 创建版本信息文件
echo "📝 创建版本信息..."
cat > "$TEMP_DIR/novelgen/VERSION.txt" << EOF
小说生成器 v2.0
================

版本号: $VERSION
创建时间: $(date)
功能特性:
- ✅ 智能导入设定系统
- ✅ 统一API接口
- ✅ 章节记忆分析
- ✅ 智能编辑功能
- ✅ 记忆管理系统
- ✅ 设定显示管理器
- ✅ AI集成架构

文件统计:
$(find "$TEMP_DIR" -name "*.py" | wc -l) Python脚本
$(find "$TEMP_DIR" -name "*.md" | wc -l) Markdown文档
$(find "$TEMP_DIR" -type f | wc -l) 总文件数

安装方法:
1. 运行: ./install.sh
2. 查看: USAGE_EXAMPLES.md
3. 开始: 启动Claude Code并调用技能

更新日志: 请查看 CHANGELOG_V2.md
EOF

# 创建快速开始指南
echo "📝 创建快速开始指南..."
cat > "$TEMP_DIR/novelgen/QUICKSTART.md" << 'EOF'
# 小说生成器 v2.0 快速开始指南

## 🚀 快速安装

```bash
# 1. 解压文件
unzip novel-generator-v2.zip

# 2. 进入目录
cd novelgen

# 3. 运行安装脚本
./install.sh
```

## 🧪 基本验证

```bash
# 测试系统状态
python3 scripts/unified_api.py --request-json '{"action": "system.status"}'

# 测试显示功能
python3 scripts/settings_display_manager.py --action list

# 测试记忆分析
python3 scripts/chapter_memory_analyzer.py --action info
```

## 📝 创建第一个项目

```bash
# 1. 创建项目目录
mkdir my-first-novel
cd my-first-novel

# 2. 创建角色
python3 ~/.claude/skills/novel-generator/scripts/data_managers/character_manager.py --action create --name "主角" --type main

# 3. 创建世界观
python3 ~/.claude/skills/novel-generator/scripts/data_managers/worldbuilder.py --action create

# 4. 查看所有设定
python3 ~/.claude/skills/novel-generator/scripts/settings_display_manager.py --action list
```

## 🆕 新功能体验

### 智能导入设定
```bash
python3 ~/.claude/skills/novel-generator/scripts/unified_api.py --request-json '{
  "action": "import.from_directory",
  "target_directory": "./materials"
}'
```

### 章节记忆分析
```bash
# 分析第1章
python3 ~/.claude/skills/novel-generator/scripts/chapter_memory_analyzer.py --action analyze --chapter 1

# 应用记忆
python3 ~/.claude/skills/novel-generator/scripts/chapter_memory_analyzer.py --action apply --chapter 1
```

### 智能编辑
```bash
python3 ~/.claude/skills/novel-generator/scripts/unified_api.py --request-json '{
  "action": "chapter.intelligent_edit",
  "chapter_number": 1,
  "edit_request": {
    "content": "这是新增加的内容...",
    "edit_mode": "append",
    "requires_ai": false
  }
}'
```

## 📖 更多帮助

- 详细使用指南: USAGE_EXAMPLES.md
- 功能完整介绍: SKILL.md
- 更新日志: CHANGELOG_V2.md
- 安装指南: INSTALLATION.md

---

🎉 开始你的小说创作之旅吧！
EOF

# 创建安装包压缩文件
echo "📦 创建安装包..."
PACKAGE_FILE="${PACKAGE_NAME}.zip"
cd "$TEMP_DIR"
zip -r "../$PACKAGE_FILE" . > /dev/null
cd ..

# 验证压缩文件
if [ -f "$PACKAGE_FILE" ]; then
    PACKAGE_SIZE=$(du -h "$PACKAGE_FILE" | cut -f1)
    echo "✅ 安装包创建成功: $PACKAGE_FILE ($PACKAGE_SIZE)"
else
    echo "❌ 错误: 安装包创建失败"
    exit 1
fi

# 清理临时目录
echo "🧹 清理临时文件..."
rm -rf "$TEMP_DIR"

# 创建发布信息
echo "📝 发布信息..."
cat > "RELEASE_INFO_$DATE.md" << EOF
# 小说生成器 v2.0 发布信息

## 📦 包信息
- **包名**: $PACKAGE_FILE
- **版本**: $VERSION
- **发布时间**: $(date)
- **包大小**: $(du -h "$PACKAGE_FILE" | cut -f1)

## 🆕 v2.0 新增功能

### 核心功能
1. **智能导入设定系统**
   - 自动扫描外部目录
   - AI辅助内容识别和分类
   - 支持多种设定类型

2. **统一API接口**
   - 所有功能统一入口
   - 标准化请求响应格式
   - 支持AI任务集成

3. **章节记忆分析**
   - 自动解析章节内容
   - 生成多维度记忆（情感、行动、关系等）
   - 智能情感权重计算

4. **智能编辑功能**
   - 支持本地和AI辅助编辑
   - 上下文感知更新
   - 多种编辑模式

5. **记忆管理系统**
   - 多维度记忆展示
   - 时间线、关联网络视图
   - 记忆统计和分析

### 技术改进
- 模块化架构设计
- AI集成架构
- 完整的错误处理
- 详细的日志记录
- 标准化的数据格式

## 📋 安装要求

### 系统要求
- Python 3.7+
- Claude Code (推荐)
- 支持的平台: macOS, Linux, Windows

### 安装步骤
1. 解压: \`unzip $PACKAGE_FILE\`
2. 进入: \`cd novelgen\`
3. 安装: \`./install.sh\`
4. 验证: \`python3 scripts/unified_api.py --request-json '{"action":"system.status"}'\`

## 🚀 快速开始

### 基础使用
\`\`\`bash
# 查看系统状态
python3 scripts/unified_api.py --request-json '{"action":"system.status"}'

# 显示世界观设定
python3 scripts/settings_display_manager.py --type worldview

# 创建角色
python3 scripts/data_managers/character_manager.py --action create --name "主角"
\`\`\`

### 高级功能
\`\`\`bash
# 智能导入设定
python3 scripts/unified_api.py --request-json '{
  "action": "import.from_directory",
  "target_directory": "./materials"
}'

# 分析章节生成记忆
python3 scripts/chapter_memory_analyzer.py --action analyze --chapter 1
python3 scripts/chapter_memory_analyzer.py --action apply --chapter 1

# 智能编辑章节
python3 scripts/unified_api.py --request-json '{
  "action": "chapter.intelligent_edit",
  "chapter_number": 1,
  "edit_request": {
    "content": "新内容",
    "edit_mode": "append"
  }
}'
\`\`\`

## 📖 文档索引

### 核心文档
- **SKILL.md**: 完整功能介绍
- **USAGE_EXAMPLES.md**: 详细使用示例
- **INSTALLATION.md**: 安装指南
- **CHANGELOG_V2.md**: 更新日志

### 技术文档
- **scripts/**: 所有核心脚本
- **references/**: 参考文档
- **assets/**: 资源文件

## 🎯 使用场景

### 适用人群
- 长篇小说作者
- 系列小说创作者
- 小说工作室
- 个人创作爱好者

### 支持的小说类型
- 科幻小说
- 奇幻小说
- 都市小说
- 历史小说
- 悬疑小说
- 现代小说

## 🔗 相关链接

- 官方文档: USAGE_EXAMPLES.md
- 更新日志: CHANGELOG_V2.md
- 安装指南: INSTALLATION.md
- 技术支持: GitHub Issues

---

🎉 享受创作之旅！
EOF

echo "🎉 安装包创建完成！"
echo ""
echo "📦 包信息:"
echo "  - 文件名: $PACKAGE_FILE"
echo "  - 版本: $VERSION"
echo "  - 大小: $(du -h "$PACKAGE_FILE" | cut -f1)"
echo "  - 发布信息: RELEASE_INFO_$DATE.md"
echo ""
echo "📋 下一步:"
echo "  1. 分发包给用户"
echo "  2. 用户解压并运行 ./install.sh"
echo "  3. 验证安装完成"
echo "  4. 开始使用新功能！"

echo ""
echo "💡 提示: 你可以运行 './test_package.sh' 来测试安装包。"