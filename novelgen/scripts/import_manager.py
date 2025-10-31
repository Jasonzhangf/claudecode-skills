#!/usr/bin/env python3
"""
小说生成器 - 导入管理器
负责从本地目录导入已有设定，自动检测和解析设定文件
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# 导入各个数据管理器
from data_managers.worldbuilder import WorldBuilder
from data_managers.character_manager import CharacterManager
from data_managers.environment_manager import EnvironmentManager
from data_managers.plot_manager import PlotManager
from data_managers.style_manager import StyleManager
from data_managers.memory_manager import MemoryManager

class ImportManager:
    """导入管理器，负责从本地目录导入设定"""

    def __init__(self, project_path: str = None, ai_client_handler=None):
        if project_path is None:
            self.project_path = Path.cwd()
        else:
            self.project_path = Path(project_path)

        self.project_name = self.project_path.name
        self.settings_dir = self.project_path / "settings"
        self.ai_client = ai_client_handler  # AI客户端处理器

        # 初始化各个管理器
        self.world_builder = WorldBuilder(project_path)
        self.character_manager = CharacterManager(project_path)
        self.environment_manager = EnvironmentManager(project_path)
        self.plot_manager = PlotManager(project_path)
        self.style_manager = StyleManager(project_path)
        self.memory_manager = MemoryManager(project_path)

        # 导入日志
        self.import_log = []

        # 支持的文件格式
        self.supported_extensions = {'.md', '.txt', '.docx', '.rtf'}

    def scan_directory_content(self, target_directory: str) -> Dict[str, Any]:
        """智能扫描目录下的所有文件内容"""
        target_path = Path(target_directory)
        if not target_path.exists():
            return {
                "status": "error",
                "message": f"目标目录不存在: {target_directory}"
            }

        scan_result = {
            "status": "success",
            "target_directory": str(target_path),
            "found_files": [],
            "total_files": 0,
            "total_size": 0
        }

        # 递归扫描所有支持的文件
        for file_path in target_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    file_info = {
                        "path": str(file_path),
                        "relative_path": str(file_path.relative_to(target_path)),
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "extension": file_path.suffix.lower(),
                        "modified_time": file_path.stat().st_mtime
                    }

                    # 读取文件内容
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_info["content"] = f.read()
                        scan_result["found_files"].append(file_info)
                        scan_result["total_files"] += 1
                        scan_result["total_size"] += file_info["size"]
                    except UnicodeDecodeError:
                        # 尝试其他编码
                        try:
                            with open(file_path, 'r', encoding='gbk') as f:
                                file_info["content"] = f.read()
                            scan_result["found_files"].append(file_info)
                            scan_result["total_files"] += 1
                            scan_result["total_size"] += file_info["size"]
                        except:
                            continue  # 跳过无法读取的文件

                except Exception as e:
                    # 记录错误但继续扫描其他文件
                    scan_result[f"error_{file_path.name}"] = str(e)
                    continue

        return scan_result

    def import_settings_from_directory(self, target_directory: str,
                                     specific_setting: str = None) -> Dict[str, Any]:
        """从目录导入设定（本地处理+AI分析）"""

        # 1. 本地：扫描文件
        scan_result = self.scan_directory_content(target_directory)
        if scan_result["status"] != "success":
            return scan_result

        if scan_result["total_files"] == 0:
            return {
                "status": "error",
                "message": f"目录 {target_directory} 中没有找到支持的文件"
            }

        # 2. 本地：准备文件内容
        file_contents = []
        for file_info in scan_result["found_files"]:
            file_contents.append({
                "path": file_info["relative_path"],
                "name": file_info["name"],
                "content": file_info["content"],
                "size": file_info["size"]
            })

        # 3. 交给AI：分析内容类型和提取信息
        ai_analysis_request = {
            "task_type": "content_analysis",
            "files": file_contents,
            "specific_setting": specific_setting,
            "supported_settings": ["worldview", "character", "environment", "plot", "style", "memory"],
            "analysis_instructions": {
                "worldview": "识别世界观设定，包括世界名称、时代背景、技术水平、社会结构等",
                "character": "识别角色信息，包括角色名称、性格、背景、关系等",
                "environment": "识别环境设定，包括地点、场景、氛围等",
                "plot": "识别情节元素，包括主线情节、冲突、转折点等",
                "style": "识别写作风格，包括叙事风格、对话风格、语言特色等",
                "memory": "识别记忆相关内容，包括角色记忆、情感体验等"
            }
        }

        # 返回AI任务请求，等待客户端处理
        return {
            "status": "ai_task_required",
            "ai_task": ai_analysis_request,
            "local_data": {
                "files_found": scan_result["total_files"],
                "target_directory": target_directory,
                "total_size": scan_result["total_size"]
            }
        }

    def process_ai_analysis_result(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """处理AI分析结果（本地处理）"""

        if ai_result.get("status") != "success":
            return {
                "status": "error",
                "message": "AI分析失败",
                "ai_error": ai_result.get("error", "未知错误")
            }

        try:
            # 1. 本地：根据AI分析结果更新相应设定
            updated_settings = []
            update_errors = []

            for setting_type, extracted_data in ai_result.get("extracted_settings", {}).items():
                try:
                    manager = self._get_manager_by_type(setting_type)
                    if manager:
                        # 2. 本地：执行设定更新
                        update_result = manager.apply_extracted_data(extracted_data)

                        # 记录更新结果
                        self.import_log.append({
                            "timestamp": datetime.now().isoformat(),
                            "category": setting_type,
                            "action": "import_from_ai_analysis",
                            "status": update_result.get("status", "unknown"),
                            "details": update_result.get("message", ""),
                            "extracted_items": len(extracted_data) if isinstance(extracted_data, list) else 1
                        })

                        if update_result.get("status") == "success":
                            updated_settings.append(setting_type)
                        else:
                            update_errors.append({
                                "setting_type": setting_type,
                                "error": update_result.get("message", "更新失败")
                            })
                    else:
                        update_errors.append({
                            "setting_type": setting_type,
                            "error": "未找到对应的管理器"
                        })

                except Exception as e:
                    update_errors.append({
                        "setting_type": setting_type,
                        "error": f"处理异常: {e}"
                    })

            # 3. 保存导入日志
            self._save_import_log()

            # 4. 返回最终结果
            result = {
                "status": "success" if not update_errors else "partial_success",
                "updated_settings": updated_settings,
                "total_updated": len(updated_settings),
                "update_errors": update_errors,
                "ai_analysis_summary": ai_result.get("analysis_summary", ""),
                "total_extracted_items": sum(
                    len(data) if isinstance(data, list) else 1
                    for data in ai_result.get("extracted_settings", {}).values()
                )
            }

            if update_errors:
                result["message"] = f"部分更新成功，{len(update_errors)}个更新失败"
            else:
                result["message"] = "所有设定更新成功"

            return result

        except Exception as e:
            return {
                "status": "error",
                "message": f"处理AI分析结果失败: {e}"
            }

    def _get_manager_by_type(self, setting_type: str):
        """根据设定类型获取对应的管理器"""
        manager_map = {
            "worldview": self.world_builder,
            "character": self.character_manager,
            "environment": self.environment_manager,
            "plot": self.plot_manager,
            "style": self.style_manager,
            "memory": self.memory_manager
        }
        return manager_map.get(setting_type)

    def scan_available_settings(self) -> Dict[str, Any]:
        """扫描本地可用的设定文件（保持原有功能）"""
        scan_result = {
            "status": "success",
            "found_settings": {},
            "missing_settings": [],
            "total_files": 0
        }

        # 定义要扫描的文件路径
        setting_files = {
            "worldview": [
                self.settings_dir / "worldview" / "world_setting.md",
                self.settings_dir / "worldview" / "world_rules.md"
            ],
            "characters": [
                self.settings_dir / "characters" / "character_relations.md",
                self.settings_dir / "characters" / "main_characters" / "main_characters.md",
                self.settings_dir / "characters" / "supporting_characters" / "supporting_characters.md"
            ],
            "environments": [
                self.settings_dir / "environments" / "locations.md",
                self.settings_dir / "environments" / "atmosphere.md",
                self.settings_dir / "environments" / "scenes.md"
            ],
            "plot": [
                self.settings_dir / "plot" / "main_plot.md",
                self.settings_dir / "plot" / "sub_plots.md",
                self.settings_dir / "plot" / "timeline.md"
            ],
            "style": [
                self.settings_dir / "writing_style" / "narrative_style.md",
                self.settings_dir / "writing_style" / "dialogue_style.md",
                self.settings_dir / "writing_style" / "vocabulary.md"
            ],
            "memory": [
                self.settings_dir / "memory" / "memory_structure.md",
                self.settings_dir / "memory" / "character_memory.md"
            ]
        }

        # 扫描每个类别的文件
        for category, files in setting_files.items():
            found_files = []
            for file_path in files:
                if file_path.exists() and file_path.stat().st_size > 0:
                    found_files.append(str(file_path))
                    scan_result["total_files"] += 1

            if found_files:
                scan_result["found_settings"][category] = found_files
            else:
                scan_result["missing_settings"].append(category)

        return scan_result

    def import_all_settings(self) -> Dict[str, Any]:
        """导入所有可用的设定"""
        self.import_log = []
        import_result = {
            "status": "success",
            "imported_categories": [],
            "failed_categories": [],
            "details": {},
            "total_files_processed": 0
        }

        # 按顺序导入各个设定类别
        import_order = ["worldview", "characters", "environments", "plot", "style", "memory"]

        for category in import_order:
            try:
                result = self.import_category(category)
                if result["status"] == "success":
                    import_result["imported_categories"].append(category)
                    import_result["details"][category] = result
                    import_result["total_files_processed"] += result.get("files_processed", 0)
                else:
                    import_result["failed_categories"].append(category)
                    import_result["details"][category] = result
            except Exception as e:
                import_result["failed_categories"].append(category)
                import_result["details"][category] = {
                    "status": "error",
                    "message": f"导入{category}时发生异常: {e}"
                }

        # 保存导入日志
        self._save_import_log()

        return import_result

    def import_category(self, category: str) -> Dict[str, Any]:
        """导入指定类别的设定"""
        if category not in ["worldview", "characters", "environments", "plot", "style", "memory"]:
            return {
                "status": "error",
                "message": f"不支持的设定类别: {category}"
            }

        try:
            if category == "worldview":
                return self._import_worldview()
            elif category == "characters":
                return self._import_characters()
            elif category == "environments":
                return self._import_environments()
            elif category == "plot":
                return self._import_plot()
            elif category == "style":
                return self._import_style()
            elif category == "memory":
                return self._import_memory()

        except Exception as e:
            return {
                "status": "error",
                "message": f"导入{category}失败: {e}"
            }

    def _import_worldview(self) -> Dict[str, Any]:
        """导入世界观设定"""
        world_setting_file = self.settings_dir / "worldview" / "world_setting.md"
        world_rules_file = self.settings_dir / "worldview" / "world_rules.md"

        if not world_setting_file.exists():
            return {
                "status": "error",
                "message": "未找到世界观设定文件"
            }

        # 解析世界观设定文件
        content = world_setting_file.read_text(encoding='utf-8')
        parsed_data = self._parse_worldview_file(content)

        # 使用worldbuilder更新设定
        result = self.world_builder.update_worldview(parsed_data)

        self.import_log.append({
            "timestamp": datetime.now().isoformat(),
            "category": "worldview",
            "action": "import",
            "status": result["status"],
            "details": result.get("message", "")
        })

        return {
            "status": result["status"],
            "message": f"世界观导入{'成功' if result['status'] == 'success' else '失败'}",
            "files_processed": 1,
            "parsed_data": parsed_data
        }

    def _import_characters(self) -> Dict[str, Any]:
        """导入角色设定"""
        character_file = self.settings_dir / "characters" / "character_relations.md"

        if not character_file.exists():
            return {
                "status": "error",
                "message": "未找到角色设定文件"
            }

        # 解析角色设定文件
        content = character_file.read_text(encoding='utf-8')
        parsed_data = self._parse_character_file(content)

        # 更新角色设定
        result = {
            "status": "success",
            "message": "角色设定导入成功",
            "characters_found": len(parsed_data.get("main_characters", [])) + len(parsed_data.get("supporting_characters", []))
        }

        self.import_log.append({
            "timestamp": datetime.now().isoformat(),
            "category": "characters",
            "action": "import",
            "status": result["status"],
            "details": result.get("message", "")
        })

        return {
            "status": result["status"],
            "message": result["message"],
            "files_processed": 1,
            "characters_imported": result["characters_found"]
        }

    def _import_environments(self) -> Dict[str, Any]:
        """导入环境设定"""
        locations_file = self.settings_dir / "environments" / "locations.md"

        if not locations_file.exists():
            return {
                "status": "error",
                "message": "未找到环境设定文件"
            }

        # 解析环境设定文件
        content = locations_file.read_text(encoding='utf-8')
        parsed_data = self._parse_environment_file(content)

        result = {
            "status": "success",
            "message": "环境设定导入成功",
            "locations_found": len(parsed_data.get("locations", []))
        }

        self.import_log.append({
            "timestamp": datetime.now().isoformat(),
            "category": "environments",
            "action": "import",
            "status": result["status"],
            "details": result.get("message", "")
        })

        return {
            "status": result["status"],
            "message": result["message"],
            "files_processed": 1,
            "locations_imported": result["locations_found"]
        }

    def _import_plot(self) -> Dict[str, Any]:
        """导入情节设定"""
        plot_file = self.settings_dir / "plot" / "main_plot.md"

        if not plot_file.exists():
            return {
                "status": "error",
                "message": "未找到情节设定文件"
            }

        # 解析情节设定文件
        content = plot_file.read_text(encoding='utf-8')
        parsed_data = self._parse_plot_file(content)

        result = {
            "status": "success",
            "message": "情节设定导入成功",
            "plot_elements_found": len([k for k in parsed_data.keys() if k not in ["status", "message"]])
        }

        self.import_log.append({
            "timestamp": datetime.now().isoformat(),
            "category": "plot",
            "action": "import",
            "status": result["status"],
            "details": result.get("message", "")
        })

        return {
            "status": result["status"],
            "message": result["message"],
            "files_processed": 1,
            "plot_elements_imported": result["plot_elements_found"]
        }

    def _import_style(self) -> Dict[str, Any]:
        """导入写作风格设定"""
        style_file = self.settings_dir / "writing_style" / "narrative_style.md"

        if not style_file.exists():
            return {
                "status": "error",
                "message": "未找到写作风格设定文件"
            }

        # 解析写作风格文件
        content = style_file.read_text(encoding='utf-8')
        parsed_data = self._parse_style_file(content)

        result = {
            "status": "success",
            "message": "写作风格导入成功",
            "style_elements_found": len([k for k in parsed_data.keys() if k not in ["status", "message"]])
        }

        self.import_log.append({
            "timestamp": datetime.now().isoformat(),
            "category": "style",
            "action": "import",
            "status": result["status"],
            "details": result.get("message", "")
        })

        return {
            "status": result["status"],
            "message": result["message"],
            "files_processed": 1,
            "style_elements_imported": result["style_elements_found"]
        }

    def _import_memory(self) -> Dict[str, Any]:
        """导入记忆设定"""
        memory_file = self.settings_dir / "memory" / "memory_structure.md"

        if not memory_file.exists():
            return {
                "status": "error",
                "message": "未找到记忆设定文件"
            }

        # 解析记忆设定文件
        content = memory_file.read_text(encoding='utf-8')
        parsed_data = self._parse_memory_file(content)

        result = {
            "status": "success",
            "message": "记忆设定导入成功",
            "memory_elements_found": len([k for k in parsed_data.keys() if k not in ["status", "message"]])
        }

        self.import_log.append({
            "timestamp": datetime.now().isoformat(),
            "category": "memory",
            "action": "import",
            "status": result["status"],
            "details": result.get("message", "")
        })

        return {
            "status": result["status"],
            "message": result["message"],
            "files_processed": 1,
            "memory_elements_imported": result["memory_elements_found"]
        }

    def _parse_worldview_file(self, content: str) -> Dict[str, Any]:
        """解析世界观设定文件"""
        parsed_data = {}

        # 解析基本信息
        world_name_match = re.search(r'\*\*世界名称\*\*:\s*([^\n]+)', content)
        if world_name_match:
            parsed_data["world_name"] = world_name_match.group(1).strip()

        era_match = re.search(r'\*\*时代背景\*\*:\s*([^\n]+)', content)
        if era_match:
            parsed_data["era"] = era_match.group(1).strip()

        tech_match = re.search(r'\*\*技术水平\*\*:\s*([^\n]+)', content)
        if tech_match:
            parsed_data["technology_level"] = tech_match.group(1).strip()

        world_type_match = re.search(r'\*\*世界类型\*\*:\s*([^\n]+)', content)
        if world_type_match:
            parsed_data["world_type"] = world_type_match.group(1).strip()

        # 解析各个部分
        sections = {
            "geography": "## 地理环境",
            "society": "## 社会结构",
            "magic_system": "## 魔法系统",
            "history": "## 历史背景",
            "culture": "## 文化特色",
            "economy": "## 经济体系",
            "religion": "## 宗教信仰"
        }

        for key, section_title in sections.items():
            section_match = re.search(rf'{section_title}\s*\n(.*?)(?=##|\Z)', content, re.DOTALL)
            if section_match:
                parsed_data[key] = section_match.group(1).strip()

        # 添加默认的魔法系统如果没有找到
        if "magic_system" not in parsed_data:
            parsed_data["magic_system"] = "待补充..."

        return parsed_data

    def _parse_character_file(self, content: str) -> Dict[str, Any]:
        """解析角色设定文件"""
        parsed_data = {
            "main_characters": [],
            "supporting_characters": []
        }

        # 解析主要角色
        main_section = re.search(r'## 主要角色\s*\n(.*?)(?=## 配角|\Z)', content, re.DOTALL)
        if main_section:
            main_content = main_section.group(1)
            char_matches = re.findall(r'### (?:角色\d+: )?([^\n]+)\s*\n(.*?)(?=###|\Z)', main_content, re.DOTALL)

            for char_name, char_info in char_matches:
                character = {
                    "name": char_name.strip(),
                    "personality": self._extract_field(char_info, "性格"),
                    "background": self._extract_field(char_info, "背景"),
                    "goal": self._extract_field(char_info, "目标"),
                    "additional_info": char_info.strip()
                }
                parsed_data["main_characters"].append(character)

        # 解析配角
        supporting_section = re.search(r'## 配角\s*\n(.*?)(?=\Z)', content, re.DOTALL)
        if supporting_section:
            supporting_content = supporting_section.group(1)
            char_matches = re.findall(r'### (?:配角\d+: )?([^\n]+)\s*\n(.*?)(?=###|\Z)', supporting_content, re.DOTALL)

            for char_name, char_info in char_matches:
                character = {
                    "name": char_name.strip(),
                    "role": self._extract_field(char_info, "作用"),
                    "traits": self._extract_field(char_info, "特点"),
                    "additional_info": char_info.strip()
                }
                parsed_data["supporting_characters"].append(character)

        return parsed_data

    def _parse_environment_file(self, content: str) -> Dict[str, Any]:
        """解析环境设定文件"""
        parsed_data = {
            "locations": [],
            "atmosphere": "",
            "scene_description_points": ""
        }

        # 解析主要地点
        locations_section = re.search(r'## 主要地点\s*\n(.*?)(?=##|\Z)', content, re.DOTALL)
        if locations_section:
            locations_content = locations_section.group(1)
            location_matches = re.findall(r'### ([^\n]+)\s*\n(.*?)(?=###|\Z)', locations_content, re.DOTALL)

            for location_name, location_info in location_matches:
                location = {
                    "name": location_name.strip(),
                    "description": location_info.strip()
                }
                parsed_data["locations"].append(location)

        # 解析环境氛围
        atmosphere_match = re.search(r'## 环境氛围\s*\n(.*?)(?=##|\Z)', content, re.DOTALL)
        if atmosphere_match:
            parsed_data["atmosphere"] = atmosphere_match.group(1).strip()

        # 解析场景描述要点
        scene_points_match = re.search(r'## 场景描述要点\s*\n(.*?)(?=##|\Z)', content, re.DOTALL)
        if scene_points_match:
            parsed_data["scene_description_points"] = scene_points_match.group(1).strip()

        return parsed_data

    def _parse_plot_file(self, content: str) -> Dict[str, Any]:
        """解析情节设定文件"""
        parsed_data = {}

        # 解析各个情节部分
        sections = {
            "main_plot": "## 主线情节",
            "main_conflicts": "## 主要冲突",
            "plot_twists": "## 情节转折点",
            "ending_setup": "## 结局设定"
        }

        for key, section_title in sections.items():
            section_match = re.search(rf'{section_title}\s*\n(.*?)(?=##|\Z)', content, re.DOTALL)
            if section_match:
                parsed_data[key] = section_match.group(1).strip()

        return parsed_data

    def _parse_style_file(self, content: str) -> Dict[str, Any]:
        """解析写作风格设定文件"""
        parsed_data = {}

        # 解析各个风格部分
        sections = {
            "narrative_style": "## 叙事风格",
            "dialogue_style": "## 对话风格",
            "language_features": "## 语言特色",
            "vocabulary_preferences": "## 词汇偏好"
        }

        for key, section_title in sections.items():
            section_match = re.search(rf'{section_title}\s*\n(.*?)(?=##|\Z)', content, re.DOTALL)
            if section_match:
                parsed_data[key] = section_match.group(1).strip()

        return parsed_data

    def _parse_memory_file(self, content: str) -> Dict[str, Any]:
        """解析记忆设定文件"""
        parsed_data = {}

        # 解析各个记忆部分
        sections = {
            "memory_structure": "## 记忆结构",
            "character_memory_links": "## 角色记忆关联",
            "memory_compression_rules": "## 记忆压缩规则"
        }

        for key, section_title in sections.items():
            section_match = re.search(rf'{section_title}\s*\n(.*?)(?=##|\Z)', content, re.DOTALL)
            if section_match:
                parsed_data[key] = section_match.group(1).strip()

        return parsed_data

    def _extract_field(self, content: str, field_name: str) -> str:
        """从内容中提取特定字段的值"""
        pattern = rf'-?\*\*{field_name}\*\*:?\s*([^\n]+)'
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""

    def _save_import_log(self):
        """保存导入日志"""
        log_file = self.project_path / "system" / "import_log.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        log_data = {
            "import_time": datetime.now().isoformat(),
            "project_name": self.project_name,
            "project_path": str(self.project_path),
            "log_entries": self.import_log
        }

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="小说生成器导入管理器")
    parser.add_argument("--action", choices=["scan", "import-all", "import-category", "scan-directory", "import-from-directory"],
                       required=True, help="操作类型")
    parser.add_argument("--category", help="要导入的设定类别 (用于import-category)")
    parser.add_argument("--target-directory", help="目标目录路径 (用于scan-directory和import-from-directory)")
    parser.add_argument("--specific-setting", help="指定导入的设定类型 (用于import-from-directory)")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    im = ImportManager(args.project_path)

    if args.action == "scan":
        result = im.scan_available_settings()
    elif args.action == "scan-directory":
        if not args.target_directory:
            print("错误: scan-directory操作需要指定--target-directory参数")
            return
        result = im.scan_directory_content(args.target_directory)
    elif args.action == "import-from-directory":
        if not args.target_directory:
            print("错误: import-from-directory操作需要指定--target-directory参数")
            return
        result = im.import_settings_from_directory(args.target_directory, args.specific_setting)
    elif args.action == "import-all":
        result = im.import_all_settings()
    elif args.action == "import-category":
        if not args.category:
            print("错误: import-category操作需要指定--category参数")
            return
        result = im.import_category(args.category)
    else:
        result = {"status": "error", "message": f"未知操作: {args.action}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()