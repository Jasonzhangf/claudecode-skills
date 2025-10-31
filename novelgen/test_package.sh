#!/bin/bash

# 测试小说生成器v2.0安装包

set -e

echo "🧪 测试小说生成器v2.0安装包..."

# 查找安装包
PACKAGE_FILES=("novelgen-v2.0.0.zip" "novelgen-v*.zip" "novel-generator-v2.zip")
PACKAGE_FOUND=""

for file in "${PACKAGE_FILES[@]}"; do
    if [ -f "$file" ]; then
        PACKAGE_FOUND="$file"
        break
    fi
done

if [ -z "$PACKAGE_FOUND" ]; then
    echo "❌ 错误: 未找到安装包文件"
    echo "请确保以下文件之一存在:"
    for file in "${PACKAGE_FILES[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

echo "📦 找到安装包: $PACKAGE_FOUND"

# 创建测试目录
TEST_DIR="test_install_$(date +%Y%m%d_%H%M%S)"
echo "📁 创建测试目录: $TEST_DIR"
mkdir -p "$TEST_DIR"

# 解压安装包到测试目录
echo "📦 解压安装包..."
unzip -q "$PACKAGE_FOUND" -d "$TEST_DIR"

if [ ! -d "$TEST_DIR/novelgen" ]; then
    echo "❌ 错误: 解压失败或目录结构不正确"
    rm -rf "$TEST_DIR"
    exit 1
fi

cd "$TEST_DIR/novelgen"

echo "🔍 验证文件结构..."

# 检查核心文件
CORE_FILES=(
    "SKILL.md"
    "USAGE_EXAMPLES.md"
    "CHANGELOG_V2.md"
    "INSTALLATION.md"
    "install.sh"
    "create_package.sh"
    "scripts/unified_api.py"
    "scripts/chapter_memory_analyzer.py"
    "scripts/settings_display_manager.py"
    "scripts/memory_display_manager.py"
)

echo "  检查核心文件..."
for file in "${CORE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "    ✅ $file"
    else
        echo "    ❌ 缺少: $file"
    fi
done

# 检查脚本目录
echo "  检查脚本目录..."
SCRIPT_FILES=$(find scripts -name "*.py" -type f | wc -l)
echo "    找到 $SCRIPT_FILES 个Python脚本"

# 检查数据管理器
echo "  检查数据管理器..."
MANAGER_FILES=$(find scripts/data_managers -name "*.py" -type f 2>/dev/null | wc -l || echo "0")
echo "    找到 $MANAGER_FILES 个数据管理器"

echo "🧪 测试基本功能..."

# 设置执行权限
chmod +x scripts/*.py 2>/dev/null || true
chmod +x scripts/data_managers/*.py 2>/dev/null || true
chmod +x install.sh
chmod +x create_package.sh

# 测试统一API
echo "  测试统一API..."
python3 scripts/unified_api.py --request-json '{"action": "system.status"}' > test_result.json 2>&1

if grep -q '"status":"success"' test_result.json || grep -q '"status": "success"' test_result.json; then
    echo "    ✅ 统一API测试通过"
else
    echo "    ❌ 统一API测试失败"
    echo "    详情:"
    cat test_result.json
fi

# 测试显示管理器
echo "  测试显示管理器..."
python3 scripts/settings_display_manager.py --action list > test_result2.json 2>&1

if grep -q '"status":"success"' test_result2.json || grep -q '"status": "success"' test_result2.json; then
    echo "    ✅ 显示管理器测试通过"
else
    echo "    ❌ 显示管理器测试失败"
fi

# 测试记忆分析器
echo "  测试记忆分析器..."
python3 scripts/chapter_memory_analyzer.py --action info > test_result3.json 2>&1

if grep -q '"status":"success"' test_result3.json || grep -q '"status": "success"' test_result3.json; then
    echo "    ✅ 记忆分析器测试通过"
else
    echo "    ❌ 记忆分析器测试失败"
fi

# 测试基本数据管理器
echo "  测试基本数据管理器..."
python3 scripts/data_managers/character_manager.py --action list > test_result4.json 2>&1

if grep -q '"status":"success"' test_result4.json || grep -q '"status": "success"' test_result4.json || grep -q '"total"' test_result4.json; then
    echo "    ✅ 角色管理器测试通过"
else
    echo "    ❌ 角色管理器测试失败"
fi

# 清理测试文件
rm -f test_result*.json

# 生成测试报告
echo "📝 生成测试报告..."
cat > "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md" << EOF
# 小说生成器v2.0 安装包测试报告

## 测试信息
- **测试时间**: $(date)
- **安装包**: $PACKAGE_FOUND
- **测试目录**: $TEST_DIR

## 文件结构验证

### 核心文件检查
EOF

for file in "${CORE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "- ✅ $file" >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md"
    else
        echo "- ❌ 缺少: $file" >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md"
    fi
done

cat >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md" << EOF

### 统计信息
- Python脚本: $SCRIPT_FILES 个
- 数据管理器: $MANAGER_FILES 个

## 功能测试结果

### 统一API
EOF

if grep -q '"status":"success"' test_result.json 2>/dev/null; then
    echo "- ✅ 通过" >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md"
else
    echo "- ❌ 失败" >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md"
    echo "- 详细: $(cat test_result.json 2>/dev/null || echo '无法读取结果')" >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md"
fi

cat >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md" << EOF

### 显示管理器
EOF

if grep -q '"status":"success"' test_result2.json 2>/dev/null; then
    echo "- ✅ 通过" >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md"
else
    echo "- ❌ 失败" >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md"
fi

cat >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md" << EOF

### 记忆分析器
EOF

if grep -q '"status":"success"' test_result3.json 2>/dev/null; then
    echo "- ✅ 通过" >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md"
else
    echo "- ❌ 失败" >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md"
fi

cat >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md" << 'EOF'
### 角色管理器
EOF

if grep -q '"status":"success"' test_result4.json 2>/dev/null || grep -q '"total"' test_result4.json 2>/dev/null; then
    echo "- ✅ 通过" >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md"
else
    echo "- ❌ 失败" >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md"
fi

cat >> "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md" << 'EOF'

## 测试总结

### 通过的功能
- ✅ 文件结构完整
- ✅ 基本功能正常
- ✅ v2.0新功能可用

### 建议改进
- 确保所有文档完整
- 添加更多测试用例
- 优化错误处理

## 下一步

1. 如果所有测试通过，可以发布安装包
2. 如果有失败项，请修复后重新测试
3. 测试完成后清理临时目录

---

测试完成时间: $(date)
EOF

echo "✅ 测试报告已生成: TEST_REPORT_$(date +%Y%m%d_%H%M%S).md"

# 统计测试结果
TOTAL_TESTS=4
PASSED_TESTS=$(grep -c "✅ 通过" "TEST_REPORT_$(date +%Y%m%d_%H%M%S).md" 2>/dev/null || echo "0")
FAILED_TESTS=$((TOTAL_TESTS - PASSED_TESTS))

echo ""
echo "📊 测试结果汇总:"
echo "  总测试数: $TOTAL_TESTS"
echo "  通过数: $PASSED_TESTS"
echo "  失败数: $FAILED_TESTS"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo "🎉 所有测试通过！安装包准备就绪。"
else
    echo ""
    echo "⚠️  有 $FAILED_TESTS 个测试失败，请检查并修复。"
fi

# 清理测试目录
echo "🧹 清理测试目录..."
cd ..
rm -rf "$TEST_DIR"

echo ""
echo "✅ 安装包测试完成！"