# Sysmem v2.0 一键安装信息

## 🌟 一键安装脚本

### Linux/macOS: `quick_install.sh`
- **智能环境检测**: 自动检测 Python、pip、Git 版本
- **项目变更检查**: Git 或文件时间变更检测
- **智能备份**: 自动备份现有安装
- **代码同步**: 验证并同步项目文件
- **自动安装**: 智能选择最佳安装方式
- **结果验证**: 验证安装是否成功
- **启动脚本**: 自动生成 sysmem 命令行工具
- **PATH配置**: 自动配置环境变量

### Windows: `quick_install.bat`
- **Windows环境适配**: 适配 Windows 命令行
- **Python检测**: 验证 Python 3.8+ 版本
- **智能安装**: 自动处理 Windows 安装流程
- **错误处理**: 完善的错误处理和提示

## 🚀 使用方法

### 快速开始
```bash
# Linux/macOS
./quick_install.sh

# Windows
quick_install.bat

# 或使用 Makefile
make quick-install
```

### 安装脚本功能对比

| 功能 | quick_install.sh | quick_install.bat | Makefile |
|------|-------------------|-------------------|----------|
| 智能环境检测 | ✅ | ✅ | ❌ |
| Git变更检测 | ✅ | ✅ | ❌ |
| 智能备份 | ✅ | ❌ | ❌ |
| 代码同步验证 | ✅ | ✅ | ❌ |
| PATH配置 | ✅ | ❌ | ❌ |
| 启动脚本生成 | ✅ | ❌ | ❌ |
| 依赖升级 | ✅ | ✅ | ✅ |
| 跨平台支持 | ✅ | ✅ | ✅ |

## 📋 安装后验证

安装完成后，运行以下命令验证安装：

```bash
# 验证安装
python3 -c "import sysmem; print(f'Sysmem安装成功')"

# 测试智能交互功能
python3 scripts/collect_data.py --interactive

# 查看可用模块
python3 scripts/collect_data.py --list-modules
```

## 🔧 故障排除

### 常见问题

1. **Python版本过低**
   - 需要 Python 3.8 或更高版本
   - 升级 Python 后重新运行安装脚本

2. **权限问题**
   - Linux/macOS: 使用普通用户运行，避免使用 sudo
   - Windows: 以管理员身份运行命令提示符

3. **网络问题**
   - 确保网络连接正常
   - 检查防火墙和代理设置

4. **依赖安装失败**
   - 升级 pip: `python3 -m pip install --upgrade pip`
   - 使用国内镜像: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/`

### 获取帮助

如果遇到问题，可以：
1. 查看详细日志：安装过程会显示详细的错误信息
2. 检查环境：确保 Python、pip、Git 可用
3. 查看文档：`cat README.md` 和 `cat INSTALLATION.md`
4. 手动安装：参考传统安装方式

## 📦 安装文件说明

- `quick_install.sh`: Linux/macOS 一键安装脚本
- `quick_install.bat`: Windows 一键安装脚本
- `scripts/install_project.py`: 智能安装检查脚本
- `Makefile`: 自动化构建工具
- `pyproject.toml`: Python 项目配置
- `setup.py`: 传统 Python 安装配置

## 🎉 安装成功标志

看到以下信息表示安装成功：

```
🎉 Sysmem v2.0.0 安装成功！

📋 快速开始:
1. 智能交互式更新: python3 scripts/collect_data.py --interactive
2. 列出可用模块: python3 scripts/collect_data.py --list-modules
3. 精确模块更新: python3 scripts/collect_data.py --module scripts
4. 查看完整帮助: python3 scripts/collect_data.py --help

💡 享受智能交互式项目管理体验！
```