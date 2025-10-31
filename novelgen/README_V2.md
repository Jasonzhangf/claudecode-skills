# 小说生成器 v2.0

## 🎯 项目概述

小说生成器是一个专业的AI辅助小说创作工具，支持长篇小说的完整创作流程。v2.0版本引入了智能导入、统一API、章节记忆分析等多项创新功能。

### ✨ 核心价值

- **智能内容管理**: 自动化设定导入和章节记忆管理
- **AI集成架构**: 支持多种AI服务的无缝集成
- **统一操作接口**: 简化复杂的创作流程
- **数据完整性**: 确保角色一致性和故事连贯性

## 🚀 v2.0 重大更新

### 🆕 核心新功能

1. **智能导入设定系统**
   - 自动扫描外部目录中的文件
   - AI辅助识别和分类设定内容
   - 支持增量更新和智能合并
   - 支持多种文件格式（.md, .txt, .docx等）

2. **统一API接口**
   - 所有功能通过统一接口访问
   - 标准化的请求响应格式
   - 支持JSON请求文件
   - 完整的错误处理和状态管理

3. **章节记忆分析**
   - 自动解析章节内容
   - 生成多维度记忆（情感、行动、关系、冲突、成长）
   - 智能情感权重计算
   - 记忆关系网络构建

4. **智能编辑功能**
   - 支持本地和AI辅助编辑
   - 上下文感知更新
   - 多种编辑模式（替换、追加、插入、前置）
   - 自动维护一致性

5. **记忆管理系统**
   - 多维度记忆展示（按类型、时间线、关联网络）
   - 记忆统计和分析
   - 情感权重管理
   - 记忆压缩和长期存储

### 🔧 技术架构升级

- **模块化设计**: 清晰的模块职责分离
- **AI集成架构**: 标准化AI任务接口
- **数据管理增强**: 更强的数据解析和更新能力
- **错误处理**: 完整的异常处理和日志记录
- **性能优化**: 优化文件操作和内存使用

## 📁 项目结构

```
novel-generator/
├── SKILL.md                    # 技能完整介绍
├── README_V2.md               # v2.0项目说明
├── USAGE_EXAMPLES.md           # 详细使用示例
├── CHANGELOG_V2.md             # v2.0更新日志
├── INSTALLATION.md              # 安装指南
├── install.sh                  # 自动安装脚本
├── create_package.sh           # 创建安装包脚本
├── QUICKSTART.md               # 快速开始指南
├── scripts/                    # 核心脚本
│   ├── unified_api.py         # 统一API接口
│   ├── chapter_memory_analyzer.py # 章节记忆分析器
│   ├── settings_display_manager.py # 设定显示管理器
│   ├── memory_display_manager.py   # 记忆显示管理器
│   ├── chapter_manager.py       # 章节管理器
│   ├── import_manager.py        # 导入管理器
│   ├── session_manager.py       # 会话管理器
│   ├── compression_engine.py    # 压缩引擎
│   └── data_managers/          # 数据管理器
│       ├── worldbuilder.py     # 世界观管理
│       ├── character_manager.py # 角色管理
│       ├── memory_manager.py    # 记忆管理
│       ├── plot_manager.py      # 情节管理
│       ├── environment_manager.py # 环境管理
│       └── style_manager.py      # 风格管理
├── references/                 # 参考文档
├── assets/                     # 资源文件
│   ├── examples/               # 示例项目
│   └── templates/              # 模板文件
└── test_updated_functions.py  # 功能测试脚本
```

## 🚀 快速开始

### 安装要求

- Python 3.7+
- Claude Code (推荐)
- 支持的平台: macOS, Linux, Windows

### 安装步骤

1. **下载安装包**
   ```bash
   # 获取 novel-generator-v2.zip
   ```

2. **解压安装**
   ```bash
   unzip novel-generator-v2.zip
   cd novelgen
   ```

3. **自动安装**
   ```bash
   ./install.sh
   ```

4. **验证安装**
   ```bash
   python3 scripts/unified_api.py --request-json '{"action": "system.status"}'
   ```

### 基础使用

#### 1. 创建小说项目
```bash
mkdir my-novel
cd my-novel
```

#### 2. 创建设定
```bash
# 创建世界观
python3 ~/.claude/skills/novel-generator/scripts/data_managers/worldbuilder.py --action create

# 创建角色
python3 ~/.claude/skills/novel-generator/scripts/data_managers/character_manager.py --action create --name "主角" --type main
```

#### 3. 查看设定
```bash
# 显示所有设定
python3 ~/.claude/skills/novel-generator/scripts/settings_display_manager.py --action list

# 显示世界观
python3 ~/.claude/skills/novel-generator/scripts/settings_display_manager.py --type worldview
```

## 🆕 v2.0新功能使用

### 智能导入设定

```bash
# 扫描并导入所有设定
python3 scripts/unified_api.py --request-json '{
  "action": "import.from_directory",
  "target_directory": "./materials"
}'

# 导入特定类型的设定
python3 scripts/unified_api.py --request-json '{
  "action": "import.from_directory",
  "target_directory": "./materials",
  "specific_setting": "character"
}'
```

### 章节记忆分析

```bash
# 分析第1章内容
python3 scripts/chapter_memory_analyzer.py --action analyze --chapter 1

# 应用生成的记忆
python3 scripts/chapter_memory_analyzer.py --action apply --chapter 1
```

### 智能编辑功能

```bash
# 追加内容
python3 scripts/unified_api.py --request-json '{
  "action": "chapter.intelligent_edit",
  "chapter_number": 1,
  "edit_request": {
    "content": "这是新增的内容...",
    "edit_mode": "append",
    "requires_ai": false
  }
}'

# AI辅助编辑
python3 scripts/unified_api.py --request-json '{
  "action": "chapter.intelligent_edit",
  "chapter_number": 1,
  "edit_request": {
    "edit_instructions": "请改进这段文字的表达",
    "requires_ai": true
  }
}'
```

### 记忆管理

```bash
# 显示角色记忆
python3 scripts/memory_display_manager.py --identifier "主角" --type character_all

# 显示记忆时间线
python3 scripts/memory_display_manager.py --identifier "主角" --type timeline

# 获取记忆统计
python3 scripts/memory_display_manager.py --action stats --identifier "主角"
```

## 🎯 核心场景

### 1. 从现有素材导入设定
```bash
# 将现有资料转换为项目设定
python3 scripts/import_manager.py --action import-from-directory \
  --target-directory "./existing_materials"

# 处理AI分析结果（如果返回ai_task_required）
python3 scripts/import_manager.py --action process-ai-result \
  --ai-result-file "ai_analysis_result.json"
```

### 2. 章节创作与记忆管理
```bash
# 创建章节
python3 scripts/chapter_manager.py --action create --chapter 1 --title "第一章"

# 写作完成后分析记忆
python3 scripts/chapter_memory_analyzer.py --action apply --chapter 1

# 查看生成的记忆
python3 scripts/memory_display_manager.py --identifier "主角" --type character_all
```

### 3. 角色关系管理
```bash
# 查看角色关系
python3 scripts/data_managers/character_manager.py --action load --name "主角"

# 添加角色关系
python3 scripts/settings_manager.py --category character --action add_relationship \
  --target "主角" --character2 "配角" --relationship-type "朋友"
```

### 4. 长篇小说管理
```bash
# 查看进度
python3 scripts/session_manager.py --action progress

# 章节跳转
python3 scripts/chapter_manager.py --action jump --chapter 5

# 压缩记忆（如果需要）
python3 scripts/memory_manager.py --action compress --character "主角"
```

## 🤖 AI集成

### AI任务类型

系统支持以下AI任务类型：

1. **content_analysis**: 分析文件内容并提取设定
2. **content_edit**: 智能编辑和改进内容
3. **generate_summary**: 生成内容摘要
4. **memory_analysis**: 分析记忆内容和关联

### AI任务处理流程

```python
# 1. 发起AI任务请求
result = api.process_request({
    "action": "import.from_directory",
    "target_directory": "./materials"
})

# 2. 如果需要AI处理
if result["status"] == "ai_task_required":
    ai_task = result["ai_task"]
    # 调用你的AI服务
    ai_result = your_ai_service.process_task(ai_task)

    # 3. 应用AI结果
    final_result = api.process_request({
        "action": "import.process_ai_result",
        "ai_result": ai_result
    })
```

## 📊 性能特性

### 数据管理
- **增量更新**: 支持部分更新而非完全替换
- **智能解析**: 自动解析和合并现有内容
- **格式标准化**: 统一的数据格式和接口
- **版本控制**: 完整的操作日志和版本管理

### AI集成
- **标准接口**: 统一的AI任务请求格式
- **异步处理**: 支持异步AI任务处理
- **错误恢复**: AI失败时的降级处理
- **扩展性**: 易于添加新的AI服务

### 记忆系统
- **多维分类**: 按类型、时间、关联等多维度分类
- **智能权重**: 自动计算记忆重要性和情感权重
- **关系网络**: 构建记忆间的关系网络
- **压缩存储**: 长期记忆的智能压缩存储

## 🔧 开发和扩展

### 代码结构
- **模块化设计**: 清晰的模块职责分离
- **统一接口**: 标准化的API接口设计
- **配置驱动**: 基于配置文件的功能控制
- **插件化**: 易于扩展新功能

### 添加新功能

1. **创建新模块**: 在 `scripts/` 或 `scripts/data_managers/` 中创建新模块
2. **集成API**: 在 `unified_api.py` 中添加新的处理逻辑
3. **更新文档**: 更新相关文档和示例
4. **测试验证**: 创建测试脚本验证功能

### 自定义AI服务

```python
class CustomAIClient:
    def process_task(self, ai_task):
        task_type = ai_task["task_type"]

        if task_type == "content_analysis":
            return self.analyze_content(ai_task)
        elif task_type == "content_edit":
            return self.edit_content(ai_task)
        # 添加更多任务类型...
```

## 🛠️ 故障排除

### 常见问题

1. **Python环境问题**
   ```bash
   # 检查Python版本
   python3 --version

   # 检查模块路径
   python3 -c "import sys; print(sys.path)"
   ```

2. **权限问题**
   ```bash
   # 设置执行权限
   chmod +x scripts/*.py
   chmod +x scripts/data_managers/*.py
   ```

3. **模块导入错误**
   ```bash
   # 检查文件结构
   ls -la scripts/data_managers/

   # 检查Python模块
   python3 -c "from data_managers.character_manager import CharacterManager"
   ```

### 调试模式

```bash
# 启用详细日志
export NOVELGEN_DEBUG=true

# 运行功能
python3 scripts/unified_api.py --request-json '{"action": "system.status"}'
```

## 📈 路线图

### v2.1 计划功能
- Web界面支持
- 多语言设定支持
- 协作编辑功能
- 版本控制集成

### v2.2 计划功能
- 智能角色对话生成
- 情节自动推导
- 多结局分支管理
- 出版格式导出

## 🤝 贡献指南

### 贡献方式
1. **报告问题**: 在GitHub Issues中报告bug
2. **功能建议**: 提出新功能想法
3. **代码贡献**: 提交Pull Request
4. **文档改进**: 完善文档和示例

### 开发环境
```bash
# 克隆项目
git clone <repository-url>
cd novel-generator

# 安装依赖
pip install -r requirements.txt

# 运行测试
python3 test_updated_functions.py
```

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 🤝 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**🎉 开始你的小说创作之旅！**