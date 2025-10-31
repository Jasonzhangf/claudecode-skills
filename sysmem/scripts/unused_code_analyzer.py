#!/usr/bin/env python3
"""
未使用代码分析器 - 静态扫描未调用的函数，并提供AI分析功能
"""

import os
import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from collections import defaultdict
import re

class UnusedCodeAnalyzer:
    """未使用代码分析器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.function_definitions = {}
        self.function_calls = defaultdict(set)
        self.imports = defaultdict(set)
        self.classes = {}
        self.methods = defaultdict(set)

    def scan_project(self, target_modules: List[str] = None) -> Dict[str, Any]:
        """扫描项目中的函数和调用关系"""
        print("🔍 开始静态分析项目代码...")

        if target_modules:
            print(f"📁 目标模块: {', '.join(target_modules)}")
            scan_dirs = [self.project_root / module for module in target_modules]
        else:
            print("📁 扫描整个项目")
            scan_dirs = [self.project_root]

        # 扫描所有Python文件
        python_files = []
        for scan_dir in scan_dirs:
            for py_file in scan_dir.rglob("*.py"):
                # 跳过__pycache__等目录
                if "__pycache__" in str(py_file) or ".venv" in str(py_file):
                    continue
                python_files.append(py_file)

        print(f"📄 发现 {len(python_files)} 个Python文件")

        # 第一遍：收集所有函数定义
        print("🔍 分析函数定义...")
        for py_file in python_files:
            self._analyze_definitions(py_file)

        # 第二遍：收集所有函数调用
        print("🔍 分析函数调用...")
        for py_file in python_files:
            self._analyze_calls(py_file)

        # 分析未使用的函数
        print("📊 分析未使用的函数...")
        unused_functions = self._find_unused_functions()

        # 生成分析报告
        report = {
            "scan_time": self._get_current_time(),
            "project_root": str(self.project_root),
            "target_modules": target_modules or ["整个项目"],
            "total_files": len(python_files),
            "total_functions": len(self.function_definitions),
            "total_calls": sum(len(calls) for calls in self.function_calls.values()),
            "unused_functions": unused_functions,
            "function_definitions": {k: v for k, v in self.function_definitions.items()},
            "import_modules": {k: list(v) for k, v in self.imports.items()},
            "function_calls": {k: list(v) for k, v in self.function_calls.items()},
            "recommendations": self._generate_recommendations(unused_functions)
        }

        print(f"✅ 分析完成，发现 {len(unused_functions)} 个可能未使用的函数")
        return report

    def _analyze_definitions(self, file_path: Path):
        """分析文件中的函数定义"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                # 函数定义
                if isinstance(node, ast.FunctionDef):
                    func_key = f"{file_path.relative_to(self.project_root)}:{node.lineno}:{node.name}"

                    self.function_definitions[func_key] = {
                        "name": node.name,
                        "file": str(file_path.relative_to(self.project_root)),
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node) or "",
                        "is_method": False,
                        "class_name": None,
                        "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
                        "is_private": node.name.startswith('_'),
                        "is_dunder": node.name.startswith('__') and node.name.endswith('__'),
                        "is_test": 'test' in node.name.lower(),
                        "code_snippet": self._extract_function_snippet(content, node)
                    }

                # 类定义
                elif isinstance(node, ast.ClassDef):
                    class_key = f"{file_path.relative_to(self.project_root)}:{node.lineno}:{node.name}"
                    self.classes[class_key] = {
                        "name": node.name,
                        "file": str(file_path.relative_to(self.project_root)),
                        "line": node.lineno,
                        "methods": []
                    }

                    # 分析类方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_key = f"{file_path.relative_to(self.project_root)}:{item.lineno}:{item.name}"

                            self.function_definitions[method_key] = {
                                "name": item.name,
                                "file": str(file_path.relative_to(self.project_root)),
                                "line": item.lineno,
                                "args": [arg.arg for arg in item.args.args],
                                "docstring": ast.get_docstring(item) or "",
                                "is_method": True,
                                "class_name": node.name,
                                "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in item.decorator_list],
                                "is_private": item.name.startswith('_'),
                                "is_dunder": item.name.startswith('__') and item.name.endswith('__'),
                                "is_test": 'test' in item.name.lower(),
                                "code_snippet": self._extract_function_snippet(content, item)
                            }

                            self.classes[class_key]["methods"].append(item.name)

                # 导入语句
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports[str(file_path.relative_to(self.project_root))].add(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            self.imports[str(file_path.relative_to(self.project_root))].add(f"{node.module}.{alias.name}")

        except Exception as e:
            print(f"⚠️ 分析文件 {file_path} 时出错: {e}")

    def _analyze_calls(self, file_path: Path):
        """分析文件中的函数调用"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            current_file = str(file_path.relative_to(self.project_root))

            for node in ast.walk(tree):
                # 函数调用
                if isinstance(node, ast.Call):
                    call_name = self._extract_call_name(node)
                    if call_name:
                        self.function_calls[current_file].add(call_name)

        except Exception as e:
            print(f"⚠️ 分析调用关系时出错 {file_path}: {e}")

    def _extract_call_name(self, node) -> Optional[str]:
        """提取函数调用名称"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return f"{self._extract_attribute_chain(node.func)}"
        return None

    def _extract_attribute_chain(self, node) -> str:
        """提取属性调用链"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._extract_attribute_chain(node.value)
            return f"{value}.{node.attr}" if value else node.attr
        return ""

    def _find_unused_functions(self) -> List[Dict[str, Any]]:
        """查找未使用的函数"""
        unused = []

        for func_key, func_info in self.function_definitions.items():
            if self._is_function_unused(func_key, func_info):
                # 添加使用分析
                usage_analysis = self._analyze_usage_patterns(func_key, func_info)

                unused.append({
                    "key": func_key,
                    "name": func_info["name"],
                    "file": func_info["file"],
                    "line": func_info["line"],
                    "args": func_info["args"],
                    "docstring": func_info["docstring"],
                    "is_method": func_info["is_method"],
                    "class_name": func_info["class_name"],
                    "is_private": func_info["is_private"],
                    "is_dunder": func_info["is_dunder"],
                    "is_test": func_info["is_test"],
                    "decorators": func_info["decorators"],
                    "code_snippet": func_info["code_snippet"],
                    "usage_analysis": usage_analysis,
                    "confidence": self._calculate_unused_confidence(func_info, usage_analysis)
                })

        # 按置信度排序
        unused.sort(key=lambda x: x["confidence"], reverse=True)
        return unused

    def _is_function_unused(self, func_key: str, func_info: Dict[str, Any]) -> bool:
        """判断函数是否未被使用"""
        func_name = func_info["name"]

        # 跳过特殊函数
        if func_info["is_dunder"]:
            return False

        # 跳过测试函数（除非明确指定要分析）
        if func_info["is_test"]:
            return False

        # 跳过特殊装饰器函数
        special_decorators = {"property", "staticmethod", "classmethod", "setter", "getter"}
        if any(dec in special_decorators for dec in func_info["decorators"]):
            return False

        # 检查是否被调用
        for file_path, calls in self.function_calls.items():
            if func_name in calls:
                # 更精确的检查：确认调用的是这个函数
                if self._is_same_function_called(func_key, func_info, file_path, calls):
                    return False

        return True

    def _is_same_function_called(self, func_key: str, func_info: Dict[str, Any],
                                file_path: str, calls: Set[str]) -> bool:
        """更精确地检查调用的函数是否是当前函数"""
        func_name = func_info["name"]
        func_file = func_info["file"]

        # 如果在同一文件中，简单的名称匹配通常足够
        if file_path == func_file:
            return func_name in calls

        # 如果在不同文件中，需要检查导入关系
        if func_file in self.imports.get(file_path, set()):
            return func_name in calls

        return False

    def _analyze_usage_patterns(self, func_key: str, func_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析函数的使用模式"""
        func_name = func_info["name"]
        func_file = func_info["file"]

        # 查找可能的间接调用
        possible_indirect_calls = []

        # 检查字符串中的调用（如反射调用）
        for file_path, calls in self.function_calls.items():
            for call in calls:
                if func_name in call:
                    possible_indirect_calls.append({
                        "file": file_path,
                        "call": call,
                        "type": "possible_indirect"
                    })

        # 检查装饰器是否可能导致间接使用
        decorator_usage = []
        for decorator in func_info["decorators"]:
            if decorator in ["property", "staticmethod", "classmethod", "setter", "getter"]:
                decorator_usage.append({
                    "decorator": decorator,
                    "reason": "自动调用的特殊方法"
                })

        return {
            "possible_indirect_calls": possible_indirect_calls,
            "decorator_usage": decorator_usage,
            "is_event_handler": self._is_likely_event_handler(func_info),
            "is_callback": self._is_likely_callback(func_info),
            "is_test_helper": self._is_likely_test_helper(func_info)
        }

    def _is_likely_event_handler(self, func_info: Dict[str, Any]) -> bool:
        """判断是否可能是事件处理器"""
        name_patterns = ["on_", "handle_", "process_", "when_"]
        return any(pattern in func_info["name"].lower() for pattern in name_patterns)

    def _is_likely_callback(self, func_info: Dict[str, Any]) -> bool:
        """判断是否可能是回调函数"""
        return "callback" in func_info["name"].lower() or "cb" in func_info["name"].lower()

    def _is_likely_test_helper(self, func_info: Dict[str, Any]) -> bool:
        """判断是否可能是测试辅助函数"""
        return "test" in func_info["file"].lower() or "helper" in func_info["name"].lower()

    def _calculate_unused_confidence(self, func_info: Dict[str, Any], usage_analysis: Dict[str, Any]) -> float:
        """计算未使用的置信度"""
        confidence = 0.8  # 基础置信度

        # 私有函数更可能未使用
        if func_info["is_private"]:
            confidence += 0.1

        # 没有文档字符串的函数更可能未使用
        if not func_info["docstring"]:
            confidence += 0.05

        # 如果有间接调用的可能性，降低置信度
        if usage_analysis["possible_indirect_calls"]:
            confidence -= 0.2

        # 如果是特殊类型的方法，降低置信度
        if usage_analysis["is_event_handler"] or usage_analysis["is_callback"]:
            confidence -= 0.15

        # 如果有装饰器，降低置信度
        if usage_analysis["decorator_usage"]:
            confidence -= 0.1

        return min(max(confidence, 0.0), 1.0)

    def _generate_recommendations(self, unused_functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成处理建议"""
        recommendations = []

        for func in unused_functions[:20]:  # 最多显示20个
            confidence = func["confidence"]

            if confidence > 0.8:
                action = "删除"
                reason = "高置信度未使用"
                priority = "高"
            elif confidence > 0.6:
                action = "人工审查"
                reason = "可能未使用，但需要人工确认"
                priority = "中"
            else:
                action = "保留"
                reason = "可能被间接使用，不建议删除"
                priority = "低"

            recommendations.append({
                "function": f"{func['file']}:{func['line']}:{func['name']}",
                "action": action,
                "reason": reason,
                "priority": priority,
                "confidence": confidence,
                "file": func["file"],
                "line": func["line"],
                "name": func["name"]
            })

        return recommendations

    def _extract_function_snippet(self, content: str, node) -> str:
        """提取函数代码片段"""
        lines = content.split('\n')
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 5

        # 确保不超出文件范围
        end_line = min(end_line, len(lines))

        snippet_lines = lines[start_line:end_line]
        snippet = '\n'.join(snippet_lines)

        # 限制长度
        if len(snippet) > 500:
            snippet = snippet[:500] + "..."

        return snippet.strip()

    def _get_current_time(self) -> str:
        """获取当前时间"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def export_report(self, report: Dict[str, Any], output_file: str = None) -> str:
        """导出分析报告"""
        if not output_file:
            output_file = self.project_root / ".claude" / "skill" / "sysmem" / "unused_code_report.json"

        # 确保目录存在
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📊 分析报告已保存到: {output_file}")
        return str(output_file)

    def format_for_ai_analysis(self, report: Dict[str, Any]) -> str:
        """格式化为AI分析友好的格式"""
        unused_funcs = report["unused_functions"]

        prompt_parts = [
            "# 废弃代码分析请求",
            "",
            f"项目路径: {report['project_root']}",
            f"扫描时间: {report['scan_time']}",
            f"总文件数: {report['total_files']}",
            f"总函数数: {report['total_functions']}",
            f"未使用函数数: {len(unused_funcs)}",
            "",
            "## 发现的可能未使用的函数",
            ""
        ]

        for i, func in enumerate(unused_funcs[:15], 1):  # 最多显示15个
            prompt_parts.extend([
                f"### {i}. {func['name']}",
                f"- **文件**: {func['file']}:{func['line']}",
                f"- **参数**: {', '.join(func['args']) if func['args'] else '无参数'}",
                f"- **类型**: {'类方法' if func['is_method'] else '函数'}" +
                           (f" (类: {func['class_name']})" if func['class_name'] else ""),
                f"- **置信度**: {func['confidence']:.2f}",
                f"- **代码片段**:",
                "```python",
                func['code_snippet'],
                "```",
                ""
            ])

        prompt_parts.extend([
            "## 分析请求",
            "",
            "请分析上述可能未使用的函数，并提供以下信息：",
            "1. 每个函数的实际用途分析",
            "2. 是否可以安全删除的判断",
            "3. 如果不能删除，说明可能的使用场景",
            "4. 重构建议（如有必要）",
            "5. 潜在的依赖关系分析",
            "",
            "请以结构化的方式回复，便于后续处理。"
        ])

        return "\n".join(prompt_parts)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='未使用代码分析器')
    parser.add_argument('directory', nargs='?', default='.', help='项目目录')
    parser.add_argument('--modules', nargs='+', help='指定要分析的模块')
    parser.add_argument('--output', '-o', help='输出报告文件路径')
    parser.add_argument('--ai-prompt', action='store_true', help='生成AI分析提示')
    parser.add_argument('--confidence', type=float, default=0.6, help='置信度阈值')
    parser.add_argument('--max-results', type=int, default=20, help='最大结果数量')

    args = parser.parse_args()

    analyzer = UnusedCodeAnalyzer(args.directory)

    print("🚀 开始未使用代码分析...")
    report = analyzer.scan_project(args.modules)

    # 过滤结果
    filtered_unused = [
        func for func in report["unused_functions"]
        if func["confidence"] >= args.confidence
    ][:args.max_results]

    report["unused_functions"] = filtered_unused
    report["filtered_count"] = len(filtered_unused)

    # 导出报告
    output_file = analyzer.export_report(report, args.output)

    # 生成AI提示
    if args.ai_prompt:
        ai_prompt = analyzer.format_for_ai_analysis(report)

        prompt_file = Path(output_file).with_suffix('.prompt.md')
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(ai_prompt)

        print(f"🤖 AI分析提示已保存到: {prompt_file}")

        # 显示简要信息
        print("\n" + "="*50)
        print("📊 分析结果摘要")
        print("="*50)
        print(f"发现 {len(filtered_unused)} 个高置信度未使用的函数")
        print(f"AI分析提示已生成，可提交给AI进行深度分析")
        print("="*50)
    else:
        print(f"\n📊 分析完成，发现 {len(filtered_unused)} 个未使用的函数")
        print(f"详细报告: {output_file}")


if __name__ == "__main__":
    main()