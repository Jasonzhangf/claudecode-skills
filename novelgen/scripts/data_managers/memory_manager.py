#!/usr/bin/env python3
"""
记忆管理器
处理角色记忆、记忆压缩和记忆关联
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class MemoryManager:
    """记忆管理器，负责角色记忆和记忆压缩"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.memory_dir = self.project_path / "settings" / "memory"

        # 确保目录存在
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # 文件路径
        self.memory_structure_file = self.memory_dir / "memory_structure.md"
        self.character_memory_file = self.memory_dir / "character_memory.md"
        self.memory_compression_file = self.memory_dir / "memory_compression_rules.md"

    def create_memory_system(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建记忆系统"""
        try:
            # 验证必需字段
            required_fields = ["memory_types", "retention_rules", "compression_method"]
            for field in required_fields:
                if field not in memory_data:
                    return {
                        "status": "error",
                        "message": f"缺少必需字段: {field}"
                    }

            # 创建记忆结构
            structure_content = self._format_memory_structure(memory_data)
            self.memory_structure_file.write_text(structure_content, encoding='utf-8')

            # 创建角色记忆关联
            character_memory_content = self._format_character_memory(memory_data)
            self.character_memory_file.write_text(character_memory_content, encoding='utf-8')

            # 创建记忆压缩规则
            compression_content = self._format_memory_compression(memory_data)
            self.memory_compression_file.write_text(compression_content, encoding='utf-8')

            return {
                "status": "success",
                "message": "记忆系统创建成功",
                "files_created": [
                    str(self.memory_structure_file),
                    str(self.character_memory_file),
                    str(self.memory_compression_file)
                ]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"创建记忆系统失败: {e}"
            }

    def add_character_memory(self, character_name: str, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """添加角色记忆"""
        try:
            # 验证必需字段
            required_fields = ["memory_type", "content", "emotional_weight"]
            for field in required_fields:
                if field not in memory_data:
                    return {
                        "status": "error",
                        "message": f"缺少必需字段: {field}"
                    }

            # 读取现有角色记忆
            if self.character_memory_file.exists():
                content = self.character_memory_file.read_text(encoding='utf-8')
            else:
                content = "# 角色记忆\n\n"

            # 添加新记忆
            new_memory = self._format_character_memory_entry(character_name, memory_data)
            content += new_memory

            # 保存更新后的内容
            self.character_memory_file.write_text(content, encoding='utf-8')

            return {
                "status": "success",
                "message": f"角色 {character_name} 的记忆添加成功"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"添加角色记忆失败: {e}"
            }

    def compress_memories(self, character_name: str = None, compression_level: str = "medium") -> Dict[str, Any]:
        """压缩记忆"""
        try:
            # 读取记忆数据
            memories = self._load_memories(character_name)

            if not memories:
                return {
                    "status": "error",
                    "message": "没有找到可压缩的记忆"
                }

            # 执行记忆压缩
            compressed_memories = self._execute_memory_compression(memories, compression_level)

            # 保存压缩结果
            compression_result = self._save_compressed_memories(
                compressed_memories, character_name, compression_level
            )

            return {
                "status": "success",
                "compression_level": compression_level,
                "original_count": len(memories),
                "compressed_count": len(compressed_memories),
                "compression_ratio": len(compressed_memories) / len(memories),
                "result": compression_result
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"记忆压缩失败: {e}"
            }

    def get_character_memories(self, character_name: str, memory_type: str = None,
                              include_compressed: bool = True) -> Dict[str, Any]:
        """获取角色记忆"""
        try:
            all_memories = []

            # 读取原始记忆
            original_memories = self._load_character_memories(character_name, memory_type)
            all_memories.extend(original_memories)

            # 读取压缩记忆
            if include_compressed:
                compressed_memories = self._load_compressed_memories(character_name, memory_type)
                all_memories.extend(compressed_memories)

            # 按时间排序
            all_memories.sort(key=lambda x: x.get("timestamp", ""))

            return {
                "status": "success",
                "character": character_name,
                "memories": all_memories,
                "total_count": len(all_memories),
                "memory_types": list(set(m.get("memory_type", "unknown") for m in all_memories))
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取角色记忆失败: {e}"
            }

    def find_memory_connections(self, character_name: str, keywords: List[str],
                               max_connections: int = 10) -> Dict[str, Any]:
        """查找记忆关联"""
        try:
            # 获取角色所有记忆
            memories_result = self.get_character_memories(character_name)
            if memories_result["status"] != "success":
                return memories_result

            memories = memories_result["memories"]

            # 查找包含关键词的记忆
            connected_memories = []
            for memory in memories:
                content = memory.get("content", "").lower()
                emotional_context = memory.get("emotional_context", "").lower()

                keyword_matches = 0
                for keyword in keywords:
                    if keyword.lower() in content or keyword.lower() in emotional_context:
                        keyword_matches += 1

                if keyword_matches > 0:
                    connected_memories.append({
                        **memory,
                        "keyword_matches": keyword_matches,
                        "relevance_score": keyword_matches / len(keywords)
                    })

            # 按相关性排序
            connected_memories.sort(key=lambda x: x["relevance_score"], reverse=True)

            return {
                "status": "success",
                "character": character_name,
                "keywords": keywords,
                "connected_memories": connected_memories[:max_connections],
                "total_found": len(connected_memories)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"查找记忆关联失败: {e}"
            }

    def update_memory_emotional_weight(self, character_name: str, memory_id: str,
                                    new_weight: int) -> Dict[str, Any]:
        """更新记忆情感权重"""
        try:
            # 验证权重范围
            if not 1 <= new_weight <= 10:
                return {
                    "status": "error",
                    "message": "情感权重必须在1-10之间"
                }

            # 读取记忆文件
            if not self.character_memory_file.exists():
                return {
                    "status": "error",
                    "message": "角色记忆文件不存在"
                }

            content = self.character_memory_file.read_text(encoding='utf-8')

            # 查找并更新指定记忆
            updated = False
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if f"**记忆ID**: {memory_id}" in line:
                    # 查找情感权重行
                    for j in range(i, min(i + 10, len(lines))):
                        if "**情感权重**" in lines[j]:
                            lines[j] = f"**情感权重**: {new_weight}"
                            updated = True
                            break
                    if updated:
                        break

            if not updated:
                return {
                    "status": "error",
                    "message": f"未找到记忆ID: {memory_id}"
                }

            # 保存更新后的内容
            self.character_memory_file.write_text('\n'.join(lines), encoding='utf-8')

            return {
                "status": "success",
                "message": f"记忆 {memory_id} 的情感权重已更新为 {new_weight}"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"更新记忆情感权重失败: {e}"
            }

    def _format_memory_structure(self, data: Dict[str, Any]) -> str:
        """格式化记忆结构"""
        return f"""# 记忆结构

## 记忆类型分类
{data.get('memory_types', '短期记忆、长期记忆、情感记忆、技能记忆')}

## 记忆保留规则
{data.get('retention_rules', '重要事件和情感强烈的记忆保留时间更长')}

## 记忆触发机制
{data.get('trigger_mechanisms', '相似情境、情感体验、感官刺激')}

## 记忆关联网络
{data.get('association_network', '通过主题、情感、人物等建立记忆关联')}

## 记忆遗忘机制
{data.get('forgetting_mechanism', '不常用的记忆逐渐模糊，重要记忆保持清晰')}

## 记忆重构过程
{data.get('reconstruction_process', '回忆时可能对记忆进行无意识的重构和修饰')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_character_memory(self, data: Dict[str, Any]) -> str:
        """格式化角色记忆"""
        return f"""# 角色记忆关联

## 角色间记忆共享
{data.get('character_memory_sharing', '共同经历的事件在相关角色间形成共享记忆')}

## 记忆冲突处理
{data.get('memory_conflict_handling', '不同角色对同一事件可能有不同的记忆和解读')}

## 记忆传播机制
{data.get('memory_spread', '通过对话和互动，记忆在角色间传播和影响')}

## 集体记忆
{data.get('collective_memory', '重要事件形成群体层面的集体记忆')}

## 记忆影响关系
{data.get('memory_influence', '过去的记忆影响角色的行为和决策')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_memory_compression(self, data: Dict[str, Any]) -> str:
        """格式化记忆压缩规则"""
        return f"""# 记忆压缩规则

## 压缩方法
{data.get('compression_method', '保留核心信息，简化细节，合并相似记忆')}

## 压缩触发条件
{data.get('compression_triggers', '记忆数量达到阈值、时间间隔、重要事件后')}

## 压缩层级
- **轻度压缩**: 保留主要情节和情感
- **中度压缩**: 保留关键信息和核心情感
- **深度压缩**: 仅保留最基本的事实和情感标签

## 压缩优先级
{data.get('compression_priority', '情感强烈的记忆最后压缩，日常记忆优先压缩')}

## 压缩恢复机制
{data.get('recovery_mechanism', '通过特定触发器可能恢复部分压缩的记忆细节')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_character_memory_entry(self, character_name: str, memory_data: Dict[str, Any]) -> str:
        """格式化角色记忆条目"""
        import uuid
        memory_id = str(uuid.uuid4())[:8]

        return f"""## {character_name} - {memory_data.get('event_summary', '记忆事件')}

**记忆ID**: {memory_id}
**记忆类型**: {memory_data['memory_type']}
**发生时间**: {memory_data.get('occurrence_time', '未知')}
**情感权重**: {memory_data['emotional_weight']}/10
**记忆内容**: {memory_data['content']}
**情感背景**: {memory_data.get('emotional_context', '无特殊情感背景')}
**相关角色**: {memory_data.get('related_characters', '无')}
**触发关键词**: {memory_data.get('trigger_keywords', '无')}
**记录时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""

    def _load_memories(self, character_name: str = None) -> List[Dict[str, Any]]:
        """加载记忆数据"""
        memories = []

        if self.character_memory_file.exists():
            content = self.character_memory_file.read_text(encoding='utf-8')
            sections = content.split("## ")

            for section in sections[1:]:  # 跳过第一个空section
                if character_name and not section.startswith(character_name):
                    continue

                memory_info = self._parse_memory_section(section)
                if memory_info:
                    memories.append(memory_info)

        return memories

    def _load_character_memories(self, character_name: str, memory_type: str = None) -> List[Dict[str, Any]]:
        """加载角色记忆"""
        all_memories = self._load_memories(character_name)

        if memory_type:
            return [m for m in all_memories if m.get("memory_type") == memory_type]

        return all_memories

    def _load_compressed_memories(self, character_name: str, memory_type: str = None) -> List[Dict[str, Any]]:
        """加载压缩记忆"""
        # 这里应该从压缩文件中读取，简化处理
        return []

    def _parse_memory_section(self, section: str) -> Optional[Dict[str, Any]]:
        """解析记忆段落"""
        lines = section.strip().split('\n')
        if not lines:
            return None

        memory = {"title": lines[0]}

        for line in lines[1:]:
            if line.startswith("**记忆ID**"):
                memory["memory_id"] = line.split(":")[1].strip()
            elif line.startswith("**记忆类型**"):
                memory["memory_type"] = line.split(":")[1].strip()
            elif line.startswith("**情感权重**"):
                memory["emotional_weight"] = int(line.split(":")[1].split("/")[0].strip())
            elif line.startswith("**记忆内容**"):
                memory["content"] = line.split(":")[1].strip()
            elif line.startswith("**记录时间**"):
                memory["timestamp"] = line.split(":")[1].strip()

        return memory

    def _execute_memory_compression(self, memories: List[Dict[str, Any]],
                                  compression_level: str) -> List[Dict[str, Any]]:
        """执行记忆压缩"""
        if compression_level == "light":
            # 轻度压缩：保留50%的记忆
            return sorted(memories, key=lambda x: x.get("emotional_weight", 5), reverse=True)[:len(memories)//2]
        elif compression_level == "medium":
            # 中度压缩：保留30%的记忆
            return sorted(memories, key=lambda x: x.get("emotional_weight", 5), reverse=True)[:len(memories)//3]
        elif compression_level == "heavy":
            # 重度压缩：保留15%的记忆
            return sorted(memories, key=lambda x: x.get("emotional_weight", 5), reverse=True)[:len(memories)//7]
        else:
            return memories

    def apply_extracted_data(self, extracted_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """应用AI提取的记忆数据"""
        try:
            if not isinstance(extracted_data, list):
                extracted_data = [extracted_data]

            applied_count = 0
            errors = []

            for memory_data in extracted_data:
                try:
                    # 检查必需字段
                    character_name = memory_data.get("character_name")
                    memory_content = memory_data.get("content")

                    if not character_name or not memory_content:
                        errors.append("跳过缺少角色名或记忆内容的数据")
                        continue

                    # 准备记忆数据
                    memory_entry = {
                        "memory_type": memory_data.get("memory_type", "长期记忆"),
                        "content": memory_content,
                        "emotional_weight": memory_data.get("emotional_weight", 5),
                        "occurrence_time": memory_data.get("occurrence_time", "未知时间"),
                        "emotional_context": memory_data.get("emotional_context", ""),
                        "related_characters": memory_data.get("related_characters", ""),
                        "trigger_keywords": memory_data.get("trigger_keywords", ""),
                        "event_summary": memory_data.get("event_summary", memory_content[:50] + "...")
                    }

                    # 添加记忆
                    add_result = self.add_character_memory(character_name, memory_entry)
                    if add_result["status"] == "success":
                        applied_count += 1
                    else:
                        errors.append(f"添加记忆失败: {add_result['message']}")

                except Exception as e:
                    errors.append(f"处理记忆数据时发生异常: {e}")

            return {
                "status": "success" if not errors else "partial_success",
                "message": f"成功处理 {applied_count} 个记忆数据" + (f"，{len(errors)} 个错误" if errors else ""),
                "applied_count": applied_count,
                "total_processed": len(extracted_data),
                "errors": errors
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"应用提取数据失败: {e}"
            }

    def _save_compressed_memories(self, compressed_memories: List[Dict[str, Any]],
                                character_name: str, compression_level: str) -> Dict[str, Any]:
        """保存压缩记忆"""
        try:
            compression_file = self.memory_dir / f"compressed_memories_{compression_level}.json"

            # 读取现有压缩数据
            if compression_file.exists():
                compressed_data = json.load(compression_file.read_text(encoding='utf-8'))
            else:
                compressed_data = {"characters": {}, "compression_history": []}

            # 更新压缩数据
            if character_name not in compressed_data["characters"]:
                compressed_data["characters"][character_name] = {}

            compressed_data["characters"][character_name][compression_level] = {
                "memories": compressed_memories,
                "compressed_at": datetime.now().isoformat(),
                "original_count": len(self._load_character_memories(character_name)),
                "compressed_count": len(compressed_memories)
            }

            # 添加压缩历史记录
            compressed_data["compression_history"].append({
                "character": character_name,
                "compression_level": compression_level,
                "timestamp": datetime.now().isoformat(),
                "original_count": len(self._load_character_memories(character_name)),
                "compressed_count": len(compressed_memories)
            })

            # 保存压缩数据
            with open(compression_file, 'w', encoding='utf-8') as f:
                json.dump(compressed_data, f, ensure_ascii=False, indent=2)

            return {
                "saved": True,
                "compression_file": str(compression_file),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "saved": False,
                "error": str(e)
            }

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="记忆管理器")
    parser.add_argument("--action", choices=["create", "add_memory", "compress", "get_memories", "connections"],
                       required=True, help="操作类型")
    parser.add_argument("--character", help="角色名称")
    parser.add_argument("--level", choices=["light", "medium", "heavy"], default="medium",
                       help="压缩级别")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    mm = MemoryManager(args.project_path)

    if args.action == "create":
        sample_data = {
            "memory_types": "短期记忆、长期记忆、情感记忆",
            "retention_rules": "重要事件保留更久",
            "compression_method": "分层压缩机制"
        }
        result = mm.create_memory_system(sample_data)

    elif args.action == "add_memory":
        if not args.character:
            print("错误: add_memory操作需要指定--character参数")
            return
        memory_data = {
            "memory_type": "情感记忆",
            "content": "重要的情感经历",
            "emotional_weight": 8
        }
        result = mm.add_character_memory(args.character, memory_data)

    elif args.action == "compress":
        result = mm.compress_memories(args.character, args.level)

    elif args.action == "get_memories":
        if not args.character:
            print("错误: get_memories操作需要指定--character参数")
            return
        result = mm.get_character_memories(args.character)

    elif args.action == "connections":
        if not args.character:
            print("错误: connections操作需要指定--character参数")
            return
        result = mm.find_memory_connections(args.character, ["重要", "情感"])

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()