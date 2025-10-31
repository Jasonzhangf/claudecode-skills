# 上下文管理策略

## 上下文窗口管理概述

小说生成器的上下文管理系统负责在有限的token窗口内智能组装最相关的信息，确保AI在生成内容时拥有足够的背景知识和上下文连贯性。

## 上下文组装策略

### 基础组装规则
```python
def build_context(chapter, mode="writing"):
    context_components = []
    token_usage = 0

    # 1. 当前章节内容 (最高优先级)
    current_content = load_current_chapter(chapter)
    if current_content:
        context_components.append({
            "type": "current_chapter",
            "content": current_content,
            "tokens": estimate_tokens(current_content),
            "priority": 1
        })

    # 2. 压缩的历史内容 (按时间和重要性排序)
    compression_data = load_compression_context(chapter)
    context_components.extend(compression_data)

    # 3. 设定数据 (世界观、角色等)
    settings_data = load_settings_context()
    context_components.extend(settings_data)

    # 4. 按优先级和token限制调整
    return optimize_context_window(context_components, token_limit)
```

### 优先级排序规则
```python
PRIORITY_MAP = {
    "current_chapter": 1,      # 当前章节
    "setting": 2,              # 设定数据
    "recent_compression": 3,   # 近期压缩
    "medium_compression": 4,   # 中期压缩
    "long_term_compression": 5  # 长期压缩
}

def sort_components_by_priority(components):
    return sorted(components, key=lambda x: PRIORITY_MAP.get(x["type"], 10))
```

## 分层上下文策略

### 第一层：核心上下文 (40k tokens)
```python
CORE_CONTEXT = {
    "current_chapter": {
        "allocation": 40000,
        "content": "完整当前章节内容",
        "priority": "essential",
        "compressible": False
    }
}
```

### 第二层：相关设定 (30k tokens)
```python
SETTINGS_CONTEXT = {
    "worldview": {"allocation": 8000, "priority": "high"},
    "main_characters": {"allocation": 10000, "priority": "high"},
    "current_plot": {"allocation": 7000, "priority": "high"},
    "writing_style": {"allocation": 5000, "priority": "medium"}
}
```

### 第三层：历史压缩 (48k tokens)
```python
COMPRESSION_CONTEXT = {
    "recent_chapters": {
        "count": 10,
        "per_chapter": 2000,
        "total": 20000,
        "type": "detailed"
    },
    "medium_chapters": {
        "count": 40,
        "per_chapter": 500,
        "total": 20000,
        "type": "summary"
    },
    "long_term_chapters": {
        "count": "remaining",
        "per_chapter": 100,
        "total": 8000,
        "type": "outline"
    }
}
```

### 第四层：缓冲空间 (10k tokens)
```python
BUFFER_CONTEXT = {
    "working_memory": {"allocation": 5000},
    "system_prompts": {"allocation": 3000},
    "error_margin": {"allocation": 2000}
}
```

## 动态上下文调整

### 内容重要性评估
```python
def calculate_content_importance(content, context_type, chapter_distance):
    base_score = {
        "current_chapter": 1.0,
        "setting": 0.9,
        "recent_compression": 0.7,
        "medium_compression": 0.5,
        "long_term_compression": 0.3
    }.get(context_type, 0.1)

    # 距离衰减
    distance_decay = max(0.1, 1.0 - (chapter_distance * 0.02))

    # 内容质量评分
    quality_score = assess_content_quality(content)

    return base_score * distance_decay * quality_score
```

### 自适应Token分配
```python
def adaptive_token_allocation(components, total_limit):
    # 计算各组件的重要性权重
    total_importance = sum(c["importance"] for c in components)

    # 基于重要性分配token
    allocations = {}
    for component in components:
        if component["compressible"]:
            ideal_allocation = (component["importance"] / total_importance) * total_limit
            allocations[component["id"]] = min(ideal_allocation, component["max_tokens"])
        else:
            allocations[component["id"]] = component["required_tokens"]

    # 检查总分配是否超限
    total_allocated = sum(allocations.values())
    if total_allocated > total_limit:
        return balance_token_allocation(allocations, total_limit)

    return allocations
```

## 上下文缓存策略

### 多级缓存设计
```python
class ContextCache:
    def __init__(self):
        self.l1_cache = {}  # 当前章节缓存
        self.l2_cache = {}  # 近期章节缓存
        self.l3_cache = {}  # 压缩数据缓存
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }

    def get_context(self, chapter, context_type):
        cache_key = f"{chapter}_{context_type}"

        # L1缓存查找
        if cache_key in self.l1_cache:
            self.cache_stats["hits"] += 1
            return self.l1_cache[cache_key]

        # L2缓存查找
        if cache_key in self.l2_cache:
            self.cache_stats["hits"] += 1
            # 提升到L1缓存
            self.l1_cache[cache_key] = self.l2_cache[cache_key]
            return self.l2_cache[cache_key]

        # L3缓存查找
        if cache_key in self.l3_cache:
            self.cache_stats["hits"] += 1
            return self.l3_cache[cache_key]

        self.cache_stats["misses"] += 1
        return None
```

### 缓存失效策略
```python
def invalidate_cache(chapter, operation_type):
    if operation_type == "chapter_update":
        # 章节更新时，失效相关缓存
        invalidate_chapter_cache(chapter)
        invalidate_related_compression_cache(chapter)

    elif operation_type == "settings_change":
        # 设定变更时，失效所有设定相关缓存
        invalidate_settings_cache()

    elif operation_type == "compression_update":
        # 压缩更新时，失效相关压缩缓存
        invalidate_compression_cache(chapter)
```

## 上下文重建策略

### 章节跳转时的上下文重建
```python
def rebuild_context_for_jump(from_chapter, to_chapter):
    jump_direction = "forward" if to_chapter > from_chapter else "backward"

    # 保存当前上下文快照
    save_context_snapshot(from_chapter)

    # 清理不必要的数据
    if jump_direction == "forward":
        clean_forward_context(from_chapter)
    else:
        clean_backward_context(to_chapter)

    # 重建目标章节上下文
    new_context = build_context(to_chapter)

    # 验证上下文连续性
    if not validate_context_continuity(from_chapter, to_chapter, new_context):
        new_context = add_context_bridges(from_chapter, to_chapter, new_context)

    return new_context
```

### 上下文连续性验证
```python
def validate_context_continuity(from_chapter, to_chapter, context):
    continuity_issues = []

    # 检查角色状态连续性
    character_issues = check_character_continuity(from_chapter, to_chapter)
    continuity_issues.extend(character_issues)

    # 检查情节连续性
    plot_issues = check_plot_continuity(from_chapter, to_chapter)
    continuity_issues.extend(plot_issues)

    # 检查设定一致性
    setting_issues = check_setting_consistency(context)
    continuity_issues.extend(setting_issues)

    return {
        "is_continuous": len(continuity_issues) == 0,
        "issues": continuity_issues
    }
```

## 上下文优化策略

### Token使用优化
```python
def optimize_token_usage(context_components, target_tokens):
    optimized_components = []
    current_tokens = 0

    # 按重要性排序
    sorted_components = sorted(context_components,
                             key=lambda x: x["importance"], reverse=True)

    for component in sorted_components:
        if current_tokens >= target_tokens:
            break

        # 检查是否需要压缩组件
        if current_tokens + component["tokens"] > target_tokens:
            # 压缩组件内容
            compressed_component = compress_component(component,
                                                   target_tokens - current_tokens)
            if compressed_component:
                optimized_components.append(compressed_component)
                current_tokens += compressed_component["tokens"]
        else:
            optimized_components.append(component)
            current_tokens += component["tokens"]

    return optimized_components
```

### 内容质量评估
```python
def assess_content_quality(content):
    quality_score = 0.0

    # 信息密度评分
    info_density = calculate_information_density(content)
    quality_score += info_density * 0.3

    # 结构完整性评分
    structural_integrity = assess_structural_integrity(content)
    quality_score += structural_integrity * 0.2

    # 相关性评分
    relevance_score = calculate_content_relevance(content)
    quality_score += relevance_score * 0.3

    # 语言质量评分
    language_quality = assess_language_quality(content)
    quality_score += language_quality * 0.2

    return min(1.0, quality_score)
```

## 特殊上下文处理

### 记忆系统集成
```python
def integrate_memory_context(character_name, current_chapter):
    # 获取角色记忆
    character_memories = get_character_memories(character_name)

    # 根据章节时间筛选相关记忆
    relevant_memories = filter_memories_by_time(character_memories, current_chapter)

    # 按情感重要性排序
    sorted_memories = sorted(relevant_memories,
                           key=lambda x: x["emotional_weight"], reverse=True)

    # 限制记忆数量
    memory_context = format_memory_context(sorted_memories[:10])

    return {
        "type": "memory_context",
        "character": character_name,
        "content": memory_context,
        "tokens": estimate_tokens(memory_context),
        "priority": 2.5
    }
```

### 多视角上下文
```python
def build_multi_pov_context(chapter, focus_characters):
    pov_contexts = []

    for character in focus_characters:
        # 获取角色视角的上下文
        character_pov = build_character_pov_context(character, chapter)
        pov_contexts.append(character_pov)

    # 合并多视角上下文
    merged_context = merge_pov_contexts(pov_contexts)

    return merged_context
```

## 上下文监控和调试

### 上下文使用统计
```python
class ContextMonitor:
    def __init__(self):
        self.usage_stats = {
            "total_context_builds": 0,
            "average_token_usage": 0,
            "compression_frequency": 0,
            "cache_hit_rate": 0.0
        }

    def record_context_build(self, token_usage, components_used):
        self.usage_stats["total_context_builds"] += 1

        # 更新平均token使用
        total = self.usage_stats["total_context_builds"]
        current_avg = self.usage_stats["average_token_usage"]
        self.usage_stats["average_token_usage"] = (
            (current_avg * (total - 1) + token_usage) / total
        )

        # 记录组件使用情况
        self.track_component_usage(components_used)
```

### 上下文调试工具
```python
def debug_context_build(chapter, mode="writing"):
    debug_info = {
        "chapter": chapter,
        "mode": mode,
        "build_time": datetime.now().isoformat(),
        "components": [],
        "token_breakdown": {},
        "optimization_steps": []
    }

    # 记录每个组件的详细信息
    for component in build_context_components(chapter, mode):
        debug_info["components"].append({
            "type": component["type"],
            "tokens": component["tokens"],
            "importance": component["importance"],
            "compression_applied": component.get("compressed", False)
        })

    return debug_info
```

## 性能优化建议

### 上下文构建优化
1. **预计算策略**
   - 提前构建常用上下文组合
   - 缓存压缩数据
   - 预测性加载相关内容

2. **并行处理**
   - 并行加载不同类型的上下文组件
   - 异步压缩处理
   - 并发缓存操作

3. **增量更新**
   - 只更新变更的上下文部分
   - 增量式压缩更新
   - 智能缓存失效

### 内存管理优化
1. **流式处理**
   - 大文件分块处理
   - 逐步加载上下文组件
   - 及时释放不必要的数据

2. **压缩优化**
   - 使用更高效的压缩算法
   - 压缩结果缓存
   - 压缩质量平衡