#!/usr/bin/env python3
"""
统一API接口
整合所有小说生成器功能的统一入口
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# 导入各个管理器
from import_manager import ImportManager
from settings_display_manager import SettingsDisplayManager
from memory_display_manager import MemoryDisplayManager
from chapter_manager import ChapterManager
from chapter_memory_analyzer import ChapterMemoryAnalyzer
from data_managers.character_manager import CharacterManager
from data_managers.worldbuilder import WorldBuilder
from data_managers.memory_manager import MemoryManager
from project_initializer import ProjectInitializer
from settings_completeness_checker import SettingsCompletenessChecker
from chapter_outline_generator import ChapterOutlineGenerator
from interactive_workflow_manager import WorkflowManager

class UnifiedAPI:
    """统一API接口，整合所有小说生成器功能"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)

        # 初始化各个管理器
        self.import_manager = ImportManager(project_path)
        self.settings_display = SettingsDisplayManager(project_path)
        self.memory_display = MemoryDisplayManager(project_path)
        self.chapter_manager = ChapterManager(project_path)
        self.memory_analyzer = ChapterMemoryAnalyzer(project_path)
        self.character_manager = CharacterManager(project_path)
        self.world_builder = WorldBuilder(project_path)
        self.memory_manager = MemoryManager(project_path)
        self.project_initializer = ProjectInitializer(project_path)
        self.settings_checker = SettingsCompletenessChecker(project_path)
        self.chapter_outline_generator = ChapterOutlineGenerator(project_path)
        self.workflow_manager = WorkflowManager(project_path)

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理统一请求"""
        try:
            action = request.get("action")
            if not action:
                return {
                    "status": "error",
                    "message": "缺少action参数"
                }

            # 路由到相应的处理器
            if action.startswith("import."):
                return self._handle_import_request(request)
            elif action.startswith("display."):
                return self._handle_display_request(request)
            elif action.startswith("chapter."):
                return self._handle_chapter_request(request)
            elif action.startswith("ai."):
                return self._handle_ai_request(request)
            elif action.startswith("project."):
                return self._handle_project_request(request)
            elif action.startswith("settings."):
                return self._handle_settings_request(request)
            elif action.startswith("outline."):
                return self._handle_outline_request(request)
            elif action.startswith("workflow."):
                return self._handle_workflow_request(request)
            elif action == "system.status":
                return self._get_system_status()
            else:
                return {
                    "status": "error",
                    "message": f"不支持的操作: {action}"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"处理请求失败: {e}"
            }

    def _handle_import_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理导入请求"""
        action = request.get("action")

        if action == "import.scan_directory":
            target_directory = request.get("target_directory")
            if not target_directory:
                return {"status": "error", "message": "缺少target_directory参数"}

            return self.import_manager.scan_directory_content(target_directory)

        elif action == "import.from_directory":
            target_directory = request.get("target_directory")
            specific_setting = request.get("specific_setting")

            if not target_directory:
                return {"status": "error", "message": "缺少target_directory参数"}

            return self.import_manager.import_settings_from_directory(
                target_directory, specific_setting
            )

        elif action == "import.process_ai_result":
            ai_result = request.get("ai_result")
            if not ai_result:
                return {"status": "error", "message": "缺少ai_result参数"}

            return self.import_manager.process_ai_analysis_result(ai_result)

        else:
            return {"status": "error", "message": f"不支持的导入操作: {action}"}

    def _handle_display_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理显示请求"""
        action = request.get("action")

        if action == "display.setting":
            setting_type = request.get("setting_type")
            setting_name = request.get("setting_name")
            format_type = request.get("format_type", "readable")

            if not setting_type:
                return {"status": "error", "message": "缺少setting_type参数"}

            return self.settings_display.display_setting(setting_type, setting_name, format_type)

        elif action == "display.memory":
            identifier = request.get("identifier")
            segment_type = request.get("segment_type", "character_all")
            display_format = request.get("display_format", "readable")

            if not identifier:
                return {"status": "error", "message": "缺少identifier参数"}

            return self.memory_display.display_memory_segment(
                identifier, segment_type, display_format
            )

        elif action == "display.memory_stats":
            character_name = request.get("character_name")
            return self.memory_display.get_memory_statistics(character_name)

        elif action == "display.available_settings":
            return self.settings_display.get_available_settings()

        else:
            return {"status": "error", "message": f"不支持的显示操作: {action}"}

    def _handle_chapter_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理章节请求"""
        action = request.get("action")

        if action == "chapter.create":
            chapter_number = request.get("chapter_number")
            title = request.get("title")
            context_summary = request.get("context_summary")

            if chapter_number is None:
                return {"status": "error", "message": "缺少chapter_number参数"}

            return self.chapter_manager.create_chapter(chapter_number, title, context_summary)

        elif action == "chapter.get_content":
            chapter_number = request.get("chapter_number")
            if chapter_number is None:
                return {"status": "error", "message": "缺少chapter_number参数"}

            return self.chapter_manager.get_chapter_content(chapter_number)

        elif action == "chapter.intelligent_edit":
            chapter_number = request.get("chapter_number")
            edit_request = request.get("edit_request")

            if chapter_number is None:
                return {"status": "error", "message": "缺少chapter_number参数"}
            if not edit_request:
                return {"status": "error", "message": "缺少edit_request参数"}

            return self.chapter_manager.intelligent_content_edit(chapter_number, edit_request)

        elif action == "chapter.process_ai_edit":
            chapter_number = request.get("chapter_number")
            ai_result = request.get("ai_result")

            if chapter_number is None:
                return {"status": "error", "message": "缺少chapter_number参数"}
            if not ai_result:
                return {"status": "error", "message": "缺少ai_result参数"}

            return self.chapter_manager.process_ai_edit_result(chapter_number, ai_result)

        elif action == "chapter.context_update":
            chapter_number = request.get("chapter_number")
            context_update = request.get("context_update")

            if chapter_number is None:
                return {"status": "error", "message": "缺少chapter_number参数"}
            if not context_update:
                return {"status": "error", "message": "缺少context_update参数"}

            return self.chapter_manager.context_aware_update(chapter_number, context_update)

        elif action == "chapter.analyze_memory":
            chapter_number = request.get("chapter_number")
            if chapter_number is None:
                return {"status": "error", "message": "缺少chapter_number参数"}

            return self.memory_analyzer.analyze_chapter_content(chapter_number)

        elif action == "chapter.generate_memory":
            chapter_number = request.get("chapter_number")
            auto_confirm = request.get("auto_confirm", False)

            if chapter_number is None:
                return {"status": "error", "message": "缺少chapter_number参数"}

            return self.memory_analyzer.apply_generated_memories(chapter_number, auto_confirm)

        elif action == "chapter.apply_memory":
            chapter_number = request.get("chapter_number")
            if chapter_number is None:
                return {"status": "error", "message": "缺少chapter_number参数"}

            return self.memory_analyzer.apply_generated_memories(chapter_number, True)

        elif action == "chapter.memory_info":
            chapter_number = request.get("chapter_number")
            if chapter_number is None:
                return {"status": "error", "message": "缺少chapter_number参数"}

            return self.memory_analyzer.get_analysis_info(chapter_number)

        else:
            return {"status": "error", "message": f"不支持的章节操作: {action}"}

    def _handle_ai_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理AI相关请求"""
        action = request.get("action")

        if action == "ai.generate_summary":
            content = request.get("content")
            summary_type = request.get("summary_type", "general")

            if not content:
                return {"status": "error", "message": "缺少content参数"}

            # 返回AI任务请求
            return {
                "status": "ai_task_required",
                "ai_task": {
                    "task_type": "generate_summary",
                    "content": content,
                    "summary_type": summary_type
                }
            }

        elif action == "ai.edit_content":
            content = request.get("content")
            existing_content = request.get("existing_content")
            edit_instructions = request.get("edit_instructions")
            edit_mode = request.get("edit_mode", "improve")

            # 支持content或existing_content参数
            if content and not existing_content:
                existing_content = content

            if not existing_content:
                return {"status": "error", "message": "缺少content或existing_content参数"}
            if not edit_instructions:
                return {"status": "error", "message": "缺少edit_instructions参数"}

            # 返回AI任务请求
            return {
                "status": "ai_task_required",
                "ai_task": {
                    "task_type": "content_edit",
                    "existing_content": existing_content,
                    "edit_instructions": edit_instructions,
                    "edit_mode": edit_mode
                }
            }

        elif action == "ai.analyze_content":
            content = request.get("content")
            files = request.get("files")
            analysis_type = request.get("analysis_type", "general")

            # 支持content或files参数
            if content:
                # 如果是简单的content，转换为files格式
                files = [{"content": content, "name": "direct_content"}]
            elif not files:
                return {"status": "error", "message": "缺少content或files参数"}

            # 返回AI任务请求
            return {
                "status": "ai_task_required",
                "ai_task": {
                    "task_type": "content_analysis",
                    "files": files,
                    "analysis_type": analysis_type
                }
            }

        else:
            return {"status": "error", "message": f"不支持的AI操作: {action}"}

    def _handle_project_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理项目相关请求"""
        action = request.get("action")

        if action == "project.initialize":
            return self._handle_project_initialization(request)
        elif action == "project.scan":
            return self._handle_project_scan(request)
        elif action == "project.backup":
            return self._handle_project_backup(request)
        else:
            return {"status": "error", "message": f"不支持的项目操作: {action}"}

    def _handle_project_initialization(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理项目初始化请求"""
        dry_run = request.get("dry_run", False)

        if dry_run:
            # 干运行模式 - 只扫描，不实际修改
            scan_result = self.project_initializer.scan_existing_documents()
            reference_scan = self.project_initializer.scan_reference_directory()

            return {
                "status": "success",
                "message": "项目初始化干运行完成",
                "dry_run": True,
                "scan_result": scan_result,
                "reference_scan": reference_scan,
                "recommended_actions": self._generate_recommended_actions(scan_result, reference_scan)
            }
        else:
            # 实际执行初始化
            result = self.project_initializer.run_initialization()

            # 如果有参考材料需要AI分析，返回AI任务
            if (result.get("success") and
                result["results"]["reference_scan"]["total_materials"] > 0):

                return {
                    "status": "ai_task_required",
                    "message": "项目初始化基础操作完成，需要AI分析参考材料",
                    "initialization_result": result,
                    "ai_task": {
                        "task_type": "content_analysis",
                        "files": self._prepare_reference_files_for_ai(result["results"]["reference_scan"]),
                        "analysis_type": "project_initialization",
                        "context": {
                            "project_path": str(self.project_path),
                            "total_materials": result["results"]["reference_scan"]["total_materials"]
                        }
                    }
                }

            return result

    def _handle_project_scan(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理项目扫描请求"""
        scan_type = request.get("scan_type", "full")

        if scan_type == "full":
            scan_result = self.project_initializer.scan_existing_documents()
            reference_scan = self.project_initializer.scan_reference_directory()

            return {
                "status": "success",
                "scan_type": "full",
                "document_scan": scan_result,
                "reference_scan": reference_scan
            }
        elif scan_type == "documents_only":
            scan_result = self.project_initializer.scan_existing_documents()
            return {
                "status": "success",
                "scan_type": "documents_only",
                "result": scan_result
            }
        elif scan_type == "references_only":
            reference_scan = self.project_initializer.scan_reference_directory()
            return {
                "status": "success",
                "scan_type": "references_only",
                "result": reference_scan
            }
        else:
            return {"status": "error", "message": f"不支持的扫描类型: {scan_type}"}

    def _handle_project_backup(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理项目备份请求"""
        try:
            self.project_initializer.create_backup()
            return {
                "status": "success",
                "message": "项目备份创建成功",
                "backup_location": str(self.project_initializer.backup_dir)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"备份创建失败: {e}"
            }

    def _generate_recommended_actions(self, scan_result: Dict[str, Any], reference_scan: Dict[str, Any]) -> List[str]:
        """生成推荐操作"""
        actions = []

        if scan_result["total_files"] == 0:
            actions.append("建议创建完整的基础设定文件")
        else:
            if len(scan_result["character_files"]) == 0:
                actions.append("建议创建角色设定文件")
            if len(scan_result["worldview_files"]) == 0:
                actions.append("建议创建世界观设定文件")

        if reference_scan["total_materials"] > 0:
            actions.append(f"发现 {reference_scan['total_materials']} 份参考材料，建议进行AI分析以完善设定")

        return actions

    def _prepare_reference_files_for_ai(self, reference_scan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """准备参考材料文件供AI分析"""
        files = []

        for material_type, materials in reference_scan["materials_by_type"].items():
            for material in materials:
                try:
                    file_path = self.project_path / material["path"]
                    if file_path.exists():
                        content = file_path.read_text(encoding='utf-8')
                        files.append({
                            "name": material["path"],
                            "content": content,
                            "type": material_type,
                            "title": material.get("title", ""),
                            "key_elements": material.get("key_elements", [])
                        })
                except Exception as e:
                    # 跳过无法读取的文件
                    pass

        return files

    def _handle_workflow_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理工作流程相关请求"""
        action = request.get("action")

        if action == "workflow.create_article":
            return self._create_article_workflow(request)
        elif action == "workflow.handle_response":
            return self._handle_workflow_response(request)
        elif action == "workflow.review_chapter":
            return self._review_chapter_workflow(request)
        elif action == "workflow.approve_chapter":
            return self._approve_chapter_workflow(request)
        elif action == "workflow.get_progress":
            return self._get_workflow_progress()
        else:
            return {"status": "error", "message": f"不支持的工作流程操作: {action}"}

    def _create_article_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """创建文章工作流程"""
        try:
            # 处理创作请求
            workflow_result = self.workflow_manager.process_creation_request(request)

            return {
                "status": "success",
                "workflow_result": workflow_result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"创建文章工作流程失败: {e}"
            }

    def _handle_workflow_response(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理工作流程响应"""
        try:
            request_id = request.get("request_id")
            user_response = request.get("user_response", {})

            if not request_id:
                return {"status": "error", "message": "缺少request_id参数"}

            response_result = self.workflow_manager.handle_user_response(request_id, user_response)

            return {
                "status": "success",
                "response_result": response_result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"处理工作流程响应失败: {e}"
            }

    def _review_chapter_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """审阅章节工作流程"""
        try:
            chapter_number = request.get("chapter_number")
            if chapter_number is None:
                return {"status": "error", "message": "缺少chapter_number参数"}

            review_result = self.workflow_manager.review_chapter(chapter_number)

            return {
                "status": "success",
                "review_result": review_result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"审阅章节失败: {e}"
            }

    def _approve_chapter_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """批准章节工作流程"""
        try:
            chapter_number = request.get("chapter_number")
            approval_data = request.get("approval_data", {})

            if chapter_number is None:
                return {"status": "error", "message": "缺少chapter_number参数"}

            approval_result = self.workflow_manager.approve_chapter(chapter_number, approval_data)

            return {
                "status": "success",
                "approval_result": approval_result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"批准章节失败: {e}"
            }

    def _get_workflow_progress(self) -> Dict[str, Any]:
        """获取工作流程进度"""
        try:
            progress = self.workflow_manager.get_workflow_progress()

            return {
                "status": "success",
                "progress": progress
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取工作流程进度失败: {e}"
            }

    def _handle_settings_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理设定相关请求"""
        action = request.get("action")

        if action == "settings.check_completeness":
            return self._check_settings_completeness()
        elif action == "settings.get_guidance":
            return self._get_settings_guidance()
        else:
            return {"status": "error", "message": f"不支持的设定操作: {action}"}

    def _handle_outline_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理梗概相关请求"""
        action = request.get("action")
        chapter_number = request.get("chapter_number")

        if chapter_number is None:
            return {"status": "error", "message": "缺少chapter_number参数"}

        if action == "outline.prepare_creation":
            return self._prepare_chapter_creation(chapter_number)
        elif action == "outline.generate_suggestions":
            return self._generate_outline_suggestions(chapter_number)
        elif action == "outline.save":
            outline_data = request.get("outline_data")
            if not outline_data:
                return {"status": "error", "message": "缺少outline_data参数"}
            return self._save_chapter_outline(chapter_number, outline_data)
        else:
            return {"status": "error", "message": f"不支持的梗概操作: {action}"}

    def _check_settings_completeness(self) -> Dict[str, Any]:
        """检查设定完整性"""
        try:
            completeness_result = self.settings_checker.check_all_settings_completeness()

            # 生成用户引导
            guidance = self.settings_checker.generate_user_guidance(completeness_result)

            return {
                "status": "success",
                "completeness_result": completeness_result,
                "user_guidance": guidance
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"检查设定完整性失败: {e}"
            }

    def _get_settings_guidance(self) -> Dict[str, Any]:
        """获取设定引导"""
        try:
            completeness_result = self.settings_checker.check_all_settings_completeness()
            guidance = self.settings_checker.generate_user_guidance(completeness_result)

            return {
                "status": "success",
                "guidance": guidance,
                "completeness_summary": {
                    "overall_score": completeness_result["overall_score"],
                    "ready_for_writing": completeness_result["ready_for_writing"],
                    "missing_count": len(completeness_result["missing_items"])
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取设定引导失败: {e}"
            }

    def _prepare_chapter_creation(self, chapter_number: int) -> Dict[str, Any]:
        """准备章节创作"""
        try:
            preparation_result = self.chapter_outline_generator.prepare_chapter_creation(chapter_number)

            # 如果需要AI任务，返回AI任务请求
            if (not preparation_result["ready_for_creation"] and
                preparation_result.get("creation_guidance", {}).get("priority_actions")):

                # 检查是否需要AI来生成缺失的设定
                missing_settings = self._identify_ai_generatable_settings(preparation_result)
                if missing_settings:
                    return {
                        "status": "ai_task_required",
                        "message": "需要AI生成缺失的设定内容",
                        "preparation_result": preparation_result,
                        "ai_task": {
                            "task_type": "generate_missing_settings",
                            "missing_settings": missing_settings,
                            "project_context": self._create_project_context_for_ai(),
                            "requirements": {
                                "style": "detailed and consistent",
                                "format": "structured content for integration"
                            }
                        }
                    }

            return {
                "status": "success",
                "preparation_result": preparation_result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"准备章节创作失败: {e}"
            }

    def _generate_outline_suggestions(self, chapter_number: int) -> Dict[str, Any]:
        """生成章节梗概建议"""
        try:
            suggestions = self.chapter_outline_generator.generate_outline_suggestions(chapter_number)

            # 如果需要AI生成梗概，返回AI任务请求
            if suggestions.get("ai_task_required"):
                return {
                    "status": "ai_task_required",
                    "message": "需要AI生成详细的章节梗概",
                    "suggestions": suggestions,
                    "ai_task": suggestions.get("ai_task")
                }

            return {
                "status": "success",
                "suggestions": suggestions
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"生成梗概建议失败: {e}"
            }

    def _save_chapter_outline(self, chapter_number: int, outline_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存章节梗概"""
        try:
            save_result = self.chapter_outline_generator.save_chapter_outline(chapter_number, outline_data)
            return {
                "status": "success" if save_result["success"] else "error",
                "message": save_result["message"],
                "files": {
                    "outline_file": save_result.get("outline_file"),
                    "json_file": save_result.get("json_file")
                } if save_result["success"] else None
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"保存章节梗概失败: {e}"
            }

    def _identify_ai_generatable_settings(self, preparation_result: Dict[str, Any]) -> List[str]:
        """识别可以由AI生成的设定"""
        missing_items = preparation_result.get("blocking_issues", [])
        generatable_settings = []

        # 根据缺失项判断哪些可以由AI生成
        for item in missing_items:
            if "世界观" in item:
                generatable_settings.append("worldview")
            elif "角色" in item:
                generatable_settings.append("characters")
            elif "情节" in item:
                generatable_settings.append("plot")
            elif "环境" in item:
                generatable_settings.append("environments")
            elif "写作风格" in item:
                generatable_settings.append("writing_style")

        return list(set(generatable_settings))

    def _create_project_context_for_ai(self) -> Dict[str, Any]:
        """为AI创建项目上下文"""
        try:
            # 获取基本的项目信息
            existing_chapters = self.chapter_outline_generator._get_existing_chapters()

            return {
                "project_path": str(self.project_path),
                "existing_chapters_count": len(existing_chapters),
                "project_status": "existing_project" if existing_chapters else "new_project",
                "current_settings": self._get_current_settings_summary()
            }
        except Exception:
            return {
                "project_path": str(self.project_path),
                "existing_chapters_count": 0,
                "project_status": "new_project"
            }

    def _get_current_settings_summary(self) -> Dict[str, Any]:
        """获取当前设定摘要"""
        try:
            completeness_result = self.settings_checker.check_all_settings_completeness()
            return {
                "overall_score": completeness_result["overall_score"],
                "ready_for_writing": completeness_result["ready_for_writing"],
                "existing_categories": list(completeness_result["category_results"].keys())
            }
        except Exception:
            return {
                "overall_score": 0,
                "ready_for_writing": False,
                "existing_categories": []
            }

    def _get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            # 检查项目目录结构
            required_dirs = [
                "settings",
                "settings/worldview",
                "settings/characters",
                "settings/environments",
                "settings/plot",
                "settings/writing_style",
                "settings/memory",
                "draft",
                "draft/chapters",
                "manuscript",
                "system",
                "progress"
            ]

            existing_dirs = []
            missing_dirs = []

            for dir_path in required_dirs:
                full_path = self.project_path / dir_path
                if full_path.exists():
                    existing_dirs.append(dir_path)
                else:
                    missing_dirs.append(dir_path)

            # 统计各个模块的状态
            worldview_status = self.world_builder.load_worldview()["status"]
            characters_result = self.character_manager.list_characters()
            character_count = characters_result.get("total", 0) if characters_result["status"] == "success" else 0

            return {
                "status": "success",
                "project_path": str(self.project_path),
                "directory_structure": {
                    "existing_dirs": existing_dirs,
                    "missing_dirs": missing_dirs,
                    "total_dirs": len(required_dirs)
                },
                "modules_status": {
                    "worldview": worldview_status,
                    "characters": {
                        "status": characters_result["status"],
                        "count": character_count
                    }
                },
                "features_available": [
                    "import_settings_from_directory",
                    "display_settings",
                    "display_memories",
                    "chapter_intelligent_edit",
                    "ai_content_analysis",
                    "memory_management",
                    "chapter_memory_analysis",
                    "auto_memory_generation",
                    "project_initialization",
                    "project_scanning",
                    "project_backup",
                    "reference_material_analysis",
                    "settings_completeness_check",
                    "user_guidance_generation",
                    "chapter_preparation",
                    "outline_suggestions",
                    "interactive_workflow"
                ]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取系统状态失败: {e}"
            }

def main():
    """命令行接口"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="小说生成器统一API")
    parser.add_argument("--request-file", help="JSON请求文件路径")
    parser.add_argument("--request-json", help="JSON请求字符串")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    # 读取请求
    if args.request_file:
        try:
            with open(args.request_file, 'r', encoding='utf-8') as f:
                request_data = json.load(f)
        except Exception as e:
            print(f"错误: 无法读取请求文件 - {e}")
            sys.exit(1)
    elif args.request_json:
        try:
            request_data = json.loads(args.request_json)
        except Exception as e:
            print(f"错误: 无法解析JSON请求 - {e}")
            sys.exit(1)
    else:
        print("错误: 请提供 --request-file 或 --request-json 参数")
        sys.exit(1)

    # 处理请求
    api = UnifiedAPI(args.project_path)
    result = api.process_request(request_data)

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()