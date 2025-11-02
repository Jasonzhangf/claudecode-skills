# Scripts Module

## 功能定义
提供 Sysmem 项目的核心脚本功能集，包含项目数据收集、分析和更新工具。

## 核心接口定义

### 主要脚本文件
- `collect_data.py` - 项目数据收集器，支持智能模块化更新和 .gitignore 解析
- `analyze_architecture.py` - 架构风险分析器，检测重复代码和架构问题
- `update_claude_md.py` - Claude 文档更新器，智能更新项目文档
- `scan_project.py` - 项目结构扫描器，基础项目遍历和文件信息收集
- `utils.py` - 公共工具类，提供脚本间共享的工具函数

### 数据结构
- 使用 JSON 格式存储项目数据，支持模块化分析
- 输出文件存储在 `.claude/skill/sysmem/` 目录

## 重要定义 (Ground Truth)
- **模块化更新优先**: 默认使用单模块更新，仅在必要时进行全面扫描
- **智能检测**: 自动判断是否需要全面更新 vs 模块化更新
- **Gitignore 集成**: 动态读取和应用 .gitignore 规则test change for interactive update
