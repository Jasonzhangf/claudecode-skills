# Sysmem - 项目架构链条化管理系统 v2.0

## 🚀 概述

Sysmem是一个全面的自动化项目架构管理系统，提供智能项目扫描、增量数据收集、静态代码分析和自动化文档更新功能。通过智能变更检测、AI辅助代码分析和交互式安装管理，确保项目架构的一致性、完整性和高性能。

## ✨ 核心特性

### 🔍 智能项目管理
- **🎯 增量数据收集**：智能检测项目变更，增量更新数据，性能提升88%
- **🤖 智能触发机制**：基于变更级别(LOW/MEDIUM/HIGH)自动判断是否需要收集
- **📊 实时变更检测**：文件变更实时响应，避免不必要的全量扫描
- **📈 性能监控**：详细的数据收集统计和性能分析

### 🔬 静态代码分析
- **🎯 未使用代码检测**：智能扫描未调用的函数和废弃代码
- **🤖 AI辅助分析**：生成结构化AI分析提示，支持深度代码审查
- **📊 置信度评估**：基于多种因素计算未使用函数的置信度
- **🎛️ 模块化分析**：支持指定模块范围分析

### 🚀 自动化安装管理
- **🔄 交互式安装提示**：项目修改后自动检测并提示安装
- **📦 动态配置生成**：根据项目结构自动生成安装命令
- **🔧 源代码同步**：安装目录与源代码双向同步
- **📋 项目类型检测**：自动识别Python/Node.js/通用项目

### 📝 完整架构管理
- **🔍 智能项目扫描**：自动发现和分析项目结构，识别模块依赖关系
- **📊 数据驱动分析**：基于收集的数据提供深度架构分析和改进建议
- **📝 自动文档管理**：保持项目文档与架构的实时同步更新
- **🎯 模块化管理**：标准化的模块组织和文档管理流程
- **🛡️ 架构健康监控**：持续监控项目架构质量，预警潜在风险
- **🔧 重复代码检测**：智能识别代码重复和架构不一致问题

## 📁 项目结构

```
sysmem/
├── README.md                          # 项目主文档
├── INSTALLATION.md                    # 安装和使用指南
├── WORKFLOW.md                        # 完整工作流程说明
├── setup.py                          # Python包配置
├── pyproject.toml                    # 现代Python项目配置
├── Makefile                          # 自动化构建和安装
├── SKILL.md                          # 技能说明文档
├── CLAUDE-sysmem-chain.md            # Claude环境架构文档
├── AGENTS-sysmem-chain.md            # Agents环境架构文档
├── sysmem/                           # Python包目录
│   ├── __init__.py                  # 包初始化
│   └── cli.py                       # 命令行接口
├── scripts/                          # 核心功能脚本
│   ├── collect_data.py              # 智能数据收集器（增量版）
│   ├── incremental_collector.py     # 增量收集核心逻辑
│   ├── change_detector.py           # 智能变更检测
│   ├── fingerprint.py               # 项目指纹系统
│   ├── unused_code_analyzer.py      # 静态代码分析器
│   ├── auto_install.py              # 交互式安装检查
│   ├── sync_to_source.py            # 源代码同步工具
│   ├── install_project.py           # 自动生成的安装脚本
│   ├── scan_project.py              # 项目结构扫描器
│   ├── analyze_architecture.py      # 架构风险分析器
│   ├── update_claude_md.py          # Claude文档更新器
│   ├── interactive_analyzer.py      # 交互式分析工具
│   ├── problem_analyzer.py          # 问题分析器
│   ├── interactive_problem_solver.py # 交互式问题解决器
│   ├── system_monitor.py            # 系统监控器
│   └── utils.py                     # 公共工具类
├── references/                       # 参考文档和模板
│   ├── readme_template.md           # 标准README模板
│   ├── claude_md_template.md        # CLAUDE.md模板
│   └── analysis_criteria.md         # 分析标准定义
├── assets/                          # 资源文件
│   └── project_structure_example.json # 数据格式示例
├── examples/                        # 使用示例
│   ├── basic_usage/                 # 基础使用示例
│   ├── advanced_analysis/           # 高级分析示例
│   ├── custom_templates/            # 自定义模板示例
│   └── intelligent_update_example.md # 智能更新工作流程详解
└── claude-sysmem-chain/             # 项目数据存储
    └── skills/
        └── sysmem/
            ├── project_data.json    # 项目完整数据
            └── project_structure.json # 项目结构信息
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Git (用于版本控制)
- 项目目录结构

### 📦 安装方式

#### 方式1: 使用自动安装脚本（推荐）
```bash
# 下载项目到本地
git clone https://github.com/your-repo/sysmem.git
cd sysmem

# 运行自动生成的安装脚本
python3 scripts/install_project.py

# 根据提示选择合适的安装命令
```

#### 方式2: 使用Makefile
```bash
# 用户模式安装
make install

# 开发模式安装（包含开发依赖）
make install-dev

# 全局安装（需要sudo权限）
make global-install
```

#### 方式3: 使用pip直接安装
```bash
# 用户模式安装
python3 -m pip install -e .

# 全局安装
sudo python3 -m pip install .

# 开发模式安装
python3 -m pip install -e ".[dev]"
```

### 🎯 快速验证安装

```bash
# 检查系统状态
python3 -c "import sysmem; print(f'Sysmem {sysmem.__version__} 安装成功')"

# 或使用CLI工具（安装后）
sysmem status
```

## 📖 核心功能使用

### 🔄 智能增量数据收集

#### 基础使用
```bash
# 智能增量收集（推荐）
python3 scripts/collect_data.py /path/to/project --smart

# 检查项目变更状态
python3 scripts/collect_data.py /path/to/project --check

# 查看收集统计信息
python3 scripts/collect_data.py /path/to/project --stats

# 非交互模式（自动化脚本中使用）
python3 scripts/collect_data.py /path/to/project --smart --non-interactive
```

#### 性能对比
- 🚀 **全量收集优化前**: 0.52秒
- ⚡ **全量收集优化后**: 0.06秒 (88% ⬇️)
- 🎯 **增量收集**: 0.14秒 (新功能)

### 🔬 静态代码分析

#### 未使用代码检测
```bash
# 分析整个项目的未使用代码
python3 scripts/unused_code_analyzer.py

# 分析指定模块
python3 scripts/unused_code_analyzer.py --modules scripts src

# 生成AI分析提示
python3 scripts/unused_code_analyzer.py --ai-prompt

# 自定义分析参数
python3 scripts/unused_code_analyzer.py \
  --confidence 0.7 \
  --max-results 15 \
  --output /path/to/report.json
```

#### 输出文件
- `unused_code_report.json` - 详细分析报告
- `unused_code_report.prompt.md` - AI分析提示

### 🚀 交互式安装管理

#### 变更检测和安装提示
```bash
# 检查项目是否需要重新安装
python3 scripts/auto_install.py --check

# 系统会自动提示可用的安装命令：
# 🔄 检测到项目变更，建议执行编译安装
# 可用的安装命令:
#   make install       # 用户模式安装
#   make global-install # 全局安装（需要sudo）
#   make install-dev   # 开发模式安装
```

#### 源代码同步
```bash
# 将安装目录的更改同步回源代码
python3 scripts/sync_to_source.py

# 非交互模式同步
python3 scripts/sync_to_source.py --non-interactive
```

### 🖥️ CLI工具（安装后）

安装后可使用的命令行工具：
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

### 📊 传统功能使用

#### 项目初始化
```bash
# 步骤1: 智能数据收集
python3 scripts/collect_data.py /path/to/project --smart

# 步骤2: 将生成的project_data.json交给Claude进行分析和文档更新
# 对Claude说: "基于project_data.json的数据，请更新我的项目文档"
```

#### 定期维护
```bash
# 定期执行架构扫描
python3 scripts/scan_project.py /path/to/project

# 深度架构分析
python3 scripts/analyze_architecture.py /path/to/project

# 系统健康监控
python3 scripts/system_monitor.py /path/to/project
```

### 核心功能详解

#### 🔍 智能数据收集 (`collect_data.py`)
- **功能**: 全面扫描项目结构，收集模块信息、文档状态、架构问题
- **输出**: 结构化的 `project_data.json` 文件
- **特点**: 非侵入式扫描，保护项目代码完整性

#### 📊 架构分析 (`analyze_architecture.py`)
- **功能**: 深度分析架构风险、重复代码、配置不一致问题
- **检测内容**:
  - **文件重复**: 同一模块内相似文件名检测（需用户进一步分析功能重复）
  - **函数重复**: 函数模式分析，识别可能的相似功能（需用户进一步分析）
  - 实现不一致 (配置文件结构、API接口格式)
  - 文档完整性评估
- **分析原则**:
  - **静态分析**: 仅提供警告参考，不自动判断功能重复
  - **用户主导**: 功能重复分析需要用户主导，基于实际代码逻辑判断
  - **模块级别**: 重点检测同一模块内的潜在重复问题
- **输出**: 详细的架构分析报告和改进建议

#### 📝 文档更新 (`update_claude_md.py`)
- **功能**: 基于收集的数据智能更新项目文档
- **策略**: 增量更新，保护用户自定义内容
- **支持**: CLAUDE.md、模块README、API文档

#### 🎯 交互式分析 (`interactive_analyzer.py`)
- **功能**: 提供用户友好的交互式分析界面
- **特性**: 实时反馈、自定义分析规则、批量处理

#### 🔧 交互式问题解决 (`problem_analyzer.py`, `interactive_problem_solver.py`)
- **功能**: 基于架构定义的智能问题分析和解决系统
- **核心流程**:
  1. **问题意图识别**: AI识别问题类型，自动关联相关模块
  2. **证据收集分析**: 基于CLAUDE.md识别相关日志文件，收集证据支持分析
  3. **原因诊断定位**: 精确定位问题发生点和可能原因，提供证据支持
  4. **方案生成评估**: 生成多个解决方案，详细分析利弊
  5. **用户交互选择**: 用户选择最佳解决方案，技能提供引导
  6. **执行指导**: 技能提供详细的执行步骤，用户手动执行
- **核心特点**:
  - **纯引导模式**: 技能只控制进度和流程，不执行任何代码
  - **证据驱动**: 所有分析都有证据支持，提供置信度评估
  - **多方案选择**: 提供多个解决方案，详细阐述利弊
  - **架构约束**: 严格遵循CLAUDE.md和模块README中的架构定义
  - **完全用户控制**: 用户自主选择方案并手动执行修复
- **使用方式**:
  ```bash
  # 交互式问题解决（推荐）
  python3 scripts/interactive_problem_solver.py

  # 直接命令行分析
  python3 scripts/problem_analyzer.py "系统性能很慢，需要优化"
  ```

#### 🏥 系统监控 (`system_monitor.py`)
- **功能**: 自动化项目架构健康监控
- **特性**:
  - 量化健康评分
  - 趋势分析
  - 问题预警
  - **改进计划生成**: 生成需要用户批准的改进计划
  - **优先级评估**: 基于影响程度评估问题优先级
  - **工作量估算**: 估算改进所需的时间和资源
- **安全机制**:
  - 只进行分析和监控，不自动修改任何文件
  - 改进计划需要用户审查和批准
  - 提供详细的问题分析和修复建议
- **使用方式**:
  ```bash
  # 执行健康检查
  python3 scripts/system_monitor.py

  # 查看健康趋势
  python3 scripts/system_monitor.py --trend
  ```

## 📊 数据文件说明

### project_data.json 结构
```json
{
  "project_info": {
    "name": "项目名称",
    "path": "项目路径",
    "scan_time": "扫描时间"
  },
  "modules": [
    {
      "name": "模块名称",
      "path": "模块路径",
      "files": ["文件列表"],
      "readme_exists": true,
      "documentation_quality": "high|medium|low"
    }
  ],
  "architecture_issues": [
    {
      "type": "duplicate_files|inconsistent_config|missing_docs",
      "severity": "high|medium|low",
      "description": "问题描述",
      "suggestion": "解决建议"
    }
  ]
}
```

### project_structure.json 结构
```json
{
  "root_structure": "根目录结构",
  "module_tree": "模块树形结构",
  "file_types": {
    "python": "Python文件数量",
    "javascript": "JavaScript文件数量",
    "documentation": "文档文件数量"
  }
}
```

## 🎯 最佳实践

### 项目初始化阶段
1. **建立基线**: 首次使用时执行完整扫描和分析
2. **文档标准化**: 使用提供的模板建立标准化文档
3. **配置检查**: 确保所有配置文件的一致性

### 开发维护阶段
1. **定期扫描**: 建议每周执行一次架构健康检查
2. **及时更新**: 代码变更后及时更新相关文档
3. **风险监控**: 关注架构分析报告中的高风险项

### 团队协作阶段
1. **统一标准**: 团队使用相同的文档模板和分析标准
2. **代码审查**: 将架构分析作为代码审查的一部分
3. **知识共享**: 保持文档的实时更新和共享

## 📋 质量保证

### 监控指标
- **模块文档覆盖率**: 目标 100%
- **重复代码检测**: 目标 0%
- **架构风险数量**: 最小化
- **目录清洁度**: 保持根目录简洁

### 分析标准
详细的分析标准请参考 `references/analysis_criteria.md`，包括：
- 文件重复检测规则
- 代码相似度计算方法
- 文档质量评估标准
- 架构复杂度评分体系

## 🔒 安全机制和用户控制

### 用户批准原则
sysmem严格遵循用户批准原则，区分文档更新和代码修复的不同权限：

1. **文档更新权限**:
   - **允许直接更新**: CLAUDE.md、README.md等文档文件
   - **自动化文档管理**: `update_claude_md.py`可直接更新架构文档
   - **增量更新保护**: 保护用户自定义内容，进行智能增量更新
   - **模板应用**: 可直接应用标准化的文档模板

2. **代码修复权限**:
   - **禁止自动修复**: 所有代码修复必须经过用户明确批准
   - **模拟执行**: 只提供修复建议和模拟执行，不直接修改代码
   - **用户完全控制**: 用户完全控制所有代码修复操作
   - **手动修复指导**: 提供详细的修复步骤和指导

3. **分析权限**:
   - **纯分析模式**: 架构分析器、系统监控器只进行分析和监控
   - **非侵入式**: 不修改任何源文件，只生成分析报告和建议
   - **数据收集**: 只在`.claude/skill/sysmem/`目录写入数据文件

### 权限分级机制

#### 🟢 直接操作权限（文档类）
- `update_claude_md.py` - CLAUDE.md文档更新
- `collect_data.py` - 数据收集和报告生成
- `scan_project.py` - 项目结构扫描

#### 🟡 分析建议权限（报告类）
- `analyze_architecture.py` - 架构风险分析
- `system_monitor.py` - 系统健康监控
- `interactive_analyzer.py` - 交互式分析报告

#### 🔴 用户批准权限（代码修复类）
- `problem_analyzer.py` - 问题分析和解决方案
- 代码修复执行（仅模拟，需用户批准）
- 配置文件修改（需用户批准）

### 用户控制流程

#### 🟢 文档更新流程（直接操作）
```bash
# 示例：CLAUDE.md文档更新
1. python3 scripts/collect_data.py
2. python3 scripts/update_claude_md.py
3. 系统直接更新CLAUDE.md文档
4. 增量更新保护用户自定义内容
```

#### 🟡 架构分析流程（报告生成）
```bash
# 示例：架构风险分析
1. python3 scripts/analyze_architecture.py
2. 系统扫描并分析架构风险
3. 生成详细的分析报告
4. 提供改进建议（不自动执行）
```

#### 🔴 问题解决流程（用户批准）
```bash
# 示例：代码问题解决
1. python3 scripts/interactive_problem_solver.py
2. 用户描述问题
3. 系统分析并生成解决方案
4. 用户选择解决方案
5. 系统显示执行计划并请求批准
6. 用户批准后，系统模拟执行
7. 用户根据模拟结果手动执行修复
```

## 🔧 高级配置

### 自定义分析规则
可以通过修改配置文件自定义分析规则：
```python
# 在collect_data.py中配置
config = {
    "scan_depth": "deep",           # 扫描深度
    "include_hidden": False,        # 是否包含隐藏文件
    "file_types": [".py", ".js", ".md"],  # 目标文件类型
    "duplicate_threshold": 0.8      # 重复检测阈值
}
```

### 自定义文档模板
1. 修改 `references/` 目录下的模板文件
2. 使用 `update_claude_md.py` 应用自定义模板
3. 保持模板格式的一致性

## 🚀 路线图

### v1.1.0 (开发中)
- [ ] Web界面支持
- [ ] 多项目并行管理
- [ ] 插件系统
- [ ] CI/CD集成

### v2.0.0 (规划中)
- [ ] 机器学习驱动的架构优化建议
- [ ] 实时架构监控仪表板
- [ ] 团队协作功能
- [ ] 企业级权限管理

## 🤝 贡献指南

### 开发环境
1. Fork本项目
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 安装依赖: `pip install -r requirements.txt`
4. 运行测试: `python -m pytest tests/`
5. 提交更改: `git commit -m "Add new feature"`

### 提交规范
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 其他更改

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持和反馈

- **文档**: 查看 `docs/` 目录下的详细文档
- **示例**: 查看 `examples/` 目录下的使用示例
- **问题反馈**: 通过GitHub Issues提交问题
- **技术支持**: 联系项目维护者

## 🔗 相关资源

- [Claude Code文档](https://docs.claude.com/claude-code)
- [项目最佳实践指南](references/best_practices.md)
- [API参考文档](docs/api_reference.md)

## 📋 代码变更历史

### 2025-10-31 - 权限分级机制和流程优化
- **建立权限分级机制**: 明确区分文档更新（🟢直接操作）、分析报告（🟡建议权限）、代码修复（🔴用户批准）三级权限
- **优化文档更新流程**: `update_claude_md.py`可直接更新CLAUDE.md等文档文件，支持增量更新保护用户内容
- **完善分析报告机制**: 所有架构分析和监控工具只生成报告和建议，不自动修改任何文件
- **强化代码修复批准**: 所有代码修复操作必须经过用户明确批准，只提供模拟执行和手动修复指导
- **建立清晰的用户控制流程**: 为不同类型的操作提供明确的流程指导，确保用户了解权限边界
- **更新安全机制文档**: 新增权限分级说明和用户控制流程，提供清晰的操作指引
- **完善问题分析功能**: 实现基于架构定义的6步交互式引导式问题分析和解决系统
- **创建智能分析器**: `problem_analyzer.py`提供AI驱动的意图识别和模块关联
- **实现用户交互界面**: `interactive_problem_solver.py`提供友好的命令行交互体验
- **建立系统监控机制**: `system_monitor.py`提供项目架构健康监控和趋势分析
- **完善System管理**: 优化数据收集、代码重构、文档同步等系统管理功能
- **创建CLAUDE.md文件**: 建立完整的项目架构文档，定义模块功能和开发规范
- **消除重复代码**: 创建`scripts/utils.py`公共工具类，重构重复函数
- **修复数据收集器Bug**: 解决变量引用顺序和类型错误问题

## 📋 更新日志

### v2.0.0 (2025-10-31) - 重大版本更新
- 🚀 **智能增量数据收集系统**:
  - 实现基于项目指纹的增量更新机制
  - 智能触发系统，基于变更级别(LOW/MEDIUM/HIGH)自动判断
  - 性能优化88%，全量收集从0.52秒降至0.06秒
  - 实时变更检测，避免不必要的全量扫描

- 🔬 **静态代码分析+AI分析**:
  - 未使用代码检测，智能扫描未调用的函数
  - AI辅助分析，生成结构化分析提示
  - 置信度评估系统，基于多种因素计算
  - 模块化分析，支持指定范围分析

- 🚀 **自动化安装管理**:
  - 交互式安装提示，项目修改后自动检测
  - 动态配置生成，根据项目结构生成安装命令
  - 源代码同步，安装目录与源代码双向同步
  - 项目类型检测，自动识别Python/Node.js/通用项目

- 📦 **完整包管理支持**:
  - Python包配置(setup.py, pyproject.toml)
  - Makefile自动化构建
  - CLI命令行工具集成
  - 开发/用户/全局安装模式

- 🔄 **工作流程优化**:
  - 完整的开发工作流程设计
  - 自动化同步机制
  - 性能监控和统计
  - 非交互模式支持

### v1.5.0 (2025-10-31) - 功能完善
- **建立清晰的用户控制流程**: 为不同类型的操作提供明确的流程指导，确保用户了解权限边界
- **更新安全机制文档**: 新增权限分级说明和用户控制流程，提供清晰的操作指引
- **完善问题分析功能**: 实现基于架构定义的6步交互式引导式问题分析和解决系统
- **创建智能分析器**: `problem_analyzer.py`提供AI驱动的意图识别和模块关联
- **实现用户交互界面**: `interactive_problem_solver.py`提供友好的命令行交互体验
- **建立系统监控机制**: `system_monitor.py`提供项目架构健康监控和趋势分析
- **完善System管理**: 优化数据收集、代码重构、文档同步等系统管理功能
- **创建CLAUDE.md文件**: 建立完整的项目架构文档，定义模块功能和开发规范
- **消除重复代码**: 创建`scripts/utils.py`公共工具类，重构重复函数
- **修复数据收集器Bug**: 解决变量引用顺序和类型错误问题

### v1.0.0 (2025-10-31) - 项目初始化
- **基础架构建立**: 创建完整的项目结构和核心功能模块
- **数据收集系统**: 实现智能项目扫描和数据收集功能
- **文档模板系统**: 提供标准化的README和CLAUDE.md模板
- **分析工具**: 开发架构风险分析和重复代码检测功能

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 📞 联系方式

- 项目主页: [GitHub Repository](https://github.com/your-repo/sysmem)
- 问题反馈: [Issues](https://github.com/your-repo/sysmem/issues)

---

**注意**: Sysmem是一个持续发展的项目，所有功能和文档都会自动保持同步更新。使用过程中遇到问题请及时反馈，我们会持续改进和完善。