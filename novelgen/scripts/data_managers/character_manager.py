#!/usr/bin/env python3
"""
角色管理器
处理角色的创建、编辑、关系管理和状态追踪
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class CharacterManager:
    """角色管理器，负责角色创建、关系管理和状态追踪"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.characters_dir = self.project_path / "settings" / "characters"

        # 确保目录存在
        self.characters_dir.mkdir(parents=True, exist_ok=True)
        (self.characters_dir / "main_characters").mkdir(exist_ok=True)
        (self.characters_dir / "supporting_characters").mkdir(exist_ok=True)

        # 文件路径
        self.relations_file = self.characters_dir / "character_relations.md"

    def create_character(self, character_data: Dict[str, Any],
                        character_type: str = "main") -> Dict[str, Any]:
        """创建角色"""
        try:
            # 验证必需字段
            required_fields = ["name", "personality", "background"]
            for field in required_fields:
                if field not in character_data:
                    return {
                        "status": "error",
                        "message": f"缺少必需字段: {field}"
                    }

            # 生成角色文件
            character_id = self._generate_character_id(character_data["name"])
            character_file = (self.characters_dir / f"{character_type}_characters" /
                             f"{character_id}.md")

            # 检查角色是否已存在
            if character_file.exists():
                return {
                    "status": "error",
                    "message": f"角色 {character_data['name']} 已存在"
                }

            # 格式化角色内容
            character_content = self._format_character_content(character_data, character_type)

            # 保存角色文件
            character_file.write_text(character_content, encoding='utf-8')

            # 更新关系文件
            self._update_relations_file()

            return {
                "status": "success",
                "message": f"角色 {character_data['name']} 创建成功",
                "character_id": character_id,
                "character_type": character_type,
                "file_path": str(character_file)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"创建角色失败: {e}"
            }

    def load_character(self, character_name: str) -> Dict[str, Any]:
        """加载角色"""
        try:
            character_file = self._find_character_file(character_name)
            if not character_file:
                return {
                    "status": "error",
                    "message": f"角色 {character_name} 不存在"
                }

            content = character_file.read_text(encoding='utf-8')

            return {
                "status": "success",
                "character_name": character_name,
                "content": content,
                "file_path": str(character_file),
                "character_type": "main" if "main_characters" in str(character_file) else "supporting"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"加载角色失败: {e}"
            }

    def update_character(self, character_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新角色"""
        try:
            character_file = self._find_character_file(character_name)
            if not character_file:
                return {
                    "status": "error",
                    "message": f"角色 {character_name} 不存在"
                }

            # 加载现有内容
            content = character_file.read_text(encoding='utf-8')

            # 解析并更新角色数据
            updated_content = self._update_character_content(content, updates)

            # 保存更新后的内容
            character_file.write_text(updated_content, encoding='utf-8')

            # 更新关系文件
            self._update_relations_file()

            return {
                "status": "success",
                "message": f"角色 {character_name} 更新成功",
                "updated_fields": list(updates.keys())
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"更新角色失败: {e}"
            }

    def list_characters(self, character_type: str = None) -> Dict[str, Any]:
        """列出角色"""
        try:
            characters = []

            # 搜索主角色
            if not character_type or character_type == "main":
                main_dir = self.characters_dir / "main_characters"
                if main_dir.exists():
                    for file in main_dir.glob("*.md"):
                        char_info = self._extract_character_info(file)
                        char_info["type"] = "main"
                        characters.append(char_info)

            # 搜索配角
            if not character_type or character_type == "supporting":
                supporting_dir = self.characters_dir / "supporting_characters"
                if supporting_dir.exists():
                    for file in supporting_dir.glob("*.md"):
                        char_info = self._extract_character_info(file)
                        char_info["type"] = "supporting"
                        characters.append(char_info)

            # 按创建时间排序
            characters.sort(key=lambda x: x.get("created_at", ""))

            return {
                "status": "success",
                "characters": characters,
                "total": len(characters)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"列出角色失败: {e}"
            }

    def add_relationship(self, character1: str, character2: str,
                         relationship_type: str, description: str = "") -> Dict[str, Any]:
        """添加角色关系"""
        try:
            # 验证角色存在
            if not self._find_character_file(character1):
                return {
                    "status": "error",
                    "message": f"角色 {character1} 不存在"
                }

            if not self._find_character_file(character2):
                return {
                    "status": "error",
                    "message": f"角色 {character2} 不存在"
                }

            # 读取现有关系文件
            if self.relations_file.exists():
                relations_content = self.relations_file.read_text(encoding='utf-8')
            else:
                relations_content = "# 角色关系\n\n"

            # 添加新关系
            new_relation = f"""## {character1} - {character2}

**关系类型**: {relationship_type}
**描述**: {description}
**建立时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""

            relations_content += new_relation

            # 保存关系文件
            self.relations_file.write_text(relations_content, encoding='utf-8')

            return {
                "status": "success",
                "message": f"成功添加 {character1} 和 {character2} 的关系",
                "relationship": f"{character1} - {character2} ({relationship_type})"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"添加关系失败: {e}"
            }

    def get_character_relationships(self, character_name: str) -> Dict[str, Any]:
        """获取角色关系"""
        try:
            if not self.relations_file.exists():
                return {"status": "success", "relationships": []}

            content = self.relations_file.read_text(encoding='utf-8')
            relationships = []

            # 解析关系文件
            sections = content.split("## ")
            for section in sections[1:]:  # 跳过第一个空section
                if character_name in section:
                    lines = section.strip().split('\n')
                    if lines:
                        title = lines[0]
                        relationship_type = ""
                        description = ""

                        for line in lines[1:]:
                            if line.startswith("**关系类型**"):
                                relationship_type = line.split(":")[1].strip()
                            elif line.startswith("**描述**"):
                                description = line.split(":")[1].strip()

                        relationships.append({
                            "title": title,
                            "type": relationship_type,
                            "description": description
                        })

            return {
                "status": "success",
                "character": character_name,
                "relationships": relationships
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取角色关系失败: {e}"
            }

    def delete_character(self, character_name: str, confirm: bool = False) -> Dict[str, Any]:
        """删除角色"""
        if not confirm:
            return {
                "status": "confirmation_required",
                "message": f"确认要删除角色 {character_name} 吗？此操作不可撤销。"
            }

        try:
            character_file = self._find_character_file(character_name)
            if not character_file:
                return {
                    "status": "error",
                    "message": f"角色 {character_name} 不存在"
                }

            # 删除角色文件
            character_file.unlink()

            # 更新关系文件
            self._update_relations_file()

            return {
                "status": "success",
                "message": f"角色 {character_name} 已删除"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"删除角色失败: {e}"
            }

    def _generate_character_id(self, name: str) -> str:
        """生成角色ID"""
        import re
        # 简化处理：使用名字的拼音或英文名
        id_part = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', name)[:10]
        timestamp = int(datetime.now().timestamp())
        return f"{id_part}_{timestamp}"

    def _find_character_file(self, character_name: str) -> Optional[Path]:
        """查找角色文件"""
        # 在主角色目录中查找
        main_dir = self.characters_dir / "main_characters"
        if main_dir.exists():
            for file in main_dir.glob("*.md"):
                content = file.read_text(encoding='utf-8')
                if f"# {character_name}" in content or f"## 角色名称\n{character_name}" in content:
                    return file

        # 在配角目录中查找
        supporting_dir = self.characters_dir / "supporting_characters"
        if supporting_dir.exists():
            for file in supporting_dir.glob("*.md"):
                content = file.read_text(encoding='utf-8')
                if f"# {character_name}" in content or f"## 角色名称\n{character_name}" in content:
                    return file

        return None

    def _format_character_content(self, data: Dict[str, Any], character_type: str) -> str:
        """格式化角色内容"""
        return f"""# {data['name']}

## 基本信息
- **角色类型**: {'主角' if character_type == 'main' else '配角'}
- **年龄**: {data.get('age', '未知')}
- **性别**: {data.get('gender', '未知')}
- **职业**: {data.get('occupation', '未知')}

## 外貌特征
{data.get('appearance', '待补充...')}

## 性格特点
{data['personality']}

## 背景故事
{data['background']}

## 能力特长
{data.get('abilities', '待补充...')}

## 目标动机
{data.get('goals', '待补充...')}

## 性格缺陷
{data.get('flaws', '待补充...')}

## 重要关系
{data.get('relationships', '待补充...')}

## 角色发展弧线
{data.get('character_arc', '待补充...')}

## 经典台词
{data.get('catchphrases', '待补充...')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _update_character_content(self, content: str, updates: Dict[str, Any]) -> str:
        """更新角色内容"""
        # 简化处理：直接在现有内容后添加更新信息
        update_section = "\n\n## 更新记录\n\n"
        for key, value in updates.items():
            update_section += f"**{key}**: {value}\n"

        update_section += f"\n*更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return content + update_section

    def _extract_character_info(self, file: Path) -> Dict[str, Any]:
        """提取角色基本信息"""
        try:
            content = file.read_text(encoding='utf-8')
            lines = content.split('\n')

            name = "未知角色"
            created_at = ""

            for line in lines:
                if line.startswith("# "):
                    name = line[2:].strip()
                elif "创建时间:" in line:
                    created_at = line.split("创建时间:")[1].strip()

            return {
                "name": name,
                "file_path": str(file),
                "created_at": created_at,
                "file_size": file.stat().st_size
            }

        except Exception:
            return {
                "name": "解析失败",
                "file_path": str(file),
                "created_at": "",
                "file_size": 0
            }

    def apply_extracted_data(self, extracted_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """应用AI提取的角色数据"""
        try:
            if not isinstance(extracted_data, list):
                extracted_data = [extracted_data]

            applied_count = 0
            errors = []

            for character_data in extracted_data:
                try:
                    # 检查角色是否已存在
                    character_name = character_data.get("name")
                    if not character_name:
                        errors.append("跳过没有名称的角色数据")
                        continue

                    existing_character = self.load_character(character_name)

                    if existing_character["status"] == "success":
                        # 角色已存在，更新角色
                        update_result = self.intelligent_update_character(character_name, character_data)
                        if update_result["status"] == "success":
                            applied_count += 1
                        else:
                            errors.append(f"更新角色 {character_name} 失败: {update_result['message']}")
                    else:
                        # 角色不存在，创建新角色
                        character_type = character_data.get("type", "main")
                        create_result = self.create_character(character_data, character_type)
                        if create_result["status"] == "success":
                            applied_count += 1
                        else:
                            errors.append(f"创建角色 {character_name} 失败: {create_result['message']}")

                except Exception as e:
                    errors.append(f"处理角色数据时发生异常: {e}")

            return {
                "status": "success" if not errors else "partial_success",
                "message": f"成功处理 {applied_count} 个角色数据" + (f"，{len(errors)} 个错误" if errors else ""),
                "applied_count": applied_count,
                "total_processed": len(extracted_data),
                "errors": errors
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"应用提取数据失败: {e}"
            }

    def intelligent_update_character(self, character_name: str, new_data: Dict[str, Any],
                                   update_mode: str = "auto") -> Dict[str, Any]:
        """智能更新角色信息"""
        try:
            # 读取现有角色文件
            character_file = self._find_character_file(character_name)
            if not character_file:
                return {
                    "status": "error",
                    "message": f"角色 {character_name} 不存在"
                }

            existing_content = character_file.read_text(encoding='utf-8')

            # 如果没有AI能力，使用简单的追加更新
            if not hasattr(self, '_ai_client') or not self._ai_client:
                return self._simple_update_character(character_name, new_data)

            # 解析现有内容
            parsed_existing = self._parse_character_content(existing_content)

            # 分析差异并选择更新策略
            if update_mode == "auto":
                update_mode = self._determine_update_strategy(parsed_existing, new_data)

            # 执行智能合并
            merged_content = self._intelligent_merge_character_content(
                parsed_existing, new_data, update_mode
            )

            # 重新格式化内容
            formatted_content = self._format_character_content_intelligently(merged_content)

            # 保存更新后的内容
            character_file.write_text(formatted_content, encoding='utf-8')

            # 更新关系文件
            self._update_relations_file()

            return {
                "status": "success",
                "message": f"角色 {character_name} 更新成功",
                "update_mode": update_mode,
                "updated_fields": list(new_data.keys())
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"智能更新角色失败: {e}"
            }

    def _simple_update_character(self, character_name: str, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """简单更新角色信息（不使用AI）"""
        return self.update_character(character_name, new_data)

    def _parse_character_content(self, content: str) -> Dict[str, Any]:
        """解析角色内容为结构化数据"""
        parsed = {
            "name": "",
            "basic_info": {},
            "personality": "",
            "background": "",
            "appearance": "",
            "abilities": "",
            "goals": "",
            "flaws": "",
            "relationships": "",
            "character_arc": "",
            "catchphrases": ""
        }

        lines = content.split('\n')
        current_section = ""
        section_content = []

        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                parsed["name"] = line[2:].strip()
            elif line.startswith("## "):
                if current_section and section_content:
                    parsed[current_section] = "\n".join(section_content).strip()
                current_section = line[3:].strip().lower().replace(" ", "_")
                section_content = []
            elif line.startswith("- **") and current_section == "basic_info":
                # 解析基本信息
                if "：" in line:
                    key, value = line.split("：", 1)
                    key = key.replace("- **", "").replace("**", "").strip()
                    value = value.strip()
                    parsed["basic_info"][key] = value
            elif line and not line.startswith("-") and not line.startswith("*"):
                section_content.append(line)

        # 处理最后一个section
        if current_section and section_content:
            parsed[current_section] = "\n".join(section_content).strip()

        return parsed

    def _determine_update_strategy(self, existing: Dict[str, Any], new_data: Dict[str, Any]) -> str:
        """确定更新策略"""
        # 简单的策略：如果新数据内容较多，使用覆盖；如果较少，使用追加
        existing_content_length = sum(len(str(v)) for v in existing.values())
        new_content_length = sum(len(str(v)) for v in new_data.values())

        if new_content_length > existing_content_length * 0.5:
            return "覆盖"
        else:
            return "追加"

    def _intelligent_merge_character_content(self, existing: Dict[str, Any], new_data: Dict[str, Any],
                                          update_mode: str) -> Dict[str, Any]:
        """智能合并角色内容"""
        merged = existing.copy()

        if update_mode == "覆盖":
            # 覆盖模式：新数据覆盖对应字段
            for key, value in new_data.items():
                if key in merged:
                    merged[key] = str(value)
                else:
                    # 如果是新的字段，添加到相应section
                    if key in ["personality", "background", "appearance", "abilities", "goals", "flaws"]:
                        merged[key] = str(value)
        else:
            # 追加模式：在现有内容基础上追加
            for key, value in new_data.items():
                if key in merged and merged[key]:
                    merged[key] = merged[key] + "\n\n" + str(value)
                elif key in merged:
                    merged[key] = str(value)

        return merged

    def _format_character_content_intelligently(self, character_data: Dict[str, Any]) -> str:
        """智能格式化角色内容"""
        name = character_data.get("name", "未命名角色")
        basic_info = character_data.get("basic_info", {})

        content_lines = [f"# {name}", "", "## 基本信息"]

        # 添加基本信息
        info_fields = ["角色类型", "年龄", "性别", "职业"]
        for field in info_fields:
            value = basic_info.get(field, character_data.get(field.lower().replace("角色", ""), "未知"))
            content_lines.append(f"- **{field}**: {value}")

        # 添加其他sections
        sections = [
            ("外貌特征", "appearance"),
            ("性格特点", "personality"),
            ("背景故事", "background"),
            ("能力特长", "abilities"),
            ("目标动机", "goals"),
            ("性格缺陷", "flaws"),
            ("重要关系", "relationships"),
            ("角色发展弧线", "character_arc"),
            ("经典台词", "catchphrases")
        ]

        for section_name, section_key in sections:
            content = character_data.get(section_key, "")
            if content and content.strip():
                content_lines.extend(["", f"## {section_name}", content.strip()])

        content_lines.extend([
            "",
            f"---",
            f"*更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])

        return "\n".join(content_lines)

    def _update_relations_file(self):
        """更新关系文件"""
        try:
            # 重新生成所有角色的关系摘要
            characters_result = self.list_characters()
            if characters_result["status"] != "success":
                return

            characters = characters_result["characters"]

            # 读取现有关系内容
            existing_relations = ""
            if self.relations_file.exists():
                existing_content = self.relations_file.read_text(encoding='utf-8')
                # 保留现有的详细关系描述
                if "## " in existing_content:
                    existing_relations = "\n" + "\n".join(existing_content.split("\n## ")[1:])

            # 生成新的关系文件头部
            new_content = f"""# 角色关系

## 角色列表

### 主角
"""
            for char in characters:
                if char["type"] == "main":
                    new_content += f"- {char['name']}\n"

            new_content += "\n### 配角\n"
            for char in characters:
                if char["type"] == "supporting":
                    new_content += f"- {char['name']}\n"

            new_content += f"\n*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"

            # 添加现有关系
            new_content += existing_relations

            # 保存更新后的关系文件
            self.relations_file.write_text(new_content, encoding='utf-8')

        except Exception:
            pass  # 更新失败不影响主流程

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="角色管理器")
    parser.add_argument("--action", choices=["create", "load", "update", "list", "relations", "delete"],
                       required=True, help="操作类型")
    parser.add_argument("--name", help="角色名称")
    parser.add_argument("--type", choices=["main", "supporting"], default="main", help="角色类型")
    parser.add_argument("--project-path", default=".", help="项目路径")
    parser.add_argument("--confirm", action="store_true", help="确认删除")

    args = parser.parse_args()

    cm = CharacterManager(args.project_path)

    if args.action == "create":
        if not args.name:
            print("错误: create操作需要指定--name参数")
            return
        sample_data = {
            "name": args.name,
            "personality": "勇敢善良，有正义感",
            "background": "出身普通家庭，因为意外获得了特殊能力"
        }
        result = cm.create_character(sample_data, args.type)

    elif args.action == "load":
        if not args.name:
            print("错误: load操作需要指定--name参数")
            return
        result = cm.load_character(args.name)

    elif args.action == "list":
        result = cm.list_characters(args.type)

    elif args.action == "relations":
        if not args.name:
            print("错误: relations操作需要指定--name参数")
            return
        result = cm.get_character_relationships(args.name)

    elif args.action == "update":
        if not args.name:
            print("错误: update操作需要指定--name参数")
            return
        sample_data = {
            "personality": "更新后的性格",
            "background": "更新后的背景"
        }
        result = cm.update_character(args.name, sample_data)

    elif args.action == "delete":
        if not args.name:
            print("错误: delete操作需要指定--name参数")
            return
        result = cm.delete_character(args.name, args.confirm)

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()