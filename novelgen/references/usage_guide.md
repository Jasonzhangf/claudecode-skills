# 小说生成器使用指南

## 修改和更新设定功能

现在小说生成器已经具备完整的设定修改和更新功能，支持通过指令进行所有设定类型的动态修改。

## 统一修改接口

### 使用设置管理器 (settings_manager.py)

设置管理器提供统一的修改接口，可以管理所有类型的设定：

```bash
# 基本语法
python scripts/settings_manager.py --category <类别> --action <操作> --target <目标> --data '<JSON数据>'

# 示例：更新角色信息
python scripts/settings_manager.py \
  --category character \
  --action update \
  --target "林辰" \
  --data '{"personality": "变得更加成熟稳重", "goals": "保护重要的人"}'

# 示例：添加角色关系
python scripts/settings_manager.py \
  --category character \
  --action add_relationship \
  --target "林辰" \
  --character2 "艾莉娅" \
  --relationship-type "师徒" \
  --description "林辰向艾莉娅学习星辰之力的控制"
```

## 各类设定的修改方法

### 1. 世界观设定修改

```bash
# 直接使用世界观管理器
python scripts/data_managers/worldbuilder.py --action update --project-path /path/to/project

# 或使用统一接口
python scripts/settings_manager.py \
  --category worldview \
  --action update \
  --data '{"magic_system": "元素魔法系统进行了完善，增加了暗元素和光元素"}'
```

### 2. 角色设定修改

#### 更新角色基本信息
```bash
python scripts/settings_manager.py \
  --category character \
  --action update \
  --target "林辰" \
  --data '{
    "age": "26岁",
    "personality": "经过历练变得更加成熟，但内心依然保持善良",
    "abilities": "掌握了基础的星辰之力控制，可以进行简单的元素操控"
  }'
```

#### 添加角色关系
```bash
python scripts/settings_manager.py \
  --category character \
  --action add_relationship \
  --target "林辰" \
  --character2 "小雅" \
  --relationship-type "青梅竹马" \
  --description "从小一起长大的朋友，关系深厚"
```

#### 添加角色记忆
```bash
python scripts/settings_manager.py \
  --category memory \
  --action add_memory \
  --target "林辰" \
  --data '{
    "memory_type": "情感记忆",
    "content": "第一次成功控制星辰之力的激动心情",
    "emotional_weight": 8,
    "related_characters": ["艾莉娅"],
    "trigger_keywords": ["星辰之力", "控制", "第一次"]
  }'
```

#### 删除角色
```bash
python scripts/settings_manager.py \
  --category character \
  --action delete \
  --target "不重要的配角" \
  --confirm
```

### 3. 环境设定修改

#### 添加新地点
```bash
python scripts/settings_manager.py \
  --category environment \
  --action add_location \
  --data '{
    "name": "星辰神殿",
    "type": "古代遗迹",
    "description": "隐藏在星际深处的古老神殿，是星灵族的圣地",
    "features": "漂浮的水晶、星辰壁画、神秘的能量场",
    "atmosphere": "神秘而庄严，充满了古老的能量"
  }'
```

#### 添加场景模板
```bash
python scripts/settings_manager.py \
  --category environment \
  --action add_scene \
  --target "星辰神殿" \
  --data '{
    "scene_name": "星辰觉醒仪式",
    "scene_type": "重要事件",
    "location": "星辰神殿",
    "description_template": "神殿中央的祭坛发出璀璨的光芒，星辰之力在周围环绕..."
  }'
```

### 4. 情节设定修改

#### 添加情节点
```bash
python scripts/settings_manager.py \
  --category plot \
  --action add_point \
  --data '{
    "title": "星辰觉醒",
    "description": "林辰在危急时刻觉醒了完整的星辰之力",
    "chapter_position": "第15章",
    "type": "关键转折",
    "related_characters": ["林辰", "艾莉娅"],
    "importance": "高"
  }' \
  --plot-type main
```

#### 添加时间线事件
```bash
python scripts/settings_manager.py \
  --category plot \
  --action add_event \
  --data '{
    "time": "故事中期",
    "event": "暗影组织首次现身",
    "related_chapter": 12,
    "characters": "林辰、卡洛斯",
    "significance": "标志着主要反派的正式登场"
  }'
```

#### 更新情节大纲
```bash
python scripts/settings_manager.py \
  --category plot \
  --action update_structure \
  --component structure \
  --data '{
    "structure_type": "四幕式结构",
    "act1_end": 12,
    "act2_end": 35,
    "act3_end": 50
  }'
```

#### 删除情节点
```bash
# 使用情节管理器直接删除
python scripts/data_managers/plot_manager.py \
  --action remove_point \
  --title "不需要的情节点" \
  --plot-type supporting
```

### 5. 写作风格设定修改

#### 更新风格组件
```bash
python scripts/settings_manager.py \
  --category style \
  --action update_component \
  --target narrative \
  --data '{
    "narrative_voice": "第三人称有限视角（主要林辰视角）",
    "pacing": "根据情节需要调整，动作场面快节奏，内心描写慢节奏"
  }'
```

#### 添加词汇类别
```bash
python scripts/settings_manager.py \
  --category style \
  --action add_vocabulary \
  --component vocabulary \
  --category "星辰相关词汇" \
  --words "星辰之力、星灵族、暗影组织、星际联盟"
```

### 6. 记忆设定修改

#### 压缩角色记忆
```bash
python scripts/settings_manager.py \
  --category memory \
  --action compress \
  --target "林辰" \
  --compression-level medium
```

#### 更新记忆权重
```bash
python scripts/settings_manager.py \
  --category memory \
  --action update_weight \
  --target "林辰" \
  --memory-id "abc12345" \
  --new-weight 9
```

## 批量操作和高级功能

### 验证设定一致性
```bash
python scripts/settings_manager.py \
  --action validate_consistency \
  --project-path /path/to/project
```

### 备份所有设定
```bash
python scripts/settings_manager.py \
  --action backup \
  --backup-name "before_major_changes" \
  --project-path /path/to/project
```

### 恢复设定备份
```bash
python scripts/settings_manager.py \
  --action restore \
  --backup-name "before_major_changes" \
  --project-path /path/to/project
```

### 获取设定状态
```bash
# 获取所有设定状态
python scripts/settings_manager.py --action status

# 获取特定类别状态
python scripts/settings_manager.py --action status --category character

# 获取特定角色状态
python scripts/settings_manager.py --action status --category character --target "林辰"
```

## 数据格式说明

### JSON数据格式
所有修改操作的数据都使用JSON格式，支持字符串、数字、数组和对象：

```json
{
  "字符串字段": "值",
  "数字字段": 123,
  "数组字段": ["元素1", "元素2"],
  "对象字段": {
    "子字段1": "值1",
    "子字段2": "值2"
  }
}
```

### 支持的操作类型
- `update`: 更新现有设定
- `add`: 添加新元素
- `delete`: 删除元素（需要确认）
- `add_relationship`: 添加关系（角色专用）
- `add_memory`: 添加记忆（记忆专用）
- `compress`: 压缩数据（记忆专用）

### 支持的设定类别
- `worldview`: 世界观设定
- `character`: 角色设定
- `environment`: 环境设定
- `plot`: 情节设定
- `style`: 写作风格设定
- `memory`: 记忆设定

## 最佳实践

### 1. 修改前备份
在进行重大修改前，建议先备份当前设定：
```bash
python scripts/settings_manager.py --action backup --backup-name "pre_chapter_20_changes"
```

### 2. 验证一致性
修改完成后，验证设定的一致性：
```bash
python scripts/settings_manager.py --action validate_consistency
```

### 3. 逐步修改
对于复杂的修改，建议分步进行，每步都验证结果。

### 4. 记录修改
所有修改操作都会自动记录在 `system/settings_operations.log` 中，便于追踪修改历史。

### 5. 使用模板
对于重复性的修改操作，可以创建JSON模板文件，然后使用 `--data @template.json` 的方式加载数据。

## 错误处理

### 常见错误及解决方案

1. **JSON格式错误**
   - 确保JSON字符串格式正确，使用单引号包围整个JSON字符串
   - 检查括号、引号、逗号是否匹配

2. **文件不存在错误**
   - 确保项目路径正确
   - 确保相关的设定文件已经创建

3. **权限错误**
   - 确保对项目目录有写权限
   - 检查文件是否被其他程序占用

4. **目标不存在错误**
   - 确保目标角色、地点等已经存在
   - 使用 `--action status` 检查当前设定状态

---

*使用这些功能，你可以灵活地修改和管理小说的所有设定，确保创作过程中的设定保持一致性和完整性。*