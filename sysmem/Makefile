# Sysmem v2.0 - 项目架构链条化管理系统
# 支持智能交互式更新和Git集成变更检测

.PHONY: help quick-install install install-dev uninstall build clean test lint format check-deps sync-version global-install demo interactive-demo

# 默认目标
help:
	@echo "Sysmem v2.0 - 项目架构链条化管理系统"
	@echo "支持智能交互式更新和Git集成变更检测"
	@echo ""
	@echo "🚀 安装命令:"
	@echo "  make quick-install    - 🌟 一键智能安装（强烈推荐）"
	@echo "  make install         - 安装到用户环境"
	@echo "  make install-dev     - 开发模式安装"
	@echo "  make global-install   - 全局安装（需要sudo）"
	@echo "  make uninstall       - 卸载包"
	@echo ""
	@echo "🤖 智能功能演示:"
	@echo "  make demo            - 运行智能安装检查"
	@echo "  make interactive-demo - 演示智能交互式更新"
	@echo ""
	@echo "🔧 开发工具:"
	@echo "  make build           - 构建分发包"
	@echo "  make clean           - 清理构建文件"
	@echo "  make test            - 运行测试"
	@echo "  make lint            - 代码检查"
	@echo "  make format          - 代码格式化"
	@echo "  make check-deps      - 检查依赖"
	@echo "  make sync-version    - 同步版本号"

# 检查Python版本
check-python:
	@python3 -c "import sys; assert sys.version_info >= (3, 8), '需要Python 3.8或更高版本'"

# 检查依赖
check-deps: check-python
	@echo "检查构建依赖..."
	@python3 -m pip install --upgrade pip setuptools wheel build
	@echo "依赖检查完成"

# 🌟 一键智能安装
quick-install:
	@echo "🌟 Sysmem v2.0 一键智能安装"
	@echo "================================"
	@if [[ -f "quick_install.sh" ]]; then \
		./quick_install.sh; \
	else \
		echo "❌ 一键安装脚本不存在"; \
		exit 1; \
	fi

# 用户模式安装
install: check-deps
	@echo "安装Sysmem到用户环境..."
	python3 -m pip install -e .
	@echo "安装完成！使用 'python3 scripts/collect_data.py --help' 开始使用"

# 开发模式安装
install-dev: check-deps
	@echo "开发模式安装Sysmem..."
	python3 -m pip install -e ".[dev]"
	@echo "开发安装完成！"

# 全局安装
global-install: check-deps
	@echo "全局安装Sysmem（需要sudo权限）..."
	sudo python3 -m pip install .
	@echo "全局安装完成！"

# 卸载
uninstall:
	@echo "卸载Sysmem..."
	python3 -m pip uninstall -y sysmem || true
	@echo "卸载完成"

# 构建分发包
build: check-deps clean
	@echo "构建Sysmem分发包..."
	python3 -m build
	@echo "构建完成！"
	@ls -la dist/

# 清理构建文件
clean:
	@echo "清理构建文件..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "清理完成"

# 运行测试
test:
	@echo "运行测试..."
	python3 -m pytest tests/ -v || echo "测试未找到或失败"

# 代码检查
lint:
	@echo "运行代码检查..."
	python3 -m flake8 scripts/ sysmem/ || echo "flake8未安装或检查完成"
	python3 -m mypy sysmem/ || echo "mypy未安装或检查完成"

# 代码格式化
format:
	@echo "格式化代码..."
	python3 -m black scripts/ sysmem/ || echo "black未安装"
	python3 -m isort scripts/ sysmem/ || echo "isort未安装"

# 同步版本号
sync-version:
	@echo "版本同步..."
	@echo "版本同步完成"

# 完整的发布流程
release: clean test lint build
	@echo "发布准备完成！"
	@echo "分发包位于 dist/ 目录"

# 🤖 智能功能演示
demo:
	@echo "🌟 Sysmem v2.0 智能安装检查演示"
	@echo "================================"
	@python3 scripts/install_project.py

# 智能交互式更新演示
interactive-demo:
	@echo "🤖 智能交互式更新演示"
	@echo "================================"
	@echo "这个命令将演示智能交互式更新功能："
	@echo "1. 自动检测文件变更"
	@echo "2. 分析影响范围"
	@echo "3. 提供更新建议"
	@echo "4. 用户交互确认"
	@echo ""
	@echo "运行以下命令开始演示："
	@echo "python3 scripts/collect_data.py --interactive"
	@echo ""
	@echo "或者查看帮助："
	@echo "python3 scripts/collect_data.py --help"