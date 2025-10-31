#!/usr/bin/env python3
"""
交互式项目分析器 - 提供与Claude直接交互的接口
"""

import json
import sys
from pathlib import Path
from collect_data import ProjectDataCollector

class InteractiveAnalyzer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.collector = ProjectDataCollector(root_path)

    def run_analysis(self) -> str:
        """运行分析并生成Claude可读的报告"""
        print("🔍 开始交互式项目分析...")

        # 收集数据
        data = self.collector.collect_all_data()

        # 生成Claude友好的报告
        report = self._generate_claude_report(data)

        # 保存数据文件供参考
        self.collector.export_data(data, "project_data.json")

        return report

    def _generate_claude_report(self, data: dict) -> str:
        """生成Claude容易理解的格式化报告"""

        report_lines = [
            "# 项目架构分析报告",
            "",
            f"**扫描时间**: {data['scan_info']['scan_time']}",
            f"**项目路径**: {data['scan_info']['project_root']}",
            "",
            "## 📊 项目概况",
            f"- 发现模块数量: {len(data['modules'])}",
            f"- CLAUDE.md存在: {'✅ 是' if data['claude_md_info']['exists'] else '❌ 否'}",
            "",
            "## 📁 发现的模块",
            ""
        ]

        # 模块信息
        for module_path, module_data in data['modules'].items():
            report_lines.extend([
                f"### {module_path}",
                f"**功能描述**: {module_data['function_summary']}",
                f"**文件数量**: {len(module_data['files'])}",
                f"**README状态**: {'✅ 完整' if len(module_data['readme_content']) > 100 else '⚠️ 需要完善'}",
                ""
            ])

            # 重要定义
            if module_data['important_definitions']:
                report_lines.append("**重要定义 (Ground Truth)**:")
                for definition in module_data['important_definitions']:
                    report_lines.append(f"- {definition}")
                report_lines.append("")

        # 架构问题
        report_lines.extend([
            "## 🚨 架构问题分析",
            ""
        ])

        arch_issues = data['architecture_analysis']

        if arch_issues['duplicate_files']:
            report_lines.append("### 重复文件")
            for issue in arch_issues['duplicate_files']:
                report_lines.append(f"- **{issue['filename']}**: {len(issue['paths'])}个位置")
                for path in issue['paths']:
                    report_lines.append(f"  - {path}")
            report_lines.append("")

        if arch_issues['duplicate_functions']:
            report_lines.append("### 重复函数")
            for issue in arch_issues['duplicate_functions']:
                report_lines.append(f"- **{issue['signature']}**:")
                for loc in issue['locations']:
                    report_lines.append(f"  - {loc['file']}:{loc['line']}")
            report_lines.append("")

        # 未记录文件
        if data['untracked_files']:
            report_lines.extend([
                "## 📋 未记录文件",
                ""
            ])

            cleanup_suggestions = {"删除": [], "需要记录": [], "需要检查": []}

            for file_info in data['untracked_files']:
                suggestion = file_info['suggestion']
                if "删除" in suggestion:
                    cleanup_suggestions["删除"].append(file_info['file'])
                elif "记录" in suggestion:
                    cleanup_suggestions["需要记录"].append(file_info['file'])
                else:
                    cleanup_suggestions["需要检查"].append(file_info['file'])

            for category, files in cleanup_suggestions.items():
                if files:
                    report_lines.append(f"### {category}")
                    for file_path in files:
                        report_lines.append(f"- {file_path}")
                    report_lines.append("")

        # CLAUDE.md状态
        claude_info = data['claude_md_info']
        report_lines.extend([
            "## 📝 CLAUDE.md状态",
            "",
            f"**文件存在**: {'✅ 是' if claude_info['exists'] else '❌ 否'}",
            f"**包含system-chain说明**: {'✅ 是' if claude_info['has_system_chain_section'] else '❌ 否'}",
            f"**包含模块结构**: {'✅ 是' if claude_info['has_module_structure'] else '❌ 否'}",
            ""
        ])

        if claude_info['exists']:
            report_lines.extend([
                "### 当前章节结构",
                ""
            ])
            for section_name, content in claude_info['sections'].items():
                report_lines.append(f"**{section_name}**: {len(content)} 字符")

        # 更新建议
        report_lines.extend([
            "",
            "## 💡 更新建议",
            "",
            "### CLAUDE.md更新",
            ""
        ])

        suggestions = data['update_suggestions']
        for suggestion in suggestions['claude_md_updates']:
            report_lines.append(f"- {suggestion}")

        report_lines.extend([
            "",
            "### README更新",
            ""
        ])

        for suggestion in suggestions['readme_updates']:
            report_lines.append(f"- {suggestion}")

        report_lines.extend([
            "",
            "## 🎯 推荐操作",
            "",
            "基于以上分析，建议按以下优先级处理：",
            "",
            "1. **高优先级**: 处理重复函数和文件",
            "2. **中优先级**: 更新CLAUDE.md和模块README",
            "3. **低优先级**: 清理未记录文件",
            "",
            "---",
            "",
            "💡 **提示**: 请告诉Claude你希望优先处理哪些项目，我将提供具体的更新方案。",
            "",
            "**数据文件**: 详细数据已保存到 `project_data.json`",
            ""
        ])

        return "\n".join(report_lines)

    def print_claude_instructions(self):
        """打印与Claude交互的说明"""
        instructions = """
## 🤖 与Claude交互指南

### 方式1: 直接复制报告
将上面的报告复制给Claude，然后说：
```
基于这个分析报告，请帮我：
1. 更新CLAUDE.md，保留我的自定义内容
2. 修复重复代码问题
3. 完善模块README文档
```

### 方式2: 提供JSON数据
将 `project_data.json` 的内容提供给Claude，然后说：
```
基于这个项目数据，请进行智能分析和文档更新
```

### 方式3: 逐项处理
针对具体问题询问Claude：
```
我的项目中有重复的process_data函数，应该如何重构？
请帮我更新src/core模块的README文档
```

### 推荐的Claude指令模板：
```
基于项目分析报告，请：

🎯 **文档更新**:
- 更新CLAUDE.md，添加system-chain技能说明
- 保持我现有的自定义内容不变
- 同步模块结构变化

🔧 **代码优化**:
- 处理重复函数问题
- 给出重构建议

📋 **文档完善**:
- 更新模块README的文件描述
- 标记重要的Ground Truth定义

请逐项说明，让我确认后再执行。
```
        """
        print(instructions)

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="交互式项目分析器")
    parser.add_argument("--path", default=".", help="项目根目录路径")
    args = parser.parse_args()

    analyzer = InteractiveAnalyzer(args.path)

    try:
        # 生成报告
        report = analyzer.run_analysis()

        # 输出报告
        print("\n" + "="*60)
        print(report)
        print("="*60)

        # 输出交互指南
        analyzer.print_claude_instructions()

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()