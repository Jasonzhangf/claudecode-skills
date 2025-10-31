#!/usr/bin/env python3
"""
世界观管理器
处理世界观的创建、编辑和验证
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class WorldBuilder:
    """世界观管理器，负责世界观的创建和维护"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.worldview_dir = self.project_path / "settings" / "worldview"

        # 确保目录存在
        self.worldview_dir.mkdir(parents=True, exist_ok=True)

        # 世界观文件路径
        self.world_setting_file = self.worldview_dir / "world_setting.md"
        self.world_rules_file = self.worldview_dir / "world_rules.md"

    def create_worldview(self, worldview_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建世界观"""
        try:
            # 验证必需字段
            required_fields = ["world_name", "era", "technology_level", "magic_system"]
            for field in required_fields:
                if field not in worldview_data:
                    return {
                        "status": "error",
                        "message": f"缺少必需字段: {field}"
                    }

            # 格式化世界观内容
            world_setting_content = self._format_world_setting(worldview_data)
            world_rules_content = self._format_world_rules(worldview_data)

            # 保存文件
            self.world_setting_file.write_text(world_setting_content, encoding='utf-8')
            self.world_rules_file.write_text(world_rules_content, encoding='utf-8')

            return {
                "status": "success",
                "message": "世界观创建成功",
                "world_name": worldview_data["world_name"],
                "files_created": [str(self.world_setting_file), str(self.world_rules_file)]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"创建世界观失败: {e}"
            }

    def load_worldview(self) -> Dict[str, Any]:
        """加载世界观"""
        try:
            if not self.world_setting_file.exists():
                return {"status": "error", "message": "世界观文件不存在"}

            # 读取世界观设定
            setting_content = self.world_setting_file.read_text(encoding='utf-8')

            # 读取世界规则
            rules_content = ""
            if self.world_rules_file.exists():
                rules_content = self.world_rules_file.read_text(encoding='utf-8')

            return {
                "status": "success",
                "setting_content": setting_content,
                "rules_content": rules_content,
                "files": {
                    "setting": str(self.world_setting_file),
                    "rules": str(self.world_rules_file) if self.world_rules_file.exists() else None
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"加载世界观失败: {e}"
            }

    def update_worldview(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新世界观"""
        try:
            # 加载现有世界观
            current_data = self.load_worldview()
            if current_data["status"] != "success":
                return current_data

            # 解析现有内容并更新
            updated_data = self._parse_and_update_worldview(current_data, updates)

            # 重新格式化并保存
            world_setting_content = self._format_world_setting(updated_data)
            world_rules_content = self._format_world_rules(updated_data)

            self.world_setting_file.write_text(world_setting_content, encoding='utf-8')
            self.world_rules_file.write_text(world_rules_content, encoding='utf-8')

            return {
                "status": "success",
                "message": "世界观更新成功",
                "updated_fields": list(updates.keys())
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"更新世界观失败: {e}"
            }

    def validate_worldview(self) -> Dict[str, Any]:
        """验证世界观完整性"""
        try:
            issues = []
            warnings = []

            if not self.world_setting_file.exists():
                issues.append("世界观设定文件不存在")
                return {"status": "error", "issues": issues}

            content = self.world_setting_file.read_text(encoding='utf-8')

            # 检查必需元素
            required_elements = ["世界名称", "时代背景", "技术水平"]
            for element in required_elements:
                if element not in content:
                    issues.append(f"缺少{element}")

            # 检查推荐元素
            recommended_elements = ["魔法系统", "社会结构", "地理环境"]
            for element in recommended_elements:
                if element not in content:
                    warnings.append(f"建议添加{element}")

            # 检查内容长度
            if len(content) < 500:
                warnings.append("世界观描述较为简短，建议增加更多细节")

            return {
                "status": "success",
                "is_valid": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "content_length": len(content)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"验证世界观失败: {e}"
            }

    def _format_world_setting(self, data: Dict[str, Any]) -> str:
        """格式化世界观设定内容"""
        return f"""# 世界观设定

## 基本信息
- **世界名称**: {data.get('world_name', '未设定')}
- **时代背景**: {data.get('era', '未设定')}
- **技术水平**: {data.get('technology_level', '未设定')}
- **世界类型**: {data.get('world_type', '未设定')}

## 地理环境
{data.get('geography', '待补充...')}

## 社会结构
{data.get('society', '待补充...')}

## 魔法系统
{data.get('magic_system', '待补充...')}

## 历史背景
{data.get('history', '待补充...')}

## 文化特色
{data.get('culture', '待补充...')}

## 经济体系
{data.get('economy', '待补充...')}

## 宗教信仰
{data.get('religion', '待补充...')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_world_rules(self, data: Dict[str, Any]) -> str:
        """格式化世界规则内容"""
        return f"""# 世界规则

## 物理法则
{data.get('physical_laws', '遵循现实世界物理法则')}

## 魔法规则
{data.get('magic_rules', '待补充...')}

## 社会规则
{data.get('social_rules', '待补充...')}

## 特殊限制
{data.get('limitations', '待补充...')}

## 世界观一致性要求
{data.get('consistency_rules', '待补充...')}

## 时间流速
{data.get('time_flow', '与现实世界相同')}

## 空间结构
{data.get('space_structure', '待补充...')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def apply_extracted_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """应用AI提取的世界观数据"""
        try:
            # 检查世界观是否已存在
            existing_worldview = self.load_worldview()

            if existing_worldview["status"] == "success":
                # 世界观已存在，更新世界观
                update_result = self.intelligent_update_worldview(extracted_data)
                return update_result
            else:
                # 世界观不存在，创建新世界观
                create_result = self.create_worldview(extracted_data)
                return create_result

        except Exception as e:
            return {
                "status": "error",
                "message": f"应用提取数据失败: {e}"
            }

    def intelligent_update_worldview(self, new_data: Dict[str, Any],
                                   update_mode: str = "auto") -> Dict[str, Any]:
        """智能更新世界观信息"""
        try:
            # 读取现有世界观文件
            if not self.world_setting_file.exists():
                return {
                    "status": "error",
                    "message": "世界观文件不存在"
                }

            existing_content = self.world_setting_file.read_text(encoding='utf-8')

            # 解析现有内容
            parsed_existing = self._parse_worldview_content(existing_content)

            # 分析差异并选择更新策略
            if update_mode == "auto":
                update_mode = self._determine_worldview_update_strategy(parsed_existing, new_data)

            # 执行智能合并
            merged_content = self._intelligent_merge_worldview_content(
                parsed_existing, new_data, update_mode
            )

            # 重新格式化内容
            formatted_content = self._format_world_setting(merged_content)

            # 保存更新后的内容
            self.world_setting_file.write_text(formatted_content, encoding='utf-8')

            return {
                "status": "success",
                "message": "世界观更新成功",
                "update_mode": update_mode,
                "updated_fields": list(new_data.keys())
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"智能更新世界观失败: {e}"
            }

    def _parse_worldview_content(self, content: str) -> Dict[str, Any]:
        """解析世界观内容为结构化数据"""
        parsed = {
            "world_name": "",
            "era": "",
            "technology_level": "",
            "world_type": "",
            "geography": "",
            "society": "",
            "magic_system": "",
            "history": "",
            "culture": "",
            "economy": "",
            "religion": "",
            "physical_laws": "",
            "magic_rules": "",
            "social_rules": "",
            "limitations": "",
            "consistency_rules": "",
            "time_flow": "",
            "space_structure": ""
        }

        lines = content.split('\n')
        current_section = ""
        section_content = []

        for line in lines:
            line = line.strip()
            if line.startswith("## "):
                if current_section and section_content:
                    parsed[current_section] = "\n".join(section_content).strip()
                current_section = line[3:].strip()
                section_content = []
            elif line.startswith("- **") and current_section == "基本信息":
                # 解析基本信息
                if "：" in line:
                    key, value = line.split("：", 1)
                    key = key.replace("- **", "").replace("**", "").strip()
                    value = value.strip()
                    # 映射到标准字段名
                    field_mapping = {
                        "世界名称": "world_name",
                        "时代背景": "era",
                        "技术水平": "technology_level",
                        "世界类型": "world_type"
                    }
                    standard_key = field_mapping.get(key, key.lower().replace(" ", "_"))
                    if standard_key in parsed:
                        parsed[standard_key] = value
            elif line and not line.startswith("-") and not line.startswith("*") and not line.startswith("#"):
                section_content.append(line)

        # 处理最后一个section
        if current_section and section_content:
            # 映射section名称到标准字段名
            section_mapping = {
                "地理环境": "geography",
                "社会结构": "society",
                "魔法系统": "magic_system",
                "历史背景": "history",
                "文化特色": "culture",
                "经济体系": "economy",
                "宗教信仰": "religion",
                "物理法则": "physical_laws",
                "魔法规则": "magic_rules",
                "社会规则": "social_rules",
                "特殊限制": "limitations",
                "世界观一致性要求": "consistency_rules",
                "时间流速": "time_flow",
                "空间结构": "space_structure"
            }
            standard_key = section_mapping.get(current_section, current_section.lower().replace(" ", "_"))
            if standard_key in parsed:
                parsed[standard_key] = "\n".join(section_content).strip()

        return parsed

    def _determine_worldview_update_strategy(self, existing: Dict[str, Any], new_data: Dict[str, Any]) -> str:
        """确定世界观更新策略"""
        # 简单的策略：如果新数据包含核心字段，使用覆盖；否则使用追加
        core_fields = ["world_name", "era", "technology_level"]
        has_core_updates = any(field in new_data for field in core_fields)

        if has_core_updates:
            return "覆盖"
        else:
            return "追加"

    def _intelligent_merge_worldview_content(self, existing: Dict[str, Any], new_data: Dict[str, Any],
                                          update_mode: str) -> Dict[str, Any]:
        """智能合并世界观内容"""
        merged = existing.copy()

        if update_mode == "覆盖":
            # 覆盖模式：新数据覆盖对应字段
            for key, value in new_data.items():
                if key in merged:
                    merged[key] = str(value)
        else:
            # 追加模式：在现有内容基础上追加
            for key, value in new_data.items():
                if key in merged and merged[key]:
                    merged[key] = merged[key] + "\n\n" + str(value)
                elif key in merged:
                    merged[key] = str(value)

        return merged

    def _parse_and_update_worldview(self, current_data: Dict[str, Any],
                                   updates: Dict[str, Any]) -> Dict[str, Any]:
        """解析现有世界观并应用更新"""
        # 这里简化处理，实际应该解析markdown内容
        # 返回合并后的数据
        current_data["setting_content"]  # 现有内容
        current_data["rules_content"]    # 现有规则

        # 构建更新的数据结构
        updated = {
            "world_name": updates.get("world_name", "未设定"),
            "era": updates.get("era", "未设定"),
            "technology_level": updates.get("technology_level", "未设定"),
            "world_type": updates.get("world_type", "未设定"),
            "geography": updates.get("geography", "待补充..."),
            "society": updates.get("society", "待补充..."),
            "magic_system": updates.get("magic_system", "待补充..."),
            "history": updates.get("history", "待补充..."),
            "culture": updates.get("culture", "待补充..."),
            "economy": updates.get("economy", "待补充..."),
            "religion": updates.get("religion", "待补充..."),
            "physical_laws": updates.get("physical_laws", "遵循现实世界物理法则"),
            "magic_rules": updates.get("magic_rules", "待补充..."),
            "social_rules": updates.get("social_rules", "待补充..."),
            "limitations": updates.get("limitations", "待补充..."),
            "consistency_rules": updates.get("consistency_rules", "待补充..."),
            "time_flow": updates.get("time_flow", "与现实世界相同"),
            "space_structure": updates.get("space_structure", "待补充...")
        }

        return updated

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="世界观管理器")
    parser.add_argument("--action", choices=["create", "load", "update", "validate"],
                       required=True, help="操作类型")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    wb = WorldBuilder(args.project_path)

    if args.action == "create":
        # 示例数据
        sample_data = {
            "world_name": "艾泽拉斯",
            "era": "魔法中世纪",
            "technology_level": "低魔法科技",
            "world_type": "奇幻世界"
        }
        result = wb.create_worldview(sample_data)

    elif args.action == "load":
        result = wb.load_worldview()

    elif args.action == "update":
        # 示例更新数据
        updates = {
            "magic_system": "元素魔法系统，包含火、水、土、风四种基本元素"
        }
        result = wb.update_worldview(updates)

    elif args.action == "validate":
        result = wb.validate_worldview()

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()