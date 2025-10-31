# 智能增量更新示例

## 场景描述

假设用户有一个现有的项目，已经编写了自定义的CLAUDE.md文档，现在需要使用system-chain技能进行智能更新，而不是覆盖。

## 使用流程

### 第1步：数据收集
```bash
cd /my-project
python3 /path/to/system-chain/scripts/collect_data.py
```

输出：
```
🔍 开始收集项目数据...
✅ 数据收集完成
📊 项目数据已导出到: /my-project/project_data.json

📋 数据收集摘要:
- 发现模块数量: 3
- CLAUDE.md存在: 是
- 架构问题: 1 个重复文件, 2 个重复函数
- 未记录文件: 4 个
```

### 第2步：Claude智能处理

用户将生成的`project_data.json`内容提供给Claude，并发出指令：

```
基于project_data.json的分析结果，请帮我更新项目文档：

1. 更新CLAUDE.md，但请保留我自定义的内容，只更新需要变化的部分
2. 检查各模块README是否需要更新
3. 给出架构问题的解决建议

要求：
- 采用增量更新，不要覆盖现有内容
- 保持我的文档风格和格式
- 重点标出需要我关注的问题
```

### 第3步：Claude的智能分析和更新

Claude会基于数据提供以下分析：

#### 📊 项目状态分析
```markdown
**扫描时间**: 2025-10-31 11:45:00
**项目根目录**: /my-project
**发现模块**: 3个 (src/core, src/api, src/payment)
```

#### 📝 CLAUDE.md更新建议
```markdown
**现有内容分析**:
- ✅ 包含自定义的项目说明
- ✅ 有完整的开发规范
- ⚠️ 模块结构部分需要更新（发现新模块）
- ⚠️ 缺少system-chain技能说明

**建议更新内容**:
1. 在技能包说明部分添加system-chain描述
2. 更新模块结构，新增src/payment模块
3. 保持你的自定义开发规范不变
```

#### 🏗️ 架构问题分析
```markdown
**发现的问题**:
1. **重复函数**: `process_data()` 在 src/core/utils.py 和 src/core/validators.py 中重复
2. **重复文件**: `config.json` 在 src/core 和 src/payment 中都存在
3. **未记录文件**:
   - src/api/debug.py (建议删除 - 调试文件)
   - src/payment/transaction.py (需要添加到README)

**解决建议**:
1. 合并重复的process_data函数到utils.py
2. 统一配置管理，避免重复配置文件
3. 清理调试文件，完善文档覆盖
```

#### 📄 README更新建议
```markdown
**src/core/README.md**:
- ✅ 结构完整，包含Ground Truth定义
- 建议：添加新文件validators.py的描述

**src/payment/README.md**:
- ⚠️ 缺少transaction.py文件描述
- 建议：更新文件结构部分

**src/api/README.md**:
- ⚠️ 第一行功能描述不够标准化
- 建议：采用"功能描述 - 主要职责 - 适用场景"格式
```

### 第4步：用户确认和实施

Claude提供具体的更新代码，用户可以选择：

**选项A：逐项确认更新**
```markdown
我准备按以下步骤更新：

1. **CLAUDE.md更新** - 只添加system-chain部分和更新模块结构
2. **src/payment/README.md更新** - 添加transaction.py描述
3. **删除调试文件** - 移除src/api/debug.py

是否同意这些更新？
```

**选项B：生成更新脚本**
```markdown
我将生成更新脚本，你可以检查后手动执行：

```bash
# 1. 备份现有文件
cp CLAUDE.md CLAUDE.md.backup
cp src/payment/README.md src/payment/README.md.backup

# 2. 更新CLAUDE.md（只更新指定部分）
# [具体的更新代码]

# 3. 删除调试文件
rm src/api/debug.py
```

## 优势对比

### ❌ 旧方式（直接覆盖）
```python
# 完全重写CLAUDE.md，丢失用户自定义内容
content = generate_new_claude_md()  # 生成全新内容
with open('CLAUDE.md', 'w') as f:
    f.write(content)  # 覆盖现有内容
```

### ✅ 新方式（智能增量）
```python
# 1. 数据收集脚本只负责分析，不修改文件
data = collect_project_data()
export_data(data, 'project_data.json')

# 2. Claude基于数据进行智能判断
# 3. 用户确认后进行增量更新
# 4. 保护自定义内容不被覆盖
```

## 实际效果

**更新前的CLAUDE.md**（用户自定义内容）：
```markdown
# CLAUDE.md

## 我的项目规范
这里是我的自定义开发规范...

## 团队协作规则
这里是我们团队的协作规则...
```

**更新后的CLAUDE.md**（保留自定义 + 新增内容）：
```markdown
# CLAUDE.md

## 我的项目规范
这里是我的自定义开发规范...

## 团队协作规则
这里是我们团队的协作规则...

## 技能包说明

### system-chain
项目架构链条化初始化和管理技能包...

## 项目架构

### 模块结构
- **src/core**: 核心模块负责提供项目的基础功能...
- **src/api**: API模块负责处理HTTP请求...
- **src/payment**: 支付模块负责处理支付流程...

### 模块功能定义
#### src/core
- **重要: 核心模块只提供基础功能，不包含业务逻辑**
...
```

**关键优势**：
- ✅ 用户的自定义项目规范完全保留
- ✅ 新增内容无缝集成到现有结构
- ✅ 文档风格和格式保持一致
- ✅ 用户完全控制更新内容