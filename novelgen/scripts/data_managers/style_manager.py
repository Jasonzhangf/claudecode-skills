#!/usr/bin/env python3
"""
写作风格管理器
处理叙事风格、对话风格、语言特色等写作风格设定
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class StyleManager:
    """写作风格管理器，负责写作风格的创建和维护"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.style_dir = self.project_path / "settings" / "writing_style"

        # 确保目录存在
        self.style_dir.mkdir(parents=True, exist_ok=True)

        # 文件路径
        self.narrative_style_file = self.style_dir / "narrative_style.md"
        self.dialogue_style_file = self.style_dir / "dialogue_style.md"
        self.vocabulary_file = self.style_dir / "vocabulary.md"
        self.grammar_patterns_file = self.style_dir / "grammar_patterns.md"

    def create_writing_style(self, style_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建写作风格设定"""
        try:
            # 验证必需字段
            required_fields = ["narrative_voice", "tone", "pacing"]
            for field in required_fields:
                if field not in style_data:
                    return {
                        "status": "error",
                        "message": f"缺少必需字段: {field}"
                    }

            # 创建叙事风格
            narrative_content = self._format_narrative_style(style_data)
            self.narrative_style_file.write_text(narrative_content, encoding='utf-8')

            # 创建对话风格
            dialogue_content = self._format_dialogue_style(style_data)
            self.dialogue_style_file.write_text(dialogue_content, encoding='utf-8')

            # 创建词汇偏好
            vocabulary_content = self._format_vocabulary(style_data)
            self.vocabulary_file.write_text(vocabulary_content, encoding='utf-8')

            # 创建语法模式
            grammar_content = self._format_grammar_patterns(style_data)
            self.grammar_patterns_file.write_text(grammar_content, encoding='utf-8')

            return {
                "status": "success",
                "message": "写作风格设定创建成功",
                "files_created": [
                    str(self.narrative_style_file),
                    str(self.dialogue_style_file),
                    str(self.vocabulary_file),
                    str(self.grammar_patterns_file)
                ]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"创建写作风格失败: {e}"
            }

    def update_style_component(self, component: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新风格组件"""
        try:
            # 选择文件
            file_map = {
                "narrative": self.narrative_style_file,
                "dialogue": self.dialogue_style_file,
                "vocabulary": self.vocabulary_file,
                "grammar": self.grammar_patterns_file
            }

            if component not in file_map:
                return {
                    "status": "error",
                    "message": f"未知的风格组件: {component}"
                }

            file_path = file_map[component]

            # 读取现有内容
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8')
            else:
                content = f"# {component}风格\n\n"

            # 应用更新
            updated_content = self._apply_style_update(content, updates, component)

            # 保存更新后的内容
            file_path.write_text(updated_content, encoding='utf-8')

            return {
                "status": "success",
                "message": f"{component}风格更新成功",
                "updated_fields": list(updates.keys())
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"更新风格组件失败: {e}"
            }

    def get_writing_style_guide(self, style_type: str = None) -> Dict[str, Any]:
        """获取写作风格指南"""
        try:
            style_guide = {}

            # 读取叙事风格
            if self.narrative_style_file.exists():
                narrative_content = self.narrative_style_file.read_text(encoding='utf-8')
                style_guide["narrative"] = self._parse_narrative_style(narrative_content)

            # 读取对话风格
            if self.dialogue_style_file.exists():
                dialogue_content = self.dialogue_style_file.read_text(encoding='utf-8')
                style_guide["dialogue"] = self._parse_dialogue_style(dialogue_content)

            # 读取词汇偏好
            if self.vocabulary_file.exists():
                vocab_content = self.vocabulary_file.read_text(encoding='utf-8')
                style_guide["vocabulary"] = self._parse_vocabulary(vocab_content)

            # 读取语法模式
            if self.grammar_patterns_file.exists():
                grammar_content = self.grammar_patterns_file.read_text(encoding='utf-8')
                style_guide["grammar"] = self._parse_grammar_patterns(grammar_content)

            if style_type:
                return {
                    "status": "success",
                    "style_type": style_type,
                    "guide": style_guide.get(style_type, {})
                }

            return {
                "status": "success",
                "complete_guide": style_guide
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"获取写作风格指南失败: {e}"
            }

    def generate_style_prompts(self, content_type: str) -> Dict[str, Any]:
        """生成风格提示"""
        try:
            # 获取风格指南
            style_guide_result = self.get_writing_style_guide()
            if style_guide_result["status"] != "success":
                return style_guide_result

            style_guide = style_guide_result["complete_guide"]

            # 根据内容类型生成提示
            prompts = self._build_style_prompts(style_guide, content_type)

            return {
                "status": "success",
                "content_type": content_type,
                "prompts": prompts
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"生成风格提示失败: {e}"
            }

    def add_vocabulary_category(self, category: str, words: List[str]) -> Dict[str, Any]:
        """添加词汇类别"""
        try:
            # 读取现有词汇文件
            if self.vocabulary_file.exists():
                content = self.vocabulary_file.read_text(encoding='utf-8')
            else:
                content = "# 词汇偏好\n\n"

            # 添加新词汇类别
            new_category = f"""## {category}

{', '.join(words)}

---

"""
            content += new_category

            # 保存更新后的内容
            self.vocabulary_file.write_text(content, encoding='utf-8')

            return {
                "status": "success",
                "message": f"词汇类别 {category} 添加成功",
                "word_count": len(words)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"添加词汇类别失败: {e}"
            }

    def validate_style_consistency(self, sample_text: str) -> Dict[str, Any]:
        """验证风格一致性"""
        try:
            # 获取风格指南
            style_guide_result = self.get_writing_style_guide()
            if style_guide_result["status"] != "success":
                return style_guide_result

            style_guide = style_guide_result["complete_guide"]

            # 分析文本风格特征
            text_analysis = self._analyze_text_style(sample_text)

            # 与设定风格进行对比
            consistency_report = self._compare_style_consistency(
                style_guide, text_analysis
            )

            return {
                "status": "success",
                "sample_length": len(sample_text),
                "text_analysis": text_analysis,
                "consistency_report": consistency_report
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"验证风格一致性失败: {e}"
            }

    def _format_narrative_style(self, data: Dict[str, Any]) -> str:
        """格式化叙事风格"""
        return f"""# 叙事风格

## 叙事视角
{data.get('narrative_voice', '第三人称有限视角')}

## 语气和语调
{data.get('tone', '客观中立')}

## 节奏控制
{data.get('pacing', '中等节奏')}

## 描述风格
{data.get('description_style', '简洁而生动')}

## 情感表达
{data.get('emotional_expression', '内敛含蓄')}

## 时空转换
{data.get('time_space_transition', '自然流畅')}

## 内心独白
{data.get('inner_monologue', '适度使用')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_dialogue_style(self, data: Dict[str, Any]) -> str:
        """格式化对话风格"""
        return f"""# 对话风格

## 对话特点
{data.get('dialogue_characteristics', '自然真实，符合角色性格')}

## 语言风格
{data.get('language_style', '口语化，避免过于书面化')}

## 方言特色
{data.get('dialect_features', '标准普通话，可根据角色需要调整')}

## 情感色彩
{data.get('emotional_color', '根据角色情绪调整语气')}

## 对话节奏
{data.get('dialogue_pacing', '张弛有度，有停顿和思考')}

## 重复模式
{data.get('repetition_patterns', '适当使用口头禅和习惯用语')}

## 对话标签
{data.get('dialogue_tags', '多样化，避免单调重复')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_vocabulary(self, data: Dict[str, Any]) -> str:
        """格式化词汇偏好"""
        return f"""# 词汇偏好

## 常用词汇类别

### 描述性词汇
{data.get('descriptive_words', '生动、准确、富有画面感')}

### 情感词汇
{data.get('emotional_words', '细腻、层次丰富、符合情境')}

### 动作词汇
{data.get('action_words', '简洁有力、准确传神')}

### 环境词汇
{data.get('environmental_words', '具体细致、营造氛围')}

## 避免使用的词汇
{data.get('avoid_words', '过于陈旧、不合时宜的词汇')}

## 特殊用词习惯
{data.get('special_usage', '根据角色特点调整用词')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _format_grammar_patterns(self, data: Dict[str, Any]) -> str:
        """格式化语法模式"""
        return f"""# 语法模式

## 句式结构
{data.get('sentence_structure', '长短句结合，富有变化')}

## 段落组织
{data.get('paragraph_organization', '逻辑清晰，层次分明')}

## 修辞手法
{data.get('rhetorical_devices', '适度使用比喻、排比等修辞')}

## 时态使用
{data.get('tense_usage', '以过去时为主，现在时用于对话')}

## 语态选择
{data.get('voice_choice', '主动语态为主，被动语态适当使用')}

## 连接词使用
{data.get('conjunction_usage', '自然过渡，避免生硬')}

## 标点符号
{data.get('punctuation_usage', '规范准确，符合语境')}

---
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _apply_style_update(self, content: str, updates: Dict[str, Any], component: str) -> str:
        """应用风格更新"""
        # 简化处理：在现有内容后添加更新信息
        update_section = "\n\n## 更新记录\n\n"
        for key, value in updates.items():
            update_section += f"**{key}**: {value}\n"

        update_section += f"\n*更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return content + update_section

    def _parse_narrative_style(self, content: str) -> Dict[str, Any]:
        """解析叙事风格"""
        style = {}
        lines = content.split('\n')

        for line in lines:
            if line.startswith("##"):
                current_section = line[3:].strip()
            elif line.startswith("**叙事视角**"):
                style["narrative_voice"] = line.split(":")[1].strip()
            elif line.startswith("**语气和语调**"):
                style["tone"] = line.split(":")[1].strip()
            elif line.startswith("**节奏控制**"):
                style["pacing"] = line.split(":")[1].strip()

        return style

    def _parse_dialogue_style(self, content: str) -> Dict[str, Any]:
        """解析对话风格"""
        style = {}
        lines = content.split('\n')

        for line in lines:
            if line.startswith("**对话特点**"):
                style["dialogue_characteristics"] = line.split(":")[1].strip()
            elif line.startswith("**语言风格**"):
                style["language_style"] = line.split(":")[1].strip()
            elif line.startswith("**对话节奏**"):
                style["dialogue_pacing"] = line.split(":")[1].strip()

        return style

    def _parse_vocabulary(self, content: str) -> Dict[str, Any]:
        """解析词汇偏好"""
        vocab = {"categories": {}}
        lines = content.split('\n')
        current_category = None

        for line in lines:
            if line.startswith("## "):
                current_category = line[3:].strip()
                vocab["categories"][current_category] = []
            elif line.startswith("- ") or line.startswith("* "):
                if current_category:
                    vocab["categories"][current_category].append(line[2:].strip())

        return vocab

    def _parse_grammar_patterns(self, content: str) -> Dict[str, Any]:
        """解析语法模式"""
        patterns = {}
        lines = content.split('\n')

        for line in lines:
            if line.startswith("**句式结构**"):
                patterns["sentence_structure"] = line.split(":")[1].strip()
            elif line.startswith("**段落组织**"):
                patterns["paragraph_organization"] = line.split(":")[1].strip()
            elif line.startswith("**修辞手法**"):
                patterns["rhetorical_devices"] = line.split(":")[1].strip()

        return patterns

    def _build_style_prompts(self, style_guide: Dict[str, Any], content_type: str) -> List[str]:
        """构建风格提示"""
        prompts = []

        if content_type in ["narration", "description", "action"]:
            # 叙事类提示
            if "narrative" in style_guide:
                narrative = style_guide["narrative"]
                prompts.append(f"使用{narrative.get('narrative_voice', '第三人称')}视角")
                prompts.append(f"保持{narrative.get('tone', '客观')}的语调")
                prompts.append(f"控制{narrative.get('pacing', '中等')}的节奏")

        elif content_type in ["dialogue", "conversation"]:
            # 对话类提示
            if "dialogue" in style_guide:
                dialogue = style_guide["dialogue"]
                prompts.append(f"对话要{dialogue.get('dialogue_characteristics', '自然真实')}")
                prompts.append(f"使用{dialogue.get('language_style', '口语化')}的语言")
                prompts.append(f"注意{dialogue.get('dialogue_pacing', '张弛有度')}的节奏")

        # 词汇提示
        if "vocabulary" in style_guide:
            prompts.append("使用符合设定的词汇偏好")

        # 语法提示
        if "grammar" in style_guide:
            grammar = style_guide["grammar"]
            prompts.append(f"句式要{grammar.get('sentence_structure', '长短句结合')}")

        return prompts

    def _analyze_text_style(self, text: str) -> Dict[str, Any]:
        """分析文本风格特征"""
        # 简单的文本分析
        sentences = text.split('。')
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0

        # 统计词汇特征
        words = text.split()
        unique_words = set(words)
        vocabulary_richness = len(unique_words) / len(words) if words else 0

        # 检测对话比例
        dialogue_count = text.count('"') + text.count('"') + text.count('"')
        dialogue_ratio = dialogue_count / len(text) if text else 0

        return {
            "avg_sentence_length": avg_sentence_length,
            "vocabulary_richness": vocabulary_richness,
            "dialogue_ratio": dialogue_ratio,
            "total_length": len(text)
        }

    def _compare_style_consistency(self, style_guide: Dict[str, Any],
                                 text_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """比较风格一致性"""
        issues = []
        suggestions = []

        # 简单的一致性检查
        if text_analysis["avg_sentence_length"] > 50:
            issues.append("句子过长，可能影响可读性")
            suggestions.append("考虑使用更多短句来改善节奏")

        if text_analysis["vocabulary_richness"] < 0.3:
            issues.append("词汇丰富度较低")
            suggestions.append("增加词汇多样性")

        if text_analysis["dialogue_ratio"] > 0.4:
            issues.append("对话比例较高")
            suggestions.append("平衡对话和叙述的比例")

        return {
            "is_consistent": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "overall_score": max(0, 100 - len(issues) * 10)
        }

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="写作风格管理器")
    parser.add_argument("--action", choices=["create", "update", "guide", "prompts", "validate"],
                       required=True, help="操作类型")
    parser.add_argument("--component", choices=["narrative", "dialogue", "vocabulary", "grammar"],
                       help="风格组件")
    parser.add_argument("--content-type", choices=["narration", "dialogue", "description", "action"],
                       help="内容类型")
    parser.add_argument("--project-path", default=".", help="项目路径")

    args = parser.parse_args()

    sm = StyleManager(args.project_path)

    if args.action == "create":
        sample_data = {
            "narrative_voice": "第三人称有限视角",
            "tone": "温和而客观",
            "pacing": "中等偏慢"
        }
        result = sm.create_writing_style(sample_data)

    elif args.action == "update":
        if not args.component:
            print("错误: update操作需要指定--component参数")
            return
        updates = {"语气": "更加温暖亲切"}
        result = sm.update_style_component(args.component, updates)

    elif args.action == "guide":
        result = sm.get_writing_style_guide(args.component)

    elif args.action == "prompts":
        if not args.content_type:
            print("错误: prompts操作需要指定--content-type参数")
            return
        result = sm.generate_style_prompts(args.content_type)

    elif args.action == "validate":
        sample_text = "这是一段用于测试风格一致性的示例文本。它包含了一些叙述和对话。"
        result = sm.validate_style_consistency(sample_text)

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()