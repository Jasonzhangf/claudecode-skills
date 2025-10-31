#!/usr/bin/env python3
"""
情节管理器
处理情节规划、大纲管理和故事结构
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class PlotManager:
    """情节管理器，负责情节规划和故事结构管理"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.plot_dir = self.project_path / "settings" / "plot"

        # 确保目录存在
        self.plot_dir.mkdir(parents=True, exist_ok=True)

        # 文件路径
        self.main_plot_file = self.plot_dir / "main_plot.md"
        self.sub_plots_file = self.plot_dir / "sub_plots.md"
        self.timeline_file = self.plot_dir / "timeline.md"
        self.story_structure_file = self.plot_dir / "story_structure.md"

    def create_plot_outline(self, plot_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建情节大纲"""
        try:
            # 验证必需字段
            required_fields = ["story_type", "main_theme", "plot_outline"]
            for field in required_fields:
                if field not in plot_data:
                    return {
                        "status": "error",
                        "message": f"缺少必需字段: {field}"
                    }

            # 创建主情节
            main_plot_content = self._format_main_plot(plot_data)
            self.main_plot_file.write_text(main_plot_content, encoding='utf-8')

            # 创建支线情节
            sub_plots_content = self._format_sub_plots(plot_data)
            self.sub_plots_file.write_text(sub_plots_content, encoding='utf-8')

            # 创建时间线
            timeline_content = self._format_timeline(plot_data)
            self.timeline_file.write_text(timeline_content, encoding='utf-8')

            # 创建故事结构
            structure_content = self._format_story_structure(plot_data)
            self.story_structure_file.write_text(structure_content, encoding='utf-8')

            return {
                "status": "success",
                "message": "情节大纲创建成功",
                "files_created": [
                    str(self.main_plot_file),
                    str(self.sub_plots_file),
                    str(self.timeline_file),
                    str(self.story_structure_file)
                ]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"创建情节大纲失败: {e}"
            }

    def add_plot_point(self, plot_point: Dict[str, Any], plot_type: str = "main") -> Dict[str, Any]:
        """添加情节点"""
        try:
            # 验证必需字段
            required_fields = ["title", "description", "chapter_position"]
            for field in required_fields:
                if field not in plot_point:
                    return {
                        "status": "error",
                        "message": f"缺少必需字段: {field}"
                    }

            # 选择文件
            if plot_type == "main":
                file_path = self.main_plot_file
            else:
                file_path = self.sub_plots_file

            # 读取现有内容
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
            else:
                content = f"# {'主情节' if plot_type == 'main' else '支线情节'}\n\n"

            # 添加新情节点
            new_point = self._format_plot_point(plot_point)
            content += new_point

            # 保存更新后的内容
            file_path.write_text(content, encoding='utf-8')

            return {
                "status": "success",
                "message": f"情节点 {plot_point['title']} 添加成功"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"添加情节点失败: {e}"
            }

    def add_timeline_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """添加时间线事件"""
        try:
            # 验证必需字段
            required_fields = ["time", "event", "related_chapter"]
            for field in required_fields:
                if field not in event_data:
                    return {
                        "status": "error",
                        "message": f"缺少必需字段: {field}"
                    }

            # 读取现有时间线
            if self.timeline_file.exists():
                content = self.timeline_file.read_text(encoding='utf-8')
            else:
                content = "# 故事时间线\n\n"

            # 添加新事件
            new_event = self._format_timeline_event(event_data)
            content += new_event

            # 保存更新后的内容
            self.timeline_file.write_text(content, encoding='utf-8')

            return {
                "status": "success",
                "message": f"时间线事件 {event_data['event']} 添加成功"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"添加时间线事件失败: {e}"
            }

    def get_plot_structure(self) -> Dict[str, Any]:
        """获取情节结构"""
        try:
            structure = {}

            # 读取主情节
            if self.main_plot_file.exists():
                main_content = self.main_plot_file.read_text(encoding='utf-8')
                structure["main_plot"] = self._parse_plot_content(main_content)

            # 读取支线情节
            if self.sub_plots_file.exists():
                sub_content = self.sub_plots_file.read_text(encoding='utf-8')
                structure["sub_plots"] = self._parse_plot_content(sub_content)

            # 读取时间线
            if self.timeline_file.exists():
                timeline_content = self.timeline_file.read_text(encoding='utf-8')
                structure["timeline"] = self._parse_timeline(timeline_content)

            return {
                "status": "success",
                "structure": structure
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取情节结构失败: {e}"
            }

    def generate_chapter_outline(self, chapter_number: int) -> Dict[str, Any]:
        """生成章节大纲"""
        try:
            # 获取情节结构
            plot_structure = self.get_plot_structure()
            if plot_structure["status"] != "success":
                return plot_structure

            # 筛选相关情节点
            relevant_points = []
            all_plots = []

            # 主情节点
            if "main_plot" in plot_structure["structure"]:
                all_plots.extend(plot_structure["structure"]["main_plot"])

            # 支线情节点
            if "sub_plots" in plot_structure["structure"]:
                all_plots.extend(plot_structure["structure"]["sub_plots"])

            # 筛选当前章节的情节点
            for point in all_plots:
                chapter_pos = point.get("chapter_position", "")
                if self._is_chapter_relevant(chapter_pos, chapter_number):
                    relevant_points.append(point)

            # 生成章节大纲
            chapter_outline = self._build_chapter_outline(chapter_number, relevant_points)

            return {
                "status": "success",
                "chapter": chapter_number,
                "outline": chapter_outline,
                "plot_points_count": len(relevant_points)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"生成章节大纲失败: {e}"
            }

    def update_plot_outline(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新情节大纲"""
        try:
            # 读取现有情节数据
            current_structure = self.get_plot_structure()
            if current_structure["status"] != "success":
                return current_structure

            # 更新主情节
            if "story_type" in updates or "main_theme" in updates or "plot_outline" in updates:
                if self.main_plot_file.exists():
                    content = self.main_plot_file.read_text(encoding='utf-8')
                    updated_content = self._update_plot_content(content, updates)
                    self.main_plot_file.write_text(updated_content, encoding='utf-8')

            # 更新故事结构
            if "structure_type" in updates or "act1_end" in updates or "act2_end" in updates:
                if self.story_structure_file.exists():
                    content = self.story_structure_file.read_text(encoding='utf-8')
                    updated_content = self._update_structure_content(content, updates)
                    self.story_structure_file.write_text(updated_content, encoding='utf-8')

            return {
                "status": "success",
                "message": "情节大纲更新成功",
                "updated_fields": list(updates.keys())
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"更新情节大纲失败: {e}"
            }

    def remove_plot_point(self, plot_title: str, plot_type: str = "main") -> Dict[str, Any]:
        """删除情节点"""
        try:
            # 选择文件
            if plot_type == "main":
                file_path = self.main_plot_file
            else:
                file_path = self.sub_plots_file

            if not file_path.exists():
                return {
                    "status": "error",
                    "message": f"{plot_type}情节文件不存在"
                }

            # 读取内容
            content = file_path.read_text(encoding='utf-8')

            # 查找并删除指定情节点
            lines = content.split('\n')
            found = False
            result_lines = []
            skip_section = False

            for line in lines:
                if line.startswith(f"## {plot_title}"):
                    found = True
                    skip_section = True
                    continue
                elif line.startswith("## ") and skip_section:
                    skip_section = False
                    result_lines.append(line)
                elif not skip_section:
                    result_lines.append(line)

            if not found:
                return {
                    "status": "error",
                    "message": f"未找到情节点: {plot_title}"
                }

            # 保存更新后的内容
            file_path.write_text('\n'.join(result_lines), encoding='utf-8')

            return {
                "status": "success",
                "message": f"情节点 {plot_title} 已删除"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"删除情节点失败: {e}"
            }

    def update_timeline_event(self, event_time: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新时间线事件"""
        try:
            if not self.timeline_file.exists():
                return {
                    "status": "error",
                    "message": "时间线文件不存在"
                }

            content = self.timeline_file.read_text(encoding='utf-8')
            lines = content.split('\n')

            updated = False
            for i, line in enumerate(lines):
                if line.startswith(f"### {event_time}"):
                    # 找到事件，更新相关信息
                    for j in range(i, min(i + 10, len(lines))):
                        if "**事件**" in lines[j]:
                            if "event" in updates:
                                lines[j] = f"**事件**: {updates['event']}"
                        elif "**相关章节**" in lines[j]:
                            if "related_chapter" in updates:
                                lines[j] = f"**相关章节**: 第{updates['related_chapter']}章"
                        elif "**参与角色**" in lines[j]:
                            if "characters" in updates:
                                lines[j] = f"**参与角色**: {updates['characters']}"
                        elif "**意义**" in lines[j]:
                            if "significance" in updates:
                                lines[j] = f"**意义**: {updates['significance']}"
                    updated = True
                    break

            if not updated:
                return {
                    "status": "error",
                    "message": f"未找到时间线事件: {event_time}"
                }

            # 保存更新后的内容
            self.timeline_file.write_text('\n'.join(lines), encoding='utf-8')

            return {
                "status": "success",
                "message": f"时间线事件 {event_time} 更新成功"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"更新时间线事件失败: {e}"
            }

    def check_plot_consistency(self) -> Dict[str, Any]:
        """检查情节一致性"""
        try:
            issues = []
            warnings = []

            # 获取情节结构
            plot_structure = self.get_plot_structure()
            if plot_structure["status"] != "success":
                return {
                    "status": "error",
                    "message": "无法获取情节结构"
                }

            # 检查情节连续性
            all_points = []
            if "main_plot" in plot_structure["structure"]:
                all_points.extend(plot_structure["structure"]["main_plot"])

            # 按章节位置排序
            all_points.sort(key=lambda x: self._parse_chapter_position(x.get("chapter_position", "")))

            # 检查逻辑连续性
            for i in range(1, len(all_points)):
                prev_point = all_points[i-1]
                curr_point = all_points[i]

                # 检查章节跳跃是否合理
                prev_chapter = self._parse_chapter_position(prev_point.get("chapter_position", ""))
                curr_chapter = self._parse_chapter_position(curr_point.get("chapter_position", ""))

                if curr_chapter - prev_chapter > 10:
                    warnings.append(f"情节跳跃过大：{prev_point['title']} -> {curr_point['title']}")

            # 检查时间线一致性
            if "timeline" in plot_structure["structure"]:
                timeline = plot_structure["structure"]["timeline"]
                timeline_issues = self._check_timeline_consistency(timeline)
                issues.extend(timeline_issues)

            return {
                "status": "success",
                "is_consistent": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "total_plot_points": len(all_points)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"检查情节一致性失败: {e}"
            }

    def _format_main_plot(self, data: Dict[str, Any]) -> str:
        """格式化主情节"""
        return f"""# 主情节大纲

## 故事类型
{data.get('story_type', '未设定')}

## 主要主题
{data.get('main_theme', '未设定')}

## 故事梗概
{data.get('plot_outline', '待补充...')}

## 主要冲突
{data.get('main_conflict', '待补充...')}

## 情节发展
{data.get('plot_development', '待补充...')}

## 高潮设定
{data.get('climax_setup', '待补充...')}

## 结局安排
{data.get('ending_arrangement', '待补充...')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_sub_plots(self, data: Dict[str, Any]) -> str:
        """格式化支线情节"""
        content = """# 支线情节

## 支线情节列表

"""

        sub_plots = data.get("sub_plots", [])
        for i, subplot in enumerate(sub_plots, 1):
            content += f"""### 支线情节{i}: {subplot.get('name', '未命名')}

**主要角色**: {subplot.get('main_characters', '待定')}
**情节描述**: {subplot.get('description', '待补充...')}
**与主情节关联**: {subplot.get('main_plot_connection', '待补充...')}
**结局安排**: {subplot.get('ending', '待补充...')}

---

"""

        content += f"""
---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return content

    def _format_timeline(self, data: Dict[str, Any]) -> str:
        """格式化时间线"""
        return f"""# 故事时间线

## 时间设定
{data.get('time_setting', '现代时间')}

## 时间流速
{data.get('time_flow', '与现实相同')}

## 重要时间节点

{self._generate_default_timeline()}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_story_structure(self, data: Dict[str, Any]) -> str:
        """格式化故事结构"""
        return f"""# 故事结构

## 结构类型
{data.get('structure_type', '三幕式结构')}

## 第一幕：开端 (1-{data.get('act1_end', 10)}章)
**目标**: 建立世界观，介绍主要角色，设置基本冲突
**重要事件**: {data.get('act1_events', '待补充...')}

## 第二幕：发展 ({data.get('act1_end', 10)+1}-{data.get('act2_end', 30)}章)
**目标**: 冲突升级，角色成长，情节推进
**重要事件**: {data.get('act2_events', '待补充...')}

## 第三幕：高潮与结局 ({data.get('act2_end', 30)+1}章-结束)
**目标**: 达到高潮，解决冲突，收束情节
**重要事件**: {data.get('act3_events', '待补充...')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_plot_point(self, plot_point: Dict[str, Any]) -> str:
        """格式化情节点"""
        return f"""## {plot_point['title']}

**章节位置**: {plot_point['chapter_position']}
**情节描述**: {plot_point['description']}
**类型**: {plot_point.get('type', '关键情节点')}
**相关角色**: {plot_point.get('related_characters', '待定')}
**重要性**: {plot_point.get('importance', '高')}
**后续影响**: {plot_point.get('aftermath', '待补充...')}

---

"""

    def _format_timeline_event(self, event_data: Dict[str, Any]) -> str:
        """格式化时间线事件"""
        return f"""### {event_data['time']}

**事件**: {event_data['event']}
**相关章节**: 第{event_data['related_chapter']}章
**参与角色**: {event_data.get('characters', '待定')}
**意义**: {event_data.get('significance', '待补充...')}

---

"""

    def _generate_default_timeline(self) -> str:
        """生成默认时间线模板"""
        return """#### 故事开始
- **时间**: 故事第1天
- **事件**: 主角登场，基本设定介绍
- **章节**: 第1章

#### 初步冲突
- **时间**: 故事第7天
- **事件**: 第一个主要冲突出现
- **章节**: 第5章

#### 情节转折
- **时间**: 故事第30天
- **事件**: 重大转折，故事走向改变
- **章节**: 第15章

#### 故事高潮
- **时间**: 故事第60天
- **事件**: 最终对决或重大事件
- **章节**: 第30章

#### 故事结局
- **时间**: 故事第75天
- **事件**: 情节收束，结局揭晓
- **章节**: 第35章

"""

    def _parse_plot_content(self, content: str) -> List[Dict[str, Any]]:
        """解析情节内容"""
        plot_points = []
        sections = content.split("## ")

        for section in sections[1:]:  # 跳过第一个空section
            lines = section.strip().split('\n')
            if lines:
                point = {"title": lines[0]}

                for line in lines[1:]:
                    if line.startswith("**章节位置**"):
                        point["chapter_position"] = line.split(":")[1].strip()
                    elif line.startswith("**情节描述**"):
                        point["description"] = line.split(":")[1].strip()
                    elif line.startswith("**类型**"):
                        point["type"] = line.split(":")[1].strip()
                    elif line.startswith("**相关角色**"):
                        point["related_characters"] = line.split(":")[1].strip()

                plot_points.append(point)

        return plot_points

    def _parse_timeline(self, content: str) -> List[Dict[str, Any]]:
        """解析时间线"""
        events = []
        sections = content.split("### ")

        for section in sections[1:]:  # 跳过第一个空section
            lines = section.strip().split('\n')
            if lines:
                event = {"time": lines[0]}

                for line in lines[1:]:
                    if line.startswith("**事件**"):
                        event["event"] = line.split(":")[1].strip()
                    elif line.startswith("**相关章节**"):
                        event["related_chapter"] = line.split(":")[1].strip()
                    elif line.startswith("**参与角色**"):
                        event["characters"] = line.split(":")[1].strip()

                events.append(event)

        return events

    def _parse_chapter_position(self, position_str: str) -> int:
        """解析章节位置"""
        try:
            # 提取数字
            import re
            numbers = re.findall(r'\d+', position_str)
            if numbers:
                return int(numbers[0])
            return 0
        except:
            return 0

    def _is_chapter_relevant(self, position_str: str, current_chapter: int) -> bool:
        """判断情节点是否与当前章节相关"""
        try:
            if not position_str:
                return False

            # 解析位置字符串
            if "第" in position_str and "章" in position_str:
                # 单章节
                chapter_num = self._parse_chapter_position(position_str)
                return abs(chapter_num - current_chapter) <= 2
            elif "-" in position_str:
                # 章节范围
                start, end = map(self._parse_chapter_position, position_str.split("-"))
                return start <= current_chapter <= end
            else:
                # 其他情况
                return False
        except:
            return False

    def _build_chapter_outline(self, chapter_number: int, plot_points: List[Dict[str, Any]]) -> str:
        """构建章节大纲"""
        outline_parts = [
            f"# 第{chapter_number}章大纲",
            "",
            "## 相关情节点",
            ""
        ]

        for point in plot_points:
            outline_parts.append(f"### {point['title']}")
            outline_parts.append(f"**情节**: {point.get('description', '待补充')}")
            outline_parts.append(f"**角色**: {point.get('related_characters', '待定')}")
            outline_parts.append(f"**重要性**: {point.get('importance', '中等')}")
            outline_parts.append("")

        outline_parts.extend([
            "## 写作要点",
            "- 保持与前面章节的连续性",
            "- 突出本章的关键情节点",
            "- 注意角色性格的一致性",
            "- 为后续章节做好铺垫",
            "",
            f"---",
            f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])

        return "\n".join(outline_parts)

    def _check_timeline_consistency(self, timeline: List[Dict[str, Any]]) -> List[str]:
        """检查时间线一致性"""
        issues = []

        # 按时间排序
        sorted_timeline = sorted(timeline, key=lambda x: x.get("time", ""))

        # 检查章节与时间的关系
        for i in range(1, len(sorted_timeline)):
            prev_event = sorted_timeline[i-1]
            curr_event = sorted_timeline[i]

            prev_chapter = self._parse_chapter_position(prev_event.get("related_chapter", ""))
            curr_chapter = self._parse_chapter_position(curr_event.get("related_chapter", ""))

            if curr_chapter < prev_chapter:
                issues.append(f"时间线混乱：{prev_event['event']} (第{prev_chapter}章) -> {curr_event['event']} (第{curr_chapter}章)")

        return issues

    def _update_plot_content(self, content: str, updates: Dict[str, Any]) -> str:
        """更新情节内容"""
        # 简化处理：在现有内容后添加更新信息
        update_section = "\n\n## 更新记录\n\n"
        for key, value in updates.items():
            update_section += f"**{key}**: {value}\n"

        update_section += f"\n*更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return content + update_section

    def _update_structure_content(self, content: str, updates: Dict[str, Any]) -> str:
        """更新故事结构内容"""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "## 结构类型" in line:
                if "structure_type" in updates:
                    lines[i] = f"## 结构类型\n{updates['structure_type']}"
            elif "## 第一幕" in line and "act1_end" in updates:
                lines[i] = f"## 第一幕：开端 (1-{updates['act1_end']}章)"
            elif "## 第二幕" in line and "act2_end" in updates:
                act1_end = updates.get("act1_end", 10)
                lines[i] = f"## 第二幕：发展 ({act1_end + 1}-{updates['act2_end']}章)"
            elif "## 第三幕" in line and "act2_end" in updates:
                act2_end = updates.get("act2_end", 30)
                lines[i] = f"## 第三幕：高潮与结局 ({act2_end + 1}章-结束)"

        return '\n'.join(lines)

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="情节管理器")
    parser.add_argument("--action", choices=["create", "add_point", "add_event", "structure", "outline", "check", "update", "remove_point", "update_event"],
                       required=True, help="操作类型")
    parser.add_argument("--title", help="标题")
    parser.add_argument("--chapter", help="章节位置")
    parser.add_argument("--project-path", default=".", help="项目路径")
    parser.add_argument("--plot-type", choices=["main", "supporting"], default="main", help="情节类型")
    parser.add_argument("--event-time", help="事件时间")
    parser.add_argument("--data", help="更新数据 (JSON格式)")

    args = parser.parse_args()

    pm = PlotManager(args.project_path)

    if args.action == "create":
        sample_data = {
            "story_type": "奇幻冒险",
            "main_theme": "成长与救赎",
            "plot_outline": "一个普通少年的成长故事"
        }
        result = pm.create_plot_outline(sample_data)

    elif args.action == "add_point":
        if not args.title or not args.chapter:
            print("错误: add_point操作需要指定--title和--chapter参数")
            return
        plot_point = {
            "title": args.title,
            "description": "重要的情节点",
            "chapter_position": f"第{args.chapter}章"
        }
        result = pm.add_plot_point(plot_point, args.plot_type)

    elif args.action == "add_event":
        if not args.title or not args.chapter:
            print("错误: add_event操作需要指定--title和--chapter参数")
            return
        event_data = {
            "time": "故事中期",
            "event": args.title,
            "related_chapter": args.chapter
        }
        result = pm.add_timeline_event(event_data)

    elif args.action == "structure":
        result = pm.get_plot_structure()

    elif args.action == "outline":
        if not args.chapter:
            print("错误: outline操作需要指定--chapter参数")
            return
        result = pm.generate_chapter_outline(int(args.chapter))

    elif args.action == "update":
        if not args.data:
            print("错误: update操作需要指定--data参数")
            return
        try:
            updates = json.loads(args.data)
        except json.JSONDecodeError:
            print("错误: data参数必须是有效的JSON格式")
            return
        result = pm.update_plot_outline(updates)

    elif args.action == "remove_point":
        if not args.title:
            print("错误: remove_point操作需要指定--title参数")
            return
        result = pm.remove_plot_point(args.title, args.plot_type)

    elif args.action == "update_event":
        if not args.event_time or not args.data:
            print("错误: update_event操作需要指定--event-time和--data参数")
            return
        try:
            updates = json.loads(args.data)
        except json.JSONDecodeError:
            print("错误: data参数必须是有效的JSON格式")
            return
        result = pm.update_timeline_event(args.event_time, updates)

    elif args.action == "check":
        result = pm.check_plot_consistency()

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()