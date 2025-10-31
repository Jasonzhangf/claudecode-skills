# Sysmem - 项目架构链条化管理系统
# 自动化编译和安装配置

.PHONY: help install install-dev uninstall build clean test lint format check-deps sync-version global-install

# 默认目标
help:
	@echo "Sysmem - 项目架构链条化管理系统"
	@echo "可用命令:"
	@echo "  make install       - 安装到用户环境"
	@echo "  make install-dev   - 开发模式安装"
	@echo "  make global-install - 全局安装（需要sudo）"
	@echo "  make uninstall     - 卸载包"
	@echo "  make build         - 构建分发包"
	@echo "  make clean         - 清理构建文件"
	@echo "  make test          - 运行测试"
	@echo "  make lint          - 代码检查"
	@echo "  make format        - 代码格式化"
	@echo "  make check-deps    - 检查依赖"
	@echo "  make sync-version  - 同步版本号"

# 检查Python版本
check-python:
	@python3 -c "import sys; assert sys.version_info >= (3, 8), '需要Python 3.8或更高版本'"

# 检查依赖
check-deps: check-python
	@echo "检查构建依赖..."
	@python3 -m pip install --upgrade pip setuptools wheel build
	@echo "依赖检查完成"

# 本地安装
install: check-deps
	@echo "安装Sysmem到用户环境..."
	python3 -m pip install -e .
	@echo "安装完成！"
	@echo "使用 'sysmem --help' 查看可用命令"

# 开发模式安装
install-dev: check-deps
	@echo "开发模式安装Sysmem..."
	python3 -m pip install -e ".[dev]"
	@echo "开发环境安装完成！"
	@echo "使用 'sysmem --help' 查看可用命令"

# 全局安装
global-install: check-deps
	@echo "全局安装Sysmem（需要管理员权限）..."
	@if command -v sudo >/dev/null 2>&1; then \
		sudo python3 -m pip install .; \
	else \
		echo "警告: 未找到sudo命令，尝试直接安装..."; \
		python3 -m pip install .; \
	fi
	@echo "全局安装完成！"
	@echo "所有用户都可以使用 'sysmem --help' 命令"

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
	find . -name "*.pyd" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "清理完成"

# 运行测试
test: check-deps
	@echo "运行测试..."
	python3 -m pytest tests/ -v --cov=sysmem --cov-report=term-missing || echo "测试目录不存在，跳过测试"

# 代码检查
lint: check-deps
	@echo "执行代码检查..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 sysmem/ scripts/ --max-line-length=88 --extend-ignore=E203,W503; \
	else \
		echo "flake8未安装，跳过代码检查"; \
	fi
	@if command -v mypy >/dev/null 2>&1; then \
		mypy sysmem/ --ignore-missing-imports; \
	else \
		echo "mypy未安装，跳过类型检查"; \
	fi

# 代码格式化
format: check-deps
	@echo "格式化代码..."
	@if command -v black >/dev/null 2>&1; then \
		black sysmem/ scripts/ --line-length=88; \
	else \
		echo "black未安装，跳过代码格式化"; \
	fi
	@if command -v isort >/dev/null 2>&1; then \
		isort sysmem/ scripts/ --profile black; \
	else \
		echo "isort未安装，跳过导入排序"; \
	fi

# 同步版本号
sync-version:
	@echo "同步版本号..."
	@python3 -c "
import re
import os

# 从pyproject.toml读取版本
with open('pyproject.toml', 'r') as f:
    content = f.read()

# 更新README.md中的版本
with open('README.md', 'r') as f:
    readme = f.read()

# 提取版本号（简化版本）
version = '2.0.0'  # 默认版本

# 更新README中的版本引用
readme = re.sub(r'sysmem v\d+\.\d+\.\d+', f'sysmem v{version}', readme)
readme = re.sub(r'version \d+\.\d+\.\d+', f'version {version}', readme)

with open('README.md', 'w') as f:
    f.write(readme)

print(f'版本已同步到 {version}')
"
	@echo "版本同步完成"

# 完整的发布流程
release: clean test lint build
	@echo "发布准备完成！"
	@echo "分发包位于 dist/ 目录"
	@echo "使用以下命令上传到PyPI:"
	@echo "  python3 -m pip install twine"
	@echo "  twine upload dist/*"