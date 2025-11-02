# Sysmem 安装和使用指南 v2.0

## 🚀 概述

Sysmem v2.0 现在支持**智能交互式更新**、Git集成文件变更检测、智能数据清理、完整的Python包管理，包括增量数据收集、交互式编译安装提示和静态代码分析功能。

## 📦 安装方式

### 1. 🌟 智能安装检查（推荐）

```bash
# 运行智能安装脚本 - 自动检测项目变更并展示新功能
python3 scripts/install_project.py
```

**安装脚本特性：**
- ✅ 自动检测项目变更（Git/文件时间）
- ✅ 展示v2.0新功能和使用方式
- ✅ 集成智能数据清理功能演示
- ✅ 智能推荐安装命令
- ✅ 生成快速开始指南
- ✅ 导出安装信息到 `.claude/install_info.json`

### 2. 传统安装检查

```bash
# 检查项目是否需要重新安装（传统方式）
python3 scripts/auto_install.py --check
```

### 3. 使用Makefile安装（推荐）

```bash
# 用户模式安装
make install

# 开发模式安装（包含开发依赖）
make install-dev

# 全局安装（需要sudo权限）
make global-install
```

### 4. 使用pip直接安装

```bash
# 用户模式安装
python3 -m pip install -e .

# 全局安装
sudo python3 -m pip install .

# 开发模式安装
python3 -m pip install -e ".[dev]"
```

### 5. 构建分发包

```bash
# 构建分发包
make build

# 完整发布流程
make release
```

## 🤖 智能交互式更新系统（v2.0全新功能）

### 🌟 核心特性
- 📊 **Git集成检测**：自动检测git仓库中的文件变更
- ⏰ **文件时间检测**：git不可用时，基于文件修改时间检测
- 💬 **用户交互确认**：清晰的变更报告，用户自主决定更新范围
- 🎯 **精确模块化更新**：避免不必要的全面扫描
- 🧠 **智能策略推荐**：根据变更类型自动推荐更新策略

### 🚀 推荐使用方式

```bash
# 智能交互式更新（推荐）
python3 scripts/collect_data.py --interactive
python3 scripts/collect_data.py -i
```

### 📋 交互流程示例

```bash
🤖 智能更新建议
============================================================
📋 变更摘要:
  • 检测到 15 个文件变更
  • 检测到 2 个关键文件变更
  • 影响 2 个模块: scripts, examples

💡 系统建议:
  • 重点关注模块: scripts

🎯 推荐行动: 选择性更新
   受影响模块: scripts, examples

可更新的受影响模块:
  1. scripts
  2. examples

请选择更新方式:
  1. 更新所有受影响模块 (scripts, examples)
  2. 选择特定模块
  3. 全面更新所有模块
  4. 取消更新
```

### 🎯 其他更新方式

```bash
# 列出可用模块
python3 scripts/collect_data.py --list-modules

# 精确更新单个模块
python3 scripts/collect_data.py --module scripts
python3 scripts/collect_data.py -m examples

# 查看完整帮助
python3 scripts/collect_data.py --help

# 强制全面更新
python3 scripts/collect_data.py --full-scan

# 重新扫描（.gitignore更新后）
python3 scripts/collect_data.py --rescan
```

## 🔧 传统增量数据收集系统

### 特性
- 🎯 **智能触发**：基于文件变更自动判断是否需要收集
- ⚡ **性能优化**：增量收集比全量收集快60-88%
- 📊 **分级管理**：LOW/MEDIUM/HIGH三级变更处理
- 🔄 **实时响应**：重要文件变更立即检测

### 使用方式

```bash
# 智能增量收集（传统方式）
python3 scripts/collect_data.py /path/to/project --smart

# 检查项目变更状态
python3 scripts/collect_data.py /path/to/project --check

# 查看收集统计
python3 scripts/collect_data.py /path/to/project --stats

# 强制全量收集
python3 scripts/collect_data.py /path/to/project --force

# 非交互模式
python3 scripts/collect_data.py /path/to/project --smart --non-interactive
```

## 🔍 静态代码分析 + AI分析

### 功能特点
- 🎯 **静态扫描**：分析未调用的函数和废弃代码
- 🤖 **AI集成**：生成AI分析提示，支持深度代码审查
- 📊 **置信度评估**：智能评估函数未使用的置信度
- 🎛️ **模块化分析**：支持指定模块分析

### 使用方式

```bash
# 分析整个项目的未使用代码
python3 scripts/unused_code_analyzer.py

# 分析指定模块
python3 scripts/unused_code_analyzer.py --modules scripts src

# 生成AI分析提示
python3 scripts/unused_code_analyzer.py --ai-prompt

# 自定义置信度阈值和结果数量
python3 scripts/unused_code_analyzer.py --confidence 0.7 --max-results 15

# 指定输出文件
python3 scripts/unused_code_analyzer.py --output /path/to/report.json
```

### 输出文件
- `unused_code_report.json`：详细分析报告
- `unused_code_report.prompt.md`：AI分析提示（使用--ai-prompt时）

## 🖥️ 命令行工具

安装后可用的命令：

```bash
# 主CLI工具
sysmem --help

# 数据收集
sysmem-collect /path/to/project --smart

# 项目扫描
sysmem-scan /path/to/project

# 架构分析
sysmem-analyze /path/to/project

# 文档更新
sysmem-update /path/to/project

# 系统监控
sysmem-monitor /path/to/project

# 未使用代码分析
sysmem-unused /path/to/project --ai-prompt

# 安装状态检查
sysmem-install --check
```

## 🔄 项目修改流程

当修改项目代码后：

1. **自动检测变更**
   ```bash
   python3 scripts/auto_install.py --check
   ```

2. **系统提示安装**（如果需要）
   - 显示可用的安装命令
   - 用户选择执行安装

3. **验证安装**
   ```bash
   sysmem status
   ```

## 📊 性能对比

| 操作 | 优化前 | 优化后 | 提升效果 |
|------|--------|--------|----------|
| 全量数据收集 | 0.52秒 | 0.06秒 | 88% ⬇️ |
| 增量数据收集 | N/A | 0.14秒 | 新功能 |
| 变更检测 | N/A | 实时 | 新功能 |
| 未使用代码分析 | N/A | 智能分析 | 新功能 |

## 🛠️ 开发环境设置

### 安装开发依赖
```bash
make install-dev
```

### 代码格式化
```bash
make format
```

### 代码检查
```bash
make lint
```

### 运行测试
```bash
make test
```

## 📁 项目结构

```
sysmem/
├── setup.py                    # Python包配置
├── pyproject.toml             # 现代Python项目配置
├── Makefile                   # 自动化构建和安装
├── sysmem/                    # Python包目录
│   ├── __init__.py           # 包初始化
│   └── cli.py                # 命令行接口
├── scripts/                   # 核心脚本
│   ├── auto_install.py       # 交互式安装检查
│   ├── unused_code_analyzer.py # 静态代码分析
│   ├── collect_data.py       # 增量数据收集
│   ├── incremental_collector.py # 增量收集核心
│   ├── change_detector.py    # 智能变更检测
│   └── fingerprint.py        # 项目指纹系统
└── .claude/skill/sysmem/     # 数据存储目录
    ├── project_data.json     # 项目数据
    ├── .fingerprint.json     # 项目指纹
    └── unused_code_report.json # 代码分析报告
```

## 🔧 故障排除

### 常见问题

1. **模块导入错误**
   ```bash
   # 确保在正确的项目目录
   cd /path/to/sysmem
   python3 scripts/collect_data.py --check
   ```

2. **权限错误**
   ```bash
   # 使用用户模式安装
   python3 -m pip install -e .

   # 或者使用虚拟环境
   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install -e .
   ```

3. **依赖缺失**
   ```bash
   # 更新pip和setuptools
   python3 -m pip install --upgrade pip setuptools wheel build
   ```

## 📝 更新日志

### v2.0.0
- ✅ 实现智能增量数据收集系统
- ✅ 添加交互式编译安装提示
- ✅ 实现静态代码分析+AI分析功能
- ✅ 性能优化：数据收集提升60-88%
- ✅ 新增CLI命令行工具
- ✅ 完整的Python包管理支持