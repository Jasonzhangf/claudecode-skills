"""
Sysmem - 项目架构链条化管理系统

自动化项目架构管理工具，提供智能项目扫描、数据驱动分析、
自动文档管理和架构健康监控功能。
"""

__version__ = "2.0.0"
__author__ = "Sysmem Team"
__email__ = "sysmem@example.com"

from pathlib import Path
import sys
import os

# 添加scripts目录到Python路径
script_dir = Path(__file__).parent.parent / "scripts"
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# 导入核心功能
try:
    from collect_data import ProjectDataCollector
    from scan_project import ProjectScanner
    from analyze_architecture import ArchitectureAnalyzer
    from update_claude_md import ClaudeMdUpdater
    from system_monitor import SystemMonitor
    from utils import SysmemUtils
except ImportError as e:
    # 如果在开发环境中，尝试从scripts目录导入
    pass

__all__ = [
    "ProjectDataCollector",
    "ProjectScanner",
    "ArchitectureAnalyzer",
    "ClaudeMdUpdater",
    "SystemMonitor",
    "SysmemUtils",
]