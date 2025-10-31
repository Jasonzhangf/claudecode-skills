#!/usr/bin/env python3
"""
环境管理器
处理环境设定、场景管理和氛围描述
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class EnvironmentManager:
    """环境管理器，负责环境设定和场景管理"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.environment_dir = self.project_path / "settings" / "environments"

        # 确保目录存在
        self.environment_dir.mkdir(parents=True, exist_ok=True)

        # 文件路径
        self.locations_file = self.environment_dir / "locations.md"
        self.atmosphere_file = self.environment_dir / "atmosphere.md"
        self.scenes_file = self.environment_dir / "scenes.md"

    def create_environment(self, env_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建环境设定"""
        try:
            # 验证必需字段
            required_fields = ["world_type", "main_locations"]
            for field in required_fields:
                if field not in env_data:
                    return {
                        "status": "error",
                        "message": f"缺少必需字段: {field}"
                    }

            # 创建地点设定
            locations_content = self._format_locations_content(env_data)
            self.locations_file.write_text(locations_content, encoding='utf-8')

            # 创建氛围设定
            atmosphere_content = self._format_atmosphere_content(env_data)
            self.atmosphere_file.write_text(atmosphere_content, encoding='utf-8')

            # 创建场景模板
            scenes_content = self._format_scenes_content(env_data)
            self.scenes_file.write_text(scenes_content, encoding='utf-8')

            return {
                "status": "success",
                "message": "环境设定创建成功",
                "files_created": [
                    str(self.locations_file),
                    str(self.atmosphere_file),
                    str(self.scenes_file)
                ]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"创建环境设定失败: {e}"
            }

    def add_location(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """添加地点"""
        try:
            # 验证必需字段
            if "name" not in location_data:
                return {
                    "status": "error",
                    "message": "缺少地点名称"
                }

            # 读取现有地点文件
            if self.locations_file.exists():
                content = self.locations_file.read_text(encoding='utf-8')
            else:
                content = "# 地点设定\n\n"

            # 添加新地点
            new_location = self._format_single_location(location_data)
            content += new_location

            # 保存更新后的内容
            self.locations_file.write_text(content, encoding='utf-8')

            return {
                "status": "success",
                "message": f"地点 {location_data['name']} 添加成功"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"添加地点失败: {e}"
            }

    def add_scene_template(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """添加场景模板"""
        try:
            # 验证必需字段
            required_fields = ["scene_name", "scene_type", "location"]
            for field in required_fields:
                if field not in scene_data:
                    return {
                        "status": "error",
                        "message": f"缺少必需字段: {field}"
                    }

            # 读取现有场景文件
            if self.scenes_file.exists():
                content = self.scenes_file.read_text(encoding='utf-8')
            else:
                content = "# 场景模板\n\n"

            # 添加新场景模板
            new_scene = self._format_scene_template(scene_data)
            content += new_scene

            # 保存更新后的内容
            self.scenes_file.write_text(content, encoding='utf-8')

            return {
                "status": "success",
                "message": f"场景模板 {scene_data['scene_name']} 添加成功"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"添加场景模板失败: {e}"
            }

    def get_locations(self) -> Dict[str, Any]:
        """获取所有地点"""
        try:
            if not self.locations_file.exists():
                return {"status": "success", "locations": []}

            content = self.locations_file.read_text(encoding='utf-8')
            locations = self._parse_locations(content)

            return {
                "status": "success",
                "locations": locations,
                "total": len(locations)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取地点失败: {e}"
            }

    def get_scene_templates(self, scene_type: str = None) -> Dict[str, Any]:
        """获取场景模板"""
        try:
            if not self.scenes_file.exists():
                return {"status": "success", "scenes": []}

            content = self.scenes_file.read_text(encoding='utf-8')
            scenes = self._parse_scene_templates(content)

            if scene_type:
                scenes = [s for s in scenes if s.get("scene_type") == scene_type]

            return {
                "status": "success",
                "scenes": scenes,
                "total": len(scenes)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取场景模板失败: {e}"
            }

    def generate_scene_description(self, location: str, atmosphere_type: str,
                                  additional_elements: List[str] = None) -> Dict[str, Any]:
        """生成场景描述"""
        try:
            # 获取地点信息
            locations_result = self.get_locations()
            location_info = None
            for loc in locations_result.get("locations", []):
                if loc["name"] == location:
                    location_info = loc
                    break

            if not location_info:
                return {
                    "status": "error",
                    "message": f"地点 {location} 不存在"
                }

            # 获取氛围设定
            atmosphere_info = self._get_atmosphere_info(atmosphere_type)

            # 生成场景描述
            scene_description = self._build_scene_description(
                location_info, atmosphere_info, additional_elements or []
            )

            return {
                "status": "success",
                "location": location,
                "atmosphere_type": atmosphere_type,
                "description": scene_description
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"生成场景描述失败: {e}"
            }

    def _format_locations_content(self, data: Dict[str, Any]) -> str:
        """格式化地点内容"""
        content = """# 地点设定

## 世界类型
""" + data.get("world_type", "未设定") + """

## 主要地点

"""

        for location in data.get("main_locations", []):
            content += self._format_single_location(location)

        content += f"""

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return content

    def _format_single_location(self, location_data: Dict[str, Any]) -> str:
        """格式化单个地点"""
        return f"""### {location_data['name']}

**地点类型**: {location_data.get('type', '未知')}
**描述**: {location_data.get('description', '待补充...')}
**特色元素**: {location_data.get('features', '待补充...')}
**氛围特点**: {location_data.get('atmosphere', '待补充...')}
**相关角色**: {location_data.get('related_characters', '待补充...')}
**重要事件**: {location_data.get('important_events', '待补充...')}

---

"""

    def _format_atmosphere_content(self, data: Dict[str, Any]) -> str:
        """格式化氛围内容"""
        return f"""# 氛围设定

## 整体氛围
{data.get('overall_atmosphere', '待补充...')}

## 天气系统
{data.get('weather_system', '待补充...')}

## 时间氛围
{data.get('time_atmosphere', '待补充...')}

## 季节变化
{data.get('seasonal_changes', '待补充...')}

## 情感氛围映射
{data.get('emotional_atmosphere', '待补充...')}

## 特殊氛围效果
{data.get('special_effects', '待补充...')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_scenes_content(self, data: Dict[str, Any]) -> str:
        """格式化场景内容"""
        return f"""# 场景模板

## 场景类型分类
- **对话场景**: 角色之间进行重要对话的场所
- **动作场景**: 发生冲突、追逐、战斗等动作的场所
- **思考场景**: 角色独处、反思、做决定的场所
- **过渡场景**: 连接不同情节的过渡场所

## 常用场景模板

{self._generate_default_scene_templates()}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_scene_template(self, scene_data: Dict[str, Any]) -> str:
        """格式化场景模板"""
        return f"""### {scene_data['scene_name']}

**场景类型**: {scene_data['scene_type']}
**所在地点**: {scene_data['location']}
**适用情节**: {scene_data.get('plot_usage', '待补充...')}
**氛围要求**: {scene_data.get('atmosphere_requirements', '待补充...')}
**必要元素**: {scene_data.get('required_elements', '待补充...')}
**描述模板**:
{scene_data.get('description_template', '待补充...')}

---

"""

    def _generate_default_scene_templates(self) -> str:
        """生成默认场景模板"""
        templates = [
            {
                "name": "初次相遇",
                "type": "对话场景",
                "location": "咖啡馆/公园/图书馆",
                "usage": "角色初次见面，建立第一印象"
            },
            {
                "name": "激烈冲突",
                "type": "对话场景",
                "location": "办公室/家中/公共场所",
                "usage": "角色间发生争执或重大分歧"
            },
            {
                "name": "重要决定",
                "type": "思考场景",
                "location": "卧室/书房/屋顶",
                "usage": "角色做出关键人生决定"
            }
        ]

        content = ""
        for template in templates:
            content += f"""#### {template['name']}

- **场景类型**: {template['type']}
- **推荐地点**: {template['location']}
- **适用情节**: {template['usage']}

"""

        return content

    def _parse_locations(self, content: str) -> List[Dict[str, Any]]:
        """解析地点信息"""
        locations = []
        sections = content.split("### ")

        for section in sections[1:]:  # 跳过第一个空section
            lines = section.strip().split('\n')
            if lines:
                location = {"name": lines[0]}

                for line in lines[1:]:
                    if line.startswith("**地点类型**"):
                        location["type"] = line.split(":")[1].strip()
                    elif line.startswith("**描述**"):
                        location["description"] = line.split(":")[1].strip()
                    elif line.startswith("**特色元素**"):
                        location["features"] = line.split(":")[1].strip()
                    elif line.startswith("**氛围特点**"):
                        location["atmosphere"] = line.split(":")[1].strip()

                locations.append(location)

        return locations

    def _parse_scene_templates(self, content: str) -> List[Dict[str, Any]]:
        """解析场景模板"""
        scenes = []
        sections = content.split("### ")

        for section in sections[1:]:  # 跳过第一个空section
            lines = section.strip().split('\n')
            if lines:
                scene = {"scene_name": lines[0]}

                for line in lines[1:]:
                    if line.startswith("**场景类型**"):
                        scene["scene_type"] = line.split(":")[1].strip()
                    elif line.startswith("**所在地点**"):
                        scene["location"] = line.split(":")[1].strip()
                    elif line.startswith("**适用情节**"):
                        scene["plot_usage"] = line.split(":")[1].strip()

                scenes.append(scene)

        return scenes

    def _get_atmosphere_info(self, atmosphere_type: str) -> Dict[str, Any]:
        """获取氛围信息"""
        atmosphere_types = {
            "peaceful": {
                "keywords": ["宁静", "平和", "安详", "温暖"],
                "colors": ["金色", "柔和", "自然"],
                "sounds": ["鸟鸣", "轻风", "流水"]
            },
            "tense": {
                "keywords": ["紧张", "压抑", "危险", "不安"],
                "colors": ["深色", "阴影", "红色"],
                "sounds": ["心跳", "呼吸", "风声"]
            },
            "mysterious": {
                "keywords": ["神秘", "未知", "幽深", "隐秘"],
                "colors": ["深蓝", "紫色", "黑色"],
                "sounds": ["低语", "回声", "风声"]
            },
            "romantic": {
                "keywords": ["浪漫", "温馨", "甜蜜", "温柔"],
                "colors": ["粉色", "柔和", "温暖"],
                "sounds": ["轻音乐", "心跳", "温柔话语"]
            }
        }

        return atmosphere_types.get(atmosphere_type, {
            "keywords": ["普通"],
            "colors": ["自然"],
            "sounds": ["环境音"]
        })

    def _build_scene_description(self, location: Dict[str, Any],
                               atmosphere: Dict[str, Any],
                               additional_elements: List[str]) -> str:
        """构建场景描述"""
        description_parts = [
            f"**地点**: {location['name']}",
            f"**环境**: {location.get('description', '神秘的地方')}",
            f"**特色**: {location.get('features', '独特的景观')}",
            f"**氛围**: {', '.join(atmosphere['keywords'])}",
            f"**色彩**: {', '.join(atmosphere['colors'])}",
            f"**声音**: {', '.join(atmosphere['sounds'])}"
        ]

        if additional_elements:
            description_parts.append(f"**特殊元素**: {', '.join(additional_elements)}")

        return "\n".join(description_parts)

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="环境管理器")
    parser.add_argument("--action", choices=["create", "add_location", "add_scene", "locations", "scenes", "generate"],
                       required=True, help="操作类型")
    parser.add_argument("--name", help="地点或场景名称")
    parser.add_argument("--type", help="类型")
    parser.add_argument("--location", help="地点")
    parser.add_argument("--atmosphere", help="氛围类型")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    em = EnvironmentManager(args.project_path)

    if args.action == "create":
        sample_data = {
            "world_type": "现代都市",
            "main_locations": [
                {
                    "name": "中央公园",
                    "type": "公园",
                    "description": "城市中心的绿地，环境优美"
                }
            ]
        }
        result = em.create_environment(sample_data)

    elif args.action == "add_location":
        if not args.name:
            print("错误: add_location操作需要指定--name参数")
            return
        location_data = {
            "name": args.name,
            "type": args.type or "未知",
            "description": "新添加的地点"
        }
        result = em.add_location(location_data)

    elif args.action == "add_scene":
        if not args.name or not args.location:
            print("错误: add_scene操作需要指定--name和--location参数")
            return
        scene_data = {
            "scene_name": args.name,
            "scene_type": args.type or "对话场景",
            "location": args.location
        }
        result = em.add_scene_template(scene_data)

    elif args.action == "locations":
        result = em.get_locations()

    elif args.action == "scenes":
        result = em.get_scene_templates(args.type)

    elif args.action == "generate":
        if not args.location or not args.atmosphere:
            print("错误: generate操作需要指定--location和--atmosphere参数")
            return
        result = em.generate_scene_description(args.location, args.atmosphere)

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()