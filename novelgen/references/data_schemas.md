# 数据结构定义

## 项目结构数据模型

### 项目配置 (project_config.json)
```json
{
  "project_name": "string",
  "project_id": "string",
  "created_at": "string (ISO 8601)",
  "last_modified": "string (ISO 8601)",
  "current_mode": "setting|writing",
  "settings": {
    "worldview_complete": "boolean",
    "characters_complete": "boolean",
    "environments_complete": "boolean",
    "plot_complete": "boolean",
    "style_complete": "boolean",
    "memory_enabled": "boolean"
  },
  "writing_progress": {
    "total_chapters": "number",
    "completed_chapters": "number",
    "current_chapter": "number",
    "word_count": "number"
  }
}
```

### 会话状态 (session_state.json)
```json
{
  "session_id": "string",
  "created_at": "string (ISO 8601)",
  "last_updated": "string (ISO 8601)",
  "mode": "setting|writing",
  "current_chapter": "number",
  "project_path": "string",
  "context_state": {
    "token_limit": "number",
    "compression_enabled": "boolean",
    "last_compression_chapter": "number"
  },
  "working_state": {
    "unsaved_changes": "boolean",
    "current_section": "string",
    "generation_cache": "object"
  },
  "navigation_history": [
    {
      "timestamp": "string (ISO 8601)",
      "action": "string",
      "from_chapter": "number",
      "to_chapter": "number",
      "details": "object"
    }
  ],
  "error_log": ["string"]
}
```

### 章节数据结构
```json
{
  "chapter": "number",
  "title": "string",
  "word_count": "number",
  "status": "created|in_progress|completed",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)",
  "compression_data": {
    "recent": {
      "plot_summary": "string",
      "character_actions": "array",
      "key_dialogues": "array",
      "scene_changes": "array",
      "emotional_beats": "array",
      "timeline_markers": "array"
    },
    "medium": {
      "plot_summary": "string",
      "major_events": "array",
      "character_developments": "array",
      "plot_advancements": "array",
      "key_relationships": "array"
    },
    "long_term": {
      "major_arc": "string",
      "story_impact": "string",
      "character_destinations": "array",
      "thematic_elements": "array",
      "legacy_notes": "string"
    }
  }
}
```

## 设定数据模型

### 世界观设定
```json
{
  "world_name": "string",
  "era": "string",
  "technology_level": "string",
  "world_type": "string",
  "geography": "string",
  "society": "string",
  "magic_system": "string",
  "history": "string",
  "culture": "string",
  "economy": "string",
  "religion": "string",
  "physical_laws": "string",
  "magic_rules": "string",
  "social_rules": "string",
  "limitations": "string",
  "consistency_rules": "string",
  "time_flow": "string",
  "space_structure": "string"
}
```

### 角色设定
```json
{
  "character_id": "string",
  "name": "string",
  "character_type": "main|supporting",
  "age": "string|number",
  "gender": "string",
  "occupation": "string",
  "appearance": "string",
  "personality": "string",
  "background": "string",
  "abilities": "string",
  "goals": "string",
  "flaws": "string",
  "relationships": "string",
  "character_arc": "string",
  "catchphrases": "array",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### 环境设定
```json
{
  "world_type": "string",
  "main_locations": [
    {
      "name": "string",
      "type": "string",
      "description": "string",
      "features": "string",
      "atmosphere": "string",
      "related_characters": "array",
      "important_events": "array"
    }
  ],
  "overall_atmosphere": "string",
  "weather_system": "string",
  "time_atmosphere": "string",
  "seasonal_changes": "string",
  "emotional_atmosphere": "string",
  "special_effects": "string"
}
```

### 情节设定
```json
{
  "story_type": "string",
  "main_theme": "string",
  "plot_outline": "string",
  "main_conflict": "string",
  "plot_development": "string",
  "climax_setup": "string",
  "ending_arrangement": "string",
  "structure_type": "string",
  "act1_end": "number",
  "act1_events": "string",
  "act2_end": "number",
  "act2_events": "string",
  "act3_events": "string",
  "sub_plots": [
    {
      "name": "string",
      "main_characters": "array",
      "description": "string",
      "main_plot_connection": "string",
      "ending": "string"
    }
  ],
  "time_setting": "string",
  "time_flow": "string"
}
```

### 写作风格设定
```json
{
  "narrative_voice": "string",
  "tone": "string",
  "pacing": "string",
  "description_style": "string",
  "emotional_expression": "string",
  "time_space_transition": "string",
  "inner_monologue": "string",
  "dialogue_characteristics": "string",
  "language_style": "string",
  "dialect_features": "string",
  "emotional_color": "string",
  "dialogue_pacing": "string",
  "repetition_patterns": "string",
  "dialogue_tags": "string",
  "descriptive_words": "string",
  "emotional_words": "string",
  "action_words": "string",
  "environmental_words": "string",
  "avoid_words": "array",
  "special_usage": "string",
  "sentence_structure": "string",
  "paragraph_organization": "string",
  "rhetorical_devices": "string",
  "tense_usage": "string",
  "voice_choice": "string",
  "conjunction_usage": "string",
  "punctuation_usage": "string"
}
```

### 记忆设定
```json
{
  "memory_types": "string",
  "retention_rules": "string",
  "trigger_mechanisms": "string",
  "association_network": "string",
  "forgetting_mechanism": "string",
  "reconstruction_process": "string",
  "character_memory_sharing": "string",
  "memory_conflict_handling": "string",
  "memory_spread": "string",
  "collective_memory": "string",
  "memory_influence": "string",
  "compression_method": "string",
  "compression_triggers": "string",
  "compression_priority": "string",
  "recovery_mechanism": "string"
}
```

### 角色记忆数据
```json
{
  "memory_id": "string",
  "character_name": "string",
  "memory_type": "string",
  "occurrence_time": "string",
  "emotional_weight": "number (1-10)",
  "content": "string",
  "emotional_context": "string",
  "related_characters": "array",
  "trigger_keywords": "array",
  "timestamp": "string (ISO 8601)",
  "compression_level": "none|light|medium|heavy",
  "associated_memories": ["string"] // 关联记忆ID列表
}
```

## 上下文管理数据

### 上下文配置 (context_config.json)
```json
{
  "token_limit": "number",
  "compression_strategy": {
    "recent_chapters": "number",
    "medium_chapters": "number",
    "token_allocation": {
      "current_chapter": "number",
      "recent_compression": "number",
      "medium_compression": "number",
      "long_term_compression": "number",
      "settings_data": "number",
      "buffer_space": "number"
    }
  },
  "memory_handling": "separate_agent|integrated",
  "context_refresh_interval": "number",
  "compression_threshold": "number"
}
```

### 上下文组件
```json
{
  "type": "current_chapter|setting|recent_compression|medium_compression|long_term_compression",
  "content": "string",
  "tokens": "number",
  "chapter": "number",
  "setting_type": "string",
  "compression_type": "string"
}
```

## 压缩数据模型

### 压缩元数据
```json
{
  "chapter": "number",
  "compression_type": "recent|medium|long_term",
  "compressed_at": "string (ISO 8601)",
  "original_tokens": "number",
  "compressed_tokens": "number",
  "compression_ratio": "number",
  "components": ["string"]
}
```

### 批量压缩记录
```json
{
  "batch_id": "string",
  "timestamp": "string (ISO 8601)",
  "chapter_range": [number, number],
  "compression_types": ["string"],
  "results": {
    "successful": "number",
    "failed": "number",
    "total": "number",
    "details": "object"
  }
}
```

## 系统数据模型

### 章节索引 (chapter_index.json)
```json
{
  "chapters": [
    {
      "chapter": "number",
      "title": "string",
      "created_at": "string (ISO 8601)",
      "last_action": "string",
      "last_updated": "string (ISO 8601)",
      "word_count": "number",
      "status": "string"
    }
  ],
  "last_updated": "string (ISO 8601)"
}
```

### 错误日志 (error_log.json)
```json
{
  "errors": [
    {
      "timestamp": "string (ISO 8601)",
      "component": "string",
      "message": "string",
      "severity": "error|warning|info",
      "context": "object"
    }
  ]
}
```

### 压缩日志 (compression_log.json)
```json
{
  "compression_operations": [
    {
      "timestamp": "string (ISO 8601)",
      "chapter": "number",
      "operation_type": "compress|recompress|batch",
      "results": "object",
      "duration": "number",
      "success": "boolean"
    }
  ]
}
```

### 导航日志 (navigation_log.json)
```json
{
  "jumps": [
    {
      "timestamp": "string (ISO 8601)",
      "from_chapter": "number",
      "to_chapter": "number",
      "force": "boolean",
      "reason": "string"
    }
  ]
}
```

## 进度追踪数据

### 章节状态 (chapter_status.json)
```json
{
  "chapters": {
    "chapter_1": {
      "status": "created|in_progress|completed",
      "last_action": "string",
      "last_updated": "string (ISO 8601)",
      "word_count": "number",
      "compression_status": "object"
    }
  }
}
```

### 项目进度 (writing_progress.md)
```markdown
# 项目进度

## 总体统计
- 总章节数: X
- 已完成章节: Y
- 当前章节: Z
- 总字数: N

## 近期目标
- [ ] 完成第X章
- [ ] 进行压缩检查
- [ ] 更新角色发展

## 遇到的问题
- [ ] 情节连贯性问题
- [ ] 角色一致性检查
```

## 验证规则

### 数据完整性验证
```json
{
  "required_fields": {
    "project_config": ["project_name", "project_id", "created_at"],
    "session_state": ["session_id", "mode", "current_chapter"],
    "chapter": ["chapter", "title", "word_count", "status"],
    "character": ["name", "personality", "background"],
    "worldview": ["world_name", "era", "technology_level"]
  },
  "field_constraints": {
    "chapter": {
      "chapter": {"min": 1, "type": "integer"},
      "word_count": {"min": 0, "type": "integer"},
      "emotional_weight": {"min": 1, "max": 10, "type": "integer"}
    },
    "project": {
      "current_chapter": {"min": 1, "type": "integer"},
      "token_limit": {"min": 32000, "type": "integer"}
    }
  },
  "relationship_constraints": {
    "chapter_navigation": "target_chapter must exist",
    "character_relationships": "both characters must exist",
    "memory_association": "memory_id must be valid"
  }
}
```

### 格式规范
- 所有时间戳使用 ISO 8601 格式
- 文件名使用小写字母和下划线
- 章节编号使用两位数字格式 (01, 02, ...)
- 压缩文件按类型分层存储
- 备份文件包含时间戳信息