#!/bin/bash

# Sysmem v2.0 一键安装脚本
# 智能检测系统环境，自动同步代码并安装

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="Sysmem"
PROJECT_VERSION="2.0.0"
PROJECT_DESCRIPTION="项目架构链条化管理系统 - 支持智能交互式更新"

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo -e "${PURPLE}🌟 $1${NC}"
}

# 显示欢迎信息
show_welcome() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║           🌟 $PROJECT_NAME v$PROJECT_VERSION 一键安装脚本          ║"
    echo "║                                                              ║"
    echo "║  $PROJECT_DESCRIPTION  ║"
    echo "║                                                              ║"
    echo "║  支持智能交互式更新、Git集成变更检测、模块化管理          ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检查系统环境
check_system() {
    log_header "检查系统环境"

    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="Windows"
    else
        OS="Unknown"
    fi

    log_info "操作系统: $OS"

    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        log_success "Python: $PYTHON_VERSION"

        # 检查Python版本
        PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
        PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

        if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 8 ]]; then
            log_success "Python版本满足要求 (>= 3.8)"
        else
            log_error "Python版本过低，需要 3.8 或更高版本"
            exit 1
        fi
    else
        log_error "未找到 Python3，请先安装 Python 3.8+"
        exit 1
    fi

    # 检查pip
    if command -v pip3 &> /dev/null; then
        PIP_VERSION=$(pip3 --version)
        log_success "pip: $PIP_VERSION"
    else
        log_warning "未找到 pip3，尝试使用 python -m pip"
    fi

    # 检查Git
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        log_success "Git: $GIT_VERSION"
    else
        log_warning "未找到 Git，某些功能可能受限"
    fi
}

# 检查项目变更
check_changes() {
    log_header "检查项目变更"

    if command -v git &> /dev/null && git rev-parse --git-dir &> /dev/null; then
        # Git仓库检查
        CHANGED_FILES=$(git status --porcelain | wc -l | tr -d ' ')
        if [[ $CHANGED_FILES -gt 0 ]]; then
            log_warning "检测到 $CHANGED_FILES 个文件变更"
            log_info "主要变更文件:"
            git status --porcelain | head -5 | while read line; do
                echo "   $line"
            done
            if [[ $CHANGED_FILES -gt 5 ]]; then
                echo "   ... 还有 $((CHANGED_FILES - 5)) 个文件"
            fi
        else
            log_success "工作目录干净，无未提交变更"
        fi
    else
        # 文件时间检查
        log_info "Git不可用，使用文件修改时间检测"
        RECENT_CHANGES=$(find . -name "*.py" -newer scripts/install_project.py 2>/dev/null | wc -l | tr -d ' ')
        if [[ $RECENT_CHANGES -gt 0 ]]; then
            log_warning "检测到 $RECENT_CHANGES 个Python文件最近修改"
        else
            log_success "未检测到最近修改的Python文件"
        fi
    fi
}

# 备份现有安装
backup_existing() {
    log_header "备份现有安装"

    # 检查是否已安装
    if python3 -c "import sysmem" 2>/dev/null; then
        INSTALLED_VERSION=$(python3 -c "import sysmem; print(getattr(sysmem, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
        log_info "发现已安装版本: $INSTALLED_VERSION"

        # 创建备份目录
        BACKUP_DIR="$HOME/.sysmem_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"

        # 备份配置文件
        if [[ -d "$HOME/.claude" ]]; then
            cp -r "$HOME/.claude" "$BACKUP_DIR/" 2>/dev/null || true
            log_success "配置文件已备份到: $BACKUP_DIR"
        fi

        # 备份已安装的包
        python3 -m pip show sysmem &>/dev/null && pip3 show sysmem > "$BACKUP_DIR/package_info.txt" 2>/dev/null || true
    else
        log_info "未发现现有安装"
    fi
}

# 同步代码到安装目录
sync_code() {
    log_header "同步代码到安装目录"

    # 检查项目结构
    if [[ ! -f "pyproject.toml" ]] && [[ ! -f "setup.py" ]]; then
        log_error "未找到项目配置文件 (pyproject.toml 或 setup.py)"
        exit 1
    fi

    log_success "项目结构验证通过"

    # 确保scripts目录可执行
    chmod +x scripts/*.py 2>/dev/null || true

    # 验证核心脚本
    CORE_SCRIPTS=(
        "scripts/collect_data.py"
        "scripts/install_project.py"
        "scripts/utils.py"
    )

    for script in "${CORE_SCRIPTS[@]}"; do
        if [[ -f "$script" ]]; then
            log_success "核心脚本存在: $script"
        else
            log_error "核心脚本缺失: $script"
            exit 1
        fi
    done
}

# 执行安装
perform_installation() {
    log_header "执行安装"

    # 升级pip
    log_info "升级pip..."
    python3 -m pip install --upgrade pip setuptools wheel

    # 安装项目
    log_info "安装 $PROJECT_NAME..."

    # 尝试用户模式安装
    if python3 -m pip install -e . --user; then
        log_success "用户模式安装成功"
        INSTALL_MODE="user"
    elif python3 -m pip install -e .; then
        log_success "系统模式安装成功"
        INSTALL_MODE="system"
    else
        log_error "安装失败"
        exit 1
    fi

    # 验证安装
    if python3 -c "import sysmem; print(f'Sysmem {getattr(sysmem, \"__version__\", \"unknown\")} 安装成功')" 2>/dev/null; then
        log_success "安装验证通过"
    else
        log_warning "安装验证失败，但安装可能已成功"
    fi
}

# 运行智能安装检查
run_smart_check() {
    log_header "运行智能安装检查"

    if [[ -f "scripts/install_project.py" ]]; then
        log_info "运行智能安装脚本..."
        python3 scripts/install_project.py
    else
        log_warning "智能安装脚本不存在，跳过"
    fi
}

# 生成启动脚本
generate_launcher() {
    log_header "生成启动脚本"

    LAUNCHER_DIR="$HOME/.local/bin"
    mkdir -p "$LAUNCHER_DIR"

    # 创建sysmem启动脚本
    cat > "$LAUNCHER_DIR/sysmem" << 'EOF'
#!/bin/bash
# Sysmem v2.0 启动脚本

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")/sysmem"

if [[ -f "$PROJECT_DIR/scripts/collect_data.py" ]]; then
    python3 "$PROJECT_DIR/scripts/collect_data.py" "$@"
else
    echo "错误: 找不到sysmem脚本"
    echo "请确保sysmem已正确安装"
    exit 1
fi
EOF

    chmod +x "$LAUNCHER_DIR/sysmem"

    # 检查PATH
    if [[ ":$PATH:" != *":$LAUNCHER_DIR:"* ]]; then
        log_warning "请将 $LAUNCHER_DIR 添加到 PATH 环境变量"
        echo "export PATH=\"\$PATH:$LAUNCHER_DIR\"" >> "$HOME/.bashrc" 2>/dev/null || true
        echo "export PATH=\"\$PATH:$LAUNCHER_DIR\"" >> "$HOME/.zshrc" 2>/dev/null || true
        log_info "已自动添加到 shell 配置文件"
    else
        log_success "启动脚本已添加到 PATH"
    fi

    log_success "启动脚本已创建: $LAUNCHER_DIR/sysmem"
}

# 显示完成信息
show_completion() {
    log_header "安装完成"

    echo -e "${GREEN}🎉 $PROJECT_NAME v$PROJECT_VERSION 安装成功！${NC}"
    echo ""
    echo -e "${CYAN}📋 快速开始:${NC}"
    echo "1. 智能交互式更新:"
    echo "   python3 scripts/collect_data.py --interactive"
    echo ""
    echo "2. 列出可用模块:"
    echo "   python3 scripts/collect_data.py --list-modules"
    echo ""
    echo "3. 精确模块更新:"
    echo "   python3 scripts/collect_data.py --module scripts"
    echo ""
    echo "4. 查看完整帮助:"
    echo "   python3 scripts/collect_data.py --help"
    echo ""
    echo -e "${CYAN}🔧 开发工具:${NC}"
    echo "• 代码分析: python3 scripts/unused_code_analyzer.py"
    echo "• 架构分析: python3 scripts/analyze_architecture.py"
    echo "• 文档更新: python3 scripts/update_claude_md.py"
    echo ""
    echo -e "${CYAN}📚 更多信息:${NC}"
    echo "• 项目文档: cat README.md"
    echo "• 安装指南: cat INSTALLATION.md"
    echo "• 智能功能: make interactive-demo"
    echo ""
    echo -e "${GREEN}💡 享受智能交互式项目管理体验！${NC}"
}

# 错误处理
handle_error() {
    log_error "安装过程中发生错误"
    log_info "请检查:"
    echo "1. Python 3.8+ 是否已安装"
    echo "2. pip 是否可用"
    echo "3. 网络连接是否正常"
    echo "4. 是否有足够的磁盘空间"
    echo ""
    echo "如需帮助，请查看: cat README.md"
    exit 1
}

# 主函数
main() {
    # 设置错误处理
    trap handle_error ERR

    # 显示欢迎信息
    show_welcome

    # 检查系统环境
    check_system

    # 检查项目变更
    check_changes

    # 备份现有安装
    backup_existing

    # 同步代码
    sync_code

    # 执行安装
    perform_installation

    # 运行智能检查
    run_smart_check

    # 生成启动脚本
    generate_launcher

    # 显示完成信息
    show_completion
}

# 检查是否以root权限运行
if [[ $EUID -eq 0 ]]; then
    log_warning "检测到root权限，建议使用普通用户安装"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 执行主函数
main "$@"