#!/usr/bin/env python3
"""
小说生成器 - 会话管理器
负责断点续传、会话状态保存和恢复
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class SessionManager:
    """会话管理器，处理断点续传和状态持久化"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.session_file = self.project_path / "session_state.json"
        self.system_dir = self.project_path / "system"
        self.system_dir.mkdir(exist_ok=True)

    def create_session(self, mode: str = "setting", chapter: int = 0, **kwargs) -> Dict[str, Any]:
        """创建新会话"""
        session_data = {
            "session_id": f"session_{int(time.time())}",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "mode": mode,  # setting | writing
            "current_chapter": chapter,
            "project_path": str(self.project_path.absolute()),
            "context_state": {
                "token_limit": kwargs.get("token_limit", 128000),
                "compression_enabled": True,
                "last_compression_chapter": 0
            },
            "working_state": {
                "unsaved_changes": False,
                "current_section": "beginning",
                "generation_cache": {}
            },
            "navigation_history": [],
            "error_log": []
        }

        self.save_session(session_data)
        return session_data

    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """保存会话状态"""
        try:
            session_data["last_updated"] = datetime.now().isoformat()

            # 保存主会话文件
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

            # 创建备份
            backup_file = self.system_dir / f"session_backup_{int(time.time())}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

            # 清理旧备份（保留最近5个）
            self._cleanup_backups()

            return True
        except Exception as e:
            self._log_error(f"Failed to save session: {e}")
            return False

    def load_session(self) -> Optional[Dict[str, Any]]:
        """加载会话状态"""
        try:
            if not self.session_file.exists():
                return None

            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # 验证会话数据完整性
            if not self._validate_session(session_data):
                return None

            return session_data
        except Exception as e:
            self._log_error(f"Failed to load session: {e}")
            return None

    def update_session(self, updates: Dict[str, Any]) -> bool:
        """更新会话状态"""
        session_data = self.load_session()
        if not session_data:
            return False

        session_data.update(updates)
        session_data["last_updated"] = datetime.now().isoformat()

        return self.save_session(session_data)

    def switch_mode(self, new_mode: str, **kwargs) -> bool:
        """切换模式（setting <-> writing）"""
        session_data = self.load_session()
        if not session_data:
            return False

        old_mode = session_data["mode"]
        session_data["mode"] = new_mode

        # 记录导航历史
        session_data["navigation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "mode_switch",
            "from": old_mode,
            "to": new_mode,
            "details": kwargs
        })

        # 模式切换时的特殊处理
        if new_mode == "writing" and old_mode == "setting":
            # 从设定模式切换到写作模式，初始化写作环境
            session_data["current_chapter"] = 1
            session_data["working_state"]["current_section"] = "chapter_beginning"
        elif new_mode == "setting" and old_mode == "writing":
            # 从写作模式切换到设定模式，保存写作进度
            session_data["working_state"]["unsaved_changes"] = True

        return self.save_session(session_data)

    def jump_to_chapter(self, chapter_number: int, force: bool = False) -> bool:
        """跳转到指定章节"""
        session_data = self.load_session()
        if not session_data:
            return False

        current_chapter = session_data["current_chapter"]

        # 记录章节跳转
        session_data["navigation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "chapter_jump",
            "from_chapter": current_chapter,
            "to_chapter": chapter_number,
            "force": force
        })

        session_data["current_chapter"] = chapter_number
        session_data["working_state"]["current_section"] = "chapter_beginning"
        session_data["working_state"]["unsaved_changes"] = False

        return self.save_session(session_data)

    def get_session_info(self) -> Dict[str, Any]:
        """获取会话基本信息"""
        session_data = self.load_session()
        if not session_data:
            return {"status": "no_session"}

        return {
            "session_id": session_data["session_id"],
            "mode": session_data["mode"],
            "current_chapter": session_data["current_chapter"],
            "created_at": session_data["created_at"],
            "last_updated": session_data["last_updated"],
            "has_unsaved_changes": session_data["working_state"]["unsaved_changes"],
            "navigation_count": len(session_data["navigation_history"])
        }

    def _validate_session(self, session_data: Dict[str, Any]) -> bool:
        """验证会话数据完整性"""
        required_fields = ["session_id", "mode", "current_chapter", "created_at"]
        for field in required_fields:
            if field not in session_data:
                self._log_error(f"Missing required field in session: {field}")
                return False
        return True

    def _cleanup_backups(self):
        """清理旧的会话备份文件"""
        backup_files = list(self.system_dir.glob("session_backup_*.json"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        # 保留最新的5个备份
        for backup_file in backup_files[5:]:
            try:
                backup_file.unlink()
            except Exception as e:
                self._log_error(f"Failed to delete backup {backup_file}: {e}")

    def _log_error(self, message: str):
        """记录错误日志"""
        error_log_file = self.system_dir / "error_log.json"

        try:
            if error_log_file.exists():
                with open(error_log_file, 'r', encoding='utf-8') as f:
                    error_log = json.load(f)
            else:
                error_log = []

            error_log.append({
                "timestamp": datetime.now().isoformat(),
                "component": "session_manager",
                "message": message
            })

            # 保留最近100条错误记录
            error_log = error_log[-100:]

            with open(error_log_file, 'w', encoding='utf-8') as f:
                json.dump(error_log, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # 避免日志记录失败导致主流程异常

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="小说生成器会话管理器")
    parser.add_argument("--action", choices=["create", "load", "save", "update", "info"],
                       required=True, help="操作类型")
    parser.add_argument("--session-id", help="会话ID")
    parser.add_argument("--mode", choices=["setting", "writing"], help="模式")
    parser.add_argument("--chapter", type=int, help="章节号")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    sm = SessionManager(args.project_path)

    if args.action == "create":
        session = sm.create_session(mode=args.mode or "setting", chapter=args.chapter or 0)
        print(f"Created session: {session['session_id']}")

    elif args.action == "load":
        session = sm.load_session()
        if session:
            print(f"Loaded session: {session['session_id']}")
            print(f"Mode: {session['mode']}, Chapter: {session['current_chapter']}")
        else:
            print("No session found")

    elif args.action == "info":
        info = sm.get_session_info()
        print(json.dumps(info, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()