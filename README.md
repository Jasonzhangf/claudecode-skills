# Claude Code Skills 合集

## 🚀 概述

这是一个集合了多个Claude Code技能的仓库，每个技能都是独立的功能模块，可以在Claude Code环境中使用。这些技能旨在提升开发效率、项目管理和内容创作能力。

## 📋 技能列表

### 🏗️ 项目管理技能

#### [sysmem](./sysmem/) - 项目架构链条化管理技能
- **功能**: 自动化项目文档维护、架构分析和问题解决
- **核心特性**:
  - 🔍 智能项目扫描和结构分析
  - 📊 数据驱动架构风险分析
  - 📝 自动文档更新和维护
  - 🔧 交互式问题分析和解决
  - 🏥 项目架构健康监控
- **适用场景**: 项目维护、架构分析、代码质量检测、技术债务管理
- **使用方法**:
  ```bash
  # 安装技能
  cp -r sysmem ~/.claude/skills/

  # 使用技能
  /skill sysmem
  ```

### 🎨 内容创作技能

#### [novelgen](./novelgen/) - 智能小说生成器
- **功能**: 长篇小说断点续传、智能上下文管理和AI辅助编辑
- **核心特性**:
  - 📚 长篇小说断点续传
  - 🧠 智能上下文管理（三层压缩机制）
  - ✏️ AI辅助编辑和记忆管理
  - 🎯 章节跳转和智能导入设定
  - 📖 交互式创作体验
- **适用场景**: 小说创作、故事续写、创意写作
- **使用方法**:
  ```bash
  # 安装技能
  cp -r novelgen ~/.claude/skills/

  # 使用技能
  /skill novelgen
  ```

## 🛠️ 安装和使用

### 系统要求
- Claude Code 环境
- Python 3.8+ (部分技能需要)
- Git

### 安装技能

#### 单个技能安装
```bash
# 克隆仓库
git clone https://github.com/Jasonzhangf/claudecode-skills.git
cd claudecode-skills

# 安装sysmem技能
cp -r sysmem ~/.claude/skills/

# 安装novelgen技能
cp -r novelgen ~/.claude/skills/
```

#### 批量安装
```bash
# 安装所有技能
for skill in sysmem novelgen; do
    cp -r $skill ~/.claude/skills/
done
```

### 使用技能

在Claude Code环境中：
1. 使用 `/skill` 命令调用技能
2. 根据技能提示进行操作
3. 查看技能目录中的README.md了解详细用法

## 📚 技能开发指南

### 技能结构标准
每个技能应包含以下结构：
```
skill-name/
├── README.md          # 技能说明文档
├── SKILL.md           # Claude Code技能定义
├── scripts/           # 核心功能脚本
├── references/        # 参考文档和模板
├── examples/          # 使用示例
└── assets/           # 资源文件
```

### 开发新技能
1. 参考现有技能的结构
2. 创建标准的README.md和SKILL.md
3. 实现核心功能脚本
4. 提供使用示例和文档

## 🤝 贡献指南

### 贡献方式
- 提交新的技能
- 改进现有技能
- 报告问题和建议
- 完善文档

### 提交流程
1. Fork 本仓库
2. 创建功能分支: `git checkout -b feature/new-skill`
3. 提交更改: `git commit -m "Add new skill: xxx"`
4. 推送分支: `git push origin feature/new-skill`
5. 创建 Pull Request

### 技能提交规范
- 每个技能目录独立完整
- 包含详细的README.md文档
- 提供SKILL.md定义文件
- 包含使用示例
- 遵循代码规范

## 📖 文档和资源

### 技能文档
- [sysmem 详细文档](./sysmem/README.md)
- [novelgen 详细文档](./novelgen/README.md)

### 开发资源
- [Claude Code 官方文档](https://docs.claude.com/claude-code)
- [技能开发指南](./docs/skill-development-guide.md)
- [API 参考文档](./docs/api-reference.md)

## 🐛 问题反馈

如果遇到问题或有建议，请：
1. 查看 [FAQ](./docs/faq.md)
2. 搜索现有的 [Issues](https://github.com/Jasonzhangf/claudecode-skills/issues)
3. 创建新的 Issue 描述问题

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [Claude Code 官方网站](https://claude.ai/code)
- [GitHub 仓库](https://github.com/Jasonzhangf/claudecode-skills)
- [技能市场](https://claude.ai/skills)

---

**注意**: 这些技能由社区开发和维护，使用前请阅读各技能的文档和许可证信息。