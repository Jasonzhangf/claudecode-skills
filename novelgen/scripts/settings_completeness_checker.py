#!/usr/bin/env python3
"""
设定完整性检查器
检查项目设定的完整性并提供用户引导
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

class SettingsCompletenessChecker:
    """设定完整性检查器"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.settings_dir = self.project_path / "settings"

    def check_all_settings_completeness(self) -> Dict[str, Any]:
        """检查所有设定的完整性"""
        completeness_result = {
            "overall_score": 0,
            "overall_status": "incomplete",
            "category_results": {},
            "missing_items": [],
            "recommendations": [],
            "ready_for_writing": False,
            "check_time": datetime.now().isoformat()
        }

        # 检查各个类别的设定
        categories = [
            ("worldview", self._check_worldview_completeness),
            ("characters", self._check_characters_completeness),
            ("plot", self._check_plot_completeness),
            ("environments", self._check_environments_completeness),
            ("writing_style", self._check_writing_style_completeness)
        ]

        total_score = 0
        max_score = 0

        for category_name, checker_func in categories:
            category_result = checker_func()
            completeness_result["category_results"][category_name] = category_result

            # 累计分数
            category_score = category_result["completeness_score"]
            category_max = category_result["max_score"]
            total_score += category_score
            max_score += category_max

            # 收集缺失项和推荐
            completeness_result["missing_items"].extend(category_result.get("missing_items", []))
            completeness_result["recommendations"].extend(category_result.get("recommendations", []))

        # 计算总体分数
        if max_score > 0:
            completeness_result["overall_score"] = round((total_score / max_score) * 100, 1)

        # 确定总体状态
        completeness_result["overall_status"] = self._determine_status(completeness_result["overall_score"])

        # 判断是否准备好写作
        completeness_result["ready_for_writing"] = self._check_ready_for_writing(completeness_result)

        return completeness_result

    def _check_worldview_completeness(self) -> Dict[str, Any]:
        """检查世界观设定完整性"""
        result = {
            "completeness_score": 0,
            "max_score": 25,
            "missing_items": [],
            "recommendations": [],
            "details": {}
        }

        world_setting_file = self.settings_dir / "worldview" / "world_setting.md"
        world_rules_file = self.settings_dir / "worldview" / "world_rules.md"

        score = 0

        if world_setting_file.exists():
            content = world_setting_file.read_text(encoding='utf-8')
            details = self._analyze_world_setting_content(content)
            result["details"]["world_setting"] = details

            # 检查必需元素
            if details.get("has_basic_info"):
                score += 5
            if details.get("has_geography"):
                score += 5
            if details.get("has_history"):
                score += 5
            if details.get("has_society"):
                score += 5

            if details["completeness"] > 0.6:
                score += 5
            else:
                result["missing_items"].append("世界观基础信息不够完整")
                result["recommendations"].append("补充世界观的时代背景、科技水平、社会结构等基础信息")
        else:
            result["missing_items"].append("缺少世界观设定文件 (world_setting.md)")
            result["recommendations"].append("创建世界观设定，描述世界的基本信息")

        if world_rules_file.exists():
            content = world_rules_file.read_text(encoding='utf-8')
            details = self._analyze_world_rules_content(content)
            result["details"]["world_rules"] = details

            if details.get("has_physics_rules"):
                score += 5
            if details.get("has_magic_tech"):
                score += 5
            if details.get("has_social_rules"):
                score += 5

            if details["completeness"] > 0.6:
                score += 5
            else:
                result["missing_items"].append("世界规则设定不够完整")
                result["recommendations"].append("完善世界的物理规则、魔法/科技系统和社会规则")
        else:
            result["missing_items"].append("缺少世界规则文件 (world_rules.md)")
            result["recommendations"].append("创建世界规则设定，定义世界运行的基本规则")

        result["completeness_score"] = score
        return result

    def _check_characters_completeness(self) -> Dict[str, Any]:
        """检查角色设定完整性"""
        result = {
            "completeness_score": 0,
            "max_score": 25,
            "missing_items": [],
            "recommendations": [],
            "details": {"main_characters": [], "supporting_characters": []}
        }

        main_chars_dir = self.settings_dir / "characters" / "main_characters"
        supporting_chars_dir = self.settings_dir / "characters" / "supporting_characters"

        score = 0
        main_char_count = 0
        supporting_char_count = 0

        # 检查主要角色
        if main_chars_dir.exists():
            for char_file in main_chars_dir.glob("*.md"):
                content = char_file.read_text(encoding='utf-8')
                char_analysis = self._analyze_character_content(content)
                result["details"]["main_characters"].append({
                    "file": char_file.name,
                    "analysis": char_analysis
                })

                if char_analysis["completeness"] > 0.7:
                    score += 8
                    main_char_count += 1
                elif char_analysis["completeness"] > 0.4:
                    score += 5
                    main_char_count += 1
                else:
                    result["missing_items"].append(f"角色 {char_file.stem} 设定不完整")
                    result["recommendations"].append(f"完善角色 {char_file.stem} 的详细设定")

        if main_char_count == 0:
            result["missing_items"].append("缺少主要角色设定")
            result["recommendations"].append("创建至少1个主要角色的详细设定")
        elif main_char_count < 2:
            result["recommendations"].append("建议增加更多主要角色以丰富故事")
        else:
            score += 5  # 角色数量加分

        # 检查配角
        if supporting_chars_dir.exists():
            for char_file in supporting_chars_dir.glob("*.md"):
                content = char_file.read_text(encoding='utf-8')
                char_analysis = self._analyze_character_content(content)
                result["details"]["supporting_characters"].append({
                    "file": char_file.name,
                    "analysis": char_analysis
                })

                if char_analysis["completeness"] > 0.5:
                    score += 3
                    supporting_char_count += 1

        if supporting_char_count == 0:
            result["recommendations"].append("建议添加一些配角设定以丰富故事世界")

        result["completeness_score"] = min(score, 25)
        return result

    def _check_plot_completeness(self) -> Dict[str, Any]:
        """检查情节设定完整性"""
        result = {
            "completeness_score": 0,
            "max_score": 20,
            "missing_items": [],
            "recommendations": [],
            "details": {}
        }

        main_plot_file = self.settings_dir / "plot" / "main_plot.md"
        story_structure_file = self.settings_dir / "plot" / "story_structure.md"

        score = 0

        if main_plot_file.exists():
            content = main_plot_file.read_text(encoding='utf-8')
            plot_analysis = self._analyze_plot_content(content)
            result["details"]["main_plot"] = plot_analysis

            if plot_analysis.get("has_main_storyline"):
                score += 5
            if plot_analysis.get("has_conflict"):
                score += 5
            if plot_analysis.get("has_key_events"):
                score += 5

            if plot_analysis["completeness"] > 0.6:
                score += 5
            else:
                result["missing_items"].append("主要情节设定不够完整")
                result["recommendations"].append("完善故事主线、核心冲突和关键情节节点")
        else:
            result["missing_items"].append("缺少主要情节设定文件 (main_plot.md)")
            result["recommendations"].append("创建主要情节设定，定义故事的主线和冲突")

        if story_structure_file.exists():
            score += 5  # 有结构文件加分
        else:
            result["recommendations"].append("建议创建故事结构设定文件")

        result["completeness_score"] = score
        return result

    def _check_environments_completeness(self) -> Dict[str, Any]:
        """检查环境设定完整性"""
        result = {
            "completeness_score": 0,
            "max_score": 15,
            "missing_items": [],
            "recommendations": [],
            "details": {}
        }

        locations_file = self.settings_dir / "environments" / "key_locations.md"
        score = 0

        if locations_file.exists():
            content = locations_file.read_text(encoding='utf-8')
            env_analysis = self._analyze_environments_content(content)
            result["details"] = env_analysis

            if env_analysis.get("has_main_locations"):
                score += 5
            if env_analysis.get("has_location_details"):
                score += 5
            if env_analysis.get("has_location_relationships"):
                score += 5

            if env_analysis["completeness"] < 0.5:
                result["missing_items"].append("环境地点设定不够详细")
                result["recommendations"].append("补充重要地点的详细描述和地点间的关系")
        else:
            result["missing_items"].append("缺少环境设定文件 (key_locations.md)")
            result["recommendations"].append("创建环境设定，定义故事中的重要地点")

        result["completeness_score"] = score
        return result

    def _check_writing_style_completeness(self) -> Dict[str, Any]:
        """检查写作风格设定完整性"""
        result = {
            "completeness_score": 0,
            "max_score": 15,
            "missing_items": [],
            "recommendations": [],
            "details": {}
        }

        style_file = self.settings_dir / "writing_style" / "narrative_style.md"
        score = 0

        if style_file.exists():
            content = style_file.read_text(encoding='utf-8')
            style_analysis = self._analyze_writing_style_content(content)
            result["details"] = style_analysis

            if style_analysis.get("has_narrative_voice"):
                score += 5
            if style_analysis.get("has_language_style"):
                score += 5
            if style_analysis.get("has_pacing"):
                score += 5

            if style_analysis["completeness"] < 0.5:
                result["missing_items"].append("写作风格设定不够完整")
                result["recommendations"].append("完善叙事视角、语言风格和节奏控制设定")
        else:
            result["missing_items"].append("缺少写作风格设定文件 (narrative_style.md)")
            result["recommendations"].append("创建写作风格设定，定义叙事风格和语言特点")

        result["completeness_score"] = score
        return result

    def _analyze_world_setting_content(self, content: str) -> Dict[str, Any]:
        """分析世界观设定内容"""
        analysis = {
            "completeness": 0.0,
            "has_basic_info": False,
            "has_geography": False,
            "has_history": False,
            "has_society": False,
            "word_count": len(content)
        }

        content_lower = content.lower()

        # 检查基础信息
        basic_patterns = [
            r'世界名称|world name',
            r'时代|时代背景|era',
            r'科技|技术水平|technology',
            r'社会|社会结构|society'
        ]

        for pattern in basic_patterns:
            if re.search(pattern, content_lower):
                analysis["has_basic_info"] = True
                break

        # 检查地理环境
        geo_patterns = [r'地理|地形|气候|geography', r'大陆|海洋|城市|地形']
        if any(re.search(pattern, content_lower) for pattern in geo_patterns):
            analysis["has_geography"] = True

        # 检查历史背景
        history_patterns = [r'历史|背景|历史发展|history', r'事件|时间线|timeline']
        if any(re.search(pattern, content_lower) for pattern in history_patterns):
            analysis["has_history"] = True

        # 检查社会结构
        society_patterns = [r'社会|文化|政治|society', r'制度|法律|宗教|culture']
        if any(re.search(pattern, content_lower) for pattern in society_patterns):
            analysis["has_society"] = True

        # 计算完整性
        true_count = sum([
            analysis["has_basic_info"],
            analysis["has_geography"],
            analysis["has_history"],
            analysis["has_society"]
        ])
        analysis["completeness"] = true_count / 4.0

        return analysis

    def _analyze_world_rules_content(self, content: str) -> Dict[str, Any]:
        """分析世界规则内容"""
        analysis = {
            "completeness": 0.0,
            "has_physics_rules": False,
            "has_magic_tech": False,
            "has_social_rules": False,
            "word_count": len(content)
        }

        content_lower = content.lower()

        # 检查物理规则
        physics_patterns = [r'物理|规则|定律|physics', r'自然|法则|natural']
        if any(re.search(pattern, content_lower) for pattern in physics_patterns):
            analysis["has_physics_rules"] = True

        # 检查魔法/科技系统
        magic_tech_patterns = [r'魔法|magic', r'科技|technology', r'系统|system']
        if any(re.search(pattern, content_lower) for pattern in magic_tech_patterns):
            analysis["has_magic_tech"] = True

        # 检查社会规则
        social_patterns = [r'社会规则|social', r'法律|law', r'道德|moral']
        if any(re.search(pattern, content_lower) for pattern in social_patterns):
            analysis["has_social_rules"] = True

        # 计算完整性
        true_count = sum([
            analysis["has_physics_rules"],
            analysis["has_magic_tech"],
            analysis["has_social_rules"]
        ])
        analysis["completeness"] = true_count / 3.0

        return analysis

    def _analyze_character_content(self, content: str) -> Dict[str, Any]:
        """分析角色设定内容"""
        analysis = {
            "completeness": 0.0,
            "has_basic_info": False,
            "has_appearance": False,
            "has_personality": False,
            "has_background": False,
            "word_count": len(content)
        }

        content_lower = content.lower()

        # 检查基础信息
        basic_patterns = [r'姓名|name', r'年龄|age', r'性别|gender']
        if any(re.search(pattern, content_lower) for pattern in basic_patterns):
            analysis["has_basic_info"] = True

        # 检查外貌描述
        appearance_patterns = [r'外貌|appearance', r'身高|height', r'特征|features']
        if any(re.search(pattern, content_lower) for pattern in appearance_patterns):
            analysis["has_appearance"] = True

        # 检查性格特点
        personality_patterns = [r'性格|personality', r'特点|character', r'习惯|habits']
        if any(re.search(pattern, content_lower) for pattern in personality_patterns):
            analysis["has_personality"] = True

        # 检查背景故事
        background_patterns = [r'背景|background', r'经历|experience', r'历史|history']
        if any(re.search(pattern, content_lower) for pattern in background_patterns):
            analysis["has_background"] = True

        # 计算完整性
        true_count = sum([
            analysis["has_basic_info"],
            analysis["has_appearance"],
            analysis["has_personality"],
            analysis["has_background"]
        ])
        analysis["completeness"] = true_count / 4.0

        return analysis

    def _analyze_plot_content(self, content: str) -> Dict[str, Any]:
        """分析情节设定内容"""
        analysis = {
            "completeness": 0.0,
            "has_main_storyline": False,
            "has_conflict": False,
            "has_key_events": False,
            "word_count": len(content)
        }

        content_lower = content.lower()

        # 检查主线故事
        storyline_patterns = [r'主线|main', r'故事|story', r'情节|plot']
        if any(re.search(pattern, content_lower) for pattern in storyline_patterns):
            analysis["has_main_storyline"] = True

        # 检查冲突
        conflict_patterns = [r'冲突|conflict', r'矛盾|contradiction', r'对手|antagonist']
        if any(re.search(pattern, content_lower) for pattern in conflict_patterns):
            analysis["has_conflict"] = True

        # 检查关键事件
        events_patterns = [r'事件|events', r'转折|turning', r'高潮|climax', r'结局|ending']
        if any(re.search(pattern, content_lower) for pattern in events_patterns):
            analysis["has_key_events"] = True

        # 计算完整性
        true_count = sum([
            analysis["has_main_storyline"],
            analysis["has_conflict"],
            analysis["has_key_events"]
        ])
        analysis["completeness"] = true_count / 3.0

        return analysis

    def _analyze_environments_content(self, content: str) -> Dict[str, Any]:
        """分析环境设定内容"""
        analysis = {
            "completeness": 0.0,
            "has_main_locations": False,
            "has_location_details": False,
            "has_location_relationships": False,
            "word_count": len(content)
        }

        content_lower = content.lower()

        # 检查主要地点
        location_patterns = [r'地点|location', r'场景|scene', r'场所|place']
        if any(re.search(pattern, content_lower) for pattern in location_patterns):
            analysis["has_main_locations"] = True

        # 检查地点细节
        detail_patterns = [r'描述|description', r'特点|features', r'环境|environment']
        if any(re.search(pattern, content_lower) for pattern in detail_patterns):
            analysis["has_location_details"] = True

        # 检查地点关系
        relationship_patterns = [r'关系|relationship', r'连接|connection', r'距离|distance']
        if any(re.search(pattern, content_lower) for pattern in relationship_patterns):
            analysis["has_location_relationships"] = True

        # 计算完整性
        true_count = sum([
            analysis["has_main_locations"],
            analysis["has_location_details"],
            analysis["has_location_relationships"]
        ])
        analysis["completeness"] = true_count / 3.0

        return analysis

    def _analyze_writing_style_content(self, content: str) -> Dict[str, Any]:
        """分析写作风格内容"""
        analysis = {
            "completeness": 0.0,
            "has_narrative_voice": False,
            "has_language_style": False,
            "has_pacing": False,
            "word_count": len(content)
        }

        content_lower = content.lower()

        # 检查叙事视角
        voice_patterns = [r'视角|perspective', r'人称|person', r'叙述|narrative']
        if any(re.search(pattern, content_lower) for pattern in voice_patterns):
            analysis["has_narrative_voice"] = True

        # 检查语言风格
        style_patterns = [r'语言|language', r'风格|style', r'词汇|vocabulary']
        if any(re.search(pattern, content_lower) for pattern in style_patterns):
            analysis["has_language_style"] = True

        # 检查节奏控制
        pacing_patterns = [r'节奏|pacing', r'速度|speed', r'密度|density']
        if any(re.search(pattern, content_lower) for pattern in pacing_patterns):
            analysis["has_pacing"] = True

        # 计算完整性
        true_count = sum([
            analysis["has_narrative_voice"],
            analysis["has_language_style"],
            analysis["has_pacing"]
        ])
        analysis["completeness"] = true_count / 3.0

        return analysis

    def _determine_status(self, score: float) -> str:
        """根据分数确定状态"""
        if score >= 80:
            return "complete"
        elif score >= 60:
            return "mostly_complete"
        elif score >= 40:
            return "partial"
        else:
            return "incomplete"

    def _check_ready_for_writing(self, completeness_result: Dict[str, Any]) -> bool:
        """检查是否准备好开始写作"""
        # 基本要求：总体完成度达到60%，且主要类别都有基础设定
        if completeness_result["overall_score"] < 60:
            return False

        # 必需的类别：世界观、角色、情节
        required_categories = ["worldview", "characters", "plot"]
        for category in required_categories:
            category_result = completeness_result["category_results"].get(category, {})
            if category_result.get("completeness_score", 0) < 10:  # 至少有一些基础内容
                return False

        # 检查关键缺失项
        critical_missing = [
            "缺少主要角色设定",
            "缺少世界观设定文件",
            "缺少主要情节设定文件"
        ]
        for missing_item in critical_missing:
            if missing_item in completeness_result["missing_items"]:
                return False

        return True

    def generate_user_guidance(self, completeness_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成用户引导"""
        guidance = {
            "ready_for_writing": completeness_result["ready_for_writing"],
            "overall_status": completeness_result["overall_status"],
            "priority_actions": [],
            "suggested_workflow": [],
            "completion_tips": []
        }

        # 确定优先行动
        if not completeness_result["ready_for_writing"]:
            # 添加必需的缺失项
            critical_missing = [
                "缺少主要角色设定",
                "缺少世界观设定文件",
                "缺少主要情节设定文件",
                "缺少环境设定文件",
                "缺少写作风格设定文件"
            ]

            for missing in critical_missing:
                if missing in completeness_result["missing_items"]:
                    guidance["priority_actions"].append({
                        "action": "create_missing_file",
                        "description": missing,
                        "priority": "high"
                    })

            # 添加完善建议
            for recommendation in completeness_result["recommendations"][:5]:
                guidance["priority_actions"].append({
                    "action": "improve_existing_content",
                    "description": recommendation,
                    "priority": "medium"
                })

        # 生成建议工作流程
        guidance["suggested_workflow"] = [
            {
                "step": 1,
                "title": "完善基础设定",
                "description": "确保世界观、主要角色、情节设定都有基础内容",
                "estimated_time": "30-60分钟"
            },
            {
                "step": 2,
                "title": "细化角色设定",
                "description": "为主角和配角添加详细的外貌、性格、背景设定",
                "estimated_time": "20-40分钟"
            },
            {
                "step": 3,
                "title": "完善环境设定",
                "description": "定义故事中的重要地点和环境描述",
                "estimated_time": "15-30分钟"
            },
            {
                "step": 4,
                "title": "确定写作风格",
                "description": "设定叙事视角、语言风格和节奏控制",
                "estimated_time": "10-20分钟"
            }
        ]

        # 添加完成技巧
        guidance["completion_tips"] = [
            "每个角色至少需要：姓名、年龄、外貌、性格、背景故事",
            "世界观设定应包含：时代背景、科技水平、社会结构、地理环境",
            "情节设定需要：主线故事、核心冲突、关键转折点、结局方向",
            "写作风格建议确定：叙事视角（第一/第三人称）、语言风格、整体节奏"
        ]

        return guidance

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="设定完整性检查器")
    parser.add_argument("--project-path", default=".", help="项目路径")
    parser.add_argument("--format", choices=["json", "readable"], default="readable", help="输出格式")

    args = parser.parse_args()

    checker = SettingsCompletenessChecker(args.project_path)
    result = checker.check_all_settings_completeness()

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 可读格式输出
        print("📊 设定完整性检查报告")
        print("=" * 40)
        print(f"总体完成度: {result['overall_score']}%")
        print(f"总体状态: {result['overall_status']}")
        print(f"准备好写作: {'是' if result['ready_for_writing'] else '否'}")
        print()

        if result['missing_items']:
            print("❌ 缺失项目:")
            for item in result['missing_items']:
                print(f"  • {item}")
            print()

        if result['recommendations']:
            print("💡 改进建议:")
            for rec in result['recommendations']:
                print(f"  • {rec}")
            print()

        # 生成用户引导
        guidance = checker.generate_user_guidance(result)
        if guidance['priority_actions']:
            print("🎯 优先行动:")
            for action in guidance['priority_actions']:
                priority_icon = "🔴" if action['priority'] == 'high' else "🟡"
                print(f"  {priority_icon} {action['description']}")
            print()

if __name__ == "__main__":
    main()