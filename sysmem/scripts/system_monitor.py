#!/usr/bin/env python3
"""
系统监控器 - 定期检查项目架构健康状态
提供自动化质量监控和预警机制
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collect_data import ProjectDataCollector
from analyze_architecture import ArchitectureAnalyzer
from utils import SysmemUtils

class SystemMonitor:
    """系统架构健康监控器"""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.monitor_log_path = self.root_path / ".claude" / "skill" / "sysmem" / "monitor_log.json"

    def run_health_check(self) -> Dict[str, Any]:
        """执行完整的系统健康检查"""
        print("🔍 开始系统健康检查...")

        # 数据收集
        collector = ProjectDataCollector(str(self.root_path))
        project_data = collector.collect_all_data()

        # 架构分析
        analyzer = ArchitectureAnalyzer(str(self.root_path))
        analysis_results = {"issues": []}  # 简化分析，专注于基础监控

        # 生成健康报告
        health_report = self._generate_health_report(project_data, analysis_results)

        # 保存监控日志
        self._save_monitor_log(health_report)

        print("✅ 系统健康检查完成")
        return health_report

    def _generate_health_report(self, project_data: Dict, analysis_results: Dict) -> Dict[str, Any]:
        """生成健康报告"""
        report = {
            "check_time": SysmemUtils.get_current_time(),
            "project_root": str(self.root_path),
            "health_score": 0,
            "issues": [],
            "metrics": {},
            "recommendations": []
        }

        # 计算健康分数
        health_score = 100

        # 检查CLAUDE.md存在性
        if not project_data["claude_md_info"]["exists"]:
            health_score -= 20
            report["issues"].append({
                "type": "missing_claude_md",
                "severity": "high",
                "description": "缺少CLAUDE.md文件",
                "recommendation": "创建CLAUDE.md文件定义项目架构"
            })

        # 检查重复函数
        duplicate_functions = len(project_data["architecture_analysis"]["duplicate_functions"])
        if duplicate_functions > 0:
            health_score -= duplicate_functions * 5
            report["issues"].append({
                "type": "duplicate_functions",
                "severity": "medium",
                "description": f"发现{duplicate_functions}个重复函数",
                "recommendation": "重构公共函数到utils.py"
            })

        # 检查未记录文件
        untracked_files = len(project_data["untracked_files"])
        if untracked_files > 0:
            health_score -= untracked_files * 3
            report["issues"].append({
                "type": "untracked_files",
                "severity": "low",
                "description": f"发现{untracked_files}个未记录文件",
                "recommendation": "更新模块README文件记录所有文件"
            })

        # 检查文档覆盖率
        total_modules = len(project_data["modules"])
        modules_with_readme = sum(1 for module in project_data["modules"].values()
                                if module.get("readme_file"))
        doc_coverage = (modules_with_readme / total_modules * 100) if total_modules > 0 else 0

        if doc_coverage < 100:
            health_score -= (100 - doc_coverage) * 0.5
            report["issues"].append({
                "type": "incomplete_documentation",
                "severity": "medium",
                "description": f"文档覆盖率: {doc_coverage:.1f}%",
                "recommendation": "为所有模块创建README文件"
            })

        report["health_score"] = max(0, health_score)

        # 设置指标
        report["metrics"] = {
            "doc_coverage": doc_coverage,
            "duplicate_functions": duplicate_functions,
            "untracked_files": untracked_files,
            "total_modules": total_modules,
            "architecture_issues": len(analysis_results.get("issues", []))
        }

        # 生成建议
        report["recommendations"] = self._generate_recommendations(report)

        return report

    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if report["health_score"] < 60:
            recommendations.append("🚨 项目架构健康状况较差，需要立即优化")
        elif report["health_score"] < 80:
            recommendations.append("⚠️ 项目架构存在一些问题，建议逐步改进")
        else:
            recommendations.append("✅ 项目架构健康状况良好")

        # 基于具体问题生成建议
        for issue in report["issues"]:
            if issue["type"] == "missing_claude_md":
                recommendations.append("📝 创建CLAUDE.md文件，定义项目架构和开发规范")
            elif issue["type"] == "duplicate_functions":
                recommendations.append("🔧 重构重复函数，使用公共工具类提高代码质量")
            elif issue["type"] == "untracked_files":
                recommendations.append("📋 更新模块README，记录所有文件的功能说明")
            elif issue["type"] == "incomplete_documentation":
                recommendations.append("📚 完善文档覆盖率，确保所有模块都有README")

        return recommendations

    def _save_monitor_log(self, report: Dict[str, Any]) -> None:
        """保存监控日志"""
        # 确保目录存在
        log_dir = self.monitor_log_path.parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # 读取现有日志
        logs = []
        if self.monitor_log_path.exists():
            try:
                with open(self.monitor_log_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []

        # 添加新报告
        logs.append(report)

        # 只保留最近30天的记录
        cutoff_date = datetime.now() - timedelta(days=30)
        logs = [log for log in logs
                if datetime.strptime(log["check_time"], "%Y-%m-%d %H:%M:%S") > cutoff_date]

        # 保存日志
        SysmemUtils.export_json_data(logs, self.monitor_log_path)

        print(f"📊 监控日志已保存: {self.monitor_log_path}")

    def get_health_trend(self) -> Dict[str, Any]:
        """获取健康趋势分析"""
        if not self.monitor_log_path.exists():
            return {"trend": "no_data", "message": "暂无监控数据"}

        try:
            with open(self.monitor_log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            return {"trend": "error", "message": "无法读取监控日志"}

        if len(logs) < 2:
            return {"trend": "insufficient_data", "message": "数据不足，需要更多监控记录"}

        # 分析趋势
        recent_scores = [log["health_score"] for log in logs[-7:]]  # 最近7次
        previous_scores = [log["health_score"] for log in logs[-14:-7]] if len(logs) >= 14 else []

        if not previous_scores:
            return {
                "trend": "stable",
                "current_score": recent_scores[-1],
                "message": f"当前健康分数: {recent_scores[-1]}"
            }

        recent_avg = sum(recent_scores) / len(recent_scores)
        previous_avg = sum(previous_scores) / len(previous_scores)

        if recent_avg > previous_avg + 5:
            trend = "improving"
            message = f"架构健康状况正在改善 (+{recent_avg - previous_avg:.1f})"
        elif recent_avg < previous_avg - 5:
            trend = "declining"
            message = f"架构健康状况正在下降 ({recent_avg - previous_avg:.1f})"
        else:
            trend = "stable"
            message = f"架构健康状况保持稳定"

        return {
            "trend": trend,
            "current_score": recent_scores[-1],
            "recent_average": recent_avg,
            "previous_average": previous_avg,
            "message": message
        }

    def generate_improvement_plan(self, health_report: Dict[str, Any]) -> Dict[str, Any]:
        """生成改进计划（需要用户批准执行）"""
        print("\n📋 生成项目架构改进计划...")

        plan = {
            "priority_issues": [],
            "recommended_actions": [],
            "estimated_effort": {},
            "user_approval_required": True
        }

        # 基于健康报告生成优先级问题
        for issue in health_report.get("issues", []):
            priority = self._assess_issue_priority(issue)
            plan["priority_issues"].append({
                "issue": issue,
                "priority": priority,
                "suggested_fix": self._suggest_fix_for_issue(issue)
            })

        # 生成推荐行动
        plan["recommended_actions"] = self._generate_recommended_actions(health_report)

        # 估算工作量
        plan["estimated_effort"] = self._estimate_improvement_effort(plan)

        return plan

    def _assess_issue_priority(self, issue: Dict[str, Any]) -> str:
        """评估问题优先级"""
        severity = issue.get("severity", "low")
        if severity == "high":
            return "critical"
        elif severity == "medium":
            return "high"
        else:
            return "medium"

    def _suggest_fix_for_issue(self, issue: Dict[str, Any]) -> str:
        """为问题建议修复方案"""
        issue_type = issue.get("type", "")
        if issue_type == "missing_claude_md":
            return "创建CLAUDE.md文件，定义项目架构和开发规范"
        elif issue_type == "duplicate_functions":
            return "重构重复函数，使用公共工具类提高代码质量"
        elif issue_type == "untracked_files":
            return "更新模块README，记录所有文件的功能说明"
        elif issue_type == "incomplete_documentation":
            return "完善文档覆盖率，确保所有模块都有README"
        else:
            return "需要进一步分析具体问题"

    def _generate_recommended_actions(self, health_report: Dict[str, Any]) -> List[str]:
        """生成推荐行动"""
        actions = []

        if health_report.get("health_score", 100) < 70:
            actions.append("立即处理高优先级问题")
            actions.append("建立定期架构审查机制")

        if health_report.get("metrics", {}).get("doc_coverage", 100) < 100:
            actions.append("完善项目文档，确保100%覆盖率")

        duplicate_count = health_report.get("metrics", {}).get("duplicate_functions", 0)
        if duplicate_count > 0:
            actions.append(f"重构{duplicate_count}个重复函数")

        actions.append("建立自动化测试流程")
        actions.append("定期运行架构健康检查")

        return actions

    def _estimate_improvement_effort(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """估算改进工作量"""
        effort = {
            "total_time": "medium",
            "breakdown": {}
        }

        # 基于问题数量和复杂性估算
        issue_count = len(plan.get("priority_issues", []))
        if issue_count <= 2:
            effort["total_time"] = "low (1-2 days)"
        elif issue_count <= 5:
            effort["total_time"] = "medium (3-5 days)"
        else:
            effort["total_time"] = "high (1-2 weeks)"

        effort["breakdown"] = {
            "analysis": "10%",
            "planning": "20%",
            "implementation": "60%",
            "testing": "10%"
        }

        return effort

if __name__ == "__main__":
    import sys

    target_directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    monitor = SystemMonitor(target_directory)

    if len(sys.argv) > 2 and sys.argv[2] == "--trend":
        # 显示趋势分析
        trend = monitor.get_health_trend()
        print(f"📈 健康趋势: {trend['message']}")
    else:
        # 执行健康检查
        report = monitor.run_health_check()

        print(f"\n🏥 系统健康报告:")
        print(f"健康分数: {report['health_score']}/100")
        print(f"发现问题: {len(report['issues'])} 个")

        if report['issues']:
            print("\n🚨 主要问题:")
            for issue in report['issues'][:3]:  # 显示前3个问题
                print(f"- {issue['description']} ({issue['severity']})")

        print(f"\n💡 改进建议:")
        for rec in report['recommendations']:
            print(f"- {rec}")