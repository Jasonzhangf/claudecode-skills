# CLAUDE.md - Sysmem项目架构文档

## 技能包说明

### sysmem
支持Claude Code和Codex双重环境的项目架构链条化管理技能包，用于自动化项目文档维护、架构分析和代码结构优化。支持跨环境数据同步和统一管理。

## 项目架构

### 模块结构
```
sysmem/                          # 项目架构链条化管理系统
├── scripts/                     # 核心功能脚本模块
│   ├── collect_data.py         # 智能数据收集器 - 扫描项目结构并收集模块信息
│   ├── scan_project.py         # 项目结构扫描器 - 基础项目遍历和文件信息收集
│   ├── analyze_architecture.py # 架构风险分析器 - 检测重复代码和架构问题
│   ├── update_claude_md.py     # Claude文档更新器 - 智能更新项目文档
│   └── interactive_analyzer.py # 交互式分析工具 - 用户友好的分析界面
├── references/                  # 参考文档和模板模块
│   ├── readme_template.md      # 标准README模板 - 确保文档格式一致性
│   ├── claude_md_template.md   # CLAUDE.md模板 - 项目架构文档标准
│   └── analysis_criteria.md    # 分析标准定义 - 架构分析规则和标准
├── examples/                    # 使用示例模块
│   ├── basic_usage/            # 基础使用示例 - 简单的入门示例
│   ├── advanced_analysis/      # 高级分析示例 - 复杂场景的使用方法
│   └── custom_templates/       # 自定义模板示例 - 模板定制指导
├── assets/                     # 资源文件模块
│   └── project_structure_example.json # 数据格式示例 - 标准数据结构示例
├── claude-sysmem-chain/        # 项目数据存储模块
│   └── skills/
│       └── sysmem/
│           ├── project_data.json     # 项目完整数据 - 收集的所有项目信息
│           └── project_structure.json # 项目结构信息 - 结构化项目数据
├── README.md                   # 项目主文档 - 项目概述和使用指南
├── SKILL.md                    # 技能说明文档 - 技能包功能说明
├── CLAUDE-sysmem-chain.md      # Claude环境架构文档
└── AGENTS-sysmem-chain.md      # Agents环境架构文档
```

### 模块功能定义

#### scripts模块
- **核心功能定义**: 提供项目数据收集、分析、文档更新的完整工具链
- **接口定义**:
  - `collect_data.py` - 主要数据收集接口，输出project_data.json
  - `analyze_architecture.py` - 架构分析接口，检测重复和风险
  - `update_claude_md.py` - 文档更新接口，智能更新项目文档
- **数据结构**: 使用JSON格式存储项目数据，支持模块化分析

#### references模块
- **核心功能定义**: 提供标准化的文档模板和分析标准
- **接口定义**:
  - `readme_template.md` - README标准化模板
  - `claude_md_template.md` - CLAUDE.md架构文档模板
  - `analysis_criteria.md` - 架构分析标准和规则
- **数据结构**: Markdown格式的模板文档，支持结构化内容

#### examples模块
- **核心功能定义**: 提供不同场景下的使用示例和最佳实践
- **接口定义**: 分层示例结构，从基础到高级的使用案例
- **数据结构**: 示例代码和配置文件，包含详细说明文档

#### assets模块
- **核心功能定义**: 提供数据格式示例和配置参考
- **接口定义**: JSON格式的数据结构示例
- **数据结构**: 标准化的JSON配置文件

## 开发规范

### 文档更新流程
1. **代码变更必须同步更新对应模块的README.md**
2. **使用sysmem技能更新CLAUDE.md中的架构树**
3. **在README.md中记录代码变更历史**
4. **执行数据收集验证文档一致性**

### 架构一致性要求
- **所有模块README必须遵循统一模板**
- **第一行必须包含结构化功能描述**
- **重要定义必须标记为Ground Truth**
- **保持跨环境文档同步**

### 文件组织原则
- **相关功能文件组织在同一模块目录**
- **避免跨模块的文件重复**
- **配置文件集中管理**
- **数据文件统一存储在.claude/skill/sysmem/目录**

### 代码质量要求
- **消除重复函数，提取公共工具类**
- **保持函数命名一致性**
- **添加适当的错误处理**
- **维护代码文档完整性**

## System管理机制

### 自动化管理流程
1. **数据收集**: 定期执行`collect_data.py`扫描项目状态
2. **架构分析**: 使用`analyze_architecture.py`检测风险和问题
3. **文档同步**: 基于收集数据智能更新项目文档
4. **质量监控**: 持续监控文档覆盖率和架构健康度

### 跨环境同步
- **Claude Code环境**: 主要的数据收集和初步分析
- **Codex环境**: 深度分析和代理协作
- **数据同步**: 自动同步项目数据和分析结果
- **配置统一**: 双重环境共享配置和模板

### 质量保证指标
- **模块文档覆盖率**: 目标 100%
- **重复代码检测**: 目标 0%
- **架构风险数量**: 最小化
- **目录清洁度**: 保持根目录简洁

## 当前架构状态

### 已识别问题
- **重复函数**: 4个需要重构的重复函数
- **未记录文件**: 3个需要添加到README的文件
- **缺失文档**: 需要创建AGENTS-sysmem-chain.md

### 优化计划
- **重构公共函数**: 提取工具类避免代码重复
- **完善文档**: 更新所有模块README文件
- **建立同步机制**: 实现双重环境数据同步
- **质量监控**: 建立自动化质量检查流程