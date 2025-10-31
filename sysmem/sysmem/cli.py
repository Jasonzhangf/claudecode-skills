#!/usr/bin/env python3
"""
Sysmem CLI - 命令行界面
提供统一的命令行接口来访问所有Sysmem功能
"""

import click
import sys
import os
from pathlib import Path
import json

# 确保可以导入scripts模块
script_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_dir))

try:
    from collect_data import ProjectDataCollector
    from scan_project import ProjectScanner
    from analyze_architecture import ArchitectureAnalyzer
    from update_claude_md import ClaudeMdUpdater
    from system_monitor import SystemMonitor
    from utils import SysmemUtils
except ImportError as e:
    click.echo(f"❌ 导入模块失败: {e}", err=True)
    click.echo("请确保在正确的项目目录中运行此命令", err=True)
    sys.exit(1)


@click.group()
@click.version_option(version="2.0.0", prog_name="Sysmem")
@click.pass_context
def cli(ctx):
    """
    Sysmem - 项目架构链条化管理系统

    自动化项目架构管理工具，提供智能项目扫描、数据驱动分析、
    自动文档管理和架构健康监控功能。
    """
    ctx.ensure_object(dict)


@cli.command()
@click.argument('directory', default='.')
@click.option('--smart', is_flag=True, help='智能增量收集（推荐）')
@click.option('--force', is_flag=True, help='强制全量收集')
@click.option('--check', is_flag=True, help='检查项目变更状态')
@click.option('--stats', is_flag=True, help='显示收集统计信息')
@click.option('--non-interactive', is_flag=True, help='非交互模式')
def collect(directory, smart, force, check, stats, non_interactive):
    """收集项目数据"""
    try:
        # 导入增量收集器
        from incremental_collector import IncrementalCollector

        collector = IncrementalCollector(directory)

        if stats:
            # 显示统计信息
            stats_data = collector.get_collection_stats()
            click.echo("📊 数据收集统计:")
            for key, value in stats_data.items():
                click.echo(f"  {key}: {value}")

        elif check:
            # 检查变更状态
            from change_detector import ChangeDetector
            detector = ChangeDetector()
            should_collect, conditions, level = detector.should_collect(directory)
            click.echo(detector.format_change_report(should_collect, conditions, level))

        elif smart or not force:
            # 智能增量收集（默认）
            click.echo("🤖 使用智能增量收集...")
            data = collector.smart_collect(
                force=force,
                interactive=not non_interactive
            )

            if data:
                click.echo(f"✅ 数据收集完成！")
                click.echo(f"  - 模块数量: {len(data.get('modules', {}))}")
                click.echo(f"  - CLAUDE.md存在: {'是' if data.get('claude_md_info', {}).get('exists') else '否'}")

        else:
            # 直接调用原始收集器
            collector = ProjectDataCollector(directory)
            data = collector.collect_all_data()
            output_file = collector.export_data(data)
            click.echo(f"✅ 数据收集完成！输出文件: {output_file}")

    except Exception as e:
        click.echo(f"❌ 数据收集失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', default='.')
@click.option('--output', '-o', help='输出文件路径')
def scan(directory, output):
    """扫描项目结构"""
    try:
        scanner = ProjectScanner(directory)
        structure = scanner.scan_project()

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(structure, f, indent=2, ensure_ascii=False)
            click.echo(f"✅ 项目结构已保存到: {output}")
        else:
            click.echo(json.dumps(structure, indent=2, ensure_ascii=False))

    except Exception as e:
        click.echo(f"❌ 项目扫描失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', default='.')
@click.option('--output', '-o', help='分析报告输出路径')
def analyze(directory, output):
    """分析项目架构"""
    try:
        analyzer = ArchitectureAnalyzer(directory)
        report = analyzer.analyze()

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            click.echo(f"✅ 架构分析报告已保存到: {output}")
        else:
            click.echo("📊 架构分析报告:")
            click.echo(json.dumps(report, indent=2, ensure_ascii=False))

    except Exception as e:
        click.echo(f"❌ 架构分析失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', default='.')
@click.option('--dry-run', is_flag=True, help='预览模式，不实际修改文件')
def update(directory, dry_run):
    """更新CLAUDE.md文档"""
    try:
        updater = ClaudeMdUpdater(directory)

        if dry_run:
            changes = updater.preview_changes()
            click.echo("📋 预览将要进行的更改:")
            click.echo(json.dumps(changes, indent=2, ensure_ascii=False))
        else:
            success = updater.update_claude_md()
            if success:
                click.echo("✅ CLAUDE.md更新完成")
            else:
                click.echo("⚠️ CLAUDE.md更新失败或无需更新")

    except Exception as e:
        click.echo(f"❌ 文档更新失败: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', default='.')
@click.option('--watch', is_flag=True, help='持续监控模式')
def monitor(directory, watch):
    """监控系统架构健康"""
    try:
        monitor = SystemMonitor(directory)

        if watch:
            click.echo("🔍 开始持续监控...")
            monitor.start_monitoring()
        else:
            report = monitor.generate_health_report()
            click.echo("📊 系统健康报告:")
            click.echo(json.dumps(report, indent=2, ensure_ascii=False))

    except Exception as e:
        click.echo(f"❌ 系统监控失败: {e}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """显示版本信息"""
    click.echo("Sysmem v2.0.0")
    click.echo("项目架构链条化管理系统")
    click.echo("Copyright (c) 2024 Sysmem Team")


@cli.command()
@click.argument('directory', default='.')
@click.option('--modules', nargs='+', help='指定要分析的模块')
@click.option('--output', '-o', help='输出报告文件路径')
@click.option('--ai-prompt', action='store_true', help='生成AI分析提示')
@click.option('--confidence', type=float, default=0.6, help='置信度阈值')
@click.option('--max-results', type=int, default=20, help='最大结果数量')
def analyze_unused(directory, modules, output, ai_prompt, confidence, max_results):
    """分析未使用的代码"""
    try:
        # 导入未使用代码分析器
        sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
        from unused_code_analyzer import UnusedCodeAnalyzer

        analyzer = UnusedCodeAnalyzer(directory)

        click.echo("🚀 开始未使用代码分析...")
        report = analyzer.scan_project(modules)

        # 过滤结果
        filtered_unused = [
            func for func in report["unused_functions"]
            if func["confidence"] >= confidence
        ][:max_results]

        report["unused_functions"] = filtered_unused
        report["filtered_count"] = len(filtered_unused)

        # 导出报告
        output_file = analyzer.export_report(report, output)

        # 生成AI提示
        if ai_prompt:
            ai_prompt_text = analyzer.format_for_ai_analysis(report)

            prompt_file = Path(output_file).with_suffix('.prompt.md')
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(ai_prompt_text)

            click.echo(f"🤖 AI分析提示已保存到: {prompt_file}")

            # 显示简要信息
            click.echo("\n" + "="*50)
            click.echo("📊 分析结果摘要")
            click.echo("="*50)
            click.echo(f"发现 {len(filtered_unused)} 个高置信度未使用的函数")
            click.echo(f"AI分析提示已生成，可提交给AI进行深度分析")
            click.echo("="*50)
        else:
            click.echo(f"\n📊 分析完成，发现 {len(filtered_unused)} 个未使用的函数")
            click.echo(f"详细报告: {output_file}")

    except Exception as e:
        click.echo(f"❌ 未使用代码分析失败: {e}", err=True)
        sys.exit(1)


@cli.command()
def status():
    """显示系统状态"""
    try:
        # 检查各个组件的状态
        current_dir = Path.cwd()

        click.echo("🔍 Sysmem系统状态检查")
        click.echo("=" * 40)

        # 检查项目数据
        data_file = current_dir / ".claude" / "skill" / "sysmem" / "project_data.json"
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            click.echo(f"✅ 项目数据存在: {len(data.get('modules', {}))} 个模块")
        else:
            click.echo("❌ 项目数据不存在")

        # 检查CLAUDE.md
        claude_md = current_dir / "CLAUDE.md"
        if claude_md.exists():
            click.echo("✅ CLAUDE.md文档存在")
        else:
            click.echo("❌ CLAUDE.md文档不存在")

        # 检查指纹
        fingerprint_file = current_dir / ".claude" / "skill" / "sysmem" / ".fingerprint.json"
        if fingerprint_file.exists():
            click.echo("✅ 项目指纹存在")
        else:
            click.echo("❌ 项目指纹不存在")

    except Exception as e:
        click.echo(f"❌ 状态检查失败: {e}", err=True)


def main():
    """主入口函数"""
    cli()


if __name__ == '__main__':
    main()