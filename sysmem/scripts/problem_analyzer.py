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

        # 加载项目数据并检查新鲜度
        project_data = self._load_and_validate_project_data()
        if not project_data:
            return None

        # 如果需要，执行局部数据更新
        updated_data = self._check_and_update_data_freshness(user_query, project_data)
        if updated_data:
            project_data = updated_data

        # AI分析问题类型和相关模块
        problem_type = self._classify_problem_type(user_query)
        related_modules = self._find_related_modules(user_query, project_data)

        # 读取相关模块的README和Ground Truth
        module_definitions = {}
        for module in related_modules:
            module_readme = self.root_path / module / "README.md"
            if module_readme.exists():
                content = SysmemUtils.safe_read_file(module_readme)
                definitions = self._extract_module_definitions(content)
                # 更新Ground Truth（如果需要）
                updated_definitions = self._update_ground_truth_if_needed(module, definitions)
                module_definitions[module] = updated_definitions
            else:
                # 如果没有README，尝试基于代码生成基本的定义
                print(f"⚠️  模块 '{module}' 没有README文件，尝试基于代码生成定义")
                basic_definitions = self._generate_ground_truth_for_module(module, module, {})
                module_definitions[module] = {
                    "ground_truth": basic_definitions,
                    "core_functions": [],
                    "interfaces": [],
                    "constraints": [],
                    "capabilities": [],
                    "limitations": []
                }

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
        """提取模块定义和Ground Truth"""
        definitions = {
            "core_functions": [],
            "ground_truth": [],
            "interfaces": [],
            "constraints": [],
            "capabilities": [],
            "limitations": []
        }

        lines = readme_content.split('\n')
        current_section = None

        for i, line in enumerate(lines):
            line = line.strip()
            line_lower = line.lower()

            # 识别不同的定义部分
            if "核心功能定义" in line or "core functions" in line_lower:
                current_section = "core_functions"
            elif "ground truth" in line_lower or "重要定义" in line_lower or "核心定义" in line_lower:
                current_section = "ground_truth"
            elif "接口定义" in line_lower or "interface" in line_lower:
                current_section = "interfaces"
            elif "约束" in line_lower or "constraint" in line_lower:
                current_section = "constraints"
            elif "功能" in line_lower or "capability" in line_lower or "能做什么" in line_lower:
                current_section = "capabilities"
            elif "限制" in line_lower or "limitation" in line_lower or "不能做什么" in line_lower:
                current_section = "limitations"
            elif line.startswith('**重要**') or line.startswith('important') or line.startswith('**ground truth**'):
                if current_section:
                    # 清理格式，提取核心内容
                    clean_line = line.replace('**', '').replace('*', '').strip()
                    if clean_line and len(clean_line) > 5:
                        # 去掉markdown格式标记
                        clean_line = re.sub(r'[#*_`]', '', clean_line)
                        definitions[current_section].append(clean_line)

            # 处理列表项
            elif line.startswith('-') or line.startswith('*'):
                if current_section and current_section in ["ground_truth", "capabilities", "limitations"]:
                    clean_line = line.lstrip('-* ').strip()
                    if clean_line and len(clean_line) > 5:
                        definitions[current_section].append(clean_line)

        # 如果没有找到ground truth，尝试智能提取
        if not definitions["ground_truth"]:
            definitions["ground_truth"] = self._extract_ground_truth_heuristic(readme_content)

        return definitions

    def _extract_ground_truth_heuristic(self, content: str) -> List[str]:
        """启发式提取Ground Truth定义"""
        ground_truth = []
        lines = content.split('\n')

        # 寻找包含关键信息的行
        gt_patterns = [
            r'主要功能[:：]',
            r'核心作用[:：]',
            r'负责.*：',
            r'支持.*：',
            r'用于.*：',
            r'目标是.*：',
            r'purpose[:：]',
            r'responsible for.*：',
            r'provides.*：'
        ]

        for line in lines:
            line = line.strip()
            if len(line) < 10:
                continue

            # 检查是否包含Ground Truth模式
            for pattern in gt_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    clean_line = re.sub(r'[#*_`]', '', line).strip()
                    if clean_line:
                        ground_truth.append(clean_line)
                    break

        # 限制数量，避免太多无关内容
        return ground_truth[:10] if ground_truth else []

    def _update_ground_truth_if_needed(self, module_path: str, current_definitions: Dict[str, Any]) -> Dict[str, Any]:
        """根据需要更新Ground Truth"""
        print(f"🔍 检查模块 '{module_path}' 的Ground Truth...")

        # 检查是否缺少关键的Ground Truth定义
        current_gt = current_definitions.get("ground_truth", [])

        # 基于模块功能智能生成Ground Truth
        if len(current_gt) < 3:  # 如果Ground Truth太少，尝试补充
            module_name = module_path.split('/')[-1]
            generated_gt = self._generate_ground_truth_for_module(module_name, module_path, current_definitions)

            if generated_gt:
                print(f"📝 为模块 '{module_path}' 补充Ground Truth定义")
                current_definitions["ground_truth"].extend(generated_gt)

        return current_definitions

    def _generate_ground_truth_for_module(self, module_name: str, module_path: str, definitions: Dict[str, Any]) -> List[str]:
        """为模块生成Ground Truth定义"""
        generated_gt = []

        # 基于模块名推断功能
        if "collect" in module_name.lower() or "data" in module_name.lower():
            generated_gt.extend([
                f"{module_name}负责收集和管理项目数据",
                f"确保数据的完整性和准确性",
                f"支持模块化和增量数据收集"
            ])
        elif "analyze" in module_name.lower() or "analysis" in module_name.lower():
            generated_gt.extend([
                f"{module_name}负责代码分析和质量检查",
                f"识别潜在问题和改进机会",
                f"提供结构化的分析报告"
            ])
        elif "install" in module_name.lower() or "setup" in module_name.lower():
            generated_gt.extend([
                f"{module_name}负责项目安装和环境配置",
                f"自动化安装流程和依赖管理",
                f"确保安装过程的可靠性"
            ])

        # 基于现有功能定义生成
        core_functions = definitions.get("core_functions", [])
        if core_functions:
            for func in core_functions[:3]:  # 最多取前3个
                generated_gt.append(f"{module_name}提供{func}功能")

        # 基于代码文件推断功能
        try:
            module_full_path = self.root_path / module_path
            if module_full_path.exists():
                py_files = list(module_full_path.glob("*.py"))
                if py_files:
                    generated_gt.append(f"{module_name}包含{len(py_files)}个Python模块文件")
        except:
            pass

        return generated_gt[:5]  # 限制数量

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

        # 读取CLAUDE.md和AGENTS.md中的日志信息
        claude_content = SysmemUtils.safe_read_file(self.claude_md_path)
        agents_md_path = self.root_path / "AGENTS.md"
        agents_content = SysmemUtils.safe_read_file(agents_md_path)

        log_info = self._extract_log_information(claude_content + "\n" + agents_content)

        # 根据问题类型确定需要查看的日志
        relevant_logs = self._determine_relevant_logs(context.problem_type, log_info)

        # 实际读取和分析日志文件
        log_analysis_results = self._read_and_analyze_log_files(relevant_logs, context)

        context.relevant_logs = relevant_logs
        context.code_analysis["log_analysis"] = log_analysis_results

        print(f"✅ 识别相关日志: {', '.join(relevant_logs)}")
        print(f"📊 发现相关日志条目: {log_analysis_results.get('total_entries', 0)} 条")
        print(f"🚨 发现错误/警告: {log_analysis_results.get('error_count', 0)} 条")

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

    def _read_and_analyze_log_files(self, log_files: List[str], context: ProblemContext) -> Dict[str, Any]:
        """实际读取和分析日志文件"""
        analysis_results = {
            "total_entries": 0,
            "error_count": 0,
            "warning_count": 0,
            "relevant_entries": [],
            "log_files_found": [],
            "error_patterns": [],
            "time_analysis": {}
        }

        # 常见日志文件位置
        log_search_paths = [
            self.root_path / "logs",
            self.root_path / ".logs",
            self.root_path / "log",
            self.root_path,
            self.root_path / "var" / "log",
            self.root_path / "tmp"
        ]

        for log_file in log_files:
            found_log_files = []

            # 搜索日志文件
            for search_path in log_search_paths:
                if search_path.exists():
                    # 直接匹配
                    direct_path = search_path / log_file
                    if direct_path.exists() and direct_path.is_file():
                        found_log_files.append(direct_path)

                    # 通配符搜索
                    for log_path in search_path.glob(f"*{log_file}*"):
                        if log_path.is_file():
                            found_log_files.append(log_path)

            # 分析找到的日志文件
            for log_path in found_log_files:
                print(f"📖 分析日志文件: {log_path}")
                try:
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()

                    file_analysis = self._analyze_log_content(log_content, log_path.name, context)
                    analysis_results["total_entries"] += file_analysis["entries"]
                    analysis_results["error_count"] += file_analysis["errors"]
                    analysis_results["warning_count"] += file_analysis["warnings"]
                    analysis_results["relevant_entries"].extend(file_analysis["relevant_entries"])
                    analysis_results["log_files_found"].append(str(log_path))
                    analysis_results["error_patterns"].extend(file_analysis["error_patterns"])

                    print(f"  - 发现条目: {file_analysis['entries']}, 错误: {file_analysis['errors']}")

                except Exception as e:
                    print(f"  ⚠️  读取日志文件失败: {e}")

        # 如果没有找到任何日志文件，尝试查看标准输出
        if not analysis_results["log_files_found"]:
            print("📋 未找到指定日志文件，尝试查找应用输出文件...")
            standard_logs = [
                "app.log", "application.log", "server.log", "service.log",
                "output.log", "out.log", "console.log"
            ]

            for std_log in standard_logs:
                for search_path in log_search_paths[:3]:  # 只搜索前几个路径
                    log_path = search_path / std_log
                    if log_path.exists():
                        print(f"📖 发现标准日志: {log_path}")
                        try:
                            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                                log_content = f.read()

                            file_analysis = self._analyze_log_content(log_content, log_path.name, context)
                            analysis_results["total_entries"] += file_analysis["entries"]
                            analysis_results["error_count"] += file_analysis["errors"]
                            analysis_results["warning_count"] += file_analysis["warnings"]
                            analysis_results["relevant_entries"].extend(file_analysis["relevant_entries"])
                            analysis_results["log_files_found"].append(str(log_path))
                        except Exception as e:
                            print(f"  ⚠️  读取失败: {e}")

        return analysis_results

    def _analyze_log_content(self, content: str, filename: str, context: ProblemContext) -> Dict[str, Any]:
        """分析日志内容"""
        analysis = {
            "entries": 0,
            "errors": 0,
            "warnings": 0,
            "relevant_entries": [],
            "error_patterns": []
        }

        lines = content.split('\n')
        user_query_lower = context.user_query.lower()
        query_keywords = user_query_lower.split()

        # 分析每一行
        for i, line in enumerate(lines):
            if not line.strip():
                continue

            analysis["entries"] += 1
            line_lower = line.lower()

            # 检查错误模式
            error_patterns = [
                r'error', r'exception', r'failed', r'crash', r'panic',
                r'错误', r'异常', r'失败', r'崩溃'
            ]

            warning_patterns = [
                r'warning', r'warn', r'deprecated', r'timeout',
                r'警告', r'超时', r'已弃用'
            ]

            # 检查是否包含错误
            is_error = any(re.search(pattern, line_lower) for pattern in error_patterns)
            is_warning = any(re.search(pattern, line_lower) for pattern in warning_patterns)

            if is_error:
                analysis["errors"] += 1
                # 记录错误模式
                for pattern in error_patterns:
                    if re.search(pattern, line_lower):
                        analysis["error_patterns"].append({
                            "pattern": pattern,
                            "line": line.strip(),
                            "line_number": i + 1,
                            "file": filename
                        })
                        break

            if is_warning:
                analysis["warnings"] += 1

            # 检查是否与用户查询相关
            relevance_score = 0
            for keyword in query_keywords:
                if keyword in line_lower:
                    relevance_score += 1

            # 如果相关度高或包含错误/警告，记录这一行
            if relevance_score > 0 or is_error or is_warning:
                analysis["relevant_entries"].append({
                    "line_number": i + 1,
                    "content": line.strip(),
                    "file": filename,
                    "is_error": is_error,
                    "is_warning": is_warning,
                    "relevance_score": relevance_score,
                    "timestamp": self._extract_timestamp(line)
                })

        # 按相关性排序
        analysis["relevant_entries"].sort(
            key=lambda x: (x["is_error"], x["is_warning"], x["relevance_score"]),
            reverse=True
        )

        # 只保留最相关的条目
        if len(analysis["relevant_entries"]) > 50:
            analysis["relevant_entries"] = analysis["relevant_entries"][:50]

        return analysis

    def _extract_timestamp(self, log_line: str) -> Optional[str]:
        """从日志行提取时间戳"""
        # 常见时间戳模式
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # 2023-12-01 10:30:45
            r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}',  # 12/01/2023 10:30:45
            r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}',  # 12-01-2023 10:30:45
            r'\d{2}:\d{2}:\d{2}',                 # 10:30:45
            r'\w{3} \d{2} \d{2}:\d{2}:\d{2}',     # Dec 01 10:30:45
        ]

        for pattern in timestamp_patterns:
            match = re.search(pattern, log_line)
            if match:
                return match.group()

        return None

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
        """步骤6: 生成ABC三种解决方案"""
        print("\n📋 步骤6: 生成ABC三种解决方案...")
        print("🔄 根据问题分析生成三种不同方向的解决方案...")

        options = []

        # 方案A: 临时绕过方案
        option_a = self._generate_workaround_solution(context, evidence)
        options.append(option_a)

        # 方案B: 完整修复方案（默认推荐）
        option_b = self._generate_complete_fix_solution(context, evidence)
        options.append(option_b)

        # 方案C: 保守疗法方案
        option_c = self._generate_conservative_solution(context, evidence)
        options.append(option_c)

        # 为每个方案添加标识
        for i, option in enumerate(options, 1):
            option["option_letter"] = chr(64 + i)  # A, B, C
            option["is_recommended"] = (i == 2)  # B方案默认推荐

        return options

    def _generate_workaround_solution(self, context: ProblemContext, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """生成方案A: 临时绕过方案"""
        return {
            "id": "A",
            "title": "方案A - 临时绕过方案",
            "description": "快速临时解决方案，绕过问题点以恢复系统功能",
            "approach": "workaround",
            "method": "临时绕过",
            "pros": [
                "实施速度快，立即可用",
                "风险最低，不影响现有功能",
                "不需要深入修改代码架构",
                "可以作为临时解决方案保证业务连续性"
            ],
            "cons": [
                "只是治标不治本，根本问题依然存在",
                "可能在系统重启后失效",
                "可能引入技术债务",
                "不适合作为长期解决方案"
            ],
            "effort": "low",
            "risk": "low",
            "affected_modules": context.related_modules[:1],
            "evidence_support": evidence.get("low_confidence", 0),
            "temporary": True,
            "estimated_time": "30分钟 - 2小时",
            "steps": [
                "识别问题触发的具体位置",
                "设计临时绕过逻辑",
                "实施代码修改",
                "添加临时监控日志",
                "验证绕过效果"
            ],
            "fallback_plan": "如果绕过失败，需要采用完整修复方案"
        }

    def _generate_complete_fix_solution(self, context: ProblemContext, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """生成方案B: 完整修复方案"""
        return {
            "id": "B",
            "title": "方案B - 完整修复方案（推荐）",
            "description": "从根本上解决问题，确保长期稳定性和系统健康",
            "approach": "complete_fix",
            "method": "完整修复",
            "pros": [
                "彻底解决根本问题",
                "提高系统长期稳定性",
                "符合最佳实践和架构原则",
                "避免技术债务积累",
                "提升代码质量和可维护性"
            ],
            "cons": [
                "实施时间较长，需要更多测试",
                "可能影响更多系统组件",
                "需要更深入的代码理解",
                "风险相对较高，需要谨慎实施"
            ],
            "effort": "high",
            "risk": "medium",
            "affected_modules": context.related_modules,
            "evidence_support": evidence.get("high_confidence", 0),
            "temporary": False,
            "estimated_time": "2-8小时",
            "recommended": True,
            "steps": [
                "深入分析问题根本原因",
                "设计完整的解决方案",
                "重构相关代码模块",
                "更新单元测试和集成测试",
                "性能测试和回归测试",
                "更新文档和Ground Truth"
            ],
            "success_criteria": [
                "问题完全解决，不再重现",
                "系统性能不下降",
                "所有相关测试通过",
                "代码质量得到改善"
            ]
        }

    def _generate_conservative_solution(self, context: ProblemContext, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """生成方案C: 保守疗法方案"""
        return {
            "id": "C",
            "title": "方案C - 保守疗法方案",
            "description": "渐进式改进，最小化变更风险，逐步优化系统",
            "approach": "conservative",
            "method": "保守疗法",
            "pros": [
                "变更风险最小，容易控制",
                "可以分阶段实施，逐步验证",
                "对现有系统影响最小",
                "便于回滚和风险控制",
                "团队学习和适应成本较低"
            ],
            "cons": [
                "解决时间较长，见效慢",
                "可能无法完全解决根本问题",
                "需要持续的监控和调整",
                "可能需要多次迭代"
            ],
            "effort": "medium",
            "risk": "low",
            "affected_modules": context.related_modules[:2],
            "evidence_support": evidence.get("medium_confidence", 0),
            "temporary": False,
            "estimated_time": "1-4小时",
            "iterative": True,
            "steps": [
                "问题风险评估和优先级排序",
                "设计最小化变更方案",
                "实施第一阶段改进",
                "监控改进效果",
                "根据结果决定下一步行动",
                "迭代优化直到问题解决"
            ],
            "phases": [
                "第一阶段: 风险缓解（1-2小时）",
                "第二阶段: 功能改进（2-4小时）",
                "第三阶段: 质量提升（按需）"
            ],
            "monitoring_required": True
        }

    def _interactive_solution_selection(self, options: List[Dict[str, Any]], evidence: Dict[str, Any], context: ProblemContext) -> Optional[Dict[str, Any]]:
        """交互式ABC方案选择流程"""
        print(f"\n🎯 ABC三种解决方案交互式选择流程")
        print("="*70)

        # 显示问题分析摘要
        print(f"\n📊 问题分析摘要:")
        print(f"- 问题类型: {context.problem_type.value}")
        print(f"- 用户问题: {context.user_query}")
        print(f"- 关联模块: {', '.join(context.related_modules) if context.related_modules else '无'}")
        print(f"- 证据总数: {evidence.get('total_evidence', 0)} 项")
        print(f"- 高置信度证据: {evidence.get('high_confidence', 0)} 项")
        print(f"- 相关日志文件: {len(evidence.get('log_analysis', {}).get('log_files_found', []))} 个")

        # 显示ABC三种方案
        print(f"\n💡 ABC三种解决方案:")
        for i, option in enumerate(options, 1):
            letter = option['option_letter']
            recommended = " (推荐)" if option.get('is_recommended') else ""
            print(f"\n{'='*70}")
            print(f"方案 {letter}{recommended}: {option['title']}")
            print(f"方法: {option['method']} | 工作量: {option['effort']} | 风险: {option['risk']}")
            print(f"预估时间: {option.get('estimated_time', '未知')}")
            print(f"影响模块: {', '.join(option['affected_modules'])}")

            print(f"\n✅ 主要优势:")
            for pro in option['pros']:
                print(f"  • {pro}")

            print(f"\n❌ 主要劣势:")
            for con in option['cons']:
                print(f"  • {con}")

            print(f"\n📋 核心步骤 (前3步):")
            for j, step in enumerate(option['steps'][:3], 1):
                print(f"  {j}. {step}")
            if len(option['steps']) > 3:
                print(f"  ... 共{len(option['steps'])}个步骤")

        # 用户交互选择
        while True:
            try:
                print(f"\n{'='*70}")
                choice = input(f"\n请选择操作:\n"
                               f"1. 选择ABC方案 (A-C)\n"
                               f"2. 查看详细证据信息\n"
                               f"3. 查看相关模块Ground Truth\n"
                               f"4. 查看日志分析结果\n"
                               f"5. 完成分析\n\n"
                               f"请输入选择 (1-5): ").strip()

                if choice == '1':
                    return self._select_abc_solution(options)
                elif choice == '2':
                    self._show_detailed_evidence(evidence)
                elif choice == '3':
                    self._show_module_ground_truth(context)
                elif choice == '4':
                    self._show_log_analysis_results(context)
                elif choice == '5':
                    print(f"\n📋 分析完成。")
                    print(f"💡 建议保存分析结果，并基于证据选择合适的解决方案。")
                    return None
                else:
                    print("请输入有效选项 (1-5)")

            except ValueError:
                print("请输入有效数字")
            except KeyboardInterrupt:
                print(f"\n📋 用户中断分析")
                return None

    def _select_abc_solution(self, options: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """选择ABC具体方案"""
        print(f"\n🎯 请选择ABC方案:")

        for option in options:
            letter = option['option_letter']
            recommended = " (推荐)" if option.get('is_recommended') else ""
            print(f"  {letter}. {option['title']}{recommended}")
            print(f"     {option['description']}")

        while True:
            try:
                choice = input(f"\n选择方案 (A/B/C) 或 'back' 返回: ").strip().upper()

                if choice == 'BACK':
                    return None

                if choice in ['A', 'B', 'C']:
                    selected = None
                    for option in options:
                        if option['option_letter'] == choice:
                            selected = option
                            break

                    if selected:
                        print(f"\n✅ 已选择: {selected['title']}")
                        print(f"📋 方案详情:")
                        print(f"  - 方法: {selected['method']}")
                        print(f"  - 工作量: {selected['effort']}")
                        print(f"  - 风险等级: {selected['risk']}")
                        print(f"  - 预估时间: {selected.get('estimated_time', '未知')}")
                        print(f"  - 临时方案: {'是' if selected.get('temporary') else '否'}")

                        # 询问确认
                        confirm = input(f"\n确认选择方案 {choice} '{selected['title']}'? (y/n): ").strip().lower()
                        if confirm == 'y':
                            print(f"\n🎉 方案 {choice} 已确认！")
                            return selected
                        else:
                            print(f"已取消选择，请重新选择。")
                    else:
                        print(f"未找到方案 {choice}，请重新选择。")
                else:
                    print("请输入 A、B、C 或 'back'")

            except ValueError:
                print("输入无效，请重新输入")

    def _show_module_ground_truth(self, context: ProblemContext):
        """显示相关模块的Ground Truth"""
        print(f"\n📋 相关模块Ground Truth:")
        print("="*50)

        module_definitions = context.code_analysis.get("module_definitions", {})

        for module in context.related_modules:
            if module in module_definitions:
                definitions = module_definitions[module]
                print(f"\n📦 模块: {module}")

                ground_truth = definitions.get("ground_truth", [])
                if ground_truth:
                    print(f"\n  🎯 Ground Truth ({len(ground_truth)}项):")
                    for i, gt in enumerate(ground_truth, 1):
                        print(f"    {i}. {gt}")
                else:
                    print(f"\n  ⚠️  未找到Ground Truth定义")

                capabilities = definitions.get("capabilities", [])
                if capabilities:
                    print(f"\n  🔧 功能能力 ({len(capabilities)}项):")
                    for cap in capabilities[:3]:
                        print(f"    • {cap}")

                limitations = definitions.get("limitations", [])
                if limitations:
                    print(f"\n  🚫 限制条件 ({len(limitations)}项):")
                    for limit in limitations[:3]:
                        print(f"    • {limit}")
            else:
                print(f"\n📦 模块: {module}")
                print(f"  ⚠️  未找到模块定义信息")

        input("\n按回车键继续...")

    def _show_log_analysis_results(self, context: ProblemContext):
        """显示日志分析结果"""
        print(f"\n📋 日志分析结果:")
        print("="*50)

        log_analysis = context.code_analysis.get("log_analysis", {})

        if log_analysis:
            print(f"\n📊 统计信息:")
            print(f"  - 总日志条目: {log_analysis.get('total_entries', 0)} 条")
            print(f"  - 错误条目: {log_analysis.get('error_count', 0)} 条")
            print(f"  - 警告条目: {log_analysis.get('warning_count', 0)} 条")
            print(f"  - 发现日志文件: {len(log_analysis.get('log_files_found', []))} 个")

            relevant_entries = log_analysis.get('relevant_entries', [])
            if relevant_entries:
                print(f"\n🔍 相关日志条目 (前10条):")
                for entry in relevant_entries[:10]:
                    status = "🚨" if entry['is_error'] else "⚠️" if entry['is_warning'] else "ℹ️"
                    timestamp = f" [{entry.get('timestamp', 'N/A')}]" if entry.get('timestamp') else ""
                    print(f"  {status} {timestamp} {entry['file']}:{entry['line_number']}")
                    print(f"     {entry['content']}")
                if len(relevant_entries) > 10:
                    print(f"  ... 还有 {len(relevant_entries) - 10} 条相关日志")
            else:
                print(f"\n ℹ️ 未发现与问题相关的日志条目")

            error_patterns = log_analysis.get('error_patterns', [])
            if error_patterns:
                print(f"\n🚨 错误模式:")
                for pattern in error_patterns[:5]:
                    print(f"  • {pattern['pattern']} - {pattern['file']}:{pattern['line_number']}")
        else:
            print(f"\n ⚠️ 未找到日志分析结果")

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

    def _load_and_validate_project_data(self) -> Optional[Dict[str, Any]]:
        """加载并验证项目数据的新鲜度"""
        if not self.project_data_path.exists():
            print("⚠️  未找到项目数据文件，需要先收集项目数据")
            return None

        try:
            with open(self.project_data_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
        except Exception as e:
            print(f"❌ 无法读取项目数据文件: {e}")
            return None

        # 检查数据时间戳
        scan_time = project_data.get("scan_info", {}).get("scan_time", "")
        if not scan_time:
            print("⚠️  项目数据缺少时间戳信息")
            return project_data  # 仍然返回数据，但警告

        print(f"✅ 项目数据已加载，扫描时间: {scan_time}")
        return project_data

    def _check_and_update_data_freshness(self, user_query: str, project_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检查数据新鲜度并根据需要进行局部更新"""
        print("🔍 检查相关模块的数据新鲜度...")

        # 1. 识别用户查询相关的模块
        related_modules = self._find_related_modules(user_query, project_data)
        if not related_modules:
            print("ℹ️  未识别到相关模块，跳过数据更新检查")
            return None

        print(f"📋 识别到相关模块: {', '.join(related_modules)}")

        # 2. 检查相关模块文件的修改时间
        modules_need_update = []
        scan_time_str = project_data.get("scan_info", {}).get("scan_time", "")

        if scan_time_str:
            try:
                from datetime import datetime
                scan_time = datetime.strptime(scan_time_str, "%Y-%m-%d %H:%M:%S")

                for module in related_modules:
                    module_path = self.root_path / module
                    if module_path.exists():
                        # 检查模块内文件的最新修改时间
                        latest_mtime = 0
                        for file_path in module_path.rglob("*"):
                            if file_path.is_file():
                                mtime = file_path.stat().st_mtime
                                latest_mtime = max(latest_mtime, mtime)

                        scan_timestamp = scan_time.timestamp()
                        if latest_mtime > scan_timestamp:
                            modules_need_update.append(module)
                            time_diff = latest_mtime - scan_timestamp
                            print(f"🔄 模块 '{module}' 需要更新 (文件变更时间差: {int(time_diff/60)} 分钟)")
            except Exception as e:
                print(f"⚠️  时间比较失败: {e}")

        # 3. 执行局部数据更新
        if modules_need_update:
            print(f"🔄 执行局部数据更新，涉及 {len(modules_need_update)} 个模块...")
            return self._perform_partial_data_update(modules_need_update)
        else:
            print("✅ 相关模块数据都是最新的，无需更新")
            return None

    def _perform_partial_data_update(self, modules_to_update: List[str]) -> Optional[Dict[str, Any]]:
        """执行局部数据更新"""
        try:
            # 导入数据收集器
            from collect_data import ProjectDataCollector

            print("🔄 正在执行局部数据收集...")
            collector = ProjectDataCollector(str(self.root_path))

            # 对每个需要更新的模块进行数据收集
            updated_data = None
            for module in modules_to_update:
                print(f"📊 收集模块 '{module}' 的最新数据...")
                module_data = collector.collect_module_specific_data(module)

                if module_data and "modules" in module_data:
                    if not updated_data:
                        # 加载现有数据作为基础
                        updated_data = self._load_project_data()

                    # 更新对应模块的数据
                    if module in module_data["modules"]:
                        updated_data["modules"][module] = module_data["modules"][module]
                        print(f"✅ 模块 '{module}' 数据已更新")

            if updated_data:
                # 保存更新后的数据
                self._save_project_data(updated_data)
                print("✅ 局部数据更新完成并已保存")
                return updated_data

        except Exception as e:
            print(f"⚠️  局部数据更新失败: {e}")
            print("💡 建议手动运行: python3 scripts/collect_data.py --module <模块名>")

        return None

    def _save_project_data(self, data: Dict[str, Any]):
        """保存项目数据"""
        try:
            self.project_data_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.project_data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存项目数据失败: {e}")

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