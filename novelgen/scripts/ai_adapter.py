#!/usr/bin/env python3
"""
AI模型适配器
支持多种AI模型的统一调用接口
"""

import os
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

class AIModel(ABC):
    """AI模型抽象基类"""

    @abstractmethod
    def generate_content(self, prompt: str, **kwargs) -> Optional[str]:
        """生成内容"""
        pass

class ClaudeModel(AIModel):
    """Claude AI模型实现"""

    def __init__(self, api_key: str = None, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.model = model
        self._client = None

    def _get_client(self):
        """获取Claude客户端"""
        if self._client is None:
            try:
                from anthropic import Anthropic
                if not self.api_key:
                    raise ValueError("未找到ANTHROPIC_API_KEY环境变量")
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("未安装anthropic库，请运行: pip install anthropic")
        return self._client

    def generate_content(self, prompt: str, **kwargs) -> Optional[str]:
        """使用Claude生成内容"""
        try:
            client = self._get_client()

            response = client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 4000),
                temperature=kwargs.get('temperature', 0.7),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            print(f"❌ Claude API调用失败: {str(e)}")
            return None

class OpenAIModel(AIModel):
    """OpenAI GPT模型实现"""

    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self._client = None

    def _get_client(self):
        """获取OpenAI客户端"""
        if self._client is None:
            try:
                from openai import OpenAI
                if not self.api_key:
                    raise ValueError("未找到OPENAI_API_KEY环境变量")
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("未安装openai库，请运行: pip install openai")
        return self._client

    def generate_content(self, prompt: str, **kwargs) -> Optional[str]:
        """使用OpenAI生成内容"""
        try:
            client = self._get_client()

            response = client.chat.completions.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 4000),
                temperature=kwargs.get('temperature', 0.7),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ OpenAI API调用失败: {str(e)}")
            return None

class LocalModel(AIModel):
    """本地AI模型实现（用于测试）"""

    def generate_content(self, prompt: str, **kwargs) -> Optional[str]:
        """生成模拟内容（仅用于测试）"""
        print("🔄 使用本地模拟模式生成内容...")

        # 简单的模拟内容生成
        content = f"""
# 第一章：血色实验室

深夜的基因研究所内，巫起澜正在进行第37次意识转移实验。纳米机器人在培养舱中编织神经网络，但数据偏差始终卡在0.37%。

突然，警报声响起，实验室遭遇不明入侵。巫起澜发现导师李云飞教授还在核心实验室，不顾警告前往查看。

在实验室中，他发现了惊人的场景：一个神秘男子正在处理导师的残缺手臂。那人展现出超人类的能力，在特种部队到来时从高楼跳下逃生。

第二天，国家安全部的专家分析监控录像，得出惊人结论：目标是量产型强化人士兵，反应时间和身体强度远超人类极限。

巫起澜意识到人类进化时代的到来，决心继续导师的研究...

---
*此内容由AI模型自动生成*
*字数: 约{len(prompt)} tokens*
"""

        return content.strip()

class AIAdapter:
    """AI模型适配器"""

    def __init__(self, model_type: str = "auto"):
        self.model_type = model_type
        self._model = None
        self._initialize_model()

    def _initialize_model(self):
        """初始化AI模型"""
        if self.model_type == "auto":
            # 自动选择可用的模型
            self._model = self._auto_select_model()
        elif self.model_type == "claude":
            self._model = ClaudeModel()
        elif self.model_type == "openai":
            self._model = OpenAIModel()
        elif self.model_type == "local":
            self._model = LocalModel()
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")

    def _auto_select_model(self) -> AIModel:
        """自动选择可用的AI模型"""

        # 1. 检查Claude是否可用
        if os.getenv('ANTHROPIC_API_KEY'):
            try:
                from anthropic import Anthropic
                print("✅ 检测到Claude API，使用Claude模型")
                return ClaudeModel()
            except ImportError:
                pass

        # 2. 检查OpenAI是否可用
        if os.getenv('OPENAI_API_KEY'):
            try:
                from openai import OpenAI
                print("✅ 检测到OpenAI API，使用GPT模型")
                return OpenAIModel()
            except ImportError:
                pass

        # 3. 使用本地模拟模式
        print("⚠️  未检测到AI API，使用本地模拟模式")
        return LocalModel()

    def generate_content(self, prompt: str, **kwargs) -> Optional[str]:
        """生成内容"""
        if not self._model:
            raise RuntimeError("AI模型未初始化")

        return self._model.generate_content(prompt, **kwargs)

    def get_model_info(self) -> Dict[str, Any]:
        """获取当前模型信息"""
        model_name = self._model.__class__.__name__

        if isinstance(self._model, ClaudeModel):
            return {
                "type": "Claude",
                "model": self._model.model,
                "api_key_configured": bool(self._model.api_key)
            }
        elif isinstance(self._model, OpenAIModel):
            return {
                "type": "OpenAI",
                "model": self._model.model,
                "api_key_configured": bool(self._model.api_key)
            }
        elif isinstance(self._model, LocalModel):
            return {
                "type": "Local",
                "model": "Simulation",
                "api_key_configured": False
            }

        return {
            "type": "Unknown",
            "model": "Unknown",
            "api_key_configured": False
        }

def main():
    """测试AI适配器"""
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python ai_adapter.py <prompt> [model_type]")
        print("模型类型: claude, openai, local, auto")
        return

    prompt = sys.argv[1]
    model_type = sys.argv[2] if len(sys.argv) > 2 else "auto"

    print(f"🤖 使用模型类型: {model_type}")
    print(f"📝 输入提示长度: {len(prompt)} 字符")

    try:
        adapter = AIAdapter(model_type)
        model_info = adapter.get_model_info()
        print(f"🔧 当前模型: {model_info}")

        print("⏳ 正在生成内容...")
        content = adapter.generate_content(prompt)

        if content:
            print("✅ 内容生成成功:")
            print("-" * 50)
            print(content)
            print("-" * 50)
            print(f"📊 生成内容长度: {len(content)} 字符")
        else:
            print("❌ 内容生成失败")

    except Exception as e:
        print(f"❌ 错误: {str(e)}")

if __name__ == "__main__":
    main()