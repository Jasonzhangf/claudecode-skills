#!/usr/bin/env python3
"""
交互式工作流程管理器
管理完整的小说创作流程，包括初始化、设定检查、章节创作、审阅等
"""

import json
import re
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from project_initializer import ProjectInitializer
from settings_completeness_checker import SettingsCompletenessChecker
from chapter_outline_generator import ChapterOutlineGenerator
from chapter_memory_analyzer import ChapterMemoryAnalyzer
from chapter_manager import ChapterManager

class WorkflowStage(Enum):
    """工作流程阶段"""
    INITIALIZATION = "initialization"
    SETTINGS_CHECK = "settings_check"
    CHAPTER_PLANNING = "chapter_planning"
    CHAPTER_CREATION = "chapter_creation"
    CHAPTER_REVIEW = "chapter_review"
    COMPLETED = "completed"

class WorkflowManager:
    """交互式工作流程管理器"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.workflow_file = self.project_path / "system" / "workflow_state.json"
        self.progress_file = self.project_path / "system" / "workflow_progress.json"

        # 初始化各个组件
        self.project_initializer = ProjectInitializer(str(self.project_path))
        self.settings_checker = SettingsCompletenessChecker(str(self.project_path))
        self.chapter_outline_generator = ChapterOutlineGenerator(str(self.project_path))
        self.memory_analyzer = ChapterMemoryAnalyzer(str(self.project_path))
        self.chapter_manager = ChapterManager(str(self.project_path))

        # 当前工作流程状态
        self.current_stage = None
        self.workflow_state = self._load_workflow_state()
        self.progress_history = self._load_progress_history()

    def process_creation_request(self, user_request: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理文章创作请求 - 主入口"""
        request_result = {
            "request_id": self._generate_request_id(),
            "timestamp": datetime.now().isoformat(),
            "current_stage": None,
            "next_actions": [],
            "blocking_issues": [],
            "ai_tasks": [],
            "user_interactions": [],
            "progress_update": {}
        }

        try:
            # 1. 检查项目是否已初始化
            initialization_status = self._check_initialization_status()
            request_result["initialization_status"] = initialization_status

            if not initialization_status["is_initialized"]:
                # 项目未初始化，需要先初始化
                return self._handle_uninitialized_project(request_result, user_request)

            # 2. 检查设定完整性
            settings_status = self._check_settings_completeness()
            request_result["settings_status"] = settings_status

            if not settings_status["ready_for_writing"]:
                # 设定不完整，需要补充
                return self._handle_incomplete_settings(request_result, user_request)

            # 3. 确定下一章节和创作准备
            chapter_preparation = self._prepare_next_chapter()
            request_result["chapter_preparation"] = chapter_preparation

            if not chapter_preparation["ready_for_creation"]:
                # 章节创作准备不充分
                return self._handle_chapter_preparation_issues(request_result, user_request)

            # 4. 开始章节创作流程
            return self._start_chapter_creation_workflow(request_result, user_request)

        except Exception as e:
            request_result["error"] = str(e)
            request_result["status"] = "error"
            return request_result

    def handle_user_response(self, request_id: str, user_response: Dict[str, Any]) -> Dict[str, Any]:
        """处理用户响应"""
        response_result = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "status": "processing",
            "next_actions": [],
            "updated_workflow": {}
        }

        try:
            # 根据当前工作流程阶段处理用户响应
            current_stage = self.workflow_state.get("current_stage")

            if current_stage == WorkflowStage.INITIALIZATION.value:
                return self._handle_initialization_response(response_result, user_response)
            elif current_stage == WorkflowStage.SETTINGS_CHECK.value:
                return self._handle_settings_response(response_result, user_response)
            elif current_stage == WorkflowStage.CHAPTER_PLANNING.value:
                return self._handle_chapter_planning_response(response_result, user_response)
            elif current_stage == WorkflowStage.CHAPTER_CREATION.value:
                return self._handle_chapter_creation_response(response_result, user_response)
            elif current_stage == WorkflowStage.CHAPTER_REVIEW.value:
                return self._handle_chapter_review_response(response_result, user_response)
            else:
                response_result["status"] = "error"
                response_result["message"] = f"未知的工作流程阶段: {current_stage}"
                return response_result

        except Exception as e:
            response_result["status"] = "error"
            response_result["error"] = str(e)
            return response_result

    def review_chapter(self, chapter_number: int) -> Dict[str, Any]:
        """审阅章节"""
        review_result = {
            "chapter_number": chapter_number,
            "timestamp": datetime.now().isoformat(),
            "chapter_content": None,
            "review_suggestions": [],
            "modification_options": [],
            "approval_status": "pending"
        }

        try:
            # 获取章节内容
            chapter_content = self._get_chapter_content(chapter_number)
            review_result["chapter_content"] = chapter_content

            if not chapter_content:
                review_result["status"] = "error"
                review_result["message"] = f"章节 {chapter_number} 不存在"
                return review_result

            # 分析章节内容
            content_analysis = self._analyze_chapter_content(chapter_content)
            review_result["content_analysis"] = content_analysis

            # 生成审阅建议
            review_suggestions = self._generate_review_suggestions(chapter_number, content_analysis)
            review_result["review_suggestions"] = review_suggestions

            # 生成修改选项
            modification_options = self._generate_modification_options(chapter_number)
            review_result["modification_options"] = modification_options

            review_result["status"] = "ready_for_review"

        except Exception as e:
            review_result["status"] = "error"
            review_result["error"] = str(e)

        return review_result

    def approve_chapter(self, chapter_number: int, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """批准章节为成品"""
        approval_result = {
            "chapter_number": chapter_number,
            "timestamp": datetime.now().isoformat(),
            "status": "processing",
            "moved_files": [],
            "updated_memories": []
        }

        try:
            # 移动章节到成品目录
            move_result = self._move_chapter_to_manuscript(chapter_number)
            approval_result["moved_files"] = move_result

            if move_result["success"]:
                # 更新相关记忆
                memory_update = self._update_chapter_memories(chapter_number)
                approval_result["updated_memories"] = memory_update

                # 更新进度记录
                self._record_chapter_completion(chapter_number, approval_data)

                approval_result["status"] = "completed"
                approval_result["message"] = f"章节 {chapter_number} 已批准为成品"
            else:
                approval_result["status"] = "error"
                approval_result["message"] = f"移动章节失败: {move_result['message']}"

        except Exception as e:
            approval_result["status"] = "error"
            approval_result["error"] = str(e)

        return approval_result

    def get_workflow_progress(self) -> Dict[str, Any]:
        """获取工作流程进度"""
        return {
            "current_stage": self.workflow_state.get("current_stage"),
            "completed_chapters": self._get_completed_chapters(),
            "total_chapters": self._get_total_chapters(),
            "workflow_history": self.progress_history,
            "next_actions": self._get_next_workflow_actions(),
            "estimated_completion": self._estimate_completion()
        }

    # 私有方法

    def _load_workflow_state(self) -> Dict[str, Any]:
        """加载工作流程状态"""
        if self.workflow_file.exists():
            try:
                with open(self.workflow_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "current_stage": None,
            "current_chapter": None,
            "workflow_id": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def _save_workflow_state(self):
        """保存工作流程状态"""
        self.workflow_state["updated_at"] = datetime.now().isoformat()
        self.workflow_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.workflow_file, 'w', encoding='utf-8') as f:
            json.dump(self.workflow_state, f, ensure_ascii=False, indent=2)

    def _load_progress_history(self) -> List[Dict[str, Any]]:
        """加载进度历史"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        return []

    def _save_progress_history(self):
        """保存进度历史"""
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress_history, f, ensure_ascii=False, indent=2)

    def _generate_request_id(self) -> str:
        """生成请求ID"""
        return f"req_{int(datetime.now().timestamp())}"

    def _check_initialization_status(self) -> Dict[str, Any]:
        """检查初始化状态"""
        # 检查是否有项目状态文件
        status_file = self.project_path / "system" / "project_status.json"

        if status_file.exists():
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    project_status = json.load(f)
                return {
                    "is_initialized": True,
                    "initialization_time": project_status.get("scan_time"),
                    "project_status": project_status
                }
            except Exception:
                pass

        return {
            "is_initialized": False,
            "message": "项目未初始化"
        }

    def _handle_uninitialized_project(self, request_result: Dict[str, Any], user_request: Dict[str, Any]) -> Dict[str, Any]:
        """处理未初始化的项目"""
        request_result["current_stage"] = WorkflowStage.INITIALIZATION.value
        request_result["blocking_issues"].append("项目未初始化")

        # 检查是否有reference目录和材料
        reference_scan = self.project_initializer.scan_reference_directory()

        if reference_scan["total_materials"] > 0:
            # 有参考材料，可以开始初始化
            request_result["next_actions"].append({
                "action": "initialize_project",
                "description": f"发现 {reference_scan['total_materials']} 份参考材料，开始项目初始化",
                "requires_user_confirmation": False,
                "auto_proceed": True
            })

            # 设置AI任务用于分析参考材料
            request_result["ai_tasks"].append({
                "task_type": "analyze_reference_materials",
                "materials": reference_scan["materials_by_type"],
                "purpose": "project_initialization"
            })
        else:
            # 没有参考材料，需要用户提供
            request_result["next_actions"].append({
                "action": "request_reference_materials",
                "description": "请将参考材料放入 reference/ 目录，然后重新请求",
                "requires_user_confirmation": True,
                "instructions": [
                    "创建 reference/ 目录",
                    "将世界观、角色、情节等参考材料放入目录",
                    "支持 .md, .txt, .docx 等格式",
                    "重新发送创作请求"
                ]
            })

        # 更新工作流程状态
        self.workflow_state["current_stage"] = WorkflowStage.INITIALIZATION.value
        self._save_workflow_state()

        request_result["status"] = "initialization_required"
        return request_result

    def _check_settings_completeness(self) -> Dict[str, Any]:
        """检查设定完整性"""
        return self.settings_checker.check_all_settings_completeness()

    def _handle_incomplete_settings(self, request_result: Dict[str, Any], user_request: Dict[str, Any]) -> Dict[str, Any]:
        """处理设定不完整的情况"""
        request_result["current_stage"] = WorkflowStage.SETTINGS_CHECK.value
        settings_status = request_result["settings_status"]

        # 生成用户引导
        user_guidance = self.settings_checker.generate_user_guidance(settings_status)
        request_result["user_guidance"] = user_guidance

        # 添加缺失项到阻塞问题
        for missing_item in settings_status["missing_items"]:
            request_result["blocking_issues"].append(f"设定缺失: {missing_item}")

        # 生成下一步行动
        if user_guidance["priority_actions"]:
            for action in user_guidance["priority_actions"]:
                if action["priority"] == "high":
                    request_result["next_actions"].append({
                        "action": "complete_missing_settings",
                        "description": action["description"],
                        "requires_user_input": True,
                        "setting_type": self._identify_setting_type(action["description"])
                    })

        # 检查是否需要AI生成设定
        if settings_status["overall_score"] < 40:
            request_result["ai_tasks"].append({
                "task_type": "generate_missing_settings",
                "missing_categories": self._identify_missing_categories(settings_status),
                "existing_settings": self._summarize_existing_settings(settings_status)
            })

        # 更新工作流程状态
        self.workflow_state["current_stage"] = WorkflowStage.SETTINGS_CHECK.value
        self._save_workflow_state()

        request_result["status"] = "settings_incomplete"
        return request_result

    def _prepare_next_chapter(self) -> Dict[str, Any]:
        """准备下一章节"""
        # 获取现有章节
        existing_chapters = self.chapter_outline_generator._get_existing_chapters()

        # 确定下一章节号
        if existing_chapters:
            next_chapter = max(ch["chapter_number"] for ch in existing_chapters) + 1
        else:
            next_chapter = 1

        # 准备章节创作
        preparation = self.chapter_outline_generator.prepare_chapter_creation(next_chapter)
        preparation["next_chapter_number"] = next_chapter
        preparation["existing_chapters"] = existing_chapters

        return preparation

    def _handle_chapter_preparation_issues(self, request_result: Dict[str, Any], user_request: Dict[str, Any]) -> Dict[str, Any]:
        """处理章节准备问题"""
        request_result["current_stage"] = WorkflowStage.CHAPTER_PLANNING.value
        chapter_prep = request_result["chapter_preparation"]

        # 添加阻塞问题
        for issue in chapter_prep.get("blocking_issues", []):
            request_result["blocking_issues"].append(f"章节准备问题: {issue}")

        # 生成梗概建议
        suggestions = self.chapter_outline_generator.generate_outline_suggestions(
            chapter_prep["next_chapter_number"]
        )
        request_result["outline_suggestions"] = suggestions

        # 添加下一步行动
        request_result["next_actions"].append({
            "action": "create_chapter_outline",
            "description": "创建章节梗概",
            "chapter_number": chapter_prep["next_chapter_number"],
            "requires_user_input": True,
            "outline_options": suggestions.get("outline_options", [])
        })

        # 如果需要AI生成梗概
        if suggestions.get("ai_task_required"):
            request_result["ai_tasks"].append(suggestions["ai_task"])

        # 更新工作流程状态
        self.workflow_state["current_stage"] = WorkflowStage.CHAPTER_PLANNING.value
        self.workflow_state["current_chapter"] = chapter_prep["next_chapter_number"]
        self._save_workflow_state()

        request_result["status"] = "chapter_planning_required"
        return request_result

    def _start_chapter_creation_workflow(self, request_result: Dict[str, Any], user_request: Dict[str, Any]) -> Dict[str, Any]:
        """开始章节创作工作流程"""
        request_result["current_stage"] = WorkflowStage.CHAPTER_CREATION.value
        chapter_prep = request_result["chapter_preparation"]
        chapter_number = chapter_prep["next_chapter_number"]

        # 记录进度
        progress_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "start_chapter_creation",
            "chapter_number": chapter_number,
            "status": "started"
        }
        self.progress_history.append(progress_entry)
        self._save_progress_history()

        # 准备AI生成任务
        context_data = self._prepare_chapter_creation_context(chapter_number, chapter_prep)

        request_result["ai_tasks"].append({
            "task_type": "generate_chapter_content",
            "chapter_number": chapter_number,
            "context": context_data,
            "requirements": {
                "word_count": "2000-3000字",
                "style": "consistent_with_existing",
                "include_previous_context": True
            }
        })

        # 添加下一步行动
        request_result["next_actions"].append({
            "action": "generate_chapter_content",
            "description": f"生成第 {chapter_number} 章内容",
            "chapter_number": chapter_number,
            "requires_ai_generation": True
        })

        # 更新工作流程状态
        self.workflow_state["current_stage"] = WorkflowStage.CHAPTER_CREATION.value
        self.workflow_state["current_chapter"] = chapter_number
        self._save_workflow_state()

        request_result["status"] = "ready_for_generation"
        return request_result

    def _prepare_chapter_creation_context(self, chapter_number: int, chapter_prep: Dict[str, Any]) -> Dict[str, Any]:
        """准备章节创作上下文"""
        context = {
            "chapter_number": chapter_number,
            "project_settings": self.settings_checker.check_all_settings_completeness(),
            "previous_chapters": self._get_previous_chapters_summary(chapter_number),
            "chapter_context": chapter_prep.get("chapter_context", {}),
            "outline_suggestions": chapter_prep.get("suggestions", {}),
            "existing_outline": chapter_prep.get("existing_outline")
        }

        return context

    def _get_previous_chapters_summary(self, chapter_number: int) -> List[Dict[str, Any]]:
        """获取前面章节的摘要"""
        existing_chapters = self.chapter_outline_generator._get_existing_chapters()
        previous_chapters = []

        for chapter in existing_chapters:
            if chapter["chapter_number"] < chapter_number:
                try:
                    # 获取章节内容摘要
                    chapter_file = self.project_path / chapter["directory"] / f"{Path(chapter['directory']).name}.md"
                    if chapter_file.exists():
                        content = chapter_file.read_text(encoding='utf-8')
                        previous_chapters.append({
                            "chapter_number": chapter["chapter_number"],
                            "title": chapter.get("title", f"第{chapter['chapter_number']}章"),
                            "word_count": len(content),
                            "summary": content[:200] + "..." if len(content) > 200 else content
                        })
                except Exception:
                    pass

        return previous_chapters

    def _handle_initialization_response(self, response_result: Dict[str, Any], user_response: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化响应"""
        if user_response.get("action") == "proceed_with_initialization":
            # 执行项目初始化
            init_result = self.project_initializer.run_initialization()
            response_result["initialization_result"] = init_result

            if init_result.get("success"):
                response_result["next_actions"].append({
                    "action": "check_settings_completeness",
                    "description": "初始化完成，检查设定完整性"
                })

                # 更新工作流程状态
                self.workflow_state["current_stage"] = WorkflowStage.SETTINGS_CHECK.value
                self._save_workflow_state()
            else:
                response_result["status"] = "error"
                response_result["message"] = "初始化失败"

        response_result["status"] = "completed"
        return response_result

    def _handle_settings_response(self, response_result: Dict[str, Any], user_response: Dict[str, Any]) -> Dict[str, Any]:
        """处理设定响应"""
        if user_response.get("action") == "settings_completed":
            # 重新检查设定完整性
            settings_status = self.settings_checker.check_all_settings_completeness()
            response_result["settings_status"] = settings_status

            if settings_status["ready_for_writing"]:
                response_result["next_actions"].append({
                    "action": "prepare_chapter_creation",
                    "description": "设定完整，准备章节创作"
                })

                # 更新工作流程状态
                self.workflow_state["current_stage"] = WorkflowStage.CHAPTER_PLANNING.value
                self._save_workflow_state()
            else:
                response_result["status"] = "incomplete"
                response_result["message"] = "设定仍不完整"

        response_result["status"] = "completed"
        return response_result

    def _handle_chapter_planning_response(self, response_result: Dict[str, Any], user_response: Dict[str, Any]) -> Dict[str, Any]:
        """处理章节规划响应"""
        if user_response.get("action") == "outline_completed":
            chapter_number = user_response.get("chapter_number")
            outline_data = user_response.get("outline_data")

            if outline_data:
                # 保存章节梗概
                save_result = self.chapter_outline_generator.save_chapter_outline(chapter_number, outline_data)
                response_result["outline_save_result"] = save_result

                if save_result.get("success"):
                    response_result["next_actions"].append({
                        "action": "generate_chapter_content",
                        "description": f"梗概已保存，开始生成第 {chapter_number} 章内容"
                    })

                    # 更新工作流程状态
                    self.workflow_state["current_stage"] = WorkflowStage.CHAPTER_CREATION.value
                    self._save_workflow_state()
                else:
                    response_result["status"] = "error"
                    response_result["message"] = "保存梗概失败"

        response_result["status"] = "completed"
        return response_result

    def _handle_chapter_creation_response(self, response_result: Dict[str, Any], user_response: Dict[str, Any]) -> Dict[str, Any]:
        """处理章节创作响应"""
        if user_response.get("action") == "content_generated":
            chapter_number = user_response.get("chapter_number")
            content = user_response.get("content")

            if content:
                # 保存章节内容
                save_result = self._save_chapter_content(chapter_number, content)
                response_result["content_save_result"] = save_result

                if save_result.get("success"):
                    response_result["next_actions"].append({
                        "action": "review_chapter",
                        "description": f"章节内容已保存，可以开始审阅第 {chapter_number} 章"
                    })

                    # 记录进度
                    progress_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "action": "chapter_content_saved",
                        "chapter_number": chapter_number,
                        "word_count": len(content),
                        "status": "completed"
                    }
                    self.progress_history.append(progress_entry)
                    self._save_progress_history()

                    # 更新工作流程状态
                    self.workflow_state["current_stage"] = WorkflowStage.CHAPTER_REVIEW.value
                    self._save_workflow_state()
                else:
                    response_result["status"] = "error"
                    response_result["message"] = "保存内容失败"

        response_result["status"] = "completed"
        return response_result

    def _handle_chapter_review_response(self, response_result: Dict[str, Any], user_response: Dict[str, Any]) -> Dict[str, Any]:
        """处理章节审阅响应"""
        if user_response.get("action") == "approve_chapter":
            chapter_number = user_response.get("chapter_number")
            approval_data = user_response.get("approval_data", {})

            # 批准章节
            approval_result = self.approve_chapter(chapter_number, approval_data)
            response_result["approval_result"] = approval_result

            if approval_result.get("status") == "completed":
                response_result["next_actions"].append({
                    "action": "continue_to_next_chapter",
                    "description": f"第 {chapter_number} 章已批准，可以继续创作下一章"
                })

                # 重置工作流程状态，准备下一章
                self.workflow_state["current_stage"] = None
                self.workflow_state["current_chapter"] = None
                self._save_workflow_state()

        response_result["status"] = "completed"
        return response_result

    # 辅助方法
    def _identify_setting_type(self, description: str) -> str:
        """识别设定类型"""
        description_lower = description.lower()
        if "世界观" in description_lower or "世界" in description_lower:
            return "worldview"
        elif "角色" in description_lower:
            return "characters"
        elif "情节" in description_lower:
            return "plot"
        elif "环境" in description_lower:
            return "environments"
        elif "写作风格" in description_lower:
            return "writing_style"
        return "unknown"

    def _identify_missing_categories(self, settings_status: Dict[str, Any]) -> List[str]:
        """识别缺失的设定类别"""
        missing_categories = []
        category_results = settings_status.get("category_results", {})

        for category, result in category_results.items():
            if result.get("completeness_score", 0) < 5:  # 基本没有内容
                missing_categories.append(category)

        return missing_categories

    def _summarize_existing_settings(self, settings_status: Dict[str, Any]) -> Dict[str, Any]:
        """总结现有设定"""
        return {
            "overall_score": settings_status.get("overall_score", 0),
            "existing_categories": list(settings_status.get("category_results", {}).keys()),
            "ready_for_writing": settings_status.get("ready_for_writing", False)
        }

    def _get_chapter_content(self, chapter_number: int) -> Optional[str]:
        """获取章节内容"""
        chapter_file = self.project_path / "draft" / "chapters" / f"chapter_{chapter_number:02d}" / f"chapter_{chapter_number:02d}.md"
        if chapter_file.exists():
            return chapter_file.read_text(encoding='utf-8')
        return None

    def _analyze_chapter_content(self, content: str) -> Dict[str, Any]:
        """分析章节内容"""
        return {
            "word_count": len(content),
            "paragraph_count": len([p for p in content.split('\n') if p.strip()]),
            "dialogue_ratio": self._calculate_dialogue_ratio(content),
            "readability_score": self._calculate_readability_score(content)
        }

    def _calculate_dialogue_ratio(self, content: str) -> float:
        """计算对话比例"""
        lines = content.split('\n')
        dialogue_lines = sum(1 for line in lines if '「' in line or '"' in line)
        return dialogue_lines / len(lines) if lines else 0

    def _calculate_readability_score(self, content: str) -> float:
        """计算可读性分数"""
        # 简化的可读性计算
        sentences = content.count('。') + content.count('！') + content.count('？')
        avg_sentence_length = len(content) / sentences if sentences > 0 else 0

        # 理想句子长度为15-20字
        if 15 <= avg_sentence_length <= 20:
            return 1.0
        elif avg_sentence_length < 15:
            return 0.8
        else:
            return max(0.6, 1.0 - (avg_sentence_length - 20) / 50)

    def _generate_review_suggestions(self, chapter_number: int, content_analysis: Dict[str, Any]) -> List[str]:
        """生成审阅建议"""
        suggestions = []

        if content_analysis["word_count"] < 1500:
            suggestions.append("章节字数偏少，建议增加更多内容")
        elif content_analysis["word_count"] > 4000:
            suggestions.append("章节字数较多，考虑是否需要拆分")

        if content_analysis["dialogue_ratio"] < 0.2:
            suggestions.append("对话比例较低，建议增加角色对话")
        elif content_analysis["dialogue_ratio"] > 0.6:
            suggestions.append("对话比例较高，建议增加叙述和描写")

        if content_analysis["readability_score"] < 0.7:
            suggestions.append("句子长度可能过长，建议调整语言节奏")

        return suggestions

    def _generate_modification_options(self, chapter_number: int) -> List[Dict[str, Any]]:
        """生成修改选项"""
        return [
            {
                "option": "intelligent_edit",
                "description": "智能编辑章节内容",
                "requires_ai": True
            },
            {
                "option": "expand_content",
                "description": "扩展章节内容",
                "requires_ai": True
            },
            {
                "option": "adjust_style",
                "description": "调整写作风格",
                "requires_ai": True
            },
            {
                "option": "manual_edit",
                "description": "手动编辑",
                "requires_ai": False
            }
        ]

    def _move_chapter_to_manuscript(self, chapter_number: int) -> Dict[str, Any]:
        """移动章节到成品目录"""
        try:
            # 获取源文件路径
            draft_dir = self.project_path / "draft" / "chapters" / f"chapter_{chapter_number:02d}"
            manuscript_dir = self.project_path / "manuscript" / "chapters" / f"chapter_{chapter_number:02d}"

            if not draft_dir.exists():
                return {"success": False, "message": "草稿章节不存在"}

            # 创建目标目录
            manuscript_dir.mkdir(parents=True, exist_ok=True)

            # 复制文件
            moved_files = []
            for file_path in draft_dir.glob("*"):
                if file_path.is_file():
                    target_path = manuscript_dir / file_path.name
                    shutil.copy2(file_path, target_path)
                    moved_files.append(str(target_path.relative_to(self.project_path)))

            return {
                "success": True,
                "message": f"章节 {chapter_number} 已移动到成品目录",
                "moved_files": moved_files
            }

        except Exception as e:
            return {"success": False, "message": f"移动失败: {e}"}

    def _update_chapter_memories(self, chapter_number: int) -> Dict[str, Any]:
        """更新章节记忆"""
        try:
            # 应用记忆分析
            memory_result = self.memory_analyzer.apply_generated_memories(chapter_number, True)
            return {
                "success": True,
                "memory_result": memory_result
            }
        except Exception as e:
            return {"success": False, "message": f"记忆更新失败: {e}"}

    def _record_chapter_completion(self, chapter_number: int, approval_data: Dict[str, Any]):
        """记录章节完成"""
        completion_record = {
            "timestamp": datetime.now().isoformat(),
            "chapter_number": chapter_number,
            "approval_data": approval_data,
            "status": "completed"
        }

        self.progress_history.append(completion_record)
        self._save_progress_history()

    def _get_completed_chapters(self) -> List[int]:
        """获取已完成章节列表"""
        completed = []
        manuscript_dir = self.project_path / "manuscript" / "chapters"

        if manuscript_dir.exists():
            for chapter_dir in manuscript_dir.iterdir():
                if chapter_dir.is_dir() and chapter_dir.name.startswith("chapter_"):
                    chapter_match = re.search(r'chapter_(\d+)', chapter_dir.name)
                    if chapter_match:
                        completed.append(int(chapter_match.group(1)))

        return sorted(completed)

    def _get_total_chapters(self) -> int:
        """获取总章节数"""
        # 这里可以根据项目设定估算总章节数
        return 10  # 默认值，可以根据实际情况调整

    def _get_next_workflow_actions(self) -> List[str]:
        """获取下一步工作流程行动"""
        current_stage = self.workflow_state.get("current_stage")

        if current_stage is None:
            return ["开始新的章节创作"]
        elif current_stage == WorkflowStage.INITIALIZATION.value:
            return ["完成项目初始化"]
        elif current_stage == WorkflowStage.SETTINGS_CHECK.value:
            return ["完善项目设定"]
        elif current_stage == WorkflowStage.CHAPTER_PLANNING.value:
            return ["创建章节梗概"]
        elif current_stage == WorkflowStage.CHAPTER_CREATION.value:
            return ["生成章节内容"]
        elif current_stage == WorkflowStage.CHAPTER_REVIEW.value:
            return ["审阅章节内容"]
        else:
            return []

    def _estimate_completion(self) -> Dict[str, Any]:
        """估算完成度"""
        completed_chapters = len(self._get_completed_chapters())
        total_chapters = self._get_total_chapters()

        return {
            "completed_chapters": completed_chapters,
            "total_chapters": total_chapters,
            "completion_percentage": (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0,
            "estimated_remaining_chapters": total_chapters - completed_chapters
        }

    def _save_chapter_content(self, chapter_number: int, content: str) -> Dict[str, Any]:
        """保存章节内容"""
        try:
            chapter_dir = self.project_path / "draft" / "chapters" / f"chapter_{chapter_number:02d}"
            chapter_dir.mkdir(parents=True, exist_ok=True)

            # 保存Markdown文件
            md_file = chapter_dir / f"chapter_{chapter_number:02d}.md"
            md_file.write_text(content, encoding='utf-8')

            # 更新JSON文件
            json_file = chapter_dir / f"chapter_{chapter_number:02d}.json"
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    chapter_data = json.load(f)
            else:
                chapter_data = {
                    "metadata": {
                        "chapter": chapter_number,
                        "title": f"第{chapter_number}章",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                        "version": "1.0"
                    }
                }

            chapter_data["metadata"]["word_count"] = len(content)
            chapter_data["metadata"]["status"] = "draft"
            chapter_data["metadata"]["updated_at"] = datetime.now().isoformat()
            chapter_data["content"]["main_content"] = content

            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(chapter_data, f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "message": f"第 {chapter_number} 章内容已保存",
                "files": [
                    str(md_file.relative_to(self.project_path)),
                    str(json_file.relative_to(self.project_path))
                ]
            }

        except Exception as e:
            return {"success": False, "message": f"保存失败: {e}"}

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="交互式工作流程管理器")
    parser.add_argument("--project-path", default=".", help="项目路径")
    parser.add_argument("--action", choices=["create_request", "get_progress"], default="create_request", help="操作类型")
    parser.add_argument("--chapter", type=int, help="章节号")
    parser.add_argument("--review", action="store_true", help="审阅模式")

    args = parser.parse_args()

    manager = WorkflowManager(args.project_path)

    if args.action == "create_request":
        result = manager.process_creation_request()
    elif args.action == "get_progress":
        result = manager.get_workflow_progress()
    elif args.review and args.chapter:
        result = manager.review_chapter(args.chapter)
    else:
        result = {"error": "无效的参数组合"}

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()