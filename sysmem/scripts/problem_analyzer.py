#!/usr/bin/env python3
"""
问题分析器 - 交互式问题分析和解决系统
基于项目架构定义进行问题定位、分析和解决方案实施
"""

import os
import re
import json
import subprocess
import signal
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from utils import SysmemUtils

class ProblemType(Enum):
    """问题类型枚举"""
    PERFORMANCE = "performance"
    FUNCTIONAL = "functional"
    ARCHITECTURE = "architecture"
    CONFIGURATION = "configuration"
    LOGGING = "logging"
    UNKNOWN = "unknown"

@dataclass
class ProblemContext:
    """问题上下文"""
    user_query: str
    problem_type: ProblemType
    related_modules: List[str]
    relevant_logs: List[str]
    code_analysis: Dict[str, Any]
    architecture_constraints: Dict[str, Any]
    potential_solutions: List[Dict[str, Any]]

class ProblemAnalyzer:
    """交互式问题分析器"""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.claude_md_path = self.root_path / "CLAUDE.md"
        self.project_data_path = self.root_path / ".claude" / "skill" / "sysmem" / "project_data.json"
        self.analysis_log = []

    def analyze_problem(self, user_query: str) -> Dict[str, Any]:
        """主问题分析流程 - 交互式引导"""
        print(f"🔍 开始问题分析流程")
        print(f"用户问题: {user_query}")

        # 初始化分析上下文
        context = None
        evidence = None
        solution_options = None
        selected_option = None

        try:
            # 步骤1: 问题意图分析和模块关联
            print(f"\n{'='*60}")
            print(f"📋 步骤 1/6: 问题意图分析")
            print(f"{'='*60}")

            context = self._analyze_problem_intent(user_query)
            if not context:
                return {"status": "failed", "message": "问题意图分析失败"}

            # 步骤2: 日志分析
            print(f"\n{'='*60}")
            print(f"📋 步骤 2/6: 日志分析")
            print(f"{'='*60}")

            self._analyze_relevant_logs(context)

            # 步骤3: 问题定位和原因分析
            print(f"\n{'='*60}")
            print(f"📋 步骤 3/6: 问题定位和原因分析")
            print(f"{'='*60}")

            self._locate_problem_source(context)

            # 步骤4: 证据收集和分析
            print(f"\n{'='*60}")
            print(f"📋 步骤 4/6: 证据收集和分析")
            print(f"{'='*60}")

            evidence = self._collect_evidence(context)

            # 步骤5: 架构约束分析
            print(f"\n{'='*60}")
            print(f"📋 步骤 5/6: 架构约束分析")
            print(f"{'='*60}")

            self._validate_architecture_constraints(context)

            # 步骤6: 多方案生成和利弊分析
            print(f"\n{'='*60}")
            print(f"📋 步骤 6/6: 解决方案选项分析")
            print(f"{'='*60}")

            solution_options = self._generate_solution_options(context, evidence)

            # 交互式选择和指导
            selected_option = self._interactive_solution_selection(solution_options, evidence, context)

            return {
                "status": "analysis_completed",
                "selected_option": selected_option,
                "context": context,
                "evidence": evidence,
                "analysis_summary": self._generate_analysis_summary(context, evidence, selected_option)
            }

        except KeyboardInterrupt:
            return {"status": "interrupted", "message": "用户中断分析"}
        except Exception as e:
            return {"status": "error", "message": f"分析过程出错: {str(e)}"}

    def _interactive_solution_selection(self, options: List[Dict[str, Any]], evidence: Dict[str, Any], context: ProblemContext) -> Optional[Dict[str, Any]]:
        """交互式解决方案选择流程"""
        print(f"\n🎯 交互式解决方案选择流程")

        # 显示问题分析摘要
        print(f"\n📊 问题分析摘要:")
        print(f"- 问题类型: {context.problem_type.value}")
        print(f"- 关联模块: {', '.join(context.related_modules) if context.related_modules else '无'}")
        print(f"- 证据总数: {evidence.get('total_evidence', 0)} 项")
        print(f"- 高置信度证据: {evidence.get('high_confidence', 0)} 项")
        print(f"- 相关文件: {len(evidence.get('supporting_files', []))} 个")

        # 显示证据详情
        print(f"\n🔍 证据详情:")
        self._display_evidence_summary(evidence)

        # 显示解决方案选项
        print(f"\n💡 解决方案选项:")
        for i, option in enumerate(options, 1):
            print(f"\n{'='*60}")
            print(f"选项 {i}: {option['title']}")
            print(f"描述: {option['description']}")
            print(f"方法: {option['approach']}")
            print(f"工作量: {option['effort']}")
            print(f"风险等级: {option['risk']}")
            print(f"影响模块: {', '.join(option['affected_modules'])}")

            print(f"\n✅ 优势:")
            for pro in option['pros']:
                print(f"  • {pro}")

            print(f"\n❌ 劣势:")
            for con in option['cons']:
                print(f"  • {con}")

            print(f"\n📋 实施步骤概览:")
            for j, step in enumerate(option['steps'][:3], 1):
                print(f"  {j}. {step}")
            if len(option['steps']) > 3:
                print(f"  ... 共{len(option['steps'])}个步骤")

        # 用户交互选择
        while True:
            try:
                print(f"\n{'='*60}")
                choice = input(f"\n请选择操作:\n1. 选择解决方案选项 (1-{len(options)})\n2. 查看详细证据信息\n3. 查看架构约束\n4. 完成分析\n\n请输入选择 (1-4): ").strip()

                if choice == '1':
                    return self._select_solution_option(options)
                elif choice == '2':
                    self._show_detailed_evidence(evidence)
                elif choice == '3':
                    self._show_architecture_constraints(context)
                elif choice == '4':
                    return None
                else:
                    print("请输入有效选项 (1-4)")

            except ValueError:
                print("请输入有效数字")

    def _select_solution_option(self, options: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """选择具体解决方案选项"""
        while True:
            try:
                choice = input(f"\n选择解决方案选项 (1-{len(options)}) 或 'back' 返回: ").strip()

                if choice.lower() == 'back':
                    return None

                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(options):
                    selected = options[choice_idx]

                    print(f"\n✅ 已选择: {selected['title']}")
                    print(f"方法: {selected['approach']}")
                    print(f"工作量: {selected['effort']}")
                    print(f"风险等级: {selected['risk']}")

                    confirm = input("\n确认此选择? (y/n): ").strip().lower()
                    if confirm == 'y':
                        return selected

            except ValueError:
                print("请输入有效数字或 'back'")

    def _display_evidence_summary(self, evidence: Dict[str, Any]):
        """显示证据摘要"""
        print(f"- 总证据数: {evidence.get('total_evidence', 0)} 项")
        print(f"- 高置信度: {evidence.get('high_confidence', 0)} 项")
        print(f"- 中等置信度: {evidence.get('medium_confidence', 0)} 项")
        print(f"- 低置信度: {evidence.get('low_confidence', 0)} 项")
        print(f"- 相关文件: {len(evidence.get('supporting_files', []))} 个")

        if evidence.get('supporting_files'):
            print("\n📁 主要相关文件:")
            for file in evidence['supporting_files'][:5]:  # 只显示前5个
                print(f"  • {file}")
            if len(evidence['supporting_files']) > 5:
                print(f"  ... 还有{len(evidence['supporting_files'])-5}个文件")

    def _show_architecture_constraints(self, context: ProblemContext):
        """显示架构约束信息"""
        validation = context.architecture_constraints
        print(f"架构合规性: {'✅ 符合' if validation.get('compliant', False) else '❌ 可能违反'}")

        if not validation.get('compliant', True):
            print("违规项:")
            for violation in validation.get('violations', []):
                print(f"  • {violation}")

        print(f"模块定义约束:")
        for module in context.related_modules:
            module_defs = context.code_analysis.get("module_definitions", {}).get(module, {})
            ground_truth = module_defs.get("ground_truth", [])
            if ground_truth:
                print(f"  {module}: {len(ground_truth)}项定义")

    def _generate_analysis_summary(self, context: ProblemContext, evidence: Dict[str, Any], selected_option: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """生成分析摘要"""
        return {
            "problem_type": context.problem_type.value,
            "related_modules": context.related_modules,
            "evidence_summary": {
                "total": evidence.get('total_evidence', 0),
                "high_confidence": evidence.get('high_confidence', 0),
                "supporting_files": evidence.get('supporting_files', [])
            },
            "selected_option": selected_option['title'] if selected_option else None,
            "analysis_timestamp": SysmemUtils.get_current_time()
        }

    def _analyze_problem_intent(self, user_query: str) -> ProblemContext:
        """步骤1: 分析问题意图和相关模块"""
        print("\n📋 步骤1: 分析问题意图...")

        # 加载项目数据
        project_data = self._load_project_data()

        # AI分析问题类型和相关模块
        problem_type = self._classify_problem_type(user_query)
        related_modules = self._find_related_modules(user_query, project_data)

        # 读取相关模块的README
        module_definitions = {}
        for module in related_modules:
            module_readme = self.root_path / module / "README.md"
            if module_readme.exists():
                content = SysmemUtils.safe_read_file(module_readme)
                module_definitions[module] = self._extract_module_definitions(content)

        # 代码层面分析
        code_analysis = self._analyze_code_context(user_query, related_modules)

        context = ProblemContext(
            user_query=user_query,
            problem_type=problem_type,
            related_modules=related_modules,
            relevant_logs=[],
            code_analysis={
                "module_definitions": module_definitions,
                "code_context": code_analysis
            },
            architecture_constraints={},
            potential_solutions=[]
        )

        print(f"✅ 识别问题类型: {problem_type.value}")
        print(f"✅ 关联模块: {', '.join(related_modules)}")

        return context

    def _classify_problem_type(self, query: str) -> ProblemType:
        """分类问题类型"""
        query_lower = query.lower()

        if any(word in query_lower for word in ['慢', '性能', '卡', '延迟', '超时']):
            return ProblemType.PERFORMANCE
        elif any(word in query_lower for word in ['错误', '异常', '崩溃', '失败', 'bug']):
            return ProblemType.FUNCTIONAL
        elif any(word in query_lower for word in ['架构', '设计', '结构', '模式']):
            return ProblemType.ARCHITECTURE
        elif any(word in query_lower for word in ['配置', '设置', '参数', '环境']):
            return ProblemType.CONFIGURATION
        elif any(word in query_lower for word in ['日志', 'log', '记录']):
            return ProblemType.LOGGING
        else:
            return ProblemType.UNKNOWN

    def _find_related_modules(self, query: str, project_data: Dict) -> List[str]:
        """查找与问题相关的模块"""
        related_modules = []
        query_terms = query.lower().split()

        # 从项目数据中查找相关模块
        if "modules" in project_data:
            for module_path, module_info in project_data["modules"].items():
                # 检查模块功能描述
                if module_info.get("function_summary"):
                    summary = module_info["function_summary"].lower()
                    if any(term in summary for term in query_terms):
                        related_modules.append(module_path)

                # 检查文件描述
                if module_info.get("file_descriptions"):
                    for file_desc in module_info["file_descriptions"].values():
                        if any(term in file_desc.lower() for term in query_terms):
                            related_modules.append(module_path)
                            break

        return list(set(related_modules))  # 去重

    def _extract_module_definitions(self, readme_content: str) -> Dict[str, Any]:
        """提取模块定义"""
        definitions = {
            "core_functions": [],
            "ground_truth": [],
            "interfaces": [],
            "constraints": []
        }

        lines = readme_content.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()

            if "核心功能定义" in line or "core functions" in line.lower():
                current_section = "core_functions"
            elif "ground truth" in line.lower() or "重要定义" in line:
                current_section = "ground_truth"
            elif "接口定义" in line.lower() or "interface" in line.lower():
                current_section = "interfaces"
            elif line.startswith('**重要**') or line.startswith('important'):
                if current_section:
                    definitions[current_section].append(line.replace('**', '').replace('*', '').strip())

        return definitions

    def _analyze_code_context(self, query: str, modules: List[str]) -> Dict[str, Any]:
        """分析代码上下文"""
        code_context = {"files": [], "functions": [], "classes": []}

        for module in modules:
            module_path = self.root_path / module
            if not module_path.exists():
                continue

            # 扫描Python文件
            for py_file in module_path.rglob("*.py"):
                if py_file.name.startswith('.'):
                    continue

                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 提取函数和类
                    functions = re.findall(r'def\s+(\w+)\s*\(', content)
                    classes = re.findall(r'class\s+(\w+)', content)

                    code_context["files"].append(str(py_file.relative_to(self.root_path)))
                    code_context["functions"].extend(functions)
                    code_context["classes"].extend(classes)

                except:
                    continue

        return code_context

    def _analyze_relevant_logs(self, context: ProblemContext):
        """步骤2: 分析相关日志"""
        print("\n📋 步骤2: 分析相关日志...")

        # 读取CLAUDE.md中的日志信息
        claude_content = SysmemUtils.safe_read_file(self.claude_md_path)
        log_info = self._extract_log_information(claude_content)

        # 根据问题类型确定需要查看的日志
        relevant_logs = self._determine_relevant_logs(context.problem_type, log_info)
        context.relevant_logs = relevant_logs

        print(f"✅ 识别相关日志: {', '.join(relevant_logs)}")

    def _extract_log_information(self, claude_content: str) -> Dict[str, Any]:
        """从CLAUDE.md提取日志信息"""
        log_info = {
            "log_locations": [],
            "log_types": [],
            "monitoring_tools": []
        }

        lines = claude_content.split('\n')
        for line in lines:
            line_lower = line.lower()

            if 'log' in line_lower or '日志' in line_lower:
                if 'location' in line_lower or '位置' in line_lower:
                    log_info["log_locations"].append(line.strip())
                elif 'type' in line_lower or '类型' in line_lower:
                    log_info["log_types"].append(line.strip())
                elif 'monitor' in line_lower or '监控' in line_lower:
                    log_info["monitoring_tools"].append(line.strip())

        return log_info

    def _determine_relevant_logs(self, problem_type: ProblemType, log_info: Dict) -> List[str]:
        """确定相关日志"""
        relevant_logs = []

        if problem_type == ProblemType.PERFORMANCE:
            relevant_logs.extend(["performance.log", "access.log", "slow-query.log"])
        elif problem_type == ProblemType.FUNCTIONAL:
            relevant_logs.extend(["error.log", "application.log", "debug.log"])
        elif problem_type == ProblemType.ARCHITECTURE:
            relevant_logs.extend(["architecture.log", "system.log"])
        elif problem_type == ProblemType.CONFIGURATION:
            relevant_logs.extend(["config.log", "startup.log"])
        else:
            relevant_logs.extend(["application.log", "system.log"])

        # 添加从CLAUDE.md中提取的日志位置
        relevant_logs.extend(log_info.get("log_locations", []))

        return list(set(relevant_logs))

    def _locate_problem_source(self, context: ProblemContext):
        """步骤3: 问题定位和原因分析"""
        print("\n📋 步骤3: 问题定位和原因分析...")

        # 基于已有信息进行问题发生点定位
        location_analysis = self._perform_problem_location(context)

        # 深入分析问题原因
        root_cause_analysis = self._analyze_root_causes(context, location_analysis)

        # 记录分析结果
        context.code_analysis["problem_location"] = location_analysis
        context.code_analysis["root_cause_analysis"] = root_cause_analysis

        print(f"✅ 问题定位: {location_analysis.get('location', '未确定')}")
        print(f"✅ 根本原因分析: {root_cause_analysis.get('primary_cause', '待进一步分析')}")
        print(f"✅ 支持证据: {len(root_cause_analysis.get('evidence', []))} 项")

    def _analyze_root_causes(self, context: ProblemContext, location_analysis: Dict) -> Dict[str, Any]:
        """深入分析问题根本原因"""
        analysis = {
            "primary_cause": "unknown",
            "contributing_factors": [],
            "evidence": [],
            "confidence": 0.0
        }

        # 基于问题类型分析原因
        if context.problem_type == ProblemType.PERFORMANCE:
            analysis["primary_cause"] = "性能瓶颈"
            analysis["contributing_factors"] = [
                "算法复杂度过高",
                "资源使用不当",
                "IO阻塞",
                "内存泄漏"
            ]
            analysis["evidence"] = self._collect_performance_evidence(context)

        elif context.problem_type == ProblemType.FUNCTIONAL:
            analysis["primary_cause"] = "功能逻辑错误"
            analysis["contributing_factors"] = [
                "边界条件处理不当",
                "输入验证不足",
                "状态管理错误",
                "依赖关系问题"
            ]
            analysis["evidence"] = self._collect_functional_evidence(context)

        elif context.problem_type == ProblemType.CONFIGURATION:
            analysis["primary_cause"] = "配置错误"
            analysis["contributing_factors"] = [
                "环境配置不匹配",
                "参数设置错误",
                "依赖版本冲突",
                "权限配置问题"
            ]
            analysis["evidence"] = self._collect_config_evidence(context)

        # 计算置信度
        evidence_count = len(analysis["evidence"])
        if evidence_count >= 3:
            analysis["confidence"] = 0.8
        elif evidence_count >= 2:
            analysis["confidence"] = 0.6
        elif evidence_count >= 1:
            analysis["confidence"] = 0.4
        else:
            analysis["confidence"] = 0.2

        return analysis

    def _collect_performance_evidence(self, context: ProblemContext) -> List[Dict[str, Any]]:
        """收集性能问题证据"""
        evidence = []

        # 检查模块中的性能相关代码
        for module in context.related_modules:
            module_path = self.root_path / module
            if not module_path.exists():
                continue

            for py_file in module_path.rglob("*.py"):
                if py_file.name.startswith('.'):
                    continue

                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 查找性能问题模式
                    if "for.*in.*range(" in content and len(content) > 1000:
                        evidence.append({
                            "type": "potential_inefficient_loop",
                            "file": str(py_file.relative_to(self.root_path)),
                            "description": "可能存在低效循环",
                            "confidence": 0.6
                        })

                    if "while.*True:" in content:
                        evidence.append({
                            "type": "infinite_loop_risk",
                            "file": str(py_file.relative_to(self.root_path)),
                            "description": "可能存在无限循环风险",
                            "confidence": 0.7
                        })

                except:
                    continue

        return evidence

    def _collect_functional_evidence(self, context: ProblemContext) -> List[Dict[str, Any]]:
        """收集功能问题证据"""
        evidence = []

        # 检查函数定义和异常处理
        for module in context.related_modules:
            module_path = self.root_path / module
            if not module_path.exists():
                continue

            for py_file in module_path.rglob("*.py"):
                if py_file.name.startswith('.'):
                    continue

                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 检查异常处理
                    function_count = content.count("def ")
                    exception_count = content.count("except")

                    if function_count > 0 and exception_count == 0:
                        evidence.append({
                            "type": "missing_exception_handling",
                            "file": str(py_file.relative_to(self.root_path)),
                            "description": f"缺少异常处理（{function_count}个函数，0个异常处理）",
                            "confidence": 0.8
                        })

                    # 检查输入验证
                    if "def " in content and "if not" not in content:
                        evidence.append({
                            "type": "potential_input_validation_issue",
                            "file": str(py_file.relative_to(self.root_path)),
                            "description": "可能缺少输入验证",
                            "confidence": 0.5
                        })

                except:
                    continue

        return evidence

    def _collect_config_evidence(self, context: ProblemContext) -> List[Dict[str, Any]]:
        """收集配置问题证据"""
        evidence = []

        # 检查配置文件
        config_files = [
            ".env", "config.json", "settings.py", "requirements.txt",
            "package.json", "docker-compose.yml", "Dockerfile"
        ]

        for config_file in config_files:
            config_path = self.root_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if len(content.strip()) == 0:
                        evidence.append({
                            "type": "empty_config_file",
                            "file": config_file,
                            "description": "配置文件为空",
                            "confidence": 0.9
                        })

                    if config_file.endswith('.json') and "error" in content.lower():
                        evidence.append({
                            "type": "config_error_indicators",
                            "file": config_file,
                            "description": "配置文件中包含错误指示",
                            "confidence": 0.7
                        })

                except:
                    evidence.append({
                        "type": "config_file_access_error",
                        "file": config_file,
                        "description": "无法读取配置文件",
                        "confidence": 0.6
                    })
            else:
                evidence.append({
                    "type": "missing_config_file",
                    "file": config_file,
                    "description": "缺少常见配置文件",
                    "confidence": 0.4
                })

        return evidence

    def _perform_problem_location(self, context: ProblemContext) -> Dict[str, Any]:
        """执行问题定位"""
        location = {
            "location": "unknown",
            "possible_causes": [],
            "confidence": 0.0
        }

        # 基于问题类型和模块信息进行定位
        if context.problem_type == ProblemType.FUNCTIONAL:
            location["location"] = "function_error"
            location["possible_causes"] = ["函数逻辑错误", "参数错误", "依赖问题"]
            location["confidence"] = 0.7
        elif context.problem_type == ProblemType.PERFORMANCE:
            location["location"] = "performance_bottleneck"
            location["possible_causes"] = ["算法复杂度", "资源竞争", "IO阻塞"]
            location["confidence"] = 0.6

        return location

    def _collect_evidence(self, context: ProblemContext) -> Dict[str, Any]:
        """步骤4: 证据收集和分析"""
        print("\n📋 步骤4: 证据收集和分析...")

        evidence_summary = {
            "total_evidence": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "evidence_by_type": {},
            "supporting_files": []
        }

        root_cause_analysis = context.code_analysis.get("root_cause_analysis", {})
        evidence_list = root_cause_analysis.get("evidence", [])

        # 统计证据
        for evidence in evidence_list:
            evidence_summary["total_evidence"] += 1
            confidence = evidence.get("confidence", 0.0)

            if confidence >= 0.7:
                evidence_summary["high_confidence"] += 1
            elif confidence >= 0.5:
                evidence_summary["medium_confidence"] += 1
            else:
                evidence_summary["low_confidence"] += 1

            # 按类型分组
            evidence_type = evidence.get("type", "unknown")
            if evidence_type not in evidence_summary["evidence_by_type"]:
                evidence_summary["evidence_by_type"][evidence_type] = []
            evidence_summary["evidence_by_type"][evidence_type].append(evidence)

            # 记录相关文件
            if "file" in evidence:
                evidence_summary["supporting_files"].append(evidence["file"])

        evidence_summary["supporting_files"] = list(set(evidence_summary["supporting_files"]))

        print(f"✅ 收集证据: {evidence_summary['total_evidence']} 项")
        print(f"✅ 高置信度: {evidence_summary['high_confidence']} 项")
        print(f"✅ 相关文件: {len(evidence_summary['supporting_files'])} 个")

        return evidence_summary

    def _validate_architecture_constraints(self, context: ProblemContext):
        """步骤4: 架构验证"""
        print("\n📋 步骤4: 架构验证...")

        # 读取CLAUDE.md中的架构定义
        claude_content = SysmemUtils.safe_read_file(self.claude_md_path)
        architecture_rules = self._extract_architecture_rules(claude_content)

        # 验证当前问题是否符合架构约束
        validation_result = self._validate_against_rules(context, architecture_rules)
        context.architecture_constraints = validation_result

        print(f"✅ 架构验证完成: {validation_result.get('compliant', '未知')}")

    def _extract_architecture_rules(self, claude_content: str) -> Dict[str, Any]:
        """提取架构规则"""
        rules = {
            "module_principles": [],
            "interface_constraints": [],
            "data_flow_rules": []
        }

        lines = claude_content.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['原则', 'principle', '规则', 'rule']):
                rules["module_principles"].append(line.strip())
            elif any(keyword in line.lower() for keyword in ['接口', 'interface', '约束', 'constraint']):
                rules["interface_constraints"].append(line.strip())

        return rules

    def _validate_against_rules(self, context: ProblemContext, rules: Dict) -> Dict[str, Any]:
        """验证是否符合架构规则"""
        validation = {
            "compliant": True,
            "violations": [],
            "recommendations": []
        }

        # 简化验证逻辑
        for rule in rules.get("module_principles", []):
            if "低耦合" in rule and len(context.related_modules) > 3:
                validation["violations"].append("可能违反模块低耦合原则")
                validation["compliant"] = False

        return validation

    def _generate_solution_options(self, context: ProblemContext, evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """步骤6: 多方案生成和利弊分析"""
        print("\n📋 步骤6: 多方案生成和利弊分析...")

        options = []

        # 基于问题类型生成多个解决方案选项
        if context.problem_type == ProblemType.FUNCTIONAL:
            options.extend([
                {
                    "id": 1,
                    "title": "快速修复方案",
                    "description": "针对具体问题的直接修复",
                    "approach": "targeted_fix",
                    "pros": [
                        "修复速度快，见效明显",
                        "风险较低，影响范围小",
                        "易于测试和验证"
                    ],
                    "cons": [
                        "可能只是表面修复，根本问题未解决",
                        "可能在未来再次出现类似问题",
                        "不考虑整体架构一致性"
                    ],
                    "effort": "low",
                    "risk": "low",
                    "affected_modules": context.related_modules[:1],
                    "evidence_support": evidence.get("high_confidence", 0),
                    "steps": [
                        "定位具体错误位置",
                        "修复错误逻辑",
                        "添加必要的异常处理",
                        "进行功能测试"
                    ]
                },
                {
                    "id": 2,
                    "title": "架构优化方案",
                    "description": "从根本上优化相关模块的架构设计",
                    "approach": "architectural_improvement",
                    "pros": [
                        "从根本上解决问题，避免复发",
                        "提高代码质量和可维护性",
                        "符合项目架构最佳实践"
                    ],
                    "cons": [
                        "需要更多时间和精力",
                        "影响范围较大，可能影响其他功能",
                        "需要更全面的测试"
                    ],
                    "effort": "high",
                    "risk": "medium",
                    "affected_modules": context.related_modules,
                    "evidence_support": evidence.get("medium_confidence", 0),
                    "steps": [
                        "重新设计相关模块架构",
                        "重构核心功能",
                        "完善错误处理机制",
                        "更新相关文档",
                        "进行全面测试"
                    ]
                },
                {
                    "id": 3,
                    "title": "配置调整方案",
                    "description": "通过调整配置参数解决问题",
                    "approach": "configuration_tuning",
                    "pros": [
                        "无需修改代码，风险最低",
                        "可以快速部署和回滚",
                        "易于监控和调整"
                    ],
                    "cons": [
                        "可能只适用于特定场景",
                        "配置复杂度可能增加",
                        "可能影响系统其他部分"
                    ],
                    "effort": "medium",
                    "risk": "low",
                    "affected_modules": ["config"],
                    "evidence_support": evidence.get("low_confidence", 0),
                    "steps": [
                        "分析当前配置问题",
                        "调整相关配置参数",
                        "更新配置文档",
                        "测试配置效果",
                        "监控系统表现"
                    ]
                }
            ])

        elif context.problem_type == ProblemType.PERFORMANCE:
            options.extend([
                {
                    "id": 1,
                    "title": "算法优化方案",
                    "description": "优化算法和数据结构提升性能",
                    "approach": "algorithm_optimization",
                    "pros": [
                        "从根本上提升性能",
                        "长期效益明显",
                        "提高代码质量"
                    ],
                    "cons": [
                        "需要深入理解业务逻辑",
                        "可能改变API接口",
                        "需要大量测试"
                    ],
                    "effort": "high",
                    "risk": "medium",
                    "affected_modules": context.related_modules,
                    "evidence_support": evidence.get("high_confidence", 0),
                    "steps": [
                        "分析性能瓶颈",
                        "优化算法复杂度",
                        "改进数据结构",
                        "添加缓存机制",
                        "性能测试验证"
                    ]
                },
                {
                    "id": 2,
                    "title": "资源优化方案",
                    "description": "优化资源使用和配置",
                    "approach": "resource_optimization",
                    "pros": [
                        "实施相对简单",
                        "效果立竿见影",
                        "风险较低"
                    ],
                    "cons": [
                        "性能提升有限",
                        "可能只是临时解决方案",
                        "资源成本可能增加"
                    ],
                    "effort": "medium",
                    "risk": "low",
                    "affected_modules": context.related_modules,
                    "evidence_support": evidence.get("medium_confidence", 0),
                    "steps": [
                        "分析资源使用情况",
                        "调整内存和CPU配置",
                        "优化数据库查询",
                        "添加负载均衡",
                        "监控性能指标"
                    ]
                }
            ])

        elif context.problem_type == ProblemType.CONFIGURATION:
            options.extend([
                {
                    "id": 1,
                    "title": "环境配置修复",
                    "description": "修复环境配置和依赖问题",
                    "approach": "environment_fix",
                    "pros": [
                        "解决根本环境问题",
                        "确保部署一致性",
                        "提高系统稳定性"
                    ],
                    "cons": [
                        "可能需要重启服务",
                        "影响范围较广",
                        "需要环境管理权限"
                    ],
                    "effort": "medium",
                    "risk": "medium",
                    "affected_modules": ["deployment", "config"],
                    "evidence_support": evidence.get("high_confidence", 0),
                    "steps": [
                        "检查环境配置",
                        "修复依赖版本冲突",
                        "更新配置文件",
                        "验证环境一致性",
                        "测试部署流程"
                    ]
                },
                {
                    "id": 2,
                    "title": "参数调整方案",
                    "description": "调整运行时参数解决问题",
                    "approach": "parameter_tuning",
                    "pros": [
                        "无需重启服务",
                        "可以实时调整",
                        "风险最低"
                    ],
                    "cons": [
                        "可能只是临时解决方案",
                        "效果有限",
                        "需要持续监控"
                    ],
                    "effort": "low",
                    "risk": "low",
                    "affected_modules": ["config"],
                    "evidence_support": evidence.get("low_confidence", 0),
                    "steps": [
                        "识别问题参数",
                        "调整参数值",
                        "监控系统表现",
                        "记录参数变更",
                        "制定长期计划"
                    ]
                }
            ])

        # 根据架构约束过滤选项
        valid_options = []
        for option in options:
            if self._validate_option_architecture(option, context):
                valid_options.append(option)

        print(f"✅ 生成 {len(valid_options)} 个解决方案选项")

        return valid_options

    def _validate_option_architecture(self, option: Dict, context: ProblemContext) -> bool:
        """验证选项是否符合架构约束"""
        # 检查是否违反模块架构定义
        for module in option.get("affected_modules", []):
            module_defs = context.code_analysis.get("module_definitions", {}).get(module, {})
            ground_truth = module_defs.get("ground_truth", [])

            # 简化验证：如果选项类型与模块定义不冲突
            if option.get("approach") == "targeted_fix" and any("配置" in truth for truth in ground_truth):
                return False

        return True

    def _generate_functional_fix(self, context: ProblemContext) -> Dict[str, Any]:
        """生成功能性修复方案"""
        return {
            "steps": [
                "定位问题函数",
                "分析函数逻辑",
                "修复错误代码",
                "添加错误处理"
            ],
            "files_to_modify": context.code_analysis["code_context"]["files"][:2],  # 限制文件数量
            "estimated_complexity": "medium"
        }

    def _generate_config_fix(self, context: ProblemContext) -> Dict[str, Any]:
        """生成配置修复方案"""
        return {
            "steps": [
                "检查配置文件",
                "调整参数值",
                "重启服务"
            ],
            "config_files": ["config.json", ".env"],
            "estimated_complexity": "low"
        }

    def _generate_performance_fix(self, context: ProblemContext) -> Dict[str, Any]:
        """生成性能修复方案"""
        return {
            "steps": [
                "性能分析",
                "算法优化",
                "缓存添加",
                "资源调整"
            ],
            "files_to_modify": context.code_analysis["code_context"]["files"][:3],
            "estimated_complexity": "high"
        }

    def _validate_solution_architecture(self, solution: Dict, context: ProblemContext) -> bool:
        """验证解决方案是否符合架构"""
        # 简化验证：检查是否涉及过多模块
        if len(solution["affected_modules"]) > 3:
            return False

        # 检查是否符合模块的ground truth定义
        for module in solution["affected_modules"]:
            module_defs = context.code_analysis["module_definitions"].get(module, {})
            ground_truth = module_defs.get("ground_truth", [])

            # 简化检查：如果解决方案类型与模块定义不冲突
            if solution["type"] == "code_fix" and any("配置" in truth for truth in ground_truth):
                return False

        return True

    def _adjust_solution_for_architecture(self, solution: Dict, context: ProblemContext) -> Optional[Dict]:
        """调整解决方案以符合架构"""
        # 简化调整：减少涉及的模块
        if len(solution["affected_modules"]) > 3:
            solution["affected_modules"] = solution["affected_modules"][:2]
            solution["description"] += " (已调整以符合架构约束)"
            return solution

        return None

    def _interact_solution_selection(self, options: List[Dict[str, Any]], evidence: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """步骤7: 用户交互和方案选择"""
        print("\n📋 步骤7: 解决方案选项分析")
        print(f"\n📊 问题分析摘要:")
        print(f"- 证据总数: {evidence.get('total_evidence', 0)} 项")
        print(f"- 高置信度证据: {evidence.get('high_confidence', 0)} 项")
        print(f"- 相关文件: {len(evidence.get('supporting_files', []))} 个")

        print(f"\n🔍 可选解决方案选项:")

        for i, option in enumerate(options, 1):
            print(f"\n{'='*60}")
            print(f"选项 {i}: {option['title']}")
            print(f"描述: {option['description']}")
            print(f"方法: {option['approach']}")
            print(f"工作量: {option['effort']}")
            print(f"风险等级: {option['risk']}")
            print(f"影响模块: {', '.join(option['affected_modules'])}")

            print(f"\n✅ 优势:")
            for pro in option['pros']:
                print(f"  • {pro}")

            print(f"\n❌ 劣势:")
            for con in option['cons']:
                print(f"  • {con}")

            print(f"\n📋 实施步骤:")
            for j, step in enumerate(option['steps'], 1):
                print(f"  {j}. {step}")

        while True:
            try:
                print(f"\n{'='*60}")
                choice = input(f"\n请选择解决方案选项 (1-{len(options)}) 或输入 'details' 查看详细证据, 'cancel' 取消: ").strip().lower()

                if choice == 'cancel':
                    return None
                elif choice == 'details':
                    self._show_detailed_evidence(evidence)
                    continue

                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(options):
                    selected = options[choice_idx]
                    print(f"\n✅ 已选择: {selected['title']}")
                    print(f"方法: {selected['approach']}")
                    print(f"工作量: {selected['effort']}, 风险: {selected['risk']}")

                    confirm = input("\n确认此选择? (y/n): ").strip().lower()
                    if confirm == 'y':
                        return selected

            except ValueError:
                print("无效输入，请输入数字、'details'或'cancel'")

    def _show_detailed_evidence(self, evidence: Dict[str, Any]):
        """显示详细证据信息"""
        print(f"\n📋 详细证据信息:")
        print(f"{'='*50}")

        print(f"\n📊 证据统计:")
        print(f"- 总证据数: {evidence.get('total_evidence', 0)}")
        print(f"- 高置信度: {evidence.get('high_confidence', 0)}")
        print(f"- 中等置信度: {evidence.get('medium_confidence', 0)}")
        print(f"- 低置信度: {evidence.get('low_confidence', 0)}")

        print(f"\n📁 相关文件:")
        for file in evidence.get('supporting_files', []):
            print(f"- {file}")

        print(f"\n🔍 证据类型:")
        for evidence_type, items in evidence.get('evidence_by_type', {}).items():
            print(f"\n{evidence_type}:")
            for item in items:
                print(f"  • {item.get('description', '未知描述')} (置信度: {item.get('confidence', 0):.1f})")
                if 'file' in item:
                    print(f"    文件: {item['file']}")

        input("\n按回车键继续...")

    def _provide_execution_guidance(self, selected_option: Dict[str, Any], context: ProblemContext) -> Dict[str, Any]:
        """步骤8: 提供执行指导"""
        print(f"\n📋 步骤8: 执行指导")
        print(f"{'='*50}")
        print(f"🎯 选定方案: {selected_option['title']}")
        print(f"📝 方法: {selected_option['approach']}")
        print(f"⏱️  预估工作量: {selected_option['effort']}")
        print(f"⚠️  风险等级: {selected_option['risk']}")

        guidance = {
            "option_title": selected_option['title'],
            "approach": selected_option['approach'],
            "steps": selected_option['steps'],
            "affected_modules": selected_option['affected_modules'],
            "preparation": self._generate_preparation_steps(selected_option, context),
            "verification": self._generate_verification_steps(selected_option),
            "rollback": self._generate_rollback_plan(selected_option),
            "timeline": self._generate_timeline(selected_option)
        }

        print(f"\n📋 准备工作:")
        for i, step in enumerate(guidance['preparation'], 1):
            print(f"  {i}. {step}")

        print(f"\n🔄 执行步骤:")
        for i, step in enumerate(guidance['steps'], 1):
            print(f"  {i}. {step}")

        print(f"\n✅ 验证方法:")
        for i, step in enumerate(guidance['verification'], 1):
            print(f"  {i}. {step}")

        print(f"\n🔙 回滚计划:")
        for i, step in enumerate(guidance['rollback'], 1):
            print(f"  {i}. {step}")

        print(f"\n📅 时间规划:")
        print(f"  {guidance['timeline']}")

        return guidance

    def _generate_preparation_steps(self, option: Dict[str, Any], context: ProblemContext) -> List[str]:
        """生成准备步骤"""
        steps = [
            "备份相关文件和配置",
            "通知相关人员维护计划",
            "准备测试环境和数据",
            "记录当前系统状态"
        ]

        if option['approach'] == 'architectural_improvement':
            steps.extend([
                "设计新的架构方案",
                "准备迁移计划",
                "建立测试策略"
            ])
        elif option['approach'] == 'algorithm_optimization':
            steps.extend([
                "分析当前算法性能",
                "准备性能基准测试",
                "设计优化算法"
            ])

        return steps

    def _generate_verification_steps(self, option: Dict[str, Any]) -> List[str]:
        """生成验证步骤"""
        steps = [
            "功能测试 - 验证基本功能正常",
            "集成测试 - 验证与其他模块集成正常",
            "性能测试 - 验证性能指标满足要求"
        ]

        if option['risk'] in ['medium', 'high']:
            steps.insert(0, "小范围测试 - 在测试环境先行验证")

        if option['approach'] in ['architectural_improvement', 'algorithm_optimization']:
            steps.append("代码审查 - 确保代码质量")
            steps.append("文档更新 - 更新相关技术文档")

        return steps

    def _generate_rollback_plan(self, option: Dict[str, Any]) -> List[str]:
        """生成回滚计划"""
        steps = [
            "停止相关服务（如需要）",
            "恢复备份的文件和配置",
            "重启相关服务",
            "验证系统恢复正常"
        ]

        if option['approach'] == 'configuration_tuning':
            steps.insert(1, "恢复原始配置参数")

        return steps

    def _generate_timeline(self, option: Dict[str, Any]) -> str:
        """生成时间规划"""
        effort_map = {
            'low': '1-2天',
            'medium': '3-5天',
            'high': '1-2周'
        }

        effort = option.get('effort', 'medium')
        base_time = effort_map.get(effort, '3-5天')

        risk_factor = option.get('risk', 'low')
        if risk_factor == 'high':
            base_time += " (包含额外测试时间)"
        elif risk_factor == 'medium':
            base_time += " (包含验证时间)"

        return f"预估时间: {base_time}，建议在非高峰时段执行"

    def _generate_fix_suggestions(self, test_result: Dict[str, Any]) -> List[str]:
        """生成修复建议（不自动执行）"""
        suggestions = []

        for test in test_result.get("tests_run", []):
            if not test["success"]:
                error_output = test.get("error", "")
                if "ImportError" in error_output:
                    suggestions.append("检查和修复导入依赖问题")
                elif "SyntaxError" in error_output:
                    suggestions.append("修复代码语法错误")
                elif "AssertionError" in error_output:
                    suggestions.append("检查测试断言，修复代码逻辑")
                elif "ModuleNotFoundError" in error_output:
                    suggestions.append("安装缺失的模块依赖")
                else:
                    suggestions.append("检查代码逻辑，确保功能正确")

        if not suggestions:
            suggestions = [
                "检查构建配置文件",
                "验证所有依赖是否正确安装",
                "检查环境配置是否正确"
            ]

        return suggestions

    def _generate_fix_suggestions(self, test_result: Dict[str, Any]) -> List[str]:
        """生成修复建议（不自动执行）"""
        suggestions = []

        for test in test_result.get("tests_run", []):
            if not test["success"]:
                error_output = test.get("error", "")
                if "ImportError" in error_output:
                    suggestions.append("检查和修复导入依赖问题")
                elif "SyntaxError" in error_output:
                    suggestions.append("修复代码语法错误")
                elif "AssertionError" in error_output:
                    suggestions.append("检查测试断言，修复代码逻辑")
                elif "ModuleNotFoundError" in error_output:
                    suggestions.append("安装缺失的模块依赖")
                else:
                    suggestions.append("检查代码逻辑，确保功能正确")

        if not suggestions:
            suggestions = [
                "检查构建配置文件",
                "验证所有依赖是否正确安装",
                "检查环境配置是否正确"
            ]

        return suggestions

    def _show_detailed_fix_plan(self, test_result: Dict[str, Any], solution: Dict[str, Any]):
        """显示详细的修复计划（仅供参考）"""
        print("\n📋 详细修复计划:")
        print("=" * 50)

        # 分析失败原因
        print("🔍 失败原因分析:")
        for test in test_result.get("tests_run", []):
            if not test["success"]:
                print(f"  命令: {test['command']}")
                print(f"  错误: {test['error'][:100]}...")

        print(f"\n📝 建议的修复步骤:")
        print("1. 检查代码修改是否正确引入")
        print("2. 验证所有依赖是否满足")
        print("3. 检查测试环境配置")
        print("4. 手动运行失败的测试，查看详细错误")
        print("5. 根据错误信息进行相应修复")

        print(f"\n⚠️ 重要提醒:")
        print("- 所有修复都需要手动执行")
        print("- 修复后请重新运行测试验证")
        print("- 确保修复符合项目架构定义")
        print("- 修复完成后需要更新相关文档")

        print("=" * 50)

    def _analyze_test_failure(self, test_result: Dict[str, Any]) -> Dict[str, Any]:
        """分析测试失败原因"""
        analysis = {
            "root_cause": "unknown",
            "specific_errors": [],
            "suggested_fixes": []
        }

        for test in test_result.get("tests_run", []):
            if not test["success"]:
                analysis["specific_errors"].append(test["error"])

        if analysis["specific_errors"]:
            analysis["root_cause"] = "test_errors_detected"
            analysis["suggested_fixes"] = ["检查测试用例", "修复代码逻辑", "更新测试依赖"]

        return analysis

    def _generate_fix_plan(self, error_analysis: Dict[str, Any], original_solution: Dict[str, Any]) -> Dict[str, Any]:
        """生成修复计划"""
        fix_plan = {
            "fixes": [],
            "estimated_time": 0
        }

        suggested_fixes = error_analysis.get("suggested_fixes", [])
        for fix in suggested_fixes:
            fix_plan["fixes"].append({
                "action": fix,
                "priority": "medium",
                "estimated_time": 10  # 分钟
            })
            fix_plan["estimated_time"] += 10

        return fix_plan

    def _apply_fixes(self, fix_plan: Dict[str, Any]) -> Dict[str, Any]:
        """应用修复"""
        print("🔧 应用修复...")

        applied_fixes = []

        for fix in fix_plan.get("fixes", []):
            print(f"应用修复: {fix['action']}")
            # 这里应该有实际的修复逻辑
            applied_fixes.append(fix["action"])

        return {
            "success": True,
            "applied_fixes": applied_fixes,
            "total_time": fix_plan.get("estimated_time", 0)
        }

    def _load_project_data(self) -> Dict[str, Any]:
        """加载项目数据"""
        if self.project_data_path.exists():
            try:
                with open(self.project_data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        return {"modules": {}}

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python problem_analyzer.py '<问题描述>'")
        print("示例: python problem_analyzer.py '系统性能很慢，需要优化'")
        sys.exit(1)

    target_directory = sys.argv[1] if len(sys.argv) > 2 else "."
    user_query = sys.argv[1] if len(sys.argv) == 2 else " ".join(sys.argv[2:])

    analyzer = ProblemAnalyzer(target_directory)
    result = analyzer.analyze_problem(user_query)

    print(f"\n📊 分析结果:")
    print(f"状态: {result['status']}")
    if 'message' in result:
        print(f"信息: {result['message']}")
    if 'final_status' in result:
        print(f"最终状态: {result['final_status']}")