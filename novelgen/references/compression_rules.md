# 压缩规则和策略

## 压缩策略概述

小说生成器采用三层压缩机制来管理长篇小说的上下文信息，确保在有限的token窗口内保持故事的连贯性和完整性。

## 压缩层级定义

### 第一层：近期压缩 (Recent Compression)
- **目标压缩比例**: 10% (20,000 tokens → 2,000 tokens)
- **适用章节**: 最新10章
- **保留内容**: 详细事件、重要对话、关键场景、情感节点
- **压缩频率**: 每章完成时触发
- **存储位置**: `manuscript/chapters/chapter_XX/compression/recent/`

### 第二层：中期压缩 (Medium Compression)
- **目标压缩比例**: 2.5% (20,000 tokens → 500 tokens)
- **适用章节**: 前40章 (第11-50章)
- **保留内容**: 关键情节点、主要角色发展、重要转折
- **压缩频率**: 每10章触发批量压缩
- **存储位置**: `manuscript/chapters/chapter_XX/compression/medium/`

### 第三层：长期压缩 (Long-term Compression)
- **目标压缩比例**: 0.5% (20,000 tokens → 100 tokens)
- **适用章节**: 50章以前
- **保留内容**: 主要故事线、角色结局方向、核心主题
- **压缩频率**: 每50章触发批量压缩
- **存储位置**: `manuscript/chapters/chapter_XX/compression/long_term/`

## 压缩触发条件

### 自动触发
1. **章节完成时**: 章节状态更新为 "completed" 时自动触发近期压缩
2. **批量压缩点**: 每10章自动触发中期压缩，每50章自动触发长期压缩
3. **章节跳转时**: 跳转到新章节时检查是否需要更新压缩数据

### 手动触发
1. **用户请求**: 用户可以手动指定章节范围进行压缩
2. **压缩失败恢复**: 自动压缩失败时提供手动重试选项
3. **数据修正**: 发现压缩数据错误时手动重新压缩

## 压缩内容选择规则

### 近期压缩内容选择
```python
近期压缩保留优先级:
1. 情节推进事件 (权重: 0.9)
2. 主要角色对话 (权重: 0.8)
3. 场景变化描述 (权重: 0.7)
4. 情感转折点 (权重: 0.8)
5. 重要物品/线索 (权重: 0.6)
6. 次要角色互动 (权重: 0.4)
7. 环境描写 (权重: 0.3)
```

### 中期压缩内容选择
```python
中期压缩保留优先级:
1. 主要情节转折 (必须保留)
2. 角色重大决定 (必须保留)
3. 关系变化 (权重: 0.9)
4. 冲突升级 (权重: 0.8)
5. 重要发现 (权重: 0.7)
6. 次要情节节点 (权重: 0.5)
```

### 长期压缩内容选择
```python
长期压缩保留优先级:
1. 故事主线发展 (必须保留)
2. 角色终极目标 (必须保留)
3. 核心冲突解决 (必须保留)
4. 主题发展 (权重: 0.8)
5. 世界观重大变化 (权重: 0.7)
```

## 压缩算法规则

### 文本摘要算法
1. **句子重要性评分**
   - 包含关键词的句子加分
   - 情感强烈的句子加分
   - 动作动词多的句子加分
   - 包含角色名称的句子加分

2. **段落重要性评分**
   - 包含多个重要句子的段落
   - 段落位置权重 (开头和结尾段落权重更高)
   - 段落长度适中 (过长或过短降权)

3. **对话保留策略**
   - 保留揭示角色性格的对话
   - 保留推进情节的对话
   - 保留表达重要情感的对话
   - 压缩功能性对话 (如问候、道别)

### 信息提取规则
1. **实体识别**
   - 角色名称 (必须保留)
   - 重要地点 (高权重)
   - 关键物品 (中权重)
   - 时间标记 (中权重)

2. **事件识别**
   - 动作事件 (高权重)
   - 对话事件 (中权重)
   - 心理活动 (低权重)
   - 环境描述 (低权重)

3. **情感识别**
   - 强烈情感表达 (必须保留)
   - 情感转折点 (高权重)
   - 情感铺垫 (中权重)
   - 情感余韵 (低权重)

## 压缩质量控制

### 压缩比例控制
```python
def adjust_compression_level(compressed_data, target_tokens):
    current_tokens = estimate_tokens(compressed_data)

    if current_tokens <= target_tokens:
        return compressed_data

    # 按优先级逐步减少内容
    priority_removal = [
        ("legacy_notes", 0.9),      # 移除90%
        ("environmental_desc", 0.7), # 移除70%
        ("minor_dialogues", 0.5),    # 移除50%
        ("secondary_events", 0.3),   # 移除30%
        ("plot_points", 0.1)         # 移除10%
    ]

    for section, removal_ratio in priority_removal:
        if current_tokens <= target_tokens:
            break
        compressed_data = remove_section(compressed_data, section, removal_ratio)
        current_tokens = estimate_tokens(compressed_data)

    return compressed_data
```

### 一致性检查规则
1. **角色一致性**
   - 角色性格特征不能矛盾
   - 角色关系变化要合理
   - 角色能力发展要连贯

2. **情节一致性**
   - 时间线不能混乱
   - 因果关系要合理
   - 逻辑链条要完整

3. **世界观一致性**
   - 世界规则不能冲突
   - 设定细节要统一
   - 逻辑框架要稳定

## 压缩存储规则

### 文件组织结构
```
manuscript/chapters/chapter_XX/compression/
├── recent/
│   ├── plot_summary.md          # 情节摘要
│   ├── character_actions.md     # 角色行动
│   ├── key_dialogues.md         # 关键对话
│   ├── scene_changes.md         # 场景变化
│   ├── emotional_beats.md       # 情感节点
│   ├── timeline_markers.md      # 时间标记
│   └── metadata.json            # 压缩元数据
├── medium/
│   ├── plot_summary.md          # 情节概要
│   ├── major_events.md          # 主要事件
│   ├── character_developments.md # 角色发展
│   ├── plot_advancements.md     # 情节推进
│   ├── key_relationships.md     # 关键关系
│   └── metadata.json
└── long_term/
    ├── major_arc.md             # 主要故事线
    ├── story_impact.md          # 故事影响
    ├── character_destinations.md # 角色结局
    ├── thematic_elements.md     # 主题元素
    ├── legacy_notes.md          # 传承要点
    └── metadata.json
```

### 元数据格式
```json
{
  "chapter": "number",
  "compression_type": "recent|medium|long_term",
  "compressed_at": "string (ISO 8601)",
  "original_tokens": "number",
  "compressed_tokens": "number",
  "compression_ratio": "number",
  "components": ["string"],
  "quality_score": "number (0-1)",
  "consistency_check": {
    "passed": "boolean",
    "issues": ["string"]
  }
}
```

## 压缩恢复机制

### 部分恢复规则
1. **触发条件**
   - 用户查询特定历史细节
   - 情节需要参考历史事件
   - 角色记忆需要激活

2. **恢复策略**
   - 从压缩文件中提取相关片段
   - 结合当前上下文补充细节
   - 保持与压缩数据的一致性

3. **恢复限制**
   - 恢复内容不能超过原始长度
   - 恢复信息必须与压缩数据兼容
   - 恢复操作需要记录日志

### 临时解压规则
```python
def temporary_decompress(chapter, compression_type, query_keywords):
    # 根据关键词临时解压相关内容
    compressed_data = load_compression_data(chapter, compression_type)
    relevant_content = extract_relevant_content(compressed_data, query_keywords)

    # 限制解压内容的token数量
    if estimate_tokens(relevant_content) > TEMP_DECOMPRESS_LIMIT:
        relevant_content = limit_content_size(relevant_content, TEMP_DECOMPRESS_LIMIT)

    return relevant_content
```

## 压缩性能优化

### 批量压缩优化
1. **并行处理**
   - 多章节同时压缩
   - 不同压缩类型并行执行
   - 异步保存压缩结果

2. **缓存策略**
   - 压缩结果缓存
   - 中间结果缓存
   - 失败结果缓存

3. **增量压缩**
   - 只压缩新增内容
   - 合并相似压缩结果
   - 避免重复压缩

### 内存管理
1. **分块处理**
   - 大文本分块压缩
   - 流式处理减少内存占用
   - 及时释放处理完的数据

2. **垃圾回收**
   - 定期清理临时数据
   - 回收不再使用的压缩缓存
   - 优化内存使用模式

## 错误处理规则

### 压缩失败处理
```python
def handle_compression_failure(chapter, compression_type, error):
    # 记录错误信息
    log_compression_error(chapter, compression_type, error)

    # 尝试降级压缩
    if compression_type == "recent":
        fallback_type = "medium"
    elif compression_type == "medium":
        fallback_type = "long_term"
    else:
        return {"status": "failed", "message": "无法进行降级压缩"}

    return attempt_fallback_compression(chapter, fallback_type)
```

### 数据损坏处理
1. **检测机制**
   - 压缩数据完整性校验
   - 元数据一致性检查
   - 内容格式验证

2. **恢复策略**
   - 从备份文件恢复
   - 重新执行压缩操作
   - 使用相邻章节数据推断

3. **预防措施**
   - 定期备份压缩数据
   - 校验压缩结果质量
   - 监控压缩操作状态